#!/usr/bin/env python3
"""
APEX Super Pro OpenClaw — Interactive Terminal UI (TUI)
Engineered for real-time streaming, rich markdown rendering, and autonomous agent loops.
Doctrine: Holographic Mesh | Operator: Casey Barton / GlacierEQ
"""

import sys
import os
import json
import time
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.live import Live
from rich.spinner import Spinner
from rich.text import Text
from rich.layout import Layout

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import WordCompleter, Completer, Completion
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import HTML

# Import Core Engine
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
from openclaw_core import SuperProOpenClaw, PROVIDERS, CASES

console = Console()

class OpenClawCompleter(Completer):
    """Context-aware auto-completion for slash commands and arguments."""
    def __init__(self):
        self.commands = [
            "/agent", "/chat", "/model", "/provider", "/device",
            "/fts", "/legal", "/motion", "/memory", "/status",
            "/clear", "/help", "/web", "/exit", "/quit"
        ]
        self.providers = list(PROVIDERS.keys())
        self.device_actions = ["battery", "toast", "notify", "speak", "vibrate", "clip", "torch", "status"]
        self.cases = list(CASES.keys())
        self.motions = ["rule60b", "spoliation", "recusal"]
        self.mem_actions = ["list", "get", "set", "search"]

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        words = text.split()
        
        if not words or (len(words) == 1 and not text.endswith(" ")):
            prefix = words[0] if words else ""
            for cmd in self.commands:
                if cmd.startswith(prefix):
                    yield Completion(cmd, start_position=-len(prefix))
            return

        cmd = words[0].lower()
        sub = words[1] if len(words) > 1 else ""
        prefix = words[-1] if not text.endswith(" ") else ""

        if cmd in ["/model", "/provider"]:
            for p in self.providers:
                if p.startswith(prefix):
                    yield Completion(p, start_position=-len(prefix))
        elif cmd in ["/device", "/dev"]:
            for d in self.device_actions:
                if d.startswith(prefix):
                    yield Completion(d, start_position=-len(prefix))
        elif cmd in ["/legal", "/case"]:
            for c in self.cases:
                if c.startswith(prefix.upper()):
                    yield Completion(c, start_position=-len(prefix))
        elif cmd in ["/motion"]:
            for m in self.motions:
                if m.startswith(prefix):
                    yield Completion(m, start_position=-len(prefix))
        elif cmd in ["/memory", "/mem"]:
            for ma in self.mem_actions:
                if ma.startswith(prefix):
                    yield Completion(ma, start_position=-len(prefix))

