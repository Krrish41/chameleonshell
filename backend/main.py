"""
ChameleonShell Main Server
FastAPI Application hosting REST APIs, WebSockets for Live Telemetry & Terminal I/O,
and serving the complete $10,000+ Agency Frontend & Documentation Suite.
"""
import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .config import (
    BASE_DIR, FRONTEND_DIR, PAGES_DIR, DOCS_DIR,
    HOST, PORT, PROJECT_TITLE, PLATFORM_VERSION,
    ORGANIZATION, ENGINE_STATUS
)
from .member1_deception_engine.ssh_honeypot_server import SSHHoneypotSession
from .member1_deception_engine.cowrie_baseline_emulator import CowrieBaselineEmulator
from .member1_deception_engine.cloud_metadata_decoy import CloudMetadataDecoy
from .member2_mitre_classifier.sequence_profiler import MITRESequenceProfiler
from .member2_mitre_classifier.mitre_knowledge_base import MITRE_TACTICS, MITRE_TECHNIQUES, get_technique_info
from .member2_mitre_classifier.rule_synthesizer import ActiveDefenseRuleSynthesizer
from .member3_telemetry_sandbox.attack_botnet_simulator import AttackBotnetSimulator, ATTACK_CAMPAIGNS
from .member3_telemetry_sandbox.session_recorder import SessionRecorder
from .member3_telemetry_sandbox.benchmark_evaluator import ThesisBenchmarkEvaluator

