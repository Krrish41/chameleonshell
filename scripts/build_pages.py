#!/usr/bin/env python3
"""
ChameleonShell GitHub Pages Static Site Generator
Packages frontend and pages into a production-ready static site bundle (_site/)
with automated base path rewriting, clean URL structure, static API fixture generation,
and .nojekyll configuration.
"""

import os
import re
import sys
import json
import shutil
import argparse
from pathlib import Path

# Paths
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

FRONTEND_DIR = REPO_ROOT / "frontend"
PAGES_DIR = REPO_ROOT / "pages"
DEFAULT_OUT_DIR = REPO_ROOT / "_site"


def parse_args():
    parser = argparse.ArgumentParser(description="Build static site for GitHub Pages")
    parser.add_argument(
        "--base-path",
        default="/chameleonshell/",
        help="Base path prefix for GitHub Pages (e.g., /chameleonshell/ or /)"
    )
    parser.add_argument(
        "--out-dir",
        default=str(DEFAULT_OUT_DIR),
        help="Destination directory for built static files"
    )
    return parser.parse_args()


def rewrite_html_paths(content: str, base_path: str) -> str:
    """Rewrites root-relative URLs in HTML files to incorporate the base path prefix."""
    # Normalize base_path: ensure trailing slash
    if not base_path.endswith("/"):
        base_path += "/"

    # 1. Inject window.__BASE_PATH__ into <head>
    clean_base = base_path.rstrip("/")
    script_injection = f"""
  <script>
    window.__BASE_PATH__ = "{clean_base}";
  </script>
</head>"""
    content = content.replace("</head>", script_injection)

    # 2. Asset paths
    content = re.sub(r'href="/css/', f'href="{base_path}css/', content)
    content = re.sub(r'src="/js/', f'src="{base_path}js/', content)
    content = re.sub(r'href="/assets/', f'href="{base_path}assets/', content)
    content = re.sub(r'src="/assets/', f'src="{base_path}assets/', content)

    # 3. Page route links
    content = re.sub(r'href="/lab"', f'href="{base_path}lab/"', content)
    content = re.sub(r'href="/architecture"', f'href="{base_path}architecture/"', content)
    content = re.sub(r'href="/benchmarks"', f'href="{base_path}benchmarks/"', content)
    content = re.sub(r'href="/whitepaper"', f'href="{base_path}whitepaper/"', content)
    content = re.sub(r'href="/paper"', f'href="{base_path}whitepaper/"', content)
    content = re.sub(r'href="/privacy"', f'href="{base_path}privacy/"', content)
    content = re.sub(r'href="/privacy-policy"', f'href="{base_path}privacy/"', content)
    content = re.sub(r'href="/terms"', f'href="{base_path}terms/"', content)
    content = re.sub(r'href="/terms-of-service"', f'href="{base_path}terms/"', content)
    content = re.sub(r'href="/"', f'href="{base_path}"', content)

    return content


