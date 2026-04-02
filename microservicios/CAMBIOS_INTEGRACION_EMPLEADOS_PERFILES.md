# Resumen de Cambios: Integración Empleados <-> Perfiles

## 📋 Descripción General

Se ha implementado una integración automática entre los servicios de **Empleados** (Java/Spring) y **Perfiles** (Laravel/PHP) usando **RabbitMQ** como broker de mensajes centralizador.

**Fecha**: 2 de Abril, 2026
**Estado**: ✅ Completado y Listo para Testing

---

## 🔄 Flujos Implementados

### Flujo 1: Crear Empleado → Crear Perfil
```
gestion-empleados (crear empleado)
      ↓
    RabbitMQ (emit: empleado.creado)
      ↓
gestion-perfiles (listener: HandleEmpleadoCreado)
      ↓
    Crear perfil automáticamente
```

**Proceso**:
1. Usuario crea empleado en `POST /empleados`
2. Sistema Java publicaa evento en RabbitMQ exchange `empleados.events` con routing key `empleado.creado`
3. Listener Laravel recibe evento
4. Se crea perfil en base de datos con: `empleado_id`, `nombre`, `email`

### Flujo 2: Eliminar Empleado → Marcar Perfil como Despedido
```
gestion-empleados (eliminar empleado)
      ↓
    RabbitMQ (emit: empleado.eliminado)
      ↓
gestion-perfiles (listener: HandleEmpleadoEliminado)
      ↓
    Marcar perfil como Despedido
```

**Proceso**:
1. Usuario elimina empleado en `DELETE /empleados/{id}`
2. Sistema Java publica evento en RabbitMQ exchange `empleados.events` con routing key `empleado.eliminado`
3. Listener Laravel recibe evento
4. Se actualiza el perfil: `biografia` = "Despedido"

---

## 📁 Archivos Creados

### Events (Eventos)
| Archivo | Descripción |
|---------|-----------|
| `app/Events/EmpleadoCreadoEvent.php` | Evento que representa la creación de un empleado. Contiene: `id`, `nombre`, `email`, `departamentoId`, `fechaIngreso` |
| `app/Events/EmpleadoEliminadoEvent.php` | Evento que representa la eliminación de un empleado. Contiene: `id`, `nombre`, `email` |

### Listeners (Escuchadores)
| Archivo | Descripción |
|---------|-----------|
| `app/Listeners/HandleEmpleadoCreado.php` | Escucha evento `EmpleadoCreadoEvent` y crea automáticamente un perfil |
| `app/Listeners/HandleEmpleadoEliminado.php` | Escucha evento `EmpleadoEliminadoEvent` y marca el perfil como "Despedido" |

### Command (Comando CLI)
| Archivo | Descripción |
|---------|-----------|
| `app/Console/Commands/RabbitMQListenEmpleadosEvents.php` | Comando que mantiene un listener activo conectado a RabbitMQ. Se ejecuta en background en Docker |

### Providers
| Archivo | Descripción |
|---------|-----------|
| `app/Providers/EventServiceProvider.php` | Registra los eventos y listeners en el sistema |

---

## 🔧 Archivos Modificados

### Configuración
| Archivo | Cambio |
|---------|--------|
| `config/app.php` | Agregado `App\Providers\EventServiceProvider::class` a la lista de providers |
| `docker-entrypoint.sh` | Agregado comando `php artisan rabbitmq:listen-empleados &` para iniciar el listener en background |

### Dependencias
```bash
composer require php-amqplib/php-amqplib
```
- Instalada librería para conectar a RabbitMQ desde PHP

---

## 🚀 Arquitetura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                      DOCKER COMPOSE                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────┐                  ┌────────────────┐  │
│  │ RabbitMQ-Broker  │                  │  Redis Cache   │  │
│  │  (5672, 15672)   │◄────────────────►│  (6379)        │  │
│  └──────────────────┘   network:       └────────────────┘  │
│         ▲               microservices-net     ▲             │
│         │                                     │             │
│         │ exchange: empleados.events          │             │
│         │ routing_keys:                       │             │
│         │ - empleado.creado                   │             │
│         │ - empleado.eliminado                │             │
│         │                                     │             │
│    ┌────┴─────────────────────────────────────┴────┐        │
│    │                                               │        │
│  ┌─▼──────────────────────────┐  ┌──────────────┐ │        │
│  │ gestion-empleados (Java)   │  │ gestion-     │ │        │
│  │ (:8080)                    │  │ perfiles     │ │        │
│  │                            │  │ (Laravel)   │ │        │
│  │ • Crea/Elimina empleados  │  │ (:8083)     │ │        │
│  │ • Publica eventos RabbitMQ │  │             │ │        │
│  │ • MongoDB                  │  │ • Escucha   │ │        │
│  │ • Spring Boot              │  │   eventos   │ │        │
│  │                            │  │ • Crea/     │ │        │
│  │ EmpleadoService            │  │   actualiza │ │        │
│  │ ├─ crearEmpleado()        │  │   perfiles  │ │        │
│  │ │  ├─ save() db           │  │ • PostgreSQL│ │        │
│  │ │  └─ publish()           │  │ • Laravel   │ │        │
│  │ │     rabbitTemplate      │  │             │ │        │
│  │ └─ eliminarEmpleado()     │  │ EventServ.  │ │        │
│  │    ├─ delete() db         │  │ ├─ dispatch │ │        │
│  │    └─ publish()           │  │ │  event    │ │        │
│  │       rabbitTemplate      │  │ └─ listeners│ │        │
│  └────────────────────────────┘  └──────────────┘ │        │
│    │                               ▲              │        │
│    └───────────────┬────────────────┘              │        │
│                    │                               │        │
│                 (HTTP)                             │        │
│                                                   │        │
└─────────────────────────────────────────────────────────────┘
```

---

## ⚙️ Configuración RabbitMQ en docker-compose.yml

```yaml
# Servicios de Perfiles - Variables de Entorno
environment:
  RABBITMQ_HOST: rabbitmq-broker
  RABBITMQ_PORT: 5672
  RABBITMQ_USER: guest
  RABBITMQ_PASS: guest
  RABBITMQ_EXCHANGE: empleados.events
  RABBITMQ_QUEUE: perfiles.queue
