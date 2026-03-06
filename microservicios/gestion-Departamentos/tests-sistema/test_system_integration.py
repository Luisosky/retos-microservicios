"""
Pruebas de integración del sistema - Gestión de Departamentos
Tests end-to-end del servicio de gestión de departamentos
"""
import requests
import time
import sys
from typing import Optional


class Colors:
    """Colores para output en consola"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'


class SystemTests:
    """Clase para ejecutar las pruebas del sistema completo"""
    
    def __init__(self, departamentos_url: str = "http://localhost:8081", 
                 empleados_url: str = "http://localhost:8080"):
        self.departamentos_url = departamentos_url
        self.empleados_url = empleados_url
        self.test_results = []
        
    def print_header(self, text: str):
        """Imprime un encabezado formateado"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{text.center(70)}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")
    
    def print_test(self, test_name: str):
        """Imprime el nombre de la prueba"""
        print(f"{Colors.YELLOW}[TEST]{Colors.END} {test_name}...")
    
    def print_success(self, message: str):
        """Imprime mensaje de éxito"""
        print(f"{Colors.GREEN}✓ {message}{Colors.END}")
        self.test_results.append(("PASS", message))
    
    def print_error(self, message: str):
        """Imprime mensaje de error"""
        print(f"{Colors.RED}✗ {message}{Colors.END}")
        self.test_results.append(("FAIL", message))
    
    def print_info(self, message: str):
        """Imprime información adicional"""
        print(f"{Colors.BLUE}  ℹ {message}{Colors.END}")
    
    def wait_for_services(self, max_attempts: int = 30, delay: int = 2):
        """Espera a que los servicios estén disponibles"""
        self.print_header("VERIFICANDO DISPONIBILIDAD DE SERVICIOS")
        
        services = [
            ("Departamentos", f"{self.departamentos_url}/docs"),
            ("Empleados", f"{self.empleados_url}/docs")
        ]
        
        for service_name, url in services:
            self.print_test(f"Esperando servicio {service_name}")
            for attempt in range(1, max_attempts + 1):
                try:
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        self.print_success(f"Servicio {service_name} disponible")
                        break
                except requests.exceptions.RequestException:
                    if attempt < max_attempts:
                        self.print_info(f"Intento {attempt}/{max_attempts}, esperando {delay}s...")
                        time.sleep(delay)
                    else:
                        self.print_error(f"Servicio {service_name} no disponible después de {max_attempts} intentos")
                        return False
        return True
    
    def test_1_crear_departamento(self):
        """Prueba 1: Crear un departamento"""
        self.print_test("Crear departamento 'IT'")
        
        departamento_data = {
            "id": "IT",
            "nombre": "Tecnología",
            "descripcion": "Departamento de TI"
        }
        
        try:
            response = requests.post(
                f"{self.departamentos_url}/departamentos",
                json=departamento_data,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                self.print_success(f"Departamento creado exitosamente (Status: {response.status_code})")
                self.print_info(f"Respuesta: {response.json()}")
                return True
            else:
                self.print_error(f"Error al crear departamento (Status: {response.status_code})")
                self.print_info(f"Respuesta: {response.text}")
                return False
        except Exception as e:
            self.print_error(f"Excepción al crear departamento: {str(e)}")
            return False
    
    def test_2_obtener_departamento(self):
        """Prueba 2: Obtener un departamento específico"""
        self.print_test("Obtener departamento 'IT'")
        
        try:
            response = requests.get(
                f"{self.departamentos_url}/departamentos/IT",
                timeout=10
            )
            
            if response.status_code == 200:
                departamento = response.json()
                self.print_success(f"Departamento encontrado: {departamento.get('nombre', 'N/A')}")
                self.print_info(f"ID: {departamento.get('id', 'N/A')}")
                self.print_info(f"Descripción: {departamento.get('descripcion', 'N/A')}")
                return True
            else:
                self.print_error(f"Departamento no encontrado (Status: {response.status_code})")
                return False
        except Exception as e:
            self.print_error(f"Excepción al obtener departamento: {str(e)}")
            return False
    
    def test_3_actualizar_departamento(self):
        """Prueba 3: Actualizar un departamento"""
        self.print_test("Actualizar departamento 'IT'")
        
        departamento_actualizado = {
            "id": "IT",
            "nombre": "Tecnología Actualizada",
            "descripcion": "Departamento de TI - Actualizado"
        }
        
        try:
            response = requests.put(
                f"{self.departamentos_url}/departamentos/IT",
                json=departamento_actualizado,
                timeout=10
            )
            
            if response.status_code in [200, 204]:
                self.print_success(f"Departamento actualizado exitosamente (Status: {response.status_code})")
                if response.status_code == 200 and response.text:
                    self.print_info(f"Respuesta: {response.json()}")
                return True
            else:
                self.print_error(f"Error al actualizar departamento (Status: {response.status_code})")
                self.print_info(f"Respuesta: {response.text}")
                return False
        except Exception as e:
            self.print_error(f"Excepción al actualizar departamento: {str(e)}")
            return False
    
    def test_4_listar_departamentos(self):
        """Prueba 4: Listar todos los departamentos"""
        self.print_test("Listar todos los departamentos")
        
        try:
            response = requests.get(
                f"{self.departamentos_url}/departamentos",
                timeout=10
            )
            
            if response.status_code == 200:
                departamentos = response.json()
                self.print_success(f"Encontrados {len(departamentos)} departamento(s)")
                for dept in departamentos:
                    self.print_info(f"  - {dept.get('id')}: {dept.get('nombre')}")
                return True
            else:
                self.print_error(f"Error al listar departamentos (Status: {response.status_code})")
                return False
        except Exception as e:
            self.print_error(f"Excepción al listar departamentos: {str(e)}")
            return False
    
    def cleanup(self):
        """Limpieza: eliminar datos de prueba (opcional)"""
        self.print_header("LIMPIEZA DE DATOS DE PRUEBA")
        
        # Intentar eliminar el departamento de prueba
        try:
            self.print_test("Eliminar departamento IT")
            response = requests.delete(f"{self.departamentos_url}/departamentos/IT", timeout=10)
            if response.status_code in [200, 204, 404]:
                self.print_success("Departamento eliminado o no existente")
            else:
                self.print_info(f"Status: {response.status_code}")
        except Exception as e:
            self.print_info(f"No se pudo eliminar departamento: {str(e)}")
    
    def print_summary(self):
        """Imprime un resumen de los resultados"""
        self.print_header("RESUMEN DE PRUEBAS")
        
        passed = sum(1 for status, _ in self.test_results if status == "PASS")
        failed = sum(1 for status, _ in self.test_results if status == "FAIL")
        total = len(self.test_results)
        
        print(f"Total de pruebas: {total}")
        print(f"{Colors.GREEN}Exitosas: {passed}{Colors.END}")
        print(f"{Colors.RED}Fallidas: {failed}{Colors.END}")
        
        if failed > 0:
            print(f"\n{Colors.RED}Pruebas fallidas:{Colors.END}")
            for status, message in self.test_results:
                if status == "FAIL":
                    print(f"  {Colors.RED}✗{Colors.END} {message}")
        
        success_rate = (passed / total * 100) if total > 0 else 0
        print(f"\nTasa de éxito: {success_rate:.1f}%")
        
        return failed == 0
    
    def run_all_tests(self):
        """Ejecuta todas las pruebas del sistema"""
        self.print_header("PRUEBAS DEL SISTEMA - GESTIÓN DE DEPARTAMENTOS")
        
        # Verificar que los servicios estén disponibles
        if not self.wait_for_services():
            print(f"\n{Colors.RED}ERROR: Los servicios no están disponibles. Asegúrese de que docker-compose esté ejecutándose.{Colors.END}")
            sys.exit(1)
        
        # Limpieza previa (opcional)
        self.cleanup()
        
        # Ejecutar pruebas
        self.print_header("EJECUTANDO PRUEBAS DE INTEGRACIÓN - DEPARTAMENTOS")
        
        tests = [
            self.test_1_crear_departamento,
            self.test_2_obtener_departamento,
            self.test_3_actualizar_departamento,
            self.test_4_listar_departamentos,
        ]
        
        for test in tests:
            test()
            print()  # Línea en blanco entre pruebas
        
        # Resumen
        all_passed = self.print_summary()
        
        return all_passed


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Pruebas de integración del sistema de microservicios')
    parser.add_argument('--departamentos-url', default='http://localhost:8081',
                        help='URL del servicio de departamentos (default: http://localhost:8081)')
    parser.add_argument('--empleados-url', default='http://localhost:8080',
                        help='URL del servicio de empleados (default: http://localhost:8080)')
    parser.add_argument('--no-cleanup', action='store_true',
                        help='No ejecutar limpieza de datos al final')
    
    args = parser.parse_args()
    
    # Crear instancia de pruebas
    tests = SystemTests(
        departamentos_url=args.departamentos_url,
        empleados_url=args.empleados_url
    )
    
    # Ejecutar pruebas
    try:
        all_passed = tests.run_all_tests()
        
        # Limpieza final (opcional)
        if not args.no_cleanup:
            tests.cleanup()
        
        # Exit code
        sys.exit(0 if all_passed else 1)
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Pruebas interrumpidas por el usuario{Colors.END}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.RED}Error inesperado: {str(e)}{Colors.END}")
        sys.exit(1)


if __name__ == "__main__":
    main()
