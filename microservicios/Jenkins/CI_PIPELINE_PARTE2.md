# Pipeline CI con JWT, Maven y Gestión de Secretos (Reto 6 - Parte 2)

## 📋 Descripción General

Pipeline CI completamente automatizado para el microservicio `gestion-empleados` que incluye:
- ✅ Compilación con Maven
- ✅ Tests con cobertura JaCoCo
- ✅ Manejo seguro de credenciales JWT
- ✅ Análisis de código con SonarQube
- ✅ Reportes de calidad

## 🏗️ Estructura de Archivos

```
gestion-empleados/
├── Jenkinsfile                 # Pipeline declarativo (Parte 2)
├── pom.xml                     # Dependencias Maven incluyen JWT (JJWT)
├── src/
│   ├── main/java/              # Código fuente
│   └── test/java/              # Tests unitarios e integración
└── target/
    └── site/jacoco/            # Reportes de cobertura

Jenkins/
├── casc.yaml                   # Configuración actualizada (Parte 2)
│   ├── Credenciales (JWT, SonarQube)
│   └── Jobs DSL
└── ...
```

## 🔐 Gestión de Credenciales

### Credencial 1: JWT Secret Key

**ID en Jenkins**: `jwt-secret-key`  
**Tipo**: Secret text  
**Uso**: Firma y validación de tokens JWT en las pruebas

#### Cómo configurarla en Jenkins

**Opción 1: Mediante casc.yaml (Automática al levantar Docker)**

```yaml
credentials:
  system:
    domainCredentials:
      - credentials:
          - simple:
              scope: GLOBAL
              id: "jwt-secret-key"
              secret: "${JWT_SECRET}"
              description: "JWT Secret Key para firma de tokens"
```

La variable de entorno `${JWT_SECRET}` viene de tu `.env`:

```env
# .env (en la raíz del proyecto)
JWT_SECRET=tu-clave-super-secreta-con-minimo-32-caracteres-para-HS256
SONARQUBE_TOKEN=tu-token-sonarqube
```

**Opción 2: Manualmente en la UI**

1. Ir a `Jenkins` → `Manage Jenkins` → `Manage Credentials`
2. Click en `(global)` domain
3. Click en `Add Credentials`
4. Seleccionar `Secret text`
5. Pegar tu JWT_SECRET
6. ID: `jwt-secret-key`
7. Click `Create`

### Credencial 2: SonarQube Token

**ID en Jenkins**: `sonarqube-token`  
**Tipo**: Secret text  
**Uso**: Autenticación con servidor SonarQube

```env
SONARQUBE_TOKEN=squ_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## 🚀 Jenkinsfile Declarativo

### Estructura Principal

```groovy
pipeline {
  agent {
    docker {
      image 'maven:3.9-eclipse-temurin-17'
      args '-v /var/run/docker.sock:/var/run/docker.sock -v maven-cache:/root/.m2'
    }
  }

  environment {
    JWT_SECRET = credentials('jwt-secret-key')
    JWT_ISSUER = 'auth-service'
    JWT_AUDIENCE = 'microservices-clients'
  }

  stages {
    stage('Build') { ... }
    stage('Test') { ... }
    stage('Code Coverage') { ... }
    stage('Analyze with SonarQube') { ... }
    stage('Build Docker Image') { ... }
  }

  post { ... }
}
```

### Etapas Principales

#### 1. **Build**
```groovy
mvn clean compile -DskipTests
```
- Compilación limpia sin ejecutar tests
- Elimina `target/` anterior para asegurar idempotencia

#### 2. **Test**
```groovy
mvn test org.jacoco:jacoco-maven-plugin:report
```
- Ejecución de pruebas unitarias e integración
- Generación automática de reporte JaCoCo en XML
- El archivo JWT_SECRET se proporciona como variable de entorno
- Las pruebas acceden a él a través de `System.getenv("JWT_SECRET")`

#### 3. **Code Coverage**
```groovy
mvn org.jacoco:jacoco-maven-plugin:report
```
- Genera reporte JaCoCo en formato XML (necesario para SonarQube)
- Publica reportes HTML en Jenkins

#### 4. **Analyze with SonarQube** (Opcional)
```groovy
mvn sonar:sonar \
  -Dsonar.projectKey=com.microservicios:gestion-empleados \
  -Dsonar.coverage.jacoco.xmlReportPaths=target/site/jacoco/jacoco.xml
