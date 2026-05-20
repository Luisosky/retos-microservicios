package step_definitions

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strconv"
	"testing"
	"time"
	"os"

	"github.com/cucumber/godog"
)

// Estructura para guardar el estado y reutilizar el cliente HTTP
type apiTestState struct {
	token        string
	responseCode int
	client       *http.Client
}

// Función para obtener variables de entorno con un valor por defecto
func getEnv(key, fallback string) string {
	if value, exists := os.LookupEnv(key); exists {
		return value
	}
	return fallback
}

// Variables globales para las URLs base
var (
	AuthURL      = getEnv("AUTH_URL", "http://localhost:8084")
	EmpleadosURL = getEnv("EMPLEADOS_URL", "http://localhost:8080")
)

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
// PASOS DE SEGURIDAD (Reto 5 - Punto 2)
// ==========================================

func (a *apiTestState) queElSistemaEstDesplegadoYOperativo() error {
	// Inicializamos un cliente HTTP con un timeout para que no se quede colgado
	a.client = &http.Client{Timeout: 60 * time.Second}

	resp, err := a.client.Get(AuthURL+"/health")
	if err != nil {
		return fmt.Errorf("el servicio de autenticación no está respondiendo: %v", err)
	}
	defer resp.Body.Close()
	return nil
}

func (a *apiTestState) queElServicioDeEmpleadosEstDisponible() error {
	// Podemos hacer una petición rápida para verificar que el puerto 8080 responde
	// (Aunque responda 401, significa que el servicio está vivo)
	resp, err := a.client.Get(EmpleadosURL+"/empleado")
	if err != nil {
		return fmt.Errorf("el servicio de empleados no está respondiendo: %v", err)
	}
	defer resp.Body.Close()
	return nil
}

func (a *apiTestState) consultoLaListaDeEmpleadosSinTokenDeAutenticacin() error {
	req, _ := http.NewRequest("GET", EmpleadosURL+"/empleado", nil)

	resp, err := a.client.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	a.responseCode = resp.StatusCode
	return nil
}

func (a *apiTestState) queEstoyAutenticadoConElRol(rol string) error {
	var email, password string

	// 1. Asignamos credenciales diferentes según el rol que pida Gherkin
	switch rol {
	case "ADMIN":
		email = "l.castellanos@empresa.com"
		password = "Micro123456!"
	case "USER":

		email = "a.salazar@empresa.com"
		password = "Micro123456!"
	default:
		return fmt.Errorf("el rol '%s' no está configurado", rol)
	}

	credentials := map[string]string{
		"email":    email,
		"password": password,
	}

	jsonData, _ := json.Marshal(credentials)

	resp, err := a.client.Post(AuthURL+"/auth/login", "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return fmt.Errorf("error al hacer login: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("falló el login para el rol %s, código: %d", rol, resp.StatusCode)
	}

	bodyBytes, _ := io.ReadAll(resp.Body)
	fmt.Printf("Respuesta de C# para %s: %s\n", rol, string(bodyBytes))

	var result map[string]interface{}
	json.Unmarshal(bodyBytes, &result)

	if t, ok := result["token"].(string); ok {
		a.token = t
		return nil
	} else if t, ok := result["accessToken"].(string); ok {
		a.token = t
		return nil
	} else if t, ok := result["Token"].(string); ok {
		a.token = t
		return nil
	}

	return fmt.Errorf("no se encontró el JWT en la respuesta. Revisa el JSON impreso arriba")
}

