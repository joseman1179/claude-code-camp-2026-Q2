# Technical Conclusion: MUD Agent Limitations

## The Core Problem
A standard coding harness (like OpenCode or Claude Code) cannot play an interactive MUD out of the box. 

The problem isn't the AI's intelligence; it’s an environment constraint. The agent’s bash tool is **atomic and non-interactive**. It runs a command, waits for it to finish, reads the text, and closes. Since a live MUD uses a persistent TCP socket connection that never closes, the agent's tools will always time out or freeze.

---

## The Solution: A Mediation Layer
To make interactive play work, we cannot give the agent direct shell access to the game. We need a bridge between the MUD and the Agent to maintain a proper **Agentic Loop**:

1. **A Dedicated SDK / Wrapper:** A local script (in Ruby or Python) that keeps the connection alive in the background, translates the game data into clean text, and allows the agent to send quick, one-off commands (e.g., `ruby prompt.rb move north`).
2. **An MCP (Model Context Protocol) Server:** A middleware server that handles the live connection and exposes structured tools (like JSON-RPC) directly to the agent, hiding the terminal streaming complexity.

## Final Takeaway
If you want an AI agent to interact with a live, real-time environment, don't use raw terminal commands. You must build or use a middleware layer (SDK or MCP) to handle the persistence.