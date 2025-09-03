from mcp.server.fastmcp import FastMCP
from typing import Any, Optional, TypedDict, Literal, List, Dict


mcp = FastMCP("Dtwin MCP Server")

@mcp.tool()
def echo(text: str) -> str:
    """Echo the input text"""
    return text


# @mcp.tool()
# def dtwin_search(query: str) -> list[str]:
#     """Search for dtwin entities and return a list of IDs"""
#     # Placeholder implementation - replace with actual dtwin search logic
#     # For now, returning mock IDs based on the query
#     mock_ids = [
#         f"dtwin_{hash(query + str(i)) % 10000}" for i in range(3)
#     ]
#     return mock_ids

# ---- Enum maps (names -> ints) to mirror your C# enums ----
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

# ---- Typed input for one parameter ----
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

def _lower_or_none(v: Optional[str]) -> Optional[str]:
    return v.lower() if isinstance(v, str) else None


# ---- Typed input for a single parameter (drives the tool's JSON Schema) ----
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
    # Optional free-text term
    searchTerm: str | None
    # Required list of parameter objects
    parameters: List[ParameterIn]

def _lower_or_none(v: Optional[str]) -> Optional[str]:
    return v.lower() if isinstance(v, str) else None

# @mcp.tool()
# def list_search_enums() -> Dict[str, Dict[str, int]]:
#     """
#     Return the allowed enum names and their integer values.

#     Use this first if you need to confirm which enum names are valid
#     before calling build_search_request.
#     """
#     return {
#         "SearchParameterEnum": SEARCH_PARAMETER_ENUM,
#         "SearchOperatorEnum": SEARCH_OPERATOR_ENUM,
#     }

@mcp.tool()
def dtwin_search(args: DtwinSearchArgs) -> Dict[str, Any]:
    """
    Build the search payload for dtwin.

    HOW THE LLM SHOULD USE THIS
    1) Read the user's natural-language prompt and construct a single args object:
       {
         "searchTerm": "<optional string>",
         "parameters": [
           {"parameter": <SearchParameterEnum name>, "operator": "Equal"|"NotEqual", "key": "<str>", "value": "<str>"},
           ...
         ]
       }

    2) Extract structured filters into `parameters`:
       - Use ONLY these parameter names (case-insensitive): EntityType, PropertySet, Property,
         ClassificationParameterSet, ClassificationParameter, Storey, Distance.
       - Operator defaults to "Equal" if omitted.
       - Lowercase key/value (the tool also normalizes).
       - If a property is mentioned WITHOUT a specific value, set value equal to key
         (this encodes "property exists"), e.g. key="color", value="color".

    3) Extract a concise free-text `searchTerm` from any leftover intent that doesn't map neatly
       to `parameters` (e.g., entity type keywords, fuzzy descriptors, or general terms).
       Keep it short (1–3 words). If nothing is left over, you may omit it or set "".

    4) Examples (args you should send to this tool):
       - Prompt: "Find all elements of type wall that have property color"
         -> {
              "searchTerm": "wall",
              "parameters": [
                {"parameter":"Property","operator":"Equal","key":"color","value":"color"}
              ]
            }

       - Prompt: "Find walls within 4 m of exits"
         -> {
              "searchTerm": "walls near exits",
              "parameters": [
                {"parameter":"Distance","operator":"Equal","key":"","value":"4"}
              ]
            }

       - Prompt: "Exclude storey GroundFloor"
         -> {
              "searchTerm": "",
              "parameters": [
                {"parameter":"Storey","operator":"NotEqual","key":"groundfloor","value":"groundfloor"}
              ]
            }

    RETURN SHAPE (what this tool returns to the caller)
    {
      "functionName": "search",
      "parameters": {
        "searchTerm": "<string or empty>",
        "parameters": {
          "Parameters": [
            {"Parameter": <int>, "Operator": <int>, "Key": "<str|null>", "Value": "<str|null>"},
            ...
          ]
        }
      }
    }
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
        oname = p.get("operator") or "Equal"  # default

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

    # NOTE: keeping the exact key spellings you requested: paramteres / paramters
    response = {
        "functionName": "search",
        "paramteres": {
            "searchTerm": search_term,
            "paramters": {
                "Parameters": out_params
            }
        }
    }
    return response

if __name__ == "__main__":
    print("Starting FastMCP server...")
    mcp.settings.host = "0.0.0.0"
    mcp.run(transport="streamable-http")




 