<div align="center">

# 🐍 PyBot — Professional Discord Community Bot

**Bot modular para Discord desarrollado en Python, orientado a comunidades, moderación y utilidades reales.**

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![discord.py](https://img.shields.io/badge/discord.py-2.7.1-5865F2?logo=discord&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-persistence-003B57?logo=sqlite&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)

**Autor:** [Alejandro Daniel Di Stefano](https://github.com/Drako01)

</div>

---

## ¿Qué es PyBot?

PyBot es un bot de Discord construido como un proyecto de software mantenible, no como una colección de handlers en un único archivo.

La versión 2.0 reorganiza completamente el proyecto alrededor de:

- **slash commands** nativos de Discord;
- arquitectura modular mediante **Cogs**;
- persistencia local con **SQLite**;
- llamadas HTTP **asíncronas**;
- configuración por servidor;
- moderación con validaciones de permisos y jerarquía;
- recordatorios persistentes;
- roles autoasignables controlados;
- CI, tests y linting;
- configuración segura mediante variables de entorno;
- documentación de arquitectura, comandos y despliegue.

La implementación está pensada para ser útil en un servidor real y, al mismo tiempo, funcionar como material educativo sobre desarrollo profesional de bots con Python y `discord.py`.

---

## Funcionalidades

### 🧭 General

- `/ayuda`: centro de ayuda del bot.
- `/ping`: latencia actual.
- `/about`: versión, framework y autor.
- `/serverinfo`: información del servidor.
- `/userinfo`: información de un miembro.
- `/avatar`: avatar en alta resolución.

### 🛠️ Utilidades

- `/dolar`: cotización de dólar oficial, blue, MEP, CCL, tarjeta, mayorista o cripto.
- `/encuesta`: encuesta con hasta cinco opciones.
- `/elegir`: selección aleatoria entre alternativas.
- `/dado`: dados configurables.
- `/moneda`: cara o cruz.
- `/mapa`: enlace seguro de búsqueda en Google Maps.

La consulta del dólar se realiza de manera asíncrona contra [DolarAPI.com](https://dolarapi.com/), evitando bloquear el event loop de Discord.

### ⏰ Recordatorios persistentes

- `/recordar tiempo mensaje`
- `/recordatorios`
- `/borrar-recordatorio id`

Ejemplos de duración:

```text
30s
15m
2h
3d
1w
```

Los recordatorios se guardan en SQLite, por lo que sobreviven a reinicios del proceso.

### 👋 Comunidad

- bienvenida configurable;
- despedida configurable;
- autorol para nuevos miembros;
- roles autoasignables seguros;
- mod-log configurable.

Administración:

```text
/config-ver
/config-bienvenida
/config-despedida
/config-modlog
/config-autorol
/config-rol-agregar
/config-rol-quitar
```

Miembros:

```text
/roles
/rol
```

A diferencia del comportamiento histórico basado en reaccionar a cualquier emoji cuyo nombre coincidiera con un rol, la versión actual usa una **allowlist persistente de roles autoasignables**. Esto evita que un usuario pueda obtener accidentalmente un rol sensible.

### 🛡️ Moderación

- `/limpiar`
- `/timeout`
- `/untimeout`
- `/expulsar`
- `/banear`
- `/slowmode`

Los comandos verifican:

- permisos del moderador;
- permisos del bot;
- jerarquía de roles;
- owner del servidor;
- imposibilidad de automoderarse;
- límites propios de Discord.

Si existe un canal de `mod-log`, las acciones relevantes quedan auditadas allí.

---

## Arquitectura

```text
Discord Gateway / Interactions
            │
            ▼
┌──────────────────────────────┐
│          PyBot Core          │
│ commands.Bot · CommandTree   │
│ intents · lifecycle · errors │
└──────────────┬───────────────┘
               │
       ┌───────┴─────────────────────────┐
       ▼                                 ▼
┌─────────────────────┐        ┌─────────────────────┐
│        Cogs         │        │      Services       │
│ core                │        │ aiohttp session     │
│ community           │        │ SQLite repository   │
│ moderation          │        │ external APIs       │
│ utilities           │        └──────────┬──────────┘
│ reminders           │                   │
└─────────────────────┘                   ▼
                                   ┌───────────────┐
                                   │    SQLite     │
                                   │ settings      │
                                   │ reminders     │
                                   │ self roles    │
                                   └───────────────┘
```

Más detalle en [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

---

## Estructura del repositorio

```text
Pybot/
├── .github/
│   └── workflows/
│       └── ci.yml
├── docs/
│   ├── ARCHITECTURE.md
│   ├── COMMANDS.md
│   └── DEPLOYMENT.md
├── pybot/
│   ├── cogs/
│   │   ├── core.py
│   │   ├── community.py
│   │   ├── moderation.py
│   │   ├── reminders.py
│   │   └── utilities.py
│   ├── utils/
│   │   └── timeparse.py
│   ├── bot.py
│   ├── config.py
│   ├── database.py
│   └── logging_config.py
├── tests/
├── .env.example
├── Dockerfile
├── main.py
├── pyproject.toml
├── requirements.txt
└── requirements-dev.txt
```

---

## Requisitos

- Python **3.11 o superior**;
- una aplicación creada en Discord Developer Portal;
- token del bot;
- acceso para invitar el bot al servidor.

La versión de referencia usa `discord.py 2.7.1`.

---

## Crear el bot en Discord Developer Portal

1. Ir a **Discord Developer Portal**.
2. Crear una **New Application**.
3. Entrar a **Bot** y crear/configurar el bot.
4. Regenerar/copiar el token y guardarlo únicamente en `.env`.
5. Habilitar **Server Members Intent**.
6. `Message Content Intent` puede permanecer deshabilitado con la configuración estándar de PyBot.
7. En **OAuth2 → URL Generator**, seleccionar:
   - `bot`
   - `applications.commands`
8. Seleccionar sólo los permisos que realmente utilizará el bot.

### Permisos básicos recomendados

- View Channels
- Send Messages
- Embed Links
- Add Reactions
- Read Message History

### Para moderación

Agregar, según las funciones deseadas:

- Manage Messages
- Moderate Members
- Kick Members
- Ban Members
- Manage Channels
- Manage Roles

> No es recomendable conceder `Administrator` sólo para simplificar la configuración.

---

## Instalación local

### 1. Clonar

```bash
git clone https://github.com/Drako01/Pybot.git
cd Pybot
```

### 2. Crear virtualenv

Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Instalar dependencias

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configurar entorno

```bash
cp .env.example .env
```

En Windows podés copiarlo manualmente o usar:

```powershell
Copy-Item .env.example .env
```

Editar `.env`:

```dotenv
DISCORD_TOKEN=tu-token-real
DEV_GUILD_ID=
DATABASE_PATH=data/pybot.db
LOG_LEVEL=INFO
SYNC_COMMANDS=true
ENABLE_MESSAGE_CONTENT_INTENT=false
BOT_STATUS=Usá /ayuda
CURRENCY_API_BASE_URL=https://dolarapi.com/v1
HTTP_TIMEOUT_SECONDS=8
```

### 5. Ejecutar

```bash
python main.py
```

---

## `DEV_GUILD_ID` y sincronización de comandos

Los slash commands globales pueden tardar en propagarse por Discord.

Durante desarrollo es conveniente establecer:

```dotenv
DEV_GUILD_ID=123456789012345678
```

En ese caso PyBot copia y sincroniza los comandos directamente al servidor de desarrollo, haciendo que los cambios aparezcan mucho más rápido.

Para producción puede dejarse vacío y usar sincronización global.

---

## Persistencia

SQLite se inicializa automáticamente en:

```text
data/pybot.db
```

Se almacenan:

- configuración por guild;
- canales de bienvenida/despedida/mod-log;
- autorol;
- roles autoasignables;
- recordatorios pendientes.

La carpeta `data/` está ignorada por Git.

En Docker o un proveedor cloud se debe montar como volumen persistente si se quiere conservar la información entre recreaciones del contenedor.

---

## Desarrollo

Instalar tooling:

```bash
pip install -r requirements-dev.txt
```

Lint:

```bash
ruff check .
```

Compilación estática básica:

```bash
python -m compileall -q main.py pybot
```

Tests:

```bash
pytest -q
```

---

## CI

GitHub Actions ejecuta para Python 3.11 y 3.12:

```text
install dependencies
      ↓
ruff check
      ↓
compileall
      ↓
pytest
```

El objetivo es evitar que cambios en un Cog, configuración o persistencia lleguen a `main` sin validación automática.

---

## Docker

Construir:

```bash
docker build -t pybot .
```

Ejecutar:

```bash
docker run --rm \
  --env-file .env \
  -v "$(pwd)/data:/app/data" \
  pybot
```

En Windows PowerShell:

```powershell
docker run --rm --env-file .env -v "${PWD}/data:/app/data" pybot
```

Más opciones en [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md).

---

## Seguridad

Nunca subir al repositorio:

- `DISCORD_TOKEN`;
- archivos `.env` reales;
- secretos de APIs;
- bases SQLite de producción;
- logs con información sensible.

Si un token de Discord se publica accidentalmente, **no alcanza con borrar el archivo o commit**: debe regenerarse inmediatamente desde Discord Developer Portal.

Consultar [`SECURITY.md`](SECURITY.md).

---

## Decisiones de ingeniería de v2

### Slash commands primero

El bot ya no depende de inspeccionar todos los mensajes del servidor para ejecutar sus funciones principales. Esto mejora UX, descubribilidad y reduce la necesidad del intent privilegiado `MESSAGE_CONTENT`.

### Nada de HTTP bloqueante

La implementación anterior usaba `requests.get()` dentro de una coroutine. Ahora se comparte una única `aiohttp.ClientSession`, evitando bloquear el event loop.

### Cogs independientes

Cada dominio tiene responsabilidad acotada. Agregar una funcionalidad nueva no exige modificar un archivo monolítico.

### Persistencia explícita

SQLite conserva configuración y recordatorios sin requerir un servidor de base de datos externo.

### Permisos mínimos

Los comandos de moderación usan checks de permisos y validan jerarquía antes de ejecutar acciones destructivas.

### Configuración segura

El token se obtiene del entorno y `.env` permanece fuera de Git.

---

## Documentación adicional

- [Arquitectura](docs/ARCHITECTURE.md)
- [Catálogo de comandos](docs/COMMANDS.md)
- [Despliegue](docs/DEPLOYMENT.md)
- [Política de seguridad](SECURITY.md)
- [Cómo contribuir](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)

---

## Roadmap razonable

La arquitectura permite incorporar posteriormente, sin reescribir el core:

- tickets de soporte;
- warnings persistentes;
- sistema de sugerencias;
- estadísticas y observabilidad externa;
- dashboard web;
- PostgreSQL para despliegues multi-instancia;
- métricas Prometheus;
- internacionalización;
- plugins/cogs opcionales por servidor.

---

## Licencia

MIT. Ver [`LICENSE`](LICENSE).

---

## Autor

**Alejandro Daniel Di Stefano**  
GitHub: [@Drako01](https://github.com/Drako01)

PyBot se mantiene como proyecto práctico de referencia sobre Python asíncrono, Discord, arquitectura modular, persistencia y buenas prácticas de ingeniería de software.
