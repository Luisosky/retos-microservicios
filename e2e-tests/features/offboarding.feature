# language: es
Característica: Flujo de Offboarding de Empleados
  Como administrador del sistema
  Quiero desvincular empleados y revocar sus accesos
  Para mantener la seguridad y el control de la empresa

  Antecedentes:
    Dado que el sistema está desplegado y operativo
    Y que estoy autenticado con el rol "ADMIN"

  Escenario: Desvinculación exitosa y bloqueo de credenciales
    Dado que preparo un empleado temporal para su posterior desvinculación
    Cuando ejecuto la desvinculación de este empleado en el sistema
    Entonces la respuesta debe tener código 200
    Y el sistema debe rechazar sus intentos de inicio de sesión

  Escenario: Prevención de recuperación de contraseña para usuarios eliminados
    Cuando el empleado desvinculado intenta solicitar una recuperación de contraseña
    Entonces la API de autenticación debe bloquear la solicitud