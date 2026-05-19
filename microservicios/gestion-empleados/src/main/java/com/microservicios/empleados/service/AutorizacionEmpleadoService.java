package com.microservicios.empleados.service;

import com.microservicios.empleados.exception.ForbiddenOperationException;
import com.microservicios.empleados.model.Empleado;
import com.microservicios.empleados.repository.EmpleadoRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class AutorizacionEmpleadoService {

    private static final String DEPARTAMENTO_RRHH = "DEP001";

    private final EmpleadoRepository empleadoRepository;

    public void asegurarAccesoTotal() {
        Empleado autenticado = obtenerEmpleadoAutenticado();
        if (!esRecursosHumanos(autenticado)) {
            throw new ForbiddenOperationException("No tienes permisos para esta operación.");
        }
    }

    public void asegurarAccesoPropioORecursosHumanosPorEmpleadoId(String empleadoId) {
        Empleado autenticado = obtenerEmpleadoAutenticado();
        if (esRecursosHumanos(autenticado)) {
            return;
        }

        String empleadoObjetivo = limpiar(empleadoId);
        if (!limpiar(autenticado.getNumeroEmpleado()).equalsIgnoreCase(empleadoObjetivo)) {
            throw new ForbiddenOperationException("Solo puedes acceder a tu propia información.");
        }
    }

    public void asegurarAccesoPropioORecursosHumanosPorEmail(String email) {
        Empleado autenticado = obtenerEmpleadoAutenticado();
        if (esRecursosHumanos(autenticado)) {
            return;
        }

        String emailObjetivo = limpiar(email).toLowerCase();
        if (!limpiar(autenticado.getEmail()).toLowerCase().equals(emailObjetivo)) {
            throw new ForbiddenOperationException("Solo puedes acceder a tu propia información.");
        }
    }

    public Empleado obtenerEmpleadoAutenticado() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || authentication.getName() == null || authentication.getName().isBlank()) {
            throw new ForbiddenOperationException("No se pudo identificar al usuario autenticado.");
        }

        String emailAutenticado = authentication.getName().trim();
        return empleadoRepository.findByEmail(emailAutenticado)
                .orElseThrow(() -> new ForbiddenOperationException("No se encontró un empleado asociado al usuario autenticado."));
    }

    public boolean esRecursosHumanos(Empleado empleado) {
        return limpiar(empleado.getDepartamentoId()).equalsIgnoreCase(DEPARTAMENTO_RRHH);
    }

    private String limpiar(String valor) {
        return valor == null ? "" : valor.trim();
    }
}