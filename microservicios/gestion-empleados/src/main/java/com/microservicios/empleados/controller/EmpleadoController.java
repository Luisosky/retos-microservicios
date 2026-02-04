package com.microservicios.empleados.controller;

import com.microservicios.empleados.model.Empleado;
import com.microservicios.empleados.service.EmpleadoService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/empleado")
@RequiredArgsConstructor
public class EmpleadoController {
    private final EmpleadoService empleadoService;

    @PostMapping
    public ResponseEntity<Empleado> registrarEmpleado(@Valid @RequestBody Empleado empleado) {
        Empleado empleadoCreado = empleadoService.crearEmpleado(empleado);
        return ResponseEntity.status(HttpStatus.OK).body(empleadoCreado);
    }

    @GetMapping("/{id}")
    public ResponseEntity<Empleado> consultarEmpleado(@PathVariable String id) {
        Empleado empleado = empleadoService.obtenerEmpleadoPorId(id);
        return ResponseEntity.status(HttpStatus.OK).body(empleado);
    }
}
