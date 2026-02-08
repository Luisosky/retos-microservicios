package com.microservicios.empleados.demo;

import org.bson.Document;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.CommandLineRunner;
import org.springframework.data.mongodb.core.MongoTemplate;
import org.springframework.stereotype.Component;

@Component
public class MongoConnectionChecker implements CommandLineRunner {

    private final MongoTemplate mongoTemplate;
    private final Logger log = LoggerFactory.getLogger(MongoConnectionChecker.class);

    public MongoConnectionChecker(MongoTemplate mongoTemplate) {
        this.mongoTemplate = mongoTemplate;
    }

    @Override
    public void run(String... args) {
        try {
            Document res = mongoTemplate.executeCommand(new Document("ping", 1));
            Object ok = res.get("ok");

            boolean connected = ok instanceof Number
                    ? ((Number) ok).doubleValue() == 1.0
                    : "1".equals(ok);

            if (connected) {
                log.info("✅ Conexión exitosa con MongoDB");
            } else {
                log.warn("⚠️ MongoDB respondió pero no confirmó conexión: {}", res.toJson());
            }

        } catch (Exception e) {
            log.error("❌ Error al conectar con MongoDB", e);
        }
    }
}
