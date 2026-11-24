from datetime import date
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, Field

Key=Field(pattern=r"^[A-Z0-9-]{3,24}$")

class Sample(BaseModel):
    code:str=Key
    lot:str=Key
    zone:Literal["bound","heart"]
    sheet:str=Field(min_length=2,max_length=24)

class Card(BaseModel):
    sample:str=Key
    fixture:str=Key
    observed_on:date
    deflection:Decimal=Field(ge=0,le=99,max_digits=4,decimal_places=2)

class Exclusion(BaseModel):
    note:str=Field(min_length=5,max_length=240)

class Cut(BaseModel):
    width:int=Field(ge=10,le=1500)
