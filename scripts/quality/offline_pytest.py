"""Opt-in pytest plugin denying real HTTP during ordinary CI (not cloud acceptance)."""

import socket

import httpx
import pytest


@pytest.fixture(autouse=True)
def deny_external_requests(monkeypatch):
    def denied(*args, **kwargs):
        raise AssertionError("Real network access is disabled in the offline validation job")

    async def denied_async(*args, **kwargs):
        denied()

    monkeypatch.setattr(httpx.HTTPTransport, "handle_request", denied)
    monkeypatch.setattr(httpx.AsyncHTTPTransport, "handle_async_request", denied_async)
    monkeypatch.setattr(socket, "create_connection", denied)
