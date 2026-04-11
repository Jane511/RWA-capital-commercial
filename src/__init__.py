from __future__ import annotations


def run_pipeline(*args, **kwargs):
    from .run_pipeline import run_pipeline as _run_pipeline

    return _run_pipeline(*args, **kwargs)


__all__ = ["run_pipeline"]
