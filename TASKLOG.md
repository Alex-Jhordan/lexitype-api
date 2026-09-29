# TASKLOG - Backend (lexitype-api)

## Phase 1: Backend Initialization and Local Environment

- [X] ### Task 1.1: Backend Structure Setup and Initial Docker Compose
  - Create the root directory `lexitype-workspace/` and initialize the subdirectory for the API in `lexitype-workspace/lexitype-api/`.
  - Inside `lexitype-workspace/lexitype-api/`, create a minimal `Dockerfile` base (using Python 3.11) required for Docker Compose build.
  - In the root `lexitype-workspace/`, create the base `docker-compose.yml` file to define the `lexitype-backend` service (mapping `./lexitype-api` to port 8000).
  - Configure the environment variable `ALLOWED_ORIGINS=http://localhost:5173` in `docker-compose.yml` to allow requests from the frontend.
  - Ensure Docker runtime is running, then run the command `docker compose up --build -d` from the root directory to verify the initial container orchestration.

---

## Phase 2: Backend — TDD, FastAPI, Pydantic, and Gemini SDK

- [X] ### Task 2.1: Python Environment Initialization and Pytest Suite
  - Inside `lexitype-workspace/lexitype-api/`, create the `requirements.txt` file adding the dependencies: `fastapi`, `uvicorn`, `pydantic`, `google-genai`, `pytest`, `pytest-asyncio`, `httpx`, and `python-dotenv`.
  - Update `lexitype-workspace/lexitype-api/Dockerfile` to copy `requirements.txt` and execute `RUN pip install -r requirements.txt`, then run `docker compose up --build -d` to sync the container image.
  - Create the local virtual environment by running `python -m venv venv` and activate it using `source venv/bin/activate` (or `venv\Scripts\activate` on Windows), followed by `pip install -r requirements.txt`.
  - Create `pytest.ini` setting `pythonpath = .` and `asyncio_mode = auto` to resolve imports and async tests cleanly.
  - Create the directory `lexitype-workspace/lexitype-api/tests/` and inside it instantiate the files `__init__.py`, `conftest.py`, and `test_generate_words.py`.
  - Create `lexitype-workspace/lexitype-api/app/__init__.py` and a minimal `app/main.py` stub (instantiating `app = FastAPI()`) to allow module imports.
  - In `tests/conftest.py`, set a dummy `GEMINI_API_KEY` in `os.environ` and configure a Pytest fixture using `httpx.AsyncClient` pointing to the FastAPI app (`from app.main import app`) with `base_url="http://test"`.
  - Run the `pytest` command from the backend directory and confirm that it recognizes the test suite without import errors.

- [X] ### Task 2.2: TDD RED - Writing Contract Tests for Pydantic Schemas
  - In `tests/test_generate_words.py`, write the test function `test_word_request_validation()` that instantiates the `WordRequest` schema with a topic shorter than 2 characters ("A") and longer than 50 characters, expecting a Pydantic `ValidationError`.
  - In the same file, write the function `test_word_response_structure()` that validates that a response dictionary contains the keys `topic` (string), `language` (2-letter ISO 639-1 string), and `words` (an exact list of 5 elements of type `WordItem`).
  - Run `pytest tests/test_generate_words.py` and confirm that the test fails (Red) due to missing schemas in `app.schemas`.

- [X] ### Task 2.3: TDD GREEN - Implementing Pydantic Schemas
  - Inside `lexitype-workspace/lexitype-api/app/`, create the file `schemas.py`.
  - In `app/schemas.py`, define the class `WordRequest(BaseModel)` with the field `topic: str = Field(..., min_length=2, max_length=50)`.
  - Define the class `WordItem(BaseModel)` with the fields `word: str`, `display_word: str`, and `meaning: str = Field(..., max_length=200)`.
  - Define the class `WordResponse(BaseModel)` with the fields `topic: str`, `language: str = Field(..., min_length=2, max_length=2)`, and `words: list[WordItem] = Field(..., min_items=5, max_items=5)`.
  - Run `pytest tests/test_generate_words.py` and confirm that the schema tests pass to green (Green).

- [X] ### Task 2.4: TDD RED - Writing API Tests, Sanitization, and Gemini Mocks
  - In `tests/test_generate_words.py`, write the asynchronous test `test_post_generate_words_success()` using `@pytest.mark.asyncio` that performs a `client.post("/api/generate-words", json={"topic": "Vue.js"})` using `unittest.mock.patch` to simulate the structured response from the Gemini SDK and expecting HTTP 200 OK.
  - Write `test_post_generate_words_sanitization()` sending `{"topic": " <script>Vue.js</script> "}` and asserting that the sanitized topic sent to the prompt is `"Vue.js"`.
  - Write `test_post_generate_words_timeout()` using `@patch` to force a `TimeoutError` in the Gemini client and asserting that the endpoint responds with HTTP 503 Service Unavailable.
  - Run `pytest` and verify that all 3 new API tests fail (Red).

- [X] ### Task 2.5: TDD GREEN - Implementing Endpoint and Gemini Service
  - Create the file `app/services.py` defining the function `sanitize_topic(raw_topic: str) -> str` that applies `.strip()`, removes HTML tags via regular expressions, and preserves accented characters.
  - In `app/services.py`, instantiate the asynchronous function `call_gemini_api(topic: str) -> WordResponse` configuring the `google-genai` client with the `GEMINI_API_KEY` key, model `gemini-2.5-flash`, `temperature=0.7`, `timeout=8.0`, and assigning the Pydantic schema `WordResponse` in `response_schema`.
  - Update `app/main.py` adding `CORSMiddleware` (reading `ALLOWED_ORIGINS` environment variable) and implementing the route `@app.post("/api/generate-words", response_model=WordResponse)`.
  - In the endpoint function, process the payload with `sanitize_topic()`, invoke `call_gemini_api()`, and capture timeout/API exceptions returning `HTTPException(status_code=503, detail="Service Unavailable")`.
  - Update `Dockerfile` setting `CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]`.
  - Run `pytest` and confirm that the entire backend test suite passes to green (Green).

- [ ] ### Task 2.6: Backend CI/CD Pipeline
  - Create the `.github/workflows/ci.yml` file in the root of `lexitype-api` configuring the steps: `actions/checkout`, `actions/setup-python`, `pip install -r requirements.txt`, and `pytest`.
  - In Koyeb, create a new service connected to the `lexitype-api` repository via native Git Integration, selecting the Dockerfile-based deployment. Configure `GEMINI_MODEL`, `GEMINI_API_KEY` and `ALLOWED_ORIGINS` (pointing to the Vercel domain).