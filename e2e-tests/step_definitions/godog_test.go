package step_definitions

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"strconv"
	"testing"
	"time"

	"github.com/cucumber/godog"
)

// Estructura para guardar el estado y reutilizar el cliente HTTP
type apiTestState struct {
	token        string
	responseCode int
	client       *http.Client
}

// ==========================================
// PASOS DE LA PRUEBA DE HUMO (Reto 5 - Punto 1)
// ==========================================
func (a *apiTestState) queElEntornoDePruebasEstáInicializado() error {
	return nil
}

func (a *apiTestState) ejecutoEsteEscenarioDeHumo() error {
	return nil
}

func (a *apiTestState) laEjecuciónDeberíaSerExitosa() error {
	return nil
}

// ==========================================
// CONFIGURACIÓN Y MAPEADO DE GODOG
// ==========================================
func InitializeScenario(ctx *godog.ScenarioContext) {
	estado := &apiTestState{}

	// Humo
	ctx.Step(`^que el entorno de pruebas está inicializado$`, estado.queElEntornoDePruebasEstáInicializado)
	ctx.Step(`^ejecuto este escenario de humo$`, estado.ejecutoEsteEscenarioDeHumo)
	ctx.Step(`^la ejecución debería ser exitosa$`, estado.laEjecuciónDeberíaSerExitosa)

	// Seguridad
	ctx.Step(`^que el sistema está desplegado y operativo$`, estado.queElSistemaEstDesplegadoYOperativo)
	ctx.Step(`^que el servicio de empleados está disponible$`, estado.queElServicioDeEmpleadosEstDisponible)
	ctx.Step(`^que estoy autenticado con el rol "([^"]*)"$`, estado.queEstoyAutenticadoConElRol)
	ctx.Step(`^consulto la lista de empleados sin token de autenticación$`, estado.consultoLaListaDeEmpleadosSinTokenDeAutenticacin)
	ctx.Step(`^consulto la lista de empleados enviando el token "([^"]*)"$`, estado.consultoLaListaDeEmpleadosEnviandoElToken)
	ctx.Step(`^consulto la lista de empleados$`, estado.consultoLaListaDeEmpleados)
	ctx.Step(`^cuando intento crear un nuevo empleado en el sistema$`, estado.cuandoIntentoCrearUnNuevoEmpleadoEnElSistema)
	ctx.Step(`^la respuesta debe tener código (\d+)$`, estado.laRespuestaDebeTenerCdigo)

	// Onboarding
	ctx.Step(`^registro un nuevo empleado con datos válidos$`, estado.registroUnNuevoEmpleadoConDatosVlidos)
	ctx.Step(`^espero a que sus credenciales sean generadas automáticamente mediante polling$`, estado.esperoAQueSusCredencialesSeanGeneradasAutomticamenteMediantePolling)
	ctx.Step(`^el nuevo empleado debería poder iniciar sesión en el sistema exitosamente$`, estado.elNuevoEmpleadoDeberaPoderIniciarSesinEnElSistemaExitosamente)
	ctx.Step(`^intento registrar un empleado sin el campo de correo electrónico$`, estado.intentoRegistrarUnEmpleadoSinElCampoDeCorreoElectrnico)

	// Offboarding
	ctx.Step(`^que preparo un empleado temporal para su posterior desvinculación$`, estado.quePreparoUnEmpleadoTemporalParaSuPosteriorDesvinculacin)
	ctx.Step(`^ejecuto la desvinculación de este empleado en el sistema$`, estado.ejecutoLaDesvinculacinDeEsteEmpleadoEnElSistema)
	ctx.Step(`^el sistema debe rechazar sus intentos de inicio de sesión$`, estado.elSistemaDebeRechazarSusIntentosDeInicioDeSesin)
	ctx.Step(`^el empleado desvinculado intenta solicitar una recuperación de contraseña$`, estado.elEmpleadoDesvinculadoIntentaSolicitarUnaRecuperacinDeContrasea)
	ctx.Step(`^la API de autenticación debe bloquear la solicitud$`, estado.laAPIDeAutenticacinDebeBloquearLaSolicitud)
}

