# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0
"""Shared settings module."""
from functools import cache
from typing import Any

from pydantic import AmqpDsn
from pydantic import AnyHttpUrl
from pydantic import BaseSettings
from pydantic import Field
from pydantic import parse_obj_as


class Settings(BaseSettings):
    """Settings from both Integration Point and Integration Engine."""

    # pylint: disable=too-few-public-methods

    enable_graphiql: bool = Field(
        False,
        description="Whether to serve GraphiQL",
    )
    header_whitelist: set[str] = Field(
        set(["authorization"]), description="List of HTTP headers to forward."
    )

    amqp_url: AmqpDsn = Field(
        parse_obj_as(AmqpDsn, "amqp://guest:guest@rabbitmq:5672/"),
        description="URL for RabbitMQ.",
    )

    mo_url: AnyHttpUrl = Field(
        parse_obj_as(AnyHttpUrl, "http://mo-service:5000"),
        description="URL for MO.",
    )


@cache
def get_settings(*args: Any, **kwargs: Any) -> Settings:
    """Get settings.

    Args:
        args: Overrides
        kwargs: Overrides

    Returns:
        Constructed settings object.
    """
    return Settings(*args, **kwargs)
