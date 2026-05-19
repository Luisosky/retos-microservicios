package com.microservicios.empleados.config;

import org.springframework.amqp.core.TopicExchange;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class RabbitMQConfig {

    public static final String EMPLEADOS_EXCHANGE = "empleados.events";

    @Bean
    public TopicExchange empleadosEventsExchange() {
        return new TopicExchange(EMPLEADOS_EXCHANGE, true, false);
    }
}
