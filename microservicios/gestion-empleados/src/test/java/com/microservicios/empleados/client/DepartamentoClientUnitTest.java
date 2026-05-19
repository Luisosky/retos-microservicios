package com.microservicios.empleados.client;

import com.microservicios.empleados.dto.DepartamentoDto;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.test.util.ReflectionTestUtils;
import org.springframework.web.client.RestTemplate;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class DepartamentoClientUnitTest {

    @Mock
    private RestTemplate restTemplate;

    @InjectMocks
    private DepartamentoClient departamentoClient;

    @BeforeEach
    void setUp() {
        ReflectionTestUtils.setField(departamentoClient, "departamentosServiceUrl", "http://departamentos:8081");
    }

    @Test
    void existeDepartamentoRetornaFalseConIdVacio() {
        assertFalse(departamentoClient.existeDepartamento(" "));
    }

    @Test
    void existeDepartamentoRetornaTrueCuandoServicioRespondeActivo() {
        DepartamentoDto departamento = new DepartamentoDto();
        departamento.setId("DEP001");
        departamento.setNombre("RRHH");
        departamento.setActivo(true);
        when(restTemplate.getForEntity("http://departamentos:8081/departamentos/DEP001", DepartamentoDto.class))
                .thenReturn(new ResponseEntity<>(departamento, HttpStatus.OK));

        assertTrue(departamentoClient.existeDepartamento("DEP001"));
    }

    @Test
    void obtenerDepartamentoRetornaNullConIdVacio() {
        assertFalse(departamentoClient.existeDepartamento(null));
    }
}