package com.microservicios.empleados.exception;

import com.fasterxml.jackson.annotation.JsonInclude;
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
@JsonInclude(JsonInclude.Include.NON_NULL)
@Schema(
        name = "ErrorResponse",
        description = "Respuesta de error del servidor",
        example = "{\"mensaje\": \"El empleado con id EMP001 no existe\", \"status\": 404, " +
                "\"error\": \"Not Found\", \"timestamp\": \"2024-02-24T21:47:34.774-05:00\"}"
)
public class ErrorResponse {
    @Schema(
            description = "Mensaje de error detallado",
            example = "El empleado con id EMP001 no existe"
    )
    private String mensaje;

    @Schema(
            description = "Código de estado HTTP",
            example = "404"
    )
    private Integer status;

    @Schema(
            description = "Tipo de error",
            example = "Not Found"
    )
    private String error;

    @Schema(
            description = "Timestamp de cuando ocurrió el error",
            example = "2024-02-24T21:47:34.774-05:00"
    )
    private LocalDateTime timestamp;

    // Constructor simplificado para compatibilidad hacia atrás
    public ErrorResponse(String mensaje) {
        this.mensaje = mensaje;
        this.timestamp = LocalDateTime.now();
    }
}
