package com.microservicios.empleados.model;

import com.microservicios.empleados.enums.EstadoEmpleado;
import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.index.Indexed;
import org.springframework.data.mongodb.core.mapping.Document;

import java.time.LocalDate;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Document(collection = "empleados")
@Schema(
        name = "Empleado",
        description = "Modelo que representa un empleado del sistema",
        example = "{\"numeroEmpleado\": \"EMP001\", \"nombre\": \"Juan\", \"apellido\": \"Pérez\", " +
                "\"email\": \"juan.perez@empresa.com\", \"cargo\": \"Desarrollador\", \"area\": \"TI\", " +
                "\"departamentoId\": \"DEP001\", \"fechaIngreso\": \"2024-01-15\", \"estado\": \"ACTIVO\"}"
)
public class Empleado {
    @Id
    @NotBlank(message = "El número de empleado es requerido")
    @Schema(
            description = "Identificador único del empleado",
            example = "EMP001",
            requiredMode = Schema.RequiredMode.REQUIRED
    )
    private String numeroEmpleado;

    @Indexed(unique = true)
    @NotBlank(message = "El email es requerido")
    @Email(message = "El email debe ser válido")
    @Schema(
            description = "Correo electrónico único del empleado",
            example = "juan.perez@empresa.com",
            requiredMode = Schema.RequiredMode.REQUIRED
    )
    private String email;

    @NotBlank(message = "El nombre es requerido")
    @Schema(
            description = "Nombre del empleado",
            example = "Juan",
            requiredMode = Schema.RequiredMode.REQUIRED
    )
    private String nombre;

    @NotBlank(message = "El apellido es requerido")
    @Schema(
            description = "Apellido del empleado",
            example = "Pérez",
            requiredMode = Schema.RequiredMode.REQUIRED
    )
    private String apellido;

    @NotBlank(message = "El cargo es requerido")
    @Schema(
            description = "Puesto o cargo del empleado",
            example = "Desarrollador Senior",
            requiredMode = Schema.RequiredMode.REQUIRED
    )
    private String cargo;

    @NotBlank(message = "El área es requerida")
    @Schema(
            description = "Departamento o área del empleado",
            example = "Tecnología e Innovación",
            requiredMode = Schema.RequiredMode.REQUIRED
    )
    private String area;

    @NotBlank(message = "El ID del departamento es requerido")
    @Schema(
            description = "Identificador del departamento al que pertenece el empleado",
            example = "DEP001",
            requiredMode = Schema.RequiredMode.REQUIRED
    )
    private String departamentoId;

    @NotNull(message = "La fecha de ingreso es requerida")
    @Schema(
            description = "Fecha de ingreso del empleado (formato: yyyy-MM-dd)",
            example = "2024-01-15",
            requiredMode = Schema.RequiredMode.REQUIRED
    )
    private LocalDate fechaIngreso;

    @Schema(
            description = "Estado actual del empleado (ACTIVO, INACTIVO, LICENCIA, etc.)",
            example = "ACTIVO",
            requiredMode = Schema.RequiredMode.NOT_REQUIRED
    )
    private EstadoEmpleado estado;
}
