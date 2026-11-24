from fastapi import APIRouter
from frame import card_routes,order_routes,sample_routes
from frame.demo import seed
from frame.worker_output import batch_sheet

router=APIRouter()
for part in (sample_routes,card_routes,order_routes):
    router.include_router(part.router)

def run_job(cx,kind,payload):
    if kind=="frame-cut-sheet": return batch_sheet(cx,payload)
    raise ValueError(f"Unknown frame task {kind}")
