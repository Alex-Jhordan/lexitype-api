# Agent Instructions & Workflow Guidelines (AGENTS.md)

This file defines the operational guidelines, project context, and mandatory protocols for AI agents and assistants working inside the `lexitype-api` backend repository.

---

## 1. Core Operating Principles

1. **Specification-Driven Development (SDD):**
   - Do not alter API schemas, add endpoints, or modify third-party service integrations without consulting the project specs located in `.github/docs/`.
   - Before executing non-trivial tasks, review the corresponding documentation file based on the task domain.

2. **Task Execution & Status Tracking:**
   - **Do NOT auto-mark tasks as completed.**
   - Do **NOT** update, check off, or annotate task checklists (e.g., in `TASKLOG.md` or issue boards) anywhere upon finishing a feature, fix, or refactor.
   - Task completion status must be explicitly verified and updated by the human engineer after review.

3. **Codebase Standards & Testing:**
   - Maintain strict Python type hinting and Pydantic schema enforcement.
   - Follow Test-Driven Development (TDD) using Pytest and HTTPX. Ensure unit test coverage and mock external services (such as the Google Gemini SDK) during tests to keep runs deterministic and fast.
   - Adhere to clean FastAPI architecture, proper exception handling, input sanitization, and structured HTTP error responses (e.g., HTTP 503 for LLM/service timeouts).

---

## 2. Documentation Architecture (`.github/docs/`)

All foundational specifications, architecture rules, and functional domain references are located at the root of the project under `./github/docs/`:

| Spec File | Purpose & Task Domain |
| :--- | :--- |
| **`overview_and_game_flow.md`** | Core game loop, lifecycle, and overall context of how the backend feeds gameplay elements. **Consult when reviewing game requirements and system context.** |
| **`architecture_and_technology_stack.md`** | High-level system architecture, FastAPI setup, Pydantic, CORS, environment variables, Pytest configuration, and Docker setup. **Consult for architecture changes, environment setup, or testing strategies.** |
| **`2d_canvas_mechanics_and_game_physics.md`** | Client-side mechanics reference. **Consult if backend data models need alignment with frontend physics requirements (e.g., word lengths, structure).** |
| **`backend_api_llm_configuration.md`** | Detailed REST endpoint contracts (`POST /api/generate-words`), Pydantic schemas (`WordRequest`, `WordItem`, `WordResponse`), input sanitization rules, Google Gemini 2.5 Flash SDK setup, system prompts, and HTTP status codes. **Consult when modifying API routes, LLM prompts, schemas, or service logic.** |
| **`ui_component_structure.md`** | Frontend UI component specification reference. **Consult when checking data requirements or error state behaviors expected by the frontend modals and screens.** |

---

## 3. Workflow Protocol for Agents

When assigned a user query or issue:

1. **Identify the Task Domain:** Map the request to one or more specification files in `./github/docs/`.
2. **Consult Specifications:** Read the relevant markdown files in `./github/docs/` prior to generating or modifying code to ensure compliance with existing contracts and schemas.
3. **Execute Changes:** Write clean, modular, and type-safe Python code adhering strictly to architectural constraints and TDD practices.
4. **Halt Checklist Updates:** Deliver code changes and summaries without altering completion markers in task tracking files.