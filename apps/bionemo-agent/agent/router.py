from dataclasses import dataclass

@dataclass(frozen=True)
class Route:
    workflow: str
    reason: str


def route(task: str) -> Route:
    text = task.lower()
    if any(k in text for k in ("structure", "fold", "protein")):
        return Route("structure_prediction", "Protein structure prediction requested")
    if any(k in text for k in ("dock", "ligand", "binding")):
        return Route("molecular_docking", "Molecular interaction workflow requested")
    if any(k in text for k in ("binder", "design protein", "binding protein")):
        return Route("protein_binder_design", "Protein design workflow requested")
    return Route("unsupported", "No safe BioNeMo workflow matched the task")
