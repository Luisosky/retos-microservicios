package com.microservicios.empleados.service;

import com.microservicios.empleados.enums.EstadoEmpleado;
import com.microservicios.empleados.exception.EmpleadoYaExisteException;
import com.microservicios.empleados.exception.EmpleadoNoEncontradoException;
import com.microservicios.empleados.model.Empleado;
import com.microservicios.empleados.model.EventoEmpleado;
import com.microservicios.empleados.repository.EmpleadoRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;
import java.util.List;

@Service
@RequiredArgsConstructor
public class EmpleadoService {
    private final EmpleadoRepository empleadoRepository;
    private final RedisTemplate<String, Object> redisTemplate;
    private final ObjectMapper objectMapper;
    private static final String STREAM_KEY = "eventos:empleados";

    @Transactional
    public Empleado crearEmpleado(Empleado empleado) {
        if (empleado.getNumeroEmpleado() == null || empleado.getNumeroEmpleado().trim().isEmpty()) {
            throw new IllegalArgumentException("El número de empleado es requerido");
        }
        if (empleadoRepository.existsByEmail(empleado.getEmail())) {
            throw new EmpleadoYaExisteException("El email " + empleado.getEmail() + " ya está registrado");
        }
        if (empleadoRepository.existsById(empleado.getNumeroEmpleado())) {
            throw new EmpleadoYaExisteException("El número de empleado " + empleado.getNumeroEmpleado() + " ya está registrado");
        }

        if (empleado.getEstado() == null) {
            empleado.setEstado(EstadoEmpleado.ACTIVO);
        }

        Empleado empleadoGuardado = empleadoRepository.save(empleado);
        publicarEventoEmpleadoCreado(empleadoGuardado);
        return empleadoGuardado;
    }

    public Empleado obtenerEmpleadoPorId(String id) {
        return empleadoRepository.findById(id)
                .orElseThrow(() -> new EmpleadoNoEncontradoException("El empleado con id " + id + " no existe"));
    }

    private void publicarEventoEmpleadoCreado(Empleado empleado) {
        try {
            EventoEmpleado evento = EventoEmpleado.builder()
                    .tipo("EMPLEADO_CREADO")
                    .datos(empleado)
                    .timestamp(LocalDateTime.now())
                    .build();

            Map<String, String> eventoMap = new HashMap<>();
            eventoMap.put("tipo", evento.getTipo());
            eventoMap.put("numeroEmpleado", empleado.getNumeroEmpleado());
            eventoMap.put("timestamp", evento.getTimestamp().toString());
            eventoMap.put("datos", objectMapper.writeValueAsString(evento.getDatos()));

            redisTemplate.opsForStream().add(STREAM_KEY, eventoMap);
        } catch (Exception e) {
            // Log the error but don't fail the employee creation
            System.err.println("Error al publicar evento a Redis: " + e.getMessage());
        }
    }

    public List<Empleado> obtenerTodosEmpleados() {
        return empleadoRepository.findAll();
    }
}
