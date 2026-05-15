from __future__ import annotations

from html import escape

from app.services.evidence_pipeline_service import build_service


SERVICE = build_service()


def _summary() -> dict:
    return SERVICE.summary()


def _verdict_class(verdict: str) -> str:
    return {"healthy": "healthy", "watch": "watch", "critical": "critical"}[verdict]


def _nav_link(href: str, label: str, current: str, key: str) -> str:
    state = "active" if current == key else ""
    return f'<a class="nav-link {state}" href="{href}">{escape(label)}</a>'


def _status_badge(verdict: str) -> str:
    return f'<span class="badge {_verdict_class(verdict)}">{escape(verdict.upper())}</span>'


def _kpi_card(label: str, value: str, note: str, progress: int, tone: str = "violet") -> str:
    return f"""
    <article class="kpi-card">
      <div class="kpi-top">
        <span class="eyebrow">{escape(label)}</span>
        <span class="arrow">→</span>
      </div>
      <div class="kpi-value">{escape(value)}</div>
      <div class="progress-track"><div class="progress-fill {tone}" style="width:{progress}%"></div></div>
      <p class="kpi-note">{escape(note)}</p>
    </article>
    """


def _component_card(component: dict) -> str:
    status_class = "hot" if component["status"] == "watch" else "good"
    return f"""
    <article class="component-card">
      <div class="component-icon">{escape(component["name"][0])}</div>
      <div class="component-copy">
        <div class="component-top">
          <strong>{escape(component["name"])}</strong>
          <span class="component-cpu {status_class}">{component["cpu"]}% CPU</span>
        </div>
        <div class="progress-track slim"><div class="progress-fill {status_class}" style="width:{component["cpu"]}%"></div></div>
        <div class="component-metrics">
          <span>{component["ramGb"]}GB RAM</span>
          <span>{component["networkMb"]}MB/S NET</span>
        </div>
      </div>
      <span class="live-dot"></span>
    </article>
    """


def _line_chart() -> str:
    series = SERVICE.sync_velocity()
    max_syncs = max(item["syncs"] for item in series)
    points = []
    labels = []
    base_x = 34
    step = 132
    for index, item in enumerate(series):
        x = base_x + (index * step)
        y = 208 - round((item["syncs"] / max_syncs) * 108)
        points.append(f"{x},{y}")
        labels.append(f'<span>{escape(item["hour"])}</span>')
    return f"""
    <section class="trend-card">
      <div class="trend-head">
        <div>
          <span class="eyebrow">Sync volume trends</span>
          <h3>Traffic and packaging pressure across the evidence lane.</h3>
        </div>
        <div class="legend-dot"><i></i> Sync volume</div>
      </div>
      <svg viewBox="0 0 860 250" class="line-chart" aria-label="Sync volume trend">
        <defs>
          <linearGradient id="syncFill" x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stop-color="rgba(91, 92, 246, 0.22)" />
            <stop offset="100%" stop-color="rgba(91, 92, 246, 0.01)" />
          </linearGradient>
        </defs>
        <line x1="20" y1="72" x2="840" y2="72" class="chart-rule"></line>
        <line x1="20" y1="128" x2="840" y2="128" class="chart-rule"></line>
        <line x1="20" y1="184" x2="840" y2="184" class="chart-rule"></line>
        <polyline fill="none" stroke="#5d5cf6" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" points="{' '.join(points)}"></polyline>
        <polygon fill="url(#syncFill)" points="{' '.join(points)} 826,218 34,218"></polygon>
      </svg>
      <div class="chart-labels">{''.join(labels)}</div>
    </section>
    """


def _distribution_card() -> str:
    monitor = SERVICE.health_monitor()
    rows = []
    for item in monitor["distribution"]:
        rows.append(
            f"""
            <div class="dist-row">
              <div class="dist-top"><strong>{escape(item["name"])}</strong><span>{item["share"]}%</span></div>
              <div class="progress-track dark"><div class="progress-fill violet" style="width:{item["share"]}%"></div></div>
            </div>
            """
        )
    totals = monitor["totals"]
    return f"""
    <section class="distribution-card">
      <span class="eyebrow">Node distribution</span>
      {''.join(rows)}
      <div class="dist-foot">
        <span>Active processes</span>
        <strong>{totals["activeProcesses"]} units</strong>
      </div>
    </section>
    """


def _pipeline_topology() -> str:
    stages = [
        ("Source", "Identity Capture", "Ingesting change requests and user metadata from ServiceNow.", "standby"),
        ("Core", "Pipeline Engine", "Decrypting metadata and mapping incident logs into evidence-ready packages.", "active"),
        ("Target", "Mapping Engine", "Aggregating session logs into audit-ready JSON-parsed packages.", "standby"),
    ]
    cards = []
    for stage, title, desc, status in stages:
        status_text = "Active" if status == "active" else "Standby"
        cards.append(
            f"""
            <article class="topology-card {status}">
              <span class="eyebrow">{escape(stage)}</span>
              <h4>{escape(title)}</h4>
              <p>{escape(desc)}</p>
              <div class="topology-status">{escape(status_text)}</div>
            </article>
            """
        )
    return f"""
    <section class="topology-grid">
      {cards[0]}
      <div class="topology-core">
        <div class="core-orbit">
          <div class="core-icon">⛓</div>
          <h4>Pipeline Engine</h4>
          <p>Decrypting metadata and mapping incident logs into audit-ready packages.</p>
          <div class="core-dots"><i></i><i></i><i></i></div>
        </div>
      </div>
      {cards[2]}
    </section>
    """


