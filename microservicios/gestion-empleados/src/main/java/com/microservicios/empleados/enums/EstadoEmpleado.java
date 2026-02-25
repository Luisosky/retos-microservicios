package com.microservicios.empleados.enums;

import io.swagger.v3.oas.annotations.media.Schema;

/**
 * Estados posibles de un empleado en el sistema.
 *
 * Valores válidos:
 * - ACTIVO: Empleado en servicio activo
 * - EN_VACACIONES: Empleado en período de vacaciones
 * - RETIRADO: Empleado retirado del sistema
 */
@Schema(
        name = "EstadoEmpleado",
        description = "Estados posibles de un empleado",
        example = "ACTIVO"
)
public enum EstadoEmpleado {
    /**
     * Empleado activo en la organización
     */
    ACTIVO,

    /**
     * Empleado en período de vacaciones
     */
    EN_VACACIONES,

    /**
     * Empleado retirado del sistema
     */
    RETIRADO
}
