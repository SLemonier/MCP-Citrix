"""
MCP-Citrix Demo — a minimal MCP server for Citrix DaaS / CVAD.

This single file is all you need to manage Citrix from an AI assistant.
Set your credentials in a .env file (see .env.example) and run:

    uv run demo.py

The full server (src/mcp_citrix/) adds pagination, error handling,
image management, monitoring, and more.
"""

import os
from datetime import datetime, timedelta, timezone

import httpx
from mcp.server.fastmcp import FastMCP

# ── Server ────────────────────────────────────────────────────────────────────

mcp = FastMCP("MCP-Citrix")

# ── Citrix Cloud credentials (from environment / .env) ───────────────────────

CLIENT_ID = os.getenv("CITRIX_CLIENT_ID")
CLIENT_SECRET = os.getenv("CITRIX_CLIENT_SECRET")
CUSTOMER_ID = os.getenv("CITRIX_CUSTOMER_ID")
INSTANCE_ID = os.getenv("CITRIX_INSTANCE_ID")

API_BASE = "https://api-eu.cloud.com/cvad/manage"
MONITOR_BASE = "https://api-eu.cloud.com/monitorodata"
AUTH_URL = f"https://api-eu.cloud.com/cctrustoauth2/{CUSTOMER_ID}/tokens/clients"
Advisor_URL = (
    f"https://{CUSTOMER_ID}.xendesktop.net/citrix/orchestration/api/{CUSTOMER_ID}/{INSTANCE_ID}"
)

# ── Auth helper ───────────────────────────────────────────────────────────────


async def get_headers() -> dict[str, str]:
    """Get a bearer token from Citrix Cloud and return auth headers."""
    async with httpx.AsyncClient() as http:
        resp = await http.post(
            AUTH_URL,
            data={
                "grant_type": "client_credentials",
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
            },
        )
    token = resp.json()["access_token"]
    return {
        "Authorization": f"CWSAuth Bearer={token}",
        "Citrix-CustomerId": CUSTOMER_ID,
        "Citrix-InstanceId": INSTANCE_ID,
        "Accept": "application/json",
    }


# ── Tools ─────────────────────────────────────────────────────────────────────


@mcp.tool()
async def citrix_list_sessions() -> dict:
    """List all active and disconnected Citrix sessions."""
    headers = await get_headers()
    async with httpx.AsyncClient() as http:
        resp = await http.get(f"{API_BASE}/Sessions", headers=headers)
    return resp.json()


@mcp.tool()
async def citrix_get_session(user_name: str) -> dict:
    """Search for a user's Citrix sessions by name."""
    headers = await get_headers()
    async with httpx.AsyncClient() as http:
        resp = await http.post(
            f"{API_BASE}/Sessions/$search",
            headers=headers,
            json={"BasicSearchString": user_name},
        )
    return resp.json()


@mcp.tool()
async def citrix_logoff_session(session_id: str) -> str:
    """Log off a Citrix session. The user will lose unsaved work."""
    headers = await get_headers()
    async with httpx.AsyncClient() as http:
        await http.post(f"{API_BASE}/Sessions/{session_id}/$logoff", headers=headers)
    return f"Session {session_id} logged off."


@mcp.tool()
async def citrix_list_machines() -> dict:
    """List all Citrix VDA machines."""
    headers = await get_headers()
    async with httpx.AsyncClient() as http:
        resp = await http.get(f"{API_BASE}/Machines", headers=headers)
    return resp.json()


@mcp.tool()
async def citrix_get_machine(machine_name: str) -> dict:
    """Search for a Citrix machine by name."""
    headers = await get_headers()
    async with httpx.AsyncClient() as http:
        resp = await http.post(
            f"{API_BASE}/Machines/$search",
            headers=headers,
            json={"BasicSearchString": machine_name},
        )
    return resp.json()


