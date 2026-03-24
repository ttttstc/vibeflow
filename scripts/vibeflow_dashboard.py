#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import threading
import time
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from vibeflow_automation import detect_phase, friendly_message_for_phase  # noqa: E402
from vibeflow_paths import load_runtime, load_state, path_contract  # noqa: E402


ARTIFACT_DESCRIPTIONS = {
    "think": "当前上下文，说明这次工作的起点、边界和目标。",
    "plan": "方案提案，说明为什么做、范围是什么。",
    "requirements": "正式需求定义，后续设计和测试都要对齐它。",
    "ucd": "用户体验说明，用于 UI 或交互细节校准。",
    "design": "实现方案，解释怎么接到当前系统里。",
    "design_review": "设计评审结论，记录工程和设计视角的反馈。",
    "tasks": "执行清单，把实现工作拆成可落地任务。",
    "review": "全局审查结果，检查结构、风险和一致性。",
    "system_test": "系统测试结果，确认核心链路可跑通。",
    "qa": "界面或体验验证结果，用于 UI 场景。",
    "release_notes": "发布记录，说明这次交付带来了什么变化。",
}

PHASE_GROUPS = [
    ("think", "Think", ["think"]),
    ("plan", "Plan", ["plan"]),
    ("requirements", "Requirements", ["requirements"]),
    ("design", "Design", ["design"]),
    ("build", "Build", ["build-init", "build-config", "build-work"]),
    ("review", "Review", ["review"]),
    ("test", "Test", ["test-system", "test-qa"]),
    ("ship", "Ship", ["ship"]),
    ("reflect", "Reflect", ["reflect"]),
]


def iso_now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def phase_index(phase: str) -> int:
    order = [
        "increment",
        "quick",
        "think",
        "template-selection",
        "plan",
        "requirements",
        "design",
        "build-init",
        "build-config",
        "build-work",
        "review",
        "test-system",
        "test-qa",
        "ship",
        "reflect",
        "done",
    ]
    return order.index(phase) if phase in order else len(order)


def file_mtime(path: Path) -> float:
    return path.stat().st_mtime if path.exists() else 0.0


def read_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def required_flags(workflow_path: Path) -> dict:
    content = workflow_path.read_text(encoding="utf-8") if workflow_path.exists() else ""
    return {
        "qa_required": "qa:\n    required: true" in content or "qa:\n  required: true" in content,
        "ship_required": "ship:\n    required: true" in content or "ship:\n  required: true" in content,
        "reflect_required": "reflect:\n    required: true" in content or "reflect:\n  required: true" in content,
    }


def build_macro_status(
    macro_key: str,
    detect_info: dict,
    state: dict,
    runtime: dict,
    *,
    qa_required: bool,
    ship_required: bool,
    reflect_required: bool,
) -> str:
    current_phase = detect_info["phase"]
    current_idx = phase_index(current_phase)

    if macro_key == "build":
        done = all(bool((state.get("checkpoints") or {}).get(key)) for key in ("build_init", "build_config", "build_work"))
        phase_ids = {"build-init", "build-config", "build-work"}
    elif macro_key == "test":
        checkpoints = state.get("checkpoints") or {}
        test_qa_done = True if not qa_required else bool(checkpoints.get("test_qa"))
        done = bool(checkpoints.get("test_system")) and test_qa_done
        phase_ids = {"test-system", "test-qa"}
    else:
        checkpoint_key = "test_system" if macro_key == "test-system" else macro_key
        done = bool((state.get("checkpoints") or {}).get(checkpoint_key))
        phase_ids = {macro_key}

    if macro_key == "ship" and not ship_required:
        return "skipped"
    if macro_key == "reflect" and not reflect_required:
        return "skipped"

    if done:
        return "completed"
    if current_phase in phase_ids:
        runtime_status = runtime.get("status")
        if runtime_status in {"blocked", "failed"}:
            return "blocked"
        if runtime_status == "waiting_manual":
            return "waiting_manual"
        return "running"

    probe_phase = next(iter(phase_ids))
    if current_idx > phase_index(probe_phase):
        return "completed"
    return "pending"


