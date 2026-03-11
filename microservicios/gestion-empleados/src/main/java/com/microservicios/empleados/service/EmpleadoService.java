package com.microservicios.empleados.service;

import com.microservicios.empleados.client.DepartamentoClient;
import com.microservicios.empleados.enums.EstadoEmpleado;
import com.microservicios.empleados.exception.DepartamentoNoValidoException;
import com.microservicios.empleados.exception.EmpleadoYaExisteException;
import com.microservicios.empleados.exception.EmpleadoNoEncontradoException;
import com.microservicios.empleados.model.Empleado;
import com.microservicios.empleados.repository.EmpleadoRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.LinkedHashMap;
import java.util.Map;
import java.util.List;

@Service
@RequiredArgsConstructor
@Slf4j
public class EmpleadoService {
    private final EmpleadoRepository empleadoRepository;
    private final RabbitTemplate rabbitTemplate;
    private final ObjectMapper objectMapper;
    private final DepartamentoClient departamentoClient;

    @Value("${app.messaging.exchange:empleados.events}")
    private String empleadosExchange;

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

    @Transactional
    public void eliminarEmpleado(String id) {
        Empleado empleado = obtenerEmpleadoPorId(id);
        empleadoRepository.delete(empleado);
        log.info("Empleado eliminado exitosamente: {}", id);

        publicarEventoEmpleadoEliminado(empleado);
    }

    public Empleado obtenerEmpleadoPorId(String id) {
        return empleadoRepository.findById(id)
                .orElseThrow(() -> new EmpleadoNoEncontradoException("El empleado con id " + id + " no existe"));
    }

    private void publicarEventoEmpleadoCreado(Empleado empleado) {
        try {
            Map<String, Object> payload = new LinkedHashMap<>();
            payload.put("id", empleado.getNumeroEmpleado());
            payload.put("nombre", empleado.getNombre());
            payload.put("email", empleado.getEmail());
            payload.put("departamentoId", empleado.getDepartamentoId());
            payload.put("fechaIngreso", empleado.getFechaIngreso());

            rabbitTemplate.convertAndSend(
                    empleadosExchange,
                    "empleado.creado",
                    objectMapper.writeValueAsString(payload)
            );
            log.info("Evento publicado: empleado.creado para empleado {}", empleado.getNumeroEmpleado());
        } catch (Exception e) {
            // Si falla el broker, no se revierte la operación de base de datos.
            log.error("Error al publicar evento empleado.creado para {}: {}", empleado.getNumeroEmpleado(), e.getMessage());
        }
    }

    private void publicarEventoEmpleadoEliminado(Empleado empleado) {
        try {
            Map<String, Object> payload = new LinkedHashMap<>();
            payload.put("id", empleado.getNumeroEmpleado());
            payload.put("nombre", empleado.getNombre());
            payload.put("email", empleado.getEmail());

            rabbitTemplate.convertAndSend(
                    empleadosExchange,
                    "empleado.eliminado",
                    objectMapper.writeValueAsString(payload)
            );
            log.info("Evento publicado: empleado.eliminado para empleado {}", empleado.getNumeroEmpleado());
        } catch (Exception e) {
            // Si falla el broker, no se revierte la operación de base de datos.
            log.error("Error al publicar evento empleado.eliminado para {}: {}", empleado.getNumeroEmpleado(), e.getMessage());
        }
    }

    public List<Empleado> obtenerTodosEmpleados() {
        return empleadoRepository.findAll();
    }
}
