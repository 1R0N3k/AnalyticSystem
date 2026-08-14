import sys
import types

import pytest


class FakeSessionState(dict):
    def __getattr__(self, name):
        if name.startswith("__"):
            raise AttributeError(name)
        return self[name]

    def __setattr__(self, name, value):
        self[name] = value


def _install_streamlit_stub():
    if "streamlit" in sys.modules:
        return

    stub = types.ModuleType("streamlit")
    stub.session_state = FakeSessionState()

    def _identity(fn):
        return fn

    def _cache_data(**kwargs):
        return _identity

    stub.cache_data = _cache_data
    stub.error = lambda *args, **kwargs: None
    stub.rerun = lambda *args, **kwargs: None

    sys.modules["streamlit"] = stub


_install_streamlit_stub()


@pytest.fixture(autouse=True)
def _clean_session_state():
    import streamlit as st

    st.session_state.clear()
    yield
