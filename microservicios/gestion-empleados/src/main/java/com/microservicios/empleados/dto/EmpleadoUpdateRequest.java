package com.microservicios.empleados.dto;

import com.microservicios.empleados.enums.EstadoEmpleado;
import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

import java.time.LocalDate;

@Data
@Schema(
        name = "EmpleadoUpdateRequest",
        description = "Payload para actualizar información de un empleado"
)
public class EmpleadoUpdateRequest {

    @NotBlank(message = "El email es requerido")
    @Email(message = "El email debe ser válido")
    private String email;

    @NotBlank(message = "El nombre es requerido")
    private String nombre;

    @NotBlank(message = "El apellido es requerido")
    private String apellido;

    @NotBlank(message = "El cargo es requerido")
    private String cargo;

    @NotBlank(message = "El área es requerida")
    private String area;

    @NotBlank(message = "El ID del departamento es requerido")
    private String departamentoId;

    @NotNull(message = "La fecha de ingreso es requerida")
    private LocalDate fechaIngreso;

    private EstadoEmpleado estado;
}