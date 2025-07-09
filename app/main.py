import json

from fastapi import FastAPI
from baml_py import ClientRegistry, Collector
from dotenv import load_dotenv
from fastapi.responses import StreamingResponse
from baml_client.async_client import b

from app.services.categorize_query import categorize_query, categorize_with_confidence
from app.services.generate_form import fill_form, stream_fill_form
from app.schemas import ClassificationInput, ExtractionInput
from typing import Any


load_dotenv()

with open("app/data/completion_format.json", "r") as f:
    COMPLETION_FORM = json.load(f)

app = FastAPI()


@app.post("/categorize/")
async def categorize_informations(data: ClassificationInput) -> dict[str, Any]:
    '''Categorizes a query into one of the predefined categories.'''
    collector = Collector(name="my-collector")
    client_registry = ClientRegistry()
    my_b = b.with_options(collector=collector, client_registry=client_registry)

    res =  await categorize_query(data, my_b)

    return res

@app.post("/categorize-score/")
async def categorize_informations_with_confidence(data: ClassificationInput, n: int = 10) -> dict[str, Any]:
    '''Categorizes a query into one of the predefined categories with confidence scores.'''
    collector = Collector(name="my-collector")
    client_registry = ClientRegistry()
    client_registry.set_primary("CustomGenericProviderTemp")
    my_b = b.with_options(collector=collector, client_registry=client_registry)

    res =  await categorize_with_confidence(data, my_b, n)

    return res



@app.post("/extract/")
async def extract_informations(request: ExtractionInput) -> dict[str, Any]:
    """
    Extracts information from a user conversation and fills a form based on a predefined schema.
    """
    collector = Collector(name="my-collector")
    client_registry = ClientRegistry()

    my_b = b.with_options(collector=collector, client_registry=client_registry)

    res = await fill_form(request.text, COMPLETION_FORM, my_b)
    
    return res

@app.post("/stream-extract/")
async def stream_extract_informations(request: ExtractionInput) -> dict[str, Any]:
    """
    Streams information extraction from a user conversation and fills a form based on a predefined schema.
    """
    collector = Collector(name="my-collector")
    client_registry = ClientRegistry()

    my_b = b.with_options(collector=collector, client_registry=client_registry)

    return StreamingResponse(stream_fill_form(request.text, COMPLETION_FORM, my_b), media_type="text/event-stream")