@mcp.tool()
async def citrix_turn_maintenance_mode_machine(machine_name: str, maintenance_mode: bool) -> dict:
    """Turn on or off maintenance mode on a specific machine."""
    headers = await get_headers()
    body = {
        "InMaintenanceMode": f"{maintenance_mode}",
    }
    async with httpx.AsyncClient(timeout=10.0) as http:
        resp = await http.patch(f"{API_BASE}/Machines/{machine_name}", headers=headers, json=body)
    return resp.json()


@mcp.tool()
async def citrix_power_on_machine(machine_name: str) -> dict:
    """Power on (or start) a specific machine"""
    headers = await get_headers()
    async with httpx.AsyncClient(timeout=10.0) as http:
        resp = await http.post(f"{API_BASE}/Machines/{machine_name}/$start", headers=headers)
    return resp.json()


@mcp.tool()
async def citrix_list_applications() -> dict:
    """List all Citrix applications."""
    headers = await get_headers()
    async with httpx.AsyncClient() as http:
        resp = await http.get(f"{API_BASE}/Applications", headers=headers)
    return resp.json()


@mcp.tool()
async def citrix_list_image_definitions() -> dict:
    """List all Citrix Image Definitinos."""
    headers = await get_headers()
    async with httpx.AsyncClient() as http:
        resp = await http.get(f"{API_BASE}/ImageDefinitions", headers=headers)
    return resp.json()


@mcp.tool()
async def citrix_get_image_definition(image_definition_name: str) -> dict:
    """Get a specific Citrix Image Definition by its name."""
    headers = await get_headers()
    async with httpx.AsyncClient() as http:
        resp = await http.get(
            f"{API_BASE}/ImageDefinitions/{image_definition_name}", headers=headers
        )
    return resp.json()


@mcp.tool()
async def citrix_delete_image_definition(image_definition_name: str) -> dict:
    """ "Delete a specific Citrix Image Definition by its name."""
    headers = await get_headers()
    async with httpx.AsyncClient(timeout=10.0) as http:
        resp = await http.delete(
            f"{API_BASE}/ImageDefinitions/{image_definition_name}", headers=headers
        )
    return resp.json()


@mcp.tool()
async def citrix_get_image_definition_version(image_definition_name: str) -> dict:
    """ "Get all image versions for a specific Citrix Image Definition by its name."""
    headers = await get_headers()
    async with httpx.AsyncClient() as http:
        resp = await http.get(
            f"{API_BASE}/ImageDefinitions/{image_definition_name}/ImageVersions", headers=headers
        )
    return resp.json()


@mcp.tool()
async def citrix_delete_image_definition_version(
    image_definition_name: str, image_version_number: int
) -> dict:
    """ "Delete a specific image version for a specific Citrix Image Definition by its name."""
    headers = await get_headers()
    async with httpx.AsyncClient(timeout=10.0) as http:
        resp = await http.delete(
            f"{API_BASE}/ImageDefinitions/{image_definition_name}/ImageVersions/{image_version_number}",
            headers=headers,
        )
    return resp.json()


@mcp.tool()
async def citrix_list_connection_failures(hours: int = 2) -> dict:
    """List Citrix connection failure logs for the past N hours (default 2).

    Expands Machine, User, and Session details for each failure.
    """
    end = datetime.now(timezone.utc)
    start = end - timedelta(hours=hours)
    fmt = "%Y-%m-%dT%H:%M:%SZ"
    params = {
        "$filter": f"(FailureDate ge {start.strftime(fmt)} and FailureDate le {end.strftime(fmt)})",
        "$expand": "Machine($select=Name,CurrentRegistrationState,IsInMaintenanceMode),User($select=Sid,Upn,UserName,Domain),Session",
    }
    headers = await get_headers()
    async with httpx.AsyncClient() as http:
        resp = await http.get(
            f"{MONITOR_BASE}/ConnectionFailureLogs", headers=headers, params=params
        )
    return resp.json()


@mcp.tool()
async def citrix_list_machine_catalogs() -> dict:
    """List all Citrix machine catalogs."""
    headers = await get_headers()
    async with httpx.AsyncClient() as http:
        resp = await http.get(f"{API_BASE}/MachineCatalogs", headers=headers)
    return resp.json()