```
- Requiere parámetro `RUN_SONAR=true` al ejecutar
- Integra reportes de cobertura JaCoCo

#### 5. **Build Docker Image**
```groovy
mvn package -DskipTests
```
- Empaqueta la aplicación en JAR
- Listo para dockerizarlo

## 🔒 Cómo el Pipeline Maneja Credenciales

### En el Jenkinsfile

```groovy
environment {
  // Jenkins automáticamente mascara esta variable en los logs
  JWT_SECRET = credentials('jwt-secret-key')
}

stage('Test') {
  steps {
    sh '''
      echo "JWT_SECRET_CONFIGURED: $([ -n "$JWT_SECRET" ] && echo 'SI' || echo 'NO')"
      mvn test  // JWT_SECRET está disponible como variable de entorno
    '''
  }
}
```

### En las Pruebas Java

```java
@SpringBootTest
class JwtTokenTest {
    
    private JwtTokenProvider jwtTokenProvider;
    
    @BeforeEach
    void setup() {
        // La clave JWT viene de variables de entorno configuradas por Jenkins
        String jwtSecret = System.getenv("JWT_SECRET");
        assertNotNull(jwtSecret, "JWT_SECRET debe estar configurada");
        
        jwtTokenProvider = new JwtTokenProvider(jwtSecret, "auth-service");
    }
    
    @Test
    void testGenerarYValidarToken() {
        String token = jwtTokenProvider.generateToken("user@example.com");
        assertTrue(jwtTokenProvider.validateToken(token));
    }
}
```

### Características de Seguridad

✅ **Credenciales enmascaradas en logs**
```
[Pipeline] sh
+ echo JWT_SECRET_CONFIGURED: SI
+ mvn test
*** -> Jenkins oculta el valor real del secret
```

✅ **Credenciales no almacenadas en Jenkinsfile**
- El secret está en Jenkins Credentials, no en el código

✅ **Variables de entorno restringidas**
- Solo accesibles durante la ejecución del job
- No se persisten en disco después del build

## 📊 Reportes Generados

### JaCoCo Coverage Report

```
target/site/jacoco/
├── index.html           # Reporte visual
├── jacoco.xml           # XML para SonarQube
└── ...
```

Acceso en Jenkins:
```
https://jenkins:9090/job/Empleados-Pipeline/123/JaCoCo_Coverage_Report/
```

### SureeFire Test Report

```
target/surefire-reports/
├── TEST-*.xml           # Resultados XML de tests
└── ...
```

Acceso en Jenkins:
```
https://jenkins:9090/job/Empleados-Pipeline/123/testReport/
```

## ⚙️ Configuración en casc.yaml

### Credenciales

```yaml
jenkins:
  credentials:
    system:
      domainCredentials:
        - credentials:
            # JWT Secret (tipo: simple - Secret text)
            - simple:
                scope: GLOBAL
                id: "jwt-secret-key"
                secret: "${JWT_SECRET}"           # Viene de .env
                description: "JWT Secret Key..."
            
            # SonarQube Token
            - string:
                scope: GLOBAL
                id: "sonarqube-token"
                secret: "${SONARQUBE_TOKEN:-default-token}"
