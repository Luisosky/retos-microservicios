FROM maven:3.9-eclipse-temurin-17 AS build
WORKDIR /app
COPY pom.xml .
RUN mvn dependency:go-offline
COPY src ./src
RUN mvn clean package -DskipTests

FROM eclipse-temurin:17-jre-jammy
WORKDIR /app
COPY --from=build /app/target/*.jar app.jar

# OpenTelemetry Java agent (Reto 7) — autoinstrumenta Spring MVC, RestTemplate,
# Mongo, RabbitMQ y exporta a Zipkin sin tocar el código de la app.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl -fsSL -o /app/opentelemetry-javaagent.jar \
       https://github.com/open-telemetry/opentelemetry-java-instrumentation/releases/download/v2.10.0/opentelemetry-javaagent.jar

EXPOSE 8080
ENTRYPOINT ["sh","-c","java -javaagent:/app/opentelemetry-javaagent.jar -jar app.jar"]