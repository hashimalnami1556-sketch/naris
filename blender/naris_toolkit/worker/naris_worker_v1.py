"""CALL OF NARIS — constrained Blender Worker v1.

This module is deliberately an operation dispatcher, not a remote Python executor.
Only the fixed NARIS operation names may reach Blender handlers.
"""

from __future__ import annotations

from typing import Any

from .operation_handlers import HANDLERS

PROTOCOL = "naris-worker/v1"
ALLOWED_OPERATIONS = set(HANDLERS)


def _progress(job_id: str, status: str, progress: int, message: str | None = None,
              result: dict[str, Any] | None = None, errors: list[str] | None = None,
              warnings: list[str] | None = None) -> dict[str, Any]:
    event: dict[str, Any] = {
        "protocol": PROTOCOL,
        "jobId": job_id,
        "status": status,
        "progress": max(0, min(100, int(progress))),
    }
    if message:
        event["message"] = message
    if result is not None:
        event["result"] = result
    if errors:
        event["errors"] = errors
    if warnings:
        event["warnings"] = warnings
    return event


def dispatch(request: dict[str, Any]) -> dict[str, Any]:
    """Validate an envelope and execute one explicit NARIS operation."""
    if not isinstance(request, dict):
        raise ValueError("NARIS_WORKER_INVALID_REQUEST")
    if request.get("protocol") != PROTOCOL:
        raise ValueError("NARIS_WORKER_PROTOCOL_MISMATCH")

    job_id = request.get("jobId")
    operation = request.get("operation")
    asset_id = request.get("assetId")
    parameters = request.get("parameters", {})

    if not isinstance(job_id, str) or not job_id:
        raise ValueError("NARIS_WORKER_INVALID_JOB_ID")
    if operation not in ALLOWED_OPERATIONS:
        return _progress(job_id, "FAILED", 0, errors=[f"Unsupported operation: {operation}"])
    if not isinstance(parameters, dict):
        return _progress(job_id, "FAILED", 0, errors=["parameters must be an object"])

    handler = HANDLERS[operation]
    try:
        running = _progress(job_id, "RUNNING", 10,
                            message=f"Executing named operation {operation}.")
        result = handler(asset_id, parameters)
        if isinstance(result, dict) and result.get("valid") is False:
            errors = result.get("errors", ["Asset validation failed"])
            return _progress(job_id, "FAILED", 100, result=result, errors=errors)
        return _progress(job_id, "SUCCEEDED", 100,
                         message=f"Completed named operation {operation}.", result=result,
                         warnings=result.get("warnings") if isinstance(result, dict) else None)
    except Exception as exc:
        return _progress(job_id, "FAILED", 100,
                         errors=[f"{type(exc).__name__}: {exc}"])
