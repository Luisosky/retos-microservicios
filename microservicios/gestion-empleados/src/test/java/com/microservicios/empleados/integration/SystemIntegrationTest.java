package com.microservicios.empleados.integration;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.*;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Tag;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.http.*;

import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.TimeUnit;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Pruebas de integración del sistema - Servicio de Empleados
 * Tests end-to-end del servicio de empleados
 * 
 * REQUISITOS:
 * - Los servicios deben estar ejecutándose (docker-compose up)
 * - Departamentos: http://localhost:8081
 * - Empleados: http://localhost:8080
 * 
 * NOTA: Las pruebas asumen que el departamento "IT" existe.
 * Si no existe, se creará automáticamente como prerequisito.
 */
/**
 * Tests E2E de integración del sistema.
 * REQUIERE servicios externos corriendo (docker-compose up).
 * NO se ejecutan en el pipeline CI (excluidos en pom.xml y Surefire).
 * Para correr manualmente: mvn test -Dgroups=integration
 */
@Tag("integration")
@Disabled("Requiere docker-compose up: empleados:8080 y departamentos:8081")
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
public class SystemIntegrationTest {

    private static final String DEPARTAMENTOS_URL = System.getenv().getOrDefault("DEPARTAMENTOS_URL", "http://localhost:8081");
    private static final String EMPLEADOS_URL = System.getenv().getOrDefault("EMPLEADOS_URL", "http://localhost:8080");
    
    private static final TestRestTemplate restTemplate = new TestRestTemplate();
    private static final ObjectMapper objectMapper = new ObjectMapper();
    
    private static final String TEST_DEPT_ID = "IT";
    private static final String TEST_EMPLEADO_ID = "E001";
    
    // Colores ANSI para output
    private static final String ANSI_RESET = "\u001B[0m";
    private static final String ANSI_GREEN = "\u001B[32m";
    private static final String ANSI_RED = "\u001B[31m";
    private static final String ANSI_YELLOW = "\u001B[33m";
    private static final String ANSI_BLUE = "\u001B[34m";
    
    @BeforeAll
    static void setup() throws InterruptedException {
        printHeader("VERIFICANDO DISPONIBILIDAD DE SERVICIOS");
        
        // Esperar a que los servicios estén disponibles
        boolean departamentosReady = waitForService("Departamentos", DEPARTAMENTOS_URL + "/docs", 30);
        boolean empleadosReady = waitForService("Empleados", EMPLEADOS_URL + "/docs", 30);
        
        if (!departamentosReady || !empleadosReady) {
            fail("Los servicios no están disponibles. Ejecute 'docker-compose up' primero.");
        }
        
        // Crear departamento prerequisito (si no existe)
        printHeader("CREANDO DEPARTAMENTO PREREQUISITO");
        crearDepartamentoPrerequisito();
        
        // Limpieza previa de empleados de prueba
        limpiarEmpleados();
    }
    
    @AfterAll
    static void tearDown() {
        printHeader("LIMPIEZA DE DATOS DE PRUEBA");
        limpiarEmpleados();
    }
    
    private static void crearDepartamentoPrerequisito() {
        printTest("Crear departamento prerequisito '" + TEST_DEPT_ID + "'");
        
        // Primero verificar si el departamento ya existe
        try {
            ResponseEntity<String> getResponse = restTemplate.getForEntity(
                DEPARTAMENTOS_URL + "/departamentos/" + TEST_DEPT_ID,
                String.class
            );
            
            if (getResponse.getStatusCode() == HttpStatus.OK) {
                printSuccess("Departamento '" + TEST_DEPT_ID + "' ya existe");
                return;
            }
        } catch (Exception e) {
            // El departamento no existe, lo crearemos
        }
        
        // Crear el departamento
        Map<String, String> departamento = new HashMap<>();
        departamento.put("id", TEST_DEPT_ID);
        departamento.put("nombre", "Tecnología");
        departamento.put("descripcion", "Departamento de TI");
        
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        HttpEntity<Map<String, String>> request = new HttpEntity<>(departamento, headers);
        
        try {
            ResponseEntity<String> response = restTemplate.postForEntity(
                DEPARTAMENTOS_URL + "/departamentos",
                request,
                String.class
            );
            
            if (response.getStatusCode().is2xxSuccessful()) {
                printSuccess("Departamento prerequisito creado (Status: " + response.getStatusCode().value() + ")");
            } else {
                printError("No se pudo crear departamento prerequisito (Status: " + response.getStatusCode().value() + ")");
            }
        } catch (Exception e) {
            printError("Error al crear departamento prerequisito: " + e.getMessage());
        }
    }
    
    private static void limpiarEmpleados() {
        try {
            printTest("Eliminar empleado " + TEST_EMPLEADO_ID);
            restTemplate.delete(EMPLEADOS_URL + "/empleados/" + TEST_EMPLEADO_ID);
            printSuccess("Empleado eliminado o no existente");
        } catch (Exception e) {
            printInfo("No se pudo eliminar empleado: " + e.getMessage());
        }
    }
    
    // MÉTODO DEPRECADO - Ya no se usa
    @Deprecated
    private static void cleanup() {
        limpiarEmpleados();
    }
    
