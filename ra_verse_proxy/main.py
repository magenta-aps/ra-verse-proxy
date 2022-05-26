# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0
"""Uvicorn entrypoint."""
from typing import Any

from fastapi import Body
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from strawberry.asgi.utils import get_graphiql_html

from .config import get_settings
from .server import send_http_call


def create_app(*args: Any, **kwargs: Any) -> FastAPI:
    """FastAPI application factory."""
    app = FastAPI()
    settings = get_settings(*args, **kwargs)

    if settings.enable_graphiql:

        @app.get(
            "/graphql",
            response_class=HTMLResponse,
        )
        async def serve_graphiql() -> HTMLResponse:
            """Serve GraphiQL.

            Returns:
                GraphiQL HTML.
            """
            html = get_graphiql_html()
            return HTMLResponse(html)

    @app.post(
        "/graphql",
        response_class=JSONResponse,
    )
    def graphql_proxy(
        request: Request,
        payload: dict = Body(...),
    ) -> JSONResponse:
        """Proxy GraphQL Post.

        Args:
            request: The incoming request to be forwarded.

        Returns:
            Result of running the GraphQL query on MO.
        """
        # Extract POST payload and relevant headers
        found_headers = settings.header_whitelist.intersection(request.headers.keys())
        headers = {key: request.headers[key] for key in found_headers}
        # Send Payload and Headers to remote worker, and await response.
        async_result = send_http_call.delay(payload, headers)
        status_code, result = async_result.get()
        if status_code != 200:
            raise HTTPException(status_code=status_code, detail=result)
        return JSONResponse(result)

    return app
