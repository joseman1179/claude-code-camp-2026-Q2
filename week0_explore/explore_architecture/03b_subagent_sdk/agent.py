#!/usr/bin/env python3
import os
import time
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types
from scripts.mud_client import MUDClient

# Load environment variables from the repository root
load_dotenv(dotenv_path=Path(__file__).resolve().parents[3] / '.env')

# Sandboxing
BASE_DIR = os.getcwd()

def _validate_path(path: str) -> str:
    """Ensures the path is within the current directory."""
    abs_path = os.path.abspath(os.path.join(BASE_DIR, path))
    if not abs_path.startswith(BASE_DIR):
        raise ValueError(f"Path {path} is outside allowed directory")
    return abs_path

# Tools
def list_directory(path: str = ".") -> list[str]:
    """Lists files and directories in the given path."""
    safe_path = _validate_path(path)
    return os.listdir(safe_path)

def read_file(path: str) -> str:
    """Reads the contents of a file."""
    safe_path = _validate_path(path)
    with open(safe_path, 'r') as f:
        return f.read()

def write_file(path: str, content: str) -> str:
    """Writes content to a file."""
    safe_path = _validate_path(path)
    with open(safe_path, 'w') as f:
        f.write(content)
    return f"File {path} written successfully."

def grep_files(pattern: str, path: str = ".") -> list[str]:
    """Searches for a pattern in files within the path."""
    results = []
    safe_path = _validate_path(path)
    for root, _, files in os.walk(safe_path):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r') as f:
                    if pattern in f.read():
                        results.append(file_path)
            except Exception:
                continue
    return results

def check_player_hunger(username: str, password: str) -> str:
    """Connects to MUD and checks if player is hungry."""
    client = MUDClient()
    try:
        client.connect(username, password)
        client.send_command("score")
        response = client.get_clean_response()
        client.close()
        if "hungry" in response.lower():
            return f"{username} is hungry."
        return f"{username} is not hungry."
    except Exception as e:
        return f"Error checking hunger for {username}: {e}"

class Agent:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = "gemini-3.1-flash-lite"
        self.tools = [list_directory, read_file, write_file, grep_files, check_player_hunger]
        self.system_instruction = "You are a helpful AI assistant with filesystem access and MUD status checking capabilities, restricted to the current directory."
        self.history = []

    def _call_api(self, contents, config, retries=5):
        for i in range(retries):
            try:
                return self.client.models.generate_content(
                    model=self.model,
                    contents=contents,
                    config=config
                )
            except Exception as e:
                if '429' in str(e) and i < retries - 1:
                    wait = 2 ** i
                    print(f"Quota exceeded. Retrying in {wait} seconds...")
                    time.sleep(wait)
                    continue
                raise e

    def run(self, task: str):
        config = types.GenerateContentConfig(
            system_instruction=self.system_instruction,
            tools=self.tools
        )
        
        # Add user message to history
        self.history.append(types.Content(role="user", parts=[types.Part.from_text(text=task)]))

        response = self._call_api(self.history, config)
        
        # Handle tool calls
        while response.function_calls:
            # Add model's response (with function call) to history
            self.history.append(response.candidates[0].content)
            
            function_call = response.function_calls[0]
            tool_map = {f.__name__: f for f in self.tools}
            
            if function_call.name in tool_map:
                tool = tool_map[function_call.name]
                args = function_call.args
                try:
                    result = tool(**args)
                    # Add function response to history
                    tool_response_part = types.Part.from_function_response(
                        name=function_call.name,
                        response={'result': result}
                    )
                    self.history.append(types.Content(role="user", parts=[tool_response_part]))
                    
                    # Generate next turn
                    response = self._call_api(self.history, config)
                except Exception as e:
                    print(f"Error executing tool: {e}")
                    break
            else:
                break
                
        # Final text response
        if response.candidates and response.candidates[0].content:
            self.history.append(response.candidates[0].content)
        print(response.text)

if __name__ == '__main__':
    agent = Agent()
    while True:
        task = input("Task: ")
        if task.lower() in ["exit", "quit"]:
            break
        agent.run(task)
