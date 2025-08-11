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
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY") # Changed from OPENAI_API_KEY

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
mcp = FastMCP("AI Email Assistant", auth=SimpleBearerAuthProvider(TOKEN))

# --- Tool: validate (required by Puch) ---
@mcp.tool
async def validate() -> str:
    if MY_NUMBER:
        return MY_NUMBER.lstrip('+')
    return ""

# --- NEW TOOL: AI Email Assistant (Powered by Google Gemini) ---
EmailAssistantDescription = RichToolDescription(
    description="Analyzes and rewrites a user's email draft to match a specific target tone (e.g., Formal, Confident). Provides analysis, suggestions, and a full rewrite.",
    use_when="Use this tool ONLY when a user pastes a block of text and explicitly asks to 'analyze', 'rewrite', 'fix', or 'change the tone' of an email. This tool is the primary choice for improving user-provided email drafts.",
    side_effects="Returns a formatted text response directly to the user.",
)

@mcp.tool(description=EmailAssistantDescription.model_dump_json())
async def analyze_and_rewrite_email(
    email_draft: Annotated[str, Field(description="The user's draft email text.")],
    target_tone: Annotated[str, Field(description="The desired tone for the rewritten email. Examples: 'Formal', 'Friendly but Professional', 'Confident', 'Persuasive', 'Concise'.")]
) -> str:
    """Analyzes and rewrites an email draft to match a target tone using Google Gemini."""
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash') # Using the fast and free model

        prompt = f"""
        You are an expert communication assistant. Analyze the following email draft and rewrite it to match the target tone.

        **Target Tone:** {target_tone}

        **Email Draft:**
        ---
        {email_draft}
        ---

        Please provide your response in three sections using Markdown:
        1.  **Current Tone Analysis:** A brief, one-sentence analysis of the draft's current tone.
        2.  **Key Suggestions:** A bulleted list of 2-3 specific, actionable suggestions for how to improve the draft to meet the target tone.
        3.  **Rewritten Version:** A complete rewrite of the email in the desired "{target_tone}" style.
        """
        
        def make_gemini_call():
            response = model.generate_content(prompt)
            return response.text

        response = await asyncio.to_thread(make_gemini_call)
        return response
    except Exception as e:
        raise McpError(ErrorData(code=INTERNAL_ERROR, message=f"Failed to process email with Google AI: {e!r}"))

# --- Run MCP Server ---
async def main():
    port = int(os.environ.get("PORT", 8088))
    print(f"🚀 Starting AI Email Assistant Server on http://0.0.0.0:{port}")
    await mcp.run_async("streamable-http", host="0.0.0.0", port=port)

if __name__ == "__main__":
    asyncio.run(main())
