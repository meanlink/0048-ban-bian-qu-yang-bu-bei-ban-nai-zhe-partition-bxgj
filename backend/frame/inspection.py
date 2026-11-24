from collections import defaultdict
from frame.card_store import cards
from frame.percentiles import describe
from frame.sample_store import samples

def evaluate(cx,lot):
    all_samples=samples(cx,lot["code"])
    registered=defaultdict(list)
    for entry in cards(cx,lot["code"]):
        if entry["stage"]=="active":
            registered[entry["zone"]].append(float(entry["normalized"]))
    zones={name:describe(registered[name]) for name in ("bound","heart")}
    incomplete=any(zone["n"]<3 for zone in zones.values()) or any(row["active_card"] is None for row in all_samples)
    state="ready"
    if incomplete: state="missing"
    elif any(row["p90"]>float(lot["max_deflection"]) or row["mad"]>float(lot["max_spread"]) for row in zones.values()):
        state="review"
    return {"lot":lot["code"],"status":state,"zones":zones,
            "p90_limit":float(lot["max_deflection"]),"mad_limit":float(lot["max_spread"])}
