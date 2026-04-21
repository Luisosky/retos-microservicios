# language: es
Característica: Flujo de Onboarding de Empleados
  Como administrador del sistema
  Quiero registrar nuevos empleados
  Para que el sistema cree automáticamente sus credenciales vía eventos asíncronos

  Antecedentes:
    Dado que el sistema está desplegado y operativo
    Y que estoy autenticado con el rol "ADMIN"

  Escenario: Registro exitoso, generación de credenciales por evento y login
    Cuando registro un nuevo empleado con datos válidos
    Entonces la respuesta debe tener código 201
    Y espero a que sus credenciales sean generadas automáticamente mediante polling
    Entonces el nuevo empleado debería poder iniciar sesión en el sistema exitosamente

  Escenario: Prevención de registro con datos inválidos o incompletos
    Cuando intento registrar un empleado sin el campo de correo electrónico
    Entonces la respuesta debe tener código 400