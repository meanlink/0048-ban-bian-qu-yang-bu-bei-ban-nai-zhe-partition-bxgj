from fastapi import HTTPException

def cards(cx,lot):
    return cx.execute("""
      SELECT f.*,s.zone,s.sheet FROM flex_cards f JOIN backing_samples s ON s.code=f.sample
      WHERE s.lot=%s ORDER BY s.zone,s.sheet,f.id
    """,(lot,)).fetchall()

def record(cx,body,normalized):
    return cx.execute("""
      INSERT INTO flex_cards(sample,fixture,observed_on,deflection,normalized)
      VALUES (%s,%s,%s,%s,%s) RETURNING *
    """,(body.sample,body.fixture,body.observed_on,body.deflection,normalized)).fetchone()

def detail(cx,card):
    row=cx.execute("SELECT * FROM flex_cards WHERE id=%s",(card,)).fetchone()
    if row is None: raise HTTPException(404,"检测卡不存在")
    return row

def remove(cx,id,note):
    row=cx.execute("""
      UPDATE flex_cards SET stage='excluded',exclusion=%s WHERE id=%s AND stage='active' RETURNING *
    """,(note,id)).fetchone()
    if row is None: raise HTTPException(409,"检测卡已经排除")
    return row
