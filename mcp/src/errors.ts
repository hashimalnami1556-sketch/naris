export const NARIS_ERRORS = {
  ASSET_NOT_FOUND: "NARIS_ASSET_NOT_FOUND",
  PERMISSION_DENIED: "NARIS_PERMISSION_DENIED",
  INVALID_ASSET_ID: "NARIS_INVALID_ASSET_ID",
  VALIDATION_FAILED: "NARIS_VALIDATION_FAILED",
  PIPELINE_NOT_FOUND: "NARIS_PIPELINE_NOT_FOUND",
  JOB_FAILED: "NARIS_JOB_FAILED",
  EXPORT_BLOCKED: "NARIS_EXPORT_BLOCKED",
  BLENDER_UNAVAILABLE: "NARIS_BLENDER_UNAVAILABLE",
  DEPENDENCY_MISSING: "NARIS_DEPENDENCY_MISSING",
  SCHEMA_INVALID: "NARIS_SCHEMA_INVALID",
  APPROVAL_REQUIRED: "NARIS_APPROVAL_REQUIRED",
} as const;

export type NarisErrorCode = typeof NARIS_ERRORS[keyof typeof NARIS_ERRORS];

export class NarisError extends Error {
  constructor(
    public readonly code: NarisErrorCode,
    message: string,
    public readonly retryable = false,
    public readonly details?: Record<string, unknown>,
  ) {
    super(message);
    this.name = "NarisError";
  }
}
