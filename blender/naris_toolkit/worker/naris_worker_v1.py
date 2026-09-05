"""CALL OF NARIS — constrained Blender Worker v1.

This module is deliberately an operation dispatcher, not a remote Python executor.
A transport may deliver validated NARIS Worker v1 envelopes to dispatch().
"""

PROTOCOL = "naris-worker/v1"
ALLOWED_OPERATIONS = {
    "VALIDATE_ASSET",
    "BUILD_ASSET",
    "GENERATE_LOD",
    "GENERATE_COLLISION",
    "PROCESS_TEXTURES",
    "RENDER_PREVIEW",
    "EXPORT_ASSET",
}


def _progress(job_id, status, progress, message=None, result=None, errors=None, warnings=None):
    event = {
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


def dispatch(request):
    """Validate an envelope and route to a named operation.

    The actual NARIS Toolkit operators should be registered behind these names.
    Unknown keys and arbitrary Python source are never executed.
    """
    if not isinstance(request, dict):
        raise ValueError("NARIS_WORKER_INVALID_REQUEST")
    if request.get("protocol") != PROTOCOL:
        raise ValueError("NARIS_WORKER_PROTOCOL_MISMATCH")

    job_id = request.get("jobId")
    operation = request.get("operation")
    parameters = request.get("parameters", {})
    if not isinstance(job_id, str) or not job_id:
        raise ValueError("NARIS_WORKER_INVALID_JOB_ID")
    if operation not in ALLOWED_OPERATIONS:
        return _progress(job_id, "FAILED", 0, errors=[f"Unsupported operation: {operation}"])
    if not isinstance(parameters, dict):
        return _progress(job_id, "FAILED", 0, errors=["parameters must be an object"])

    # Integration point for bpy/NARIS Toolkit operators.
    # Keep this explicit so every production operation is auditable and testable.
    return _progress(
        job_id,
        "RUNNING",
        0,
        message=f"Accepted named operation {operation}; Toolkit operator dispatch is ready.",
        warnings=["No geometry mutation is performed by this protocol adapter alone."],
    )
