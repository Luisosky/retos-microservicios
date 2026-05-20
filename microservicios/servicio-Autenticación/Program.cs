using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.EntityFrameworkCore;
using Microsoft.IdentityModel.Tokens;
using Npgsql;
using NpgsqlTypes;
using ServicioAutenticacion.Data;
using ServicioAutenticacion.Messaging;
using ServicioAutenticacion.Services;
using System.Text;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();
builder.Services.AddSingleton<IJwtTokenService, JwtTokenService>();
builder.Services.AddSingleton<IRabbitMqPublisher, RabbitMqPublisher>();
builder.Services.AddHostedService<EmpleadoEventsConsumerService>();
builder.Services.AddHostedService<RecuperacionPasswordConsumerService>();

var authDatabaseUrl = Environment.GetEnvironmentVariable("AUTH_DATABASE_URL")
    ?? Environment.GetEnvironmentVariable("DEP_DATABASE_URL")
    ?? Environment.GetEnvironmentVariable("NOTIF_DATABASE_URL")
    ?? builder.Configuration["ConnectionStrings:AuthDatabase"];

if (string.IsNullOrWhiteSpace(authDatabaseUrl))
{
    throw new InvalidOperationException("AUTH_DATABASE_URL/DEP_DATABASE_URL is not configured.");
}

authDatabaseUrl = NormalizePostgresConnectionString(authDatabaseUrl);

// Ensure pooling settings are added using a proper Npgsql builder.
// String concatenation can accidentally mutate credentials when the
// connection string is already in key/value format.
var csBuilder = new NpgsqlConnectionStringBuilder(authDatabaseUrl)
{
    MaxPoolSize = 25,
    MinPoolSize = 0,
    KeepAlive = 30,
    ConnectionIdleLifetime = 30,
    ConnectionPruningInterval = 10,
    // Supabase pgbouncer (transaction mode, port 6543) no soporta prepared statements
    // ni el RESET ALL que Npgsql emite por defecto.
    MaxAutoPrepare = 0,
    ServerCompatibilityMode = ServerCompatibilityMode.NoTypeLoading,
    NoResetOnClose = true,
    Multiplexing = false
};
authDatabaseUrl = csBuilder.ConnectionString;

builder.Services.AddDbContext<AuthDbContext>(options => 
{
    options.UseNpgsql(authDatabaseUrl, npgsqlOptions =>
    {
        // Keep failed database calls from stalling the request for too long.
        npgsqlOptions.CommandTimeout(10);
        
        // Retry transient failures once after reopening the connection.
        npgsqlOptions.EnableRetryOnFailure(
            maxRetryCount: 1,
            maxRetryDelay: TimeSpan.FromSeconds(1),
            errorCodesToAdd: null);
    });
});

var jwtSection = builder.Configuration.GetSection("Jwt");
var issuer = Environment.GetEnvironmentVariable("JWT_ISSUER") ?? jwtSection["Issuer"] ?? "auth-service";
var audience = Environment.GetEnvironmentVariable("JWT_AUDIENCE") ?? jwtSection["Audience"] ?? "microservices-clients";
var secret = Environment.GetEnvironmentVariable("JWT_SECRET") ?? jwtSection["Secret"];

if (string.IsNullOrWhiteSpace(secret))
{
    throw new InvalidOperationException("JWT secret is not configured. Set JWT_SECRET env variable or Jwt:Secret in appsettings.");
}

var key = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(secret));

builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidIssuer = issuer,
            ValidateAudience = true,
            ValidAudience = audience,
            ValidateIssuerSigningKey = true,
            IssuerSigningKey = key,
            ValidateLifetime = true,
            ClockSkew = TimeSpan.FromSeconds(30)
        };
    });

builder.Services.AddAuthorization();

var app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseAuthentication();
app.UseAuthorization();

app.MapControllers();

app.MapGet("/health", () => Results.Ok(new
{
    status = "ok",
    service = "autenticacion",
    timestamp = DateTimeOffset.UtcNow
}));

// Only ensure created in development to avoid startup failures
if (app.Environment.IsDevelopment())
{
    try
    {
        using (var scope = app.Services.CreateScope())
        {
            var db = scope.ServiceProvider.GetRequiredService<AuthDbContext>();
            db.Database.EnsureCreated();
        }
    }
    catch (Exception ex)
    {
        Console.WriteLine($"Warning: Could not create database: {ex.Message}");
    }
}

app.Run();

static string NormalizePostgresConnectionString(string value)
{
    if (string.IsNullOrWhiteSpace(value))
    {
        return value;
    }

    if (value.Contains("Host=", StringComparison.OrdinalIgnoreCase)
        || value.Contains("Server=", StringComparison.OrdinalIgnoreCase))
    {
        return value;
    }

    var uriStyle = value
        .Replace("postgresql+psycopg2://", "postgresql://", StringComparison.OrdinalIgnoreCase)
        .Replace("postgres+psycopg2://", "postgresql://", StringComparison.OrdinalIgnoreCase)
        .Replace("postgres://", "postgresql://", StringComparison.OrdinalIgnoreCase);

    if (!Uri.TryCreate(uriStyle, UriKind.Absolute, out var uri)
        || !uri.Scheme.Equals("postgresql", StringComparison.OrdinalIgnoreCase))
    {
        return value;
    }

    var builder = new NpgsqlConnectionStringBuilder
    {
        Host = uri.Host,
        Port = uri.IsDefaultPort ? 5432 : uri.Port
    };

    var database = uri.AbsolutePath.Trim('/');
    if (!string.IsNullOrWhiteSpace(database))
    {
        builder.Database = database;
    }

    if (!string.IsNullOrWhiteSpace(uri.UserInfo))
    {
        var parts = uri.UserInfo.Split(':', 2);
        if (parts.Length > 0 && !string.IsNullOrWhiteSpace(parts[0]))
        {
            builder.Username = Uri.UnescapeDataString(parts[0]);
        }

        if (parts.Length > 1)
        {
            builder.Password = Uri.UnescapeDataString(parts[1]);
        }
    }

    if (!string.IsNullOrWhiteSpace(uri.Query))
    {
        var query = uri.Query.TrimStart('?').Split('&', StringSplitOptions.RemoveEmptyEntries);
        foreach (var entry in query)
        {
            var pair = entry.Split('=', 2);
            var key = Uri.UnescapeDataString(pair[0]);
            var rawValue = pair.Length > 1 ? Uri.UnescapeDataString(pair[1]) : string.Empty;

            switch (key.ToLowerInvariant())
            {
                case "sslmode":
                    if (Enum.TryParse<SslMode>(rawValue, true, out var sslMode))
                    {
                        builder.SslMode = sslMode;
                    }
                    break;
            }
        }
    }

    return builder.ConnectionString;
}
