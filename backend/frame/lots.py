from fastapi import HTTPException

def inventory(cx):
    return cx.execute("SELECT * FROM board_lots ORDER BY code").fetchall()

def look_up(cx,code,lock=False):
    row=cx.execute("SELECT * FROM board_lots WHERE code=%s"+(" FOR UPDATE" if lock else ""),(code,)).fetchone()
    if row is None:
        raise HTTPException(404,"背板批号未找到")
    return row

def writable(cx,code):
    row=look_up(cx,code,True)
    if cx.execute("SELECT 1 FROM frame_cut_orders WHERE lot=%s",(code,)).fetchone():
        raise HTTPException(409,"批次已签发边框裁切，检测留档已冻结")
    return row
