# Changelog

Todos los cambios relevantes de PyBot se documentan en este archivo.

El versionado sigue [Semantic Versioning](https://semver.org/).

## [2.0.0] — 2026-08-23

### Added

- arquitectura modular basada en Cogs;
- slash commands como interfaz principal;
- configuración tipada por variables de entorno;
- persistencia SQLite con `aiosqlite`;
- configuración por servidor para bienvenida, despedida, mod-log y autorol;
- self roles con allowlist administrativa;
- recordatorios persistentes;
- moderación con timeout, untimeout, kick, ban, purge y slowmode;
- validaciones de permisos y jerarquías;
- auditoría de acciones de moderación;
- consulta asíncrona de cotizaciones mediante DolarAPI;
- encuestas, elección aleatoria, dados, moneda y Google Maps;
- error handler global para application commands;
- una única `aiohttp.ClientSession` administrada por lifecycle;
- Dockerfile;
- CI para Python 3.11 y 3.12;
- Ruff, compile checks y pytest;
- tests de configuración, parsing de duración y persistencia;
- documentación de arquitectura, comandos, despliegue y seguridad;
- `CONTRIBUTING.md` y `.env.example`.

### Changed

- `discord.py` actualizado de 2.3.2 a 2.7.1;
- entrypoint movido a `main.py`;
- proceso Heroku/Procfile cambiado de `web` a `worker`;
- el bot deja de depender del parsing de mensajes libres para sus funciones centrales;
- `Message Content Intent` pasa a ser opcional y deshabilitado por defecto;
- la consulta de dólar deja de usar `requests` síncrono;
- roles por reacción reemplazados por self roles explícitos y seguros;
- README reescrito como guía completa de producto e ingeniería.

### Removed

- implementación monolítica antigua de `bot.py`;
- `events.py` legacy;
- `wsgi.py` obsoleto;
- bytecode `__pycache__` versionado;
- dependencias antiguas/no utilizadas como `requests`, `youtube-dl` y paquetes transitivos fijados manualmente.

### Security

- token exclusivamente desde entorno;
- `.env` ignorado;
- permisos mínimos documentados;
- controles de jerarquía para moderación y roles;
- Message Content Intent no requerido en operación estándar.
