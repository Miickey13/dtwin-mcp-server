from typing import Any, Optional, TypedDict, Literal, List, Dict

SEARCH_PARAMETER_ENUM: Dict[str, int] = {
    "entityType": 1,
    "propertySet": 2,
    "property": 3,
    "classificationParameterSet": 4,
    "classificationParameter": 5,
    "storey": 6,
    "distance": 7,
}
SEARCH_OPERATOR_ENUM: Dict[str, int] = {
    "equal": 1,
    "notEqual": 2,
}

class ParameterIn(TypedDict, total=False):
    parameter: Literal[
        "entityType",
        "propertySet",
        "property",
        "classificationParameterSet",
        "classificationParameter",
        "storey",
        "distance",
    ]
    operator: Literal["Equal", "NotEqual"]
    key: Optional[str]
    value: Optional[str]

class DtwinSearchArgs(TypedDict, total=False):
    searchTerm: str | None
    parameters: List[ParameterIn]

def _lower_or_none(v: Optional[str]) -> Optional[str]:
    return v.lower() if isinstance(v, str) else None

def dtwin_search(
    searchTerm: Optional[str] = None,
    parameters: List[ParameterIn] = [],
) -> Dict[str, Any]:
    """
    Build the search payload for dTwin.

BACKEND REALITY (match this exactly)
- searchTerm → used as a lowercase text query over: entity.name, (name + longname), type, ifcid, storey.name, model.name, and ifcclass. It also gates a property text search if the caller sets searchProperties=true (outside this tool).
- Parameters are evaluated with exact equality (case-insensitive) per enum:
  entityType(1), propertySet(2), property(3), classificationParameterSet(4),
  classificationParameter(5), storey(6), distance(7).

WHAT TO PARAMETERIZE (and what NOT to)

1) Only use entityType when the user explicitly mentions type. otherwise use searchTerm.

2) distance → parameters[0] = distance
   - Phrases “within …”, “radius …”, “near …”, “distance …” + number ⇒ a single distance parameter:
       {"Parameter": 7, "Operator": 1, "Key": "<anchor id or ''>", "Value": "<number as string>"}
   - Ignore units; keep Value as a plain number string (e.g., "7", "7.5"). Key is optional; use "" unless a specific anchor element ID is given.

3) property → only when you have BOTH key and value
   - Backend checks `p.Name == key` AND `p.Value == value` on non-classification sets.
   - If the prompt doesn’t provide a concrete value, DO NOT create a property parameter. Use searchTerm only.

4) propertySet (non-classification sets)
   - Use only when the prompt gives an exact set name that is NOT a classification set.
   - This maps to `ps.Name == key` AND `ps.PropertySetTypeID != Classification`.

5) classificationParameterSet vs classificationParameter
   - classificationParameterSet: set name (e.g., “Uniclass”). Maps to `ps.Name == key`.
   - classificationParameter: key/value inside a classification set  → `p.Name == key` AND `p.Value == value`.

6) storey
   - Ideal case: the prompt provides an explicit storeyID (GUID string). Then:
       {"parameter": 6, "operator": 1, "key": "", "value": "<guid>"}
   - If the prompt references a storey/level but **no GUID is available**, still emit a placeholder:
       {"parameter": 6, "operator": 1, "key": "", "value": "placeholder"}
     (Downstream logic will resolve/replace the placeholder. Do not guess GUIDs.)

7) searchTerm rules
   - Always singular, lowercase (1-3 words). Strip filler: “elements/element/items/item”.
   - If nothing specific remains, set `searchTerm` = "".

8) One-parameter policy (output at most one parameter)
   - If multiple structured filters appear, *keep exactly one*
   - Represent all other intent via `searchTerm`.

INPUT (to this tool): a single object
{
  "searchTerm": "<optional>",
  "parameters": [
    { "parameter": "entityType|propertySet|property|classificationParameterSet|classificationParameter|storey|distance",
      "operator": "equal|notEqual",
      "key": "<string or ''>",
      "value": "<string or ''>" }
  ]
}

OUTPUT (from this tool):
{
  "function": {
    "command": "search",
    "arguments": {
      "searchTerm": "<singular, lowercase or ''>",
      "parameters": [
        { "parameter": <int>, "operator": <int>, "key": "<string|null|''>", "value": "<string|null|''>" }
      ]  // 0 or 1 item only
    }
  }
}

EXAMPLES (follow exactly)

A) "Find all elements of type wall within radius 7 meters"
-> {
     "function": {
       "command": "search",
       "arguments": {
         "searchTerm": "wall",
         "parameters": [
           {"parameter": 7, "operator": 1, "key": "", "value": "7"}
         ]
       }
     }
   }

B) "IfcWall only"
-> {
     "function": {
       "command": "search",
       "arguments": {
         "searchTerm": "",
         "parameters": [
           {"parameter": 1, "operator": 1, "key": "", "value": "ifcwall"}
         ]
       }
     }
   }

C) "Walls with property color red"
-> {
     "function": {
       "command": "search",
       "arguments": {
         "searchTerm": "wall",
         "parameters": [
           {"parameter": 3, "operator": 1, "key": "color", "value": "red"}
         ]
       }
     }
   }

D) "Find items that have classifications 'name' with value 'value'"
-> {
     "function": {
       "command": "search",
       "arguments": {
         "searchTerm": "",
         "parameters": [
           {"parameter": 5, "operator": 1, "key": "name", "value": "value"}
         ]
       }
     }
   }

E) "On level 2"
-> {
     "function": {
       "command": "search",
       "arguments": {
         "searchTerm": "",
         "parameters": [
           {"parameter": 6, "operator": 1, "key": "", "value": "placeholder"}
         ]
       }
     }
   }
    """

    args = {"searchTerm": searchTerm, "parameters": parameters or []}

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
            "parameter": SEARCH_PARAMETER_ENUM[pname],
            "operator": SEARCH_OPERATOR_ENUM[oname],
            "key": _lower_or_none(p.get("key")),
            "value": _lower_or_none(p.get("value")),
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