// ESTA ES LA FUNCIÓN QUE BUSCA GO TEST PARA INICIAR
func TestFeatures(t *testing.T) {
	suite := godog.TestSuite{
		ScenarioInitializer: InitializeScenario,
		Options: &godog.Options{
			Format:   "pretty",
			Paths:    []string{"../features"}, // Busca los .feature un nivel arriba
			TestingT: t,
		},
	}

	if suite.Run() != 0 {
		t.Fatal("Falló la ejecución de las pruebas BDD")
	}
}

// ==========================================
// PASOS DE SEGURIDAD (Reto 5 - Punto 2) - IMPLEMENTACIÓN REAL
// ==========================================

func (a *apiTestState) queElSistemaEstDesplegadoYOperativo() error {
	// Inicializamos un cliente HTTP con un timeout para que no se quede colgado
	a.client = &http.Client{Timeout: 30 * time.Second}

	// Hacemos ping al health check de autenticación (puerto 8084)
	resp, err := a.client.Get("http://localhost:8084/health")
	if err != nil {
		return fmt.Errorf("el servicio de autenticación no está respondiendo: %v", err)
	}
	defer resp.Body.Close()
	return nil
}

func (a *apiTestState) queElServicioDeEmpleadosEstDisponible() error {
	// Podemos hacer una petición rápida para verificar que el puerto 8080 responde
	// (Aunque responda 401, significa que el servicio está vivo)
	resp, err := a.client.Get("http://localhost:8080/empleado")
	if err != nil {
		return fmt.Errorf("el servicio de empleados no está respondiendo: %v", err)
	}
	defer resp.Body.Close()
	return nil
}

func (a *apiTestState) queEstoyAutenticadoConElRol(rol string) error {

	credentials := map[string]string{
		"email":    "usuario_" + rol + "@empresa.com", // Ej: usuario_ADMIN@empresa.com
		"password": "Password123!",
	}

	jsonData, _ := json.Marshal(credentials)

	resp, err := a.client.Post("http://localhost:8084/auth/login", "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return fmt.Errorf("error al hacer login: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("falló el login para el rol %s, código: %d", rol, resp.StatusCode)
	}

	// Extraer el token de la respuesta JSON
	var result map[string]interface{}
	json.NewDecoder(resp.Body).Decode(&result)

	// Ajusta la llave "token" según cómo devuelva el JWT tu API en C#
	if t, ok := result["token"].(string); ok {
		a.token = t
		return nil
	}
	return fmt.Errorf("no se encontró el JWT en la respuesta de login")
}

func (a *apiTestState) consultoLaListaDeEmpleadosSinTokenDeAutenticacin() error {
	req, _ := http.NewRequest("GET", "http://localhost:8080/empleado", nil)
	// No agregamos header de Authorization

	resp, err := a.client.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	a.responseCode = resp.StatusCode
	return nil
}

func (a *apiTestState) consultoLaListaDeEmpleadosEnviandoElToken(tokenFalso string) error {
	req, _ := http.NewRequest("GET", "http://localhost:8080/empleado", nil)
	req.Header.Add("Authorization", "Bearer "+tokenFalso)

	resp, err := a.client.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	a.responseCode = resp.StatusCode
	return nil
}

func (a *apiTestState) consultoLaListaDeEmpleados() error {
	req, _ := http.NewRequest("GET", "http://localhost:8080/empleado", nil)
	req.Header.Add("Authorization", "Bearer "+a.token)

	resp, err := a.client.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	a.responseCode = resp.StatusCode
	return nil
}

func (a *apiTestState) cuandoIntentoCrearUnNuevoEmpleadoEnElSistema() error {
	// JSON ajustado al modelo exacto de Spring Boot
	nuevoEmpleado := map[string]interface{}{
		"numeroEmpleado": "EMP999",
		"email":          "testbdd999@empresa.com",
		"nombre":         "Automatización",
		"apellido":       "Prueba",
		"cargo":          "Ingeniero de Pruebas",
		"area":           "QA",
		"departamentoId": "DEP001",
		"fechaIngreso":   "2026-04-15",
		"estado":         "ACTIVO",
	}
	jsonData, _ := json.Marshal(nuevoEmpleado)

	req, _ := http.NewRequest("POST", "http://localhost:8080/empleado", bytes.NewBuffer(jsonData))
	req.Header.Add("Content-Type", "application/json")
	req.Header.Add("Authorization", "Bearer "+a.token)

	resp, err := a.client.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	a.responseCode = resp.StatusCode
	return nil
}

