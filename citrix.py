from typing import Any
import httpx
import os
import requests
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("Citrix")

# Citrix Cloud Constants
citrixCloudClientID = os.getenv("CITRIX_CLIENT_ID")
citrixCloudClientSecret = os.getenv("CITRIX_CLIENT_SECRET")
citrixCloudInstanceID = os.getenv("CITRIX_INSTANCE_ID")
citrixCloudCustomerID = os.getenv("CITRIX_CUSTOMER_ID")

# Constants
CITRIX_API_BASE = "https://api.cloud.com/cvad/manage"
CITRIX_AUTH_API_BASE = f"https://api.cloud.com/cctrustoauth2/{citrixCloudCustomerID}/tokens/clients"


#Helper functions
def get_headers():
    body = {
        "grant_type": "client_credentials",
        "client_id": citrixCloudClientID,
        "client_secret": citrixCloudClientSecret
    }

    response = requests.post(CITRIX_AUTH_API_BASE, body)
    token = response.json()


    #request_uri = "https://api.cloud.com/cvad/manage/me"
    #headers = {
    #    'Authorization': 'CWSAuth Bearer=%s' % token['access_token'],
    #    'Citrix-CustomerId': citrixCloudCustomerID,
    #    'Content-Type': 'application/json',
    #    'Accept': 'application/json'
    #}

    #response = requests.get(request_uri, headers = headers)

    headers = {
        "Accept": "application/json",
        "Authorization": f"CwsAuth Bearer={token['access_token']}",
        "Citrix-CustomerId": citrixCloudCustomerID,
        "Citrix-InstanceId": citrixCloudInstanceID
    }

    return headers



@mcp.tool()
async def get_user_session(query: str) -> list[dict]:
    """Get specific user's sessions from Citrix Cloud"""
    headers = get_headers()
    body = {
        "BasicSearchString": query,
    }
    response = requests.post(f"{CITRIX_API_BASE}/Sessions/$search", headers=headers, json=body)
    return response.json()

@mcp.tool()
async def get_all_sessions() -> list[dict]:
    """Get all sessions from Citrix Cloud"""
    headers = get_headers()
    response = requests.get(f"{CITRIX_API_BASE}/Sessions", headers=headers)
    return response.json()

@mcp.tool()
async def shutdown_server(server_id: str) -> dict:
    """Shutdown a server"""
    headers = get_headers()
    response = requests.post(f"{CITRIX_API_BASE}/Machines/{server_id}/$shutdown", headers=headers)
    return response.json()

@mcp.tool()
async def log_off_session(session_id: str) -> dict:
    """Log off a session"""
    headers = get_headers()
    response = requests.post(f"{CITRIX_API_BASE}/Sessions/{session_id}/$logoff", headers=headers)

@mcp.tool()
async def get_all_servers() -> dict:
    """Get details of a specific server"""
    headers = get_headers()
    response = requests.get(f"{CITRIX_API_BASE}/Machines", headers=headers)
    return response.json()

@mcp.tool()
async def get_server_details(query: str) -> dict:
    """Get details of a specific server"""
    headers = get_headers()
    body = {
        "BasicSearchString": query,
    }
    response = requests.post(f"{CITRIX_API_BASE}/Machines/$search", headers=headers, json=body)
    return response.json()


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')