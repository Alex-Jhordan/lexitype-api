import pytest
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
