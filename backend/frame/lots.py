from fastapi import HTTPException

def inventory(cx):
    return cx.execute("SELECT * FROM board_lots ORDER BY code").fetchall()

def look_up(cx,code,lock=False):
    row=cx.execute("SELECT * FROM board_lots WHERE code=%s"+(" FOR UPDATE" if lock else ""),(code,)).fetchone()
    if row is None:
        raise HTTPException(404,"背板批号未找到")
    return row

def active_order(cx,code,lock=False):
    tail=" FOR UPDATE" if lock else ""
    return cx.execute(
        f"SELECT * FROM frame_cut_orders WHERE lot=%s AND status='active'{tail}",(code,)
    ).fetchone()

def writable(cx,code):
    row=look_up(cx,code,True)
    if active_order(cx,row["code"]):
        raise HTTPException(409,"批次已有有效裁切单，检测留档已冻结；如需复测请先停用旧单")
    return row
