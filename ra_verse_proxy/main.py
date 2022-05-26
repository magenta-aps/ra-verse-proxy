# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0
"""Uvicorn entrypoint."""
from typing import Any
from typing import cast

from asgiref.sync import sync_to_async
from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import HTMLResponse
from strawberry.asgi.utils import get_graphiql_html

from .config import get_settings
from .server import send_http_call


def create_app() -> FastAPI:
    """FastAPI application factory."""
    app = FastAPI()
    settings = get_settings()

    if settings.enable_graphiql:

        @app.get("/graphql")
        async def serve_graphiql() -> HTMLResponse:
            """Serve GraphiQL.

            Returns:
                GraphiQL HTML.
            """
            html = get_graphiql_html()
            return HTMLResponse(html)

    @app.post("/graphql")
    async def graphql_proxy(request: Request) -> dict[str, Any]:
        """Proxy GraphQL Post.

        Args:
            request: The incoming request to be forwarded.

        Returns:
            Result of running the GraphQL query on MO.
        """
        # Extract POST payload and relevant headers
        payload = await request.json()
        headers = {
            key: value
            for key, value in request.headers.items()
            if key in settings.header_whitelist
        }
        # Send Payload and Headers to remote worker, and await response.
        async_result = send_http_call.delay(payload, headers)
        result = await sync_to_async(async_result.get, thread_sensitive=True)()
        return cast(dict[str, Any], result)

    return app
