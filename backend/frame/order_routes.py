from fastapi import APIRouter,Depends
from core import db,require
from frame.orders import issue,preview
from frame.request import Cut

router=APIRouter(prefix="/api/frame/lots")

@router.get("/{code}/distribution")
def distribution(code:str,_=Depends(require())):
    with db() as cx: return preview(cx,code)

@router.post("/{code}/issue",status_code=201)
def release(code:str,body:Cut,user=Depends(require("reviewer"))):
    with db() as cx: return issue(cx,code,body,user["email"])