func (a *apiTestState) laRespuestaDebeTenerCdigo(codigoEsperado int) error {
	if a.responseCode != codigoEsperado {
		return fmt.Errorf("se esperaba HTTP %d, pero se obtuvo HTTP %d", codigoEsperado, a.responseCode)
	}
	return nil
}

// ==========================================
// PASOS DE ONBOARDING (Reto 5 - Punto 3)
// ==========================================

// Variable temporal para guardar el correo del usuario recién creado y poder loguearlo
var nuevoCorreo string

func (a *apiTestState) registroUnNuevoEmpleadoConDatosVlidos() error {
	// Generamos un ID y correo dinámicos para que la prueba no falle por "email duplicado"
	idUnico := strconv.FormatInt(time.Now().Unix(), 10)
	nuevoCorreo = "nuevo" + idUnico + "@empresa.com"

	// Usamos exactamente el modelo de Spring Boot que compartiste
	nuevoEmpleado := map[string]interface{}{
		"numeroEmpleado": "EMP" + idUnico,
		"email":          nuevoCorreo,
		"nombre":         "Usuario",
		"apellido":       "Onboarding",
		"cargo":          "Desarrollador",
		"area":           "TI",
		"departamentoId": "DEP001",
		"fechaIngreso":   time.Now().Format("2006-01-02"), // Formato yyyy-MM-dd
		"estado":         "ACTIVO",
	}
	jsonData, _ := json.Marshal(nuevoEmpleado)

	req, _ := http.NewRequest("POST", "http://localhost:8080/empleado", bytes.NewBuffer(jsonData))
	req.Header.Add("Content-Type", "application/json")
	req.Header.Add("Authorization", "Bearer "+a.token) // Usamos el token del ADMIN

	resp, err := a.client.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	a.responseCode = resp.StatusCode
	return nil
}

func (a *apiTestState) esperoAQueSusCredencialesSeanGeneradasAutomticamenteMediantePolling() error {
	// ⚠️ JUSTIFICACIÓN DEL POLLING (Requisito de rúbrica):
	// En lugar de hacer un time.Sleep(10 * time.Second) bloqueante y ciego,
	// intentamos hacer login. Si falla, esperamos medio segundo y reintentamos,
	// hasta un máximo de 10 intentos (5 segundos total). Esto hace la prueba rápida y resiliente.

	maxIntentos := 10
	tiempoEspera := 500 * time.Millisecond

	// Asume la contraseña por defecto que tu microservicio de C# asigna al crear usuarios
	// CAMBIA ESTO por la contraseña real por defecto de tu sistema
	passwordPorDefecto := "Password123!"

	credentials := map[string]string{
		"email":    nuevoCorreo,
		"password": passwordPorDefecto,
	}
	jsonData, _ := json.Marshal(credentials)

	for i := 1; i <= maxIntentos; i++ {
		resp, err := a.client.Post("http://localhost:8084/auth/login", "application/json", bytes.NewBuffer(jsonData))

		if err == nil && resp.StatusCode == http.StatusOK {
			fmt.Printf("Credenciales detectadas exitosamente en el intento %d\n", i)
			resp.Body.Close()
			return nil // ¡El evento de RabbitMQ se procesó y las credenciales ya existen!
		}

		if resp != nil {
			resp.Body.Close()
		}

		// Si llegamos aquí, el C# aún no ha procesado el evento. Esperamos y volvemos a intentar.
		time.Sleep(tiempoEspera)
	}

	return fmt.Errorf("timeout: Las credenciales no se generaron después de %v", time.Duration(maxIntentos)*tiempoEspera)
}

func (a *apiTestState) elNuevoEmpleadoDeberaPoderIniciarSesinEnElSistemaExitosamente() error {
	// Como el paso de polling ya confirmó que el login responde 200 OK,
	// este paso es simplemente una aserción final de éxito semántica para Gherkin.
	return nil
}

