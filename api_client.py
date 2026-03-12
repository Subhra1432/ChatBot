"""
API Client module for the ChatBot application.
Supports multiple LLM providers (Groq, OpenAI) and web search.
"""

import json
import os
import shutil
import requests
import re
from urllib.parse import quote_plus
from bs4 import BeautifulSoup


class APIClient:
    """Handles all API interactions for the chatbot."""

    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.config = self._load_config(config_path)
        self.conversation_history = []
        self.system_prompt = self.config.get("system_prompt", "You are a helpful assistant.")

    def _load_config(self, config_path):
        # Auto-create config.json from template if missing
        if not os.path.exists(config_path):
            template = os.path.join(os.path.dirname(config_path), "config.example.json")
            if os.path.exists(template):
                shutil.copy(template, config_path)
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "api_provider": "groq",
                "groq_api_key": "",
                "groq_model": "llama-3.3-70b-versatile",
                "openai_api_key": "",
                "openai_model": "gpt-3.5-turbo",
                "max_tokens": 4096,
                "temperature": 0.7,
                "system_prompt": "You are a helpful assistant.",
                "web_search_enabled": True,
                "chat_history_limit": 50,
            }

    def save_config(self, config_path=None):
        path = config_path or self.config_path
        with open(path, "w") as f:
            json.dump(self.config, f, indent=4)

    def update_config(self, **kwargs):
        self.config.update(kwargs)
        if "system_prompt" in kwargs:
            self.system_prompt = kwargs["system_prompt"]
        self.save_config()

    def clear_history(self):
        self.conversation_history = []

    # -- LLM Chat ------------------------------------------------------

    def chat(self, user_message: str) -> str:
        """Send a message and get a response from the configured LLM provider."""
        self.conversation_history.append({"role": "user", "content": user_message})

        # Trim history
        limit = self.config.get("chat_history_limit", 50)
        if len(self.conversation_history) > limit:
            self.conversation_history = self.conversation_history[-limit:]

        provider = self.config.get("api_provider", "groq")
        try:
            if provider == "groq":
                response = self._call_groq()
            elif provider == "openai":
                response = self._call_openai()
            else:
                response = "[Error] Unknown API provider. Please check settings."
        except Exception as e:
            response = f"[Error] API Error: {str(e)}"

        self.conversation_history.append({"role": "assistant", "content": response})
        return response

    def _build_messages(self):
        return [{"role": "system", "content": self.system_prompt}] + self.conversation_history

    def _call_groq(self) -> str:
        api_key = self.config.get("groq_api_key", "")
        if not api_key or api_key == "YOUR_GROQ_API_KEY_HERE":
            return (
                "Groq API key not configured.\n\n"
                "To get a FREE API key:\n"
                "1. Go to https://console.groq.com\n"
                "2. Sign up and create an API key\n"
                "3. Open Settings and paste your key\n\n"
                "Groq offers free access to Llama, Mixtral, and Gemma models!"
            )

        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.config.get("groq_model", "llama-3.3-70b-versatile"),
            "messages": self._build_messages(),
            "max_tokens": self.config.get("max_tokens", 4096),
            "temperature": self.config.get("temperature", 0.7),
        }

        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]

    def _call_openai(self) -> str:
        api_key = self.config.get("openai_api_key", "")
        if not api_key or api_key == "YOUR_OPENAI_API_KEY_HERE":
            return (
                "OpenAI API key not configured.\n\n"
                "1. Go to https://platform.openai.com/api-keys\n"
                "2. Create a new API key\n"
                "3. Open Settings and paste your key"
            )

        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.config.get("openai_model", "gpt-3.5-turbo"),
            "messages": self._build_messages(),
            "max_tokens": self.config.get("max_tokens", 4096),
            "temperature": self.config.get("temperature", 0.7),
        }

        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]

    # -- Web Search ----------------------------------------------------

    def web_search(self, query: str, num_results: int = 5) -> str:
        """Perform a web search using DuckDuckGo HTML (no API key needed)."""
        try:
            url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            }
            resp = requests.get(url, headers=headers, timeout=15)
            resp.raise_for_status()

            soup = BeautifulSoup(resp.text, "html.parser")
            results = []

            for i, result in enumerate(soup.select(".result"), 1):
                if i > num_results:
                    break
                title_tag = result.select_one(".result__title a")
                snippet_tag = result.select_one(".result__snippet")
                if title_tag:
                    title = title_tag.get_text(strip=True)
                    link = title_tag.get("href", "")
                    snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""
                    results.append(f"**{i}. {title}**\n   {snippet}\n   Link: {link}")

            if results:
                return f"Search results for: **{query}**\n\n" + "\n\n".join(results)
            else:
                return f"No results found for: {query}"
        except Exception as e:
            return f"[Error] Search error: {str(e)}"

    def fetch_webpage(self, url: str) -> str:
        """Fetch and extract text content from a webpage."""
        try:
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            }
            resp = requests.get(url, headers=headers, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            # Remove script/style elements
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()

            text = soup.get_text(separator="\n", strip=True)
            # Collapse blank lines
            text = re.sub(r"\n{3,}", "\n\n", text)
            # Limit length
            if len(text) > 5000:
                text = text[:5000] + "\n\n... (content truncated)"

            return f"Content from {url}:\n\n{text}"
        except Exception as e:
            return f"[Error] Failed to fetch page: {str(e)}"
