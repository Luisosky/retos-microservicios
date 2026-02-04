# Microservicio Gestión de Empleados

## Características
- Registro y consulta de empleados
- Integración con MongoDB para persistencia
- Publicación de eventos a Redis Streams
- Contenerización con Docker

## Endpoints

### Registrar Empleado
**POST** http://localhost:8080/empleado

```json
{
  "numeroEmpleado": "EMP001",
  "nombre": "Juan",
  "apellido": "Pérez",
  "email": "juan.perez@empresa.com",
  "cargo": "Desarrollador",
  "area": "TI",
  "fechaIngreso": "2024-01-15",
  "estado": "ACTIVO"
}
```

**Respuesta (200 OK):** Empleado registrado

### Consultar Empleado por ID
**GET** http://localhost:8080/empleado/{id}

**Respuesta (200 OK):** Información del empleado

**Respuesta (404 Not Found):** El empleado con id {id} no existe

## Requisitos Previos
- Java 17
- Maven 3.9+
- MongoDB (puerto 27017)
- Redis (puerto 6379)
- Docker

## Ejecución Local

### Sin Docker
```bash
cd microservicios/gestion-empleados
mvn spring-boot:run
```

### Con Docker
```bash
cd microservicios/gestion-empleados
docker build -t servidor-empleados .
docker run -p 8080:8080 servidor-empleados
```

## Stack Tecnológico
- Java 17
- Spring Boot 3.2.2
- MongoDB
- Redis Streams
- Lombok
