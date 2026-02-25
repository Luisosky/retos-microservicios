package com.microservicios.empleados.service;

import com.microservicios.empleados.client.DepartamentoClient;
import com.microservicios.empleados.enums.EstadoEmpleado;
import com.microservicios.empleados.exception.DepartamentoNoValidoException;
import com.microservicios.empleados.exception.EmpleadoYaExisteException;
import com.microservicios.empleados.exception.EmpleadoNoEncontradoException;
import com.microservicios.empleados.model.Empleado;
import com.microservicios.empleados.model.EventoEmpleado;
import com.microservicios.empleados.repository.EmpleadoRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;
import java.util.List;

@Service
@RequiredArgsConstructor
@Slf4j
public class EmpleadoService {
    private final EmpleadoRepository empleadoRepository;
    private final RedisTemplate<String, Object> redisTemplate;
    private final ObjectMapper objectMapper;
    private final DepartamentoClient departamentoClient;
    private static final String STREAM_KEY = "eventos:empleados";

    @Transactional
    public Empleado crearEmpleado(Empleado empleado) {
        // Validar número de empleado
        if (empleado.getNumeroEmpleado() == null || empleado.getNumeroEmpleado().trim().isEmpty()) {
            throw new IllegalArgumentException("El número de empleado es requerido");
        }

        // Validar que el departamento existe mediante comunicación con el servicio de departamentos
        log.info("Validando existencia del departamento: {}", empleado.getDepartamentoId());
        if (!departamentoClient.existeDepartamento(empleado.getDepartamentoId())) {
            throw new DepartamentoNoValidoException(
                    "El departamento con id '" + empleado.getDepartamentoId() + "' no existe o no está activo"
            );
        }
        log.info("Departamento validado exitosamente");

        // Validar unicidad de email
        if (empleadoRepository.existsByEmail(empleado.getEmail())) {
            throw new EmpleadoYaExisteException("El email " + empleado.getEmail() + " ya está registrado");
        }

        // Validar unicidad de número de empleado
        if (empleadoRepository.existsById(empleado.getNumeroEmpleado())) {
            throw new EmpleadoYaExisteException("El número de empleado " + empleado.getNumeroEmpleado() + " ya está registrado");
        }

        // Establecer estado por defecto si no se proporciona
        if (empleado.getEstado() == null) {
            empleado.setEstado(EstadoEmpleado.ACTIVO);
        }

        Empleado empleadoGuardado = empleadoRepository.save(empleado);
        log.info("Empleado creado exitosamente: {}", empleadoGuardado.getNumeroEmpleado());
        
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
