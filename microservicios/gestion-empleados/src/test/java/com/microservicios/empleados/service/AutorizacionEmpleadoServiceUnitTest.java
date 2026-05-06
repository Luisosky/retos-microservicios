package com.microservicios.empleados.service;

import com.microservicios.empleados.exception.ForbiddenOperationException;
import com.microservicios.empleados.model.Empleado;
import com.microservicios.empleados.repository.EmpleadoRepository;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;

import java.util.Optional;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class AutorizacionEmpleadoServiceUnitTest {

    @Mock
    private EmpleadoRepository empleadoRepository;

    @InjectMocks
    private AutorizacionEmpleadoService autorizacionEmpleadoService;

    @AfterEach
    void tearDown() {
        SecurityContextHolder.clearContext();
    }

    @Test
    void asegurarAccesoTotalPermiteRecursosHumanos() {
        autenticado("rrhh@empresa.com", "DEP001");

        assertDoesNotThrow(() -> autorizacionEmpleadoService.asegurarAccesoTotal());
    }

    @Test
    void asegurarAccesoTotalRechazaUsuarioNormal() {
        autenticado("ana@empresa.com", "DEP002");

        assertThrows(ForbiddenOperationException.class, () -> autorizacionEmpleadoService.asegurarAccesoTotal());
    }

    @Test
    void asegurarAccesoPropioPermiteMismoEmpleado() {
        autenticado("ana@empresa.com", "DEP002");

        assertDoesNotThrow(() -> autorizacionEmpleadoService.asegurarAccesoPropioORecursosHumanosPorEmail("ana@empresa.com"));
    }

    @Test
    void asegurarAccesoPropioRechazaEmpleadoDistinto() {
        autenticado("ana@empresa.com", "DEP002");

        assertThrows(ForbiddenOperationException.class,
                () -> autorizacionEmpleadoService.asegurarAccesoPropioORecursosHumanosPorEmpleadoId("EMP999"));
    }

    @Test
    void obtenerEmpleadoAutenticadoDevuelveEmpleado() {
        autenticado("ana@empresa.com", "DEP002");
        when(empleadoRepository.findByEmail("ana@empresa.com")).thenReturn(Optional.of(empleado("ana@empresa.com", "DEP002")));

        assertDoesNotThrow(() -> autorizacionEmpleadoService.obtenerEmpleadoAutenticado());
    }

    private void autenticado(String email, String departamentoId) {
        SecurityContextHolder.getContext().setAuthentication(
                new UsernamePasswordAuthenticationToken(email, "N/A")
        );
        when(empleadoRepository.findByEmail(email)).thenReturn(Optional.of(empleado(email, departamentoId)));
    }

    private Empleado empleado(String email, String departamentoId) {
        Empleado empleado = new Empleado();
        empleado.setNumeroEmpleado("EMP001");
        empleado.setEmail(email);
        empleado.setDepartamentoId(departamentoId);
        return empleado;
    }
}