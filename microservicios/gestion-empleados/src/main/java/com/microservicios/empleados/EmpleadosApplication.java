package com.microservicios.empleados;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.data.mongodb.repository.config.EnableMongoRepositories;

@SpringBootApplication
@EnableMongoRepositories(basePackages = "com.microservicios.empleados.repository")
public class EmpleadosApplication {
    public static void main(String[] args) {
        SpringApplication.run(EmpleadosApplication.class, args);
    }
}
