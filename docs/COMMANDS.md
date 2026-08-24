# Catálogo de comandos

Todos los comandos principales de PyBot v2 son **slash commands**.

## General

### `/ayuda`
Muestra un resumen de módulos y comandos.

### `/ping`
Devuelve la latencia estimada del bot contra Discord.

### `/about`
Versión de PyBot, `discord.py`, cantidad de servidores y autor.

### `/serverinfo`
Información del servidor actual.

### `/userinfo [miembro]`
Información de un miembro. Sin parámetro usa el usuario que ejecuta el comando.

### `/avatar [usuario]`
Muestra el avatar en alta resolución.

## Comunidad

### `/roles`
Lista roles autoasignables permitidos.

### `/rol rol`
Alterna un rol permitido: si el usuario no lo tiene lo agrega; si ya lo tiene lo quita.

### `/config-ver`
**Permiso:** Manage Server.

Muestra canales, autorol y self roles configurados.

### `/config-bienvenida [canal]`
**Permiso:** Manage Server.

Define el canal de bienvenida. Sin canal, desactiva la función.

### `/config-despedida [canal]`
**Permiso:** Manage Server.

Define el canal de despedida. Sin canal, desactiva la función.

### `/config-modlog [canal]`
**Permiso:** Manage Server.

Define el canal donde se auditan acciones de moderación.

### `/config-autorol [rol]`
**Permiso:** Manage Roles.

Configura el rol que reciben nuevos miembros. PyBot valida jerarquía y roles gestionados.

### `/config-rol-agregar rol`
**Permiso:** Manage Roles.

Agrega un rol a la allowlist de autoasignación.

### `/config-rol-quitar rol`
**Permiso:** Manage Roles.

Elimina un rol de esa allowlist.

## Moderación

### `/limpiar cantidad`
**Permiso:** Manage Messages.

Elimina entre 1 y 100 mensajes recientes.

### `/timeout miembro minutos [motivo]`
**Permiso:** Moderate Members.

Aplica timeout entre 1 minuto y 28 días.

### `/untimeout miembro [motivo]`
**Permiso:** Moderate Members.

Quita el timeout.

### `/expulsar miembro [motivo]`
**Permiso:** Kick Members.

Expulsa un miembro validando jerarquía.

### `/banear miembro [motivo] [borrar_horas]`
**Permiso:** Ban Members.

Banea un miembro. `borrar_horas` permite borrar hasta 168 horas de mensajes previos según soporte de Discord.

### `/slowmode segundos`
**Permiso:** Manage Channels.

Configura slowmode entre 0 y 21600 segundos. Cero lo desactiva.

## Utilidades

### `/dolar tipo`
Consulta DolarAPI de forma asíncrona.

Tipos disponibles:

- Oficial
- Blue
- MEP / Bolsa
- CCL
- Tarjeta
- Mayorista
- Cripto

### `/encuesta pregunta opcion_1 opcion_2 [opcion_3] [opcion_4] [opcion_5]`
Crea un embed y agrega reacciones numéricas para votar.

### `/elegir opciones`
Selecciona aleatoriamente una opción.

Formato:

```text
pizza | sushi | empanadas
```

### `/dado [caras] [cantidad]`
Tira entre 1 y 10 dados, con entre 2 y 1000 caras.

### `/moneda`
Cara o cruz.

### `/mapa lugar`
Genera un enlace a una búsqueda de Google Maps sin requerir API key.

## Recordatorios

### `/recordar tiempo mensaje`
Crea un recordatorio persistente.

Unidades:

- `s`: segundos
- `m`: minutos
- `h`: horas
- `d`: días
- `w`: semanas

Ejemplo:

```text
/recordar tiempo:2h mensaje:Revisar el deploy
```

Máximo: 365 días.

### `/recordatorios`
Lista hasta los próximos 10 recordatorios del usuario.

### `/borrar-recordatorio id`
Borra un recordatorio propio por ID.

## Comandos legacy

La versión 1 reaccionaba a texto libre en mensajes como `dolar blue compra`, menciones, saludos o `¿dónde queda ...?`.

En v2 esas funcionalidades fueron reemplazadas por comandos explícitos (`/dolar`, `/mapa`, `/ayuda`, etc.). Esto reduce falsos positivos, hace las funciones descubribles y evita depender del Message Content Intent para la operación normal.