    private static boolean waitForService(String serviceName, String url, int maxAttempts) throws InterruptedException {
        printTest("Esperando servicio " + serviceName);
        
        for (int i = 1; i <= maxAttempts; i++) {
            try {
                ResponseEntity<String> response = restTemplate.getForEntity(url, String.class);
                if (response.getStatusCode() == HttpStatus.OK) {
                    printSuccess("Servicio " + serviceName + " disponible");
                    return true;
                }
            } catch (Exception e) {
                if (i < maxAttempts) {
                    printInfo("Intento " + i + "/" + maxAttempts + ", esperando 2s...");
                    TimeUnit.SECONDS.sleep(2);
                }
            }
        }
        
        printError("Servicio " + serviceName + " no disponible después de " + maxAttempts + " intentos");
        return false;
    }
    
    
    @Test
    @Order(1)
    @DisplayName("Test 1: Crear empleado con departamento válido")
    void test1_crearEmpleadoValido() {
        printHeader("TEST 1: CREAR EMPLEADO CON DEPARTAMENTO VÁLIDO");
        
        // Preparar datos
        Map<String, String> empleado = new HashMap<>();
        empleado.put("id", TEST_EMPLEADO_ID);
        empleado.put("nombre", "Juan Pérez");
        empleado.put("email", "juan@empresa.com");
        empleado.put("departamentoId", TEST_DEPT_ID);
        
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        HttpEntity<Map<String, String>> request = new HttpEntity<>(empleado, headers);
        
        // Ejecutar
        ResponseEntity<String> response = restTemplate.postForEntity(
            EMPLEADOS_URL + "/empleados",
            request,
            String.class
        );
        
        // Verificar
        assertTrue(response.getStatusCode().is2xxSuccessful(),
            "Empleado debe crearse exitosamente con departamento válido");
        
        printSuccess("Empleado creado exitosamente (Status: " + response.getStatusCode().value() + ")");
        printInfo("Respuesta: " + response.getBody());
    }
    
    @Test
    @Order(2)
    @DisplayName("Test 2: Verificar que el empleado existe")
    void test2_verificarEmpleadoExiste() {
        printHeader("TEST 2: VERIFICAR EMPLEADO EXISTE");
        
        // Ejecutar
        ResponseEntity<String> response = restTemplate.getForEntity(
            EMPLEADOS_URL + "/empleados/" + TEST_EMPLEADO_ID,
            String.class
        );
        
        // Verificar
        assertEquals(HttpStatus.OK, response.getStatusCode(),
            "Empleado debe existir");
        
        try {
            JsonNode empleado = objectMapper.readTree(response.getBody());
            assertEquals(TEST_EMPLEADO_ID, empleado.get("id").asText());
            assertEquals("Juan Pérez", empleado.get("nombre").asText());
            assertEquals("juan@empresa.com", empleado.get("email").asText());
            assertEquals(TEST_DEPT_ID, empleado.get("departamentoId").asText());
            
            printSuccess("Empleado encontrado: " + empleado.get("nombre").asText());
            printInfo("Email: " + empleado.get("email").asText());
            printInfo("Departamento: " + empleado.get("departamentoId").asText());
        } catch (Exception e) {
            fail("Error al parsear respuesta: " + e.getMessage());
        }
    }
    
    @Test
    @Order(3)
    @DisplayName("Test 3: Rechazar empleado con departamento inexistente")
    void test3_rechazarDepartamentoInvalido() {
        printHeader("TEST 3: RECHAZAR DEPARTAMENTO INEXISTENTE");
        
        // Preparar datos
        Map<String, String> empleado = new HashMap<>();
        empleado.put("id", "E002");
        empleado.put("nombre", "María López");
        empleado.put("email", "maria@empresa.com");
        empleado.put("departamentoId", "DEPT_NO_EXISTE");
        
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        HttpEntity<Map<String, String>> request = new HttpEntity<>(empleado, headers);
        
        // Ejecutar
        ResponseEntity<String> response = restTemplate.postForEntity(
            EMPLEADOS_URL + "/empleados",
            request,
            String.class
        );
        
        // Verificar
        assertEquals(HttpStatus.BAD_REQUEST, response.getStatusCode(),
            "Debe rechazar empleado con departamento inexistente (status 400)");
        
        printSuccess("Validación correcta: rechazado con status 400");
        printInfo("Mensaje: " + response.getBody());
    }
    
    @Test
    @Order(4)
    @DisplayName("Test 4: Listar todos los empleados")
    void test4_listarEmpleados() {
        printHeader("TEST 4: LISTAR EMPLEADOS");
        
        // Ejecutar
        ResponseEntity<String> response = restTemplate.getForEntity(
            EMPLEADOS_URL + "/empleados",
            String.class
        );
        
        // Verificar
        assertEquals(HttpStatus.OK, response.getStatusCode(),
            "Debe poder listar empleados");
        
        try {
            JsonNode empleados = objectMapper.readTree(response.getBody());
            assertTrue(empleados.isArray());
            printSuccess("Encontrados " + empleados.size() + " empleado(s)");
            
            empleados.forEach(emp -> {
                printInfo("  - " + emp.get("id").asText() + ": " + 
                         emp.get("nombre").asText() + " (" + 
                         emp.get("departamentoId").asText() + ")");
            });
        } catch (Exception e) {
            fail("Error al parsear respuesta: " + e.getMessage());
        }
    }
    
    // Métodos de utilidad para output formateado
    private static void printHeader(String text) {
        System.out.println();
        System.out.println(ANSI_BLUE + "=".repeat(70) + ANSI_RESET);
        System.out.println(ANSI_BLUE + text + ANSI_RESET);
        System.out.println(ANSI_BLUE + "=".repeat(70) + ANSI_RESET);
        System.out.println();
    }
    
    private static void printTest(String message) {
        System.out.println(ANSI_YELLOW + "[TEST] " + message + "..." + ANSI_RESET);
    }
    
    private static void printSuccess(String message) {
        System.out.println(ANSI_GREEN + "✓ " + message + ANSI_RESET);
    }
    
    private static void printError(String message) {
        System.out.println(ANSI_RED + "✗ " + message + ANSI_RESET);
    }
    
    private static void printInfo(String message) {
        System.out.println(ANSI_BLUE + "  ℹ " + message + ANSI_RESET);
    }
}
