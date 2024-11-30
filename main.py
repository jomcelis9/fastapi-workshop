from fastapi import FastAPI, Query, Path, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from http import HTTPStatus

app = FastAPI()

# Root route
@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}

# Item model
class Item(BaseModel):
    name: str
    price: float
    description: Optional[str] = None

class ItemOut(Item):
    created_at: datetime

class Message(BaseModel):
    message: str

# POST endpoint to create an item
@app.post(
    "/items",
    response_model=ItemOut,
    response_model_exclude_none=True,
    response_model_exclude_unset=True,
    responses={
        HTTPStatus.INTERNAL_SERVER_ERROR: {
            "model": Message,
            "description": "Internal Server Error",
        },
    },
    summary="Create Item",
    description="Create item details for a product",
)
async def create_item(item: Item):
    response = ItemOut(
        **item.dict(),
        created_at=datetime.now(),
    )
    return response

# Dependency for common parameters
async def common_parameters(q: str | None = Query(None, description="Query string")):
    return {"q": q}

# GET endpoint to read items
@app.get("/items/")
async def read_items(q: str = None):
    commons = await common_parameters(q)
    return commons

# GET endpoint to read users
@app.get("/users/")
async def read_users(q: str = None):
    commons = await common_parameters(q)
    return commons

# Extended common parameters dependency
async def extended_common_parameters(
    q: str | None = Query(None, description="Query string"),
    item_id: int = Path(..., description="The ID of the item to get"),
):
    return {"q": q, "item_id": item_id}

# GET endpoint to retrieve item details
@app.get(
    "/items/{item_id}",
    response_model=ItemOut,
    response_model_exclude_none=True,
    response_model_exclude_unset=True,
    responses={
        HTTPStatus.NOT_FOUND: {
            "model": Message,
            "description": "Item not found",
        },
        HTTPStatus.INTERNAL_SERVER_ERROR: {
            "model": Message,
            "description": "Internal Server Error",
        },
    },
    summary="Get Item",
    description="Get item details for a product",
)
async def read_item(params: dict = Depends(extended_common_parameters)):
    print(params)
    return ItemOut(
        name=str(params["item_id"]),
        price=100,
        description=params["q"],
        created_at=datetime.now(),
    )

# GET endpoint to retrieve a list of items
@app.get(
    "/items_list/{item_id}",
    dependencies=[Depends(extended_common_parameters)],
    response_model=List[ItemOut],
)
async def read_item_list(params: dict = Depends(extended_common_parameters)):
    return [
        ItemOut(
            name=str(params["item_id"]),
            price=100,
            description=params["q"],
            created_at=datetime.now(),
        )
    ]
