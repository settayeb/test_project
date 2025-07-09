import asyncio

from app.schemas import ClassificationInput
from baml_client.async_client import BamlAsyncClient
from typing import Dict, Any

async def categorize_query(data: ClassificationInput, baml_client: BamlAsyncClient) -> Dict[str, Any]:
    """
    Categorizes a query into one of the predefined categories.

    Args:
        query (str): The input query to categorize.

    Returns:
        str: The category of the query.
    """
    res =  await baml_client.CategorizeFeedback(
        user_message=data.text,
        categories=[{"title": class_.title, "description":class_.description} for class_ in data.themes]
    )

    

    return {
        "model_reasoning": res.rationale,
        "chosen_theme": {
            "title": data.themes[res.category - 1].title,
            "description": data.themes[res.category - 1].description,
        },
    }

async def categorize_with_confidence(data: ClassificationInput, baml_client: BamlAsyncClient, n: int) -> str:
    """
    Categorizes a query into one of the predefined categories with confidence scores.
    """

    tasks = [
        baml_client.CategorizeFeedback(
            user_message=data.text,
            categories=[{"title": class_.title, "description":class_.description} for class_ in data.themes],
            ) for _ in range(n)
        ]
    res =  await asyncio.gather(*tasks)

    Counter = {}
    for elem in res:
        if elem.category not in Counter:
            Counter[elem.category] = {
                'num': 0,
                'first': {
                    "model_reasoning": elem.rationale,
                    "chosen_theme": {
                        "title": data.themes[elem.category - 1].title,
                        "description": data.themes[elem.category - 1].description,
                    },
                }
            }
        Counter[elem.category]['num'] += 1
    
    res = max(Counter.items(), key=lambda x: x[1]['num'])[1]
    res['first']['confidence'] = res['num'] / n

    return res['first']