def _bundle_table() -> str:
    rows = []
    for bundle in SERVICE.evidence_bundles()[:4]:
        rows.append(
            f"""
            <tr>
              <td><strong>{escape(bundle["incidentId"].replace("INC", "TX-"))}</strong></td>
              <td>{escape(bundle["requiredEvidence"][0].replace(" artifact chain", "").replace(" ", "_").title())}</td>
              <td>{escape(bundle["accountName"])}</td>
              <td>{escape(bundle["incidentId"])}</td>
              <td>{'VERIFIED' if bundle["bundleReady"] else 'SYNCING' if bundle["verdict"] == 'watch' else 'PENDING'}</td>
            </tr>
            """
        )
    return f"""
    <section class="table-card">
      <div class="filter-row">
        <span class="filter-chip active">All</span>
        <span class="filter-chip">Verified</span>
        <span class="filter-chip">Syncing</span>
        <span class="filter-chip">Pending</span>
      </div>
      <table>
        <thead>
          <tr>
            <th>Transaction ID</th>
            <th>Evidence Type</th>
            <th>CyberArk Vault</th>
            <th>Snow Ref</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {''.join(rows)}
        </tbody>
      </table>
    </section>
    """


def _shell(title: str, subtitle: str, current: str, body: str) -> str:
    summary = _summary()
    monitor = SERVICE.health_monitor()
    tabs = [
        ("/", "Dashboard", "overview"),
        ("/security-architecture", "Security & Architecture", "architecture"),
        ("/audit-log", "Audit Trail", "audit"),
    ]
    sidebar = [
        ("/", "Dashboard", "overview"),
        ("/pipeline-board", "Pipeline Board", "pipeline"),
        ("/bundles", "Evidence Bundles", "bundles"),
        ("/monitor", "System Monitor", "monitor"),
        ("/security-architecture", "Security & Architecture", "architecture"),
        ("/integrations", "Integration Posture", "integrations"),
        ("/methodology", "Methodology", "methodology"),
        ("/docs", "Docs", "docs"),
    ]
    return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{escape(title)}</title>
    <style>
      :root {{
        --page: #eef2f7;
        --nav: #121a2f;
        --nav-soft: #202a41;
        --panel: #ffffff;
        --ink: #1b2a41;
        --muted: #6f86a4;
        --line: #dfe6f0;
        --violet: #5d5cf6;
        --violet-soft: rgba(93, 92, 246, 0.12);
        --green: #16c784;
        --green-soft: rgba(22, 199, 132, 0.12);
        --amber: #f5b94c;
        --amber-soft: rgba(245, 185, 76, 0.16);
        --red: #ff5c7a;
        --red-soft: rgba(255, 92, 122, 0.14);
        --shadow: 0 24px 54px rgba(22, 32, 55, 0.08);
      }}
      * {{ box-sizing: border-box; }}
      body {{
        margin: 0;
        font-family: "Segoe UI", Inter, system-ui, sans-serif;
        color: var(--ink);
        background:
          radial-gradient(circle at top left, rgba(93, 92, 246, 0.08), transparent 18%),
          linear-gradient(180deg, #f7f9fc 0%, var(--page) 100%);
      }}
      a {{ color: inherit; text-decoration: none; }}
      .topbar {{
        position: sticky; top: 0; z-index: 5;
        display: flex; align-items: center; justify-content: space-between;
        gap: 18px; padding: 18px 30px; background: var(--nav); color: white;
        box-shadow: 0 16px 40px rgba(6, 12, 24, 0.24);
      }}
      .brand {{ display: flex; align-items: center; gap: 16px; }}
      .brand-mark {{
        width: 46px; height: 46px; border-radius: 12px; display: grid; place-items: center;
        background: linear-gradient(135deg, #5d5cf6, #7b68ff); font-weight: 900; font-size: 26px;
      }}
      .brand-copy strong {{ display: block; font-size: 20px; letter-spacing: 0.02em; }}
      .brand-copy span {{ display: block; margin-top: 2px; color: #b9c5dc; font-size: 12px; }}
      .top-tabs {{
        display: flex; align-items: center; gap: 8px; padding: 8px; border-radius: 16px;
        background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.05);
      }}
      .nav-link {{
        display: inline-flex; align-items: center; justify-content: center;
        padding: 12px 18px; border-radius: 12px; color: #b6c4db; font-size: 11px;
        font-weight: 800; text-transform: uppercase; letter-spacing: 0.12em;
      }}
      .nav-link.active {{ background: var(--violet); color: white; box-shadow: 0 12px 28px rgba(93, 92, 246, 0.32); }}
      .top-actions {{ display: flex; align-items: center; gap: 12px; }}
      .action {{
        padding: 11px 16px; border-radius: 14px; background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08); color: #cad5ea; font-weight: 700;
      }}
      .status-live {{ display: inline-flex; align-items: center; gap: 10px; color: #14d18a; font-size: 11px; font-weight: 900; letter-spacing: 0.12em; text-transform: uppercase; }}
      .status-live i {{ width: 10px; height: 10px; border-radius: 50%; background: #14d18a; box-shadow: 0 0 16px rgba(20, 209, 138, 0.7); }}
      .page {{ max-width: 1720px; margin: 26px auto 24px; padding: 0 22px 24px; }}
      .hero {{
        display: grid; gap: 20px; grid-template-columns: 1.55fr 1fr;
        padding: 24px; background: white; border: 1px solid var(--line); border-radius: 28px; box-shadow: var(--shadow);
      }}
      .eyebrow {{ color: #7c8ea9; font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.16em; }}
      h1 {{ margin: 14px 0 10px; font-size: clamp(40px, 4vw, 64px); line-height: 0.95; letter-spacing: -0.05em; font-family: Georgia, "Times New Roman", serif; }}
      .hero p {{ margin: 0; color: var(--muted); font-size: 18px; line-height: 1.6; max-width: 860px; }}
      .lead-box {{
        border-radius: 20px; padding: 18px 20px; margin-top: 18px; background: linear-gradient(180deg, #f7f8ff, #f2f4ff);
        border: 1px solid #dce2ff;
      }}
      .lead-box strong {{ display: block; color: #5d5cf6; font-size: 10px; text-transform: uppercase; letter-spacing: 0.18em; margin-bottom: 8px; }}
      .lead-box span {{ font-size: 16px; line-height: 1.55; color: #243754; }}
      .hero-side {{
        border-radius: 24px; padding: 22px; background: linear-gradient(180deg, #131d34, #10182a);
        color: white; display: grid; gap: 18px;
      }}
      .hero-side h3 {{ margin: 0; font-size: 18px; letter-spacing: 0.01em; }}
      .hero-side p {{ margin: 0; color: #bdc9df; font-size: 14px; line-height: 1.6; }}
      .hero-side .meta-row {{ display: flex; justify-content: space-between; gap: 18px; color: #8fa1bf; font-size: 11px; text-transform: uppercase; letter-spacing: 0.12em; }}
      .hero-side .meta-row strong {{ color: white; font-size: 12px; }}
      .grid-4 {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 18px; margin-top: 20px; }}
      .grid-2plus {{ display: grid; grid-template-columns: minmax(0, 1.2fr) minmax(360px, 0.58fr); gap: 18px; margin-top: 18px; }}
      .grid-3 {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 18px; margin-top: 18px; }}
      .kpi-card, .trend-card, .distribution-card, .panel, .table-card {{
        background: white; border: 1px solid var(--line); border-radius: 24px; box-shadow: var(--shadow);
      }}
      .kpi-card {{ padding: 22px 24px; }}
      .kpi-top {{ display: flex; justify-content: space-between; gap: 10px; align-items: center; }}
      .arrow {{ color: #b3c0d4; font-size: 18px; }}
      .kpi-value {{ margin-top: 10px; font-size: 44px; font-style: italic; font-weight: 800; letter-spacing: -0.04em; }}
      .progress-track {{ margin-top: 16px; height: 7px; border-radius: 999px; background: #edf1f6; overflow: hidden; }}
      .progress-track.slim {{ height: 6px; margin-top: 10px; }}
      .progress-track.dark {{ background: rgba(255,255,255,0.08); }}
      .progress-fill {{ height: 100%; border-radius: 999px; }}
      .progress-fill.violet {{ background: linear-gradient(90deg, #5d5cf6, #746dff); }}
      .progress-fill.good {{ background: linear-gradient(90deg, #19bf7f, #2bd49b); }}
      .progress-fill.hot {{ background: linear-gradient(90deg, #ff5c7a, #ff8a64); }}
      .kpi-note {{ margin: 14px 0 0; color: var(--muted); font-size: 14px; line-height: 1.5; }}
      .component-grid {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 18px; margin-top: 18px; }}
      .component-card {{
        position: relative; display: grid; grid-template-columns: 74px minmax(0, 1fr); gap: 16px;
        padding: 22px; background: white; border-radius: 24px; border: 1px solid var(--line); box-shadow: var(--shadow);
      }}
      .component-icon {{
        width: 74px; height: 64px; border-radius: 18px; display: grid; place-items: center;
        background: linear-gradient(180deg, #ebf4ef, #f4fbf7); color: #27c58b; font-size: 28px; font-weight: 900;
      }}
      .component-card .live-dot {{
        position: absolute; top: 18px; right: 18px; width: 10px; height: 10px; border-radius: 50%;
        background: #3ce0a3;
      }}
      .component-top {{ display: flex; justify-content: space-between; gap: 12px; align-items: center; }}
      .component-top strong {{ font-size: 16px; }}
      .component-cpu {{ font-size: 12px; font-weight: 800; }}
      .component-cpu.good {{ color: #1abc7d; }}
      .component-cpu.hot {{ color: #ff5776; }}
      .component-metrics {{ display: flex; justify-content: space-between; gap: 12px; margin-top: 12px; color: var(--muted); font-size: 12px; font-weight: 700; }}
      .trend-card {{ padding: 22px 24px; }}
      .trend-head {{ display: flex; justify-content: space-between; gap: 18px; align-items: start; }}
      .trend-head h3 {{ margin: 8px 0 0; font-size: 20px; letter-spacing: -0.02em; }}
      .legend-dot {{ display: inline-flex; align-items: center; gap: 8px; color: var(--muted); font-size: 12px; font-weight: 700; }}
      .legend-dot i {{ width: 12px; height: 12px; border-radius: 50%; background: #5d5cf6; display: inline-block; }}
      .line-chart {{ width: 100%; height: auto; margin-top: 10px; }}
      .chart-rule {{ stroke: #dfe5ee; stroke-dasharray: 5 8; }}
      .chart-labels {{ display: flex; justify-content: space-between; margin-top: -6px; color: #93a5bf; font-size: 12px; padding: 0 12px; }}
      .distribution-card {{
        padding: 24px; background: linear-gradient(180deg, #141d34, #10182b); color: white;
      }}
      .dist-row + .dist-row {{ margin-top: 22px; }}
      .dist-top {{ display: flex; justify-content: space-between; gap: 12px; margin-bottom: 10px; }}
      .dist-top strong {{ font-size: 16px; }}
      .dist-top span {{ color: #8da2c7; font-weight: 800; }}
      .dist-foot {{ display: flex; justify-content: space-between; gap: 12px; margin-top: 34px; padding-top: 18px; border-top: 1px solid rgba(255,255,255,0.08); color: #90a2bf; text-transform: uppercase; font-size: 12px; letter-spacing: 0.12em; }}
      .dist-foot strong {{ color: #18d28c; font-size: 22px; }}
      .topology-grid {{ display: grid; grid-template-columns: minmax(0, 1fr) 1.2fr minmax(0, 1fr); gap: 18px; margin-top: 18px; align-items: center; }}
      .topology-card {{
        min-height: 240px; padding: 24px; border-radius: 24px; background: white; border: 1px solid var(--line); box-shadow: var(--shadow);
      }}
      .topology-card.target {{ background: linear-gradient(180deg, #172038, #12192c); color: white; }}
      .topology-card h4, .core-orbit h4 {{ margin: 16px 0 10px; font-size: 24px; letter-spacing: -0.03em; }}
      .topology-card p, .core-orbit p {{ margin: 0; color: var(--muted); font-size: 15px; line-height: 1.65; }}
      .topology-card.target p {{ color: #b6c3d8; }}
      .topology-status {{ margin-top: 24px; color: #98aaca; font-size: 11px; font-weight: 900; letter-spacing: 0.16em; text-transform: uppercase; }}
      .topology-core {{
        position: relative; min-height: 280px; display: grid; place-items: center; border-radius: 28px;
        background: linear-gradient(180deg, #f8faff, #f2f5ff); border: 1px solid #dfe6ff; box-shadow: var(--shadow);
      }}
      .topology-core::before, .topology-core::after {{
        content: ""; position: absolute; top: 50%; width: 23%; height: 2px; background: linear-gradient(90deg, rgba(93,92,246,0.05), rgba(93,92,246,0.35), rgba(93,92,246,0.05));
      }}
      .topology-core::before {{ left: 0; }}
      .topology-core::after {{ right: 0; }}
      .core-orbit {{
        width: 360px; height: 360px; border-radius: 50%; background: white; display: grid; place-items: center;
        text-align: center; box-shadow: inset 0 0 0 16px rgba(93, 92, 246, 0.06);
      }}
      .core-icon {{
        width: 90px; height: 90px; border-radius: 26px; display: grid; place-items: center;
        background: linear-gradient(135deg, #5d5cf6, #7e6eff); color: white; font-size: 42px; font-weight: 900;
        box-shadow: 0 24px 44px rgba(93, 92, 246, 0.28);
      }}
      .core-dots {{ display: flex; gap: 10px; justify-content: center; margin-top: 14px; }}
      .core-dots i {{ width: 8px; height: 8px; border-radius: 50%; background: rgba(93, 92, 246, 0.35); }}
      .core-dots i:nth-child(2) {{ background: rgba(93, 92, 246, 0.85); }}
      .table-card {{ padding: 18px 20px 10px; margin-top: 18px; overflow: hidden; }}
      .filter-row {{ display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 14px; }}
      .filter-chip {{
        display: inline-flex; align-items: center; padding: 10px 14px; border-radius: 999px;
        border: 1px solid var(--line); color: #93a2b8; background: #f9fbff; font-size: 12px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.08em;
      }}
      .filter-chip.active {{ color: white; border-color: #5d5cf6; background: #5d5cf6; }}
      table {{ width: 100%; border-collapse: collapse; }}
      th, td {{ padding: 16px 14px; text-align: left; vertical-align: top; }}
      thead th {{ color: #8ea1bc; font-size: 11px; font-weight: 900; text-transform: uppercase; letter-spacing: 0.12em; }}
      tbody tr + tr td {{ border-top: 1px solid #edf1f6; }}
      tbody td {{ font-size: 14px; color: #20324d; }}
      .panel {{ padding: 24px; }}
      .panel h2 {{ margin: 12px 0 8px; font-size: 28px; letter-spacing: -0.03em; font-family: Georgia, "Times New Roman", serif; }}
      .panel p {{ margin: 0; color: var(--muted); font-size: 15px; line-height: 1.65; }}
      .mini-panel {{ border-radius: 20px; background: #f8faff; border: 1px solid #ebf0f7; padding: 18px; }}
      .mini-panel h3 {{ margin: 0 0 8px; font-size: 15px; }}
      .mini-panel p {{ font-size: 14px; }}
      .badge {{
        display: inline-flex; align-items: center; justify-content: center; padding: 8px 12px; border-radius: 999px;
        font-size: 11px; font-weight: 900; letter-spacing: 0.12em; text-transform: uppercase;
      }}
      .badge.healthy {{ color: #10a86e; background: var(--green-soft); }}
      .badge.watch {{ color: #d89318; background: var(--amber-soft); }}
      .badge.critical {{ color: #e54565; background: var(--red-soft); }}
      .incident-card {{
        padding: 22px 24px; border-radius: 24px; background: white; border: 1px solid var(--line); box-shadow: var(--shadow);
      }}
      .incident-head {{ display: flex; justify-content: space-between; gap: 16px; align-items: start; }}
      .incident-head h3 {{ margin: 0; font-size: 28px; letter-spacing: -0.04em; }}
      .incident-copy p {{ margin: 10px 0 0; color: var(--muted); font-size: 15px; line-height: 1.6; }}
      .incident-meta {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; margin-top: 18px; }}
      .meta-chip {{ padding: 14px 16px; border-radius: 16px; background: #f7faff; border: 1px solid #ebf0f7; }}
      .meta-chip span {{ display: block; color: #8a9cb6; font-size: 10px; text-transform: uppercase; letter-spacing: 0.16em; font-weight: 800; }}
      .meta-chip strong {{ display: block; margin-top: 8px; font-size: 16px; }}
      .log-shell {{ overflow: hidden; border-radius: 24px; background: #121a2f; color: white; box-shadow: var(--shadow); }}
      .log-head {{ display: flex; align-items: center; gap: 12px; padding: 16px 18px; border-bottom: 1px solid rgba(255,255,255,0.08); }}
      .lights {{ display: flex; gap: 8px; }}
      .lights i {{ width: 11px; height: 11px; border-radius: 50%; display: block; }}
      .lights i:nth-child(1) {{ background: rgba(255, 92, 122, 0.75); }}
      .lights i:nth-child(2) {{ background: rgba(245, 185, 76, 0.75); }}
      .lights i:nth-child(3) {{ background: rgba(20, 209, 138, 0.75); }}
      .log-title {{ color: #c4d0e8; font-size: 11px; font-weight: 900; text-transform: uppercase; letter-spacing: 0.16em; }}
      .log-body {{ padding: 16px; display: grid; gap: 10px; }}
      .log-line {{
        display: grid; grid-template-columns: 170px 220px minmax(0, 1fr) 90px;
        gap: 14px; padding: 12px 14px; border-radius: 16px; background: rgba(255,255,255,0.03);
      }}
      .log-line time {{ color: #89a0c2; font-family: Consolas, monospace; font-size: 12px; }}
      .log-line strong {{ color: #6fc6ff; font-family: Consolas, monospace; font-size: 12px; letter-spacing: 0.06em; }}
      .log-line p {{ margin: 0; color: #d9e3f5; font-size: 13px; line-height: 1.5; }}
      .terminal-card {{ background: linear-gradient(180deg, #121a2f, #101728); color: white; border: 1px solid rgba(255,255,255,0.05); border-radius: 24px; box-shadow: var(--shadow); overflow: hidden; }}
      .terminal-card pre {{ margin: 0; padding: 18px; font-size: 13px; line-height: 1.7; font-family: Consolas, "Cascadia Code", monospace; white-space: pre-wrap; }}
      .footer {{
        display: flex; justify-content: space-between; gap: 14px; margin-top: 22px; padding: 14px 4px 0;
        color: #7f91aa; font-size: 12px; align-items: center;
      }}
      .footer .right {{ display: flex; align-items: center; gap: 10px; }}
      .footer .right i {{ width: 8px; height: 8px; border-radius: 50%; background: #16c784; }}
      @media (max-width: 1280px) {{
        .hero, .grid-2plus, .topology-grid {{ grid-template-columns: 1fr; }}
        .grid-4, .component-grid, .grid-3, .incident-meta {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
        .topbar {{ flex-wrap: wrap; }}
      }}
      @media (max-width: 880px) {{
        .grid-4, .component-grid, .grid-3, .incident-meta {{ grid-template-columns: 1fr; }}
        .top-tabs {{ width: 100%; overflow: auto; }}
        .log-line {{ grid-template-columns: 1fr; }}
      }}
    </style>
  </head>
  <body>
    <header class="topbar">
      <div class="brand">
        <div class="brand-mark">P</div>
        <div class="brand-copy">
          <strong>Evidence Pipeline</strong>
          <span>ServiceNow → CyberArk Bridge</span>
        </div>
      </div>
      <nav class="top-tabs">
        {''.join(_nav_link(href, label, current, key) for href, label, key in tabs)}
      </nav>
      <div class="top-actions">
        <a class="action" href="/monitor">Monitor</a>
        <a class="action" href="/audit-log">Terminal</a>
        <span class="status-live"><i></i> System active</span>
      </div>
    </header>
    <main class="page">
      <section class="hero">
        <div>
          <span class="eyebrow">ServiceNow CyberArk Evidence Pipeline</span>
          <h1>{escape(title)}</h1>
          <p>{escape(subtitle)}</p>
          <div class="lead-box">
            <strong>Lead recommendation</strong>
            <span>{escape(summary["leadRecommendation"])}</span>
          </div>
        </div>
        <aside class="hero-side">
          <div>
            <span class="eyebrow" style="color:#9db0d1;">System active</span>
            <h3>Evidence bridge posture</h3>
            <p>The pipeline keeps incident state, vault context, evidence aging, and closure artifacts visible in the same operating lane.</p>
          </div>
          <div class="meta-row"><span>Total syncs (24h)</span><strong>{summary["totalSyncs24h"]:,}</strong></div>
          <div class="meta-row"><span>Pipeline success</span><strong>{summary["pipelineSuccess"]}%</strong></div>
          <div class="meta-row"><span>CyberArk latency</span><strong>{summary["cyberarkLatencyMs"]}ms</strong></div>
          <div class="meta-row"><span>API response</span><strong>{monitor["totals"]["apiResponseMs"]}ms</strong></div>
        </aside>
      </section>
      {body}
      <footer class="footer">
        <span>v2.4.1-stable · Connected to: ServiceNow-Instance-01</span>
        <div class="right"><i></i><span>Worker Node #12 Health: Excellent</span></div>
      </footer>
    </main>
  </body>
</html>"""


def render_overview() -> str:
    summary = _summary()
    monitor = SERVICE.health_monitor()
    body = f"""
    <section class="grid-4">
      {_kpi_card("Total syncs (24h)", f"{summary['totalSyncs24h']:,}", "Evidence packets flowing across the bridge in the last day.", 72)}
      {_kpi_card("CyberArk latency", f"{summary['cyberarkLatencyMs']}ms", "Current enrichment latency at the vault edge.", 24)}
      {_kpi_card("Pipeline success", f"{summary['pipelineSuccess']}%", "Successful package assembly and export completion.", 99, "good")}
      {_kpi_card("Critical alerts", str(summary['criticalAlerts']), "High-severity system alerts blocking the packaging lane.", 4)}
    </section>
    <section class="component-grid">
      {''.join(_component_card(component) for component in monitor["components"])}
    </section>
    <section class="grid-2plus">
      {_line_chart()}
      {_distribution_card()}
    </section>
    {_pipeline_topology()}
    {_bundle_table()}
    """
    return _shell(
        "Audit-ready evidence flow for privileged access work.",
        "Control-plane view for sync volume, evidence packaging pressure, and the systems carrying the ServiceNow → CyberArk bridge.",
        "overview",
        body,
    )


def render_pipeline_board() -> str:
    cards = []
    for incident in SERVICE.pipeline_board():
        cards.append(
            f"""
            <article class="incident-card">
              <div class="incident-head">
                <div class="incident-copy">
                  <span class="eyebrow">{escape(incident["assignmentGroup"])}</span>
                  <h3>{escape(incident["incidentId"])} · {escape(incident["accountName"])}</h3>
                  <p>{escape(incident["topConcern"])}</p>
                </div>
                {_status_badge(incident["verdict"])}
              </div>
              <div class="incident-meta">
                <div class="meta-chip"><span>Risk score</span><strong>{incident["riskScore"]}</strong></div>
                <div class="meta-chip"><span>Artifacts</span><strong>{incident["approvalArtifacts"]} attached</strong></div>
                <div class="meta-chip"><span>Evidence age</span><strong>{incident["evidenceAgeDays"]} days</strong></div>
                <div class="meta-chip"><span>Next action</span><strong>{escape(incident["nextAction"])}</strong></div>
              </div>
            </article>
            """
        )
    body = f'<section class="grid-3" style="grid-template-columns: 1fr;">{"".join(cards)}</section>'
    return _shell(
        "Queue the incidents most likely to age into audit debt.",
        "This lane keeps ServiceNow workflow state and CyberArk evidence quality visible together so reviewers know what to fix first.",
        "pipeline",
        body,
    )


def render_bundles() -> str:
    rows = []
    for bundle in SERVICE.evidence_bundles():
        rows.append(
            f"""
            <article class="panel">
              <span class="eyebrow">{escape(bundle["assignmentGroup"])}</span>
              <h2>{escape(bundle["incidentId"])} · {escape(bundle["targetSystem"])}</h2>
              <p>{escape(bundle["accountName"])} · {escape(', '.join(bundle["requiredEvidence"]))}</p>
              <div class="grid-3" style="margin-top:18px;">
                <div class="mini-panel"><h3>Risk score</h3><p>{bundle["riskScore"]}</p></div>
                <div class="mini-panel"><h3>Bundle state</h3><p>{'Ready for review' if bundle['bundleReady'] else 'Needs enrichment'}</p></div>
                <div class="mini-panel"><h3>Targets</h3><p>{escape(', '.join(bundle["governanceTargets"]))}</p></div>
              </div>
            </article>
            """
        )
    body = f'<section class="grid-3" style="grid-template-columns: 1fr;">{"".join(rows)}</section>'
    return _shell(
        "Turn incident state into reusable evidence packets.",
        "Bundle output preserves the artifact checklist, review posture, and governance targets so audit work does not have to reconstruct the story later.",
        "bundles",
        body,
    )


def render_audit_log() -> str:
    log_rows = []
    for row in SERVICE.audit_log():
        result = _status_badge("healthy" if row["result"] == "Success" else "critical")
        log_rows.append(
            f"""
            <div class="log-line">
              <time>{escape(row["timestamp"])}</time>
              <strong>{escape(row["action"])}</strong>
              <p><span style="font-weight:800;">{escape(row["resource"])}</span><br>{escape(row["detail"])}</p>
              {result}
            </div>
            """
        )
    terminal = "\n".join(SERVICE.terminal_feed())
    body = f"""
    <section class="grid-2plus">
      <div class="log-shell">
        <div class="log-head">
          <div class="lights"><i></i><i></i><i></i></div>
          <div class="log-title">Advanced forensic audit trail</div>
        </div>
        <div class="log-body">{''.join(log_rows)}</div>
      </div>
      <div class="terminal-card">
        <div class="log-head">
          <div class="lights"><i></i><i></i><i></i></div>
          <div class="log-title">Operator terminal</div>
        </div>
        <pre>{escape(terminal)}</pre>
      </div>
    </section>
    """
    return _shell(
        "Replayable audit trail for enrichment, failure, and evidence emission.",
        "The useful part is not just collecting events. It is making them legible to reviewers, auditors, and operators under time pressure.",
        "audit",
        body,
    )


def render_integrations() -> str:
    posture = SERVICE.integration_posture()
    target_rows = []
    for target in posture["targets"]:
        target_rows.append(
            f"""
            <div class="mini-panel">
              <h3>{escape(target["name"])}</h3>
              <p>{escape(target["type"])} · {'enabled' if target['enabled'] else 'disabled'}</p>
            </div>
            """
        )
    body = f"""
    <section class="grid-3">
      <div class="panel">
        <span class="eyebrow">ServiceNow</span>
        <h2>Incident intake contract</h2>
        <p>{escape(posture["servicenow"]["authType"])} · {escape(posture["servicenow"]["stateFilter"])}</p>
      </div>
      <div class="panel">
        <span class="eyebrow">CyberArk</span>
        <h2>Vault enrichment contract</h2>
        <p>{escape(posture["cyberark"]["authType"])} · {escape(posture["cyberark"]["dualApprovalModel"])}</p>
      </div>
      <div class="panel">
        <span class="eyebrow">Pipeline</span>
        <h2>Packaging cadence</h2>
        <p>{posture["pipeline"]["intervalMinutes"]}-minute cadence · {escape(posture["pipeline"]["bundleExportFormat"])}</p>
      </div>
    </section>
    <section class="grid-3">{''.join(target_rows)}</section>
    """
    return _shell(
        "Integration posture across the intake, enrichment, and export layers.",
        "This surface keeps the connector story grounded: what is being called, how it is authenticated, and where the evidence packages are allowed to land.",
        "integrations",
        body,
    )


def render_security_architecture() -> str:
    architecture = SERVICE.security_architecture()
    nodes = architecture["nodes"]
    body = f"""
    <section class="grid-2plus">
      <div class="panel">
        <span class="eyebrow">System architecture diagram</span>
        <h2>Bridge the incident system, the vault, and the evidence archive.</h2>
        <div class="topology-grid">
          <article class="topology-card">
            <span class="eyebrow">{escape(nodes[0]["type"])}</span>
            <h4>{escape(nodes[0]["name"])}</h4>
            <p>{escape(nodes[0]["summary"])}</p>
          </article>
          <div class="topology-core">
            <div class="core-orbit">
              <div class="core-icon">▣</div>
              <h4>{escape(nodes[1]["name"])}</h4>
              <p>{escape(nodes[1]["summary"])}</p>
              <div class="core-dots"><i></i><i></i><i></i></div>
            </div>
          </div>
          <article class="topology-card target">
            <span class="eyebrow">{escape(nodes[2]["type"])}</span>
            <h4>{escape(nodes[2]["name"])}</h4>
            <p>{escape(nodes[2]["summary"])}</p>
          </article>
        </div>
        <div class="mini-panel" style="margin-top:18px;">
          <h3>{escape(nodes[3]["name"])}</h3>
          <p>{escape(nodes[3]["summary"])}</p>
        </div>
      </div>
      <div class="grid-3" style="grid-template-columns: 1fr; margin-top:0;">
        <div class="panel">
          <span class="eyebrow">Credential mgmt</span>
          <h2>Secret handling posture</h2>
          {''.join(f'<div class="mini-panel" style="margin-top:14px;"><h3>{escape(item["title"])}</h3><p>{escape(item["detail"])}</p></div>' for item in architecture["credentials"])}
        </div>
        <div class="panel" style="background: linear-gradient(180deg, #f7fcfb, #f9fffd);">
          <span class="eyebrow">Transit security</span>
          <h2>Transport safeguards</h2>
          <div class="panel" style="padding:0; border:none; box-shadow:none; background:transparent;">
            {"".join(f'<div class="mini-panel" style="margin-top:12px;"><p>{escape(item)}</p></div>' for item in architecture["transitControls"])}
          </div>
        </div>
        <div class="distribution-card">
          <span class="eyebrow">Access control</span>
          {"".join(f'<div class="dist-row"><div class="dist-top"><strong>{escape(role["name"])}</strong></div><p style="margin:8px 0 0;color:#b7c5dc;line-height:1.6;">{escape(role["detail"])}</p></div>' for role in architecture["accessRoles"])}
        </div>
      </div>
    </section>
    """
    return _shell(
        "Security and architecture posture for the evidence bridge.",
        "This view makes the bridge legible to security reviewers: credential handling, transit safeguards, access roles, and the systems carrying the audit narrative.",
        "architecture",
        body,
    )


def render_monitor() -> str:
    monitor = SERVICE.health_monitor()
    cards = "".join(_component_card(component) for component in monitor["components"])
    body = f"""
    <section class="grid-2plus">
      <div class="panel">
        <span class="eyebrow">System health monitor</span>
        <h2>Real-time infrastructure telemetry for the evidence bridge.</h2>
        <div class="component-grid" style="grid-template-columns: repeat(2, minmax(0, 1fr));">{cards}</div>
      </div>
      <div class="distribution-card">
        <span class="eyebrow">Aggregate resource pool</span>
        <div class="dist-row">
          <div class="dist-top"><strong>Avg CPU</strong><span>{monitor["totals"]["avgCpu"]}%</span></div>
          <div class="progress-track dark"><div class="progress-fill violet" style="width:{round(monitor["totals"]["avgCpu"])}%"></div></div>
        </div>
        <div class="dist-row">
          <div class="dist-top"><strong>Avg memory</strong><span>{monitor["totals"]["avgMemGb"]}GB</span></div>
          <div class="progress-track dark"><div class="progress-fill hot" style="width:62%"></div></div>
        </div>
        <div class="dist-row">
          <div class="dist-top"><strong>Total net I/O</strong><span>{monitor["totals"]["totalNetIoMb"]} MB/s</span></div>
          <div class="progress-track dark"><div class="progress-fill good" style="width:74%"></div></div>
        </div>
        <div class="dist-foot"><span>Cluster status</span><strong>{monitor["totals"]["clusterNodes"]} nodes OK</strong></div>
      </div>
    </section>
    """
    return _shell(
        "Monitor the bridge infrastructure, not just the ticket queue.",
        "The control plane should surface resource posture, API latency, and component load before evidence quality starts to slide.",
        "monitor",
        body,
    )


def render_methodology() -> str:
    body = """
    <section class="grid-3">
      <div class="panel">
        <span class="eyebrow">Scoring inputs</span>
        <h2>Risk is driven by evidence age, approvals, owners, and exception pressure.</h2>
        <p>The service scores each incident across priority, evidence freshness, artifact depth, manager verification, dual-approval expectations, exception count, and owner quality.</p>
      </div>
      <div class="panel">
        <span class="eyebrow">Bundle logic</span>
        <h2>A record is only review-ready when the packet is defensible.</h2>
        <p>Bundle-ready status requires enough attached artifacts, ticket linkage, manager verification, and a fresh evidence window.</p>
      </div>
      <div class="panel">
        <span class="eyebrow">Operator intent</span>
        <h2>The lane is built for governance teams, not vanity dashboards.</h2>
        <p>The UI exists to tell operators what is fragile, what is aging, and what can close safely into a certification or audit cycle.</p>
      </div>
    </section>
    """
    return _shell(
        "How the evidence bridge decides what is safe, stale, or escalation-worthy.",
        "The methodology is deliberately simple and auditable so operators can explain why a packet was promoted, paused, or forced back into evidence refresh.",
        "methodology",
        body,
    )


def render_docs() -> str:
    routes = [
        ("/", "Dashboard overview and traffic posture"),
        ("/pipeline-board", "Incident review queue with evidence pressure"),
        ("/bundles", "Evidence packet output and downstream targets"),
        ("/monitor", "Infrastructure telemetry and component health"),
        ("/security-architecture", "Security review surface for the bridge"),
        ("/audit-log", "Replayable forensic trail and terminal output"),
        ("/api/dashboard/summary", "Top-line metrics for embeddings or widgets"),
        ("/api/incidents", "Modeled incident catalog"),
        ("/api/bundles", "Evidence packet summaries"),
        ("/api/health", "Monitor telemetry snapshot"),
        ("/api/security-architecture", "Security posture model"),
        ("/api/terminal", "Terminal-style operator feed"),
    ]
    rows = "".join(
        f'<tr><td><strong>{escape(path)}</strong></td><td>{escape(desc)}</td></tr>'
        for path, desc in routes
    )
    body = f"""
    <section class="table-card">
      <table>
        <thead>
          <tr><th>Route</th><th>Purpose</th></tr>
        </thead>
        <tbody>{rows}</tbody>
      </table>
    </section>
    """
    return _shell(
        "Route surface for the evidence bridge.",
        "The HTML routes are meant for proof and operator review; the JSON routes are there so the same posture can feed other systems or dashboards.",
        "docs",
        body,
    )
