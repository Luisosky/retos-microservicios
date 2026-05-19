package com.microservicios.empleados.config;

import org.conscrypt.Conscrypt;
import org.springframework.boot.autoconfigure.mongo.MongoClientSettingsBuilderCustomizer;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import jakarta.annotation.PostConstruct;

import javax.net.ssl.SSLContext;
import javax.net.ssl.TrustManagerFactory;
import java.security.KeyStore;
import java.security.Security;

@Configuration
public class MongoConfig {

    /**
     * Registers Conscrypt (BoringSSL-based) as the top security provider.
     * This completely replaces Sun JSSE for all TLS connections, fixing the
     * "SSLException: Received fatal alert: internal_error" on WSL2 with Java 17.
     */
    @PostConstruct
    public void installConscrypt() {
        try {
            Security.insertProviderAt(Conscrypt.newProvider(), 1);
        } catch (Exception e) {
            throw new RuntimeException("Failed to install Conscrypt security provider", e);
        }
    }

    /**
     * Configures MongoDB to use a Conscrypt-backed SSLContext.
     */
    @Bean
    public MongoClientSettingsBuilderCustomizer mongoSslCustomizer() {
        return builder -> {
            try {
                TrustManagerFactory tmf = TrustManagerFactory
                        .getInstance(TrustManagerFactory.getDefaultAlgorithm());
                tmf.init((KeyStore) null);

                // SSLContext.getInstance will now use Conscrypt as provider #1
                SSLContext sslContext = SSLContext.getInstance("TLS");
                sslContext.init(null, tmf.getTrustManagers(), null);

                builder.applyToSslSettings(ssl -> ssl
                        .enabled(true)
                        .invalidHostNameAllowed(false)
                        .context(sslContext)
                );
            } catch (Exception e) {
                throw new RuntimeException("Failed to configure MongoDB SSLContext via Conscrypt", e);
            }
        };
    }
}
