# Retos Microservicios

Proyecto de microservicios usando arquitectura cloud-native con bases de datos en la nube.

## 🏗️ Arquitectura

- **Microservicio Empleados** (Java/Spring Boot) → MongoDB Atlas (Cloud)
- **Microservicio Departamentos** (Python/FastAPI) → Supabase PostgreSQL (Cloud)
- **Redis** (Local/Docker) → Mensajería entre servicios

## 🚀 Inicio Rápido

### 1. Configurar Credenciales

El archivo `.env` ya está configurado con las credenciales de MongoDB Atlas. Solo asegúrate de que tu IP esté autorizada:

1. Ve a [MongoDB Atlas](https://cloud.mongodb.com)
2. Network Access → Add IP Address
3. Agrega tu IP actual o usa `0.0.0.0/0` para desarrollo

### 2. Ejecutar con Docker Compose

```bash
cd microservicios
docker-compose up --build
```

**Servicios disponibles:**
- Empleados API: http://localhost:8080
- Departamentos API: http://localhost:8081

## 📁 Estructura del Proyecto

```
microservicios/
├── .env                    # ⚡ Credenciales (MongoDB Atlas, Supabase)
├── .env.example           # 📝 Plantilla de configuración
├── CONFIG.md              # 📖 Documentación de configuración
├── docker-compose.yml     # 🐳 Orquestación de servicios
├── gestion-empleados/     # ☕ Microservicio Java
└── gestion-departamentos/ # 🐍 Microservicio Python
```

## ⚙️ ¿Por qué existe el archivo `.env`?

Cuando usas **Docker Compose**, necesita las credenciales para que los contenedores se conecten a las bases de datos en la nube (MongoDB Atlas y Supabase). El archivo `.env`:

- ✅ Centraliza las credenciales
- ✅ Es leído automáticamente por Docker Compose
- ✅ Está en `.gitignore` (no se sube a Git)
- ✅ Facilita cambiar entre ambientes

**No necesitas cargar variables manualmente** - Docker Compose lo hace por ti.

## 📚 Documentación

- [CONFIG.md](microservicios/CONFIG.md) - Configuración detallada
- [Empleados README](microservicios/gestion-empleados/README.md) - API de empleados
- [Departamentos README](microservicios/gestion-departamentos/README.md) - API de departamentos

## 🔧 Desarrollo Local (sin Docker)

Si prefieres ejecutar directamente desde tu IDE:

```bash
# Opción 1: Configurar variables en tu IDE (IntelliJ, VS Code)
# Instala plugins para .env y ejecuta desde el IDE

# Opción 2: PowerShell (manual)
$env:MONGODB_URI="mongodb+srv://usuario:pass@cluster.mongodb.net/empleados-db"
cd microservicios/gestion-empleados
mvn spring-boot:run
```

## 🛠️ Tecnologías

- **Backend**: Java 17, Spring Boot 3.2.2, Python, FastAPI
- **Bases de Datos**: MongoDB Atlas, PostgreSQL (Supabase)
- **Mensajería**: Redis Streams
- **Containerización**: Docker, Docker Compose

## 📝 Notas

- Las bases de datos están en la **nube** (no en Docker local)
- Solo Redis se ejecuta localmente con Docker
- El archivo `load-env.ps1` es opcional (solo para ejecución sin Docker)

