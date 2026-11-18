"""
Asciinema v2 Session Recorder & Telemetry Broadcaster
Records interactive terminal streams into Asciinema v2 (.cast) JSON logs
compatible with web terminal replay engines.
"""
import time
import json
from typing import Dict, Any, List


class SessionRecorder:
    """Records interactive shell sessions in Asciinema v2 format."""

    def __init__(self, session_id: str, title: str = "ChameleonShell Deception Session", width: int = 100, height: int = 28):
        self.session_id = session_id
        self.title = title
        self.width = width
        self.height = height
        self.start_time = time.time()
        self.events: List[List[Any]] = []  # [offset_sec, "o", text]
        self.header = {
            "version": 2,
            "width": width,
            "height": height,
            "timestamp": int(self.start_time),
            "title": title,
            "env": {
                "SHELL": "/bin/bash",
                "TERM": "xterm-256color"
            }
        }

    def record_output(self, text: str):
        offset = round(time.time() - self.start_time, 3)
        formatted = text.replace("\n", "\r\n")
        self.events.append([offset, "o", formatted])

    def export_cast(self) -> str:
        """Returns JSONL formatted Asciinema v2 document."""
        lines = [json.dumps(self.header)]
        for ev in self.events:
            lines.append(json.dumps(ev))
        return "\n".join(lines) + "\n"

    def export_dict(self) -> Dict[str, Any]:
        return {
            "header": self.header,
            "events": self.events
        }
