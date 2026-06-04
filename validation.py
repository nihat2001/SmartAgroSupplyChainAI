from sqlalchemy import Column, String, Integer
from pydantic import BaseModel, Field
from database import Base

class Inventory(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True)
    product_name = Column(String)
    quantity = Column(Integer)

class Shipment(Base):
    __tablename__ = "shipments"
    id = Column(Integer, primary_key=True)
    product_name = Column(String)
    quantity = Column(Integer)
    destination = Column(String) 
    status = Column(String, default="In Transit") 

class InventorySchema(BaseModel):
    product_name: str
    quantity: int = Field(gt=0)

class ShipmentSchema(BaseModel):
    product_name: str
    quantity: int = Field(gt=0)
    destination: str