@mcp.tool()
async def citrix_list_machine_catalog(machine_catalog_name: str) -> dict:
    """List a specific Citrix machine catalog."""
    headers = await get_headers()
    async with httpx.AsyncClient() as http:
        resp = await http.get(f"{API_BASE}/MachineCatalogs/{machine_catalog_name}", headers=headers)
    return resp.json()


@mcp.tool()
async def citrix_create_machine_catalog(usecase_name: str) -> dict:
    """ "Create a new machine catalog for a specific use case."""
    headers = await get_headers()
    body = {
        "Name": f"CATALOG-{usecase_name}",
        "AllocationType": "Random",
        "MinimumFunctionalLevel": "L7_34",
        "PersistUserChanges": "Discard",
        "ProvisioningType": "MCS",
        "SessionSupport": "MultiSession",
        "Zone": "YOUR-ZONE-NAME",
        "ProvisioningScheme": {
            "CpuCount": None,
            "MemoryMB": None,
            "UseWriteBackCache": False,
            "NumTotalMachines": 1,
            "NetworkMapping": [
                {
                    "DeviceNameOrId": "subnet-XXXXXXXXXXXXXXXXX",
                    "NetworkDeviceNameOrId": "0",
                    "NetworkPath": "XDHyp:\\HostingUnits\\YOUR-HOSTING-UNIT\\your-az.availabilityzone\\10.0.0.0`/24 (vpc-XXXXXXXXXXXXXXXXX).network",
                }
            ],
            "IdentityType": "HybridAzureAD",
            "MachineAccountCreationRules": {
                "NamingScheme": "VDA#####",
                "NamingSchemeType": "Numeric",
                "Domain": "corp.local",
                "OU": "OU=VDI,DC=corp,DC=local",
            },
            "AssignImageVersionToProvisioningScheme": {
                "ImageVersion": "00000000-0000-0000-0000-000000000000",
                "ImageDefinition": "00000000-0000-0000-0000-000000000000",
            },
            "ResourcePool": "YOUR-HOSTING-UNIT",
            "PrepareImage": True,
            "DedicatedTenancy": False,
            "TenancyType": "Shared",
            "CustomProperties": [],
            "ServiceOfferingPath": "XDHyp:\\HostingUnits\\YOUR-HOSTING-UNIT\\Your Instance Type.serviceoffering",
            "MachineProfilePath": "XDHyp:\\HostingUnits\\YOUR-HOSTING-UNIT\\your-machine-profile (lt-XXXXXXXXXXXXXXXXX).launchtemplate\\lt-XXXXXXXXXXXXXXXXX (1).launchtemplateversion",
            "ServiceAccountUid": ["00000000-0000-0000-0000-000000000000"],
        },
    }
    async with httpx.AsyncClient(timeout=10.0) as http:
        resp = await http.post(f"{API_BASE}/MachineCatalogs?async=true", headers=headers, json=body)
    return resp.json()


@mcp.tool()
async def citrix_list_delivery_groups() -> dict:
    """List all Citrix delivery groups."""
    headers = await get_headers()
    async with httpx.AsyncClient() as http:
        resp = await http.get(f"{API_BASE}/DeliveryGroups", headers=headers)
    return resp.json()


async def citrix_list_delivery_group(delivery_group_name: str) -> dict:
    """List a specific Citrix Delivery Group."""
    headers = await get_headers()
    async with httpx.AsyncClient() as http:
        resp = await http.get(f"{API_BASE}/DeliveryGroups/{delivery_group_name}", headers=headers)
    return resp.json()


