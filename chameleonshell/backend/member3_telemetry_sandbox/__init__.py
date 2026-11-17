"""
Subsystem 03: Telemetry Sandbox, Botnet Simulator & Session Replay
Provides 6 automated multi-stage adversarial campaigns, Asciinema v2 session recording,
and automated comparative enterprise benchmark evaluations.
"""
from .attack_botnet_simulator import AttackBotnetSimulator, ATTACK_CAMPAIGNS
from .session_recorder import SessionRecorder
from .benchmark_evaluator import ThesisBenchmarkEvaluator, run_benchmark_suite

__all__ = [
    "AttackBotnetSimulator",
    "ATTACK_CAMPAIGNS",
    "SessionRecorder",
    "ThesisBenchmarkEvaluator",
    "run_benchmark_suite"
]
