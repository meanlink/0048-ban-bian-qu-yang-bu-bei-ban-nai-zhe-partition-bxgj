from fastapi import HTTPException

def one(cx,code):
    found=cx.execute("SELECT * FROM backing_samples WHERE code=%s",(code,)).fetchone()
    if not found:
        raise HTTPException(404,"取样卡不存在")
    return found

def samples(cx,lot):
    return cx.execute("""
      SELECT s.*,f.id AS active_card FROM backing_samples s
      LEFT JOIN flex_cards f ON f.sample=s.code AND f.stage='active'
      WHERE s.lot=%s ORDER BY s.zone,s.sheet
    """,(lot,)).fetchall()

def put(cx,body):
    return cx.execute("""
      INSERT INTO backing_samples VALUES (%(code)s,%(lot)s,%(zone)s,%(sheet)s) RETURNING *
    """,body.model_dump()).fetchone()
