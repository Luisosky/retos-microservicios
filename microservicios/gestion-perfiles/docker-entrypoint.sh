#!/bin/sh
set -e

# Generate app key if not set
if [ -z "$APP_KEY" ] || [ "$APP_KEY" = "" ]; then
  echo "[PERFILES] Generando APP_KEY..."
  php artisan key:generate --force
fi

echo "[PERFILES] Ejecutando migraciones..."
php artisan migrate --force

echo "[PERFILES] Iniciando consumer de RabbitMQ en background..."
php artisan perfiles:consume-eventos &

echo "[PERFILES] Iniciando servidor HTTP en puerto 8083..."
exec php artisan serve --host=0.0.0.0 --port=8083
