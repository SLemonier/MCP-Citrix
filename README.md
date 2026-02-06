# Citrix MCP Server (Proof of Concept)

> ⚠️ **Status: Experimental / Proof of Concept**
> This is an early exploration of using MCP (Model Context Protocol) to manage Citrix infrastructure via AI assistants. Not production-ready.

## What is this?

An MCP server implementation that enables AI assistants (like Claude) to interact with Citrix Cloud/CVAD APIs. This allows administrators to manage Citrix infrastructure through natural language conversations.

## Why does this matter?

- Citrix consoles present data the way Citrix designed it — but that's not always how *you* need it for a specific task
- With an LLM, you decide how data is presented: need a property hidden by default? A comparison across delivery groups? Just ask
- No more digging through multiple console tabs or writing complex PowerShell to extract what is relevant to *you*
- MCP enables a conversational interface: "Show me all disconnected sessions" instead of writing scripts
- This bridges the gap between AI capabilities and EUC operational tasks

## Current Capabilities

This POC currently supports:
- **Session Management**: List all sessions, search sessions by user, log off sessions
- **Machine Management**: List all machines, search machines by name, shutdown servers

## Planned Capabilities

Future development will include:
- [ ] Power management (start, restart, suspend machines)
- [ ] Maintenance mode toggle
- [ ] Delivery group management
- [ ] Session messaging
- [ ] Machine catalog operations
- [ ] Applications management
- [ ] Interact with Monitor APIs

## Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager
- Citrix Cloud API credentials:
  - Client ID
  - Client Secret
  - Customer ID
  - Instance ID

## Installation

```bash
# Clone the repository
git clone https://github.com/SLemonier/MCP-Citrix.git
cd MCP-Citrix

# Install dependencies
uv sync
```

## Configuration

Set the following environment variables:

```bash
export CITRIX_CLIENT_ID="your-client-id"
export CITRIX_CLIENT_SECRET="your-client-secret"
export CITRIX_CUSTOMER_ID="your-customer-id"
export CITRIX_INSTANCE_ID="your-instance-id"
```

## Usage

### With Claude Code

Add to your MCP configuration:

```bash
claude mcp add citrix -s project -- uv run {yourpathto}/MCP-Citrix/citrix.py
```

### with Google Gemini-CLI

Add to your MCP configuration:

```bash
gemini mcp add citrix uv run /Users/steven.lemonier/Developer/MCP-Citrix/citrix.py
```

### Then

Then interact naturally:
- "List all current sessions"
- "Show me sessions for user john.doe"
- "Log off session abc-123"
- "Show all servers"

## Architecture

```
Claude/AI Assistant
        ↓
   MCP Protocol
        ↓
  citrix.py (MCP Server)
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
