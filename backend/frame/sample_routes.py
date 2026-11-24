from fastapi import APIRouter,Depends
from core import db,require
from frame.fixtures import available
from frame.lots import inventory,writable
from frame.request import Sample
from frame.sample_store import put,samples

router=APIRouter(prefix="/api/frame")

@router.get("/lots")
def lots(_=Depends(require())):
    with db() as cx: return inventory(cx)

@router.get("/fixtures")
def fixtures(_=Depends(require())):
    with db() as cx: return available(cx)

@router.get("/lots/{code}/samples")
def taken(code:str,_=Depends(require())):
    with db() as cx: return samples(cx,code)

@router.post("/samples",status_code=201)
def add(body:Sample,_=Depends(require("operator"))):
    with db() as cx:
        writable(cx,body.lot)
        return put(cx,body)
