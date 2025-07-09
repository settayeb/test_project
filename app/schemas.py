from pydantic import BaseModel

class ClassificationClass(BaseModel):
    title: str
    description: str

class ClassificationInput(BaseModel):
    text: str
    themes: list[ClassificationClass]

class ExtractionInput(BaseModel):
    text: str