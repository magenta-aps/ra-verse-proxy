# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0
# pylint: disable=redefined-outer-name
"""This module contains pytest specific code, fixtures and helpers."""
from typing import Generator

import pytest

from ra_verse_proxy.server import app


@pytest.fixture
def celery_eager() -> Generator[None, None, None]:
    """Fixture to set celery in eager mode

    Eager mode calls the remote method directly, thus bypassing the worker.
    This is useful for unit-testing.
    """

    old_setting = app.conf.task_always_eager
    app.conf.task_always_eager = True
    yield
    app.conf.task_always_eager = old_setting
