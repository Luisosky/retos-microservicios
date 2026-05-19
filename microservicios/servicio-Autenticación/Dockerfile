# Build stage
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

COPY . .
RUN dotnet restore "ServicioAutenticacion.csproj"
RUN dotnet publish "ServicioAutenticacion.csproj" -c Release -o /app/publish /p:UseAppHost=false

# Runtime stage
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS final
WORKDIR /app

# curl is used by docker-compose healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY --from=build /app/publish .

EXPOSE 8084
ENV ASPNETCORE_URLS=http://+:8084

ENTRYPOINT ["dotnet", "ServicioAutenticacion.dll"]