def build_subphase_status(phase: str, detect_info: dict, state: dict, runtime: dict, *, qa_required: bool, ship_required: bool, reflect_required: bool) -> str:
    if phase == "test-qa" and not qa_required:
        return "skipped"
    if phase == "ship" and not ship_required:
        return "skipped"
    if phase == "reflect" and not reflect_required:
        return "skipped"

    checkpoint_map = {
        "test-system": "test_system",
        "test-qa": "test_qa",
        "build-init": "build_init",
        "build-config": "build_config",
        "build-work": "build_work",
    }
    checkpoint_key = checkpoint_map.get(phase, phase)
    if (state.get("checkpoints") or {}).get(checkpoint_key):
        return "completed"
    if detect_info["phase"] == phase:
        runtime_status = runtime.get("status")
        if runtime_status in {"blocked", "failed"}:
            return "blocked"
        if runtime_status == "waiting_manual":
            return "waiting_manual"
        return "running"
    if phase_index(detect_info["phase"]) > phase_index(phase):
        return "completed"
    return "pending"


def load_feature_summary(project_root: Path) -> dict:
    feature_path = project_root / "feature-list.json"
    if not feature_path.exists():
        return {"total": 0, "passing": 0, "running": 0, "failing": 0, "items": []}
    payload = json.loads(feature_path.read_text(encoding="utf-8"))
    items = []
    passing = running = failing = 0
    for feature in payload.get("features", []):
        if feature.get("deprecated"):
            continue
        status = feature.get("status", "pending")
        if status == "passing":
            passing += 1
        elif status == "running":
            running += 1
        elif status not in {"pending", "queued", "ready", "skipped"}:
            failing += 1
        items.append(
            {
                "id": feature.get("id"),
                "title": feature.get("title", "Untitled"),
                "status": status,
                "dependencies": feature.get("dependencies") or [],
                "priority": feature.get("priority", "medium"),
            }
        )
    return {
        "total": len(items),
        "passing": passing,
        "running": running,
        "failing": failing,
        "items": items,
    }


def build_dashboard_snapshot(project_root: Path) -> dict:
    project_root = project_root.resolve()
    state = load_state(project_root)
    runtime = load_runtime(project_root)
    contract = path_contract(project_root, state)
    detect_info = detect_phase(project_root)
    flags = required_flags(contract["workflow"])
    feature_summary = load_feature_summary(project_root)

    macro_cards = []
    for key, label, phases in PHASE_GROUPS:
        macro_cards.append(
            {
                "key": key,
                "label": label,
                "status": build_macro_status(
                    key,
                    detect_info,
                    state,
                    runtime,
                    qa_required=flags["qa_required"],
                    ship_required=flags["ship_required"],
                    reflect_required=flags["reflect_required"],
                ),
                "phases": [
                    {
                        "key": phase,
                        "status": build_subphase_status(
                            phase,
                            detect_info,
                            state,
                            runtime,
                            qa_required=flags["qa_required"],
                            ship_required=flags["ship_required"],
                            reflect_required=flags["reflect_required"],
                        ),
                    }
                    for phase in phases
                ],
            }
        )

    artifacts = []
    for key, path in contract["artifacts"].items():
        artifacts.append(
            {
                "key": key,
                "path": str(path),
                "exists": path.exists(),
                "description": ARTIFACT_DESCRIPTIONS.get(key, ""),
            }
        )
    artifacts.append(
        {
            "key": "release_notes",
            "path": str(contract["release_notes"]),
            "exists": contract["release_notes"].exists(),
            "description": ARTIFACT_DESCRIPTIONS["release_notes"],
        }
    )

    phase_history = read_json(contract["phase_history"], [])
    events = list(runtime.get("events") or [])
    for entry in phase_history[-30:]:
        events.append(
            {
                "timestamp": entry.get("timestamp", iso_now()),
                "kind": entry.get("type", "phase"),
                "title": entry.get("phase", "phase"),
                "detail": entry.get("detail", ""),
                "phase": entry.get("phase", ""),
                "status": entry.get("status", "info"),
            }
        )
    events = sorted(events, key=lambda item: item.get("timestamp", ""), reverse=True)[:40]

    token_parts = [
        str(file_mtime(contract["state"])),
        str(file_mtime(contract["runtime"])),
        str(file_mtime(contract["feature_list"])),
        str(file_mtime(contract["phase_history"])),
        str(file_mtime(contract["release_notes"])),
    ]
    token_parts.extend(str(file_mtime(path)) for path in contract["artifacts"].values())
    token = "-".join(token_parts)

    current_phase = detect_info["phase"]
    runtime_status = runtime.get("status") or ("completed" if current_phase == "done" else "idle")
    friendly = runtime.get("friendly_message") or friendly_message_for_phase(
        current_phase,
        status="waiting_manual" if current_phase in {"think", "plan", "requirements", "design", "quick"} else runtime_status,
        detail=detect_info["reason"],
    )

    return {
        "project": project_root.name,
        "project_root": str(project_root),
        "generated_at": iso_now(),
        "token": token,
        "mode": state.get("mode", "full"),
        "current_phase": current_phase,
        "status": runtime_status,
        "friendly_message": friendly,
        "reason": detect_info["reason"],
        "active_change": state.get("active_change") or {},
        "workflow": macro_cards,
        "features": feature_summary,
        "artifacts": artifacts,
        "events": events,
        "checkpoints": state.get("checkpoints") or {},
        "runtime": runtime,
        "flags": flags,
    }


