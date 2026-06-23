# ClientStateProfiler

**Educational Java project: a microservice-based client state monitoring system.**

A web application for financial monitoring. Implements user registration/authentication with role-based access and CRUD operations for client expertise records.

---

## Architecture

ClientStateProfiler follows a **microservice architecture** with an API Gateway, a shared database, and an AI-powered database agent.

```
┌──────────────┐     ┌──────────────┐     ┌───────────────────┐
│  Browser     │────▶│  GatewayApp  │────▶│ExpertiseMonitoring│
│  (Thymeleaf) │     │  :8085       │     │  :8084            │
└──────────────┘     │ WebFlux      │     │ Spring MVC        │
                     │ R2DBC        │     │ JPA/Hibernate     │
                     └──────┬───────┘     └────────┬──────────┘
                            │                       │
          ┌─────────────────┼───────────────────────┼──────────────────┐
          │                 ▼                       ▼                  │
          │          ┌───────────────────────────────────┐             │
          │          │       PostgreSQL :15432           │             │
          │          │  ┌─────────┐  ┌───────────────┐   │             │
          │          │  │ USERS   │  │  EXPERTISES   │   │             │
          │          │  └─────────┘  └───────────────┘   │             │
          │          └───────────────────────────────────┘             │
          │                    ▲                                       │ 
          │                    │                                       │
          │          ┌──────────────────┐                              │
          │          │ MigrationService │                              │
          │          │  (Flyway)        │──────────────────────────────┘
          │          └──────────────────┘
          │
          │  ┌────────────────────────────────────────────────────────┐
          │  │                    DbAgent :8080                       │
          ├──│──── Web UI (chat)    Python 3.13, Django 5, gunicorn   │
          │  │              ┌──────────────────┬──────────────┐       │
          │  │              │  Ollama          │  PostgreSQL  │       │
          │  │              │ :11434           │  (via        │       │
          │  │              │ qwen2.5-coder:7B │   psycopg2)  │       │
          │  │              └──────────────────┴──────────────┘       │
          │  └────────────────────────────────────────────────────────┘
          │
          │  ┌──────────────────────────────────────────┐
          └──│ Operator (CLI) — docker exec db_agent    │
             │ stdin/stdout — natural language queries  │
             └──────────────────────────────────────────┘
```


---

## Table of Contents

