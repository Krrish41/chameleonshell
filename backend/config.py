"""
ChameleonShell Global Configuration
Loads environment variables and sets defaults for Deception Engine,
MITRE Classifier, and Telemetry Sandbox.
"""
import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
PAGES_DIR = BASE_DIR / "pages"
DOCS_DIR = BASE_DIR / "docs"
DATA_DIR = BASE_DIR / "data"

# Ensure data directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Server Configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8080"))
SSH_PORT = int(os.getenv("SSH_PORT", "2222"))
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# Deception & LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "deterministic")  # deterministic | gemini | ollama
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OLLAMA_ENDPOINT = os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3:8b")

# Enterprise Production Metadata
PROJECT_TITLE = "ChameleonShell: Autonomous Cloud Deception & Active Threat Intelligence"
PLATFORM_VERSION = "2.4.0-enterprise"
ORGANIZATION = "ChameleonShell Threat Research Group"
ENGINE_STATUS = "ONLINE"
