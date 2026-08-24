# Despliegue de PyBot

## Principio general

PyBot es un proceso de larga duración conectado al Discord Gateway. No es una aplicación HTTP tradicional.

Por eso debe ejecutarse como **worker** y no como web dyno.

El `Procfile` incluido usa:

```text
worker: python main.py
```

## Variables obligatorias

```dotenv
DISCORD_TOKEN=...
```

## Variables recomendadas

```dotenv
DATABASE_PATH=data/pybot.db
LOG_LEVEL=INFO
SYNC_COMMANDS=true
ENABLE_MESSAGE_CONTENT_INTENT=false
BOT_STATUS=Usá /ayuda
CURRENCY_API_BASE_URL=https://dolarapi.com/v1
HTTP_TIMEOUT_SECONDS=8
```

`DEV_GUILD_ID` debe usarse sólo cuando se quiera una sincronización rápida sobre un servidor concreto.

## Docker

### Build

```bash
docker build -t pybot .
```

### Run

```bash
docker run --rm \
  --env-file .env \
  -v "$(pwd)/data:/app/data" \
  pybot
```

El volumen es importante porque SQLite vive en `/app/data`.

## Plataformas cloud

Cualquier plataforma que ejecute un proceso Python persistente sirve, siempre que:

- permita configurar variables de entorno;
- no suspenda el proceso por falta de tráfico HTTP;
- permita almacenamiento persistente si se usa SQLite;
- permita conexiones salientes a Discord y DolarAPI.

Ejemplos conceptuales: Railway, Render Background Worker, Fly.io, VPS, Docker Compose o una VM.

## SQLite y múltiples réplicas

No ejecutar varias réplicas escribiendo sobre el mismo archivo SQLite mediante un filesystem compartido sin diseñar esa topología explícitamente.

Para alta disponibilidad o múltiples instancias, migrar la capa `Database` a PostgreSQL y usar un mecanismo de coordinación distribuida para el dispatcher de recordatorios.

## Reinicios

Los recordatorios sobreviven reinicios porque se guardan en SQLite.

Al volver a iniciar, el dispatcher procesa cualquier reminder cuya fecha ya haya vencido.

## Logs

PyBot escribe logs a stdout. Esto permite que Docker, systemd o el proveedor cloud recopile los logs sin necesidad de archivos locales.

Para producción:

```dotenv
LOG_LEVEL=INFO
```

Para troubleshooting temporal:

```dotenv
LOG_LEVEL=DEBUG
```

No dejar DEBUG de forma permanente si el volumen de logs es alto.

## systemd (ejemplo)

```ini
[Unit]
Description=PyBot Discord Bot
After=network-online.target

[Service]
Type=simple
WorkingDirectory=/opt/pybot
EnvironmentFile=/opt/pybot/.env
ExecStart=/opt/pybot/.venv/bin/python /opt/pybot/main.py
Restart=always
RestartSec=5
User=pybot

[Install]
WantedBy=multi-user.target
```

Luego:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now pybot
sudo systemctl status pybot
```

## Checklist previo a producción

- [ ] Token rotado si alguna vez estuvo expuesto.
- [ ] `.env` fuera de Git.
- [ ] `Server Members Intent` habilitado.
- [ ] Message Content Intent deshabilitado salvo necesidad real.
- [ ] Scopes `bot` y `applications.commands` al invitar.
- [ ] Permisos mínimos necesarios.
- [ ] Rol del bot por encima de los roles que debe administrar.
- [ ] Volumen persistente para `data/`.
- [ ] `DEV_GUILD_ID` removido si se desea sync global.
- [ ] CI en verde.
- [ ] Canal de mod-log configurado si se usa moderación.
