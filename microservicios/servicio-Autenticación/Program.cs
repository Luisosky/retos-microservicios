using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.IdentityModel.Tokens;
using ServicioAutenticacion.Services;
using System.Text;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();
builder.Services.AddSingleton<IUserRepository, InMemoryUserRepository>();
builder.Services.AddSingleton<IJwtTokenService, JwtTokenService>();

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

app.Run();
