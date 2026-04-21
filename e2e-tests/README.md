# Automatización de Pruebas Funcionales (Reto 5)

Este repositorio contiene la suite de pruebas automatizadas E2E utilizando la metodología BDD (Behavior-Driven Development) para validar los flujos de seguridad, onboarding y offboarding del sistema de gestión de empleados.

## 🛠 Justificación del Framework (Go + Godog)
Para este reto, se ha seleccionado el lenguaje **Go** junto con el framework oficial **Godog** por las siguientes razones técnicas:
1. **Concurrencia nativa (Goroutines):** Go maneja operaciones asíncronas de manera excepcional. Esto permitió implementar un mecanismo de *Polling* eficiente para el escenario de onboarding (espera de credenciales vía RabbitMQ), evitando el uso de pausas fijas y bloqueantes (`sleeps`).
2. **Rendimiento y compilación estática:** El test suite se compila directamente a código máquina en un solo binario, lo que hace que la ejecución de los escenarios sea notablemente más rápida frente a alternativas interpretadas.
3. **Manejo de estado seguro:** Se utilizó una estructura de datos (`struct apiTestState`) para compartir variables de entorno (como el Token JWT y los clientes HTTP) a lo largo de los *steps*, manteniendo un código limpio y thread-safe.

## Instrucciones de Ejecución

Para ejecutar esta suite de pruebas, asegúrese de tener la infraestructura levantada.

1. **Levantar el entorno base:**
   Navegue a la raíz del proyecto principal y levante los microservicios:
   ```bash
   docker compose up -d


(Asegúrese de que los puertos 8080 y 8084 estén libres y los servicios de Empleados y Autenticación reporten un estado saludable).

Paso 2: Ejecutar la Suite de Pruebas BDD
Navegue hacia la carpeta de automatización e2e-tests y ejecute el comando de pruebas recursivo de Go:

cd e2e-tests
go test ./step_definitions -v


 Descripción de los Escenarios (Features)
Los escenarios han sido diseñados siguiendo las mejores prácticas de Gherkin, separando las pruebas en archivos .feature enfocados en áreas específicas del negocio:

humo.feature: Validaciones primarias del entorno de ejecución. Comprueba que el framework Godog esté correctamente enlazado con los pasos programados en Go.

seguridad.feature: Valida las reglas del Control de Acceso Basado en Roles (RBAC). Comprueba el rechazo por 401 Unauthorized ante la ausencia o alteración del token, y certifica que el rol USER reciba un 403 Forbidden al intentar realizar peticiones de escritura, reservadas únicamente para el rol ADMIN.

onboarding.feature: Evalúa la interacción entre el microservicio de Empleados (Java) y el microservicio de Autenticación. Verifica que, tras la creación exitosa (201 Created) de un empleado, el evento emitido por RabbitMQ sea procesado y se generen las credenciales para un inicio de sesión exitoso.

offboarding.feature: Valida el proceso de desvinculación de un empleado del sistema. Se comprueba la eliminación exitosa del recurso, el bloqueo inmediato para iniciar sesión en la API de Auth, y el rechazo en los intentos de utilizar endpoints de recuperación de contraseña, garantizando la seguridad post-empleo.