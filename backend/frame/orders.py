from fastapi import HTTPException
from psycopg.types.json import Jsonb

from core import enqueue
from frame.inspection import evaluate
from frame.lots import active_order, look_up
from frame.preview_token import assert_fresh, issue_token

def history(cx,code):
    return cx.execute("""
      SELECT o.*,j.status AS job_status,j.error AS job_error
      FROM frame_cut_orders o JOIN app_jobs j ON j.id=o.job
      WHERE o.lot=%s ORDER BY o.created_at DESC,o.id DESC
    """,(code,)).fetchall()

def order(cx,code):
    return active_order(cx,code)

def preview(cx,code):
    lot=look_up(cx,code,True)
    current=active_order(cx,code)
    if current:
        report=current["inspection"]
    else:
        report=evaluate(cx,lot)
    return {"report":report,"order":current,"orders":history(cx,code),
            "preview_token":issue_token(report)}

def void(cx,code,reason,operator):
    look_up(cx,code,True)
    current=active_order(cx,code,lock=True)
    if current is None:
        raise HTTPException(409,"该批次没有可停用的有效裁切单")
    cx.execute("""
      UPDATE frame_cut_orders
      SET status='voided',void_reason=%s,voided_at=now(),voided_by=%s
      WHERE id=%s
    """,(reason,operator,current["id"]))
    # A queued batch-sheet credential must never reach the cutting desk.
    cx.execute("""
      UPDATE app_jobs SET status='failed',
        error='裁切单已停用，批签凭据作废',finished_at=now()
      WHERE id=%s AND status IN ('queued','running')
    """,(current["job"],))
    return cx.execute("SELECT * FROM frame_cut_orders WHERE id=%s",(current["id"],)).fetchone()

def issue(cx,code,body,operator):
    lot=look_up(cx,code,True)
    # Same request key means the reviewer retried the same confirmation:
    # return the stored order instead of cutting another sheet. Checked
    # before the freeze so a retried request still gets the original answer.
    repeat=cx.execute(
        "SELECT * FROM frame_cut_orders WHERE lot=%s AND request_key=%s",
        (code,body.request_key),
    ).fetchone()
    if repeat is not None:
        return repeat
    if active_order(cx,code):
        raise HTTPException(409,"批次已有有效裁切单，检测留档已冻结；如需复测请先停用旧单")
    report=evaluate(cx,lot)
    assert_fresh(report,body.preview_token)
    if report["status"]=="missing":
        raise HTTPException(409,"两区各至少三片，且每张取样卡都要有有效检测")
    if report["status"]=="review":
        raise HTTPException(409,"分区挠度 P90 或 MAD 超线，复测达标后才能换发")
    job=enqueue(cx,"frame-cut-sheet",{"lot":code})
    return cx.execute("""
      INSERT INTO frame_cut_orders(lot,kept_width,issuer,inspection,request_key,job)
      VALUES (%s,%s,%s,%s,%s,%s) RETURNING *
    """,(code,body.width,operator,Jsonb(report),body.request_key,job)).fetchone()