def dashboard_html() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>VibeFlow Dashboard</title>
  <style>
    :root{
      --bg:#08111b;
      --bg-soft:#101d2b;
      --card:#122133;
      --card-soft:#17283c;
      --text:#f3f6fb;
      --muted:#98a8bb;
      --line:rgba(138,166,194,.18);
      --accent:#48d5ff;
      --success:#67d69a;
      --warning:#ffbd59;
      --danger:#ff7a59;
      --shadow:0 20px 60px rgba(3,10,18,.35);
    }
    *{box-sizing:border-box}
    body{
      margin:0;
      min-height:100vh;
      background:
        radial-gradient(circle at top left, rgba(72,213,255,.16), transparent 32%),
        radial-gradient(circle at 80% 10%, rgba(255,122,89,.10), transparent 28%),
        linear-gradient(180deg, #07111a 0%, #091521 100%);
      color:var(--text);
      font-family:"Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
    }
    .app{padding:28px; display:grid; gap:20px;}
    .hero,.panel,.card{
      background:linear-gradient(180deg, rgba(255,255,255,.04), rgba(255,255,255,.02));
      border:1px solid var(--line);
      border-radius:24px;
      box-shadow:var(--shadow);
      backdrop-filter:blur(12px);
    }
    .hero{padding:28px; display:grid; gap:18px; overflow:hidden; position:relative;}
    .hero::after{
      content:"";
      position:absolute; inset:auto -8% -30% auto;
      width:280px; height:280px; border-radius:50%;
      background:radial-gradient(circle, rgba(72,213,255,.16), transparent 70%);
      pointer-events:none;
      animation:floatGlow 4.8s ease-in-out infinite;
    }
    @keyframes floatGlow{0%,100%{transform:translateY(0)}50%{transform:translateY(-12px)}}
    .eyebrow{font-size:12px; letter-spacing:.22em; text-transform:uppercase; color:var(--muted)}
    .title-row{display:flex; justify-content:space-between; align-items:flex-start; gap:20px; flex-wrap:wrap}
    h1{margin:0; font-size:40px; line-height:1; font-weight:700;}
    .hero-meta{display:flex; gap:12px; flex-wrap:wrap}
    .pill{
      padding:8px 12px; border-radius:999px; background:rgba(255,255,255,.05);
      border:1px solid var(--line); color:var(--muted); font-size:13px;
    }
    .status-pill.running{color:var(--accent)}
    .status-pill.completed{color:var(--success)}
    .status-pill.blocked,.status-pill.failed{color:var(--danger)}
    .status-pill.waiting_manual{color:var(--warning)}
    .status-pill.skipped{color:var(--muted)}
    .friendly{
      max-width:820px; font-size:16px; line-height:1.7; color:#dce6f2;
      padding:16px 18px; border-radius:18px; background:rgba(255,255,255,.035); border:1px solid var(--line);
    }
    .grid{display:grid; grid-template-columns:2fr 1fr; gap:20px;}
    .panel{padding:20px;}
    .workflow-header,.side-header{display:flex; justify-content:space-between; align-items:center; gap:12px; margin-bottom:16px;}
    .workflow{display:grid; gap:12px;}
    .stage{
      position:relative; padding:18px 18px 16px; border-radius:22px; background:linear-gradient(180deg, rgba(255,255,255,.045), rgba(255,255,255,.025));
      border:1px solid transparent; transform-origin:center; transition:transform .35s ease, border-color .35s ease, background .35s ease, opacity .35s ease;
      opacity:.78;
    }
    .stage.current{transform:translateY(-4px) scale(1.01); border-color:rgba(72,213,255,.42); opacity:1;}
    .stage.completed{border-color:rgba(103,214,154,.24)}
    .stage.blocked,.stage.failed{border-color:rgba(255,122,89,.34)}
    .stage.waiting_manual{border-color:rgba(255,189,89,.34)}
    .stage:hover{transform:translateY(-4px) perspective(1000px) rotateX(2deg);}
    .stage::before{
      content:""; position:absolute; inset:0; border-radius:22px; pointer-events:none; opacity:0;
      background:radial-gradient(circle at top left, rgba(72,213,255,.18), transparent 45%);
      transition:opacity .35s ease;
    }
    .stage.current::before{opacity:1; animation:pulseGlow 2.8s ease-in-out infinite}
    @keyframes pulseGlow{0%,100%{opacity:.42}50%{opacity:.9}}
    .stage-top{display:flex; justify-content:space-between; gap:12px; align-items:center;}
    .stage-title{font-size:22px; font-weight:700;}
    .stage-sub{font-size:13px; color:var(--muted); margin-top:8px;}
    .subphases{display:flex; gap:8px; flex-wrap:wrap; margin-top:14px;}
    .subphase{
      padding:6px 10px; border-radius:999px; font-size:12px; border:1px solid var(--line); color:var(--muted);
      background:rgba(255,255,255,.03);
    }
    .subphase.running,.badge.running{color:var(--accent)}
    .subphase.completed,.badge.completed{color:var(--success)}
    .subphase.blocked,.subphase.failed,.badge.blocked,.badge.failed{color:var(--danger)}
    .subphase.waiting_manual,.badge.waiting_manual{color:var(--warning)}
    .drawer,.timeline,.features{display:grid; gap:10px;}
    .artifact,.event,.feature{
      padding:14px 16px; border-radius:18px; background:rgba(255,255,255,.03); border:1px solid var(--line);
      transition:transform .28s ease, border-color .28s ease;
    }
    .artifact:hover,.event:hover,.feature:hover{transform:translateY(-2px); border-color:rgba(72,213,255,.28)}
    .artifact-title,.feature-title{font-weight:600}
    .artifact-meta,.event-meta,.feature-meta{font-size:12px; color:var(--muted); margin-top:6px; line-height:1.6}
    .artifact-path{font-size:12px; color:#7fdcff; word-break:break-all; margin-top:8px}
    .timeline{max-height:360px; overflow:auto; padding-right:4px}
    .features{max-height:360px; overflow:auto; padding-right:4px}
    .empty{color:var(--muted); font-size:14px}
    @media (max-width: 1100px){.grid{grid-template-columns:1fr}}
    @media (max-width: 720px){.app{padding:16px} h1{font-size:30px}}
  </style>
</head>
<body>
  <main class="app">
    <section class="hero">
      <div class="eyebrow">VibeFlow Editorial Ops Dashboard</div>
      <div class="title-row">
        <div>
          <h1 id="title">Workflow Overview</h1>
          <div class="hero-meta">
            <div class="pill" id="mode"></div>
            <div class="pill status-pill" id="status"></div>
            <div class="pill" id="phase"></div>
            <div class="pill" id="change"></div>
          </div>
        </div>
        <div class="pill" id="updated"></div>
      </div>
      <div class="friendly" id="friendly"></div>
    </section>
    <section class="grid">
      <div class="panel">
        <div class="workflow-header">
          <div>
            <div class="eyebrow">Workflow Spine</div>
            <div>多阶段状态一眼看清，当前阶段会自己呼吸。</div>
          </div>
          <div class="pill" id="feature-summary"></div>
        </div>
        <div class="workflow" id="workflow"></div>
      </div>
      <div class="panel">
        <div class="side-header">
          <div>
            <div class="eyebrow">Artifacts</div>
            <div>关键产物与用途说明</div>
          </div>
        </div>
        <div class="drawer" id="artifacts"></div>
      </div>
    </section>
    <section class="grid">
      <div class="panel">
        <div class="side-header">
          <div>
            <div class="eyebrow">Build Detail</div>
            <div>功能级状态，后续并行 lane 也会落在这里</div>
          </div>
        </div>
        <div class="features" id="features"></div>
      </div>
      <div class="panel">
        <div class="side-header">
          <div>
            <div class="eyebrow">Event Timeline</div>
            <div>最近的阶段推进、失败、完成事件</div>
          </div>
        </div>
        <div class="timeline" id="timeline"></div>
      </div>
    </section>
  </main>
  <script>
    const qs = (id) => document.getElementById(id);
    const statusLabel = (status) => {
      const labels = {
        running: "Running",
        completed: "Completed",
        blocked: "Blocked",
        failed: "Failed",
        waiting_manual: "Waiting Manual",
        skipped: "Skipped",
        pending: "Pending",
        idle: "Idle"
      };
      return labels[status] || status;
    };
    const escapeHtml = (value) => String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;");

    function renderWorkflow(cards, currentPhase) {
      qs("workflow").innerHTML = cards.map(card => {
        const cls = ["stage", card.status];
        if (currentPhase && card.phases.some(item => item.key === currentPhase) || card.key === currentPhase) cls.push("current");
        return `
          <article class="${cls.join(" ")}">
            <div class="stage-top">
              <div class="stage-title">${escapeHtml(card.label)}</div>
              <div class="pill badge ${card.status}">${escapeHtml(statusLabel(card.status))}</div>
            </div>
            <div class="stage-sub">${escapeHtml(card.key)}</div>
            <div class="subphases">
              ${card.phases.map(phase => `<span class="subphase ${phase.status}">${escapeHtml(phase.key)} · ${escapeHtml(statusLabel(phase.status))}</span>`).join("")}
            </div>
          </article>
        `;
      }).join("");
    }

    function renderArtifacts(artifacts) {
      qs("artifacts").innerHTML = artifacts.map(item => `
        <article class="artifact">
          <div class="artifact-title">${escapeHtml(item.key)}</div>
          <div class="artifact-meta">${escapeHtml(item.description)}</div>
          <div class="artifact-meta">${item.exists ? "已生成" : "尚未生成"}</div>
          <div class="artifact-path">${escapeHtml(item.path)}</div>
        </article>
      `).join("");
    }

    function renderFeatures(features) {
      if (!features.items.length) {
        qs("features").innerHTML = `<div class="empty">还没有可展示的 feature 状态。</div>`;
        return;
      }
      qs("features").innerHTML = features.items.map(item => `
        <article class="feature">
          <div class="feature-title">#${escapeHtml(item.id)} ${escapeHtml(item.title)}</div>
          <div class="feature-meta">状态：${escapeHtml(item.status)} · 优先级：${escapeHtml(item.priority)} · 依赖：${item.dependencies.length ? escapeHtml(item.dependencies.join(", ")) : "无"}</div>
        </article>
      `).join("");
    }

    function renderTimeline(events) {
      if (!events.length) {
        qs("timeline").innerHTML = `<div class="empty">还没有事件。</div>`;
        return;
      }
      qs("timeline").innerHTML = events.map(item => `
        <article class="event">
          <div class="artifact-title">${escapeHtml(item.title)}</div>
          <div class="event-meta">${escapeHtml(item.timestamp || "")}</div>
          <div class="event-meta">${escapeHtml(item.detail || "")}</div>
        </article>
      `).join("");
    }

    function render(snapshot) {
      qs("title").textContent = snapshot.project;
      qs("mode").textContent = `Mode · ${snapshot.mode}`;
      qs("status").textContent = statusLabel(snapshot.status);
      qs("status").className = `pill status-pill ${snapshot.status}`;
      qs("phase").textContent = `Phase · ${snapshot.current_phase}`;
      qs("change").textContent = `Change · ${snapshot.active_change.id || "-"}`;
      qs("updated").textContent = `Updated · ${snapshot.generated_at}`;
      qs("friendly").textContent = snapshot.friendly_message;
      qs("feature-summary").textContent = `Features ${snapshot.features.passing}/${snapshot.features.total}`;
      renderWorkflow(snapshot.workflow, snapshot.current_phase);
      renderArtifacts(snapshot.artifacts);
      renderFeatures(snapshot.features);
      renderTimeline(snapshot.events);
    }

    async function fetchSnapshot() {
      const response = await fetch("/api/snapshot", { cache: "no-store" });
      const payload = await response.json();
      render(payload);
    }

    fetchSnapshot();
    if (window.EventSource) {
      const stream = new EventSource("/api/events");
      stream.addEventListener("snapshot", (event) => render(JSON.parse(event.data)));
      stream.onerror = () => {};
    } else {
      setInterval(fetchSnapshot, 2000);
    }
  </script>
</body>
</html>"""


def make_handler(project_root: Path):
    class DashboardHandler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):  # noqa: A003
            return

        def _send_json(self, payload: dict, status: int = HTTPStatus.OK) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):  # noqa: N802
            parsed = urlparse(self.path)
            if parsed.path == "/":
                body = dashboard_html().encode("utf-8")
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return

            if parsed.path == "/api/snapshot":
                self._send_json(build_dashboard_snapshot(project_root))
                return

            if parsed.path == "/api/events":
                params = parse_qs(parsed.query)
                once = params.get("once", ["0"])[0] == "1"
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Cache-Control", "no-store")
                self.send_header("Connection", "close" if once else "keep-alive")
                self.end_headers()

                last_token = None
                iterations = 1 if once else 300
                for _ in range(iterations):
                    snapshot = build_dashboard_snapshot(project_root)
                    if snapshot["token"] != last_token:
                        payload = json.dumps(snapshot, ensure_ascii=False)
                        try:
                            self.wfile.write(f"event: snapshot\ndata: {payload}\n\n".encode("utf-8"))
                            self.wfile.flush()
                        except (BrokenPipeError, ConnectionResetError):
                            break
                        last_token = snapshot["token"]
                    if once:
                        break
                    time.sleep(1)
                self.close_connection = True
                return

            self._send_json({"error": "not found"}, status=HTTPStatus.NOT_FOUND)

    return DashboardHandler


def run_dashboard_server(project_root: Path, host: str = "127.0.0.1", port: int = 4317) -> ThreadingHTTPServer:
    server = ThreadingHTTPServer((host, port), make_handler(project_root.resolve()))
    return server


def serve_in_background(project_root: Path, host: str = "127.0.0.1", port: int = 4317) -> tuple[ThreadingHTTPServer, threading.Thread]:
    server = run_dashboard_server(project_root, host=host, port=port)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread
