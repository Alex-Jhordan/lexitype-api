# LexiType API (`lexitype-api`)

`lexitype-api` is the backend service for **LexiType Space**, an arcade typing game. Built with **FastAPI**, **Pydantic**, and the **Groq Python SDK**, this service is responsible for validating user-requested topics, sanitizing inputs, and generating structured word lists for gameplay with Groq.

---

## 🛠️ Tech Stack & Dependencies

- **Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Python 3.11+)
- **Data Validation & Schemas:** [Pydantic v2](https://docs.pydantic.dev/)
- **LLM Integration:** [Groq Python SDK](https://github.com/groq/groq-python) (`groq` using `openai/gpt-oss-20b` by default)
- **Testing & Mocks:** [Pytest](https://docs.pytest.org/), `pytest-asyncio`, `httpx`, `unittest.mock`
- **Server & Environment:** Uvicorn, `python-dotenv`
- **Containerization & Deployment:** Docker, Docker Compose, GitHub Actions (CI), Render

---

## 🏗️ Project Architecture

```text
lexitype-api/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application, CORS setup, and HTTP endpoints
│   ├── schemas.py       # Pydantic data validation contracts (WordRequest, WordResponse)
│   └── services.py      # Input sanitization and Groq API integration service
├── tests/
│   ├── __init__.py
│   ├── conftest.py      # Pytest fixtures (httpx.AsyncClient setup)
│   └── test_generate_words.py  # Unit, schema contract, and mock API tests
├── .github/
│   ├── docs/            # Specification-Driven Development (SDD) references
│   └── workflows/
│       └── ci.yml       # GitHub Actions automated test workflow
├── AGENTS.md            # AI agent instructions and operational guidelines
├── TASKLOG.md           # Granular task tracking checklist
├── docker-compose.yml   # Multi-container local orchestration (workspace root)
├── Dockerfile           # Production container configuration
├── requirements.txt     # Python dependency lockfile
└── README.md            # Project documentation
```

## 📡 API Endpoint Contract

### `POST /api/generate-words`

Generates 5 themed words based on a user-provided topic.

#### **Request Body (`WordRequest`)**
```json
{
  "topic": "Vue.js"
}
```

- **Constraints:** `topic` must be between 2 and 50 characters long. HTML tags are automatically stripped and whitespace is sanitized before prompt processing.

#### **Successful Response (`WordResponse` - 200 OK)**
```json
{
  "topic": "Vue.js",
  "language": "es",
  "words": [
    {
      "word": "componente",
      "display_word": "componente",
      "meaning": "Bloque de construcción reutilizable en la interfaz de usuario."
    },
    {
      "word": "reactividad",
      "display_word": "reactividad",
      "meaning": "Mecanismo que actualiza automáticamente la vista cuando los datos cambian."
    },
    {
      "word": "directiva",
      "display_word": "directiva",
      "meaning": "Instrucción especial en el plantilla que aplica comportamientos al DOM."
    },
    {
      "word": "plantilla",
      "display_word": "plantilla",
      "meaning": "Sintaxis basada en HTML que vincula la instancia con el DOM."
    },
    {
      "word": "instancia",
      "display_word": "instancia",
      "meaning": "Objeto principal que inicializa y controla una aplicación en Vue."
    }
  ]
}
```

#### **Error Responses**
- **422 Unprocessable Entity:** Payload schema validation failure (e.g., topic length < 2 or > 50).
- **503 Service Unavailable:** Downstream Groq API timeout (> 8.0s), network/rate-limit error, invalid key configuration, or invalid model response.

---

## 🚀 Getting Started Locally

### Option 1: Running with Docker Compose (Recommended)

From the root workspace directory (`lexitype-workspace/`):

Create `lexitype-api/.env` with the backend credentials (this path is git-ignored):

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-20b
```

```bash
docker compose up --build -d
```

The API will be accessible at `http://localhost:8000`.

Send a request to the local endpoint from PowerShell:

```powershell
$body = @{ topic = "Vue.js" } | ConvertTo-Json
Invoke-RestMethod `
  -Uri "http://localhost:8000/api/generate-words" `
  -Method Post `
  -ContentType "application/json" `
  -Body $body
```

The response should contain a two-letter `language` code and exactly five `words`.

### Option 2: Local Python Environment Setup

1. **Navigate to the API directory:**
   ```bash
   cd lexitype-api
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration:**
   Create a `.env` file in the root of `lexitype-api/`:

   ```bash
   GROQ_API_KEY=your_groq_api_key_here
   GROQ_MODEL=your_groq_model_here
   ALLOWED_ORIGINS=http://localhost:5173
   ```

5. **Run the local development server:**
   ```bash
   uvicorn app.main:app --reload --port 8000 --env-file .env
   ```

## 🧪 Testing Suite (TDD)

The codebase strictly enforces Test-Driven Development (TDD) with high unit test coverage and deterministic external mocks.

Run these commands from `lexitype-api` with its virtual environment active. The tests mock Groq and do not need a live API key:

```bash
python -m pytest tests/test_generate_words.py -q
python -m pytest
```

For verbose output:

```bash
python -m pytest -v -s
```

## 🚢 CI/CD & Deployment

- **Continuous Integration (CI):** GitHub Actions executes `.github/workflows/ci.yml` on every push/pull-request, running dependency verification and the Pytest suite.
- **Continuous Deployment (CD):** Render natively builds and deploys the container from GitHub on successful main branch merges.

---

## 📚 Specification-Driven Architecture

All system requirements, API schema contracts, backend architecture, and integration rules are strictly documented inside `.github/docs/`:

| Specification File | Scope & Domain |
| :--- | :--- |
| **`overview_and_game_flow.md`** | Game loop overview, topic validation requirements, and vocabulary generation rules. |
| **`architecture_and_technology_stack.md`** | FastAPI architecture, Pydantic v2 schemas, project layout, and dependencies. |
| **`2d_canvas_mechanics_and_game_physics.md`** | Front-end Canvas constraints impacting backend word payload sizes and lengths. |
| **`backend_api_llm_configuration.md`** | REST endpoints (`POST /api/generate-words`), Groq SDK configuration, error codes (422, 503), timeouts, and sanitization logic. |
| **`ui_component_structure.md`** | UI state handling for loading (`LLM_LOADING`) and error (`SERVICE_UNAVAILABLE`) states. |

---

## 🛡️ Agent Guidelines (`AGENTS.md`)

AI assistants and automated agents working within this repository must adhere to the rules in `AGENTS.md`:

1. **Consult Specifications First:** Review the relevant domain documents in `.github/docs/` prior to generating or refactoring code or writing test cases.
2. **Strict Test-Driven Development (TDD):** Maintain strict Pydantic models, FastAPI response types, and comprehensive Pytest test coverage using mocks for all external LLM network requests.
3. **Do NOT automatically check off tasks or update `TASKLOG.md`** — task verification must remain an explicit human engineering task.