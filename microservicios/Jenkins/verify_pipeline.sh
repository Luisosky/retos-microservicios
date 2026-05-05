#!/bin/bash
# Script de verificación para Pipeline CI de Empleados (Reto 6 - Parte 2)
# Valida que Jenkins, credenciales y el Jenkinsfile estén correctamente configurados

set -e

echo "=================================================="
echo "Verificación del Pipeline CI - Reto 6 Parte 2"
echo "=================================================="
echo ""

# Colores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para print status
check_status() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $1${NC}"
    else
        echo -e "${RED}✗ $1${NC}"
        return 1
    fi
}

# 1. Verificar que Jenkins está ejecutándose
echo "1️⃣  Verificando servicio Jenkins..."
if docker ps | grep -q jenkins-server; then
    check_status "Jenkins container está ejecutándose"
else
    echo -e "${RED}✗ Jenkins no está ejecutándose${NC}"
    echo "  Ejecuta: docker-compose up -d jenkins"
    exit 1
fi

# 2. Verificar conectividad a Jenkins
echo ""
echo "2️⃣  Verificando conectividad a Jenkins (puerto 9090)..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:9090/login | grep -q "200"; then
    check_status "Jenkins responde en http://localhost:9090"
else
    echo -e "${YELLOW}⚠ Jenkins aún está iniciando, esperando...${NC}"
    sleep 10
fi

# 3. Verificar que Jenkinsfile existe
echo ""
echo "3️⃣  Verificando archivos necesarios..."
if [ -f "gestion-empleados/Jenkinsfile" ]; then
    check_status "Jenkinsfile existe"
else
    echo -e "${RED}✗ Jenkinsfile no encontrado${NC}"
    exit 1
fi

# 4. Verificar pom.xml
if [ -f "gestion-empleados/pom.xml" ]; then
    check_status "pom.xml existe"
else
    echo -e "${RED}✗ pom.xml no encontrado${NC}"
    exit 1
fi

# 5. Verificar casc.yaml tiene credenciales
echo ""
echo "4️⃣  Verificando configuración JCasC..."
if grep -q "jwt-secret-key" Jenkins/casc.yaml; then
    check_status "Credencial JWT definida en casc.yaml"
else
    echo -e "${RED}✗ Credencial JWT no encontrada en casc.yaml${NC}"
    exit 1
fi

if grep -q "Empleados-Pipeline" Jenkins/casc.yaml; then
    check_status "Job DSL 'Empleados-Pipeline' definido"
else
    echo -e "${YELLOW}⚠ Job DSL 'Empleados-Pipeline' no encontrado${NC}"
fi

# 6. Verificar Docker socket montado
echo ""
echo "5️⃣  Verificando Docker Socket Mount..."
if docker exec jenkins-server test -e /var/run/docker.sock; then
    check_status "Docker socket accesible desde Jenkins"
else
    echo -e "${RED}✗ Docker socket no accesible${NC}"
fi

# 7. Verificar Docker CLI en Jenkins
echo ""
echo "6️⃣  Verificando Docker CLI en Jenkins..."
if docker exec jenkins-server docker --version > /dev/null 2>&1; then
    VERSION=$(docker exec jenkins-server docker --version)
    check_status "Docker CLI disponible: $VERSION"
else
    echo -e "${RED}✗ Docker CLI no disponible${NC}"
fi

# 8. Verificar Maven en el contenedor
echo ""
echo "7️⃣  Verificando Maven..."
if docker run --rm -q maven:3.9-eclipse-temurin-17 mvn --version > /dev/null 2>&1; then
    check_status "Maven image disponible"
else
    echo -e "${YELLOW}⚠ Maven image no disponible localmente (se descargará en primer build)${NC}"
fi

# 9. Verificar Plugins instalados
echo ""
echo "8️⃣  Verificando plugins instalados..."
if docker exec jenkins-server ls /var/jenkins_home/plugins/ | grep -q "configuration-as-code"; then
    check_status "Plugin 'configuration-as-code' instalado"
else
    echo -e "${YELLOW}⚠ Esperando a que se instalen los plugins...${NC}"
fi

if docker exec jenkins-server ls /var/jenkins_home/plugins/ | grep -q "workflow-aggregator"; then
    check_status "Plugin 'workflow-aggregator' instalado"
fi

if docker exec jenkins-server ls /var/jenkins_home/plugins/ | grep -q "docker-pipeline"; then
    check_status "Plugin 'docker-pipeline' instalado"
fi

# 10. Verificar volumen maven-cache
echo ""
echo "9️⃣  Verificando volúmenes Docker..."
if docker volume ls | grep -q "maven-cache"; then
    check_status "Volumen 'maven-cache' existe"
else
    echo -e "${YELLOW}⚠ Volumen 'maven-cache' se creará en primer build${NC}"
fi

# 11. Verificar configuración de .env
echo ""
echo "🔟 Verificando variables de entorno..."
if [ -f ".env" ]; then
    if grep -q "JWT_SECRET" .env; then
        JWT_VALUE=$(grep "^JWT_SECRET=" .env | cut -d'=' -f2)
        if [ ${#JWT_VALUE} -ge 32 ]; then
            check_status "JWT_SECRET configurada (${#JWT_VALUE} caracteres)"
        else
            echo -e "${RED}✗ JWT_SECRET muy corta (mínimo 32 caracteres)${NC}"
        fi
    else
        echo -e "${YELLOW}⚠ JWT_SECRET no configurada en .env${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Archivo .env no encontrado (usando valores por defecto)${NC}"
fi

echo ""
echo "=================================================="
echo "✅ Verificación completada"
echo "=================================================="
echo ""
echo "📝 Próximos pasos:"
echo ""
echo "1. Acceder a Jenkins:"
echo "   http://localhost:9090"
echo ""
echo "2. Ejecutar el pipeline:"
echo "   - Ir a 'Empleados-Pipeline'"
echo "   - Click en 'Build Now' (o 'Build with Parameters' para SonarQube)"
echo ""
echo "3. Ver logs en tiempo real:"
echo "   docker logs jenkins-server -f"
echo ""
echo "4. Ver reportes:"
echo "   - JaCoCo: Jenkins UI → Empleados-Pipeline → Build → JaCoCo Coverage Report"
echo "   - Tests: Jenkins UI → Empleados-Pipeline → Build → Test Report"
echo ""
