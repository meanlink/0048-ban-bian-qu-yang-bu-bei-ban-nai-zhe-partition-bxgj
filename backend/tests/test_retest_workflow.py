"""End-to-end rules for the retest / re-issue workflow.

Runs against a real PostgreSQL (business_test) and Redis, using FastAPI's
TestClient plus the actual worker processing loop.
"""
import os

os.environ.setdefault("DATABASE_URL", "postgresql://app@/business_test?host=/tmp&port=17942")
os.environ.setdefault("REDIS_URL", "redis://127.0.0.1:16379/15")
os.environ.setdefault("JWT_SECRET", "test-secret-381613")
os.environ.setdefault("SEED_DEMO", "true")
os.environ.setdefault("DEMO_PASSWORD", "Demo2026!")

import pytest
from fastapi.testclient import TestClient

import domain
import worker
from app import app
from core import db

LOT = "FLEX-17"


@pytest.fixture()
def client():
    with db() as cx:
        cx.execute("""
            DROP TABLE IF EXISTS frame_cut_orders,flex_cards,backing_samples,
                flex_fixtures,board_lots,app_jobs,app_users CASCADE
        """)
    with TestClient(app) as live:
        yield live


def login(client, role):
    response = client.post("/api/auth/login",
                           json={"email": f"{role}@demo.local", "password": "Demo2026!"})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def distribution(client, headers):
    return client.get(f"/api/frame/lots/{LOT}/distribution", headers=headers).json()


def make_ready(client, headers, operator):
    """Exclude the off-line S-13 card and register the retest so the lot passes."""
    cards = client.get(f"/api/frame/lots/{LOT}/cards", headers=headers).json()
    bad = next(card for card in cards if card["sample"] == "S-13")
    answer = client.put(f"/api/frame/cards/{bad['id']}/exclude",
                        headers=headers, json={"note": "样片压线偏移，夹持错误排除"})
    assert answer.status_code == 200
    answer = client.post("/api/frame/cards", headers=operator, json={
        "sample": "S-13", "fixture": "JIG-4", "observed_on": "2026-11-19",
        "deflection": 2.6,
    })
    assert answer.status_code == 201
    assert float(answer.json()["normalized"]) == pytest.approx(2.4)
    return distribution(client, headers)


def run_worker_once():
    with db() as cx:
        assert worker.process(cx)


def test_review_blocks_issue_until_retest_passes(client):
    reviewer = login(client, "reviewer")
    operator = login(client, "operator")
    preview = distribution(client, reviewer)
    assert preview["order"] is None
    assert preview["report"]["status"] == "review"
    # Over-limit report cannot be issued even with a fresh preview token.
    refused = client.post(f"/api/frame/lots/{LOT}/issue", headers=reviewer, json={
        "width": 220, "request_key": "key-0001-first", "preview_token": preview["preview_token"],
    })
    assert refused.status_code == 409
    ready = make_ready(client, reviewer, operator)
    assert ready["report"]["status"] == "ready"


def test_issue_freezes_lot_and_queues_batch_sheet(client):
    reviewer = login(client, "reviewer")
    operator = login(client, "operator")
    make_ready(client, reviewer, operator)
    preview = distribution(client, reviewer)
    answer = client.post(f"/api/frame/lots/{LOT}/issue", headers=reviewer, json={
        "width": 220, "request_key": "key-0002-issue", "preview_token": preview["preview_token"],
    })
    assert answer.status_code == 201
    first = answer.json()
    assert first["status"] == "active"
    with db() as cx:
        job = cx.execute("SELECT * FROM app_jobs WHERE id=%s", (first["job"],)).fetchone()
    assert job["status"] == "queued"
    # Frozen: no more samples or cards while an active cut order exists.
    blocked_sample = client.post("/api/frame/samples", headers=operator, json={
        "code": "S-99", "lot": LOT, "zone": "bound", "sheet": "整板 99",
    })
    assert blocked_sample.status_code == 409
    blocked_card = client.post("/api/frame/cards", headers=operator, json={
        "sample": "S-11", "fixture": "JIG-4", "observed_on": "2026-11-19", "deflection": 2.1,
    })
    assert blocked_card.status_code == 409
    # Cutting desk receives the credential built from the snapshot.
    run_worker_once()
    with db() as cx:
        done = cx.execute("SELECT * FROM app_jobs WHERE id=%s", (first["job"],)).fetchone()
    assert done["status"] == "done"
    assert done["result"]["cut_width_mm"] == 220
    assert done["result"]["tested_pieces"] == 6


