from sqlalchemy.ext.asyncio import AsyncSession
from validation import Inventory, Shipment
from data_clean import clean_task
from sqlalchemy import select
from database import cache

async def add_inventory_tool(product_name: str, quantity: int, db: AsyncSession):
    """Adds new product or increases existing stock."""
    
    clean_product_name = clean_task(product_name)
    
    stmt = select(Inventory).where(Inventory.product_name == clean_product_name)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    
    if item:
        item.quantity += quantity
    else:
        new_item = Inventory(product_name=clean_product_name, quantity=quantity)
        db.add(new_item)
    
    await db.commit()
    await cache.delete("inventory_list")
    return {"status": "success", "message": f"{quantity} tons {clean_product_name} added to stock."}

async def log_shipment_tool(product_name: str, quantity: int, destination: str, db: AsyncSession):
    """Removes product from stock and creates a new shipment."""
    
    clean_product_name = clean_task(product_name)
    clean_destination = clean_task(destination)

    stmt = select(Inventory).where(Inventory.product_name == clean_product_name)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    
    if item and item.quantity >= quantity:
        item.quantity -= quantity
        
        new_shipment = Shipment(
            product_name=clean_product_name, 
            quantity=quantity, 
            destination=clean_destination
        )
        db.add(new_shipment)
        await db.commit()
        await cache.delete("inventory_list")
        await cache.delete("shipments_list") 
        return {"status": "success", "message": f"{quantity} tons {clean_product_name} sent to {clean_destination}."}
    
    return {"status": "error", "message": "Stock shortage or product couldn't found."}

async def check_inventory_tool(db: AsyncSession):
    """Checks the status of the inventory."""
    result = await db.execute(select(Inventory))
    items = result.scalars().all()
    return [
        {"id": i.id, "product": i.product_name, "quantity": i.quantity}
        for i in items
    ]

async def get_shipments_tool(db: AsyncSession):
    """Returns all shipments."""
    result = await db.execute(select(Shipment))
    items = result.scalars().all()
    return [
        {
            "id": s.id,
            "product": s.product_name,
            "quantity": s.quantity,
            "destination": s.destination,
            "status": s.status
        }
        for s in items
    ]

async def mark_shipment_delivered_tool(shipment_id: int, db: AsyncSession):
    stmt = select(Shipment).where(Shipment.id == shipment_id)
    result = await db.execute(stmt)
    shipment = result.scalar_one_or_none()
    if not shipment:
        return {"status": "error", "message": "Shipment not found."}
    if shipment.status == "Delivered":
        return {"status": "error", "message": "Already delivered."}
    shipment.status = "Delivered"
    await db.commit()
    await cache.delete("shipments_list")
    return {"status": "success", "message": f"Shipment #{shipment_id} marked as Delivered."}