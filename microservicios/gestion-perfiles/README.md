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
| GET    | `/api/perfiles/{id}`                  | Obtener perfil por ID               |
| GET    | `/api/perfiles/empleado/{empleadoId}` | Obtener perfil por ID de empleado   |
| PUT    | `/api/perfiles/{id}`                  | Actualizar perfil                   |
| DELETE | `/api/perfiles/{id}`                  | Eliminar perfil (soft delete)       |

## Puerto

Expone en el puerto **8083**.

## Variables de entorno

Ver [.env.example](.env.example) para la lista completa.

## Ejecución con Docker Compose

```bash
# Desde la raíz del proyecto
docker-compose up --build perfiles mysql-perfiles
```

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
