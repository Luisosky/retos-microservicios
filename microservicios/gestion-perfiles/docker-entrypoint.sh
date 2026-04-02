#!/bin/sh
set -e

# Ensure Laravel .env exists
if [ ! -f /var/www/.env ]; then
  if [ -f /var/www/.env.example ]; then
    echo "[PERFILES] Creando .env desde .env.example..."
    cp /var/www/.env.example /var/www/.env
  else
    echo "[PERFILES] Creando .env vacío (no se encontró .env.example)..."
    touch /var/www/.env
  fi
fi

set_env_var() {
  key="$1"
  value="$2"
  if grep -q "^${key}=" /var/www/.env; then
    sed -i "s|^${key}=.*|${key}=${value}|" /var/www/.env
  else
    echo "${key}=${value}" >> /var/www/.env
  fi
}

if [ -n "$APP_ENV" ]; then
  set_env_var "APP_ENV" "$APP_ENV"
fi

if [ -n "$APP_DEBUG" ]; then
  set_env_var "APP_DEBUG" "$APP_DEBUG"
fi

if [ -n "$APP_URL" ]; then
  set_env_var "APP_URL" "$APP_URL"
fi

set_env_var "LOG_CHANNEL" "${LOG_CHANNEL:-stack}"
set_env_var "LOG_LEVEL" "${LOG_LEVEL:-debug}"
set_env_var "CACHE_DRIVER" "${CACHE_DRIVER:-redis}"
set_env_var "SESSION_DRIVER" "${SESSION_DRIVER:-redis}"
set_env_var "QUEUE_CONNECTION" "${QUEUE_CONNECTION:-sync}"

set_env_var "REDIS_HOST" "${REDIS_HOST:-redis}"
set_env_var "REDIS_PORT" "${REDIS_PORT:-6379}"
set_env_var "REDIS_PASSWORD" "${REDIS_PASSWORD:-}"

set_env_var "APP_KEY" "${APP_KEY}"

set_env_var "DB_CONNECTION" "pgsql"
if [ -n "$DATABASE_URL" ]; then
  set_env_var "DATABASE_URL" "$DATABASE_URL"
fi

echo "[PERFILES] Limpiando caché de configuración..."
php artisan config:clear || true
php artisan cache:clear || true

echo "[PERFILES] Ejecutando scripts post-autoload de Composer..."
composer run-script post-autoload-dump || true

# Generate app key if not set
if [ -z "$APP_KEY" ] || [ "$APP_KEY" = "" ]; then
  echo "[PERFILES] Generando APP_KEY..."
  php artisan key:generate --force
fi

echo "[PERFILES] Ejecutando migraciones..."
php artisan migrate --force

echo "[PERFILES] Iniciando consumer de eventos de empleados desde RabbitMQ en background..."
php artisan rabbitmq:listen-empleados &

echo "[PERFILES] Iniciando servidor HTTP en puerto 8083..."
exec php artisan serve --host=0.0.0.0 --port=8083