def test_void_reopens_lot_and_cancels_queued_credential(client):
    reviewer = login(client, "reviewer")
    make_ready(client, reviewer, login(client, "operator"))
    preview = distribution(client, reviewer)
    issued = client.post(f"/api/frame/lots/{LOT}/issue", headers=reviewer, json={
        "width": 220, "request_key": "key-0003-void", "preview_token": preview["preview_token"],
    }).json()
    # Voiding without a reason is rejected by the request model.
    assert client.post(f"/api/frame/lots/{LOT}/void", headers=reviewer,
                       json={"reason": "x"}).status_code == 422
    answer = client.post(f"/api/frame/lots/{LOT}/void", headers=reviewer,
                         json={"reason": "复检发现样片夹偏，停用旧单复测"})
    assert answer.status_code == 200
    voided = answer.json()
    assert voided["status"] == "voided"
    assert voided["void_reason"].startswith("复检发现样片夹偏")
    with db() as cx:
        job = cx.execute("SELECT * FROM app_jobs WHERE id=%s", (issued["job"],)).fetchone()
        active = cx.execute(
            "SELECT count(*) AS n FROM frame_cut_orders WHERE lot=%s AND status='active'",
            (LOT,)).fetchone()["n"]
    # The queued batch-sheet credential never reaches the cutting desk.
    assert job["status"] == "failed"
    assert "停用" in job["error"]
    assert active == 0
    # Lot is writable again: operator can register a retest card.
    cards = client.get(f"/api/frame/lots/{LOT}/cards", headers=reviewer).json()
    current = next(card for card in cards if card["sample"] == "S-13" and card["stage"] == "active")
    excluded = client.put(f"/api/frame/cards/{current['id']}/exclude",
                          headers=reviewer, json={"note": "复测前再次排除压线样片"})
    assert excluded.status_code == 200
    retest = client.post("/api/frame/cards", headers=login(client, "operator"), json={
        "sample": "S-13", "fixture": "JIG-4", "observed_on": "2026-11-19", "deflection": 2.5,
    })
    assert retest.status_code == 201
    # Voiding twice has no active order to act on.
    again = client.post(f"/api/frame/lots/{LOT}/void", headers=reviewer,
                        json={"reason": "没有有效单可停用了"})
    assert again.status_code == 409


def test_stale_preview_is_rejected_then_fresh_reissue_succeeds(client):
    reviewer = login(client, "reviewer")
    operator = login(client, "operator")
    make_ready(client, reviewer, operator)
    old_preview = distribution(client, reviewer)
    # Issue, void, then change the inspection data.
    issued = client.post(f"/api/frame/lots/{LOT}/issue", headers=reviewer, json={
        "width": 220, "request_key": "key-0004-cycle-a", "preview_token": old_preview["preview_token"],
    }).json()
    client.post(f"/api/frame/lots/{LOT}/void", headers=reviewer,
                json={"reason": "样片夹偏停用，安排原批次复测"})
    cards = client.get(f"/api/frame/lots/{LOT}/cards", headers=reviewer).json()
    current = next(card for card in cards if card["sample"] == "S-13" and card["stage"] == "active")
    client.put(f"/api/frame/cards/{current['id']}/exclude",
               headers=reviewer, json={"note": "第二次排除压线原卡"})
    client.post("/api/frame/cards", headers=operator, json={
        "sample": "S-13", "fixture": "JIG-4", "observed_on": "2026-11-19", "deflection": 2.7,
    })
    # The token from the pre-change preview must be bounced back.
    stale = client.post(f"/api/frame/lots/{LOT}/issue", headers=reviewer, json={
        "width": 230, "request_key": "key-0004-cycle-b", "preview_token": old_preview["preview_token"],
    })
    assert stale.status_code == 409
    assert "过期" in stale.json()["detail"]
    fresh = distribution(client, reviewer)
    assert fresh["preview_token"] != old_preview["preview_token"]
    reissued = client.post(f"/api/frame/lots/{LOT}/issue", headers=reviewer, json={
        "width": 230, "request_key": "key-0004-cycle-c", "preview_token": fresh["preview_token"],
    })
    assert reissued.status_code == 201
    new_order = reissued.json()
    assert new_order["id"] != issued["id"]
    assert new_order["status"] == "active"
    assert new_order["kept_width"] == 230


