# Integración Perfiles <-> Empleados via RabbitMQ

## Descripción

Se ha implementado una integración automática entre los servicios de Empleados y Perfiles usando RabbitMQ como broker de mensajes.

### Flujos Implementados

#### 1. Crear Empleado → Crear Perfil Automáticamente
- Cuando se crea un empleado en `gestion-empleados`
- Se publica evento `empleado.creado` en RabbitMQ
- El servicio `gestion-perfiles` escucha este evento
- Se crea automáticamente un perfil con:
  - `empleado_id`: ID del empleado
  - `nombre`: Nombre del empleado
  - `email`: Email del empleado
  - `biografia`: Vacío (puede ser completado después)

#### 2. Eliminar Empleado → Marcar Perfil como Despedido
- Cuando se elimina un empleado en `gestion-empleados`
- Se publica evento `empleado.eliminado` en RabbitMQ
- El servicio `gestion-perfiles` escucha este evento
- Se marca el perfil como:
  - `biografia`: "Despedido"

## Componentes Implementados

### Events (Eventos)
- `App\Events\EmpleadoCreadoEvent`: Representa un empleado creado
- `App\Events\EmpleadoEliminadoEvent`: Representa un empleado eliminado

### Listeners (Escuchadores)
- `App\Listeners\HandleEmpleadoCreado`: Procesa evento de empleado creado
- `App\Listeners\HandleEmpleadoEliminado`: Procesa evento de empleado eliminado

### Command (Comando CLI)
- `app:rabbitmq:listen-empleados`: Escucha eventos de RabbitMQ en tiempo real

## Estructura de Eventos

### evento: empleado.creado
```json
{
  "id": "numeroEmpleado",
  "nombre": "Juan Pérez",
  "email": "juan@example.com",
  "departamentoId": "dept-123",
  "fechaIngreso": "2026-04-02"
}
```

### evento: empleado.eliminado
```json
{
  "id": "numeroEmpleado",
  "nombre": "Juan Pérez",
  "email": "juan@example.com"
}
```

## Configuración en docker-compose.yml

El servicio `perfiles` ya está configurado con:
- Variable `RABBITMQ_HOST`: rabbitmq-broker
- Variable `RABBITMQ_PORT`: 5672
- Variable `RABBITMQ_EXCHANGE`: empleados.events
- Variable `RABBITMQ_QUEUE`: perfiles.queue

## Cómo Probar la Integración

### Opción 1: Usando Docker Compose

```bash
# 1. Construir y levantar los servicios
docker-compose up -d

# 2. Esperar 30-40 segundos a que los servicios se inicien
# 3. Crear un empleado (desde la API de empleados)
curl -X POST http://localhost:8080/empleados \
  -H "Content-Type: application/json" \
  -d '{
    "numeroEmpleado": "EMP001",
    "nombre": "Juan Pérez",
    "apellido": "Rodríguez",
    "email": "juan@example.com",
    "departamentoId": "DEPT001"
  }'

# 4. Verificar que el perfil se creó automáticamente
curl http://localhost:8083/api/perfiles

# 5. Eliminar el empleado
curl -X DELETE http://localhost:8080/empleados/EMP001

# 6. Verificar que el perfil fue marcado como despedido
curl http://localhost:8083/api/perfiles
```

### Opción 2: Ejecutar el Listener manualmente (desarrollo local)

```bash
# Dentro del contenedor o en desarrollo local
cd gestion-perfiles

# Ver logs del listener
php artisan rabbitmq:listen-empleados

# Con timeout de 60 segundos (útil para testing)
php artisan rabbitmq:listen-empleados --timeout=60
```

## Ver Logs

### Docker Logs
```bash
# Ver logs del contenedor de perfiles
docker logs -f perfiles-service

# Ver logs del consumer de eventos
docker logs -f perfiles-service | grep -i "empleado\|perfil\|rabbitmq"
```

### Laravel Logs
Los logs están en: `gestion-perfiles/storage/logs/laravel.log`

```bash
# Ver logs en tiempo real
tail -f gestion-perfiles/storage/logs/laravel.log
```

## Solución de Problemas

### El listener no inicia
1. Verificar que RabbitMQ está corriendo: `docker logs rabbitmq-broker`
2. Verificar conexión a RabbitMQ desde el contenedor:
   ```bash
   docker exec perfiles-service php artisan tinker
   # Dentro de tinker:
   config('rabbitmq')
   ```

### Los eventos no se procesan
1. Verificar que `rabbitmq:listen-empleados` está ejecutándose:
   ```bash
   docker exec perfiles-service ps aux | grep rabbitmq
   ```
2. Verificar logs en `storage/logs/laravel.log`
3. Verificar que el empleado y perfil tienen el mismo `empleado_id`

### Perfil no se crea cuando se crea empleado
1. Esperar unos segundos (hay latencia de red)
2. Verificar que el listener está activo
3. Verificar logs de perfiles con: `docker logs -f perfiles-service`

## Cambios en el Código

### Archivos Creados
- `app/Events/EmpleadoCreadoEvent.php`
- `app/Events/EmpleadoEliminadoEvent.php`
- `app/Listeners/HandleEmpleadoCreado.php`
- `app/Listeners/HandleEmpleadoEliminado.php`
- `app/Console/Commands/RabbitMQListenEmpleadosEvents.php`
- `app/Providers/EventServiceProvider.php`

### Archivos Modificados
- `config/app.php`: Agregado `EventServiceProvider` a providers
- `docker-entrypoint.sh`: Agregado comando para iniciar el listener en background

### Dependencias Instaladas
- `php-amqplib/php-amqplib`: Librería para conectar a RabbitMQ

## Próximos Pasos Opcionales

1. **Agregar campo `estado` a perfiles**: Para mejor control de estado (activo/despedido)
2. **Sincronización bidireccional**: Si se actualiza el perfil, actualizar datos en empleado
3. **Reintentos**: Implementar reintentos exponenciales si falla la creación de perfil
4. **Auditoría**: Registrar quién creó/eliminó cada evento

## Monitoreo en Producción

Para monitorear la integración en producción:

1. Usar la UI de RabbitMQ:
   ```
   http://localhost:15672
   Usuario: guest
   Contraseña: guest
   ```

2. Verificar actividad en la cola `perfiles.queue`

3. Monitorear logs con sistema centralizado (ELK, Splunk, etc.)

## Referencias

- [RabbitMQ Documentation](https://www.rabbitmq.com/documentation.html)
- [Laravel Events](https://laravel.com/docs/services#events)
- [php-amqplib](https://github.com/php-amqplib/php-amqplib)
