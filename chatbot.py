"""
Modern ChatBot - Tkinter GUI
A sleek, dark-themed chatbot with LLM and web-search integration.
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog, filedialog
import threading
import json
import re
import os
import datetime

from api_client import APIClient

# -- Resolve base path (works for both dev and PyInstaller bundle) -----
import sys
if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
    # On macOS .app, the exe is inside Contents/MacOS
    if sys.platform == "darwin" and "Contents/MacOS" in BASE_DIR:
        BASE_DIR = os.path.join(BASE_DIR, "..", "..", "..")
        BASE_DIR = os.path.normpath(BASE_DIR)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# -- Colour palette ----------------------------------------------------
BG_DARK       = "#1a1b26"    # main background
BG_SIDEBAR    = "#16161e"    # sidebar
BG_INPUT      = "#24283b"    # input area
BG_MSG_USER   = "#3d59a1"    # user bubble
BG_MSG_BOT    = "#292e42"    # bot bubble
BG_CODE       = "#1e2030"    # code block background
FG_PRIMARY    = "#c0caf5"    # main text
FG_SECONDARY  = "#565f89"    # muted text
FG_ACCENT     = "#7aa2f7"    # accent / links
FG_GREEN      = "#9ece6a"    # success highlights
FG_ORANGE     = "#e0af68"    # warning highlights
FG_RED        = "#f7768e"    # error highlights
BORDER_COLOR  = "#292e42"    # subtle borders
HOVER_COLOR   = "#33394e"    # hover effect


class ChatBotApp:
    """Main application window."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("ChatBot - Code & Research Assistant")
        self.root.geometry("1100x750")
        self.root.minsize(800, 550)
        self.root.configure(bg=BG_DARK)

        # Client
        config_path = os.path.join(BASE_DIR, "config.json")
        self.client = APIClient(config_path)
        self.is_processing = False
        self.chat_sessions = [{"name": "New Chat", "history": []}]
        self.current_session = 0

        self._build_ui()
        self._show_welcome()

    # -- UI Construction -----------------------------------------------

    def _build_ui(self):
        # Top bar
        top = tk.Frame(self.root, bg=BG_SIDEBAR, height=50)
        top.pack(fill=tk.X)
        top.pack_propagate(False)

        tk.Label(
            top, text="ChatBot", font=("Helvetica", 16, "bold"),
            bg=BG_SIDEBAR, fg=FG_ACCENT,
        ).pack(side=tk.LEFT, padx=16)

        # Top-bar buttons (right side)
        btn_cfg = dict(
            font=("Helvetica", 12), bg=BG_SIDEBAR, fg=FG_SECONDARY,
            bd=0, padx=10, activebackground=HOVER_COLOR,
            activeforeground=FG_PRIMARY, cursor="hand2",
        )

        tk.Button(top, text="Settings", command=self._open_settings, **btn_cfg).pack(side=tk.RIGHT, padx=4)
        tk.Button(top, text="Export", command=self._export_chat, **btn_cfg).pack(side=tk.RIGHT, padx=4)
        tk.Button(top, text="Clear", command=self._clear_chat, **btn_cfg).pack(side=tk.RIGHT, padx=4)

        # Provider label
        provider = self.client.config.get("api_provider", "groq").upper()
        model = self.client.config.get(
            f"{self.client.config.get('api_provider','groq')}_model", ""
        )
        self.provider_label = tk.Label(
            top,
            text=f"{provider} | {model}",
            font=("Helvetica", 10),
            bg=BG_SIDEBAR, fg=FG_SECONDARY,
        )
        self.provider_label.pack(side=tk.RIGHT, padx=12)

        # -- Main area -------------------------------------------------
        main = tk.Frame(self.root, bg=BG_DARK)
        main.pack(fill=tk.BOTH, expand=True)

        # Sidebar
        self.sidebar = tk.Frame(main, bg=BG_SIDEBAR, width=220)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        tk.Label(
            self.sidebar, text="Sessions",
            font=("Helvetica", 12, "bold"), bg=BG_SIDEBAR, fg=FG_PRIMARY,
        ).pack(pady=(16, 8), padx=12, anchor="w")

        tk.Button(
            self.sidebar, text="+  New Chat", font=("Helvetica", 11),
            bg=FG_ACCENT, fg=BG_DARK, bd=0, pady=6,
            activebackground="#5a8af7", activeforeground=BG_DARK,
            cursor="hand2", command=self._new_session,
        ).pack(fill=tk.X, padx=12, pady=(0, 8))

        self.session_list = tk.Frame(self.sidebar, bg=BG_SIDEBAR)
        self.session_list.pack(fill=tk.BOTH, expand=True, padx=8)

        # Quick-action buttons
        qa_frame = tk.Frame(self.sidebar, bg=BG_SIDEBAR)
        qa_frame.pack(fill=tk.X, padx=12, pady=(0, 12))

        for label, cmd in [
            ("Web Search", self._web_search_prompt),
            ("Fetch URL", self._fetch_url_prompt),
        ]:
            tk.Button(
                qa_frame, text=label, font=("Helvetica", 10),
                bg=BG_INPUT, fg=FG_PRIMARY, bd=0, pady=4,
                activebackground=HOVER_COLOR, activeforeground=FG_PRIMARY,
                cursor="hand2", command=cmd,
            ).pack(fill=tk.X, pady=2)

        self._refresh_session_list()

        # Chat display
        chat_frame = tk.Frame(main, bg=BG_DARK)
        chat_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.chat_display = scrolledtext.ScrolledText(
            chat_frame, wrap=tk.WORD, font=("Menlo", 12),
            bg=BG_DARK, fg=FG_PRIMARY, insertbackground=FG_PRIMARY,
            selectbackground=FG_ACCENT, selectforeground=BG_DARK,
            bd=0, padx=20, pady=16, state=tk.DISABLED, spacing3=4,
            relief=tk.FLAT,
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)

        # Configure text tags for rich formatting
        self.chat_display.tag_configure("user_name", foreground=FG_ACCENT, font=("Helvetica", 11, "bold"))
        self.chat_display.tag_configure("bot_name", foreground=FG_GREEN, font=("Helvetica", 11, "bold"))
        self.chat_display.tag_configure("user_msg", foreground=FG_PRIMARY, font=("Menlo", 12), lmargin1=16, lmargin2=16)
        self.chat_display.tag_configure("bot_msg", foreground=FG_PRIMARY, font=("Menlo", 12), lmargin1=16, lmargin2=16)
        self.chat_display.tag_configure("code_block", foreground=FG_ORANGE, background=BG_CODE, font=("Menlo", 11), lmargin1=24, lmargin2=24, rmargin=24, spacing1=4, spacing3=4)
        self.chat_display.tag_configure("inline_code", foreground=FG_ORANGE, background=BG_CODE, font=("Menlo", 11))
        self.chat_display.tag_configure("bold_text", font=("Helvetica", 12, "bold"))
        self.chat_display.tag_configure("timestamp", foreground=FG_SECONDARY, font=("Helvetica", 9))
        self.chat_display.tag_configure("divider", foreground=BORDER_COLOR)
        self.chat_display.tag_configure("system", foreground=FG_SECONDARY, font=("Helvetica", 11, "italic"), justify="center")
        self.chat_display.tag_configure("error", foreground=FG_RED, font=("Menlo", 12), lmargin1=16, lmargin2=16)
        self.chat_display.tag_configure("search", foreground=FG_GREEN, font=("Menlo", 12), lmargin1=16, lmargin2=16)

        # -- Input bar -------------------------------------------------
        input_bar = tk.Frame(self.root, bg=BG_INPUT, pady=10)
        input_bar.pack(fill=tk.X)

        inner = tk.Frame(input_bar, bg=BG_INPUT)
        inner.pack(fill=tk.X, padx=16)

        self.input_box = tk.Text(
            inner, height=2, wrap=tk.WORD, font=("Menlo", 13),
            bg=BG_DARK, fg=FG_PRIMARY, insertbackground=FG_PRIMARY,
            selectbackground=FG_ACCENT, bd=0, padx=12, pady=8,
            relief=tk.FLAT,
        )
        self.input_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
        self.input_box.bind("<Return>", self._on_enter)
        self.input_box.bind("<Shift-Return>", lambda e: None)  # allow newline

        self.send_btn = tk.Button(
            inner, text="  Send >  ", font=("Helvetica", 13, "bold"),
            bg=FG_ACCENT, fg=BG_DARK, bd=0, padx=18, pady=8,
            activebackground="#5a8af7", activeforeground=BG_DARK,
            cursor="hand2", command=self._send_message,
        )
        self.send_btn.pack(side=tk.RIGHT)

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = tk.Label(
            self.root, textvariable=self.status_var,
            font=("Helvetica", 10), bg=BG_SIDEBAR, fg=FG_SECONDARY,
            anchor="w", padx=16, pady=4,
        )
        status_bar.pack(fill=tk.X)

        # Focus input
        self.input_box.focus_set()

    # -- Session management --------------------------------------------

    def _refresh_session_list(self):
        for w in self.session_list.winfo_children():
            w.destroy()
        for i, session in enumerate(self.chat_sessions):
            is_active = i == self.current_session
            bg = HOVER_COLOR if is_active else BG_SIDEBAR
            fg = FG_PRIMARY if is_active else FG_SECONDARY
            btn = tk.Button(
                self.session_list, text=f"  {session['name']}",
                font=("Helvetica", 11), bg=bg, fg=fg, bd=0,
                anchor="w", padx=8, pady=6,
                activebackground=HOVER_COLOR, activeforeground=FG_PRIMARY,
                cursor="hand2", command=lambda idx=i: self._switch_session(idx),
            )
            btn.pack(fill=tk.X, pady=1)

    def _new_session(self):
        self.chat_sessions.append({"name": f"Chat {len(self.chat_sessions) + 1}", "history": []})
        self.current_session = len(self.chat_sessions) - 1
        self.client.clear_history()
        self._refresh_session_list()
        self._clear_display()
        self._show_welcome()

    def _switch_session(self, idx):
        # Save current
        self.chat_sessions[self.current_session]["history"] = list(self.client.conversation_history)
        self.current_session = idx
        self.client.conversation_history = list(self.chat_sessions[idx]["history"])
        self._refresh_session_list()
        self._rebuild_display()

    def _rebuild_display(self):
        self._clear_display()
        history = self.chat_sessions[self.current_session]["history"]
        for msg in history:
            if msg["role"] == "user":
                self._append_message("You", msg["content"], is_user=True)
            else:
                self._append_message("ChatBot", msg["content"], is_user=False)

    # -- Message handling ----------------------------------------------

    def _on_enter(self, event):
        if not event.state & 0x1:  # Shift not held
            self._send_message()
            return "break"

    def _send_message(self):
        text = self.input_box.get("1.0", tk.END).strip()
        if not text or self.is_processing:
            return

        self.input_box.delete("1.0", tk.END)
        self._append_message("You", text, is_user=True)

        # Check for slash commands
        if text.startswith("/search "):
            query = text[8:].strip()
            self._run_async(lambda: self.client.web_search(query), tag="search")
            return
        elif text.startswith("/fetch "):
            url = text[7:].strip()
            self._run_async(lambda: self.client.fetch_webpage(url), tag="search")
            return
        elif text == "/help":
            self._show_help()
            return
        elif text == "/clear":
            self._clear_chat()
            return

        # Normal chat
        self._run_async(lambda: self.client.chat(text))

    def _run_async(self, fn, tag=None):
        self.is_processing = True
        self.send_btn.configure(state=tk.DISABLED, text="  ...  ")
        self.status_var.set("Thinking...")

        def worker():
            try:
                result = fn()
            except Exception as e:
                result = f"[Error] {e}"
                tag_override = "error"
            else:
                tag_override = tag
            self.root.after(0, lambda: self._on_response(result, tag_override))

        threading.Thread(target=worker, daemon=True).start()

    def _on_response(self, text, tag=None):
        self.is_processing = False
        self.send_btn.configure(state=tk.NORMAL, text="  Send >  ")
        self.status_var.set("Ready")
        self._append_message("ChatBot", text, is_user=False, tag=tag)
        # Update session name from first user message
        session = self.chat_sessions[self.current_session]
        if session["name"].startswith(("New Chat", "Chat ")) and self.client.conversation_history:
            first_msg = self.client.conversation_history[0]["content"]
            session["name"] = (first_msg[:28] + "...") if len(first_msg) > 28 else first_msg
            self._refresh_session_list()
        session["history"] = list(self.client.conversation_history)

    # -- Display helpers -----------------------------------------------

    def _append_message(self, sender, text, is_user=False, tag=None):
        self.chat_display.configure(state=tk.NORMAL)
        ts = datetime.datetime.now().strftime("%H:%M")

        # Sender line
        name_tag = "user_name" if is_user else "bot_name"
        icon = ">" if is_user else "<"
        self.chat_display.insert(tk.END, f"\n {icon} {sender}  ", name_tag)
        self.chat_display.insert(tk.END, f"{ts}\n", "timestamp")

        # Body - render with basic markdown-like formatting
        if tag == "error":
            self.chat_display.insert(tk.END, text + "\n", "error")
        elif tag == "search":
            self.chat_display.insert(tk.END, text + "\n", "search")
        else:
            self._render_markdown(text)

        self.chat_display.insert(tk.END, "\n", "divider")
        self.chat_display.configure(state=tk.DISABLED)
        self.chat_display.see(tk.END)

    def _render_markdown(self, text: str):
        """Minimal markdown renderer: code blocks, inline code, bold."""
        parts = re.split(r"(```[\s\S]*?```)", text)
        for part in parts:
            if part.startswith("```") and part.endswith("```"):
                code = part[3:-3]
                # Strip optional language hint on first line
                if code and code[0] != "\n":
                    code = code.split("\n", 1)[-1] if "\n" in code else code
                self.chat_display.insert(tk.END, code.strip() + "\n", "code_block")
            else:
                # Handle inline code
                segments = re.split(r"(`[^`]+`)", part)
                for seg in segments:
                    if seg.startswith("`") and seg.endswith("`"):
                        self.chat_display.insert(tk.END, seg[1:-1], "inline_code")
                    else:
                        # Bold
                        bold_parts = re.split(r"(\*\*[^*]+\*\*)", seg)
                        for bp in bold_parts:
                            if bp.startswith("**") and bp.endswith("**"):
                                self.chat_display.insert(tk.END, bp[2:-2], "bold_text")
                            else:
                                tag = "user_msg" if False else "bot_msg"
                                self.chat_display.insert(tk.END, bp, "bot_msg")

    def _clear_display(self):
        self.chat_display.configure(state=tk.NORMAL)
        self.chat_display.delete("1.0", tk.END)
        self.chat_display.configure(state=tk.DISABLED)

    def _show_welcome(self):
        self.chat_display.configure(state=tk.NORMAL)
        welcome = (
            "\n\n"
            "         Welcome to ChatBot\n"
            "       Your Code & Research Assistant\n\n"
            "   -------------------------------------\n\n"
            "   Quick start:\n\n"
            "     *  Just type a message to chat with the AI\n"
            "     *  /search <query>   -> Web search\n"
            "     *  /fetch <url>      -> Extract page content\n"
            "     *  /help             -> Show all commands\n"
            "     *  /clear            -> Clear conversation\n\n"
            "   Configure your API key in Settings\n"
            "       (Groq is FREE - recommended!)\n\n"
            "   -------------------------------------\n"
        )
        self.chat_display.insert(tk.END, welcome, "system")
        self.chat_display.configure(state=tk.DISABLED)

    def _show_help(self):
        help_text = (
            "**Available Commands:**\n\n"
            "  /search <query>  - Search the web (DuckDuckGo)\n"
            "  /fetch <url>     - Fetch & extract webpage text\n"
            "  /clear           - Clear the conversation\n"
            "  /help            - Show this help message\n\n"
            "**Tips:**\n"
            "  * Shift+Enter for multi-line input\n"
            "  * Use the sidebar buttons for quick actions\n"
            "  * Code blocks in responses are highlighted\n"
            "  * Export your chat with the Export button\n"
        )
        self._append_message("ChatBot", help_text, is_user=False)

    # -- Actions -------------------------------------------------------

    def _clear_chat(self):
        self.client.clear_history()
        self.chat_sessions[self.current_session]["history"] = []
        self._clear_display()
        self._show_welcome()
        self.status_var.set("Chat cleared")

    def _web_search_prompt(self):
        query = simpledialog.askstring("Web Search", "Enter search query:", parent=self.root)
        if query:
            self._append_message("You", f"/search {query}", is_user=True)
            self._run_async(lambda: self.client.web_search(query), tag="search")

    def _fetch_url_prompt(self):
        url = simpledialog.askstring("Fetch URL", "Enter URL to fetch:", parent=self.root)
        if url:
            self._append_message("You", f"/fetch {url}", is_user=True)
            self._run_async(lambda: self.client.fetch_webpage(url), tag="search")

    def _export_chat(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Markdown", "*.md"), ("Text", "*.txt")],
            title="Export Chat",
        )
        if not path:
            return
        try:
            with open(path, "w") as f:
                f.write(f"# ChatBot Export - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
                for msg in self.client.conversation_history:
                    role = "You" if msg["role"] == "user" else "ChatBot"
                    f.write(f"## {role}\n\n{msg['content']}\n\n---\n\n")
            self.status_var.set(f"Chat exported to {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    # -- Settings dialog -----------------------------------------------

    def _open_settings(self):
        win = tk.Toplevel(self.root)
        win.title("Settings")
        win.geometry("520x620")
        win.configure(bg=BG_DARK)
        win.transient(self.root)
        win.grab_set()

        canvas = tk.Canvas(win, bg=BG_DARK, highlightthickness=0)
        scrollbar = tk.Scrollbar(win, orient="vertical", command=canvas.yview)
        frame = tk.Frame(canvas, bg=BG_DARK)
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        cfg = self.client.config
        entries = {}

        def add_section(title):
            tk.Label(
                frame, text=title, font=("Helvetica", 13, "bold"),
                bg=BG_DARK, fg=FG_ACCENT,
            ).pack(anchor="w", padx=20, pady=(16, 4))
            tk.Frame(frame, bg=BORDER_COLOR, height=1).pack(fill=tk.X, padx=20, pady=(0, 8))

        def add_field(label, key, show=None):
            tk.Label(
                frame, text=label, font=("Helvetica", 11),
                bg=BG_DARK, fg=FG_PRIMARY,
            ).pack(anchor="w", padx=24, pady=(4, 0))
            e = tk.Entry(
                frame, font=("Menlo", 11), bg=BG_INPUT, fg=FG_PRIMARY,
                insertbackground=FG_PRIMARY, bd=0, relief=tk.FLAT,
                show=show,
            )
            e.pack(fill=tk.X, padx=24, pady=(2, 4), ipady=6)
            e.insert(0, str(cfg.get(key, "")))
            entries[key] = e

        def add_dropdown(label, key, options):
            tk.Label(
                frame, text=label, font=("Helvetica", 11),
                bg=BG_DARK, fg=FG_PRIMARY,
            ).pack(anchor="w", padx=24, pady=(4, 0))
            var = tk.StringVar(value=str(cfg.get(key, options[0])))
            menu = tk.OptionMenu(frame, var, *options)
            menu.configure(
                font=("Menlo", 11), bg=BG_INPUT, fg=FG_PRIMARY,
                activebackground=HOVER_COLOR, activeforeground=FG_PRIMARY,
                bd=0, highlightthickness=0,
            )
            menu.pack(fill=tk.X, padx=24, pady=(2, 4))
            entries[key] = var

        # Sections
        add_section("API Provider")
        add_dropdown("Provider", "api_provider", ["groq", "openai"])

        add_section("Groq (Free)")
        add_field("API Key", "groq_api_key", show="*")
        add_dropdown("Model", "groq_model", [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768",
            "gemma2-9b-it",
        ])

        add_section("OpenAI")
        add_field("API Key", "openai_api_key", show="*")
        add_dropdown("openai_model", "openai_model", [
            "gpt-3.5-turbo",
            "gpt-4",
            "gpt-4-turbo",
            "gpt-4o",
            "gpt-4o-mini",
        ])

        add_section("Generation")
        add_field("Max Tokens", "max_tokens")
        add_field("Temperature (0.0 - 2.0)", "temperature")

        add_section("System Prompt")
        tk.Label(
            frame, text="System prompt (instructions for the AI):",
            font=("Helvetica", 11), bg=BG_DARK, fg=FG_PRIMARY,
        ).pack(anchor="w", padx=24, pady=(4, 0))
        sp_box = tk.Text(
            frame, height=5, wrap=tk.WORD, font=("Menlo", 11),
            bg=BG_INPUT, fg=FG_PRIMARY, insertbackground=FG_PRIMARY,
            bd=0, relief=tk.FLAT, padx=8, pady=6,
        )
        sp_box.pack(fill=tk.X, padx=24, pady=(2, 8))
        sp_box.insert("1.0", cfg.get("system_prompt", ""))
        entries["system_prompt"] = sp_box

        # Save button
        def save():
            try:
                new_cfg = {}
                for key, widget in entries.items():
                    if isinstance(widget, tk.Text):
                        new_cfg[key] = widget.get("1.0", tk.END).strip()
                    elif isinstance(widget, tk.StringVar):
                        new_cfg[key] = widget.get()
                    else:
                        new_cfg[key] = widget.get().strip()

                # Convert numeric fields
                new_cfg["max_tokens"] = int(new_cfg.get("max_tokens", 4096))
                new_cfg["temperature"] = float(new_cfg.get("temperature", 0.7))

                self.client.update_config(**new_cfg)

                # Update provider label
                provider = new_cfg.get("api_provider", "groq").upper()
                model = new_cfg.get(f"{new_cfg.get('api_provider','groq')}_model", "")
                self.provider_label.configure(text=f"{provider} | {model}")

                self.status_var.set("Settings saved")
                win.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=win)

        tk.Button(
            frame, text="  Save Settings  ", font=("Helvetica", 13, "bold"),
            bg=FG_ACCENT, fg=BG_DARK, bd=0, padx=20, pady=8,
            activebackground="#5a8af7", cursor="hand2", command=save,
        ).pack(pady=20)


# -- Entry point -------------------------------------------------------

def main():
    root = tk.Tk()
    # macOS dark title bar
    try:
        root.tk.call("::tk::unsupported::MacWindowStyle", "style", root._w, "moveableModal", "")
    except tk.TclError:
        pass
    app = ChatBotApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
