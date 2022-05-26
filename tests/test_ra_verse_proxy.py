# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0
"""This module tests ra_verse_proxy."""
# pylint: disable=unused-argument
# pylint: disable=redefined-outer-name
from typing import Callable
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from httpx import Response
from respx import MockRouter

from ra_verse_proxy.main import create_app


@pytest.fixture
def fire_graphql_query(
    celery_eager: None,
    respx_mock: MockRouter,
) -> Generator[Callable[..., Response], None, None]:
    """Fixture to unit-test the entire application end-to-end."""

    def inner(
        graphql_query: dict[str, str],
        response: Response,
    ) -> Response:
        mo_route = respx_mock.post("/graphql", json=graphql_query).mock(
            return_value=response
        )

        app = create_app()
        client = TestClient(app)
        response = client.post(
            "/graphql",
            json=graphql_query,
        )
        mo_route.calls.assert_called_once()
        return response

    yield inner


def test_happy_path(fire_graphql_query: Callable[..., Response]) -> None:
    """Test our happy-path scenario.

    Tests that our GraphQL query makes to the workers call against MO,
    and that whatever is returned by MO is returned to the caller.
    """
    graphql_query = {"a": "b"}
    graphql_response = {"c": "d"}

    mo_response = Response(200, json=graphql_response)
    response = fire_graphql_query(graphql_query, mo_response)
    assert response.status_code == 200
    assert response.json() == graphql_response


def test_bad_response_from_mo(fire_graphql_query: Callable[..., Response]) -> None:
    """Test our happy-path scenario.

    Tests that our GraphQL query makes to the workers call against MO,
    and that whatever is returned by MO is returned to the caller.
    """
    graphql_query = {"a": "b"}
    error_message = {"error": "Internal Server Error"}

    mo_response = Response(500, json=error_message)
    response = fire_graphql_query(graphql_query, mo_response)
    assert response.status_code == 500
    assert response.json() == {"detail": error_message}
