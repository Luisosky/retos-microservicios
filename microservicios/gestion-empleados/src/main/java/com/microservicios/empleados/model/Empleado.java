package com.microservicios.empleados.model;

import com.microservicios.empleados.enums.EstadoEmpleado;
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
    private String numeroEmpleado;

    @Indexed(unique = true)
    private String email;

    private String nombre;
    private String apellido;
    private String cargo;
    private String area;
    private LocalDate fechaIngreso;
    private EstadoEmpleado estado;
}
