package com.microservicios.empleados.config;

import org.conscrypt.Conscrypt;
import org.springframework.boot.autoconfigure.mongo.MongoClientSettingsBuilderCustomizer;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import jakarta.annotation.PostConstruct;

import javax.net.ssl.SSLContext;
import javax.net.ssl.TrustManagerFactory;
import java.security.KeyStore;
import java.security.Security;

@Configuration
public class MongoConfig {

    @Value("${app.mongo.useConscrypt:false}")
    private boolean useConscrypt;

    /**
     * Registers Conscrypt (BoringSSL-based) as the top security provider.
     * This completely replaces Sun JSSE for all TLS connections, fixing the
     * "SSLException: Received fatal alert: internal_error" on WSL2 with Java 17.
     */
    @PostConstruct
    public void installConscrypt() {
        if (!useConscrypt) {
            return;
        }

        try {
            Security.insertProviderAt(Conscrypt.newProvider(), 1);
        } catch (Exception e) {
            // Keep default JVM TLS stack if Conscrypt cannot be installed.
        }
    }

    /**
     * Configures MongoDB to use a Conscrypt-backed SSLContext.
     */
    @Bean
    public MongoClientSettingsBuilderCustomizer mongoSslCustomizer() {
        if (!useConscrypt) {
            return builder -> { };
        }

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
                // Keep default SSL configuration if custom context creation fails.
            }
        };
    }
}
