# Guía Rápida de Ejecución - Reto 6 Parte 2

## 🎯 Objetivo
Pipeline CI completamente funcional para `gestion-empleados` que maneja JWT de forma segura, compila con Maven, ejecuta tests con cobertura JaCoCo y puede integrar SonarQube.

---

## 📋 Quick Start (5 minutos)

### 1. Preparar el archivo .env

```bash
# En la raíz del proyecto, copiar el ejemplo
cp Jenkins/.env.example .env

# Editar .env y completar valores seguros
# JWT_SECRET=tu-clave-secreta-super-segura-32-caracteres-minimo
# SONARQUBE_TOKEN=squ_xxxxxxxx
```

### 2. Levantar Jenkins

```bash
# Build e inicio (primera vez ~3-5 minutos)
docker-compose up --build -d jenkins

# Esperar a que esté listo
sleep 60

# Acceder a Jenkins
start http://localhost:9090  # Windows
open http://localhost:9090   # Mac
xdg-open http://localhost:9090  # Linux
```

### 3. Verificar que todo está configurado

**Windows PowerShell:**
```powershell
.\Jenkins\verify_pipeline.ps1
```

**Linux/Mac Bash:**
```bash
bash Jenkins/verify_pipeline.sh
```

### 4. Ejecutar el Pipeline

**Opción A: UI Web**
1. Ir a http://localhost:9090
2. Click en **Empleados-Pipeline**
3. Click en **Build Now**
4. Ver progreso en tiempo real

**Opción B: CLI**
```bash
# Build simple
curl -X POST http://localhost:9090/job/Empleados-Pipeline/build

# Build con análisis SonarQube
curl -X POST "http://localhost:9090/job/Empleados-Pipeline/buildWithParameters?RUN_SONAR=true"
```

### 5. Ver Reportes

```
http://localhost:9090/job/Empleados-Pipeline/<build-number>/JaCoCo_Coverage_Report/
http://localhost:9090/job/Empleados-Pipeline/<build-number>/testReport/
```

---

## 🔐 Gestión de Credenciales - Explicado

### ¿Cómo funciona la seguridad?

```
1. Usuario define JWT_SECRET en .env (máquina local)
   ↓
2. docker-compose.yml pasa JWT_SECRET al contenedor Jenkins
   ↓
3. casc.yaml lee ${JWT_SECRET} y crea credencial "jwt-secret-key"
   ↓
4. Jenkinsfile usa: environment { JWT_SECRET = credentials('jwt-secret-key') }
   ↓
5. Maven tests acceden a JWT_SECRET como variable de entorno
   ↓
6. Jenkins ENMASCARA el valor en logs (muestra: *****)
```

### Ejemplo de test que usa JWT_SECRET

```java
@SpringBootTest
class JwtTokenProviderTest {
    
    @Test
    void testTokenGeneration() {
        // JWT_SECRET viene como variable de entorno desde Jenkins
        String secret = System.getenv("JWT_SECRET");
        assertNotNull(secret);
        
        JwtTokenProvider provider = new JwtTokenProvider(secret);
        String token = provider.generateToken("user@example.com");
        assertTrue(provider.validateToken(token));
    }
}
```

### Verificar que la credencial está configurada

```bash
# Ver logs de casc.yaml
docker logs jenkins-server 2>&1 | grep -i "casc\|credential"

# Ver credenciales almacenadas (sin mostrar valores)
docker exec jenkins-server curl -s http://localhost:8080/credentials/api/json
```

---

## 📊 Etapas del Pipeline - Desglose

### 1. **Build** (Compilación)
```groovy
stage('Build') {
  mvn clean compile -DskipTests
}
```
- Elimina builds anteriores
- Compila código Java
- ~20-30 segundos (primera vez), ~5-10 (cache)

### 2. **Test** (Pruebas)
```groovy
stage('Test') {
  mvn test org.jacoco:jacoco-maven-plugin:report
}
```
- Ejecuta todas las pruebas en `src/test/java/`
- JWT_SECRET disponible como variable de entorno
- Genera reporte JaCoCo XML
- ~30-60 segundos

### 3. **Code Coverage** (Cobertura)
```groovy
stage('Code Coverage') {
  mvn org.jacoco:jacoco-maven-plugin:report
}
```
- Genera HTML de cobertura JaCoCo
- Publica en Jenkins UI
- ~10 segundos

### 4. **Analyze with SonarQube** (Opcional)
```groovy
stage('Analyze with SonarQube') {
  when { expression { params.RUN_SONAR == true } }
  mvn sonar:sonar ...
}
```
- Solo si marques checkbox en "Build with Parameters"
- Envía análisis a servidor SonarQube
- Requiere SONARQUBE_TOKEN en `.env`
- ~1-2 minutos

### 5. **Build Docker Image**
```groovy
stage('Build Docker Image') {
  mvn package -DskipTests
}
```
- Empaqueta en JAR ejecutable
- ~20 segundos

---

## 🐳 Volúmenes y Caché

### Maven Cache (maven-cache)
```
Primera ejecución:  ~3-5 minutos (descarga dependencias)
Subsecuentes:       ~30-60 segundos (usa cache)
```

