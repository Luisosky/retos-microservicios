# 📑 INDEX - Reto 6: Integración Continua (Partes 1 & 2)

## 🎯 Objetivo General

Implementar un servidor Jenkins completamente automatizado y pre-configurado mediante Docker, capaz de ejecutar pipelines CI/CD seguros para microservicios con manejo de credenciales JWT.

---

## 📖 ÍNDICE COMPLETO

### 🔵 PARTE 1: Configuración Básica de Jenkins con JCasC

#### Documentos de Referencia
- **README.md** → Descripción general + características
- **Dockerfile** → Construcción de imagen Jenkins LTS-JDK17
- **casc.yaml** → Configuración automática + pipeline "Prueba-Docker"

#### Características Entregadas
✅ Jenkins server pre-configurado  
✅ Plugins automáticamente instalados  
✅ Docker-in-Docker funcional  
✅ Pipeline de prueba (docker --version + docker ps)  
✅ Healthcheck configurado  
✅ Red microservices-net integrada  

#### Cómo Levantar (Parte 1)
```bash
docker-compose up --build -d jenkins
curl http://localhost:9090/login
```

---

### 🟢 PARTE 2: Pipeline CI con JWT, Maven y Gestión de Secretos

#### Documentos Principales

| Documento | Ubicación | Propósito |
|-----------|-----------|----------|
| **QUICK_START_PARTE2.md** | Raíz | Guía rápida (5 minutos) |
| **ENTREGA_PARTE2_RETO6.md** | Raíz | Resumen completo de entregables |
| **ARQUITECTURA_PARTE2.md** | Raíz | Diagramas y flujos de la arquitectura |
| **CI_PIPELINE_PARTE2.md** | Jenkins/ | Documentación técnica detallada |
| **Jenkinsfile** | gestion-empleados/ | Pipeline declarativo (320 líneas) |
| **casc.yaml** | Jenkins/ | JCasC con credenciales + Job DSL |

#### Scripts de Ayuda

| Script | Ubicación | Propósito |
|--------|-----------|----------|
| **verify_pipeline.sh** | Jenkins/ | Validación en Bash (Linux/Mac) |
| **verify_pipeline.ps1** | Jenkins/ | Validación en PowerShell (Windows) |
| **deploy_parte2.sh** | Raíz | Despliegue automatizado + guía |

#### Archivos de Configuración

| Archivo | Ubicación | Propósito |
|---------|-----------|----------|
| **.env** | Raíz | Variables reales de secretos |
| **docker-compose.yml** | Raíz | Actualizado con jenkins + env vars |

#### Características Entregadas

✅ Jenkinsfile declarativo con Docker  
✅ Manejo seguro de JWT_SECRET  
✅ Caché Maven para velocidad  
✅ 5 etapas de calidad:
  - Build (mvn clean compile)
  - Test (mvn test + JaCoCo)
  - Code Coverage (reportes XML)
  - SonarQube (opcional)
  - Docker Image (empaquetado)

✅ Credenciales en casc.yaml  
✅ Job DSL automatizado  
✅ Reportes JUnit + JaCoCo  
✅ Post-processing con notificaciones  

#### Cómo Levantar (Parte 2)

```bash
# 1. Verificar .env
# El archivo raíz ya debe contener JWT_SECRET y SONARQUBE_TOKEN

# 2. Levantar Jenkins
docker-compose up --build -d jenkins

# 3. Verificar
bash Jenkins/verify_pipeline.sh  # o .ps1 en Windows

# 4. Ejecutar pipeline
# Opción A: UI (http://localhost:9090 → Empleados-Pipeline → Build Now)
# Opción B: CLI (curl -X POST http://localhost:9090/job/Empleados-Pipeline/build)
```

---

## 🗂️ ESTRUCTURA DE CARPETAS

