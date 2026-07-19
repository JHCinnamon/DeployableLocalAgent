# Deployable Local Ollama Agent

Local Docker stack for running:

- Ollama for local model serving
- TimescaleDB (PostgreSQL-compatible) for data storage
- pgAdmin4 for database administration

## Prerequisites

- Docker Desktop (with Docker Compose support)
- Python 3.10+

## Services and Ports

- Ollama: http://localhost:11434
- TimescaleDB: localhost:5432
- pgAdmin4: http://localhost:5050

## Start/Stop with PowerShell

From the repository root:

```powershell
# Start stack
.\start_stack.ps1 -Action up

# Stop stack
.\start_stack.ps1 -Action down

# Restart stack
.\start_stack.ps1 -Action restart

# Show running services
.\start_stack.ps1 -Action ps

# Tail logs
.\start_stack.ps1 -Action logs -Follow
```

## Start/Stop with Python

From the repository root:

```powershell
python .\manage_stack.py up
python .\manage_stack.py ps
python .\manage_stack.py logs --follow
python .\manage_stack.py down
```

Optional build flag:

```powershell
python .\manage_stack.py up --build
```

## Environment Variables

The compose file supports these optional variables (defaults are provided):

- POSTGRES_DB
- POSTGRES_USER
- POSTGRES_PASSWORD
- PGADMIN_DEFAULT_EMAIL
- PGADMIN_DEFAULT_PASSWORD

You can define them in your shell environment or in a root `.env` file before starting the stack.

## Notes

- The database service is named `timescaledb` and is fully PostgreSQL compatible.
- pgAdmin4 waits for the database health check before starting.
