package com.microservicios.empleados.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.License;
import io.swagger.v3.oas.models.servers.Server;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.List;

@Configuration
public class OpenAPIConfiguration {

    @Bean
    public OpenAPI customOpenAPI() {
        return new OpenAPI()
                .info(new Info()
                        .title("API Gestión de Empleados")
                        .description("Microservicio para gestión de empleados con MongoDB y Redis Streams. " +
                                "Proporciona endpoints para registrar, consultar, actualizar y eliminar empleados.")
                        .version("1.0.0")
                        .contact(new Contact()
                                .name("Equipo de Desarrollo")
                                .email("dev@empresa.com")
                                .url("https://github.com/tu-repo"))
                        .license(new License()
                                .name("MIT")
                                .url("https://opensource.org/licenses/MIT")))
                .servers(List.of(
                        new Server()
                                .url("http://localhost:8080")
                                .description("Desarrollo Local"),
                        new Server()
                                .url("http://empleados-service:8080")
                                .description("Docker Compose"),
                        new Server()
                                .url("https://api.produccion.com")
                                .description("Producción")));
    }
}

