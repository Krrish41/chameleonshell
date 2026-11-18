"""
SSH Honeypot Decoy Server Interface
Provides containerized SSH listener hooks and terminal session abstraction.
"""
import asyncio
from typing import Dict, Any, Optional
from .vst_state_tree import VSTStateTree
from .fast_path_router import FastPathRouter
from .llm_slow_path import LLMSlowPathEngine


class SSHHoneypotSession:
    """Represents an active interactive terminal session over SSH or Web."""

    def __init__(self, session_id: str = "interactive_sess_1"):
        self.session_id = session_id
        self.state_tree = VSTStateTree(session_id=session_id)
        self.fast_router = FastPathRouter(self.state_tree)
        self.slow_engine = LLMSlowPathEngine(self.state_tree)

    def process_command(self, cmd_line: str) -> Dict[str, Any]:
        """Routes command to Fast-Path or Slow-Path based on AST analysis."""
        cleaned = cmd_line.strip()
        if self.fast_router.can_handle(cleaned):
            return self.fast_router.execute(cleaned)
        else:
            return self.slow_engine.execute(cleaned)

    def get_prompt(self) -> str:
        """Returns standard bash prompt string."""
        u = self.state_tree.current_user
        h = self.state_tree.hostname
        cwd = self.state_tree.current_working_dir
        if cwd == f"/home/{u}":
            cwd_str = "~"
        else:
            cwd_str = cwd
        sym = "#" if u == "root" else "$"
        return f"{u}@{h}:{cwd_str}{sym} "
