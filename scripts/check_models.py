#!/usr/bin/env python3
"""Check which LLMModel enum values are working by making a real call to each."""

import asyncio
import sys
from dataclasses import dataclass, field

from pydantic import BaseModel

from yalc import LLMModel, create_client

# ANSI colors
GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
DIM = "\033[2m"
BOLD = "\033[1m"
RESET = "\033[0m"

SPINNER = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]


class Ping(BaseModel):
    message: str


MESSAGES = [
    {
        "role": "user",
        "content": "Reply with the word 'pong' and nothing else.",
    }
]


@dataclass
class CheckState:
    pending: set[str] = field(default_factory=set)
    frame: int = 0

    def spin_char(self) -> str:
        c = SPINNER[self.frame % len(SPINNER)]
        self.frame += 1
        return c

    def render_spinner(self) -> None:
        waiting = len(self.pending)
        line = f"  {YELLOW}{self.spin_char()}{RESET} waiting: {DIM}{waiting}{RESET}"
        sys.stdout.write(f"\r{line:<100}")
        sys.stdout.flush()

    def clear_line(self) -> None:
        sys.stdout.write(f"\r{' ' * 100}\r")
        sys.stdout.flush()


async def spinner_task(
    state: CheckState, stop_event: asyncio.Event
) -> None:
    while not stop_event.is_set():
        state.render_spinner()
        await asyncio.sleep(0.08)


def _format_error(e: Exception) -> str:
    msg = str(e)
    # Instructor wraps retries in XML-ish blobs — extract the last exception
    if "<last_exception>" in msg:
        start = msg.index("<last_exception>") + len(
            "<last_exception>"
        )
        end = msg.index("</last_exception>")
        msg = msg[start:end].strip().strip('"')
    msg = msg.splitlines()[0].strip()
    # Map common patterns to readable messages
    if "OPENAI_API_KEY" in msg or (
        "api_key" in msg.lower() and "openai" in msg.lower()
    ):
        return "missing OPENAI_API_KEY"
    if "api_key" in msg.lower() and "anthropic" in msg.lower():
        return "missing ANTHROPIC_API_KEY"
    if "resolve authentication" in msg.lower() or "X-Api-Key" in msg:
        return "missing API key"
    if "Unsupported provider" in msg or isinstance(e, KeyError):
        return f"not in provider map ({msg})"
    if (
        "model_not_found" in msg.lower()
        or "does not exist" in msg.lower()
    ):
        return f"model not found: {msg[:80]}"
    return msg[:120]


async def check_model(
    model: LLMModel, state: CheckState
) -> tuple[LLMModel, bool, str]:
    state.pending.add(model.value)
    try:
        client = create_client(model)
        result, call = await client.structured_response(
            Ping, MESSAGES
        )
        detail = f"'{result.message}' {DIM}({call.input_tokens}in/{call.output_tokens}out){RESET}"
        ok, icon = True, f"{GREEN}✓{RESET}"
    except Exception as e:
        detail = f"{RED}{_format_error(e)}{RESET}"
        ok, icon = False, f"{RED}✗{RESET}"

    state.pending.discard(model.value)
    state.clear_line()
    print(f"  {icon}  {CYAN}{model.value:<45}{RESET} {detail}")

    return model, ok, detail


async def main() -> None:
    models = list(LLMModel)
    print(f"\n{BOLD}Checking {len(models)} models...{RESET}\n")

    state = CheckState()
    stop_event = asyncio.Event()
    spin = asyncio.create_task(spinner_task(state, stop_event))

    results = await asyncio.gather(
        *[check_model(m, state) for m in models]
    )

    stop_event.set()
    await spin
    state.clear_line()

    passed = sum(1 for _, ok, _ in results if ok)
    total = len(results)
    color = (
        GREEN if passed == total else (YELLOW if passed > 0 else RED)
    )
    print(f"\n{BOLD}{color}{passed}/{total} models OK{RESET}\n")


if __name__ == "__main__":
    asyncio.run(main())