```
microservicios/
│
├── 📄 QUICK_START_PARTE2.md          ← EMPEZAR AQUÍ
├── 📄 ENTREGA_PARTE2_RETO6.md        ← Resumen ejecutivo
├── 📄 ARQUITECTURA_PARTE2.md         ← Diagramas
├── 📄 deploy_parte2.sh               ← Setup automatizado
│
├── .env (LOCAL)
│   └─ JWT_SECRET=...
│   └─ SONARQUBE_TOKEN=...
│
├── docker-compose.yml                ← ACTUALIZADO (Part 2)
│
├── Jenkins/                          ← PARTE 1 & 2
│   ├── Dockerfile                    ← Part 1
│   ├── casc.yaml                     ← ACTUALIZADO (Part 2)
│   ├── README.md                     ← Part 1
│   ├── CI_PIPELINE_PARTE2.md         ← Part 2
│   ├── .env                          ← Variables reales
│   ├── verify_pipeline.sh            ← Part 2
│   └── verify_pipeline.ps1           ← Part 2
│
├── gestion-empleados/                ← CÓDIGO MICROSERVICIO
│   ├── Jenkinsfile                   ← NUEVO (Part 2)
│   ├── pom.xml                       ← Maven
│   ├── src/
│   │  ├── main/java/...
│   │  └── test/java/...
│   └── target/
│      ├── surefire-reports/          ← JUnit reports
│      └── site/jacoco/               ← Coverage reports
│
├── gestion-departamentos/            ← Otros microservicios
├── gestion-notificaciones/
├── gestion-perfiles/
└── servicio-Autenticación/
```

---

## 🔐 GESTIÓN DE SECRETOS

### Variables de Entorno Necesarias

```env
# Archivo: .env (local, en .gitignore)

# ⭐ REQUERIDA: JWT Secret para firma de tokens
JWT_SECRET=tu-clave-super-segura-con-minimo-32-caracteres-HS256

# Opcional: Token para análisis SonarQube
SONARQUBE_TOKEN=squ_xxxxxxxx...
```

### Flujo de Credenciales

```
.env (LOCAL)
  ↓
docker-compose.yml (interpola)
  ↓
Jenkins container (ENV)
  ↓
casc.yaml (lee ${JWT_SECRET})
  ↓
Jenkins Credentials (encriptado)
  ↓
Jenkinsfile (credentials('jwt-secret-key'))
  ↓
Maven container (variable de entorno)
  ↓
Tests (System.getenv("JWT_SECRET"))
  ↓
Logs (*** - enmascarado)
```

---

## ✅ CHECKLIST DE IMPLEMENTACIÓN

### Prerequisitos
- [ ] Docker instalado
- [ ] Docker Compose instalado
- [ ] 2GB RAM disponible
- [ ] Puertos 9090, 50000 libres

### Setup Inicial
- [ ] Verificar `JWT_SECRET` en `.env`
- [ ] Verificar `SONARQUBE_TOKEN` en `.env` (opcional)
- [ ] `docker-compose up --build -d jenkins`
- [ ] Esperar 60-90 segundos
- [ ] Ejecutar `verify_pipeline.sh` o `.ps1`

### Verificación
- [ ] Jenkins accesible en http://localhost:9090
- [ ] Empleados-Pipeline visible en UI
- [ ] Credencial "jwt-secret-key" registrada
- [ ] Volumen maven-cache existente
- [ ] Docker socket accesible desde Jenkins

### Ejecución
- [ ] Build manual exitoso (sin parámetros)
- [ ] Test Report disponible
- [ ] JaCoCo Coverage Report disponible
- [ ] Logs muestran JWT_SECRET: ****

### Escalabilidad
- [ ] Patrón replicable para otros microservicios
- [ ] Misma credencial JWT para todos
- [ ] Job DSL fácilmente extensible

---

## 📊 REPORTES GENERADOS

### Por Build

| Reporte | Ubicación | Acceso en Jenkins |
|---------|-----------|------------------|
| **JUnit Test Report** | target/surefire-reports/ | Build → Test Report |
| **JaCoCo Coverage** | target/site/jacoco/ | Build → JaCoCo Coverage Report |
| **Console Output** | Jenkins logs | Build → Console Output |
| **SonarQube** | sonarqube:9000 | (Si RUN_SONAR=true) |

