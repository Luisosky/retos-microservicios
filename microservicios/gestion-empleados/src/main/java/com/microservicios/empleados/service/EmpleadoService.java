package com.microservicios.empleados.service;

import com.microservicios.empleados.enums.EstadoEmpleado;
import com.microservicios.empleados.exception.EmpleadoYaExisteException;
import com.microservicios.empleados.exception.EmpleadoNoEncontradoException;
import com.microservicios.empleados.model.Empleado;
import com.microservicios.empleados.model.EventoEmpleado;
import com.microservicios.empleados.repository.EmpleadoRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class EmpleadoService {
    private final EmpleadoRepository empleadoRepository;
    private final RedisTemplate<String, Object> redisTemplate;
    private static final String STREAM_KEY = "eventos:empleados";

    @Transactional
    public Empleado crearEmpleado(Empleado empleado) {
        if (empleadoRepository.existsByEmail(empleado.getEmail())) {
            throw new EmpleadoYaExisteException("El email " + empleado.getEmail() + " ya está registrado");
        }
        if (empleadoRepository.existsByNumeroEmpleado(empleado.getNumeroEmpleado())) {
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
        EventoEmpleado evento = EventoEmpleado.builder()
                .tipo("EMPLEADO_CREADO")
                .datos(empleado)
                .timestamp(LocalDateTime.now())
                .build();
        redisTemplate.opsForStream().add(STREAM_KEY, (Map<? extends Object, ? extends Object>) evento);
    }
}
