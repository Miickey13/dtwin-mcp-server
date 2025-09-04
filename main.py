from mcp.server.fastmcp import FastMCP
from typing import Any, Optional, TypedDict, Literal, List, Dict


mcp = FastMCP("Dtwin MCP Server")

@mcp.tool()
def echo(text: str) -> str:
    """Echo the input text"""
    return text


DTWIN_ABOUT_TEXT = (
    "dTwin harmonizes and visualizes all your facility’s data in a digital twin that allows you "
    "to see and understand your asset and enables you to act data-driven to increase its value. "
    "With dTwin you are getting the whole picture of your project, facility or building, you are "
    "leveraging the data you already own, and you are managing your asset more efficiently."
)

@mcp.tool()
def dtwin_about() -> str:
    """
    Return the official dTwin overview text.

    Use this tool whenever the user asks about dTwin (e.g., "what is dtwin?",
    "tell me about dtwin", "dtwin overview"). Quote or paraphrase the returned
    text in your answer; do not invent additional definitions.
    """
    return DTWIN_ABOUT_TEXT

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

    GATING RULE — WHEN TO BUILD `parameters`
    - Only attempt to populate the `parameters` array if the user's prompt explicitly mentions
      one of the SearchParameterEnum concepts or a close synonym:
        • EntityType  → "type", "entity type", "IFC type", specific types like "wall", "door", "pipe"
        • PropertySet → "property set", "pset", "parameter set"
        • Property    → "property", "attribute", "field", "has property"
        • ClassificationParameterSet → "classification set", "cls set"
        • ClassificationParameter    → "classification", "category code", "uniclass/omni/ifc class"
        • Storey      → "storey", "story", "level", "floor"
        • Distance    → "within", "distance", "radius", "near", "<= 4 m", "less than 5m"
    - If NONE of the above are clearly present, DO NOT build `parameters`. Instead, put a concise
      keyword (1–3 words) into `searchTerm` and leave `parameters` empty.

    SEARCHTERM RULES
    - Extract a concise free-text `searchTerm` from leftover intent that doesn't map neatly to `parameters`.
    - DO NOT use generic filler nouns like **"elements"**, **"element"**, **"items"**, or **"item"** as `searchTerm`.
      If nothing specific remains after removing such filler terms, set `searchTerm` to an empty string "".

    HOW THE LLM SHOULD USE THIS
    1) Read the user's natural-language prompt and construct a single args object:
       {
         "searchTerm": "<optional string>",
         "parameters": [
           {"parameter": <SearchParameterEnum name>, "operator": "Equal"|"NotEqual", "key": "<str>", "value": "<str>"},
           ...
         ]
       }

    2) Extract structured filters into `parameters` ONLY if the gating rule passes:
       - Use ONLY these parameter names (case-insensitive): EntityType, PropertySet, Property,
         ClassificationParameterSet, ClassificationParameter, Storey, Distance.
       - Operator defaults to "Equal" if omitted.
       - Lowercase key/value (the tool also normalizes).
       - If a property is mentioned WITHOUT a specific value, set value equal to key
         (this encodes "property exists"), e.g., key="color", value="color".
       - Do NOT invent new parameters. If a candidate parameter name isn't valid, omit it.

    3) Always extract a concise `searchTerm` (respecting the SEARCHTERM RULES). If nothing specific remains, use "".

    4) Examples (args you should send to this tool):

       - Prompt: "Find all elements of type wall that have property color"
         (mentions EntityType + Property → build parameters; exclude filler "elements")
         -> {
              "searchTerm": "wall",
              "parameters": [
                {"parameter":"Property","operator":"Equal","key":"color","value":"color"}
              ]
            }

       - Prompt: "Find walls within 4 m"
         (mentions Distance → build parameters)
         -> {
              "searchTerm": "walls",
              "parameters": [
                {"parameter":"Distance","operator":"Equal","key":"","value":"4"}
              ]
            }

       - Prompt: "Items on level 2"
         (Storey synonym present; exclude filler "items" from searchTerm)
         -> {
              "searchTerm": "",
              "parameters": [
                {"parameter":"Storey","operator":"Equal","key":"level","value":"2"}
              ]
            }

       - Prompt: "Show me elevators"
         (no structured enum concept beyond a general noun; ok to skip parameters if uncertain)
         -> {
              "searchTerm": "elevators",
              "parameters": []
            }

       - Prompt: "What is dtwin?"
         (no enum concept → DO NOT build parameters)
         -> {
              "searchTerm": "dtwin",
              "parameters": []
            }

    RETURN SHAPE (what this tool returns to the caller)
    {
      "functionName": "search",
      "parameters": {
        "searchTerm": "<string or empty>",
        "paramters": {
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

    response = {
        "functionName": "search",
        "parameters": {
            "searchTerm": search_term,
            "paramters": {
                "Parameters": out_params
            }
        }
    }
    return response



if __name__ == "__main__":
    print("Starting FastMCP server...")
    # Set the host to 0.0.0.0 to allow external connections for render.com
    mcp.settings.host = "0.0.0.0"
    # mcp.settings.host = "127.0.0.1"
    mcp.run(transport="streamable-http")




 