# Gestion de Perfiles - Microservicio Laravel (PHP)

Microservicio REST API construido con **Laravel 10 + PHP 8.2** para gestionar perfiles de empleados.

## Responsabilidades

- CRUD completo de perfiles de empleados
- Consumo de eventos RabbitMQ desde `gestion-empleados`:
  - `empleado.creado` → crea automáticamente un perfil
  - `empleado.eliminado` → desactiva y elimina (soft delete) el perfil
- Base de datos propia: **MySQL 8**

## Endpoints

| Método | Ruta                                  | Descripción                         |
|--------|---------------------------------------|-------------------------------------|
| GET    | `/api/health`                         | Health check del servicio           |
| GET    | `/api/perfiles`                       | Listar perfiles (paginado)          |
| POST   | `/api/perfiles`                       | Crear un nuevo perfil               |
| GET    | `/api/perfiles/{empleadoId}`          | Obtener perfil por ID de empleado   |
| PUT    | `/api/perfiles/{empleadoId}`          | Actualizar perfil por empleadoId    |
| PATCH  | `/api/perfiles/{empleadoId}`          | Actualización parcial por empleadoId|
| DELETE | `/api/perfiles/{empleadoId}`          | Eliminar perfil por empleadoId      |
| GET    | `/api/perfiles/id/{id}`               | Obtener perfil por ID interno (UUID)|
| DELETE | `/api/perfiles/id/{id}`               | Eliminar perfil por ID interno      |

## Contrato del perfil

Los perfiles se exponen con este formato:

```json
{
  "id": "string",
  "empleadoId": "string",
  "nombre": "string",
  "email": "string",
  "telefono": "string",
  "direccion": "string",
  "ciudad": "string",
  "biografia": "string",
  "fechaCreacion": "datetime"
}
```

`nombre` y `email` se obtienen del servicio `gestion-empleados`. En `POST /api/perfiles` se valida primero que el empleado exista llamando al endpoint `GET /empleado/{id}` de ese servicio.

## Puerto

Expone en el puerto **8083**.

## Variables de entorno

Ver [.env.example](.env.example) para la lista completa.

## Ejecución con Docker Compose

```bash
# Desde la raíz del proyecto
docker-compose up --build perfiles
```

Si la base de datos está en la nube, define `PERFILES_DB_HOST` (y opcionalmente `PERFILES_DB_PORT`) en tu `.env` de la raíz.

## Tests

Los tests usan SQLite en memoria, por lo que no requieren MySQL:

```bash
# Dentro del contenedor
docker exec perfiles-service php artisan test

# O localmente (requiere PHP + Composer instalados)
composer install
php artisan test
```

## Estructura

```
app/
├── Console/Commands/ConsumeEmpleadoEvents.php  # Consumer RabbitMQ
├── Http/
│   ├── Controllers/PerfilController.php        # Controlador REST
│   └── Requests/                               # Validaciones de entrada
├── Models/Perfil.php                           # Modelo Eloquent
├── Services/PerfilService.php                  # Lógica de negocio
database/
├── migrations/                                 # Esquema de BD
├── factories/PerfilFactory.php                 # Fábrica para tests
routes/api.php                                  # Definición de rutas
```