```

**Variables en `config/rabbitmq.php`**:
```php
return [
    'host'     => env('RABBITMQ_HOST', 'rabbitmq-broker'),
    'port'     => (int) env('RABBITMQ_PORT', 5672),
    'user'     => env('RABBITMQ_USER', 'guest'),
    'pass'     => env('RABBITMQ_PASS', 'guest'),
    'exchange' => env('RABBITMQ_EXCHANGE', 'empleados.events'),
    'queue'    => env('RABBITMQ_QUEUE', 'perfiles.queue'),
];
```

---

## 🧪 Testing

### Archivo de Testing Creado
- **`test_integracion_empleados_perfiles.ps1`**
  - Script PowerShell que prueba el flujo completo
  - Crea empleado → Verifica perfil creado
  - Elimina empleado → Verifica perfil como Despedido

### Instrucciones de Testing
```powershell
# Ejecutar el script de testing
./test_integracion_empleados_perfiles.ps1

# O con URLs personalizadas
./test_integracion_empleados_perfiles.ps1 `
  -EmpleadosUrl "http://localhost:8080" `
  -PerfilesUrl "http://localhost:8083"
```

---

## 📊 Estructura de Mensajes RabbitMQ

### Evento: `empleado.creado`
```json
{
  "id": "EMP001",
  "nombre": "Juan Pérez",
  "email": "juan@example.com",
  "departamentoId": "DEPT123",
  "fechaIngreso": "2026-04-02T10:30:00Z"
}
```

### Evento: `empleado.eliminado`
```json
{
  "id": "EMP001",
  "nombre": "Juan Pérez",
  "email": "juan@example.com"
}
```

---

## 🔍 Validación de Sintaxis

Todos los archivos PHP creados han sido validados sin errores:
```
✅ app/Events/EmpleadoCreadoEvent.php
✅ app/Events/EmpleadoEliminadoEvent.php
✅ app/Listeners/HandleEmpleadoCreado.php
✅ app/Listeners/HandleEmpleadoEliminado.php
✅ app/Console/Commands/RabbitMQListenEmpleadosEvents.php
✅ app/Providers/EventServiceProvider.php
```

---

## 📝 Documentación Disponible

- **INTEGRACION_EMPLEADOS_PERFILES.md**: Documentación completa con instrucciones de uso y troubleshooting
- **Este archivo (CAMBIOS_INTEGRACION.md)**: Resumen de cambios técnicos

---

## 🎯 Próximos Pasos (Opcionales)

1. **Agregar campo `estado` a perfiles**
   - Para mejor tracking: `activo`, `despedido`, `suspendido`
   
2. **Implementar reintentos**
   - Usar exponential backoff si falla la creación de perfil
   
3. **Sincronización bidireccional**
   - Si se actualiza el perfil, actualizar datos en empleado
   
4. **Auditoría eompleta**
   - Registrar todas los cambios causados por eventos
   
5. **Monitoring en producción**
   - Integración con ELK Stack, Datadog, o similar

---

## 🐛 Troubleshooting Rápido

| Problema | Solución |
|----------|----------|
| Perfil no se crea al crear empleado | Ver logs: `docker logs -f perfiles-service` |
| Listener no inicia | Verificar RabbitMQ: `docker logs rabbitmq-broker` |
| Error en syntaxis PHP | Usar: `php -l app/path/to/file.php` |
| RabbitMQ no accesible | Verificar conectividad: `docker ps \| grep rabbitmq` |

---

## ✅ Checklist de Implementación

- [x] Crear eventos en Laravel
- [x] Crear listeners en Laravel
- [x] Crear command para escuchar RabbitMQ
- [x] Registrar EventServiceProvider
- [x] Instalar dependencia php-amqplib
- [x] Actualizar docker-entrypoint.sh
- [x] Validar sintaxis de todos los archivos
- [x] Crear documentación completa
- [x] Crear script de testing
- [ ] Ejecutar tests end-to-end (Next Step)

---

**Material de Referencia**:
- [RabbitMQ Official Docs](https://www.rabbitmq.com/documentation.html)
- [Laravel Events](https://laravel.com/docs/services#events)
- [php-amqplib/php-amqplib](https://github.com/php-amqplib/php-amqplib)
- [Spring RabbitMQ](https://spring.io/projects/spring-amqp)
