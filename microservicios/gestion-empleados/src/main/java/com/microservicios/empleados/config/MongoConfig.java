package com.microservicios.empleados.config;

import com.mongodb.MongoClientSettings;
import org.springframework.boot.autoconfigure.mongo.MongoClientSettingsBuilderCustomizer;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import javax.net.ssl.SSLContext;
import javax.net.ssl.TrustManagerFactory;
import java.security.KeyStore;

@Configuration
public class MongoConfig {

    /**
     * Forces the MongoDB driver to use TLS 1.2 via a custom SSLContext.
     * This bypasses the JVM-level TLS negotiation that causes
     * "SSLException: Received fatal alert: internal_error" on WSL2 with Java 17.
     */
    @Bean
    public MongoClientSettingsBuilderCustomizer mongoSslCustomizer() {
        return builder -> {
            try {
                // Build a TrustManagerFactory using the default JDK truststore
                TrustManagerFactory tmf = TrustManagerFactory
                        .getInstance(TrustManagerFactory.getDefaultAlgorithm());
                tmf.init((KeyStore) null); // null = use default cacerts

                // Create an SSLContext pinned to TLSv1.2
                SSLContext sslContext = SSLContext.getInstance("TLSv1.2");
                sslContext.init(null, tmf.getTrustManagers(), null);

                builder.applyToSslSettings(ssl -> ssl
                        .enabled(true)
                        .invalidHostNameAllowed(false)
                        .context(sslContext)
                );
            } catch (Exception e) {
                throw new RuntimeException("Failed to configure MongoDB SSLContext with TLSv1.2", e);
            }
        };
    }
}
