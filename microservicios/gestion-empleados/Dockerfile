FROM maven:3.9-eclipse-temurin-17 AS build
WORKDIR /app
COPY pom.xml .
RUN mvn dependency:go-offline
COPY src ./src
RUN mvn clean package -DskipTests

FROM eclipse-temurin:17-jre-focal
WORKDIR /app
COPY --from=build /app/target/*.jar app.jar

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Override java.security to disable TLS 1.3 - fixes SSL handshake failure with
# MongoDB Atlas on Docker + WSL2 (OpenSSL/JSSE incompatibility)
RUN find /opt/java -name "java.security" | head -1 | xargs -I{} sh -c \
    "sed -i 's/TLSv1.3,//g; s/, TLSv1.3//g' {} && \
     sed -i 's/^jdk.tls.disabledAlgorithms=/jdk.tls.disabledAlgorithms=TLSv1.3, /' {}"

EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]