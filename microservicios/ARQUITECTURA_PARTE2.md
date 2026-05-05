# Arquitectura del Pipeline CI - Reto 6 Parte 2

## 🏗️ Diagrama de Flujo

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         USUARIO / CI/CD TRIGGER                         │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     JENKINS SERVER (Docker)                              │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │ JCasC Configuration (casc.yaml)                                  │  │
│  │  • Credenciales: jwt-secret-key, sonarqube-token                │  │
│  │  • Jobs: Prueba-Docker, Empleados-Pipeline                     │  │
│  │  • Seguridad: Local auth + Role-based access                   │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ Job: Empleados-Pipeline (Jenkinsfile)                           │   │
│  │                                                                  │   │
│  │  1. CHECKOUT                                                    │   │
│  │     └─ git clone gestion-empleados                            │   │
│  │                                                                  │   │
│  │  2. BUILD (Agente Docker: maven:3.9-eclipse-temurin-17)        │   │
│  │     ├─ mvn clean compile -DskipTests                           │   │
│  │     └─ Cache: /root/.m2 (volumen maven-cache)                 │   │
│  │                                                                  │   │
│  │  3. TEST (Con JWT_SECRET inyectado)                            │   │
│  │     ├─ Cargar credencial 'jwt-secret-key'                      │   │
│  │     ├─ Pasar como JWT_SECRET (variable env)                    │   │
│  │     ├─ mvn test + JaCoCo                                        │   │
│  │     └─ Logs: JWT_SECRET enmascarado (****)                     │   │
│  │                                                                  │   │
│  │  4. CODE COVERAGE                                              │   │
│  │     └─ mvn jacoco:report → target/site/jacoco/jacoco.xml      │   │
│  │                                                                  │   │
│  │  5. SONARQUBE (Opcional)                                       │   │
│  │     ├─ Parámetro: RUN_SONAR=true                               │   │
│  │     ├─ mvn sonar:sonar (con sonarqube-token)                   │   │
│  │     └─ Integra reportes JaCoCo                                │   │
│  │                                                                  │   │
│  │  6. BUILD DOCKER IMAGE                                         │   │
│  │     └─ mvn package -DskipTests → target/gestion-empleados.jar │   │
│  │                                                                  │   │
│  │  7. POST (Reportes + Notificaciones)                           │   │
│  │     ├─ Publish JUnit Report                                    │   │
│  │     ├─ Publish JaCoCo HTML Report                              │   │
│  │     └─ Echo Success/Failure/Aborted                           │   │
│  │                                                                  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ Reportes Publicados:                                            │   │
│  │  • target/surefire-reports/*.xml → Test Report                │   │
│  │  • target/site/jacoco/index.html → Coverage Report            │   │
│  │  • Console Output (Logs)                                       │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
   ┌─────────┐  ┌──────────┐  ┌─────────────┐
   │  JUnit  │  │ JaCoCo   │  │ SonarQube   │
   │ Reports │  │ Coverage │  │  Analysis   │
   └─────────┘  └──────────┘  └─────────────┘
```

---

## 🔐 Flujo de Credenciales (JWT_SECRET)

```
┌──────────────────────────────────────────────────────────────────────┐
│ MÁQUINA LOCAL                                                         │
│ ┌────────────────────────────────────────────────────────────────┐  │
│ │ .env (LOCAL, NO VERSIONADO)                                   │  │
│ │ JWT_SECRET=clave-super-segura-32-caracteres                   │  │
│ └────────────┬───────────────────────────────────────────────────┘  │
│              │                                                       │
│              ▼                                                       │
│ ┌────────────────────────────────────────────────────────────────┐  │
│ │ docker-compose.yml                                            │  │
│ │ environment:                                                  │  │
│ │   JWT_SECRET: ${JWT_SECRET}  ◄─ Interpolación                │  │
│ └────────────┬───────────────────────────────────────────────────┘  │
└──────────────┼──────────────────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────────────────┐
│ CONTENEDOR JENKINS                                                    │
│ ┌────────────────────────────────────────────────────────────────┐  │
│ │ Variables de Entorno (De docker-compose)                      │  │
│ │ JWT_SECRET=clave-super-segura-32-caracteres                   │  │
│ │ SONARQUBE_TOKEN=squ_xxxxx                                     │  │
│ └────────────┬───────────────────────────────────────────────────┘  │
│              │                                                       │
│              ▼                                                       │
│ ┌────────────────────────────────────────────────────────────────┐  │
│ │ casc.yaml (JCasC Configuration)                               │  │
│ │ credentials:                                                  │  │
│ │   - id: "jwt-secret-key"                                      │  │
│ │     secret: "${JWT_SECRET}"  ◄─ Lee variable env             │  │
│ │                                                               │  │
│ │ Resultado: Credencial "jwt-secret-key" almacenada en         │  │
│ │ Jenkins Credentials (encriptada)                             │  │
│ └────────────┬───────────────────────────────────────────────────┘  │
│              │                                                       │
│              ▼                                                       │
│ ┌────────────────────────────────────────────────────────────────┐  │
│ │ Jenkinsfile (Al ejecutar job)                                │  │
│ │                                                               │  │
│ │ environment {                                                │  │
│ │   JWT_SECRET = credentials('jwt-secret-key')  ◄─ Desencripta│  │
│ │ }                                                             │  │
│ │                                                               │  │
│ │ ⚠️  Jenkins ENMASCARA en logs:                              │  │
│ │ [Pipeline] Decrypting secret variables                       │  │
│ │ *** (valor oculto) ***                                       │  │
│ └────────────┬───────────────────────────────────────────────────┘  │
│              │                                                       │
│              ▼                                                       │
│ ┌────────────────────────────────────────────────────────────────┐  │
│ │ Contenedor Maven (Agente Docker)                             │  │
│ │                                                               │  │
│ │ environment {                                                │  │
│ │   JWT_SECRET = (valor desencriptado de Jenkins)             │  │
│ │ }                                                             │  │
│ │                                                               │  │
│ │ $ mvn test  ◄─ JWT_SECRET disponible como var env          │  │
│ │                                                               │  │
│ │ Tests acceden:                                              │  │
│ │ String secret = System.getenv("JWT_SECRET")                 │  │
│ └────────────┬───────────────────────────────────────────────────┘  │
└──────────────┼──────────────────────────────────────────────────────┘
               │
               ▼
        ┌─────────────────┐
        │ Build Completa  │
        │ JWT_SECRET no   │
        │ persiste en     │
        │ disco           │
        └─────────────────┘
```

---

## 📂 Estructura de Archivos Entregados

```
microservicios/
├── .env (LOCAL)
│   └─ JWT_SECRET=...
│   └─ SONARQUBE_TOKEN=...
│
├── docker-compose.yml (ACTUALIZADO)
│   ├─ jenkins:
│   │  ├─ build: ./Jenkins
│   │  ├─ ports: 9090:8080, 50000:50000
│   │  ├─ volumes:
│   │  │  ├─ jenkins_data
│   │  │  └─ /var/run/docker.sock
│   │  └─ environment:
│   │     ├─ JWT_SECRET: ${JWT_SECRET}
│   │     └─ SONARQUBE_TOKEN: ${SONARQUBE_TOKEN}
│   └─ networks: microservices-net
│
├── Jenkins/ (COMPLETO)
│   ├─ Dockerfile (Parte 1)
│   ├─ casc.yaml (ACTUALIZADO - Parte 2)
│   │  ├─ Credenciales:
│   │  │  ├─ jwt-secret-key (Secret text)
│   │  │  └─ sonarqube-token
│   │  └─ Jobs DSL:
│   │     ├─ Prueba-Docker (Parte 1)
│   │     └─ Empleados-Pipeline (Parte 2)
│   │
│   ├─ .env.example (NUEVO)
│   ├─ README.md (Actualizado)
│   ├─ CI_PIPELINE_PARTE2.md (NUEVO)
│   ├─ verify_pipeline.sh (NUEVO)
│   ├─ verify_pipeline.ps1 (NUEVO)
│   └─ casc.yaml (ACTUALIZADO)
│
├── gestion-empleados/
│   ├─ pom.xml
│   ├─ Jenkinsfile (NUEVO - Parte 2)
│   ├─ src/
│   │  ├─ main/java/...
│   │  └─ test/java/...
│   └─ target/
│      ├─ surefire-reports/
│      └─ site/jacoco/
│
├── QUICK_START_PARTE2.md (NUEVO)
├─ ENTREGA_PARTE2_RETO6.md (NUEVO)
└─ deploy_parte2.sh (NUEVO)
```

---

## 🔄 Ciclo de Ejecución Completo

```
1️⃣  USUARIO DISPARA BUILD
    └─ Jenkins UI: Click "Build Now"
       o CLI: curl -X POST http://localhost:9090/job/Empleados-Pipeline/build

2️⃣  JENKINS LEE casc.yaml
    └─ Carga credenciales:
       • jwt-secret-key: decrypta ${JWT_SECRET} desde env
       • sonarqube-token: decrypta ${SONARQUBE_TOKEN}

3️⃣  JENKINSFILE INICIA
    └─ agent: docker { image 'maven:3.9-eclipse-temurin-17' }
    └─ Levanta contenedor Maven limpio

4️⃣  CHECKOUT
    └─ git clone / copia código

5️⃣  BUILD
    └─ mvn clean compile
    └─ Cache Maven .m2 reutilizado (rápido)

6️⃣  TEST (CON CREDENCIALES)
    └─ environment { JWT_SECRET = credentials('jwt-secret-key') }
    └─ JWT_SECRET inyectado como variable env
    └─ mvn test (tests acceden a JWT_SECRET)
    └─ JaCoCo genera reports
    └─ Logs muestran: JWT_SECRET: ****

7️⃣  CODE COVERAGE
    └─ mvn jacoco:report
    └─ Genera: target/site/jacoco/jacoco.xml

8️⃣  SONARQUBE (OPCIONAL)
    └─ if (params.RUN_SONAR == true)
    └─ mvn sonar:sonar
    └─ Envía análisis a servidor SonarQube

9️⃣  DOCKER IMAGE
    └─ mvn package
    └─ Genera: target/gestion-empleados-1.0.0.jar

🔟  POST-PROCESSING
    └─ Archiva JUnit reports
    └─ Publica JaCoCo HTML
    └─ Logs de éxito/error
    └─ Cleanup

1️⃣1️⃣ REPORTES DISPONIBLES
    └─ Jenkins UI:
       • Test Report
       • JaCoCo Coverage Report
       • Console Output
```

---

## 🔐 Seguridad: Capas

```
CAPA 1: MÁQUINA LOCAL
   .env (ignorado por git, local only)
   JWT_SECRET: clave física guardada localmente
   
CAPA 2: TRANSPORTE
   docker-compose.yml interpola ${JWT_SECRET}
   Pasa al contenedor como variable env
   ✓ NO se guarda en Dockerfile
   ✓ NO se versionea en git

CAPA 3: JENKINS CREDENTIALS
   casc.yaml lee ${JWT_SECRET} del env
   Almacena en Jenkins Credentials (encriptado)
   ✓ Almacenamiento seguro en disco
   ✓ Acceso controlado por roles

CAPA 4: RUNTIME
   Jenkinsfile: environment { JWT_SECRET = credentials(...) }
   Jenkins desencripta para el build
   Pasa al contenedor Maven solo durante ejecución
   ✓ NO persiste después del build
   ✓ NO aparece en logs (Jenkins enmasca ***)

CAPA 5: TESTS
   String secret = System.getenv("JWT_SECRET")
   Tests acceden a través de variable env
   ✓ NO hardcoded en código
   ✓ NO en archivos de config
   ✓ Solo en tiempo de ejecución
```

---

## 📊 Reportes Generados y Ubicaciones

### Test Report (JUnit)
```
Ubicación en Disco:
  target/surefire-reports/TEST-*.xml

Acceso en Jenkins:
  Job → LastBuild → Test Report

Contenido:
  • Número de tests ejecutados
  • Tests pasados/fallidos
  • Trazas de error
  • Duración
```

### Coverage Report (JaCoCo)
```
Ubicación en Disco:
  target/site/jacoco/
  ├── index.html (Navegable)
  ├── jacoco.xml (Parseable)
  └── ...

Acceso en Jenkins:
  Job → LastBuild → JaCoCo Coverage Report

Contenido:
  • Líneas cubiertas %
  • Ramas cubiertas %
  • Por clase/método
  • Detalles de cobertura
```

### SonarQube Analysis (Opcional)
```
Ubicación Original:
  target/sonar/

Servidor Remoto:
  http://sonarqube:9000/projects

Contenido:
  • Code smells
  • Vulnerabilities
  • Code duplication
  • Technical debt
  • Integración con JaCoCo
```

---

## 🚀 Escalabilidad

### Para agregar más microservicios

```
Patrón: Igual que gestion-empleados

Paso 1: Crear Jenkinsfile en nuevo microservicio
  gestion-notificaciones/Jenkinsfile
  gestion-perfiles/Jenkinsfile

Paso 2: Actualizar casc.yaml con Job DSL
  jobs:
    - script: > pipelineJob('Notificaciones-Pipeline') { ... }
    - script: > pipelineJob('Perfiles-Pipeline') { ... }

Paso 3: Misma credencial JWT funciona para todos
  JWT_SECRET compartida entre microservicios

Resultado: Múltiples pipelines, misma infraestructura
```

---

## 🎯 Verificación de Implementación

✅ **Requiremento 1: Jenkinsfile Declarativo + Agente Docker**
```groovy
pipeline {
  agent { docker { image 'maven:3.9-eclipse-temurin-17' } }
```

✅ **Requerimiento 2: Manejo de Credenciales**
```groovy
JWT_SECRET = credentials('jwt-secret-key')
```

✅ **Requerimiento 3: Caché Maven**
```groovy
args '-v maven-cache:/root/.m2'
```

✅ **Requerimiento 4: Etapas de Calidad**
- Build ✓
- Test ✓
- SonarQube (Opcional) ✓

✅ **Requerimiento 5: JCasC con Credenciales**
```yaml
credentials:
  - simple: "jwt-secret-key"
```

✅ **Requerimiento 6: Job DSL Automatizado**
```yaml
jobs:
  - script: > pipelineJob('Empleados-Pipeline')
```

---

**Todas las especificaciones cumplidas ✅**
