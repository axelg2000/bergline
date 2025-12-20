from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

class Item(BaseModel):
    text : str = None
    is_done : bool = False


app = FastAPI()

items = []



@app.get("/")
def root():
    return {"message": "Hello, World!"}


@app.post("/items")
def create_item(item: Item):
    items.append(item)
    return items[-1]

@app.get("/items/{item_id}", response_model=Item)
def read_item(item_id: int):
    if item_id < len(items):
        return items[item_id]
    else:
        raise HTTPException(status_code=404, detail=f"Item not found: {item_id}")

@app.get("/items")
def list_item(limit: int = 10):
    return items[:limit]
