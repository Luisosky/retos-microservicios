# Jenkins LTS con JCasC y Docker-in-Docker
FROM jenkins/jenkins:lts-jdk17

# Cambiar a usuario root para instalar dependencias
USER root

# Actualizar packages e instalar Docker CLI
RUN apt-get update && apt-get install -y \
  docker.io \
  git \
  curl \
  wget \
  maven \
  golang-go \
    && rm -rf /var/lib/apt/lists/*

# Agregar usuario jenkins al grupo docker para acceso al socket
RUN groupadd -f docker && usermod -aG docker jenkins

# Cambiar de vuelta a usuario jenkins
USER jenkins

# Instalar plugins necesarios
# workflow-aggregator: Soporte para declarative y scripted pipelines
# docker-pipeline: Integración con Docker
# git: Integración con repositorios Git
# configuration-as-code: JCasC para configuración automática
# sonar: Integración con SonarQube
# job-dsl: DSL para crear jobs
# pipeline-stage-view: Vista de etapas en pipelines
# Instalar plugins necesarios
# Instalar plugins necesarios


# Copiar archivo de configuración JCasC# Instalar plugins necesarios
RUN jenkins-plugin-cli --plugins \
    workflow-aggregator \
    docker-workflow \
    git \
    configuration-as-code \
    sonar \
    job-dsl \
    pipeline-stage-view \
    role-strategy

COPY casc.yaml /var/jenkins_home/casc.yaml

# Establecer variables de entorno para JCasC
ENV CASC_JENKINS_CONFIG=/var/jenkins_home/casc.yaml

# Exponer puertos
# 8080: interfaz web de Jenkins
# 50000: puerto para agentes Jenkins
EXPOSE 8080 50000
