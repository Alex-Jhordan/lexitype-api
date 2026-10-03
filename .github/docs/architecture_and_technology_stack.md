# Architecture and Technology Stack

## 1. Architecture Overview

LexiType Space uses a decoupled monolith architecture based on the complete separation between the frontend client and the backend service. This decision guarantees a clear separation of concerns, secure handling of API credentials, and ease of running independent Continuous Integration and Continuous Deployment (CI/CD) pipelines.

The development of both layers strictly adheres to the Test-Driven Development (TDD) methodology in its Red-Green-Refactor cycle, ensuring that every API contract, state function, physics rule, and mathematical calculation has an automated test before production code is written.

* **Frontend (`lexitype`):** Single Page Application (SPA) built with Vue 3 that encapsulates the user interface logic, the game state machine, and interactive 2D Canvas rendering.
* **Backend (`lexitype-api`):** RESTful service built with FastAPI that acts as a secure middleware between the client and the Groq API (`openai/gpt-oss-20b` by default), handling data sanitization, language detection, and structured parsing.

## 2. Frontend Technology Stack

* **Vue 3 (Composition API + Single File Components):** Main user interface framework. Composition API is used along with `<script setup lang="ts">` syntax to achieve modular organization, facilitating the isolation of state logic in pure composables for isolated testing with Vitest.
* **Vite:** Next-generation bundler providing an ultra-fast local development environment and serving as the direct runner for Vitest test suites.
* **TypeScript:** Primary programming language on the client side. Provides strict static typing to define test schemas, words, game metrics, and API responses, catching contract errors at compile time.
* **Pinia:** Official state management library for Vue 3. Responsible for centralizing the game state machine (`INSTRUCTIONS`, `TOPIC_INPUT`, `LLM_LOADING`, `SERVICE_UNAVAILABLE`, `PLAYING`, `GAME_OVER`). Its architecture simplifies instantiating fresh store instances in each unit test.
* **HTML5 Canvas 2D + RequestAnimationFrame:** Technology used for the play area in the `PLAYING` state. Executes the rendering loop at a stable 60 FPS.
* **Tailwind CSS:** Utility-first CSS framework for rapid layout of main screens, modals, health bars, and results panels.
* **VueUse:** Collection of essential Vue 3 composables. Used for efficient keyboard event handling and timer bindings.
* **Lucide Icons & Canvas Confetti:**
  * **Lucide Icons:** Set of lightweight vector icons.
  * **Canvas Confetti:** Graphical library for visual effects upon game completion.

## 3. Backend Technology Stack

* **FastAPI (Python):** Asynchronous web framework for Python. Responsible for exposing the `POST /api/generate-words` REST endpoint. Its integration with Pytest allows high-speed asynchronous test requests without spinning up a server on a physical port.
* **Groq Python SDK (`groq`) & GPT OSS 20B:** Asynchronous SDK integration with Groq Chat Completions. Strict JSON Schema structured output is validated locally against the Pydantic response contract.
* **Pydantic:** Data validation library. Defines input and output schemas, strictly enforcing API contracts previously validated in the Red phase of backend testing.
* **Uvicorn:** Lightweight ASGI web server running the FastAPI application both locally and in production within Docker containers.

## 4. TDD Methodology and Testing Strategy

The project applies the TDD philosophy (Red-Green-Refactor) across three testing tiers:

### TDD Workflow (Red-Green-Refactor)
1. **Red Phase:** Write a unit or integration test describing the expected functionality or business rule (e.g., state transition, WPM calculation, or character validation). The test must fail before writing any production code.
2. **Green Phase:** Write the minimum amount of production code strictly required to pass the test.
3. **Refactor Phase:** Clean up the code, remove duplication, and improve readability or structure while keeping the test suite green.

### Frontend Testing (`lexitype`)

* **Vitest + Vue Test Utils (Unit and Integration Tests):**
  * **State Machine (Pinia Store):** TDD coverage to verify that only valid transitions between the 6 finite states are allowed and that unauthorized transitions throw exceptions or are ignored.
  * **Decoupled Game Engine Logic (`useGameEngine.ts`):** To keep mathematical tests pure and fast without DOM/Canvas dependencies, physics calculations (trajectory calculations, delta time, word floor collision detection, and target selection by lowest Y position) reside in TypeScript composables evaluated directly with Vitest.
  * **Metrics Calculation:** Unit tests for WPM, accuracy percentage, and separate destroyed/fallen word-appearance counts. Recycled appearances count as new outcomes, even when the term has appeared before.
* **Playwright (End-to-End - E2E Tests):**
  * E2E integration tests simulating the full user flow in the browser (topic entry, transition through loading screen, live word typing via `keydown` keyboard event dispatching, and display of the `GAME_OVER` modal).
  * **API Mocking:** E2E tests intercept network requests to simulate successful responses or `503 Service Unavailable` errors from `/api/generate-words`, ensuring fast and deterministic executions in the pipeline without depending on the live LLM.

### Backend Testing (`lexitype-api`)

* **Pytest + HTTPX (API and Data Contract Tests):**
  * **Schema Validation:** Tests sending valid and invalid payloads to the `POST /api/generate-words` endpoint to validate HTTP 200, 400, and 422 status codes.
  * **Sanitization and Injection:** Unit tests confirming the removal of quotes, HTML tags, and disallowed characters in the `topic` field.
  * **Groq SDK Mocking:** `unittest.mock` is used to simulate structured responses, provider errors, and timeout scenarios (8.0s), verifying that the application catches exceptions and returns a `503 Service Unavailable` status code.

## 5. DevOps Strategy, Containerization, and CI/CD

### GitHub Repository Structure
* `lexitype`: Dedicated repository for the Vue 3 frontend client.
* `lexitype-api`: Dedicated repository for the FastAPI backend service.

### Containerization and Local Development Environment
In the developer's local environment, both repositories exist as subfolders within the root `lexitype-workspace/` directory. A `docker-compose.yml` file orchestrates joint execution:
* `lexitype-frontend`: Based on Node.js `Dockerfile.dev` exposed on port 5173.
* `lexitype-backend`: Based on Python `Dockerfile` exposed on port 8000.

### Continuous Integration Pipelines with TDD Validation (CI)
Both repositories feature automated workflows via GitHub Actions acting as guardians of the TDD methodology:
* **Frontend CI:** On `push` or `pull_request` events to `main`, executes linter, type checking with `vue-tsc`, the complete unit test suite with Vitest, and E2E tests with Playwright. No branch is merged if any test is in the Red state.
* **Backend CI:** On `push` or `pull_request` events to `main`, sets up Python, installs dependencies, and runs the full Pytest suite (with contract coverage and mocks).

### Continuous Deployment Pipelines (CD) and Production
* **Frontend Deployment (Vercel):** Connected to the `lexitype` repository. Upon passing CI tests and merging into `main`, Vercel compiles the application and deploys it to its global CDN. The `VITE_API_URL` environment variable points to the backend on Render (`https://lexitype-api.onrender.com`).
* **Backend Deployment (Render):** Connected to `lexitype-api` via Git Integration. After passing CI tests, Render builds the Docker image and deploys the service.
* **Security and CORS:** FastAPI configures `CORSMiddleware`, restricting requests exclusively to the domain assigned by Vercel (`https://lexitype.vercel.app`).