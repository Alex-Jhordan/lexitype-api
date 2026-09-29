from pydantic import BaseModel, Field


class WordRequest(BaseModel):
    topic: str = Field(..., min_length=2, max_length=50)


class WordItem(BaseModel):
    word: str
    display_word: str
    meaning: str = Field(..., max_length=200)


class WordResponse(BaseModel):
    topic: str
    language: str = Field(..., min_length=2, max_length=2)
    words: list[WordItem] = Field(..., min_items=5, max_items=5)
