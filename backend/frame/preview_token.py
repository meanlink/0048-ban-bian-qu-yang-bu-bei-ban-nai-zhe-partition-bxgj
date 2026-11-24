"""HMAC fingerprint of the inspection state backing an issue preview.

The issuance page computes a report from the *active* cards and receives this
token together with the preview. When the reviewer later confirms the cut
order, the token is recomputed: excluding a card, registering a retest or any
other change to the active cards makes the old preview stale and the request
is rejected.
"""
import hashlib
import hmac
import json

from fastapi import HTTPException

from core import SECRET

def _message(report):
    return json.dumps(
        {"lot":report["lot"],"status":report["status"],
         "zones":{zone:{"n":row["n"],"values":row["values"]}
                  for zone,row in sorted(report["zones"].items())}},
        ensure_ascii=False,separators=(",",":"),sort_keys=True,
    )

def issue_token(report):
    digest=hmac.new(SECRET.encode(),_message(report).encode(),hashlib.sha256)
    return digest.hexdigest()[:32]

def assert_fresh(report,token):
    if not hmac.compare_digest(issue_token(report),token or ""):
        raise HTTPException(409,"签发依据已过期：预览后检测数据发生变化，请刷新复核后重新换发")
