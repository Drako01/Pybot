# Security Policy

## Secretos

Nunca publicar:

- `DISCORD_TOKEN`;
- `.env` real;
- credenciales de APIs privadas;
- bases SQLite con datos de servidores reales;
- logs que contengan secretos.

Si un token de Discord se expone, debe regenerarse inmediatamente desde Discord Developer Portal. Borrar el archivo del último commit no elimina el secreto del historial Git.

## Permisos del bot

PyBot está diseñado para trabajar con permisos específicos. No se recomienda conceder `Administrator` sólo para evitar configurar permisos.

Los módulos de moderación necesitan únicamente los permisos asociados a las acciones activadas.

## Intents privilegiados

`Server Members Intent` es necesario para welcome/farewell/autorole.

`Message Content Intent` está desactivado por defecto y no es requerido para los slash commands de v2.

## Roles

Los self roles usan una allowlist persistente configurada por administradores. El bot también verifica que:

- el rol no sea gestionado;
- no sea `@everyone`;
- esté por debajo del rol más alto del bot.

## Moderación

Los comandos verifican permisos y jerarquías antes de kick, ban o timeout.

## Dependencias

Las actualizaciones de dependencias deben pasar CI. No aplicar upgrades mayores a ciegas sin revisar changelog de `discord.py` y ejecutar tests.

## Reporte responsable

Si encontrás una vulnerabilidad, evitá publicar tokens, datos personales o un exploit operativo en un Issue público. Contactá al mantenedor por un canal privado cuando la información permita abuso directo.

## Alcance

PyBot es software comunitario/educativo. No implementa un sistema formal de compliance, SIEM ni gestión centralizada de secretos. Para despliegues críticos se recomienda integrar un secret manager, observabilidad externa y políticas del proveedor de infraestructura.
