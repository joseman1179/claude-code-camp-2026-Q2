# Plan: Transition to Gemini Agent SDK

**Goal**: Replace the current filesystem sub-agent with a robust Gemini Agent SDK implementation for better agentic control over file system operations.

## Phase 1: Exploration & Clarification
1.  **Identify Current Implementation**: Conduct a thorough audit to locate the current "filesystem sub-agent" and how it's integrated (e.g., as a tool, an agent definition, or a helper script).
2.  **Define Requirements**: Clarify the scope of the "Gemini Agent SDK". Does this imply using a specific Google GenAI library, or designing a new, more abstracted SDK for `opencode` that interfaces with Gemini models?

## Phase 2: Design & Prototyping
1.  **Define SDK Interfaces**: Design the core interfaces for the `GeminiAgentSDK` for handling:
    *   File System Operations (Read/Write/List/Glob).
    *   Context Management.
    *   Safety & Permissions.
2.  **Prototyping**: Create a mock implementation of the SDK to test the API surface before deep integration.

## Phase 3: Implementation
1.  **SDK Implementation**: Develop the actual SDK code within the project structure (e.g., `scripts/GeminiAgentSDK.ts`).
2.  **Integration**: Replace the existing filesystem sub-agent's logic with the new SDK.
3.  **Update Agent Configs**: Update agent definitions (e.g., `play-mud.md`) to utilize the new SDK for their file system tasks.

## Phase 4: Verification
1.  **Unit Testing**: Ensure the SDK methods work correctly in isolation.
2.  **End-to-End Testing**: Verify that sub-agents (like `play-mud`) can successfully use the SDK to perform file operations without regression.