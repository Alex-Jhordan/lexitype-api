# Backend API & LLM Configuration

## 1. API Overview

The LexiType Space backend service (`lexitype-api`), built with FastAPI, acts as a decoupled middleware responsible for securely managing integration with the Google Gemini API (`gemini-2.5-flash`). Its main function is to receive requests from the frontend client, sanitize input, construct prompts for the language model, validate structured responses using Pydantic, and return them to the client.

Following TDD methodology, the `POST /api/generate-words` endpoint is built starting with contract test specifications in Pytest, utilizing mocks to isolate external calls to the Google GenAI SDK. All access credentials (`GEMINI_API_KEY`) reside in server environment variables and are never exposed to the client.

## 2. Contract Definitions and Pydantic Schemas

The backend uses Pydantic to ensure a strict data contract for API communication, validated through unit tests on schemas.

### Request Schema (`WordRequest`)

* **`topic` (string):** Topic or concept provided by the user. Minimum length of 2 and maximum of 50 characters after sanitization.

### Glossary Item Schema (`WordItem`)

* **`word` (string):** Normalized term without accents or special characters (e.g., "Navegacion"). Used for typing mechanics in the 2D Canvas.

* **`display_word` (string):** Term written with exact orthography, accents, and diacritics (e.g., "Navegación"). Used in the results modal (`GAME_OVER`).

* **`meaning` (string):** Concise explanation of the term (maximum 20 words).

### Response Schema (`WordResponse`)

* **`topic` (string):** The processed, sanitized topic.

* **`language` (string):** ISO 639-1 code of the detected language (e.g., "es", "en", "fr").

* **`words` (list\[WordItem\]):** Array containing exactly 5 `WordItem` objects.

## 3. TDD Test Specification and Test Case Matrix (Pytest)

Before implementing endpoint logic, the Pytest + HTTPX suite must define and fail (Red) on the following contract and behavior tests:

| **Test ID** | **Scenario / Input** | **Mock / Condition** | **Expected Result** | 
| `test_generate_words_success` | Valid payload: `{"topic": "Vue.js"}` | Gemini SDK returns valid structured JSON with 5 words. | HTTP 200 OK, response conforms to `WordResponse` schema. | 
| `test_topic_too_short` | Invalid payload: `{"topic": "A"}` | Gemini SDK is not invoked. | HTTP 400 Bad Request with validation error message. | 
| `test_topic_too_long` | Payload > 50 characters | Gemini SDK is not invoked. | HTTP 400 Bad Request. | 
| `test_input_sanitization` | Payload with HTML/symbols: `{"topic": "<script>Vue</script>"}` | String is sanitized before being sent to the prompt. | Prompt receives sanitized "Vue"; HTTP 200 OK. | 
| `test_gemini_timeout` | Valid payload: `{"topic": "Physics"}` | SDK mock simulates a timeout (8.0 seconds). | Exception caught; HTTP 503 Service Unavailable response. | 
| `test_gemini_api_error` | Valid payload | SDK mock raises authentication exception or service outage. | Exception caught; HTTP 503 Service Unavailable response. | 

## 4. Input Sanitization and Validation Logic

The endpoint function implements cleaning rules previously validated by the TDD suite:

* **Space Normalization (Trim):** Removal of unnecessary leading and trailing whitespace, collapsing multiple spaces into single internal spaces.

* **Multilingual Character Preservation:** Accents and diacritics from the original language are preserved (e.g., "Física cuántica"), as they are essential for language detection by the LLM.

* **Control Character Filtering:** Elimination of HTML tags, double quotes, and non-printable control characters.

* **Prompt Injection Delimitation:** User input is inserted encapsulated within strict delimiters inside the System Prompt.

## 5. LLM Configuration and System Prompt

Inference configuration with the Gemini SDK (`google-genai`):

* **Model:** `gemini-2.5-flash`

* **Temperature:** `0.7`

* **Top-P:** `0.95`

* **Timeout:** `8.0` seconds

### LLM System Prompt

```
You are a precise linguistic assistant for an educational typing video game called LexiType Space.
Your task is to analyze the user-provided topic and generate a JSON response following these strict rules:
1. Identify the language of the provided topic and represent it using its standard two-letter ISO 639-1 code (e.g., "es", "en", "fr"). All generated words and meanings MUST be written in that same language.
2. Generate exactly 5 relevant terms, words, or concepts directly related to the provided topic.
3. Words MUST be either single terms or short compound terms (maximum 2 words separated by a single space).
4. Provide two versions for each word:
   - "word": The term normalized WITHOUT any accent marks, tildes, or special characters (e.g., "Navegacion", "Tecnica"). Used for typing mechanics.
   - "display_word": The term written with correct standard orthography, including accent marks and proper capitalization (e.g., "Navegación", "Técnica"). Used for the glossary. 
5. Provide a clear, concise, and educational meaning for each generated term. Meanings should be short (20 words maximum).
6. You MUST strictly adhere to the requested JSON schema. Do not include markdown formatting, code block wrappers, or additional conversational text in your output. 

```

### Expected JSON Response Example (Output Schema)

```
{
  "topic": "Vue.js",
  "language": "es",
  "words": [
    {
      "word": "Reactividad",
      "display_word": "Reactividad",
      "meaning": "Mecanismo que actualiza automáticamente la interfaz de usuario cuando los datos del estado cambian."
    },
    {
      "word": "Navegacion",
      "display_word": "Navegación",
      "meaning": "Gestión de rutas e historial para desplazarse entre diferentes vistas en una aplicación SPA."
    },
    {
      "word": "Composables",
      "display_word": "Composables",
      "meaning": "Funciones que aprovechan la Composition API para encapsular y reutilizar lógica con estado."
    },
    {
      "word": "Directivas",
      "display_word": "Directivas",
      "meaning": "Atributos especiales en el HTML que aplican comportamientos reactivos al elemento del DOM."
    },
    {
      "word": "Virtual DOM",
      "display_word": "Virtual DOM",
      "meaning": "Representación ligera en memoria del DOM real para optimizar los cambios en pantalla."
    }
  ]
}

```

## 6. Error Handling and HTTP Status Codes

Captured exceptions guarantee predictable behavior automatically verified by the Pytest test suite:

* **200 OK:** Successful request. Returns the structured `WordResponse`.

* **400 Bad Request:** Invalid topic format or length (less than 2 or more than 50 characters).

* **422 Unprocessable Entity:** Invalid JSON request body structure (emitted automatically by Pydantic).

* **503 Service Unavailable:** Exception caught when the Gemini API fails to respond, authentication fails, time exceeds the 8.0-second limit, or a service outage occurs. This response triggers an immediate transition to the `SERVICE_UNAVAILABLE` state on the frontend.