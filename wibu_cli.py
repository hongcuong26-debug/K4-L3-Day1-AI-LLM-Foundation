#!/usr/bin/env python3
"""
(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧  O T A K U   S T A T I O N  ✧･ﾟ: *ヽ(◕ヮ◕ヽ)
------------------------------------------------------------------
A neon Cyberpunk-Otaku terminal front-end for the K4 LLM API lab
(AICB-P1 — Ngày 1: Khám Phá LLM API).
------------------------------------------------------------------
"""

from __future__ import annotations

import os
import random
import sys
import time
from dataclasses import dataclass, field

from rich.align import Align
from rich.box import DOUBLE_EDGE, HEAVY, ROUNDED
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

try:
    import pyfiglet

    _HAS_FIGLET = True
except ImportError:
    _HAS_FIGLET = False

# ---------------------------------------------------------------------------
# Load lab functions. Fall back to DEMO MODE if unavailable.
# ---------------------------------------------------------------------------
_LAB_AVAILABLE = False
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from template import (  # type: ignore
        OPENAI_MODEL,
        call_openai,
        count_tokens,
        estimate_cost,
        retry_with_backoff,
    )

    _LAB_AVAILABLE = bool(os.getenv("OPENAI_API_KEY"))
except Exception:
    OPENAI_MODEL = "gpt-4o (demo)"
    _LAB_AVAILABLE = False


# ===========================================================================
# THEME — Neon Anime Palette
# ===========================================================================
WIBU_THEME = Theme(
    {
        "neon.pink": "bold #ff4fd8",
        "neon.magenta": "bold #ff2ec4",
        "neon.purple": "bold #b967ff",
        "neon.cyan": "bold #4dfff3",
        "neon.mint": "bold #7dffb3",
        "neon.dim": "dim #a892ff",
        "prompt.tag": "bold #4dfff3 on #1a0b2e",
        "hp": "bold #ff4fd8",
        "mp": "bold #4dfff3",
        "warn": "bold #ffb84d",
        "err": "bold #ff5c5c",
    }
)

console = Console(theme=WIBU_THEME)

KAOMOJI = [
    "(≧◡≦)",
    "(◕‿◕✿)",
    "(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧",
    "(๑˃̵ᴗ˂̵)و",
    "(⁄ ⁄•⁄ω⁄•⁄ ⁄)",
    "ヽ(・∀・)ﾉ",
    "(*≧▽≦)",
    "(ノ˘ω˘)ノ",
]

COMPANION_LINES = [
    "Senpai noticed you~ let's chat! {kao}",
    "System nominal. Standing by for your command, Master. {kao}",
    "Ehh? Another query already? I'm ready! {kao}",
    "Uwaa~ the neon core is humming today. {kao}",
    "Mou~ don't keep me waiting too long, okay? {kao}",
]

DEMO_REPLIES = [
    "Sugoi! In demo mode I can't reach the real API, but here's a "
    "placeholder response so you can see the panel styling in action.",
    "Ara ara~ no API key detected, so I'm improvising this reply "
    "locally. Add OPENAI_API_KEY to your .env to unlock the real me!",
    "Beep boop. Simulated neural core online. This is a canned "
    "response — connect your key for genuine LLM output, senpai.",
]


# ===========================================================================
# STATE — Retro RPG stats for the session
# ===========================================================================
@dataclass
class SessionState:
    level: int = 1
    hp: int = 100
    hp_max: int = 100
    mp: int = 80
    mp_max: int = 100
    turns: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    last_ping_ms: float = 0.0
    companion: str = "Mika"
    model: str = OPENAI_MODEL
    mode: str = "LIVE" if _LAB_AVAILABLE else "DEMO"
    history: list = field(default_factory=list)

    def register_turn(self, tokens: int, cost: float, ping_ms: float) -> None:
        self.turns += 1
        self.total_tokens += tokens
        self.total_cost += cost
        self.last_ping_ms = ping_ms
        self.mp = max(5, self.mp - random.randint(3, 9))
        if self.mp < 20:
            self.hp = max(10, self.hp - random.randint(1, 4))
        if self.turns % 5 == 0 and self.level < 99:
            self.level += 1
            self.mp = self.mp_max
            self.hp = self.hp_max


