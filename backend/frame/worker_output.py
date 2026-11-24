from fastapi import HTTPException
from frame.orders import order

def batch_sheet(cx,payload):
    packet=order(cx,payload["lot"])
    if packet is None:
        raise HTTPException(409,"裁切单已停用，批签凭据作废，裁切桌不接收旧单")
    zones=packet["inspection"]["zones"]
    maximum=max(value["p90"] for value in zones.values())
    return {"lot":packet["lot"],"cut_width_mm":packet["kept_width"],"max_zone_p90_mm":maximum,
            "tested_pieces":sum(zone["n"] for zone in zones.values())}
