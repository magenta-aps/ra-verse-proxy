# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0
"""This module tests ra_verse_proxy."""
# pylint: disable=unused-argument
import json

from fastapi.testclient import TestClient
from httpx import Response
from more_itertools import one
from respx import MockRouter

from ra_verse_proxy.main import create_app


def test_happy_path(celery_eager: None, respx_mock: MockRouter) -> None:
    """Test our happy-path scenario.

    Tests that our GraphQL query makes to the workers call against MO,
    and that whatever is returned by MO is returned to the caller.
    """

    graphql_query = {"a": "b"}
    graphql_response = {"c": "d"}

    mo_route = respx_mock.post("/graphql").mock(
        return_value=Response(200, json=graphql_response)
    )

    app = create_app()
    client = TestClient(app)
    response = client.post(
        "/graphql",
        json=graphql_query,
    )
    mo_route.calls.assert_called_once()
    call = one(mo_route.calls)
    binary_graphql_query = json.dumps(graphql_query).encode("ascii")
    assert call.request.content == binary_graphql_query

    assert response.status_code == 200
    assert response.json() == graphql_response
