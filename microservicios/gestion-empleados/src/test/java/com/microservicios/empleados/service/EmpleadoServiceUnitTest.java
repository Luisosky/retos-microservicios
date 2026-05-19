package com.microservicios.empleados.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.microservicios.empleados.client.DepartamentoClient;
import com.microservicios.empleados.dto.EmpleadoUpdateRequest;
import com.microservicios.empleados.enums.EstadoEmpleado;
import com.microservicios.empleados.exception.DepartamentoNoValidoException;
import com.microservicios.empleados.exception.EmpleadoNoEncontradoException;
import com.microservicios.empleados.exception.EmpleadoYaExisteException;
import com.microservicios.empleados.model.Empleado;
import com.microservicios.empleados.repository.EmpleadoRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.test.util.ReflectionTestUtils;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class EmpleadoServiceUnitTest {

    @Mock
    private EmpleadoRepository empleadoRepository;

    @Mock
    private RabbitTemplate rabbitTemplate;

    @Mock
    private ObjectMapper objectMapper;

    @Mock
    private DepartamentoClient departamentoClient;

    @InjectMocks
    private EmpleadoService empleadoService;

    @BeforeEach
    void setUp() {
        ReflectionTestUtils.setField(empleadoService, "empleadosExchange", "empleados.events");
    }

    @Test
    void crearEmpleadoAsignaEstadoActivoYPublicaEvento() throws Exception {
        Empleado empleado = empleadoBase();
        when(departamentoClient.existeDepartamento("DEP001")).thenReturn(true);
        when(empleadoRepository.existsByEmail("ana@empresa.com")).thenReturn(false);
        when(empleadoRepository.existsById("EMP001")).thenReturn(false);
        when(empleadoRepository.save(empleado)).thenReturn(empleado);
        when(objectMapper.writeValueAsString(any())).thenReturn("{}");

        Empleado resultado = empleadoService.crearEmpleado(empleado);

        assertEquals(EstadoEmpleado.ACTIVO, resultado.getEstado());
        verify(empleadoRepository).save(empleado);
        verify(rabbitTemplate).convertAndSend(eq("empleados.events"), eq("empleado.creado"), eq("{}"));
    }

    @Test
    void crearEmpleadoRechazaDepartamentoInvalido() {
        Empleado empleado = empleadoBase();
        when(departamentoClient.existeDepartamento("DEP001")).thenReturn(false);

        assertThrows(DepartamentoNoValidoException.class, () -> empleadoService.crearEmpleado(empleado));
        verify(empleadoRepository, never()).save(any(Empleado.class));
    }

    @Test
    void crearEmpleadoRechazaEmailRepetido() {
        Empleado empleado = empleadoBase();
        when(departamentoClient.existeDepartamento("DEP001")).thenReturn(true);
        when(empleadoRepository.existsByEmail("ana@empresa.com")).thenReturn(true);

        assertThrows(EmpleadoYaExisteException.class, () -> empleadoService.crearEmpleado(empleado));
    }

    @Test
    void obtenerEmpleadoPorIdLanzaSiNoExiste() {
        when(empleadoRepository.findById("EMP999")).thenReturn(Optional.empty());

        assertThrows(EmpleadoNoEncontradoException.class, () -> empleadoService.obtenerEmpleadoPorId("EMP999"));
    }

    @Test
    void actualizarEmpleadoActualizaDatos() {
        Empleado existente = empleadoBase();
        EmpleadoUpdateRequest request = new EmpleadoUpdateRequest();
        request.setEmail("ana.nueva@empresa.com");
        request.setNombre("Ana Maria");
        request.setApellido("Perez");
        request.setCargo("Lider");
        request.setArea("TI");
        request.setDepartamentoId("DEP002");
        request.setFechaIngreso(LocalDate.of(2024, 1, 15));
        request.setEstado(EstadoEmpleado.RETIRADO);

        when(empleadoRepository.findById("EMP001")).thenReturn(Optional.of(existente));
        when(empleadoRepository.existsByEmail("ana.nueva@empresa.com")).thenReturn(false);
        when(departamentoClient.existeDepartamento("DEP002")).thenReturn(true);
        when(empleadoRepository.save(existente)).thenReturn(existente);

        Empleado actualizado = empleadoService.actualizarEmpleado("EMP001", request);

        assertEquals("ana.nueva@empresa.com", actualizado.getEmail());
        assertEquals("Ana Maria", actualizado.getNombre());
        assertEquals("DEP002", actualizado.getDepartamentoId());
        assertEquals(EstadoEmpleado.RETIRADO, actualizado.getEstado());
    }

    @Test
    void obtenerTodosEmpleadosRetornaLista() {
        when(empleadoRepository.findAll()).thenReturn(List.of(empleadoBase()));

        List<Empleado> empleados = empleadoService.obtenerTodosEmpleados();

        assertEquals(1, empleados.size());
    }

    private Empleado empleadoBase() {
        Empleado empleado = new Empleado();
        empleado.setNumeroEmpleado("EMP001");
        empleado.setEmail("ana@empresa.com");
        empleado.setNombre("Ana");
        empleado.setApellido("Perez");
        empleado.setCargo("Analista");
        empleado.setArea("TI");
        empleado.setDepartamentoId("DEP001");
        empleado.setFechaIngreso(LocalDate.of(2024, 1, 15));
        return empleado;
    }
}