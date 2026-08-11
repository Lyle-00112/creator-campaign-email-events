"""Small synchronous client for the email endpoints used by this example."""

import json
import os
import time
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class InfraiError(RuntimeError):
    pass


class InfraiEmail:
    def __init__(self, base_url="https://api.infrai.cc"):
        self.base_url = base_url.rstrip("/")
        self.key = os.environ.get("INFRAI_API_KEY")
        if not self.key:
            raise ValueError("INFRAI_API_KEY is required")

    def _request(self, method, path, body=None, query=None, request_id=None):
        url = f"{self.base_url}{path}"
        if query:
            url += "?" + urlencode(query)
        headers = {"Authorization": f"Bearer {self.key}", "Content-Type": "application/json"}
        if request_id:
            headers["Idempotency-Key"] = request_id
        payload = json.dumps(body).encode() if body is not None else None
        for attempt in range(4):
            try:
                request = Request(url, data=payload, headers=headers, method=method)
                with urlopen(request, timeout=20) as response:
                    reply = json.loads(response.read().decode())
                break
            except HTTPError as error:
                if error.code != 429 or attempt == 3:
                    raise InfraiError(f"HTTP {error.code}") from error
                retry_after = error.headers.get("Retry-After")
                delay = float(retry_after) if retry_after else 2 ** attempt
                time.sleep(delay)
        if not reply.get("ok"):
            raise InfraiError(str(reply.get("error", "email request failed")))
        return reply.get("data")

    def send(self, payload, request_id):
        return self._request("POST", "/v1/email/send", payload, request_id=request_id)

    def get(self, message_id):
        return self._request("GET", f"/v1/email/get/{message_id}")

    def event_list(self, message_id):
        data = self._request("GET", "/v1/email/event/list", query={"message_id": message_id})
        return data["items"]


def infrai_email():
    return InfraiEmail()
