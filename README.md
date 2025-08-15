# 🤖 AI Email Assistant for Puch AI

An intelligent tool built for the **Puch AI Hackathon** that serves as a personal communication assistant. This server provides a suite of tools to analyze, rewrite, shorten, and expand email drafts, helping users communicate more effectively. The project is deployed permanently on Render and is powered by Google's Gemini API.

## ✨ Core Features

This project isn't just one tool, but a **suite of four distinct functions** to provide a comprehensive email-crafting experience:

* **`analyze_email_tone`**: Analyzes the tone of a draft and provides actionable feedback and suggestions for improvement.
* **`rewrite_email`**: Rewrites an entire email draft to match a specific target tone (e.g., "Formal," "Confident," "Friendly").
* **`shorten_email`**: Condenses a verbose email into a concise and clear message while retaining the core meaning.
* **`expand_from_bullets`**: Takes a simple list of bullet points and expands it into a fully-formed, professional email.

## 🛠️ Tech Stack

* **Framework**: FastMCP
* **AI Model**: Google Gemini 1.5 Flash
* **Deployment**: Render (for permanent, 24/7 hosting)
* **Primary Libraries**: `google-generativeai`, `fastmcp`, `python-dotenv`

## 🚀 Deployment

This server is permanently deployed as a web service on Render, automatically rebuilding and deploying upon any new commit to the `main` branch. Environment variables for API keys and authentication tokens are managed securely through the Render dashboard.

## 💻 Local Development Setup

To run this server on your own computer for development and testing, follow these steps:

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/akshata-13/puch-email-assistant.git](https://github.com/akshata-13/puch-email-assistant.git)
    cd puch-email-assistant
    ```

2.  **Create a Virtual Environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows, use `\.venv\Scripts\activate`
    ```

3.  **Install Dependencies:**
    The project uses `pyproject.toml` to manage dependencies. Install them with pip:
    ```bash
    pip install .
    ```

4.  **Configure Environment Variables:**
    Create a file named `.env` in the root directory and add your secret keys (see Configuration section below).

5.  **Run the Server:**
    ```bash
    python mcp_starter.py
    ```
    The server will start on a local port, and you can use a tool like `ngrok` to expose it for testing with the Puch AI platform.

---

##  Configuration

The server requires the following environment variables to be set in a `.env` file for local development or in the hosting environment (e.g., Render) for deployment.

| Variable         | Description                                                                                 |
| :--------------- | :------------------------------------------------------------------------------------------ |
| `AUTH_TOKEN`     | A secret token you create to authenticate the connection between Puch AI and your server.     |
| `MY_NUMBER`      | Your phone number in `+countrycodephonenumber` format, required for the `validate` tool.      |
| `GOOGLE_API_KEY` | Your API key from the Google AI Studio to access the Gemini model.                            |
