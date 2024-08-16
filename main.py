from enum import Enum
from fastapi import Body, FastAPI, Path, Query
from pydantic import BaseModel, Field, HttpUrl
from typing import Annotated, List


# Nested Models
class Image(BaseModel):
    url: HttpUrl
    name: str


# Body - Fields
# Body - Nested Models
class Item(BaseModel):
    name: str
    description: str | None = Field(
        default=None, title="The description of the item", max_length=300
    )
    price: float = Field(gt=0, description="The price must be greater than zero")
    tax: float | None = None
    tags: list[str] = set()
    images: list[Image] | None = None


# Body - Nested Models
class Offer(BaseModel):
    name: str
    description: str | None = None
    price: float
    items: list[Item]


class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


class User(BaseModel):
    username: str
    full_name: str | None = None


app = FastAPI()

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


# Bodies of arbitrary dict
@app.post("/index-weights/")
async def create_index_weights(weights: dict[int, float]):
    return weights


# Bodies of pure lists
@app.post("/images/multiple/")
async def create_multiple_images(images: list[Image]):
    return images


# Embed a single body parameter
@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Annotated[Item, Body(embed=True)]):
    results = {"item_id": item_id, "item": item}
    return results


# Multiple body params and query
@app.put("/items/{item_id}")
async def update_item(
        *,
        item_id: int,
        item: Item,
        user: User,
        importance: Annotated[int, Body(gt=0)],
        q: str | None = None,
):
    results = {"item_id": item_id, "item": item, "user": user, "importance": importance}
    if q:
        results.update({"q": q})
    return results


# Singular values in body
@app.put("/items/{item_id}")
async def update_item(
        item_id: int, item: Item, user: User, importance: Annotated[int, Body()]
):
    results = {"item_id": item_id, "item": item, "user": user, "importance": importance}
    return results


