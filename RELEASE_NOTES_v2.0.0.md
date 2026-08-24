# PyBot v2.0.0 — Professional Discord Bot Edition

PyBot 2.0 transforma el proyecto original en una plataforma modular de utilidades y administración para comunidades Discord.

## Highlights

- Slash commands nativos.
- Arquitectura por Cogs.
- SQLite para configuración y recordatorios.
- Sistema completo de bienvenida/despedida/autorol.
- Self roles seguros y administrables.
- Herramientas de moderación con controles de jerarquía.
- Mod-log.
- Recordatorios persistentes.
- Cotización del dólar mediante I/O asíncrono.
- Encuestas y utilidades comunitarias.
- Docker.
- CI Python 3.11/3.12.
- Tests y Ruff.
- Documentación completa.

## Breaking architecture change

La estructura monolítica anterior (`bot.py` + `events.py`) fue reemplazada por `main.py` y el paquete `pybot/`.

El comportamiento basado en inspección automática de mensajes también fue reemplazado por slash commands explícitos.

Para desplegar v2 es necesario revisar `.env.example` y usar `DISCORD_TOKEN`.

## Discord Developer Portal

La versión actual necesita **Server Members Intent** para funciones de miembros.

`Message Content Intent` no es requerido por defecto.

Al invitar el bot se deben incluir los scopes:

- `bot`
- `applications.commands`

## Persistencia

Los datos se almacenan por defecto en:

```text
data/pybot.db
```

En despliegues Docker/cloud se debe persistir la carpeta `data/`.

## Upgrade recomendado

1. Crear backup de cualquier configuración externa que se quiera conservar.
2. Actualizar código.
3. Crear `.env` desde `.env.example`.
4. Instalar nuevas dependencias.
5. Revisar intents y permisos del bot.
6. Ejecutar `python main.py`.
7. Configurar el servidor desde `/config-*`.

## Autor

**Alejandro Daniel Di Stefano**  
GitHub: [@Drako01](https://github.com/Drako01)

Tag sugerido: `v2.0.0`

Título sugerido de Release:

**PyBot v2.0.0 — Professional Discord Bot Edition**
