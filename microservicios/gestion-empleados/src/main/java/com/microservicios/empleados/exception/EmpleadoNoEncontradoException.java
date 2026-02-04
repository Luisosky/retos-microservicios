package com.microservicios.empleados.exception;

public class EmpleadoNoEncontradoException extends RuntimeException {
    public EmpleadoNoEncontradoException(String message) {
        super(message);
    }
}
