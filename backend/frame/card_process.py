from fastapi import HTTPException
from frame import card_store,sample_store
from frame.fixtures import measure
from frame.lots import writable

def add(cx,body):
    sample=sample_store.one(cx,body.sample)
    lot=writable(cx,sample["lot"])
    if cx.execute("SELECT 1 FROM flex_cards WHERE sample=%s AND stage='active'",(body.sample,)).fetchone():
        raise HTTPException(409,"取样已有有效检测，复测前须排除原卡")
    return card_store.record(cx,body,measure(cx,lot,body))

def exclude(cx,card,body):
    item=card_store.detail(cx,card)
    writable(cx,sample_store.one(cx,item["sample"])["lot"])
    return card_store.remove(cx,card,body.note)
