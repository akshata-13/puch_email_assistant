import asyncio
from typing import Annotated
import os

from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.server.auth.providers.bearer import BearerAuthProvider, RSAKeyPair
from mcp import ErrorData, McpError
from mcp.server.auth.provider import AccessToken
from mcp.types import INTERNAL_ERROR
from pydantic import BaseModel, Field

import google.generativeai as genai

# --- Load environment variables ---
load_dotenv()

TOKEN = os.environ.get("AUTH_TOKEN")
MY_NUMBER = os.environ.get("MY_NUMBER")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

assert TOKEN is not None, "Please set AUTH_TOKEN in your .env file"
assert MY_NUMBER is not None, "Please set MY_NUMBER in your .env file"
assert GOOGLE_API_KEY is not None, "Please set GOOGLE_API_KEY in your .env file"

# --- Auth Provider ---
class SimpleBearerAuthProvider(BearerAuthProvider):
    def __init__(self, token: str):
        k = RSAKeyPair.generate()
        super().__init__(public_key=k.public_key, jwks_uri=None, issuer=None, audience=None)
        self.token = token

    async def load_access_token(self, token: str) -> AccessToken | None:
        if token == self.token:
            return AccessToken(token=token, client_id="puch-client", scopes=["*"], expires_at=None)
        return None

# --- Rich Tool Description model ---
class RichToolDescription(BaseModel):
    description: str
    use_when: str
    side_effects: str | None = None

# --- MCP Server Setup ---
mcp = FastMCP("AI Email Assistant Suite", auth=SimpleBearerAuthProvider(TOKEN))
genai.configure(api_key=GOOGLE_API_KEY)

# --- Tool: validate (required by Puch) ---
@mcp.tool
async def validate() -> str:
    if MY_NUMBER:
        return MY_NUMBER.lstrip('+')
    return ""

# --- Helper function for making Gemini calls ---
async def make_gemini_call(prompt: str) -> str:
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        def do_generate():
            response = model.generate_content(prompt)
            return response.text
        response_text = await asyncio.to_thread(do_generate)
        return response_text
    except Exception as e:
        raise McpError(ErrorData(code=INTERNAL_ERROR, message=f"Failed to process with Google AI: {e!r}"))

# --- NEW TOOL SUITE ---

@mcp.tool(description="Analyzes the tone of a draft email and provides feedback.")
async def analyze_email_tone(
    email_draft: Annotated[str, Field(description="The user's draft email text.")]
) -> str:
    """Analyzes the tone of an email draft."""
    prompt = f"Please analyze the tone of the following email draft. Describe the current tone and provide a bulleted list of suggestions for improvement.\n\nDraft:\n---\n{email_draft}"
    return await make_gemini_call(prompt)

@mcp.tool(description="Rewrites an email draft to match a specific target tone.")
async def rewrite_email(
    email_draft: Annotated[str, Field(description="The email draft to rewrite.")],
    target_tone: Annotated[str, Field(description="The desired tone (e.g., Formal, Confident, Friendly).")]
) -> str:
    """Rewrites an email to a new tone."""
    prompt = f"Please rewrite the following email draft to have a '{target_tone}' tone. Provide only the rewritten version.\n\nDraft:\n---\n{email_draft}"
    return await make_gemini_call(prompt)

@mcp.tool(description="Shortens an email draft to make it more concise.")
async def shorten_email(
    email_draft: Annotated[str, Field(description="The email draft to be shortened.")]
) -> str:
    """Shortens an email to be more concise."""
    prompt = f"Please shorten the following email to be as concise as possible while retaining the core message. Provide only the shortened version.\n\nDraft:\n---\n{email_draft}"
    return await make_gemini_call(prompt)

@mcp.tool(description="Expands a list of bullet points into a full, well-formatted email.")
async def expand_from_bullets(
    bullet_points: Annotated[str, Field(description="A list of bullet points or short notes.")],
    goal: Annotated[str, Field(description="The overall goal or context of the email (e.g., 'a project update to my manager').")]
) -> str:
    """Expands bullet points into a full email."""
    prompt = f"Please expand the following bullet points into a well-formatted email. The goal of the email is: {goal}. Provide only the full email text.\n\nBullet Points:\n---\n{bullet_points}"
    return await make_gemini_call(prompt)

# --- Run MCP Server ---
async def main():
    port = int(os.environ.get("PORT", 8088))
    print(f"🚀 Starting AI Email Assistant Suite Server on http://0.0.0.0:{port}")
    await mcp.run_async("streamable-http", host="0.0.0.0", port=port)

if __name__ == "__main__":
    asyncio.run(main())
