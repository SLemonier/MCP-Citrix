# Citrix MCP Server (Proof of Concept)

> ⚠️ **Status: Experimental / Proof of Concept**
> This is an early exploration of using MCP (Model Context Protocol) to manage Citrix infrastructure via AI assistants. Not production-ready.

## What is this?

An MCP server that lets AI assistants (Claude, Gemini, …) talk to your Citrix Cloud / CVAD environment. Instead of clicking through Studio or writing PowerShell, you ask for what you want in natural language and the assistant calls the right Citrix REST API for you.

## Why does this matter?

- Citrix consoles present data the way Citrix designed it — not always how *you* need it for a specific task.
- With an LLM, you decide how data is presented: hide a property, compare across delivery groups, summarise across hundreds of machines — just ask.
- No more digging through console tabs or scripting one-off PowerShell to extract what is relevant to *you*.
- MCP enables a conversational interface: *"Show me all disconnected sessions"* instead of writing scripts.
- Bridges the gap between AI capabilities and EUC operational tasks.

## Current Capabilities

The single-file demo (`demo.py`) currently exposes:

- **Sessions** — list, search by user, log off
- **Machines** — list, search, power on, toggle maintenance mode
- **Applications** — list
- **Machine Catalogs** — list, get, create (template body — edit before use)
- **Delivery Groups** — list, create (template body — edit before use)
- **Image Definitions** — list, get, delete (incl. specific versions)
- **Monitoring** — list connection failures over a time window
- **Advisor** — list and trigger recommendations

> ℹ️ The `citrix_create_machine_catalog` and `citrix_create_delivery_group` tools contain **placeholder values** for AWS subnet, VPC, OU, image UUIDs, AD SID, etc. You must replace those with values from your own environment before calling them.

## Prerequisites

- **Python 3.11+**
- **[uv](https://docs.astral.sh/uv/)** — fast Python package & project manager
- **Citrix Cloud API credentials** (see [Getting Citrix credentials](#getting-citrix-credentials) below):
  - Client ID
  - Client Secret
  - Customer ID
  - Instance ID

## Installation

### 1. Install `uv`

macOS / Linux:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Windows (PowerShell):
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Other install methods: <https://docs.astral.sh/uv/getting-started/installation/>

### 2. Clone the repo

```bash
git clone https://github.com/SLemonier/MCP-Citrix.git
cd MCP-Citrix
```

### 3. Create the virtual environment and install dependencies

`uv sync` reads `pyproject.toml`/`uv.lock`, creates `.venv/` automatically, and installs everything pinned to the right versions.

```bash
uv sync
```

You do **not** need to activate the venv manually — `uv run` handles that for you.

### 4. Configure your credentials

Copy the example env file and fill it in:

```bash
cp .env.example .env
```

Then edit `.env`:

```dotenv
# === Required ===
CITRIX_CLIENT_ID=your-client-id
CITRIX_CLIENT_SECRET=your-client-secret
CITRIX_CUSTOMER_ID=your-customer-id
CITRIX_INSTANCE_ID=your-instance-id

# === Optional ===
# Region: us | eu | ap-s (default: us)
# CITRIX_REGION=us
```

> 🔒 `.env` is gitignored — your secrets stay local. **Never commit it.**

> ⚠️ The demo currently hardcodes the **EU** Citrix Cloud endpoints (`api-eu.cloud.com`). If you're in `us` / `ap-s`, edit the `API_BASE`, `MONITOR_BASE`, and `AUTH_URL` constants at the top of `demo.py` accordingly.

### 5. Test it runs

```bash
uv run demo.py
```

The process should start and wait silently on stdin (that's normal for an MCP stdio server). Press `Ctrl+C` to stop. If you see a stack trace, double-check your `.env` values.

## Getting Citrix credentials

In **Citrix Cloud → Identity and Access Management → API Access**, create a Secure Client and capture the **Client ID** and **Client Secret**. Your **Customer ID** is shown in the same console (top right). The **Instance ID** comes from a `GET /Me` call against the CVAD API — Citrix's docs walk through it: <https://developer-docs.citrix.com/>

## Usage

### With Claude Code

From inside the cloned repo:

```bash
claude mcp add citrix -s project -- uv run "$(pwd)/demo.py"
```

Or edit your project `.mcp.json` directly:

```json
{
  "mcpServers": {
    "citrix": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "/absolute/path/to/MCP-Citrix/demo.py"],
      "env": {}
    }
  }
}
```

### With Google Gemini CLI

```bash
gemini mcp add citrix uv run /absolute/path/to/MCP-Citrix/demo.py
```

### Then just ask

- *"List all current sessions"*
- *"Show me sessions for user john.doe"*
- *"Log off session abc-123"*
- *"Show all machines in maintenance mode"*
- *"List connection failures from the last 6 hours"*

## Troubleshooting

- **`uv: command not found`** — uv isn't on your `PATH`. Restart your shell, or add `~/.local/bin` to `PATH`.
- **`401 Unauthorized` from Citrix** — check `CITRIX_CLIENT_ID` / `CITRIX_CLIENT_SECRET`, and confirm the Secure Client hasn't been disabled.
- **`404` on every call** — your account is probably not in the EU region. Edit the `*_BASE` URLs in `demo.py` (see step 4 above).
- **Claude / Gemini doesn't see the tools** — confirm the path in your MCP config is **absolute**, and that `uv run demo.py` works standalone first.

## Architecture

```
Claude / AI Assistant
        ↓
   MCP Protocol (stdio)
        ↓
    demo.py  (FastMCP server)
        ↓
  Citrix Cloud REST API
```

## Contributing

This is an experimental project. Issues and PRs welcome.

## About the Author

I'm Steven Lemonier, a Citrix Cloud Engineer with 15+ years of experience in Citrix technologies. I'm passionate about automation and exploring how AI can transform EUC administration.

- 🌐 [stevenlemonier.fr](https://stevenlemonier.fr)
- 💼 [LinkedIn](https://linkedin.com/in/stevenlemonier)
- 🧑🏻‍💻 [GitHub](https://github.com/SLemonier)

## License

MIT