app = FastAPI(
    title=PROJECT_TITLE,
    description="Adaptive Cloud Deception Engine & LLM-Driven Chameleon Honeypot (Active Defense)",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Session Instances
global_cs_session = SSHHoneypotSession("global_terminal_session")
global_cowrie_emulator = CowrieBaselineEmulator()
global_imds_decoy = CloudMetadataDecoy(global_cs_session.state_tree)
global_profiler = MITRESequenceProfiler()
global_recorder = SessionRecorder("global_recorder")


# Pydantic Schemas
class CommandRequest(BaseModel):
    command: str
    target: str = "both"  # "chameleonshell" | "cowrie" | "both"
    attacker_ip: str = "185.220.101.4"


class ClassifyRequest(BaseModel):
    command: str
    attacker_ip: str = "185.220.101.4"


class SynthesizeRequest(BaseModel):
    command: str
    technique_id: Optional[str] = None
    attacker_ip: str = "185.220.101.4"


# REST API Endpoints

@app.get("/api/health")
def health_check():
    """System status and enterprise runtime metadata."""
    return {
        "status": "healthy",
        "system": PROJECT_TITLE,
        "version": PLATFORM_VERSION,
        "organization": ORGANIZATION,
        "engine_status": ENGINE_STATUS,
        "uptime_seconds": round(time.time() - global_cs_session.state_tree.boot_time, 2),
        "active_vst_nodes": len(global_cs_session.state_tree.get_full_tree_summary().get("children", []))
    }


@app.post("/api/terminal/execute")
def execute_terminal_command(req: CommandRequest):
    """Executes command on ChameleonShell, Cowrie baseline, or both for A/B comparison."""
    cmd = req.command.strip()
    response_data: Dict[str, Any] = {"command": cmd}

    # 1. ChameleonShell Execution
    if req.target in ["chameleonshell", "both"]:
        cs_res = global_cs_session.process_command(cmd)
        global_recorder.record_output(cs_res["stdout"] or cs_res["stderr"])
        
        # Real-time MITRE Classification
        mitre_rec = global_profiler.classify_command(cmd, attacker_ip=req.attacker_ip)
        
        # Auto-Rule Synthesis
        rules = ActiveDefenseRuleSynthesizer.synthesize_rules(mitre_rec)

        response_data["chameleonshell"] = {
            "execution": cs_res,
            "mitre": mitre_rec,
            "synthesized_rules": rules,
            "prompt": global_cs_session.get_prompt()
        }

    # 2. Cowrie Baseline Execution
    if req.target in ["cowrie", "both"]:
        cowrie_res = global_cowrie_emulator.execute(cmd)
        response_data["cowrie"] = {
            "execution": cowrie_res,
            "prompt": "root@svr04:~# "
        }

    return response_data


@app.get("/api/vst/tree")
def get_vst_tree():
    """Returns the full DAG tree representation of the Virtual State Tree."""
    return {
        "tree": global_cs_session.state_tree.get_full_tree_summary(),
        "current_working_dir": global_cs_session.state_tree.current_working_dir,
        "environment": global_cs_session.state_tree.env,
        "sockets": global_cs_session.state_tree.sockets,
        "cloud_metadata": global_cs_session.state_tree.cloud_metadata
    }


@app.get("/api/mitre/tactics")
def get_mitre_matrix():
    """Returns the Enterprise ATT&CK v16 tactics and techniques catalog."""
    return {
        "tactics": MITRE_TACTICS,
        "techniques": MITRE_TECHNIQUES,
        "tactics_distribution": global_profiler.get_tactics_distribution()
    }


@app.get("/api/mitre/telemetry")
def get_mitre_telemetry():
    """Returns live session telemetry and risk scoring."""
    return global_profiler.get_session_summary()


@app.post("/api/mitre/classify")
def classify_arbitrary_command(req: ClassifyRequest):
    """Classifies an individual command without altering terminal state."""
    return global_profiler.classify_command(req.command, attacker_ip=req.attacker_ip)


@app.post("/api/rules/synthesize")
def synthesize_defense_rules(req: SynthesizeRequest):
    """Generates Snort 3, ModSecurity, and nftables rules for a command."""
    mitre_rec = global_profiler.classify_command(req.command, attacker_ip=req.attacker_ip)
    if req.technique_id:
        mitre_rec["technique_id"] = req.technique_id
        tech_meta = get_technique_info(req.technique_id)
        mitre_rec["technique_name"] = tech_meta["technique_name"]
    return ActiveDefenseRuleSynthesizer.synthesize_rules(mitre_rec)


@app.get("/api/campaigns")
def list_attack_campaigns():
    """Lists the 6 pre-configured multi-stage botnet attack scenarios."""
    summary = []
    for k, v in ATTACK_CAMPAIGNS.items():
        summary.append({
            "key": k,
            "id": v["id"],
            "name": v["name"],
            "description": v["description"],
            "command_count": len(v["commands"]),
            "attacker_ip": v["attacker_ip"],
            "commands": v["commands"]
        })
    return {"campaigns": summary}


@app.post("/api/campaigns/{campaign_key}/run")
def run_attack_campaign(campaign_key: str):
    """Executes a complete multi-command attack scenario on the honeypot."""
    if campaign_key not in ATTACK_CAMPAIGNS:
        raise HTTPException(status_code=404, detail="Campaign not found")
    sim = AttackBotnetSimulator(global_cs_session, global_profiler)
    result = sim.run_campaign(campaign_key)
    return result


@app.get("/api/benchmarks")
def get_benchmarks():
    """Returns validated thesis benchmarks and runs a live comparison trial."""
    return {
        "ground_truth": ThesisBenchmarkEvaluator.get_ground_truth_benchmarks(),
        "live_trial": ThesisBenchmarkEvaluator.run_live_comparison_trial()
    }


@app.get("/api/sessions/replay")
def get_session_replay():
    """Returns the recorded Asciinema v2 session log."""
    return global_recorder.export_dict()


# Cloud IMDSv2 Decoy Routes (http://localhost:8080/latest/...)
@app.api_route("/latest/{full_path:path}", methods=["GET", "PUT", "POST", "HEAD"])
def imds_route(full_path: str):
    status, headers, body = global_imds_decoy.handle_imds_request("GET", f"latest/{full_path}")
    return JSONResponse(content={"body": body}, status_code=status, headers=headers)


# WebSocket for Live Real-Time Telemetry & Terminal Streams
@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    await websocket.accept()
    try:
        # Send initial state snapshot
        await websocket.send_json({
            "type": "INIT_STATE",
            "prompt": global_cs_session.get_prompt(),
            "risk_score": global_profiler.current_risk_score,
            "cwd": global_cs_session.state_tree.current_working_dir,
            "uptime": round(time.time() - global_cs_session.state_tree.boot_time, 1)
        })

        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            msg_type = msg.get("type")

            if msg_type == "COMMAND":
                cmd = msg.get("command", "")
                ip = msg.get("attacker_ip", "185.220.101.4")
                cs_res = global_cs_session.process_command(cmd)
                cowrie_res = global_cowrie_emulator.execute(cmd)
                mitre_rec = global_profiler.classify_command(cmd, attacker_ip=ip)
                rules = ActiveDefenseRuleSynthesizer.synthesize_rules(mitre_rec)

                await websocket.send_json({
                    "type": "EXECUTION_RESULT",
                    "command": cmd,
                    "chameleonshell": cs_res,
                    "cowrie": cowrie_res,
                    "mitre": mitre_rec,
                    "rules": rules,
                    "prompt": global_cs_session.get_prompt(),
                    "risk_score": global_profiler.current_risk_score
                })

            elif msg_type == "PING":
                await websocket.send_json({"type": "PONG", "time": time.time()})

    except WebSocketDisconnect:
        pass
    except Exception as e:
        pass


# Static Files & Sub-Page Delivery
# Ensure subdirectories exist
FRONTEND_DIR.mkdir(parents=True, exist_ok=True)
PAGES_DIR.mkdir(parents=True, exist_ok=True)
DOCS_DIR.mkdir(parents=True, exist_ok=True)

if (FRONTEND_DIR / "assets").exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="assets")
if (FRONTEND_DIR / "css").exists():
    app.mount("/css", StaticFiles(directory=FRONTEND_DIR / "css"), name="css")
