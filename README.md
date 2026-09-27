# SysDespacho-IA

Proyecto académico desarrollado en Python para la Tarea Académica 2
del curso Herramientas de Desarrollo Profesional - TIC.

## Descripción

SysDespacho-IA implementa un asistente llamado DespachoBot para
clasificar, registrar y notificar despachos de contenedores.

El proyecto aplica los temas de las Semanas 06 y 07: chatbot con IA,
Streamlit, transcripción de audio, asistentes, Function Calling,
argumentos JSON y automatización de tareas externas.

## Estados de despacho

- `A_TIEMPO`: faltan más de 30 minutos.
- `PROXIMO`: faltan entre 0 y 30 minutos.
- `RETRASADO`: la hora programada ya pasó.

## Funcionalidades

- Chatbot mediante la API de Groq.
- Modelo `openai/gpt-oss-20b`.
- Interfaz desarrollada con Streamlit.
- Historial de conversación mediante `st.session_state`.
- Consultas mediante texto.
- Carga de archivos de audio.
- Grabación directa mediante micrófono.
- Transcripción mediante Whisper.
- Clasificación automática de despachos.
- Function Calling con argumentos JSON.
- Registro de despachos en Google Sheets.
- Notificaciones mediante Gmail.
- Notificaciones mediante WhatsApp y WAHA.
- Proceso completo automatizado:
  - clasificar;
  - registrar en Google Sheets;
  - enviar correo;
  - enviar WhatsApp.
- Pruebas automatizadas con Pytest.

## Herramientas disponibles

DespachoBot puede ejecutar las siguientes funciones:

- `clasificar_despacho`
- `registrar_despacho`
- `enviar_alerta_correo`
- `enviar_alerta_whatsapp`
- `procesar_despacho_completo`

Las herramientas que modifican información o envían mensajes solo
deben ejecutarse cuando el usuario lo solicite expresamente.

## Estructura principal

```text
SysDespacho-IA/
├── streamlit_app.py
├── app_consola.py
├── app_asistente.py
├── app_audio.py
├── funciones.py
├── herramientas.py
├── automatizacion.py
├── transcripcion.py
├── google_sheets.py
├── correo.py
├── whatsapp.py
├── tests/
│   ├── test_funciones.py
│   └── test_herramientas.py
├── requirements.txt
├── .env.example
└── README.md
```

## Requisitos

- Python 3.11 o superior.
- Cuenta y clave API de Groq.
- Proyecto de Google Cloud con Google Sheets API.
- Cuenta de servicio de Google.
- Cuenta de Gmail con contraseña de aplicación.
- Docker Desktop.
- WAHA ejecutándose mediante Docker.
- Cuenta de WhatsApp de prueba o autorizada.

## Instalación

Crear y activar el entorno virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instalar las dependencias:

```powershell
python -m pip install -r requirements.txt
```

## Variables de entorno

Crear un archivo `.env` tomando como referencia `.env.example`.

Las variables principales son:

- `GROQ_API_KEY`
- `GROQ_MODEL`
- `GROQ_AUDIO_MODEL`
- `GOOGLE_CREDENTIALS_FILE`
- `GOOGLE_SHEET_ID`
- `GOOGLE_WORKSHEET`
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USER`
- `SMTP_APP_PASSWORD`
- `ALERT_EMAIL_TO`
- `WAHA_URL`
- `WAHA_API_KEY`
- `WAHA_SESSION`
- `WHATSAPP_TO`

## Ejecución de la interfaz

Primero debe estar iniciado Docker Desktop y el contenedor de WAHA.

Para iniciar nuevamente un contenedor WAHA existente:

```powershell
docker start waha
```

Después, ejecutar la aplicación:

```powershell
python -m streamlit run .\streamlit_app.py
```

## Ejecución por consola

Chatbot básico:

```powershell
python .\app_consola.py
```

Asistente con herramientas:

```powershell
python .\app_asistente.py
```

## Pruebas automatizadas

Ejecutar:

```powershell
python -m pytest -v
```

El proyecto contiene pruebas para:

- estado `A_TIEMPO`;
- estado `PROXIMO`;
- límite de cero minutos;
- estado `RETRASADO`;
- procesamiento de argumentos JSON;
- control de herramientas inexistentes.

## Flujo automatizado

```text
Usuario
   ↓
DespachoBot
   ↓
Function Calling
   ↓
Clasificación del despacho
   ↓
Google Sheets + correo + WhatsApp
   ↓
Respuesta final al usuario
```

## Seguridad

Los siguientes archivos y directorios no deben subirse al repositorio:

- `.env`
- `service_account.json`
- `waha/.env`
- `waha/sessions/`
- entornos virtuales;
- archivos temporales de Python.

Estos elementos están excluidos mediante `.gitignore`.

No deben escribirse claves, contraseñas ni números personales
directamente dentro del código fuente.

## Relación con la Semana 06

El proyecto incluye:

- chatbot con modelo de IA;
- uso de una API;
- desarrollo en Python;
- interfaz con Streamlit;
- historial de conversación;
- carga y grabación de audio;
- transcripción mediante Whisper.

## Relación con la Semana 07

El proyecto incluye:

- asistente con instrucciones especializadas;
- mensajes e historial;
- ejecución de herramientas;
- Function Calling;
- argumentos JSON;
- Google Sheets;
- correo automático;
- WhatsApp mediante WAHA;
- automatización completa de un proceso.