from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import os
import httpx

app = FastAPI(title="NARIS BioNeMo Agent", version="0.1.0")

OPENFOLD3_URL = os.getenv(
    "OPENFOLD3_URL",
    "https://health.api.nvidia.com/v1/biology/openfold/openfold3/predict",
)

class StructureRequest(BaseModel):
    sequence: str = Field(min_length=1, max_length=10000)
    input_id: str = Field(default="naris-protein")
    output_format: str = Field(default="pdb")

class StructureResponse(BaseModel):
    input_id: str
    status: str
    provider: str
    result: dict


def normalize_sequence(sequence: str) -> str:
    seq = "".join(sequence.split()).upper()
    if not seq:
        raise ValueError("Sequence is empty")
    invalid = sorted(set(seq) - set("ACDEFGHIKLMNPQRSTVWY"))
    if invalid:
        raise ValueError(f"Unsupported amino-acid symbols: {','.join(invalid)}")
    return seq


@app.get("/health")
def health():
    return {"status": "ok", "service": "naris-bionemo-agent"}


@app.post("/api/v1/structure", response_model=StructureResponse)
async def predict_structure(request: StructureRequest):
    try:
        sequence = normalize_sequence(request.sequence)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    api_key = os.getenv("NGC_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="NGC_API_KEY is not configured")

    payload = {
        "input_id": request.input_id,
        "output_format": request.output_format,
        "molecules": [
            {"type": "protein", "id": "A", "sequence": sequence}
        ],
    }

    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(OPENFOLD3_URL, json=payload, headers=headers)
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        detail = exc.response.text[:2000]
        raise HTTPException(status_code=502, detail=f"BioNeMo NIM error: {detail}") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"BioNeMo connection error: {exc}") from exc

    return StructureResponse(
        input_id=request.input_id,
        status="completed",
        provider="NVIDIA BioNeMo OpenFold3 NIM",
        result=response.json(),
    )
