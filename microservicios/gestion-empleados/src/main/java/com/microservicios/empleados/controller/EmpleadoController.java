package com.microservicios.empleados.controller;

import com.microservicios.empleados.dto.EmpleadoUpdateRequest;
import com.microservicios.empleados.model.Empleado;
import com.microservicios.empleados.service.AutorizacionEmpleadoService;
import com.microservicios.empleados.service.EmpleadoService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/empleado")
@RequiredArgsConstructor
@Tag(name = "Empleados", description = "API para gestión de empleados")
public class EmpleadoController {
    private final EmpleadoService empleadoService;
        private final AutorizacionEmpleadoService autorizacionEmpleadoService;

    @PostMapping
    @Operation(
            summary = "Registrar nuevo empleado",
            description = "Crea un nuevo empleado en la base de datos. Los campos requeridos son: " +
                    "numeroEmpleado, nombre, apellido, email, cargo, área, departamentoId, fechaIngreso y estado. " +
                    "El email debe ser único en el sistema. " +
                    "El departamentoId será validado consultando al servicio de departamentos."
    )
    @ApiResponses(value = {
            @ApiResponse(
                    responseCode = "201",
                    description = "Empleado registrado exitosamente",
                    content = @Content(
                            mediaType = "application/json",
                            schema = @Schema(implementation = Empleado.class)
                    )
            ),
            @ApiResponse(
                    responseCode = "400",
                    description = "Solicitud inválida. Validaciones fallidas:\n" +
                            "- Email duplicado\n" +
                            "- Número de empleado duplicado\n" +
                            "- Campos requeridos faltantes\n" +
                            "- Formato de email inválido\n" +
                            "- Departamento no existe o no está activo"
            ),
            @ApiResponse(
                    responseCode = "500",
                    description = "Error interno del servidor"
            )
    })
    public ResponseEntity<Empleado> registrarEmpleado(
            @Valid @RequestBody Empleado empleado
    ) {
                autorizacionEmpleadoService.asegurarAccesoTotal();
        Empleado empleadoCreado = empleadoService.crearEmpleado(empleado);
        return ResponseEntity.status(HttpStatus.CREATED).body(empleadoCreado);
    }

    @GetMapping
    @Operation(
            summary = "Listar todos los empleados",
            description = "Obtiene la lista completa de todos los empleados registrados en la base de datos."
    )
    @ApiResponses(value = {
            @ApiResponse(
                    responseCode = "200",
                    description = "Lista de empleados obtenida exitosamente",
                    content = @Content(
                            mediaType = "application/json",
                            schema = @Schema(implementation = Empleado.class)
                    )
            ),
            @ApiResponse(
                    responseCode = "500",
                    description = "Error interno del servidor"
            )
    })
    public ResponseEntity<List<Empleado>> listarEmpleados() {
                autorizacionEmpleadoService.asegurarAccesoTotal();
        List<Empleado> empleados = empleadoService.obtenerTodosEmpleados();
        return ResponseEntity.status(HttpStatus.OK).body(empleados);
    }

    @GetMapping("/{id}")
    @Operation(
            summary = "Obtener empleado por ID",
            description = "Obtiene los detalles de un empleado específico usando su número de empleado como identificador."
    )
    @ApiResponses(value = {
            @ApiResponse(
                    responseCode = "200",
                    description = "Empleado encontrado",
                    content = @Content(
                            mediaType = "application/json",
                            schema = @Schema(implementation = Empleado.class)
                    )
            ),
            @ApiResponse(
                    responseCode = "404",
                    description = "Empleado no encontrado con el ID proporcionado"
            ),
            @ApiResponse(
                    responseCode = "500",
                    description = "Error interno del servidor"
            )
    })
    public ResponseEntity<Empleado> consultarEmpleado(
            @Parameter(
                    name = "id",
                    description = "Número de empleado único (ej: EMP001)",
                    required = true,
                    example = "EMP001"
            )
            @PathVariable String id
    ) {
        autorizacionEmpleadoService.asegurarAccesoPropioORecursosHumanosPorEmpleadoId(id);
        Empleado empleado = empleadoService.obtenerEmpleadoPorId(id);
        return ResponseEntity.status(HttpStatus.OK).body(empleado);
    }

    @GetMapping("/email/{email:.+}")
    @Operation(
            summary = "Obtener empleado por email",
            description = "Obtiene los detalles de un empleado usando su correo electrónico como identificador."
    )
    public ResponseEntity<Empleado> consultarEmpleadoPorEmail(
            @PathVariable String email
    ) {
        autorizacionEmpleadoService.asegurarAccesoPropioORecursosHumanosPorEmail(email);
        Empleado empleado = empleadoService.obtenerEmpleadoPorEmail(email);
        return ResponseEntity.status(HttpStatus.OK).body(empleado);
    }

    @PutMapping("/{id}")
    @Operation(
            summary = "Actualizar empleado por ID",
            description = "Actualiza la información de un empleado por su número de empleado."
    )
    public ResponseEntity<Empleado> actualizarEmpleado(
            @PathVariable String id,
            @Valid @RequestBody EmpleadoUpdateRequest request
    ) {
        autorizacionEmpleadoService.asegurarAccesoPropioORecursosHumanosPorEmpleadoId(id);
        Empleado actualizado = empleadoService.actualizarEmpleado(id, request);
        return ResponseEntity.status(HttpStatus.OK).body(actualizado);
    }

    @PatchMapping("/{id}")
    @Operation(
            summary = "Actualizar parcialmente empleado por ID",
            description = "Alias de actualización para compatibilidad con clientes que usan PATCH."
    )
    public ResponseEntity<Empleado> actualizarEmpleadoParcial(
            @PathVariable String id,
            @Valid @RequestBody EmpleadoUpdateRequest request
    ) {
        autorizacionEmpleadoService.asegurarAccesoPropioORecursosHumanosPorEmpleadoId(id);
        Empleado actualizado = empleadoService.actualizarEmpleado(id, request);
        return ResponseEntity.status(HttpStatus.OK).body(actualizado);
    }

    @DeleteMapping("/{id}")
    @Operation(
            summary = "Eliminar empleado por ID",
            description = "Elimina un empleado por su número de empleado. Si la eliminación es exitosa, se publica el evento empleado.eliminado en RabbitMQ."
    )
    @ApiResponses(value = {
            @ApiResponse(
                    responseCode = "200",
                    description = "Empleado eliminado exitosamente y notificación publicada"
            ),
            @ApiResponse(
                    responseCode = "404",
                    description = "Empleado no encontrado con el ID proporcionado"
            ),
            @ApiResponse(
                    responseCode = "500",
                    description = "Error interno del servidor"
            )
    })
    public ResponseEntity<Map<String, Object>> eliminarEmpleado(
            @Parameter(
                    name = "id",
                    description = "Número de empleado único (ej: EMP001)",
                    required = true,
                    example = "EMP001"
            )
            @PathVariable String id
    ) {
                autorizacionEmpleadoService.asegurarAccesoTotal();
        empleadoService.eliminarEmpleado(id);
        Map<String, Object> response = new HashMap<>();
        response.put("mensaje", "Empleado eliminado exitosamente");
        response.put("empleadoId", id);
        response.put("notificacion", "Evento empleado.eliminado publicado en RabbitMQ");
        return ResponseEntity.ok(response);
    }
}
