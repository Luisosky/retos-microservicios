#!/bin/bash
# Despliegue rápido de verificación - Reto 6 Parte 2
# Este script automatiza el setup y verificación completa

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   DESPLIEGUE RÁPIDO: Reto 6 Parte 2 - Pipeline CI        ║"
echo "║   JWT + Maven + SonarQube Ready                           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Función auxiliar
info() { echo "ℹ️  $1"; }
success() { echo "✅ $1"; }
warning() { echo "⚠️  $1"; }
error() { echo "❌ $1"; }

# 1. Verificar Docker
info "Verificando Docker..."
if ! command -v docker &> /dev/null; then
    error "Docker no está instalado"
    exit 1
fi
success "Docker disponible"

# 2. Verificar .env
info "Verificando archivo .env..."
if [ ! -f ".env" ]; then
    warning "Archivo .env no encontrado, creando desde .example..."
    if [ -f "Jenkins/.env.example" ]; then
        cp Jenkins/.env.example .env
        echo ""
        echo "📝 IMPORTANTE: Edita .env y agrega valores seguros:"
        echo "   JWT_SECRET=tu-clave-super-segura-32-caracteres-minimo"
        echo "   SONARQUBE_TOKEN=squ_xxxxxxxx"
        echo ""
        read -p "¿Ya editaste .env? (s/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Ss]$ ]]; then
            error "Por favor edita .env primero"
            exit 1
        fi
    fi
else
    success ".env encontrado"
fi

# 3. Levantar Jenkins
info "Levantando Jenkins con Docker Compose..."
docker-compose up --build -d jenkins

if [ $? -eq 0 ]; then
    success "Jenkins iniciado"
else
    error "Error iniciando Jenkins"
    exit 1
fi

# 4. Esperar a que Jenkins esté listo
info "Esperando a que Jenkins esté listo... (esto toma ~60-90 segundos)"
for i in {1..30}; do
    if curl -s http://localhost:9090/login > /dev/null 2>&1; then
        success "Jenkins respondiendo en http://localhost:9090"
        break
    fi
    echo -n "."
    sleep 3
done
echo ""

# 5. Ejecutar verificación
info "Ejecutando verificación de componentes..."
bash Jenkins/verify_pipeline.sh

# 6. Mostrar resumen
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    🎉 LISTO PARA USAR 🎉                 ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📍 Ubicaciones importantes:"
echo ""
echo "   🌐 Jenkins Web UI"
echo "      http://localhost:9090"
echo ""
echo "   📄 Pipeline a ejecutar"
echo "      Empleados-Pipeline"
echo ""
echo "   📚 Documentación"
echo "      QUICK_START_PARTE2.md      - Guía rápida"
echo "      ENTREGA_PARTE2_RETO6.md    - Resumen completo"
echo "      Jenkins/CI_PIPELINE_PARTE2.md - Documentación técnica"
echo ""
echo "🚀 Próximos pasos:"
echo ""
echo "   1. Acceder a http://localhost:9090"
echo "   2. Click en 'Empleados-Pipeline'"
echo "   3. Click en 'Build Now'"
echo "   4. Ver progreso en logs"
echo ""
echo "📊 Ver reportes:"
echo ""
echo "   - Logs en vivo:"
echo "     docker logs jenkins-server -f"
echo ""
echo "   - Test Report:"
echo "     Jenkins UI → Empleados-Pipeline → [Build] → Test Report"
echo ""
echo "   - Code Coverage (JaCoCo):"
echo "     Jenkins UI → Empleados-Pipeline → [Build] → JaCoCo Coverage Report"
echo ""
echo "🔧 Para más ayuda:"
echo ""
echo "   bash Jenkins/verify_pipeline.sh     # Validar configuración"
echo "   docker logs jenkins-server -f       # Ver logs"
echo "   curl http://localhost:9090/api/json # API Jenkins"
echo ""