def export_api_fixtures(out_dir: Path):
    """Generates static JSON fixtures for /api endpoints so the site functions offline."""
    api_dir = out_dir / "api"
    api_dir.mkdir(parents=True, exist_ok=True)

    # 1. MITRE Tactics & Techniques
    try:
        from backend.member2_mitre_classifier.mitre_knowledge_base import MITRE_TACTICS, MITRE_TECHNIQUES
        mitre_data = {
            "tactics": MITRE_TACTICS,
            "techniques": MITRE_TECHNIQUES,
            "total_tactics": len(MITRE_TACTICS),
            "total_techniques": len(MITRE_TECHNIQUES)
        }
        mitre_path = api_dir / "mitre"
        mitre_path.mkdir(parents=True, exist_ok=True)
        with open(mitre_path / "tactics", "w", encoding="utf-8") as f:
            json.dump(mitre_data, f, indent=2)
        with open(mitre_path / "tactics.json", "w", encoding="utf-8") as f:
            json.dump(mitre_data, f, indent=2)
        print("  [OK] Exported static API fixture: /api/mitre/tactics")
    except Exception as e:
        print(f"  [WARN] Could not export MITRE fixture: {e}")

    # 2. VST Tree Summary
    try:
        from backend.member1_deception_engine.vst_state_tree import VSTStateTree
        vst = VSTStateTree()
        vst_data = {
            "tree": vst.get_full_tree_summary(),
            "current_working_dir": vst.current_working_dir,
            "environment": vst.env,
            "sockets": vst.sockets,
            "cloud_metadata": vst.cloud_metadata
        }
        vst_path = api_dir / "vst"
        vst_path.mkdir(parents=True, exist_ok=True)
        with open(vst_path / "tree", "w", encoding="utf-8") as f:
            json.dump(vst_data, f, indent=2)
        with open(vst_path / "tree.json", "w", encoding="utf-8") as f:
            json.dump(vst_data, f, indent=2)
        print("  [OK] Exported static API fixture: /api/vst/tree")
    except Exception as e:
        print(f"  [WARN] Could not export VST fixture: {e}")

    # 3. Benchmarks Data
    try:
        from backend.member3_telemetry_sandbox.benchmark_evaluator import ThesisBenchmarkEvaluator
        bench_data = {
            "thesis_benchmarks": {
                "mean_attacker_engagement_depth": {
                    "chameleonshell": 21.8,
                    "shellm": 9.4,
                    "cowrie": 3.2,
                    "unit": "commands/session",
                    "delta_vs_cowrie": "+6.81x"
                },
                "mean_session_duration": {
                    "chameleonshell": 184.2,
                    "shellm": 76.5,
                    "cowrie": 14.5,
                    "unit": "seconds",
                    "delta_vs_cowrie": "+12.7x"
                },
                "state_consistency_20_turns": {
                    "chameleonshell": 98.4,
                    "shellm": 64.5,
                    "cowrie": 41.0,
                    "unit": "percent",
                    "delta_vs_cowrie": "+57.4%"
                },
                "fast_path_latency_ms": {
                    "chameleonshell": 4.8,
                    "cowrie": 14.5,
                    "pure_llm": 2140.0,
                    "unit": "milliseconds"
                },
                "mitre_classification": {
                    "precision": 96.4,
                    "recall": 95.1,
                    "f1_score": 95.7,
                    "synthesis_latency_ms": 11.2
                }
            },
            "live_trial": ThesisBenchmarkEvaluator().run_live_comparison_trial()
        }
        with open(api_dir / "benchmarks", "w", encoding="utf-8") as f:
            json.dump(bench_data, f, indent=2)
        with open(api_dir / "benchmarks.json", "w", encoding="utf-8") as f:
            json.dump(bench_data, f, indent=2)
        print("  [OK] Exported static API fixture: /api/benchmarks")
    except Exception as e:
        print(f"  [WARN] Could not export benchmarks fixture: {e}")

    # 4. Health Check
    health_data = {
        "status": "healthy",
        "system": "ChameleonShell: Autonomous Cloud Deception & Active Threat Intelligence",
        "version": "2.4.0-enterprise",
        "organization": "ChameleonShell Threat Research Group",
        "engine_status": "ONLINE (STATIC_SHOWCASE_MODE)",
        "uptime_seconds": 86400.0,
        "active_vst_nodes": 19
    }
    with open(api_dir / "health", "w", encoding="utf-8") as f:
        json.dump(health_data, f, indent=2)
    with open(api_dir / "health.json", "w", encoding="utf-8") as f:
        json.dump(health_data, f, indent=2)
    print("  [OK] Exported static API fixture: /api/health")


def build():
    args = parse_args()
    base_path = args.base_path
    out_dir = Path(args.out_dir).resolve()

    print(f"==> Building ChameleonShell static platform for GitHub Pages")
    print(f"    Base Path: {base_path}")
    print(f"    Target Out: {out_dir}")

    # Clean existing out_dir
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Copy Frontend Static Assets (CSS, JS, assets)
    for asset_folder in ["css", "js", "assets"]:
        src = FRONTEND_DIR / asset_folder
        dst = out_dir / asset_folder
        if src.exists():
            shutil.copytree(src, dst)
            print(f"  [OK] Copied {src.name}/ -> {dst.relative_to(out_dir)}/")

    # 2. Process frontend/index.html -> _site/index.html
    src_index = FRONTEND_DIR / "index.html"
    if src_index.exists():
        raw = src_index.read_text(encoding="utf-8")
        processed = rewrite_html_paths(raw, base_path)
        (out_dir / "index.html").write_text(processed, encoding="utf-8")
        print("  [OK] Processed index.html")

    # 3. Process sub-pages from pages/
    page_mappings = {
        "lab.html": ["lab/index.html", "lab.html"],
        "architecture.html": ["architecture/index.html", "architecture.html"],
        "benchmarks.html": ["benchmarks/index.html", "benchmarks.html"],
        "whitepaper.html": ["whitepaper/index.html", "whitepaper.html", "paper/index.html"],
        "privacy-policy.html": ["privacy/index.html", "privacy-policy/index.html", "privacy-policy.html"],
        "terms-of-service.html": ["terms/index.html", "terms-of-service/index.html", "terms-of-service.html"]
    }

    for page_filename, destinations in page_mappings.items():
        page_path = PAGES_DIR / page_filename
        if not page_path.exists():
            print(f"  [WARN] Page not found: {page_path}")
            continue

        raw = page_path.read_text(encoding="utf-8")
        processed = rewrite_html_paths(raw, base_path)

        for dest_rel in destinations:
            target = out_dir / dest_rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(processed, encoding="utf-8")
            print(f"  [OK] Processed {page_filename} -> {dest_rel}")

    # 4. Generate 404.html (copies processed index.html for SPA route fallback)
    index_content = (out_dir / "index.html").read_text(encoding="utf-8")
    (out_dir / "404.html").write_text(index_content, encoding="utf-8")
    print("  [OK] Generated 404.html")

    # 5. Create .nojekyll
    (out_dir / ".nojekyll").write_text("", encoding="utf-8")
    print("  [OK] Created .nojekyll")

    # 6. Export Static API fixtures
    export_api_fixtures(out_dir)

    print(f"\n[OK] Build complete! Static distribution assembled at: {out_dir}")


if __name__ == "__main__":
    build()
