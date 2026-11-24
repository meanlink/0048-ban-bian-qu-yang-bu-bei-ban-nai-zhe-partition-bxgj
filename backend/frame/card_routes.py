from fastapi import APIRouter,Depends
from core import db,require
from frame.card_process import add,exclude
from frame.card_store import cards
from frame.request import Card,Exclusion

router=APIRouter(prefix="/api/frame")

@router.get("/lots/{code}/cards")
def archive(code:str,_=Depends(require())):
    with db() as cx: return cards(cx,code)

@router.post("/cards",status_code=201)
def new_card(body:Card,_=Depends(require("operator"))):
    with db() as cx: return add(cx,body)

@router.put("/cards/{id}/exclude")
def discard(id:int,body:Exclusion,_=Depends(require("reviewer"))):
    with db() as cx: return exclude(cx,id,body)
