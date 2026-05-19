package com.microservicios.empleados.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * DTO para recibir la respuesta del servicio de departamentos
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class DepartamentoDto {
    private String id;
    private String nombre;
    private String descripcion;
    private Boolean activo;
}
