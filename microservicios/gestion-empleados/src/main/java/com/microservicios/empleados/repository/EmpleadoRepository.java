package com.microservicios.empleados.repository;

import com.microservicios.empleados.model.Empleado;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface EmpleadoRepository extends MongoRepository<Empleado, String> {
    Optional<Empleado> findByNumeroEmpleado(String numeroEmpleado);
    Optional<Empleado> findByEmail(String email);
    boolean existsByEmail(String email);
}