Directorio cacheado:
```
/root/.m2/repository/
  ├── org/springframework/...
  ├── io/jsonwebtoken/...
  └── ... (todas las dependencias)
```

### Verificar que caché existe

```bash
docker volume ls | grep maven

# Ver contenido
docker run -v maven-cache:/root/.m2 -it ubuntu ls -la /root/.m2/repository/ | head
```

---

## 🔍 Troubleshooting

### ❌ "Credencial no encontrada"
```
ERROR: Credencial ID [jwt-secret-key] not found
```

**Solución:**
```bash
# Reiniciar Jenkins
docker restart jenkins-server

# Esperar 30 segundos
sleep 30

# Verificar logs
docker logs jenkins-server | tail -20
```

### ❌ Test fallan sin JWT
```
Error: JWT_SECRET is null
```

**Solución:**
```bash
# Verificar .env existe y tiene valor
cat .env | grep JWT_SECRET

# Verificar que Jenkins tiene la variable
docker exec jenkins-server printenv | grep JWT_SECRET

# Si está vacío, pasar explícitamente:
docker-compose down jenkins
# Editar .env con valor válido
docker-compose up -d --build jenkins
```

### ❌ Maven tarda mucho la primera vez
```
[INFO] Downloading: org/springframework/boot/...
```

Normal. Primera ejecución descarga ~500MB de dependencias. Subsecuentes son rápidas.

```bash
# Ver progreso de descargas
docker logs jenkins-server -f
```

### ❌ SonarQube análisis falla
```
SONAR_HOST_URL no está configurado
```

**Solución:** SonarQube es opcional. Si no lo tienes:
- No marques checkbox "RUN_SONAR"
- O instala servidor SonarQube y configura URL

---

## 📈 Integración con SonarQube (Avanzado)

Si tienes servidor SonarQube corriendo:

```yaml
# docker-compose.yml - Agregar servicio SonarQube
sonarqube:
  image: sonarqube:lts
  ports:
    - "9000:9000"
  environment:
    SONAR_JDBC_URL: jdbc:postgresql://db:5432/sonarqube
    SONAR_JDBC_USERNAME: sonar
    SONAR_JDBC_PASSWORD: sonar
```

Luego en Jenkins:
```bash
# Ir a Manage Jenkins → Configure System → SonarQube servers
# Agregar:
#   Name: SonarQube
#   URL: http://sonarqube:9000
#   Token: (tu token de SonarQube)
```

---

## 📝 Monitoreo del Pipeline

### Ver logs en tiempo real
```bash
docker logs jenkins-server -f

# O solo del job en ejecución
docker exec jenkins-server tail -f /var/jenkins_home/jobs/Empleados-Pipeline/builds/1/log
```

### Estadísticas del build

```bash
# Duración del último build
docker exec jenkins-server curl -s http://localhost:8080/job/Empleados-Pipeline/lastBuild/api/json | jq '.duration'

# Número de tests
docker exec jenkins-server curl -s http://localhost:8080/job/Empleados-Pipeline/lastBuild/api/json | jq '.result'

# Cobertura JaCoCo
# (Disponible en UI: Jenkins → Job → Build → JaCoCo Coverage Report)
```

---

## 🎓 Conceptos Clave

### Pipeline as Code (Jenkinsfile)
- Versionar el pipeline con el código
- Cambios en git = cambios en pipeline
- Reproducible y auditable

### Configuration as Code (casc.yaml)
- Jenkins pre-configurada sin UI manual
- Ambiente reproducible
- Infrastructure as Code

### Declarative Pipeline
```groovy
pipeline { ... }  // Estructura simple y clara
// vs
node { ... }      // Scripted (más flexible pero complejo)
```

### Docker Container per Build
- Aislamiento total
- Reproducibilidad garantizada
- No contamina el host

### JWT Secret Management
```
Nunca en código ❌
Sí en Jenkins Credentials ✅
Variables de entorno en runtime ✅
Enmascaradas en logs ✅
```

---

## ✅ Checklist Final

- [ ] `.env` creado con JWT_SECRET válida
- [ ] `docker-compose up --build -d jenkins` ejecutado
- [ ] Jenkins accesible en http://localhost:9090
- [ ] `verify_pipeline.sh` o `.ps1` ejecutado sin errores
- [ ] "Empleados-Pipeline" visible en Jenkins UI
- [ ] Build ejecutado exitosamente (sin parámetros)
- [ ] Reportes JaCoCo visibles
- [ ] Test Report muestra tests ejecutados

---

## 🚀 Próximas Fases

**Reto 6 - Parte 3:**
- [ ] SonarQube server integrado
- [ ] Notificaciones Slack/Email
- [ ] Deployment automático
- [ ] Pipelines multi-servicio (departamentos, perfiles, etc.)

---

## 📞 Soporte

Para errores específicos, ver:
- `Jenkins/CI_PIPELINE_PARTE2.md` - Documentación completa
- `gestion-empleados/Jenkinsfile` - Código del pipeline
- `Jenkins/casc.yaml` - Configuración JCasC
- `docker-compose.yml` - Infraestructura

---

**¡A continuación: Parte 3 - SonarQube, Notificaciones y Deployment! 🚀**
