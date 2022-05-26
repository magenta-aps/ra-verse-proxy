# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0
"""Celery entrypoint."""
from typing import Any
from typing import cast

import httpx
from celery import Celery

from .config import get_settings

settings = get_settings()
app = Celery(
    "ra_verse_proxy",
    backend="rpc://",
    broker=settings.amqp_url,
)


@app.task
def send_http_call(payload: dict[str, Any], headers: dict[str, Any]) -> dict[str, Any]:
    """HTTP call worker.

    Calls /graphql on OS2mo.

    Args:
        payload: The JSON payload to send to OS2mo.
        headers: Dictionary of HTTP headers to send to OS2mo.

    Returns:
        GraphQL JSON response.
    """
    response = httpx.post(
        get_settings().mo_url + "/graphql",
        json=payload,
        headers=headers,
    )
    return cast(dict[str, Any], response.json())
