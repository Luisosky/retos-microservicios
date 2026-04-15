package com.microservicios.empleados.client;

import com.microservicios.empleados.dto.DepartamentoDto;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Component;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.RestTemplate;

/**
 * Cliente HTTP para comunicarse con el microservicio de departamentos
 */
@Component
@RequiredArgsConstructor
@Slf4j
public class DepartamentoClient {

    private final RestTemplate restTemplate;

    @Value("${services.departamentos.url}")
    private String departamentosServiceUrl;

    /**
     * Verifica si un departamento existe consultando al servicio de departamentos
     *
     * @param departamentoId ID del departamento a verificar
     * @return true si el departamento existe y está activo, false en caso contrario
     */
    public boolean existeDepartamento(String departamentoId) {
        try {
            // Limpiar y validar el departamentoId
            if (departamentoId == null || departamentoId.trim().isEmpty()) {
                log.warn("ID de departamento vacío o nulo");
                return false;
            }
            
            String idLimpio = departamentoId.trim();
            String url = departamentosServiceUrl + "/departamentos/" + idLimpio;
            log.info("Consultando departamento en: {}", url);

            ResponseEntity<DepartamentoDto> response = restTemplate.getForEntity(
                    url,
                    DepartamentoDto.class
            );

            if (response.getStatusCode() == HttpStatus.OK && response.getBody() != null) {
                DepartamentoDto departamento = response.getBody();
                log.info("Departamento encontrado: {} - {}", departamento.getId(), departamento.getNombre());
                return departamento.getActivo() != null ? departamento.getActivo() : true;
            }

            return false;

        } catch (HttpClientErrorException.NotFound e) {
            log.warn("Departamento con id '{}' no encontrado", departamentoId);
            return false;
        } catch (Exception e) {
            log.error("Error al consultar el servicio de departamentos: {}", e.getMessage(), e);
            throw new RuntimeException("Error al comunicarse con el servicio de departamentos: " + e.getMessage(), e);
        }
    }

    /**
     * Obtiene la información completa de un departamento
     *
     * @param departamentoId ID del departamento
     * @return DTO con la información del departamento o null si no existe
     */
    public DepartamentoDto obtenerDepartamento(String departamentoId) {
        try {
            // Limpiar y validar el departamentoId
            if (departamentoId == null || departamentoId.trim().isEmpty()) {
                log.warn("ID de departamento vacío o nulo");
                return null;
            }
            
            String idLimpio = departamentoId.trim();
            String url = departamentosServiceUrl + "/departamentos/" + idLimpio;
            ResponseEntity<DepartamentoDto> response = restTemplate.getForEntity(
                    url,
                    DepartamentoDto.class
            );

            return response.getBody();

        } catch (HttpClientErrorException.NotFound e) {
            return null;
        } catch (Exception e) {
            log.error("Error al obtener departamento: {}", e.getMessage(), e);
            throw new RuntimeException("Error al comunicarse con el servicio de departamentos", e);
        }
    }
}
