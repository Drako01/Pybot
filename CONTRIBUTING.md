# Contribuir a PyBot

## Flujo recomendado

1. Crear una rama desde `main`.
2. Mantener cada cambio enfocado en un dominio.
3. Agregar o actualizar tests cuando corresponda.
4. Ejecutar lint y tests localmente.
5. Abrir PR explicando problema, solución y validación.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
```

En Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
Copy-Item .env.example .env
```

## Calidad

Antes del PR:

```bash
ruff check .
python -m compileall -q main.py pybot
pytest -q
```

## Arquitectura

- Los comandos deben vivir en el Cog del dominio correspondiente.
- No crear una `ClientSession` por request/comando.
- No usar librerías HTTP síncronas dentro de coroutines.
- El acceso SQLite debe pasar por `Database`.
- No leer variables de entorno directamente desde Cogs; usar `Settings`.
- Las acciones destructivas deben validar permisos y jerarquía.
- Evitar habilitar intents privilegiados si una feature no los necesita.

## Nuevos comandos

Al agregar un comando:

- usar slash commands;
- escribir `description` clara;
- usar tipos de Discord cuando corresponda (`Member`, `Role`, `TextChannel`);
- aplicar rangos con `app_commands.Range`;
- aplicar checks de permisos;
- responder `ephemeral=True` cuando la información sea administrativa o sensible;
- documentarlo en `docs/COMMANDS.md`.

## Persistencia

Los cambios de esquema deben ser compatibles con instalaciones existentes. `CREATE TABLE IF NOT EXISTS` es suficiente para tablas nuevas, pero cambios de columnas deben tratarse como migraciones explícitas en futuras versiones.

## Commits

Se recomienda Conventional Commits:

```text
feat: add ticket system
fix: prevent role hierarchy escalation
docs: explain production deployment
test: cover reminder parser
refactor: isolate external API client
```

## Seguridad

No incluir tokens reales, IDs privados innecesarios, `.env`, databases ni dumps de servidores en commits o fixtures.
