package com.microservicios.empleados.controller;

import com.microservicios.empleados.model.Empleado;
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

import java.util.List;

@RestController
@RequestMapping("/empleado")
@RequiredArgsConstructor
@Tag(name = "Empleados", description = "API para gestión de empleados")
public class EmpleadoController {
    private final EmpleadoService empleadoService;

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
        Empleado empleado = empleadoService.obtenerEmpleadoPorId(id);
        return ResponseEntity.status(HttpStatus.OK).body(empleado);
    }
}
