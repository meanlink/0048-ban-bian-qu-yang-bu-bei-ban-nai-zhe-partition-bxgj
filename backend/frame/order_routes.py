from fastapi import APIRouter,Depends
from core import db,require
from frame.orders import issue,preview,void
from frame.request import Cut,Void

router=APIRouter(prefix="/api/frame/lots")

@router.get("/{code}/distribution")
def distribution(code:str,_=Depends(require())):
    with db() as cx: return preview(cx,code)

@router.post("/{code}/issue",status_code=201)
def release(code:str,body:Cut,user=Depends(require("reviewer"))):
    with db() as cx: return issue(cx,code,body,user["email"])

@router.post("/{code}/void",status_code=200)
def deactivate(code:str,body:Void,user=Depends(require("reviewer"))):
    with db() as cx: return void(cx,code,body.reason,user["email"])
