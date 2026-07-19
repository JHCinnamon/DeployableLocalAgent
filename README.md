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

# Start stack without table initialization
.\start_stack.ps1 -Action up -SkipInitTable

# Stop stack
.\start_stack.ps1 -Action down

# Restart stack
.\start_stack.ps1 -Action restart

# Show running services
.\start_stack.ps1 -Action ps

# Tail logs
.\start_stack.ps1 -Action logs -Follow

# Initialize vector table only
.\start_stack.ps1 -Action initdb
```

## Start/Stop with Python

From the repository root:

```powershell
python .\manage_stack.py up
python .\manage_stack.py up --skip-init-table
python .\manage_stack.py ps
python .\manage_stack.py logs --follow
python .\manage_stack.py initdb
python .\manage_stack.py down
```

## Chat with Persistent Memory

From the repository root:

```powershell
cd .\app
python .\chat_with_memory.py
```

- Each user and assistant turn is embedded and stored in PostgreSQL (`public.embeddings`).
- Memory retrieval is scoped by `conversation_id`, so you can resume the same thread later.

Resume an existing conversation:

```powershell
cd .\app
python .\chat_with_memory.py --conversation-id "your-conversation-id"
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
- Running `up` or `restart` now initializes the default vector table (`embeddings`) automatically.
