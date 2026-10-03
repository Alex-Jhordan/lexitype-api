import asyncio
import os
import re

from groq import AsyncGroq

from app.schemas import WordResponse


SYSTEM_PROMPT = """
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
""".strip()

WORD_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "topic": {"type": "string"},
        "language": {"type": "string"},
        "words": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "word": {"type": "string"},
                    "display_word": {"type": "string"},
                    "meaning": {"type": "string"},
                },
                "required": ["word", "display_word", "meaning"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["topic", "language", "words"],
    "additionalProperties": False,
}


def sanitize_topic(raw_topic: str) -> str:
    cleaned = re.sub(r"<[^>]+>", " ", raw_topic, flags=re.IGNORECASE)
    cleaned = re.sub(r"&nbsp;?", " ", cleaned)
    cleaned = re.sub(r"[\x00-\x1f\x7f]+", " ", cleaned)
    cleaned = cleaned.strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned


async def call_groq_api(topic: str) -> WordResponse:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("Missing GROQ_API_KEY")

    model_name = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

    async with AsyncGroq(api_key=api_key, timeout=8.0) as client:
        response = await asyncio.wait_for(
            client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Topic: {topic}"},
                ],
                temperature=1,
                max_completion_tokens=1024,
                reasoning_effort="low",
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "word_response",
                        "strict": True,
                        "schema": WORD_RESPONSE_SCHEMA,
                    },
                },
            ),
            timeout=8.0,
        )

    payload = response.choices[0].message.content
    if not payload:
        raise ValueError("Groq returned an empty response")
    return WordResponse.model_validate_json(payload)
