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

## Ejecución

Este microservicio usa **MongoDB Atlas** (cloud) para la base de datos. Las credenciales están en el archivo `.env` del directorio `microservicios/`.

### Opción 1: Con Docker Compose (⭐ Recomendado)

```bash
cd microservicios
docker-compose up --build
```

Docker Compose automáticamente:
- Lee las credenciales del archivo `.env`
- Inicia Redis localmente
- Ejecuta el microservicio conectándose a MongoDB Atlas

La aplicación estará disponible en `http://localhost:8080`

### Opción 2: Ejecución Local (sin Docker)

Si necesitas ejecutar directamente en tu máquina para debugging:

```bash
cd microservicios/gestion-empleados

# Maven (si tienes Maven instalado)
mvn spring-boot:run

# O desde tu IDE (IntelliJ IDEA, Eclipse, VS Code)
# El IDE debe estar configurado para leer el archivo .env
```

**Nota**: Asegúrate de que las variables de entorno estén configuradas en tu IDE o sistema.

## Solución de Problemas

### Error: "Can't connect to MongoDB" o "MongoTimeoutException"

**Causa**: No se puede conectar a MongoDB Atlas.

**Solución**:

1. **Verifica tu IP en MongoDB Atlas**:
   - Ve a [MongoDB Atlas](https://cloud.mongodb.com) → Network Access
   - Agrega tu IP actual o usa `0.0.0.0/0` (⚠️ solo para desarrollo)
   - Espera 1-2 minutos para que se aplique el cambio

2. **Verifica las credenciales**:
   ```bash
   cd microservicios
   cat .env  # Linux/Mac/Git Bash
   type .env # Windows CMD
   ```
   La variable `MONGODB_URI` debe tener el formato correcto

3. **Verifica que el cluster está activo**:
   - MongoDB Atlas → Database → Clusters
   - El estado debe ser "Active" (no pausado)

4. **Prueba la conexión**:
   - Desde MongoDB Atlas, usa "Connect" → "Connect your application"
   - Verifica que la URI coincide con la del `.env`

### Error: "Connection refused to Redis"

**Causa**: Redis no está ejecutándose localmente.

**Solución**:
```bash
cd microservicios
docker-compose up redis -d
```

### Error: "Authentication failed"

**Causa**: Usuario o contraseña incorrectos en MongoDB Atlas.

**Solución**:
1. Ve a MongoDB Atlas → Database Access
2. Verifica el usuario y contraseña
3. Si es necesario, crea un nuevo usuario o resetea la contraseña
4. Actualiza las credenciales en el archivo `.env`

### Error: Las variables de entorno no se cargan

**Con Docker Compose**: Docker automáticamente lee el `.env`, no necesitas hacer nada.

**Sin Docker (ejecución local)**:
- **IntelliJ IDEA**: Instala el plugin "EnvFile" y configúralo
- **VS Code**: Usa el plugin "DotENV" 
- **Eclipse**: Configura las variables en Run Configurations
- **PowerShell**: `$env:MONGODB_URI="tu-uri-aqui"`

## Stack Tecnológico
- Java 17
- Spring Boot 3.2.2
- MongoDB
- Redis Streams
- Lombok
