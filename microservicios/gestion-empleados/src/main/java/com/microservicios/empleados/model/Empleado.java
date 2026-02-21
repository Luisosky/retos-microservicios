package com.microservicios.empleados.model;

import com.microservicios.empleados.enums.EstadoEmpleado;
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
public class Empleado {
    @Id
    @NotBlank(message = "El número de empleado es requerido")
    private String numeroEmpleado;

    @Indexed(unique = true)
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

    @NotNull(message = "La fecha de ingreso es requerida")
    private LocalDate fechaIngreso;

    private EstadoEmpleado estado;
}
