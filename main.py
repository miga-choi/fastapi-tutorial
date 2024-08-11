from enum import Enum
from fastapi import FastAPI
from pydantic import BaseModel


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


# Predefined values
class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


app = FastAPI()

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


@app.post("/items/")
async def create_item(item: Item):
    item_dict = item.model_dump()
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict


@app.get("/")
async def root():
    return {"message": "Hello World"}


# Optional parameters
@app.get("/items/optional/{item_id}")
async def read_item(item_id: str, q: str | None = None):
    if q:
        return {"item_id": item_id, "q": q}
    return {"item_id": item_id}


# Query parameter type conversion
@app.get("/items/conversion/{item_id}")
async def read_item(item_id: str, q: str | None = None, short: bool = False):
    item = {"item_id": item_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item


# Required query parameters
@app.get("/items/required/{item_id}")
async def read_user_item(item_id: str, needy: str):
    item = {"item_id": item_id, "needy": needy}
    return item


# Required + Default value + Optional
@app.get("/items/multiple/{item_id}")
async def read_user_item(
        item_id: str, needy: str, skip: int = 0, limit: int | None = None
):
    item = {"item_id": item_id, "needy": needy, "skip": skip, "limit": limit}
    return item


# Path parameters with types
@app.get("/items/types/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}


# Path Parameters
@app.get("/items/{item_id}")
async def read_item(item_id):
    return {"item_id": item_id}


# Query Parameters
@app.get("/items/")
async def read_item(skip: int = 0, limit: int = 10):
    return fake_items_db[skip: skip + limit]


# Multiple path and query parameters
@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(
        user_id: int, item_id: str, q: str | None = None, short: bool = False
):
    item = {"item_id": item_id, "owner_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item


# Order matters 1-1
@app.get("/users/me")
async def read_user_me():
    return {"user_id": "the current user"}


# Order matters 1-2
@app.get("/users/{user_id}")
async def read_user(user_id: str):
    return {"user_id": user_id}


# Order matters 2-1
@app.get("/users")
async def read_users():
    return ["Rick", "Morty"]


# Order matters 2-2
@app.get("/users")
async def read_users2():
    return ["Bean", "Elfo"]


# Declare a path parameter + Working with Python enumerations
@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}


# Path parameters containing paths
@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}