def test_same_request_key_never_cuts_twice(client):
    reviewer = login(client, "reviewer")
    make_ready(client, reviewer, login(client, "operator"))
    token = distribution(client, reviewer)["preview_token"]
    payload = {"width": 220, "request_key": "key-0005-idempotent", "preview_token": token}
    first = client.post(f"/api/frame/lots/{LOT}/issue", headers=reviewer, json=payload)
    assert first.status_code == 201
    # Retried confirmation, even after the freeze is in place: same order back.
    retry = client.post(f"/api/frame/lots/{LOT}/issue", headers=reviewer, json=payload)
    assert retry.status_code == 201
    assert retry.json()["id"] == first.json()["id"]
    with db() as cx:
        count = cx.execute(
            "SELECT count(*) AS n FROM frame_cut_orders WHERE request_key=%s",
            ("key-0005-idempotent",)).fetchone()["n"]
    assert count == 1


def test_history_keeps_voided_order_and_inspection_snapshot(client):
    reviewer = login(client, "reviewer")
    make_ready(client, reviewer, login(client, "operator"))
    token = distribution(client, reviewer)["preview_token"]
    issued = client.post(f"/api/frame/lots/{LOT}/issue", headers=reviewer, json={
        "width": 220, "request_key": "key-0006-history", "preview_token": token,
    }).json()
    client.post(f"/api/frame/lots/{LOT}/void", headers=reviewer,
                json={"reason": "留档测试：停用旧裁切单"})
    view = distribution(client, reviewer)
    assert view["order"] is None
    records = view["orders"]
    assert len(records) == 1
    record = records[0]
    assert record["id"] == issued["id"]
    assert record["status"] == "voided"
    assert record["void_reason"] == "留档测试：停用旧裁切单"
    # Snapshot of the inspection at issue time stays attached to the old order.
    assert record["inspection"]["zones"]["bound"]["n"] == 3
    assert record["job_status"] == "failed"


def test_worker_refuses_credential_for_voided_order(client):
    reviewer = login(client, "reviewer")
    make_ready(client, reviewer, login(client, "operator"))
    token = distribution(client, reviewer)["preview_token"]
    issued = client.post(f"/api/frame/lots/{LOT}/issue", headers=reviewer, json={
        "width": 220, "request_key": "key-0007-worker", "preview_token": token,
    }).json()
    # Bypass the route's queue cancellation: mark the credential back to queued
    # after voiding, proving the worker itself still rejects the stale sheet.
    client.post(f"/api/frame/lots/{LOT}/void", headers=reviewer,
                json={"reason": "验证 worker 兜底停用单"})
    with db() as cx:
        cx.execute("UPDATE app_jobs SET status='queued',error=NULL,finished_at=NULL WHERE id=%s",
                   (issued["job"],))
    run_worker_once()
    with db() as cx:
        job = cx.execute("SELECT * FROM app_jobs WHERE id=%s", (issued["job"],)).fetchone()
    assert job["status"] == "failed"
    assert "作废" in job["error"]


def test_roles_are_enforced(client):
    viewer = login(client, "viewer")
    operator = login(client, "operator")
    make_ready(client, login(client, "reviewer"), operator)
    token = distribution(client, viewer)["preview_token"]
    payload = {"width": 220, "request_key": "key-0008-rbac", "preview_token": token}
    assert client.post(f"/api/frame/lots/{LOT}/issue",
                       headers=operator, json=payload).status_code == 403
    assert client.post(f"/api/frame/lots/{LOT}/issue",
                       headers=viewer, json=payload).status_code == 403
    assert client.post(f"/api/frame/lots/{LOT}/void", headers=operator,
                       json={"reason": "操作员无权停用裁切单"}).status_code == 403
    # Read access still works for every role.
    assert distribution(client, viewer)["report"]["lot"] == LOT