func (a *apiTestState) consultoLaListaDeEmpleadosEnviandoElToken(tokenFalso string) error {
	req, _ := http.NewRequest("GET", EmpleadosURL+"/empleado", nil)
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
	req, _ := http.NewRequest("GET", EmpleadosURL+"/empleado", nil)
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

	idUnico := strconv.FormatInt(time.Now().Unix(), 10)

	nuevoEmpleado := map[string]interface{}{
		"numeroEmpleado": "EMP" + idUnico,
		"email":          "testbdd" + idUnico + "@empresa.com",
		"nombre":         "Automatización",
		"apellido":       "Prueba",
		"cargo":          "Ingeniero de Pruebas",
		"area":           "QA",
		"departamentoId": "Dep001",
		"fechaIngreso":   time.Now().Format("2006-01-02"),
		"estado":         "ACTIVO",
	}

	jsonData, _ := json.Marshal(nuevoEmpleado)

	req, _ := http.NewRequest("POST", EmpleadosURL+"/empleado", bytes.NewBuffer(jsonData))
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

	nuevoEmpleado := map[string]interface{}{
		"numeroEmpleado": "EMP" + idUnico,
		"email":          nuevoCorreo,
		"nombre":         "Usuario",
		"apellido":       "Onboarding",
		"cargo":          "Desarrollador",
		"area":           "TI",
		"departamentoId": "Dep001",
		"fechaIngreso":   time.Now().Format("2006-01-02"),
		"estado":         "ACTIVO",
	}
	jsonData, _ := json.Marshal(nuevoEmpleado)

	req, _ := http.NewRequest("POST", EmpleadosURL+"/empleado", bytes.NewBuffer(jsonData))
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
	passwordPorDefecto := "Micro123456!"
	credentials := map[string]string{
		"email":    nuevoCorreo,
		"password": passwordPorDefecto,
	}
	jsonData, _ := json.Marshal(credentials)

	fmt.Printf("\n[Hilo Principal] Iniciando búsqueda asíncrona para %s...\n", nuevoCorreo)

	// 1. Creamos un canal por donde el hilo nos avisará si tuvo éxito
	exitoChan := make(chan bool)
	
	// 2. Definimos el tiempo máximo que el Hilo Principal va a esperar (30 segundos)
	timeout := time.After(30 * time.Second)

	// 3. ¡LANZAMOS EL HILO! (Goroutine)
	// Todo lo que está dentro de go func() se ejecuta en segundo plano
	go func() {
		clienteRapido := &http.Client{Timeout: 3 * time.Second}
		intento := 1

		for {
			url := AuthURL + "/auth/login" // <-- Usando la variable global
			resp, err := clienteRapido.Post(url, "application/json", bytes.NewBuffer(jsonData))

			if err == nil && resp.StatusCode == http.StatusOK {
				fmt.Printf("✅ [Hilo Secundario] ¡Credenciales listas en el intento %d!\n", intento)
				resp.Body.Close()
				exitoChan <- true // Le avisamos al Hilo Principal que terminamos
				return            // Matamos este hilo
			}

			if resp != nil {
				resp.Body.Close()
			}

			fmt.Printf("⏳ [Hilo Secundario] Intento %d fallido. Reintentando...\n", intento)
			intento++
			time.Sleep(1500 * time.Millisecond) // Pausa de 1.5s antes de volver a intentar
		}
	}()

	// 4. El Hilo Principal se queda esperando aquí (Bloqueo Inteligente)
	select {
	case <-exitoChan:
		// El hilo secundario mandó la señal de éxito
		return nil
	case <-timeout:
		// El cronómetro de 30 segundos llegó a cero antes de recibir éxito
		return fmt.Errorf("timeout: Las credenciales no se generaron después de 30 segundos")
	}
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
		"departamentoId": "Dep001",
		"fechaIngreso":   "2026-04-15",
	}
	jsonData, _ := json.Marshal(empleadoInvalido)

	req, _ := http.NewRequest("POST", EmpleadosURL+"/empleado", bytes.NewBuffer(jsonData))
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
		"departamentoId": "Dep001",
		"fechaIngreso":   time.Now().Format("2006-01-02"),
		"estado":         "ACTIVO",
	}
	jsonData, _ := json.Marshal(empleadoTemp)

	req, _ := http.NewRequest("POST", EmpleadosURL+"/empleado", bytes.NewBuffer(jsonData))
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
	url := EmpleadosURL+"/empleado/" + offboardID
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

	resp, err := a.client.Post(AuthURL+"/auth/login", "application/json", bytes.NewBuffer(jsonData))
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
	payload := map[string]string{"email": offboardEmail}
	jsonData, _ := json.Marshal(payload)

	req, _ := http.NewRequest("POST", AuthURL+"/auth/recover-password", bytes.NewBuffer(jsonData))
	req.Header.Add("Content-Type", "application/json")

	// Creamos un cliente que solo espere 3 segundos en lugar de 60
	clienteRapido := &http.Client{Timeout: 3 * time.Second}

	resp, err := clienteRapido.Do(req)
	if err != nil {
		return err // Si falla rápido, al menos no te congela la terminal
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
