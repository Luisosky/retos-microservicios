package com.microservicios.empleados.controller;

import org.bson.Document;
import org.springframework.data.mongodb.core.MongoTemplate;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.HashMap;
import java.util.Map;

@RestController
public class MongoHealthController {
    private final MongoTemplate mongoTemplate;

    public MongoHealthController(MongoTemplate mongoTemplate) {
        this.mongoTemplate = mongoTemplate;
    }

    @GetMapping("/mongo/health")
    public ResponseEntity<Map<String, Object>> health() {
        Map<String, Object> body = new HashMap<>();
        try {
            Document res = mongoTemplate.executeCommand(new Document("ping", 1));
            Object ok = res.get("ok");
            boolean connected = ok instanceof Number ? ((Number) ok).doubleValue() == 1.0 : "1".equals(ok);
            body.put("connected", connected);
            body.put("detail", res);
            return ResponseEntity.ok(body);
        } catch (Exception e) {
            body.put("connected", false);
            body.put("error", e.getMessage());
            return ResponseEntity.status(503).body(body);
        }
    }
}