class OpenClawTUI:
    def __init__(self):
        self.claw = SuperProOpenClaw()
        self.active_provider = "groq"
        self.active_model = PROVIDERS["groq"]["default_model"]
        self.auto_tools = True
        self.history_file = Path("/data/data/com.termux/files/home/.openclaw/tui_history.txt")
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        self.session = PromptSession(
            history=FileHistory(str(self.history_file)),
            completer=OpenClawCompleter()
        )

    def print_banner(self):
        console.clear()
        title = Text("⚡ APEX SUPER PRO OPENCLAW v20.0 ⚡", style="bold cyan")
        subtitle = Text("Interactive Agentic Workspace · Holographic Mesh Engine", style="dim white")
        meta = Table.grid(padding=(0, 2))
        meta.add_row(
            f"[bold green]Operator:[/] Casey Barton / GlacierEQ",
            f"[bold magenta]Active Mesh:[/] {self.active_provider.upper()} ({self.active_model})",
            f"[bold yellow]Posture:[/] Hard · Pro · Elite · G"
        )
        banner_content = Table.grid(padding=(0, 1))
        banner_content.add_row(title)
        banner_content.add_row(subtitle)
        banner_content.add_row("")
        banner_content.add_row(meta)
        
        console.print(Panel(banner_content, border_style="cyan", padding=(1, 2)))
        console.print("[dim]Type your message or request. Use [bold cyan]/help[/] for commands, [bold cyan]/tools[/] to toggle auto-tools.[/dim]\n")

    def bottom_toolbar(self):
        try:
            tools_badge = '<style fg="#00ffcc">ON</style>' if self.auto_tools else '<style fg="#ff4444">OFF</style>'
            return HTML(
                f'<b><style bg="#005577" fg="#ffffff"> OPENCLAW </style></b> '
                f'Provider: <b><style fg="#00ffcc">{self.active_provider.upper()}</style></b> '
                f'Model: <style fg="#ffff00">{self.active_model}</style> | '
                f'Tools: <b>{tools_badge}</b> | '
                f'<style fg="#888888">Type /help | Ctrl+D to exit</style>'
            )
        except Exception:
            return ""

    def handle_slash_command(self, line: str) -> bool:
        """Processes slash commands. Returns True if handled, False if exit requested."""
        parts = line.strip().split(maxsplit=1)
        cmd = parts[0].lower()
        arg = parts[1].strip() if len(parts) > 1 else ""

        if cmd in ["/exit", "/quit", ":q"]:
            console.print("[bold yellow]Exiting OpenClaw TUI. Mesh remains persistent.[/bold yellow]")
            return False

        elif cmd in ["/clear", "/cls"]:
            self.print_banner()

        elif cmd in ["/status", "/s"]:
            with console.status("[bold cyan]Querying holographic mesh telemetry...[/bold cyan]", spinner="dots"):
                st = self.claw.system_status()
            
            table = Table(title="APEX Mesh Telemetry", border_style="cyan")
            table.add_column("Subsystem", style="bold green")
            table.add_column("Status / Detail", style="white")
            
            table.add_row("Engine", f"{st['engine']} (v{st['version']})")
            table.add_row("Operator", st['operator'])
            table.add_row("Doctrine", st['doctrine'])
            table.add_row("Chat Records", f"{st['databases']['chat_forensics']['rows']:,} rows (FTS5 active)")
            table.add_row("Aspen Memory", f"{st['memory_substrate']['active_pointers']} pointers ({st['memory_substrate']['status']})")
            
            p_text = ", ".join([f"{k.upper()}: {'✓' if v else '✗'}" for k, v in st['api_keys'].items()])
            table.add_row("AI Providers", p_text)
            console.print(table)
            console.print()

        elif cmd in ["/model", "/models", "/provider"]:
            if not arg:
                table = Table(title="Configured Mesh Providers", border_style="magenta")
                table.add_column("Provider ID", style="bold cyan")
                table.add_column("Name", style="white")
                table.add_column("Default Model", style="yellow")
                table.add_column("Models Available", style="dim")
                for p_id, cfg in PROVIDERS.items():
                    active_marker = " [bold green]● ACTIVE[/bold green]" if p_id == self.active_provider else ""
                    table.add_row(p_id + active_marker, cfg["name"], cfg["default_model"], ", ".join(cfg["models"]))
                console.print(table)
                console.print("[dim]Switch provider via: [bold cyan]/provider <id>[/] or [bold cyan]/model <id> <model>[/dim]\n")
            else:
                p_parts = arg.split(maxsplit=1)
                target_p = p_parts[0].lower()
                if target_p in PROVIDERS:
                    self.active_provider = target_p
                    if len(p_parts) > 1:
                        self.active_model = p_parts[1]
                    else:
                        self.active_model = PROVIDERS[target_p]["default_model"]
                    console.print(f"[bold green]✓ Switched mesh route to {self.active_provider.upper()} ({self.active_model})[/bold green]\n")
                else:
                    console.print(f"[bold red]Unknown provider '{target_p}'. Available: {list(PROVIDERS.keys())}[/bold red]\n")

        elif cmd in ["/device", "/dev", "/hw"]:
            if not arg:
                console.print("[dim]Usage: /device <battery|toast|notify|speak|vibrate|clip|torch>[/dim]\n")
            else:
                d_parts = arg.split(maxsplit=1)
                act = d_parts[0].lower()
                d_args = d_parts[1].split() if len(d_parts) > 1 else []
                with console.status(f"[bold yellow]Executing device action: {act}...[/bold yellow]", spinner="aesthetic"):
                    res = self.claw.device_control(act, *d_args)
                console.print(Panel(Syntax(json.dumps(res, indent=2), "json", theme="monokai"), title=f"Hardware Result: {act}", border_style="yellow"))
                console.print()

        elif cmd in ["/fts", "/search"]:
            if not arg:
                console.print("[dim]Usage: /fts <forensic query>[/dim]\n")
            else:
                t0 = time.time()
                with console.status(f"[bold cyan]Searching 140,688 messages for '{arg}'...[/bold cyan]", spinner="bouncingBar"):
                    results = self.claw.fts_search(arg, limit=5)
                el = time.time() - t0
                
                table = Table(title=f"FTS5 Query Results ({el*1000:.1f}ms)", border_style="cyan")
                table.add_column("Msg ID", style="bold dim")
                table.add_column("Role", style="green")
                table.add_column("Conversation", style="yellow")
                table.add_column("Snippet", style="white")
                
                for r in results:
                    table.add_row(str(r.get("msg_id", "")), r.get("role", ""), r.get("conv_title", "")[:25], r.get("snippet", "")[:120] + "...")
                console.print(table)
                console.print()

        elif cmd in ["/legal", "/case"]:
            ck = arg.upper() if arg else "1FDV"
            dos = self.claw.get_case_dossier(ck)
            if "error" in dos:
                console.print(f"[bold red]{dos['error']}[/bold red]\n")
            else:
                table = Table(title=f"Casebuilder 4000 Dossier: {ck}", border_style="green")
                table.add_column("Property", style="bold cyan")
                table.add_column("Value", style="white")
                for k, v in dos.items():
                    table.add_row(k, str(v))
                console.print(table)
                console.print()

        elif cmd in ["/motion"]:
            mt = arg.lower() if arg else "rule60b"
            mot = self.claw.draft_motion(mt)
            console.print(Panel(Syntax(json.dumps(mot, indent=2), "json", theme="monokai"), title=f"Draft Motion: {mt.upper()}", border_style="magenta"))
            console.print()

        elif cmd in ["/memory", "/mem"]:
            m_parts = arg.split(maxsplit=2) if arg else ["list"]
            act = m_parts[0].lower()
            k = m_parts[1] if len(m_parts) > 1 else ""
            v = m_parts[2] if len(m_parts) > 2 else ""
            with console.status("[bold blue]Querying Aspen-Grove Memory Substrate...[/bold blue]", spinner="point"):
                res = self.claw.memory_action(act, k, v)
            console.print(Panel(Syntax(json.dumps(res, indent=2), "json", theme="monokai"), title=f"Memory: {act}", border_style="blue"))
            console.print()

        elif cmd in ["/agent", "/auto", "/task"]:
            if not arg:
                console.print("[dim]Usage: /agent <goal or multi-step task description>[/dim]\n")
            else:
                console.print(f"[bold yellow]▶ Launching Autonomous Agent Loop for:[/] {arg}")
                self.run_agent_visual(arg)

        elif cmd in ["/tools", "/autotools"]:
            if arg.lower() in ["off", "false", "0", "disable"]:
                self.auto_tools = False
            elif arg.lower() in ["on", "true", "1", "enable"]:
                self.auto_tools = True
            else:
                self.auto_tools = not self.auto_tools
            state = "[bold green]ENABLED[/bold green]" if self.auto_tools else "[bold red]DISABLED[/bold red]"
            console.print(f"✓ Autonomous Tool Execution: {state}\n")

        elif cmd in ["/web", "/studio"]:
            console.print("[bold green]Starting OpenClaw Web Studio on http://127.0.0.1:18800...[/bold green]")
            import subprocess
            web_script = str(Path(__file__).resolve().parent / "openclaw_web.py")
            subprocess.Popen([sys.executable, web_script], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(1)
            # Try to trigger Termux browser open if present
            subprocess.run(["termux-open-url", "http://127.0.0.1:18800"], capture_output=True)
            console.print("[bold cyan]OpenClaw Studio running at http://127.0.0.1:18800 and http://localhost:18800[/bold cyan]\n")

        elif cmd in ["/help", "/h", "?"]:
            help_table = Table(title="OpenClaw Pro TUI Commands", border_style="cyan")
            help_table.add_column("Command", style="bold cyan")
            help_table.add_column("Arguments", style="yellow")
            help_table.add_column("Description", style="white")
            
            help_table.add_row("/tools", "[on|off]", "Toggle autonomous multi-step tool execution")
            help_table.add_row("/agent", "<task description>", "Run autonomous multi-step tool execution loop")
            help_table.add_row("/provider", "<provider_id>", "Switch inference mesh (groq, google, mistral, etc.)")
            help_table.add_row("/model", "", "List available models and current active route")
            help_table.add_row("/device", "<battery|toast|notify|...>", "Direct hardware telemetry and control")
            help_table.add_row("/fts", "<search term>", "Sub-second accelerated chat forensics search (~150ms)")
            help_table.add_row("/legal", "[1FDV|RICO|CFAA|...]", "View Casebuilder 4000 damage and fact dossiers")
            help_table.add_row("/motion", "<rule60b|spoliation|...>", "Draft structured procedural motion skeletons")
            help_table.add_row("/memory", "<list|get|set|search>", "Access Aspen-Grove persistent quantum memory")
            help_table.add_row("/web", "", "Launch OpenClaw Web Studio on port 18800")
            help_table.add_row("/status", "", "System health, API keys, database rows")
            help_table.add_row("/clear", "", "Clear terminal screen and redraw banner")
            help_table.add_row("/exit", "", "Exit OpenClaw interactive shell")
            console.print(help_table)
            console.print()

        else:
            console.print(f"[bold red]Unknown command: {cmd}. Type [cyan]/help[/cyan] for available commands.[/bold red]\n")

        return True

    def run_agent_visual(self, task_prompt: str):
        """Runs autonomous agent loop with real-time visual step cards."""
        with console.status("[bold yellow]Agent reasoning through tool chain...[/bold yellow]", spinner="bouncingBall"):
            res = self.claw.run_agentic_loop(task_prompt)

        trace = res.get("trace", [])
        for step in trace:
            turn = step.get("turn", 1)
            tool = step.get("tool", "")
            thought = step.get("thought", "")
            action = step.get("action", {})
            
            step_table = Table.grid(padding=(0, 1))
            if thought:
                step_table.add_row(f"[bold cyan]Thought:[/] [italic]{thought}[/italic]")
            step_table.add_row(f"[bold magenta]Tool Call:[/] [bold]{tool}[/bold] -> [dim]{json.dumps(action)}[/dim]")
            
            console.print(Panel(step_table, title=f"Step {turn}", border_style="yellow", padding=(0, 1)))

        result_text = res.get("result", "Agent completed execution.")
        console.print(Panel(Markdown(result_text), title="Agent Final Conclusion", border_style="green"))
        console.print()

    def run(self):
        self.print_banner()
        while True:
            try:
                user_input = self.session.prompt(
                    HTML('<b><style fg="#00ffcc">openclaw</style></b> <style fg="#888888">❯</style> '),
                    bottom_toolbar=self.bottom_toolbar
                ).strip()

                if not user_input:
                    continue

                if user_input.startswith("/"):
                    keep_going = self.handle_slash_command(user_input)
                    if not keep_going:
                        break
                    continue

                if self.auto_tools:
                    # Stream with Autonomous Tools
                    tag = f"[{self.active_provider.upper()} / {self.active_model}]"
                    t0 = time.time()
                    collected = []
                    live = None
                    tools_executed = 0
                    try:
                        for ev in self.claw.stream_chat_with_tools(
                            user_input,
                            provider=self.active_provider,
                            model=self.active_model,
                            max_turns=5,
                            enable_tools=True
                        ):
                            ev_type = ev.get("type")
                            if ev_type == "tool_start":
                                if live:
                                    live.stop()
                                    live = None
                                tool_name = ev.get("tool", "tool")
                                thought = ev.get("thought", "")
                                args_str = json.dumps(ev.get("args", {}))
                                t_grid = Table.grid(padding=(0, 1))
                                if thought:
                                    t_grid.add_row(f"[italic cyan]Thought:[/] [dim]{thought}[/dim]")
                                t_grid.add_row(f"[bold yellow]Tool Call:[/] [bold]{tool_name}[/bold] [dim]{args_str}[/dim]")
                                console.print(Panel(t_grid, title=f"⚙ Step {ev.get('turn', 1)}: {tool_name}", border_style="yellow", padding=(0, 1)))
                            elif ev_type == "tool_end":
                                if live:
                                    live.stop()
                                    live = None
                                tools_executed += 1
                                out_snippet = ev.get("output", "")
                                if len(out_snippet) > 400:
                                    out_snippet = out_snippet[:400] + " ...[truncated]"
                                console.print(Panel(Text(out_snippet.strip()), title=f"✓ Tool Result ({ev.get('tool', '')})", border_style="green", padding=(0, 1)))
                            elif ev_type == "token":
                                tok = ev.get("token", "")
                                collected.append(tok)
                                if not live:
                                    console.print(f"\n[bold green]{tag}[/bold green]:")
                                    live = Live(Markdown(""), refresh_per_second=15, console=console)
                                    live.start()
                                live.update(Markdown("".join(collected)))
                            elif ev_type == "done":
                                if live:
                                    live.stop()
                                    live = None
                                elapsed = ev.get("elapsed", time.time() - t0)
                                tag_done = ev.get("tag", tag)
                                console.print(f"\n[dim]⚡ {tag_done} completed in {elapsed:.2f}s ({tools_executed} tools)[/dim]\n")
                        if live:
                            live.stop()
                            live = None
                    except Exception as stream_err:
                        if live:
                            live.stop()
                            live = None
                        console.print(f"[red]Streaming error: {stream_err}[/red]\n")
                else:
                    # Real-Time Streaming Conversational Query (Tools Disabled)
                    tag = f"[{self.active_provider.upper()} / {self.active_model}]"
                    console.print(f"\n[bold green]{tag}[/bold green]:")
                    
                    t0 = time.time()
                    collected = []
                    try:
                        with Live(Markdown(""), refresh_per_second=15, console=console) as live:
                            for tag_out, token in self.claw.stream_query(
                                user_input,
                                target_provider=self.active_provider,
                                target_model=self.active_model
                            ):
                                collected.append(token)
                                live.update(Markdown("".join(collected)))
                    except Exception as stream_err:
                        tag, answer, elapsed = self.claw.query(
                            user_input,
                            target_provider=self.active_provider,
                            target_model=self.active_model
                        )
                        console.print(Panel(Markdown(answer), title=f"[bold green]{tag}[/] [dim]({elapsed:.2f}s)[/]", border_style="cyan", padding=(1, 2)))
                    else:
                        elapsed = time.time() - t0
                        console.print(f"[dim]⚡ Completed in {elapsed:.2f}s[/dim]\n")

            except KeyboardInterrupt:
                console.print("\n[dim]Interrupted. Type /exit or Ctrl+D to quit.[/dim]\n")
                continue
            except EOFError:
                console.print("\n[bold yellow]Session ended.[/bold yellow]")
                break
            except Exception as e:
                console.print(f"[bold red]Execution error: {e}[/bold red]\n")

def main():
    tui = OpenClawTUI()
    tui.run()

if __name__ == "__main__":
    main()
