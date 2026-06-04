from tools import log_shipment_tool, check_inventory_tool, add_inventory_tool, get_shipments_tool, mark_shipment_delivered_tool
from validation import ShipmentSchema, InventorySchema
from database import get_session, cache, Base, engine
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from dotenv import load_dotenv
from groq import AsyncGroq
import json
import os

load_dotenv()

client = AsyncGroq(api_key = os.getenv("API_KEY"))

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(lifespan = lifespan)

@app.post("/inventory/")
async def add_inventory(inventory: InventorySchema, db: AsyncSession = Depends(get_session)):
    return await add_inventory_tool(inventory.product_name, inventory.quantity, db)

@app.post("/shipment/")
async def create_shipment(shipment: ShipmentSchema, db: AsyncSession = Depends(get_session)):
    return await log_shipment_tool(shipment.product_name, shipment.quantity, shipment.destination, db)

@app.patch("/shipment/{shipment_id}/deliver")
async def deliver_shipment(shipment_id: int, db: AsyncSession = Depends(get_session)):
    return await mark_shipment_delivered_tool(shipment_id, db)

tools = [
    {
        "type": "function",
        "function": {
            "name": "log_shipment_tool",
            "description": "Removes product from warehouse and creates shipment.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {"type": "string"},
                    "quantity": {"type": "integer"},
                    "destination": {"type": "string"}
                },
                "required": ["product_name", "quantity", "destination"]
            }
        }
    },
    {
    "type": "function",
    "function": {
        "name": "get_shipments_tool",
        "description": "Returns all shipments from the database.",
        "parameters": {"type": "object", "properties": {}}
    }
    },
    {
        "type": "function",
        "function": {
            "name": "check_inventory_tool",
            "description": "Checks available products in the warehouse.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_inventory_tool",
            "description": "Adds new product to warehouse or increases existing stock.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {"type": "string"},
                    "quantity": {"type": "integer"}
                },
                "required": ["product_name", "quantity"]
            }
        }
    }
]

@app.post("/ai-task/")
async def ai_create_task(user_input: str, db: AsyncSession = Depends(get_session)):
    chat_completion = await client.chat.completions.create(
        messages=[{"role": "user", "content": user_input}],
        model="llama-3.3-70b-versatile",
        tools=tools,
        tool_choice="auto"
    )
    
    message = chat_completion.choices[0].message
    if message.tool_calls:
        tool_call = message.tool_calls[0]
        args = json.loads(tool_call.function.arguments)
        
        if tool_call.function.name == "log_shipment_tool":
            return await log_shipment_tool(args["product_name"], args["quantity"], args["destination"], db)
        elif tool_call.function.name == "check_inventory_tool":
            return await check_inventory_tool(db)
        elif tool_call.function.name == "add_inventory_tool":
            return await add_inventory_tool(args["product_name"], args["quantity"], db)
        elif tool_call.function.name == "get_shipments_tool":
            return await get_shipments_tool(db)
            
    return {"reply": message.content}

@app.get("/inventory/")
async def get_inventory(db: AsyncSession = Depends(get_session)):
    cached = await cache.get("inventory_list")
    if cached: return json.loads(cached)

    items = await check_inventory_tool(db)
    await cache.set("inventory_list", json.dumps(items), ex=3600)
    return items

@app.get("/shipments/")
async def get_shipments(db: AsyncSession = Depends(get_session)):
    cached = await cache.get("shipments_list")
    if cached: return json.loads(cached)
    
    items = await get_shipments_tool(db)
    await cache.set("shipments_list", json.dumps(items), ex=3600)
    return items