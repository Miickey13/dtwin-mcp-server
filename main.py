
from mcp.server.fastmcp import FastMCP
from tools import echo, dtwin_about, dtwin_search

mcp = FastMCP("Dtwin MCP Server")

mcp.tool()(echo)
mcp.tool()(dtwin_about)
mcp.tool()(dtwin_search)

if __name__ == "__main__":
    print("Starting FastMCP server...")
    # Set the host to 0.0.0.0 to allow external connections for render.com
    mcp.settings.host = "0.0.0.0"
    # mcp.settings.host = "127.0.0.1"
    mcp.run(transport="streamable-http")




 