```

### Job DSL - Empleados-Pipeline

```yaml
jobs:
  - script: >
      pipelineJob('Empleados-Pipeline') {
        definition {
          cpsScm {
            scm {
              git {
                remote {
                  url('...')
                  credentials('github-credentials')
                }
              }
            }
            scriptPath('gestion-empleados/Jenkinsfile')
          }
        }
      }
```

## 🔄 Flujo Completo de Ejecución

```
1. Jenkins lee credenciales desde casc.yaml
   ↓
2. Job DSL crea el pipelineJob "Empleados-Pipeline"
   ↓
3. Build disparado (manual o por trigger SCM)
   ↓
4. Docker container con Maven es levantado
   ↓
5. Jenkinsfile ejecuta 5 etapas:
   - Build:              mvn clean compile
   - Test:               mvn test + JaCoCo
   - Code Coverage:      Generar reportes XML
   - SonarQube:          (Opcional) Análisis de código
   - Docker Image:       mvn package
   ↓
6. Post-processing:
   - Archiva reportes JUnit
   - Publica reporte JaCoCo HTML
   - Envía notificaciones
   ↓
7. Logs limpios, credenciales enmascaradas
```

## 🛠️ Cómo Ejecutar el Pipeline

### Opción 1: Interfaz Web

1. Acceder a `http://localhost:9090`
2. Click en `Empleados-Pipeline`
3. Click en `Build with Parameters`
4. Marcar `RUN_SONAR` si deseas análisis SonarQube
5. Click `Build`

### Opción 2: CLI con curl

```bash
# Build simple
curl -X POST http://localhost:9090/job/Empleados-Pipeline/build

# Build con parámetro
curl -X POST "http://localhost:9090/job/Empleados-Pipeline/buildWithParameters?RUN_SONAR=true"
```

### Opción 3: Trigger automático (SCM Poll)

El casc.yaml puede configurarse para polling automático:

```yaml
triggers {
  pollSCM('H/15 * * * *')  # Cada 15 minutos
}
```

## 🐳 Docker Cache de Maven

El Jenkinsfile configura un volumen Docker para caché Maven:

```groovy
agent {
  docker {
    args '-v maven-cache:/root/.m2'
  }
}
```

**Ventajas:**
- Descargas de dependencias reutilizadas entre builds
- Compilación 3-5x más rápida en builds subsecuentes
- Idempotencia garantizada

## 🔍 Troubleshooting

### Error: "Credencial no encontrada"

```
ERROR: Credencial ID [jwt-secret-key] not found
```

**Solución:**
1. Reiniciar Jenkins: `docker restart jenkins-server`
2. Verificar `.env` tiene `JWT_SECRET` definido
3. Revisar logs: `docker logs jenkins-server | grep -i credentials`

### Test fallan sin mensaje claro

```bash
# Ver si JWT_SECRET está disponible
docker exec jenkins-server printenv | grep JWT
```

### SonarQube no recibe reportes JaCoCo

```bash
# Verificar que archivo existe
docker logs jenkins-server | grep "jacoco.xml"

# Manual:
mvn org.jacoco:jacoco-maven-plugin:report
```

## 📝 Próximos Pasos (Reto 6 - Parte 3)

- [ ] Integración con SonarQube (servidor separado)
- [ ] Notificaciones en Slack/Email
- [ ] Deployment automático a staging
- [ ] Pipelines para otros microservicios
- [ ] Blue/Green deployment

## 📚 Referencias

- [Jenkinsfile Declarativo](https://www.jenkins.io/doc/book/pipeline/declarative/)
- [Manejo de Credenciales en Jenkins](https://www.jenkins.io/doc/book/using/using-credentials/)
- [JJWT - JWT para Java](https://github.com/jwtk/jjwt)
- [Maven JaCoCo Plugin](https://www.eclemma.org/jacoco/trunk/doc/maven.html)
- [JCasC Documentation](https://plugins.jenkins.io/configuration-as-code/)
- [Jenkins Job DSL](https://plugins.jenkins.io/job-dsl/)
