import pytest
from unittest.mock import patch
from pydantic import ValidationError

from app.schemas import WordItem, WordRequest, WordResponse


def test_word_request_validation():
    with pytest.raises(ValidationError):
        WordRequest(topic="A")

    with pytest.raises(ValidationError):
        WordRequest(topic="x" * 51)


def test_word_response_structure():
    payload = {
        "topic": "React",
        "language": "en",
        "words": [
            {"word": "component", "display_word": "component", "meaning": "A reusable UI unit."},
            {"word": "state", "display_word": "state", "meaning": "The current condition of the app."},
            {"word": "render", "display_word": "render", "meaning": "To display UI content."},
            {"word": "props", "display_word": "props", "meaning": "Data passed into a component."},
            {"word": "hook", "display_word": "hook", "meaning": "A function that uses component state."},
        ],
    }

    response = WordResponse(**payload)

    assert response.topic == "React"
    assert response.language == "en"
    assert isinstance(response.words, list)
    assert len(response.words) == 5
    assert all(isinstance(item, WordItem) for item in response.words)


@pytest.mark.asyncio
async def test_post_generate_words_success(client):
    mock_response = {
        "topic": "Vue.js",
        "language": "en",
        "words": [
            {"word": "component", "display_word": "component", "meaning": "A reusable UI unit."},
            {"word": "state", "display_word": "state", "meaning": "The current condition of the app."},
            {"word": "render", "display_word": "render", "meaning": "To display UI content."},
            {"word": "props", "display_word": "props", "meaning": "Data passed into a component."},
            {"word": "hook", "display_word": "hook", "meaning": "A function that uses component state."},
        ],
    }

    with patch("app.main.call_gemini_api", return_value=WordResponse(**mock_response)):
        response = await client.post("/api/generate-words", json={"topic": "Vue.js"})

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_post_generate_words_sanitization(client):
    captured = {}

    async def fake_call_gemini_api(topic: str):
        captured["topic"] = topic
        return WordResponse(
            topic=topic,
            language="en",
            words=[
                {"word": "component", "display_word": "component", "meaning": "A reusable UI unit."},
                {"word": "state", "display_word": "state", "meaning": "The current condition of the app."},
                {"word": "render", "display_word": "render", "meaning": "To display UI content."},
                {"word": "props", "display_word": "props", "meaning": "Data passed into a component."},
                {"word": "hook", "display_word": "hook", "meaning": "A function that uses component state."},
            ],
        )

    with patch("app.main.call_gemini_api", side_effect=fake_call_gemini_api):
        response = await client.post("/api/generate-words", json={"topic": " <script>Vue.js</script> "})

    assert response.status_code == 200
    assert captured["topic"] == "Vue.js"


@pytest.mark.asyncio
async def test_post_generate_words_timeout(client):
    with patch("app.main.call_gemini_api", side_effect=TimeoutError):
        response = await client.post("/api/generate-words", json={"topic": "Vue.js"})

    assert response.status_code == 503
    assert response.json()["detail"] == "Service Unavailable"