@mcp.tool()
async def citrix_create_delivery_group(usecase_name: str, machine_catalog_id: str) -> dict:
    """ "Create a new delivery group for a specific use case."""
    headers = await get_headers()
    body = {
        "Name": f"DG-{usecase_name}",
        "MachineCatalogs": [
            {"MachineCatalog": f"{machine_catalog_id}", "Count": 1, "AssignMachinesToUsers": []}
        ],
        "DeliveryType": "DesktopsAndApps",
        "Desktops": [
            {
                "Enabled": True,
                "IncludedUserFilterEnabled": False,
                "IncludedUsers": [],
                "ExcludedUsers": [],
                "ExcludedUserFilterEnabled": False,
                "PublishedName": f"{usecase_name}",
                "MaxDesktops": 1,
                "SessionReconnection": "Always",
            }
        ],
        "MinimumFunctionalLevel": "L7_34",
        "RequireUserHomeZone": False,
        "RequiredSleepCapability": "None",
        "SimpleAccessPolicy": {
            "IncludedUsers": ["S-1-5-21-XXXXXXXXXX-XXXXXXXXXX-XXXXXXXXXX-XXXXXX"],
            "ExcludedUsers": [],
            "AllowAnonymous": False,
            "IncludedUserFilterEnabled": True,
            "ExcludedUserFilterEnabled": True,
        },
        "AppAccessPolicy": {"SessionReconnection": "Always"},
        "Applications": {
            "ExistingApplications": [],
            "NewApplications": [],
            "ExistingApplicationGroups": [],
        },
        "Scopes": [],
        "TimeZone": "UTC",
        "DefaultDesktopIcon": "1",
        "ProductCode": "",
        "LicenseModel": "None",
        "AutoScaleEnabled": True,
    }
    async with httpx.AsyncClient(timeout=10.0) as http:
        resp = await http.post(f"{API_BASE}/DeliveryGroups?async=true", headers=headers, json=body)
    return resp.json()


@mcp.tool()
async def citrix_list_advisor() -> dict:
    """List Citrix Advisor."""
    headers = await get_headers()
    async with httpx.AsyncClient() as http:
        resp = await http.get(
            f"{Advisor_URL}/Advisor/Recommendations?includeDismissed=false", headers=headers
        )
    return resp.json()


@mcp.tool()
async def citrix_start_Advisor() -> dict:
    """ Start Citrix Advisor."""
    headers = await get_headers()
    body = {
        "AspectNameList": [
            "Security",
            "Reliability",
            "Performance",
            "OperationalExcellence",
            "CostOptimization",
        ],
        "IsRunAllChecks": True,
        "RecommendationIdList": [],
    }
    async with httpx.AsyncClient() as http:
        resp = await http.post(
            f"{Advisor_URL}Advisor/$generateRecommendations?async=true", headers=headers, json=body
        )
    return resp.json()

@mcp.tool()
async def citrix_list_image_definitions() -> dict:
    """List all image definitions."""
    headers = await get_headers()
    async with httpx.AsyncClient() as http:
        resp = await http.get(f"{API}/ImageDefinitions", headers=headers)
    return resp.json()

@mcp.tool()
async def citrix_list_image_definition(image_definition_name: str) -> dict:
    """List a specific image definition by its name."""
    headers = await get_headers()
    async with httpx.AsyncClient() as http:
        resp = http.get(f"{API_BASE}/ImageDefinitions/{image_definition_name}")
    return resp.json()

@mcp.tool()
async def citrix_list_image_versions(image_definition_name: str) -> dict:
    """List all the image versions for a specific image definition."""
    headers = await get_headers()
    async with httpx.AsyncClient() as http:
        resp = http.get(f"{API_BASE}/ImageDefinitions/{image_definition_name}/ImageVersions", headers=headers)
    return resp.json()

@mcp.tool()
async def citrix_list_image_version(image_definition_name: str, version_number: str) -> dict:
    """Show a specific image version for a specific image definition."""
    headers = get_headers()
    async with httpx.AsyncClient() as http:
        resp = http.get(f"{API_BASE}/ImageDefinitions/{image_definition_name}/ImageVersion/{version_number}", headers=headers)
    return resp.json()

# ── Run ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run(transport="stdio")
