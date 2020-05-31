import asyncio
import os
from unittest import mock

import pytest
from async_asgi_testclient import TestClient
from django.http import HttpResponse
from django.urls.conf import path

from django_simple_task import defer

os.environ["DJANGO_SETTINGS_MODULE"] = "tests.settings"


@pytest.fixture
async def get_app():
    async def _get_app(patterns, asgi_version=3, inner_asgi_version=3):
        from . import urls, app

        urls.urlpatterns.clear()
        urls.urlpatterns.extend(patterns)
        test_app = (
            app.application
            if inner_asgi_version == 3
            else app.application_wrapping_asgi2
        )
        if asgi_version == 2:
            return app.application_wrapt_as_asgi2
        return test_app

    return _get_app


@pytest.mark.asyncio
async def test_sanity_check(get_app):
    def view(requests):
        return HttpResponse("Foo")

    app = await get_app([path("", view)])
    async with TestClient(app) as client:
        resp = await client.get("/")
        assert resp.status_code == 200
        assert resp.text == "Foo"

    app_asgi2 = await get_app([path("", view)], 2)
    async with TestClient(app_asgi2) as client_asgi2:
        resp = await client_asgi2.get("/")
        assert resp.status_code == 200
        assert resp.text == "Foo"

    app_wrapping_asgi2 = await get_app([path("", view)], 3, 2)
    async with TestClient(app_asgi2) as client_asgi2:
        resp = await client_asgi2.get("/")
        assert resp.status_code == 200
        assert resp.text == "Foo"


@pytest.mark.asyncio
async def test_should_call_task(get_app):
    task = mock.MagicMock()

    def view(requests):
        defer(task)
        return HttpResponse("Foo1")

    app = await get_app([path("", view)])
    async with TestClient(app) as client:
        task.assert_not_called()
        resp = await client.get("/")
        assert resp.status_code == 200
        assert resp.text == "Foo1"
    task.assert_called_once()


@pytest.mark.asyncio
async def test_should_call_async_task(get_app):
    cb = mock.MagicMock()

    async def task():
        await asyncio.sleep(1)
        cb()

    def view(requests):
        defer(task)
        defer(task)
        defer(task)
        defer(task)
        return HttpResponse("Foo")

    app = await get_app([path("", view)])
    async with TestClient(app) as client:
        cb.assert_not_called()
        resp = await client.get("/")
        assert resp.text == "Foo"
        cb.assert_not_called()
    assert cb.call_count == 4