func (a *apiTestState) intentoRegistrarUnEmpleadoSinElCampoDeCorreoElectrnico() error {
	// Copiamos el payload pero omitimos intencionalmente el correo para forzar el fallo
	// que debería capturar la anotación @NotBlank de tu Spring Boot
	empleadoInvalido := map[string]interface{}{
		"numeroEmpleado": "EMP-ERROR",
		// OMITIMOS EL EMAIL INTENCIONALMENTE
		"nombre":         "Fallo",
		"apellido":       "Validacion",
		"cargo":          "N/A",
		"area":           "N/A",
		"departamentoId": "DEP001",
		"fechaIngreso":   "2026-04-15",
	}
	jsonData, _ := json.Marshal(empleadoInvalido)

	req, _ := http.NewRequest("POST", "http://localhost:8080/empleado", bytes.NewBuffer(jsonData))
	req.Header.Add("Content-Type", "application/json")
	req.Header.Add("Authorization", "Bearer "+a.token)

	resp, err := a.client.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	a.responseCode = resp.StatusCode
	return nil
}

// ==========================================
// PASOS DE OFFBOARDING (Reto 5 - Punto 4)
// ==========================================

var offboardID string
var offboardEmail string

func (a *apiTestState) quePreparoUnEmpleadoTemporalParaSuPosteriorDesvinculacin() error {
	// 1. Creamos un empleado al vuelo para poder eliminarlo después sin afectar la BD real
	offboardID = "EMP-DEL-" + strconv.FormatInt(time.Now().Unix(), 10)
	offboardEmail = offboardID + "@empresa.com"

	empleadoTemp := map[string]interface{}{
		"numeroEmpleado": offboardID,
		"email":          offboardEmail,
		"nombre":         "Temporal",
		"apellido":       "Offboarding",
		"cargo":          "N/A",
		"area":           "N/A",
		"departamentoId": "DEP001",
		"fechaIngreso":   time.Now().Format("2006-01-02"),
		"estado":         "ACTIVO",
	}
	jsonData, _ := json.Marshal(empleadoTemp)

	req, _ := http.NewRequest("POST", "http://localhost:8080/empleado", bytes.NewBuffer(jsonData))
	req.Header.Add("Content-Type", "application/json")
	req.Header.Add("Authorization", "Bearer "+a.token) // Reutilizamos el token de ADMIN

	resp, err := a.client.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode != 201 {
		return fmt.Errorf("no se pudo crear el empleado temporal de prueba, status: %d", resp.StatusCode)
	}

	// Simulamos una pequeña espera para que C# alcance a registrar sus credenciales
	time.Sleep(2 * time.Second)
	return nil
}

func (a *apiTestState) ejecutoLaDesvinculacinDeEsteEmpleadoEnElSistema() error {
	// Hacemos un DELETE al endpoint de empleados
	url := "http://localhost:8080/empleado/" + offboardID
	req, _ := http.NewRequest("DELETE", url, nil)
	req.Header.Add("Authorization", "Bearer "+a.token)

	resp, err := a.client.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	a.responseCode = resp.StatusCode
	return nil
}

func (a *apiTestState) elSistemaDebeRechazarSusIntentosDeInicioDeSesin() error {
	credentials := map[string]string{
		"email":    offboardEmail,
		"password": "Password123!",
	}
	jsonData, _ := json.Marshal(credentials)

	resp, err := a.client.Post("http://localhost:8084/auth/login", "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	// Como el empleado fue eliminado, el login DEBE fallar (401 o 404)
	if resp.StatusCode == http.StatusOK {
		return fmt.Errorf("riesgo de seguridad: el empleado desvinculado aún puede iniciar sesión")
	}
	return nil
}

func (a *apiTestState) elEmpleadoDesvinculadoIntentaSolicitarUnaRecuperacinDeContrasea() error {
	payload := map[string]string{
		"email": offboardEmail,
	}
	jsonData, _ := json.Marshal(payload)

	// Usamos el endpoint de recuperación de tu documento de rutas
	resp, err := a.client.Post("http://localhost:8084/auth/recover-password", "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	a.responseCode = resp.StatusCode
	return nil
}

func (a *apiTestState) laAPIDeAutenticacinDebeBloquearLaSolicitud() error {
	// Esperamos un error por parte del servidor al intentar recuperar la clave de un inactivo/eliminado
	if a.responseCode == http.StatusOK {
		return fmt.Errorf("fallo de seguridad: el sistema permitió recuperación de contraseña a un usuario inactivo")
	}
	return nil
}
