from fastapi import HTTPException

def available(cx):
    return cx.execute("SELECT * FROM flex_fixtures ORDER BY code").fetchall()

def measure(cx,lot,body):
    jig=cx.execute("SELECT * FROM flex_fixtures WHERE code=%s",(body.fixture,)).fetchone()
    if not jig:
        raise HTTPException(404,"夹具不存在")
    if body.observed_on>jig["cal_due"]:
        raise HTTPException(409,"夹具校验已经过期")
    if lot["panel_mm"]!=jig["panel_mm"]:
        raise HTTPException(409,"夹具与背板厚度规格不匹配")
    value=body.deflection-jig["offset_mm"]
    if value<0:
        raise HTTPException(409,"校正后挠度为负，需检查零位")
    return value
