from fastapi import HTTPException
from psycopg.types.json import Jsonb
from core import enqueue
from frame.inspection import evaluate
from frame.lots import look_up,writable

def order(cx,code):
    return cx.execute("SELECT * FROM frame_cut_orders WHERE lot=%s",(code,)).fetchone()

def preview(cx,code):
    lot=look_up(cx,code,True)
    existing=order(cx,code)
    return {"report":existing["inspection"] if existing else evaluate(cx,lot),"order":existing}

def issue(cx,code,body,operator):
    lot=writable(cx,code)
    report=evaluate(cx,lot)
    if report["status"]=="missing":
        raise HTTPException(409,"两区各至少三片，且每张取样卡都要有有效检测")
    if report["status"]=="review":
        raise HTTPException(409,"分区挠度 P90 或 MAD 超线，需复测后签发")
    job=enqueue(cx,"frame-cut-sheet",{"lot":code})
    return cx.execute("""
      INSERT INTO frame_cut_orders VALUES (%s,%s,%s,%s,%s) RETURNING *
    """,(code,body.width,operator,Jsonb(report),job)).fetchone()
