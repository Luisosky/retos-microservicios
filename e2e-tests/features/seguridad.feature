# language: es
Característica: Seguridad y control de acceso
  Como sistema de autenticación
  Quiero controlar el acceso a los recursos
  Para garantizar que solo los usuarios autorizados realicen operaciones

  Antecedentes:
    Dado que el sistema está desplegado y operativo
    Y que el servicio de empleados está disponible

  Escenario: Acceso denegado sin token de autenticación
    Cuando consulto la lista de empleados sin token de autenticación
    Entonces la respuesta debe tener código 401

  Escenario: Acceso denegado con token inválido o malformado
    Cuando consulto la lista de empleados enviando el token "token_falso_123"
    Entonces la respuesta debe tener código 401

  Escenario: Usuario estándar (USER) puede consultar pero no modificar recursos
    Dado que estoy autenticado con el rol "USER"
    Cuando consulto la lista de empleados
    Entonces la respuesta debe tener código 200
    Pero cuando intento crear un nuevo empleado en el sistema
    Entonces la respuesta debe tener código 403

  Escenario: Administrador (ADMIN) tiene permisos totales en el sistema
    Dado que estoy autenticado con el rol "ADMIN"
    Cuando consulto la lista de empleados
    Entonces la respuesta debe tener código 200
    Y cuando intento crear un nuevo empleado en el sistema
    Entonces la respuesta debe tener código 201