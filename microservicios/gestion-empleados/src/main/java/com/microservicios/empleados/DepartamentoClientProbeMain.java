package com.microservicios.empleados;

import com.microservicios.empleados.dto.DepartamentoDto;
import org.springframework.http.ResponseEntity;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.web.client.RestTemplate;

/**
 * Main de prueba para validar la comunicacion con el servicio de departamentos.
 */
public class DepartamentoClientProbeMain {

    private static final String DEFAULT_DEPARTAMENTOS_URL = "http://localhost:8081";

    public static void main(String[] args) {
        String departamentoId;

        if (args.length == 0 || args[0] == null || args[0].trim().isEmpty()) {
            departamentoId = "Dep001"; // Valor por defecto para pruebas
            System.out.println("No se proporcionó departamentoId, usando valor por defecto: " + departamentoId);
            System.out.println("Uso: DepartamentoClientProbeMain <departamentoId>");
            System.out.println();
        } else {
            departamentoId = args[0].trim();
        }
        String baseUrl = resolveBaseUrl();
        String endpoint = baseUrl + "/departamentos/" + departamentoId;

        RestTemplate restTemplate = new RestTemplate();

        System.out.println("Consultando departamento en: " + endpoint);

        try {
            ResponseEntity<DepartamentoDto> response = restTemplate.getForEntity(endpoint, DepartamentoDto.class);
            DepartamentoDto departamento = response.getBody();

            if (departamento == null) {
                System.out.println("Respuesta OK pero sin cuerpo.");
                return;
            }

            System.out.println("Departamento encontrado:");
            System.out.println("- id: " + departamento.getId());
            System.out.println("- nombre: " + departamento.getNombre());
            System.out.println("- descripcion: " + departamento.getDescripcion());
            System.out.println("- activo: " + departamento.getActivo());
        } catch (HttpClientErrorException.NotFound ex) {
            System.out.println("No existe un departamento con id: " + departamentoId);
        } catch (ResourceAccessException ex) {
            System.out.println("No se pudo conectar con el servicio de departamentos.");
            System.out.println("Verifica la URL en DEPARTAMENTOS_SERVICE_URL o -Ddepartamentos.url.");
            System.out.println("Detalle: " + ex.getMessage());
        } catch (Exception ex) {
            System.out.println("Error al consultar el servicio de departamentos: " + ex.getMessage());
        }
    }

    private static String resolveBaseUrl() {
        String bySystemProperty = System.getProperty("departamentos.url");
        if (bySystemProperty != null && !bySystemProperty.trim().isEmpty()) {
            return bySystemProperty.trim();
        }

        String byEnvVar = System.getenv("DEPARTAMENTOS_SERVICE_URL");
        if (byEnvVar != null && !byEnvVar.trim().isEmpty()) {
            return byEnvVar.trim();
        }

        return DEFAULT_DEPARTAMENTOS_URL;
    }
}

