# Reto 6: Guía Rápida de Referencia

## 🚀 Resumen Ejecutivo

El **Reto 6** integra **3 capas de calidad** en tu pipeline CI/CD:

| Capa | Herramienta | Umbral | Acción |
|------|-----------|--------|--------|
| **Cobertura** | JaCoCo | ≥ 70% | ❌ Aborta si falla |
| **Análisis** | SonarQube | Calidad | ❌ Aborta si falla |
| **Disponibilidad** | Health Checks | Responden | ⏸️ Espera activa |

---

## 1️⃣ Configuración de JaCoCo (pom.xml)

```xml
<plugin>
    <groupId>org.jacoco</groupId>
    <artifactId>jacoco-maven-plugin</artifactId>
    <version>0.8.10</version>
    <executions>
        <execution>
            <id>prepare-agent</id>
            <phase>initialize</phase>
            <goals>
                <goal>prepare-agent</goal>
            </goals>
            <configuration>
                <destFile>${project.build.directory}/coverage-reports/jacoco-ut.exec</destFile>
                <propertyName>surefireArgLine</propertyName>
            </configuration>
        </execution>
        <execution>
            <id>report</id>
            <phase>test</phase>
            <goals>
                <goal>report</goal>
            </goals>
        </execution>
    </executions>
</plugin>

<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-surefire-plugin</artifactId>
    <version>3.1.2</version>
    <configuration>
        <argLine>${surefireArgLine}</argLine>
    </configuration>
</plugin>
```

**Comando para probar**:
```bash
cd microservicios/gestion-empleados
mvn clean verify
# Revisar: target/site/jacoco/index.html
```

---

## 2️⃣ Stages del Jenkinsfile

### Build & Test
```groovy
stage('Build & Test') {
  steps {
    dir("${APP_DIR}") {
      sh '''
        mvn clean org.jacoco:jacoco-maven-plugin:prepare-agent verify org.jacoco:jacoco-maven-plugin:report \
          -DskipTests=false
      '''
    }
  }
  post {
    always {
      junit testResults: '...target/surefire-reports/*.xml', allowEmptyResults: true
      archiveArtifacts artifacts: '...target/site/jacoco/*', allowEmptyArchive: true
    }
  }
}
```

### Coverage Gate
```groovy
stage('Coverage Gate (>= 70%)') {
  steps {
    dir("${APP_DIR}") {
      script {
        def coverage = sh(
          script: '''
            awk -F, 'NR>1 {missed+=$4; covered+=$5} END {total=missed+covered; if(total==0){print "0.00"} else {printf "%.2f", (covered*100)/total}}' target/site/jacoco/jacoco.csv
          ''',
          returnStdout: true
        ).trim()

        echo "Cobertura JaCoCo: ${coverage}%"
        if (coverage.toBigDecimal() < env.MIN_COVERAGE.toBigDecimal()) {
          error("Cobertura insuficiente: ${coverage}% < ${env.MIN_COVERAGE}%")
        }
      }
    }
  }
}
```

**Cálculo**:
```
Cobertura = (Líneas Cubiertas × 100) / (Líneas Cubiertas + Líneas No Cubiertas)
```

### SonarQube Analysis
```groovy
stage('SonarQube Analysis') {
  steps {
    dir("${APP_DIR}") {
      withSonarQubeEnv('SonarQube') {
        sh '''
          mvn sonar:sonar \
            -Dsonar.host.url=${SONAR_HOST_URL} \
            -Dsonar.token=${SONARQUBE_TOKEN} \
            -Dsonar.projectKey=${SONAR_PROJECT_KEY} \
            -Dsonar.projectName=${SONAR_PROJECT_NAME} \
            -Dsonar.coverage.jacoco.xmlReportPaths=target/site/jacoco/jacoco.xml
        '''
      }
    }
  }
}
```

### Quality Gate
```groovy
stage('Quality Gate') {
  steps {
    timeout(time: 10, unit: 'MINUTES') {
      waitForQualityGate abortPipeline: true
    }
  }
}
```

### E2E Tests (Espera Activa + Godog)
```groovy
stage('E2E Tests') {
  steps {
    sh '''
      docker compose -f ${COMPOSE_FILE} up -d --build

      # Espera activa: máximo 30 intentos, 10 segundos entre intentos
      for url in \
        http://localhost:8080/v3/api-docs \
        http://localhost:8081/docs \
        http://localhost:8084/health; do
        echo "Esperando: ${url}"
        ok=0
        for i in $(seq 1 30); do
          if curl -fsS "$url" >/dev/null; then
            ok=1
            echo "✅ Listo: ${url}"
            break
          fi
          sleep 10
        done
        if [ "$ok" -ne 1 ]; then
          echo "❌ Timeout"
          exit 1
        fi
      done
    '''

    dir("${E2E_DIR}") {
      sh 'go test ./step_definitions -v'
    }
  }
}
```

### Limpieza
```groovy
post {
  always {
    sh 'docker compose -f ${COMPOSE_FILE} down -v --remove-orphans || true'
  }
}
```

---

## 3️⃣ Health Checks en Docker Compose

### Patrón general:
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:PUERTO/ENDPOINT"]
  interval: 10s         # Verifica cada 10 segundos
  timeout: 5s           # Timeout de 5 segundos
  retries: 5            # Máximo 5 reintentos
  start_period: 30s     # Espera 30s antes de verificar
