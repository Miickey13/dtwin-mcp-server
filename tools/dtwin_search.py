from typing import Any, Optional, TypedDict, Literal, List, Dict

SEARCH_PARAMETER_ENUM: Dict[str, int] = {
    "EntityType": 1,
    "PropertySet": 2,
    "Property": 3,
    "ClassificationParameterSet": 4,
    "ClassificationParameter": 5,
    "Storey": 6,
    "Distance": 7,
}
SEARCH_OPERATOR_ENUM: Dict[str, int] = {
    "Equal": 1,
    "NotEqual": 2,
}

class ParameterIn(TypedDict, total=False):
    parameter: Literal[
        "EntityType",
        "PropertySet",
        "Property",
        "ClassificationParameterSet",
        "ClassificationParameter",
        "Storey",
        "Distance",
    ]
    operator: Literal["Equal", "NotEqual"]
    key: Optional[str]
    value: Optional[str]

class DtwinSearchArgs(TypedDict, total=False):
    searchTerm: str | None
    parameters: List[ParameterIn]

def _lower_or_none(v: Optional[str]) -> Optional[str]:
    return v.lower() if isinstance(v, str) else None

def dtwin_search(args: DtwinSearchArgs) -> Dict[str, Any]:
    """
    Build the search payload for dtwin.
    """
    if not isinstance(args, dict):
        raise ValueError("Tool expects a single object argument.")

    params_in = args.get("parameters") or []
    if not isinstance(params_in, list):
        raise ValueError("`parameters` must be a list.")

    out_params: List[Dict[str, Any]] = []
    for p in params_in:
        if not isinstance(p, dict):
            raise ValueError("Each parameter must be an object.")
        pname = p.get("parameter")
        oname = p.get("operator") or "Equal"

        if pname not in SEARCH_PARAMETER_ENUM:
            raise ValueError(f"Unknown parameter enum: {pname}")
        if oname not in SEARCH_OPERATOR_ENUM:
            raise ValueError(f"Unknown operator enum: {oname}")

        out_params.append({
            "Parameter": SEARCH_PARAMETER_ENUM[pname],
            "Operator": SEARCH_OPERATOR_ENUM[oname],
            "Key": _lower_or_none(p.get("key")),
            "Value": _lower_or_none(p.get("value")),
        })

    search_term = args.get("searchTerm") or ""

    response = {
        "function": {
            "command": "search",
            "arguments": {
                "searchTerm": search_term,
                "parameters": out_params 
            }
        }
    }
    return response