# ===========================================================================
# RENDERING HELPERS
# ===========================================================================
def _bar(current: int, maximum: int, width: int = 20, style: str = "hp") -> Text:
    filled = int(width * max(0, current) / max(1, maximum))
    filled = min(width, filled)
    txt = Text()
    txt.append("█" * filled, style=style)
    txt.append("░" * (width - filled), style="neon.dim")
    txt.append(f" {current}/{maximum}")
    return txt


def render_banner() -> None:
    console.clear()
    kao = random.choice(KAOMOJI)

    if _HAS_FIGLET:
        try:
            art = pyfiglet.figlet_format("OTAKU STATION", font="slant")
        except Exception:
            art = "OTAKU STATION"
    else:
        art = r"""
   ____  _         _          ____  _         _   _
  / __ \| |       | |        / ___|| |       | | (_)
 | |  | | |_ __ _| | ___    | (___ | |_ __ _| |_ _  ___  _ __
 | |  | | __/ _` | |/ / |    \___ \| __/ _` | __| |/ _ \| '_ \
 | |__| | || (_| |   <| |    ____) | || (_| | |_| | (_) | | | |
  \____/ \__\__,_|_|\_\_|   |_____/ \__\__,_|\__|_|\___/|_| |_|
"""

    banner_text = Text(art, style="neon.magenta", justify="center")
    subtitle = Text.assemble(
        (f"✧ Cyberpunk Otaku Terminal OS ✧  {kao}\n", "neon.cyan"),
        ("Neural Uplink for AICB-P1 · K4 — Khám Phá LLM API\n", "neon.purple"),
    )

    console.print(
        Panel(
            Align.center(Text.assemble(banner_text, "\n", subtitle)),
            box=DOUBLE_EDGE,
            border_style="neon.pink",
            padding=(1, 2),
        )
    )


def render_status(state: SessionState) -> None:
    table = Table.grid(padding=(0, 2), expand=True)
    table.add_column(justify="left", ratio=1)
    table.add_column(justify="left", ratio=1)

    left = Table.grid(padding=(0, 1))
    left.add_row(Text("LV", style="neon.mint"), Text(str(state.level), style="bold white"))
    left.add_row(Text("HP", style="hp"), _bar(state.hp, state.hp_max, style="hp"))
    left.add_row(Text("MP", style="mp"), _bar(state.mp, state.mp_max, style="mp"))
    left.add_row(
        Text("Companion", style="neon.purple"),
        Text(f"{state.companion} {random.choice(KAOMOJI)}", style="white"),
    )

    right = Table.grid(padding=(0, 1))
    right.add_row(Text("Mode", style="neon.cyan"), Text(state.mode, style="warn" if state.mode == "DEMO" else "neon.mint"))
    right.add_row(Text("Model", style="neon.cyan"), Text(str(state.model), style="white"))
    right.add_row(Text("Ping", style="neon.cyan"), Text(f"{state.last_ping_ms:.0f} ms", style="white"))
    right.add_row(Text("Tokens used", style="neon.cyan"), Text(str(state.total_tokens), style="white"))
    right.add_row(Text("Session cost", style="neon.cyan"), Text(f"${state.total_cost:.5f}", style="white"))

    table.add_row(left, right)

    console.print(
        Panel(
            table,
            title="[bold]⚔ STATUS ⚔[/bold]",
            title_align="center",
            box=ROUNDED,
            border_style="neon.purple",
            padding=(0, 1),
        )
    )


def typewriter_print(text: str, style: str = "white", delay: float = 0.012) -> None:
    """Visual-novel-style typewriter text effect."""
    for ch in text:
        console.print(ch, style=style, end="", soft_wrap=True)
        sys.stdout.flush()
        time.sleep(delay * (4 if ch in ".!?…" else 1))
    console.print()


def render_reply_panel(reply_text: str) -> None:
    console.print(
        Panel(
            Markdown(reply_text) if _looks_like_markdown(reply_text) else Text(reply_text, style="white"),
            title="[Waifu Assistant AI]",
            title_align="left",
            subtitle=random.choice(KAOMOJI),
            subtitle_align="right",
            box=ROUNDED,
            border_style="neon.pink",
            padding=(1, 2),
        )
    )


