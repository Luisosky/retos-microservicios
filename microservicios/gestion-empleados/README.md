# Microservicio Gestión de Empleados

### Pasos para Ejecutar

1. **Clonar/Descargar el proyecto**:
```bash
cd gestion-empleados
```

2. **Compilar el proyecto**:
```bash
mvn clean compile
```

3. **Ejecutar la aplicación**:
```bash
mvn spring-boot:run
```

4. **Acceder a la API**:
- URL base: http://localhost:8080
- Swagger UI: http://localhost:8080/swagger-ui.html
- API Docs: http://localhost:8080/v3/api-docs

## 📖 Documentación

Para información detallada sobre la configuración, consulta los siguientes archivos:

- 📄 **[MONGODB_ATLAS_CONFIG.md](MONGODB_ATLAS_CONFIG.md)** - Configuración de MongoDB Atlas
- 📄 **[SETUP_ENVIRONMENT_VARIABLES.md](SETUP_ENVIRONMENT_VARIABLES.md)** - Configurar variables de entorno
## Características
- Registro y consulta de empleados
## Endpoints

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

### Interfaz de administración del broker (RabbitMQ)

Con Docker Compose levantado, la consola de administración queda disponible en:

- URL: `http://localhost:15672`
- Usuario: `guest` (o el valor de `RABBITMQ_DEFAULT_USER`)
- Contraseña: `guest` (o el valor de `RABBITMQ_DEFAULT_PASS`)

Si deseas cambiar credenciales, define estas variables en el archivo `.env` del proyecto raíz:

- `RABBITMQ_DEFAULT_USER`
- `RABBITMQ_DEFAULT_PASS`

Luego reinicia:

```bash
docker compose up -d --build
```

## ¿Por qué se eligió RabbitMQ como broker?

Se eligió RabbitMQ para este proyecto porque ofrece un equilibrio sólido entre simplicidad operativa y capacidades de mensajería empresarial:

- Soporta colas, enrutamiento y patrones pub/sub de forma nativa (ideal para microservicios).
- Incluye confirmaciones de entrega y reintentos, útiles para desacoplar servicios con mayor confiabilidad.
- Tiene interfaz de administración web integrada para monitoreo rápido (colas, exchanges, consumers, throughput).
- Es maduro, ampliamente documentado y fácil de ejecutar en Docker para entornos académicos y de desarrollo.

### Comparación breve con alternativas

- Redis Pub/Sub: muy rápido y simple, pero menos robusto para persistencia, reintentos y garantías de entrega.
- Apache Kafka: excelente para alto volumen y streaming, pero introduce mayor complejidad operativa para este alcance.
- NATS: ligero y veloz, aunque con menor adopción en escenarios de colas tradicionales con enrutamiento tipo AMQP.

Para este sistema, RabbitMQ cubre mejor el caso de uso de eventos entre servicios sin sobrecargar la infraestructura.

## Publicación de eventos del Servicio de Empleados

El servicio publica eventos en RabbitMQ después de que la operación en base de datos es exitosa.

- Exchange: `empleados.events`
- Routing key al crear: `empleado.creado`
- Routing key al eliminar: `empleado.eliminado`

Si la publicación en el broker falla, la operación de base de datos no se revierte. El error se registra en logs para diagnóstico.

### Contrato JSON: empleado.creado

Se publica al ejecutar exitosamente `POST /empleado`:

```json
{
  "id": "EMP001",
  "nombre": "Juan",
  "email": "juan.perez@empresa.com",
  "departamentoId": "DEP001",
  "fechaIngreso": "2024-01-15"
}
```

### Contrato JSON: empleado.eliminado

Se publica al ejecutar exitosamente `DELETE /empleado/{id}`:
{
   "id": "EMP001",
   "nombre": "Juan",
   "email": "juan.perez@empresa.com"
}
```

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
