package com.microservicios.empleados.exception;

/**
 * Excepción lanzada cuando se intenta registrar un empleado con un departamento inválido o inexistente
 */
public class DepartamentoNoValidoException extends RuntimeException {
    
    public DepartamentoNoValidoException(String mensaje) {
        super(mensaje);
    }
    
    public DepartamentoNoValidoException(String mensaje, Throwable causa) {
        super(mensaje, causa);
    }
}