- [Technology Stack](#technology-stack)
- [Microservices](#microservices)
- [Security Model](#security-model)
- [Database Schema](#database-schema)
- [API Endpoints](#api-endpoints)
- [Quick Start](#quick-start)
    - [Docker Compose (recommended)](#docker-compose-recommended)
    - [Manual Start](#manual-start)
- [Test Credentials](#test-credentials)
- [Environment Variables](#environment-variables)
- [Development](#development)

---

## Technology Stack

| Technology | Version | Usage |
|---|---|---|
| Java | 17 | Development language |
| Spring Boot | 3.1.6 | Core framework |
| Spring Cloud Gateway | 2022.0.3 | API Gateway (routing) |
| Spring WebFlux | 3.1.6 | Reactive stack (GatewayApp) |
| Spring MVC / WebMVC | 3.1.6 | Servlet stack (ExpertiseMonitoring) |
| Spring Data R2DBC | 3.1.6 | Reactive DB access (GatewayApp) |
| Spring Data JPA / Hibernate | 3.1.6 | ORM (ExpertiseMonitoring) |
| Spring Security (Reactive) | 3.1.6 | Authentication & authorization |
| Thymeleaf + SpringSecurity6 | — | Template engine (Frontend) |
| Flyway | 10.7.1 | Database migrations |
| PostgreSQL | 16 | Relational database |
| Lombok | 1.18.x | Boilerplate code generation |
| Jasypt Spring Boot Starter | 2.1.2 | Sensitive data encryption |
| R2DBC PostgreSQL | 1.0.2 | Reactive PostgreSQL driver |
| **Python** | **3.13** | **Development language (DbAgent)** |
| **Django** | **≥5.0** | **Web framework for DbAgent UI** |
| **gunicorn** | **≥21.2** | **WSGI server for DbAgent web interface** |
| **whitenoise** | **≥6.6** | **Static file serving for Django (DbAgent)** |
| **psycopg2-binary** | **≥2.9** | **PostgreSQL connector (DbAgent)** |
| **Ollama** | **0.30.10** | **Local LLM inference server** |
| **qwen2.5-coder:7B** | — | **LLM model for natural language → SQL** |
| Docker / Docker Compose | — | Containerization |
| Maven | 3.x | Project build |

---

## Microservices

### 1. GatewayApp (`GatewayApp/`)

| Characteristic | Value |
|---|---|
| Port | `8085` |
| Technologies | Spring Cloud Gateway, WebFlux, R2DBC, Reactive Security |
| Stack | **Reactive** |
| Purpose | API Gateway + User Service |

**Features:**
- User authentication and registration
- Request proxying to ExpertiseMonitoring (`/finmonitoring/v1/**`)
- Role-Based Access Control (RBAC)

### 2. ExpertiseMonitoring (`ExpertiseMonitoring/`)

| Characteristic | Value |
|---|---|
| Port | `8084` |
| Technologies | Spring MVC, JPA/Hibernate, Thymeleaf, Validation |
| Stack | **Servlet** |
| Purpose | CRUD for financial monitoring expertise records |

**Features:**
- Search expertises by ID and ClientId
- Create, edit, and delete records
- Display results via Thymeleaf templates

### 3. MigrationService (`MigrationService/`)

| Characteristic | Value |
|---|---|
| Technologies | Spring Boot, Flyway, PostgreSQL JDBC |
| Type | **Ephemeral** (terminates after migration) |
| Purpose | Database schema initialization and seed data |

---

### 4. DbAgent (`DbAgent/`)

| Characteristic | Value |
|---|---|
| Web UI Port | `8080` (gunicorn) — via `http://localhost:8080` |
| Interfaces | **Django Web UI** (browser chat) + **Interactive CLI** |
| Technologies | Python 3.13, Django 5, gunicorn, whitenoise, psycopg2, requests (Ollama REST API) |
| Purpose | AI-powered natural language interface to the database |

**Features:**
- **Dual interface**: Web UI (primary) and interactive CLI (alternative)
- Accepts natural language queries in Russian or English (e.g. *"покажи всех пользователей"*, *"find all expertises for client X"*)
- Uses **Ollama** (local LLM server) with the `qwen2.5-coder:7B` model to generate SQL
- Executes SQL against the shared PostgreSQL database
- Summarizes results in human-readable form with automatic password masking

**Web UI features:**
- Chat-like interface with real-time status indicators (Ollama/PostgreSQL)
- Step-by-step visualization (1/3 Generate SQL → 2/3 Execute → 3/3 Summarize)
- Results displayed in a table (first 5 rows by default, with total row count)
- Keyboard shortcuts: `Ctrl+R` (refresh status), `Ctrl+L` (clear conversation)
- "Pull model" button to download Ollama model from the UI
- REST API endpoints: `GET /api/status`, `POST /api/query`, `POST /api/pull-model`

**Workflow:**
1. User enters a query → 2. Ollama generates SQL → 3. SQL executes against PostgreSQL → 4. Ollama summarizes results

**Key files:**
| File | Purpose |
|---|---|
| **Core pipeline** | |
| `src/main.py` | Interactive CLI loop, 3-step orchestration |
| `src/llm_client.py` | Ollama REST client (generate, extract SQL, pull model) |
| `src/db_connector.py` | PostgreSQL connection via psycopg2 |
| `src/prompt_templates.py` | LLM prompts and DB schema definition |
| **Web UI (Django)** | |
| `manage.py` | Django management command-line utility |
| `web/settings.py` | Django settings (Whitenoise, timezone, etc.) |
| `web/urls.py` | URL routing: `/`, `/api/query`, `/api/status`, `/api/pull-model` |
| `web/views.py` | Django views: index page, query API, status API, pull model API |
| `web/agent_service.py` | Wraps pipeline (`run_pipeline`, `check_connections`, `pull_ollama_model`) |
| `web/wsgi.py` | WSGI entry point for gunicorn |
| `web/templates/web/index.html` | Chat UI template (status bar, messages, results table) |
| `web/static/web/css/style.css` | Chat interface styles |
| `web/static/web/js/main.js` | Frontend JS: query submission, status polling, keyboard shortcuts |
| **Infrastructure** | |
| `Dockerfile` | Python 3.13-slim, gunicorn, static file collection |
| `requirements.txt` | Django, gunicorn, whitenoise, psycopg2, requests |

---

## Security Model

### User Roles

| Role | Permissions |
|---|---|
| `ROLE_USER` | Access to own information |
| `ROLE_MONITORING_USER` | Full access to expertise service |
| `ROLE_ADMIN` | Full access, view all users |

### Mechanisms
- **Authentication:** HTTP Basic + Form Login (Spring Security Reactive)
- **Password hashing:** BCryptPasswordEncoder
- **Configuration encryption:** Jasypt Spring Boot Starter (password: `commonpoint`)
- **CSRF:** Disabled for REST API
- **Authorization:** `SecurityWebFilterChain` configuration with declarative path permissions

---

## Database Schema

### `USERS` table (managed by GatewayApp via R2DBC)

| Field | Type | Description |
|---|---|---|
| `id` | `BIGINT PK` | Auto-increment ID |
| `login` | `VARCHAR(30)` | Username |
| `password` | `VARCHAR(60)` | BCrypt password hash |
| `granted_authority` | `VARCHAR(30)` | Role (e.g., `ROLE_MONITORING_USER`) |

### `EXPERTISES` table (managed by ExpertiseMonitoring via JPA)

| Field | Type | Description |
|---|---|---|
| `id` | `BIGINT PK` | Auto-increment ID |
| `expertise_type` | `VARCHAR(30)` | Expertise type (enum) |
| `client_id` | `VARCHAR(36)` | Client UUID |
| `status` | `VARCHAR(30)` | Processing status |
| `comment` | `VARCHAR(1000)` | Comment |
| `dt_expertise_status` | `TIMESTAMP` | Last modification timestamp |

### Expertise Types (ExpertiseType)

| Enum value | Code |
|---|---|
| `TURNOVER_INCREASE` | `1Dff03` |
| `ACCOUNT_LOCK` | `3Dzx05` |
| `SUPPLIER_LOSS` | `6Dix30` |

---

## API Endpoints

### GatewayApp (port 8085)

#### Public (no authentication required)

| Method | Path | Description |
|---|---|---|
| `GET` | `/login` | Login page |
| `GET` | `/signup` | Registration page |
| `GET` | `/static/public/css/*` | Static resources (CSS) |
| `POST` | `/users/v1/users` | Register a new user |

#### Authenticated (login required)

| Method | Path | Role | Description |
|---|---|---|---|
| `GET` | `/` | Authenticated | Main page with services |
| `GET` | `/users/v1/user_authorities` | Authenticated | Current user information |
| `GET` | `/selfinfo` | Authenticated | Self information |
| `GET` | `/users/v1/users/{id}` | Authenticated | Get user by ID |

#### Administrative

| Method | Path | Role | Description |
|---|---|---|---|
| `GET` | `/users/v1/users` | `ROLE_ADMIN` | List all users |

### ExpertiseMonitoring (port 8084, accessed through Gateway)

| Method | Path | Role | Description |
|---|---|---|---|
| `GET` | `/finmonitoring/v1/expertises_main` | MONITORING | Expertise main menu |
| `GET` | `/finmonitoring/v1/expertises` | MONITORING | Search expertises (params: `id`, `clientId`) |
| `POST` | `/finmonitoring/v1/expertises` | MONITORING | Create new expertise |
| `PATCH` | `/finmonitoring/v1/expertises` | MONITORING | Edit existing expertise |
| `DELETE` | `/finmonitoring/v1/expertises/{id}` | MONITORING | Delete expertise |
| `GET` | `/finmonitoring/v1/save_res` | MONITORING | Create expertise form |
| `GET` | `/finmonitoring/v1/upd_res` | MONITORING | Edit expertise form |

---

## Quick Start

### Docker Compose (recommended)

```bash
# Clone the repository
git clone git@github.com:Michael-Borovinskiy/ClientStateProfiler.git
cd ClientStateProfiler

# Start all services
docker-compose -f docker/docker-compose.yml up --build
```

After startup:
1. **PostgreSQL** will be available at `localhost:15432`
2. **GatewayApp** at `http://localhost:8085`
3. **ExpertiseMonitoring** at `http://localhost:8084` (via Gateway)
4. **Ollama** (LLM server) at `http://localhost:11434`
5. **DbAgent** — two interfaces:
   - **Web UI**: open `http://localhost:8080` in your browser
   - **CLI**: attach with `docker exec -it db_agent python /app/src/main.py`
6. Flyway migrations run automatically when `MigrationService` starts

```bash
# Stop all containers
docker-compose -f docker/docker-compose.yml down

# Stop and remove volumes (reset database)
docker-compose -f docker/docker-compose.yml down -v
```

### Manual Start

Requirements: **Java 17+**, **Maven 3.x**, **PostgreSQL 16+**

#### 1. Start PostgreSQL

Ensure PostgreSQL is running on `localhost:15432` with user `mike1` and password `nnm`.

#### 2. Create tables (run `docker/init.sql`)

```bash
psql -h localhost -p 15432 -U mike1 -d default -f docker/init.sql
```

#### 3. Populate with test data (run SQL from migrations)

```bash
psql -h localhost -p 15432 -U mike1 -d default -f MigrationService/src/main/resources/db.migration/V01__CREATE_USERS.sql
psql -h localhost -p 15432 -U mike1 -d default -f MigrationService/src/main/resources/db.migration/V02__CREATE_EXPERTISES.sql
```

#### 4. Build and start microservices

```bash
# GatewayApp (port 8085)
cd GatewayApp
mvn clean package -DskipTests
java -jar -Djasypt.encryptor.password=commonpoint target/GatewayApp-1.0-SNAPSHOT.jar &

# ExpertiseMonitoring (port 8084)
cd ../ExpertiseMonitoring
mvn clean package -DskipTests
java -jar -Djasypt.encryptor.password=commonpoint target/ExpertiseMonitoring-1.0-SNAPSHOT.jar &
```

> **Important:** When starting manually, you must pass `jasypt.encryptor.password=commonpoint` as a VM argument or environment variable.

---

## Test Credentials

| Username | Password | Role | Description |
|---|---|---|---|
| **Max** | **rewq21** | `ROLE_MONITORING_USER` | Full access to expertises |
| Leo | BCrypt | `ROLE_USER` | Basic access |
| Marco | BCrypt | `ROLE_USER` | Basic access |
| Karl | BCrypt | `ROLE_ADMIN` | Administrator |

> **Recommended login:** `Max / rewq21` — this account has access to the financial monitoring service.

---

## Development

### Project Structure

```
ClientStateProfiler/
├── docker/                        # Docker infrastructure
│   ├── docker-compose.yml         # Container orchestration
│   ├── .env                       # DB + Ollama parameters
│   ├── .env_sc                    # Jasypt password
│   └── init.sql                   # DB schema initialization
├── GatewayApp/                    # API Gateway + User Service
│   ├── src/main/java/.../         # Java code
│   └── src/main/resources/       # Configurations, templates, static files
├── ExpertiseMonitoring/           # Expertise monitoring service
│   ├── src/main/java/.../         # Java code
│   └── src/main/resources/       # Configurations, templates
├── MigrationService/              # DB migration service
│   ├── src/main/java/.../         # Java code
│   └── src/main/resources/       # Configurations, SQL migrations
├── DbAgent/                       # AI-powered DB agent (Python)
│   ├── Dockerfile                 # Python 3.13-slim, gunicorn, collectstatic
│   ├── manage.py                  # Django management command-line utility
│   ├── requirements.txt           # Django, gunicorn, whitenoise, psycopg2, requests
│   ├── src/                       # Core pipeline source code
│   │   ├── main.py                # Interactive CLI entry point
│   │   ├── llm_client.py          # Ollama REST API client
│   │   ├── db_connector.py        # PostgreSQL connector (psycopg2)
│   │   └── prompt_templates.py    # LLM prompts + DB schema
│   ├── web/                       # Django web application
│   │   ├── __init__.py
│   │   ├── settings.py            # Django settings (Whitenoise, timezone)
│   │   ├── urls.py                # URL routing (/, /api/query, /api/status, /api/pull-model)
│   │   ├── views.py               # Django views (index, api_query, api_status, api_pull_model)
│   │   ├── wsgi.py                # WSGI entry point for gunicorn
│   │   ├── agent_service.py       # Wraps pipeline for web (run_pipeline, check_connections)
│   │   ├── templates/web/
│   │   │   └── index.html         # Chat UI template
│   │   └── static/web/
│   │       ├── css/style.css      # Chat interface styles
│   │       └── js/main.js         # Frontend JavaScript
│   └── staticfiles/               # Collected static files (auto-generated)
│       └── web/
│           ├── css/style.css
│           └── js/main.js
├── logs/                          # Application logs
│   └── archived/                  # Archived log files
├── Architecture.md                # Architecture documentation (PlantUML)
├── README.md                      # This file
└── .gitignore
```

### How to Add a New Microservice (Java)

1. Create a new module following the pattern of `ExpertiseMonitoring/`
2. Add the service to `docker/docker-compose.yml`
3. Configure a route in GatewayApp (`application.yml` → `spring.cloud.gateway.routes`)
4. Add access permissions to `security.paths` in GatewayApp
5. If needed, create a Flyway migration in `MigrationService/src/main/resources/db.migration/`

### How to Add a New Python Agent

1. Create a new module following the pattern of `DbAgent/`
2. Add the service to `docker/docker-compose.yml`
3. Configure environment variables in `docker/.env`
4. The agent connects to the database via JDBC (psycopg2) or the Ollama API as needed

### Logging

- Java services use Logback with format: `%d{yyyy-MM-dd HH:mm:ss.SSS} %-5level [%thread] %logger - %msg%n`
- Log level: `INFO`
- Archived logs: `logs/archived/`