# Body - Multiple Parameters
# Mix Path, Query and body parameters
@app.put("/items/{item_id}")
async def update_item(
        item_id: Annotated[int, Path(title="The ID of the item to get", ge=0, le=1000)],
        q: str | None = None,
        item: Item | None = None,
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    if item:
        results.update({"item": item})
    return results


# Number validations: floats, greater than and less than
@app.get("/items/{item_id}")
async def read_items(
        *,
        item_id: Annotated[int, Path(title="The ID of the item to get", ge=0, le=1000)],
        q: str,
        size: Annotated[float, Query(gt=0, lt=10.5)],
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results


# Number validations: greater than and less than or equal
@app.get("/items/{item_id}")
async def read_items(
        item_id: Annotated[int, Path(title="The ID of the item to get", gt=0, le=1000)],
        q: str,
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results


# Number validations: greater than or equal
@app.get("/items/{item_id}")
async def read_items(
        item_id: Annotated[int, Path(title="The ID of the item to get", ge=1)], q: str
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results


# Order the parameters as you need, tricks
@app.get("/items/{item_id}")
async def read_items(*, item_id: int = Path(title="The ID of the item to get"), q: str):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results


# Path Parameters and Numeric Validations
@app.get("/items/{item_id}")
async def read_items(
        item_id: Annotated[int, Path(title="The ID of the item to get")],
        q: Annotated[str | None, Query(alias="item-query")] = None,
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results


# Exclude from OpenAPI
@app.get("/items/")
async def read_items(
        hidden_query: Annotated[str | None, Query(include_in_schema=False)] = None,
):
    if hidden_query:
        return {"hidden_query": hidden_query}
    else:
        return {"hidden_query": "Not found"}


# Deprecating parameters
@app.get("/items/")
async def read_items(
        q: Annotated[
            str | None,
            Query(
                alias="item-query",
                title="Query string",
                description="Query string for the items to search in the database that have a good match",
                min_length=3,
                max_length=50,
                pattern="^fixedquery$",
                deprecated=True,
            ),
        ] = None,
):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


# Alias parameters
# try:
#   http://127.0.0.1:8000/items/?item-query=foobaritems
@app.get("/items/")
async def read_items(q: Annotated[str | None, Query(alias="item-query")] = None):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


# Declare more metadata
@app.get("/items/")
async def read_items(
        q: Annotated[
            str | None,
            Query(
                title="Query string",
                description="Query string for the items to search in the database that have a good match",
                min_length=3,
            ),
        ] = None,
):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


# Query parameter list / multiple values with defaults
# try:
#   http://localhost:8000/items/
@app.get("/items/")
async def read_items(q: Annotated[List[str], Query()] = ["foo", "bar"]):
    query_items = {"q": q}
    return query_items


# Query parameter list / multiple values
# try:
#   http://localhost:8000/items/?q=foo&q=bar
@app.get("/items/")
async def read_items(q: Annotated[list[str] | None, Query()] = None):
    query_items = {"q": q}
    return query_items


# Required with None
@app.get("/items/")
async def read_items(q: Annotated[str | None, Query(min_length=3)] = ...):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


# Required with Ellipsis (...)
@app.get("/items/")
async def read_items(q: Annotated[str, Query(min_length=3)] = ...):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


# Make it required
@app.get("/items/")
async def read_items(q: Annotated[str, Query(min_length=3)]):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


# Default values
@app.get("/items/")
async def read_items(q: Annotated[str, Query(min_length=3)] = "fixedquery"):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


# Add regular expressions
@app.get("/items/")
async def read_items(
        q: Annotated[
            str | None, Query(min_length=3, max_length=50, pattern="^fixedquery$")
        ] = None,
):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


# Add more validations
@app.get("/items/")
async def read_items(
        q: Annotated[str | None, Query(min_length=3, max_length=50)] = None,
):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


# Alternative (old) Query as the default value
@app.get("/items/")
async def read_items(q: str | None = Query(default=None, max_length=50)):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


# Query Parameters and String Validations
@app.get("/items/")
async def read_items(q: Annotated[str | None, Query(max_length=50)] = None):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


# Request body + path + query parameters
@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item, q: str | None = None):
    result = {"item_id": item_id, **item.model_dump()}
    if q:
        result.update({"q": q})
    return result


# Request body + path parameters
@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    return {"item_id": item_id, **item.model_dump()}


# Use the model
@app.post("/items/")
async def create_item(item: Item):
    item_dict = item.model_dump()
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict


# Request Body
@app.post("/items/")
async def create_item(item: Item):
    return item


# Required parameters + Optional parameters
@app.get("/items/{item_id}")
async def read_user_item(
        item_id: str, needy: str, skip: int = 0, limit: int | None = None
):
    item = {"item_id": item_id, "needy": needy, "skip": skip, "limit": limit}
    return item


# Required query parameters
# try:
#   http://127.0.0.1:8000/items/foo-item
#   http://127.0.0.1:8000/items/foo-item?needy=sooooneedy
@app.get("/items/{item_id}")
async def read_user_item(item_id: str, needy: str):
    item = {"item_id": item_id, "needy": needy}
    return item


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


# Query parameter type conversion
# try:
#   http://127.0.0.1:8000/items/foo?short=1
#   http://127.0.0.1:8000/items/foo?short=True
#   http://127.0.0.1:8000/items/foo?short=true
#   http://127.0.0.1:8000/items/foo?short=on
#   http://127.0.0.1:8000/items/foo?short=yes
@app.get("/items/{item_id}")
async def read_item(item_id: str, q: str | None = None, short: bool = False):
    item = {"item_id": item_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item


# Optional parameters
@app.get("/items/{item_id}")
async def read_item(item_id: str, q: str | None = None):
    if q:
        return {"item_id": item_id, "q": q}
    return {"item_id": item_id}


# Query Parameters
# try:
#   http://127.0.0.1:8000/items/
#   http://127.0.0.1:8000/items/?skip=0&limit=10
#   http://127.0.0.1:8000/items/?skip=20
@app.get("/items/")
async def read_item(skip: int = 0, limit: int = 10):
    return fake_items_db[skip: skip + limit]


# Path parameters containing paths
@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}


# Predefined values
@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}


# Order matters 1
@app.get("/users/me")
async def read_user_me():
    return {"user_id": "the current user"}


# Order matters 2
@app.get("/users/{user_id}")
async def read_user(user_id: str):
    return {"user_id": user_id}


# Path Parameters with types
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}


# Path Parameters
@app.get("/items/{item_id}")
async def read_item(item_id):
    return {"item_id": item_id}


@app.get("/")
async def root():
    return {"message": "Hello World"}
