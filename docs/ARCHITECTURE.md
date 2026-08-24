# Arquitectura de PyBot

## Objetivo

PyBot v2 aplica una arquitectura modular para evitar que eventos, comandos, acceso a datos y llamadas HTTP queden mezclados en un único archivo.

## Capas

### `main.py`

Es el composition root. Sólo:

1. carga `Settings`;
2. configura logging;
3. construye `PyBot`;
4. inicia el cliente Discord.

No contiene lógica de negocio.

### `pybot/bot.py`

Contiene el lifecycle del bot:

- intents;
- carga de extensiones;
- creación de una única `aiohttp.ClientSession`;
- conexión SQLite;
- sincronización de slash commands;
- presence;
- cierre ordenado de recursos;
- error handler global de application commands.

### Cogs

Cada Cog representa un dominio.

| Cog | Responsabilidad |
|---|---|
| `core.py` | ayuda, ping e información |
| `community.py` | joins/leaves, configuración, autorol y self roles |
| `moderation.py` | acciones de moderación y auditoría |
| `utilities.py` | dólar, encuestas y utilidades generales |
| `reminders.py` | creación y dispatch de recordatorios |

Los Cogs no crean conexiones HTTP ni conexiones de base propias: reutilizan recursos administrados por `PyBot`.

## Persistencia

`Database` encapsula SQLite mediante `aiosqlite`.

Tablas actuales:

### `guild_settings`

Configuración por servidor:

- welcome channel;
- farewell channel;
- mod-log channel;
- autorole.

### `self_roles`

Allowlist de roles que los miembros pueden asignarse mediante `/rol`.

### `reminders`

Recordatorios persistentes, con usuario, canal, guild, deadline y mensaje.

SQLite usa WAL para mejorar comportamiento ante lecturas/escrituras concurrentes del mismo proceso.

## Flujo de un slash command

```text
Usuario
  │
  ▼
Discord Interaction
  │
  ▼
CommandTree
  │
  ▼
Cog command
  ├── permission checks
  ├── validation
  ├── DB / external API
  └── Interaction response
```

## Intents

Se habilita `members` porque PyBot implementa:

- bienvenida/despedida;
- autorol;
- información de miembros.

`message_content` está deshabilitado por defecto. Los slash commands no lo necesitan.

Esto evita pedir un intent privilegiado que ya no forma parte de la funcionalidad principal.

## HTTP

PyBot no utiliza `requests` en handlers async.

El core crea una sola `aiohttp.ClientSession` con timeout global y la comparte durante toda la vida del proceso. Esto evita:

- bloquear el event loop;
- crear conexiones nuevas por cada comando;
- dejar sesiones sin cerrar.

## Manejo de errores

El `CommandTree` tiene un error handler global que diferencia:

- cooldown;
- permisos faltantes del usuario;
- permisos faltantes del bot;
- check failures;
- errores inesperados.

Los errores inesperados se registran y al usuario se le devuelve un mensaje neutro.

## Moderación y jerarquía

Los comandos destructivos no confían sólo en permisos de Discord. También verifican:

- self-target;
- owner del guild;
- top role del moderador;
- top role del bot;
- roles gestionados.

## Recordatorios

Un `tasks.loop` consulta recordatorios vencidos cada 15 segundos.

Sólo se elimina el recordatorio después de una entrega exitosa. Si Discord no permite entregar el mensaje temporalmente, el registro permanece para un próximo intento.

## Sincronización de comandos

En desarrollo puede definirse `DEV_GUILD_ID` para sincronización inmediata sobre un guild.

En producción se omite para sincronización global.

## Escalabilidad

SQLite es adecuada para una única instancia del bot y comunidades pequeñas/medianas.

Si PyBot evolucionara a múltiples réplicas, se recomienda reemplazar `Database` por PostgreSQL y agregar coordinación distribuida para jobs/recordatorios.

La separación actual permite hacer ese cambio sin reescribir los Cogs.

## Principios aplicados

- responsabilidades separadas;
- configuración externa;
- recursos compartidos con lifecycle explícito;
- I/O no bloqueante;
- least privilege;
- persistencia detrás de una abstracción;
- commands as product API;
- testabilidad de lógica pura y persistencia;
- backward cleanup: sin mantener dos cores en paralelo.