### Métricas Disponibles

```
Tests:
  ├─ Total ejecutados
  ├─ Pasados/Fallidos
  ├─ Duración
  └─ Trazas de error

Coverage:
  ├─ Cobertura de líneas %
  ├─ Cobertura de ramas %
  ├─ Por clase
  └─ Por método

SonarQube (Opcional):
  ├─ Code smells
  ├─ Vulnerabilities
  ├─ Code duplication
  ├─ Technical debt
  └─ Integración JaCoCo
```

---

## 🚀 PRÓXIMOS PASOS

### Corto Plazo (Completar Reto 6)
- [ ] Parte 3: Notificaciones + Deployment
- [ ] Agregar SonarQube server
- [ ] Integración Slack/Email
- [ ] Blue/Green deployment

### Mediano Plazo (Pasar a otro reto)
- [ ] Pipelines para gestion-departamentos
- [ ] Pipelines para gestion-perfiles
- [ ] Pipelines para gestion-notificaciones
- [ ] Pipelines para servicio-autenticación

### Largo Plazo
- [ ] GitOps workflow
- [ ] Helm charts para deployment
- [ ] Observability (ELK, Prometheus)
- [ ] Seguridad (SAST, DAST, Scanning)

---

## 🎓 CONCEPTOS CLAVE

### Pipeline as Code ✓
El pipeline vive con el código, se versiona y es reproducible.

### Configuration as Code ✓
Jenkins pre-configurado sin interfaz manual, mediante YAML.

### Credenciales en Jenkins ✓
NO en código, enmascaradas en logs, encriptadas en storage.

### Docker Aislamiento ✓
Cada build en contenedor limpio, reproducible, sin contaminación.

### Reportes Integrados ✓
JUnit, JaCoCo, SonarQube - métricas de calidad automáticas.

---

## 📞 TROUBLESHOOTING RÁPIDO

### Jenkins no inicia
```bash
docker logs jenkins-server -f
# Esperar 90 segundos, el setup toma tiempo
```

### Credencial no encontrada
```bash
docker restart jenkins-server
# Reiniciar para que casc.yaml recargue
```

### Tests fallan sin JWT
```bash
cat .env | grep JWT_SECRET
# Verificar que está configurada y tiene 32+ caracteres
```

### Maven tarda mucho
```bash
# Normal en primera ejecución. Próximas builds serán rápidas.
# El caché .m2 se persiste entre builds.
```

---

## 📚 LECTURAS RECOMENDADAS (EN ORDEN)

1. **QUICK_START_PARTE2.md** ← Empezar aquí (5 min)
2. **ENTREGA_PARTE2_RETO6.md** ← Resumen ejecutivo (10 min)
3. **ARQUITECTURA_PARTE2.md** ← Entender flujos (15 min)
4. **CI_PIPELINE_PARTE2.md** ← Detalles técnicos (30 min)
5. **Jenkinsfile** ← Analizar código (15 min)
6. **casc.yaml** ← Ver configuración (10 min)

**Total: ~90 minutos para entendimiento completo**

---

## 🏆 RESUMEN DE LOGROS

✅ **Parte 1**: Jenkins pre-configurado con JCasC  
✅ **Parte 2**: Pipeline CI con Maven + JWT + reportes  
✅ **Seguridad**: Credenciales gestionadas correctamente  
✅ **Escalabilidad**: Patrón replicable a otros microservicios  
✅ **Documentación**: Guías completas + troubleshooting  
✅ **Automatización**: Scripts de setup + validación  

---

## 📞 CONTACTO / SOPORTE

Para preguntas o problemas:
1. Revisar archivos de documentación
2. Ejecutar scripts de validación
3. Revisar logs: `docker logs jenkins-server -f`
4. Revisar sección Troubleshooting

---

**Estado Final: ✅ COMPLETADO**

**Fecha**: Mayo 4, 2026  
**Reto**: 6 - Integración Continua  
**Partes Completadas**: 1/3 ✅, 2/3 ✅  
**Próxima**: Parte 3 - Notificaciones y Deployment
