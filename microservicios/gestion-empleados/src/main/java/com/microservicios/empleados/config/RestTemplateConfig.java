package com.microservicios.empleados.config;

import jakarta.servlet.http.HttpServletRequest;
import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpHeaders;
import org.springframework.web.context.request.RequestAttributes;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;
import org.springframework.web.client.RestTemplate;

import java.time.Duration;

/**
 * Configuración de RestTemplate para comunicación entre microservicios
 */
@Configuration
public class RestTemplateConfig {

    @Bean
    public RestTemplate restTemplate(RestTemplateBuilder builder) {
        return builder
                .setConnectTimeout(Duration.ofSeconds(10))
                .setReadTimeout(Duration.ofSeconds(10))
                .additionalInterceptors((request, body, execution) -> {
                    RequestAttributes attrs = RequestContextHolder.getRequestAttributes();
                    if (attrs instanceof ServletRequestAttributes servletAttrs) {
                        HttpServletRequest inboundRequest = servletAttrs.getRequest();
                        String authorization = inboundRequest.getHeader(HttpHeaders.AUTHORIZATION);
                        if (authorization != null && !authorization.isBlank()) {
                            request.getHeaders().set(HttpHeaders.AUTHORIZATION, authorization);
                        }
                    }

                    return execution.execute(request, body);
                })
                .build();
    }
}
