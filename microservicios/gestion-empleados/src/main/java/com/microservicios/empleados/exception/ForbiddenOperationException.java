package com.microservicios.empleados.exception;

public class ForbiddenOperationException extends RuntimeException {

    public ForbiddenOperationException(String mensaje) {
        super(mensaje);
    }
}