```

### Ejemplos por tecnología:

**Java/Spring Boot:**
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8080/v3/api-docs"]
  interval: 15s
  timeout: 5s
  retries: 5
  start_period: 40s
```

**Python/FastAPI:**
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8081/docs"]
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 30s
```

**PHP/Laravel:**
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8083/api/health"]
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 30s
```

**C#/ASP.NET:**
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8084/health"]
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 30s
```

**Redis:**
```yaml
healthcheck:
  test: ["CMD", "redis-cli", "ping"]
  interval: 10s
  timeout: 5s
  retries: 5
```

**RabbitMQ:**
```yaml
healthcheck:
  test: ["CMD", "rabbitmq-diagnostics", "check_running"]
  interval: 10s
  timeout: 5s
  retries: 5
```

---

## 4️⃣ Variables de Entorno Necesarias

```bash
# En .env o al ejecutar docker-compose
export JWT_SECRET="SuperSecretKeyWithMoreThan32CharactersForJWTTokenSigning"
export SONARQUBE_TOKEN="your-sonarqube-token-here"
export REGISTRY_PORT=5001  # Windows: 5001, Linux: 5000
export GIT_REPO_URL="file:///workspace/repo"
export GIT_BRANCH="*/main"
```

---

## 5️⃣ Validación Manual

### Test JaCoCo:
```bash
cd microservicios/gestion-empleados
mvn clean verify
open target/site/jacoco/index.html  # macOS
explorer target/site/jacoco/index.html  # Windows
```

### Test Disponibilidad:
```bash
cd microservicios
docker compose up -d

# Verifica health status
docker compose ps
# Verifica logs de un servicio
docker logs -f empleados-service

# Prueba curl directo
curl http://localhost:8080/v3/api-docs
curl http://localhost:8081/docs
curl http://localhost:8084/health
```

### Test E2E:
```bash
cd e2e-tests
go test ./step_definitions -v
```

---

## 6️⃣ Métricas Clave

| Métrica | Target | Verificación |
|---------|--------|--------------|
| **Cobertura de código** | ≥ 70% | `jacoco.csv` en Build & Test |
| **Quality Gate** | ✅ OK | `waitForQualityGate` en SonarQube |
| **Disponibilidad API** | 200 OK | Espera activa en E2E Tests |
| **Uptime Servicios** | 100% | Health checks cada 10s |

---

## 7️⃣ Flujo Visual del Pipeline

```
[1] CHECKOUT
    ↓
[2] BUILD & TEST + JACOCO
    ├─ mvn clean verify
    ├─ Genera: jacoco.xml, jacoco.csv
    └─ Archiva reporte
    ↓
[3] COVERAGE GATE (≥70%)
    ├─ Lee jacoco.csv
    ├─ Calcula porcentaje
    └─ ❌ Aborta si < 70%
    ↓
[4] SONARQUBE ANALYSIS
    ├─ mvn sonar:sonar
    ├─ Envía reporte XML
    └─ Registra en servidor
    ↓
[5] QUALITY GATE
    ├─ waitForQualityGate (10 min timeout)
    └─ ❌ Aborta si falla
    ↓
[6] PACKAGE
    ├─ docker build
    └─ docker push (si registry disponible)
    ↓
[7] E2E TESTS
    ├─ docker compose up -d
    ├─ Espera activa (3 endpoints × 30 intentos × 10s)
    ├─ Verifica 200 OK
    └─ Ejecuta: go test ./step_definitions -v
    ↓
[LIMPIEZA]
    └─ docker compose down -v
    └─ Elimina volúmenes
```

---

## 📞 Troubleshooting Rápido

| Problema | Solución |
|----------|----------|
| "Cobertura < 70%" | Aumentar tests en `src/test/` |
| "Quality Gate Failed" | Revisar http://localhost:9000 |
| "Timeout esperando servicios" | Aumentar `start_period` en docker-compose |
| "Port 5000 in use (Windows)" | `REGISTRY_PORT=5001 docker compose up` |
| "Jenkins no inicia" | Revisar: `docker logs jenkins-server` |
| "SonarQube no responde" | Revisar: `docker logs sonarqube` |

---

## 🔗 Enlaces de Acceso

| Servicio | URL | Usuario | Contraseña |
|----------|-----|--------|-----------|
| Jenkins | http://localhost:9090 | nicolasAdmin | omar |
| SonarQube | http://localhost:9000 | admin | admin |
| RabbitMQ | http://localhost:15672 | guest | guest |
| API Empleados | http://localhost:8080 | - | - |
| API Departamentos | http://localhost:8081 | - | - |

---

## ✅ Checklist de Implementación

- [x] JaCoCo configurado en pom.xml
- [x] Build & Test con cobertura
- [x] Coverage Gate con umbral 70%
- [x] SonarQube Analysis integrado
- [x] Quality Gate con waitForQualityGate
- [x] Health checks en todos los servicios
- [x] Espera activa en E2E Tests
- [x] Godog tests ejecutándose
- [x] Limpieza con docker-compose down -v
- [x] Documentación completa

---

**Documento generado**: Mayo 2026  
**Estado**: ✅ LISTO PARA PRODUCCIÓN