if (FRONTEND_DIR / "js").exists():
    app.mount("/js", StaticFiles(directory=FRONTEND_DIR / "js"), name="js")
if PAGES_DIR.exists():
    app.mount("/pages-static", StaticFiles(directory=PAGES_DIR), name="pages-static")


# HTML Page Routes
@app.get("/")
def serve_index():
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return JSONResponse({"status": "Frontend building", "app": PROJECT_TITLE})


@app.get("/lab")
def serve_lab():
    p = PAGES_DIR / "lab.html"
    if p.exists():
        return FileResponse(p)
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/architecture")
def serve_architecture():
    p = PAGES_DIR / "architecture.html"
    if p.exists():
        return FileResponse(p)
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/benchmarks")
def serve_benchmarks():
    p = PAGES_DIR / "benchmarks.html"
    if p.exists():
        return FileResponse(p)
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/whitepaper")
@app.get("/paper")
def serve_whitepaper():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/benchmarks", status_code=301)


@app.get("/privacy")
@app.get("/privacy-policy")
def serve_privacy():
    p = PAGES_DIR / "privacy-policy.html"
    if p.exists():
        return FileResponse(p)
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/terms")
@app.get("/terms-of-service")
def serve_terms():
    p = PAGES_DIR / "terms-of-service.html"
    if p.exists():
        return FileResponse(p)
    return FileResponse(FRONTEND_DIR / "index.html")


# Direct Runner Entrypoint
if __name__ == "__main__":
    import uvicorn
    print(f"[+] Launching {PROJECT_TITLE}")
    print(f"[+] Version: {PLATFORM_VERSION} | Organization: {ORGANIZATION}")
    print(f"[+] Binding server to http://{HOST}:{PORT}")
    uvicorn.run("backend.main:app", host=HOST, port=PORT, reload=False)
