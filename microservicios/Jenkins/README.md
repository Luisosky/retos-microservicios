# Jenkins Configuration as Code (JCasC) - Reto 6

## 📋 Descripción General

Sistema de CI/CD completamente automatizado y pre-configurado mediante Docker, usando JCasC para infraestructura como código.

### Partes del Reto

- **Parte 1**: [Configuración Básica con JCasC](README.md) - Setup automático de Jenkins, plugins y pipeline de prueba
- **Parte 2**: [Pipeline CI con JWT y Maven](CI_PIPELINE_PARTE2.md) - Build, tests, JaCoCo, gestión de secretos JWT

## 🚀 Inicio Rápido

### Prerequisitos
- Docker y docker-compose instalados
- Archivo `.env` en la raíz con variables de secretos

### Levantamiento

```bash
# Build e inicio
docker-compose up --build -d jenkins

# Esperar 60-90 segundos a que Jenkins inicie
sleep 90

# Acceder
open http://localhost:9090
```

### Verificación

**Linux/Mac:**
```bash
bash Jenkins/verify_pipeline.sh
```

**Windows PowerShell:**
```powershell
.\Jenkins\verify_pipeline.ps1
```

## 📁 Estructura

## Características

### Dockerfile
- **Imagen base**: `jenkins/jenkins:lts-jdk17`
- **Docker-in-Docker**: Cliente Docker instalado con acceso al socket del host
- **Plugins pre-instalados**:
  - `workflow-aggregator`: Declarative y Scripted Pipelines
  - `docker-pipeline`: Integración con Docker
  - `git`: Gestión de repositorios Git
  - `configuration-as-code`: Configuración automática (JCasC)
  - `sonar`: Integración con SonarQube
  - `job-dsl`: DSL para creación de jobs
  - `pipeline-stage-view`: Visualización de etapas en pipelines

### Configuración JCasC (casc.yaml)
- **Setup Wizard desactivado**: Jenkins inicia sin necesidad de configuración manual
- **Security Realm**: Local sin sign-up
- **Authorization**: Control de acceso basado en roles (admin, developer)
- **Pipeline "Prueba-Docker"**: Job de prueba declarativo que verifica Docker

### Infraestructura Docker
- **Puertos**:
  - `9090`: Interfaz web de Jenkins (http://localhost:9090)
  - `50000`: Puerto para conexión de agentes
- **Volúmenes**:
  - `jenkins_data`: Persistencia de datos y configuración
  - `/var/run/docker.sock`: Acceso a Docker del host (Docker Socket Mount)
- **Networking**: Integrado en la red `microservices-net`
- **Health Check**: Validación del endpoint de login

## Pipeline de Prueba "Prueba-Docker"

El pipeline incluye tres etapas:

### Etapa 1: Verificar Docker
```bash
docker --version
```
Verifica que Docker está instalado y disponible en Jenkins.

### Etapa 2: Listar Contenedores
```bash
docker ps
```
Muestra todos los contenedores Docker activos.

### Etapa 3: Información del Sistema
```bash
docker info | head -20
```
Proporciona información detallada sobre el daemon de Docker.

## Instrucciones de Levantamiento

### 1. Desde la raíz del proyecto
```bash
docker-compose up --build -d jenkins
```

### 2. Esperar a que Jenkins esté listo
```bash
# Verificar logs
docker logs jenkins-server -f

# Esperar hasta ver:
# "Jenkins is fully up and running"
```

### 3. Acceder a la interfaz web
```
http://localhost:9090
```

### 4. Ejecutar el pipeline de prueba
1. Ir a la página principal de Jenkins
2. Hacer clic en el job "Prueba-Docker"
3. Hacer clic en "Build Now"
4. Ver el progreso en el console output

## Verificación de Configuración

Para verificar que todo está correctamente configurado:

```bash
# Verificar que Jenkins puede ejecutar Docker
docker exec jenkins-server docker ps

# Ver logs de configuración JCasC
docker logs jenkins-server | grep "JCasC"

# Verificar que el job está creado
curl http://localhost:9090/api/json | grep -i "prueba-docker"
```

## Archivos de Configuración

- `Dockerfile`: Define la imagen de Jenkins con plugins y configuración
- `casc.yaml`: Configuración como código - auto-provisiona Jenkins al iniciar
- `docker-compose.yml`: Define el servicio Jenkins en la infraestructura

## Volúmenes y Persistencia

Los datos de Jenkins se almacenan en el volumen `jenkins_data`. Si necesitas limpiar completamente:

```bash
# Eliminar Jenkins y su volumen
docker-compose down -v jenkins

# Levantar nuevamente
docker-compose up --build -d jenkins
```

## Troubleshooting

### Jenkins no inicia
```bash
# Ver logs detallados
docker logs jenkins-server

# Aumentar límites de memoria si es necesario
docker stats jenkins-server
```

### No puedo ejecutar Docker desde Jenkins
```bash
# Verificar permisos del socket
docker exec jenkins-server ls -la /var/run/docker.sock

# Verificar que jenkins está en grupo docker
docker exec jenkins-server groups jenkins
```

### Pipeline no aparece
```bash
# Reiniciar Jenkins para recargar JCasC
docker restart jenkins-server

# Ver logs de JCasC
docker logs jenkins-server | grep -i "casc"
```

## Próximos Pasos (Reto 6 - Parte 2)

- Configurar integración con repositorio Git
- Crear pipelines para cada microservicio
- Configurar SonarQube para análisis de código
- Implementar deployment automático

## Referencias

- [Jenkins Official Image](https://hub.docker.com/r/jenkins/jenkins)
- [Jenkins Configuration as Code](https://plugins.jenkins.io/configuration-as-code/)
- [Docker Pipeline Plugin](https://plugins.jenkins.io/docker-pipeline/)
- [Jenkins Job DSL](https://plugins.jenkins.io/job-dsl/)
