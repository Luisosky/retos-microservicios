FROM php:8.2-fpm-alpine AS base

# Install system dependencies
RUN apk add --no-cache \
    curl \
    libpng-dev \
    libxml2-dev \
    zip \
    unzip \
    git \
    oniguruma-dev \
    rabbitmq-c-dev \
    autoconf \
    gcc \
    g++ \
    make

# Install PHP extensions
RUN docker-php-ext-install \
    pdo \
    pdo_mysql \
    mbstring \
    exif \
    pcntl \
    bcmath \
    gd \
    opcache

# Install AMQP extension for RabbitMQ
RUN pecl install amqp && docker-php-ext-enable amqp

# Install Composer
COPY --from=composer:2.6 /usr/bin/composer /usr/bin/composer

WORKDIR /var/www

# Copy dependency files first (layer caching)
COPY composer.json composer.lock* ./

# Install PHP dependencies (no dev for production)
RUN composer install --no-dev --no-interaction --optimize-autoloader --no-scripts

# Copy application source
COPY . .

# Set permissions
RUN chown -R www-data:www-data /var/www \
    && chmod -R 755 /var/www/storage \
    && chmod -R 755 /var/www/bootstrap/cache \
    && chmod +x /var/www/docker-entrypoint.sh

EXPOSE 8083

ENTRYPOINT ["/var/www/docker-entrypoint.sh"]
