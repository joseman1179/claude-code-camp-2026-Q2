"""HTTP client that POSTs a PromptBuilder payload to the LLM API.

Includes retry logic for transient network errors and retryable HTTP status codes.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
import ssl
import socket

from boukensha.errors import ApiError


class Client:
    RETRYABLE_STATUS_CODES = {408, 409, 429, 500, 502, 503, 504}
    MAX_RETRIES = 3
    BASE_RETRY_DELAY = 0.5

    def __init__(self, builder) -> None:
        self.builder = builder

    def call(self, max_output_tokens: int = 1024) -> dict:
        payload = self.builder.to_api_payload(max_output_tokens=max_output_tokens)
        data = json.dumps(payload).encode("utf-8")
        headers = self.builder.headers()

        request = urllib.request.Request(
            self.builder.url(),
            data=data,
            headers=headers,
            method="POST",
        )

        attempts = 0
        response = None

        while True:
            attempts += 1

            try:
                response = urllib.request.urlopen(request, timeout=30)
            except urllib.error.HTTPError as e:
                # HTTP errors with retryable status codes get another attempt.
                # Non-retryable codes (401, 403, etc.) fail immediately.
                if e.code in self.RETRYABLE_STATUS_CODES and attempts <= self.MAX_RETRIES:
                    time.sleep(self._retry_delay(attempts))
                    continue
                body = e.read().decode("utf-8", errors="replace")
                raise ApiError(
                    f"API request failed after {attempts} "
                    f"attempt{'s' if attempts != 1 else ''} ({e.code}): {body}"
                )
            except (
                urllib.error.URLError,
                socket.timeout,
                TimeoutError,
                ConnectionResetError,
                ConnectionRefusedError,
                ssl.SSLError,
                OSError,
            ) as e:
                if attempts > self.MAX_RETRIES:
                    raise ApiError(
                        f"API request failed after {attempts} attempts: "
                        f"{type(e).__name__}: {e}"
                    )
                time.sleep(self._retry_delay(attempts))
                continue

            # urlopen only returns for 2xx — success.
            return json.loads(response.read().decode("utf-8"))

    # ---------- private ---------------------------------------------------

    def _retry_delay(self, attempt: int) -> float:
        return self.BASE_RETRY_DELAY * (2 ** (attempt - 1))