def _looks_like_markdown(text: str) -> bool:
    markers = ("```", "**", "- ", "# ", "1. ")
    return any(m in text for m in markers)


def themed_prompt() -> str:
    console.print()
    console.print(
        Text.assemble(("[Master@OtakuStation ~] ", "neon.cyan"), ("❯ ", "neon.pink")),
        end="",
    )
    try:
        return input()
    except (EOFError, KeyboardInterrupt):
        return "quit"


# ===========================================================================
# BACKEND
# ===========================================================================
def get_reply(prompt: str, state: SessionState) -> tuple[str, float, int, float]:
    start = time.perf_counter()

    if _LAB_AVAILABLE:
        try:
            text, latency = retry_with_backoff(lambda: call_openai(prompt))
        except Exception as exc:
            console.print(
                Panel(
                    f"API error: {exc}\nFalling back to demo reply for this turn.",
                    title="[bold err]⚠ SIGNAL LOST[/bold err]",
                    border_style="err",
                    box=HEAVY,
                )
            )
            text = random.choice(DEMO_REPLIES)
            latency = time.perf_counter() - start
        tokens_in = count_tokens(prompt)
        tokens_out = count_tokens(text)
        cost = estimate_cost(prompt, text)["total_cost"]
        total_tokens = tokens_in + tokens_out
    else:
        time.sleep(random.uniform(0.3, 0.8))
        text = random.choice(DEMO_REPLIES)
        latency = time.perf_counter() - start
        total_tokens = max(1, len(prompt.split()) + len(text.split()))
        cost = 0.0

    return text, latency * 1000, total_tokens, cost


# ===========================================================================
# MAIN LOOP
# ===========================================================================
def print_help() -> None:
    help_table = Table(box=ROUNDED, border_style="neon.cyan", show_header=False)
    help_table.add_row("[neon.pink]quit / exit[/neon.pink]", "Disconnect from Otaku Station")
    help_table.add_row("[neon.pink]/status[/neon.pink]", "Redraw the RPG status dashboard")
    help_table.add_row("[neon.pink]/help[/neon.pink]", "Show this command list")
    console.print(help_table)


def main() -> None:
    state = SessionState()

    try:
        render_banner()
        console.print(
            Panel(
                Text(random.choice(COMPANION_LINES).format(kao=random.choice(KAOMOJI)), justify="center"),
                border_style="neon.mint",
                box=ROUNDED,
            )
        )
        if not _LAB_AVAILABLE:
            console.print(
                Panel(
                    "No OPENAI_API_KEY found (or template.py not importable).\n"
                    "Running in [bold]DEMO MODE[/bold] — the UI is fully live, "
                    "replies are simulated.\n"
                    "Set OPENAI_API_KEY in a .env file next to this script to "
                    "go LIVE.",
                    title="[bold warn]⚠ OFFLINE CORE[/bold warn]",
                    border_style="warn",
                    box=ROUNDED,
                )
            )

        render_status(state)
        console.print(Rule(style="neon.purple"))
        print_help()

        while True:
            user_msg = themed_prompt().strip()
            if not user_msg:
                continue
            if user_msg.lower() in ("quit", "exit"):
                break
            if user_msg.lower() == "/help":
                print_help()
                continue
            if user_msg.lower() == "/status":
                render_status(state)
                continue

            with console.status("[neon.purple]Transmitting to the neural core...", spinner="dots12"):
                reply_text, ping_ms, tokens, cost = get_reply(user_msg, state)

            state.register_turn(tokens, cost, ping_ms)
            render_reply_panel(reply_text)
            console.print(Rule(style="neon.dim"))
            render_status(state)

    finally:
        console.print()
        console.print(
            Panel(
                Align.center(
                    Text(
                        f"Session closed after {state.turns} turn(s). "
                        f"See you again, Master {random.choice(KAOMOJI)}",
                        style="neon.pink",
                    )
                ),
                box=DOUBLE_EDGE,
                border_style="neon.purple",
            )
        )


if __name__ == "__main__":
    main()