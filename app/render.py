from __future__ import annotations

import json
from html import escape

from app.services.evidence_pipeline_service import build_service


SERVICE = build_service()


def _summary() -> dict:
    return SERVICE.summary()


def _verdict_class(verdict: str) -> str:
    return {"healthy": "healthy", "watch": "watch", "critical": "critical"}[verdict]


def _mini_chart() -> str:
    series = SERVICE.sync_velocity()
    max_bundles = max(item["bundles"] for item in series)
    bars = []
    for item in series:
        height = max(20, round((item["bundles"] / max_bundles) * 108))
        bars.append(
            f"""
            <div class="chart-col">
              <div class="chart-bar-wrap">
                <div class="chart-bar" style="height:{height}px"></div>
              </div>
              <div class="chart-num">{item["bundles"]}</div>
              <div class="chart-label">{escape(item["day"])}</div>
            </div>
            """
        )
    summary = _summary()
    return f"""
      <div class="mini-chart">
        <div class="chart-head">
          <div>
            <div class="micro-label">Bundle velocity</div>
            <h3>How much evidence packaging work the lane is carrying this week.</h3>
          </div>
          <div class="chart-legend">
            <span><i></i> Evidence bundles prepared</span>
          </div>
        </div>
        <div class="chart-grid">{"".join(bars)}</div>
        <div class="chart-foot">
          <span><strong>Average evidence age:</strong> {summary["averageEvidenceAge"]} days</span>
          <span><strong>Queue pressure:</strong> {summary["urgentCount"]} urgent / {summary["watchCount"]} watch</span>
        </div>
      </div>
    """


def _shell(title: str, subtitle: str, current: str, body: str) -> str:
    summary = _summary()
    nav_items = [
        ("/", "Overview", "overview"),
        ("/pipeline-board", "Pipeline Board", "pipeline"),
        ("/bundles", "Bundles", "bundles"),
        ("/audit-log", "Audit Log", "audit"),
        ("/integrations", "Integrations", "integrations"),
        ("/methodology", "Methodology", "methodology"),
        ("/docs", "Docs", "docs"),
    ]
    sidebar = "".join(
        f"""<a class="side-link {'active' if key == current else ''}" href="{href}">{escape(label)}</a>"""
        for href, label, key in nav_items
    )
    tabs = "".join(
        f"""<a class="tab-pill {'active' if key == current else ''}" href="{href}">{escape(label)}</a>"""
        for href, label, key in nav_items
    )
    return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{escape(title)}</title>
    <style>
      :root {{
        color-scheme: dark;
        --bg: #04070d;
        --panel: rgba(9, 16, 28, 0.92);
        --line: rgba(255,255,255,0.07);
        --text: #f5f7fd;
        --muted: #96a9c6;
        --soft: #6d809b;
        --blue: #74c8ff;
        --indigo: #5d78ff;
        --green: #49d79e;
        --amber: #f6c46a;
        --red: #ff7987;
      }}
      * {{ box-sizing: border-box; }}
      body {{
        margin: 0;
        font-family: Inter, "Segoe UI", system-ui, sans-serif;
        color: var(--text);
        background:
          radial-gradient(circle at top left, rgba(116,200,255,0.14), transparent 24%),
          radial-gradient(circle at top right, rgba(255,121,135,0.08), transparent 16%),
          linear-gradient(180deg, #02050a 0%, #050912 100%);
      }}
      a {{ color: inherit; text-decoration: none; }}
      .shell {{ min-height: 100vh; display: grid; grid-template-columns: 248px minmax(0,1fr); }}
      .sidebar {{
        background: rgba(0,0,0,0.3);
        border-right: 1px solid rgba(255,255,255,0.06);
        backdrop-filter: blur(16px);
        padding: 24px 18px;
        display: flex;
        flex-direction: column;
      }}
      .brand {{
        display: flex; align-items: center; gap: 12px; padding: 8px 10px 18px;
        border-bottom: 1px solid rgba(255,255,255,0.06);
      }}
      .brand-mark {{
        width: 40px; height: 40px; border-radius: 12px; display:grid; place-items:center;
        background: linear-gradient(135deg, #0c97c2, #5d78ff); color:white; font-weight:900;
        box-shadow: 0 0 18px rgba(93,120,255,0.28);
      }}
      .brand strong {{ display:block; font-size:14px; }}
      .brand span {{ display:block; margin-top:4px; color:var(--blue); font-size:10px; letter-spacing:.18em; text-transform:uppercase; }}
      nav {{ margin-top: 18px; }}
      .side-link {{
        display:block; padding:13px 14px; border-radius:14px; color:#8195b4; font-size:12px;
        font-weight:700; text-transform:uppercase; letter-spacing:.12em; transition:all 150ms ease;
      }}
      .side-link.active {{ color:var(--blue); background:rgba(116,200,255,0.08); border:1px solid rgba(116,200,255,0.16); }}
      .side-link:hover {{ color:var(--text); background:rgba(255,255,255,0.04); }}
      .meta {{ margin-top:auto; padding:16px 12px 8px; border-top:1px solid rgba(255,255,255,0.06); }}
      .meta dt {{ color:#687c98; font-size:10px; text-transform:uppercase; letter-spacing:.14em; margin-bottom:4px; }}
      .meta dd {{ margin:0 0 14px; font-size:12px; font-weight:700; line-height:1.45; }}
      .topbar {{
        height:72px; position:sticky; top:0; z-index:2; display:flex; align-items:center; justify-content:space-between;
        padding:0 34px; background:rgba(0,0,0,0.34); border-bottom:1px solid rgba(255,255,255,0.06); backdrop-filter: blur(16px);
      }}
      .status-chip {{
        display:inline-flex; align-items:center; gap:10px; padding:9px 14px; border-radius:999px;
        border:1px solid rgba(116,200,255,0.14); background:rgba(116,200,255,0.05); color:#b9e1ff;
        font-size:10px; font-weight:800; text-transform:uppercase; letter-spacing:.18em;
      }}
      .status-dot {{ width:8px; height:8px; border-radius:50%; background:var(--blue); box-shadow:0 0 12px rgba(116,200,255,0.84); }}
      .topbar-right {{ display:flex; align-items:center; gap:22px; }}
      .meta-block {{ display:flex; flex-direction:column; align-items:flex-end; }}
      .meta-block span {{ color:#6d809b; font-size:9px; text-transform:uppercase; letter-spacing:.15em; }}
      .meta-block strong {{ margin-top:4px; font-size:11px; text-transform:uppercase; letter-spacing:.12em; }}
      .action-pill {{
        display:inline-flex; align-items:center; padding:12px 16px; border-radius:999px; color:white;
        background:linear-gradient(135deg, #0f8fbf, #5d78ff); box-shadow:0 0 20px rgba(93,120,255,0.24);
        font-size:10px; font-weight:900; letter-spacing:.18em; text-transform:uppercase;
      }}
      .wrap {{ max-width: 1280px; margin:0 auto; padding:34px; }}
      .hero {{
        border:1px solid var(--line); border-radius:28px; padding:28px;
        background: linear-gradient(180deg, rgba(9,16,28,0.96), rgba(6,11,20,0.94));
        box-shadow: 0 26px 60px rgba(0,0,0,0.34);
      }}
      .hero-eyebrow {{ margin-bottom:18px; color:var(--blue); font-size:11px; letter-spacing:.28em; text-transform:uppercase; font-weight:800; }}
      h1 {{ margin:0; font-size:clamp(38px,5vw,70px); line-height:.92; font-family:Georgia, "Times New Roman", serif; letter-spacing:-.04em; }}
      .hero-subtitle {{ margin-top:14px; max-width:860px; color:var(--muted); font-size:19px; line-height:1.55; }}
      .hero-strip {{ display:flex; flex-wrap:wrap; gap:14px; margin-top:24px; }}
      .hero-kpi {{ min-width:180px; padding:14px 16px; border-radius:18px; border:1px solid rgba(255,255,255,0.06); background:rgba(255,255,255,0.03); }}
      .hero-kpi .k {{ color:#6f83a0; font-size:10px; text-transform:uppercase; letter-spacing:.14em; font-weight:800; }}
      .hero-kpi .v {{ margin-top:6px; font-size:28px; font-weight:800; }}
      .hero-callout {{
        margin-top:18px; padding:18px 20px; border-radius:18px; border:1px solid rgba(255,255,255,0.06); background:rgba(2,8,17,0.62);
      }}
      .hero-callout strong {{ display:block; color:var(--amber); font-size:10px; text-transform:uppercase; letter-spacing:.18em; margin-bottom:8px; }}
      .hero-callout p {{ margin:0; color:#dce7fb; font-size:17px; line-height:1.5; }}
      .tab-row {{ display:flex; gap:10px; flex-wrap:wrap; margin-top:20px; }}
      .tab-pill {{
        display:inline-flex; align-items:center; padding:10px 14px; border-radius:999px; border:1px solid rgba(255,255,255,0.08);
        background:rgba(255,255,255,0.03); color:#afc0d8; font-size:11px; font-weight:800; text-transform:uppercase; letter-spacing:.12em;
      }}
      .tab-pill.active {{ color:var(--amber); border-color:rgba(246,196,106,0.18); background:rgba(246,196,106,0.08); }}
      .page-section {{ margin-top:24px; border-radius:26px; border:1px solid var(--line); background:var(--panel); overflow:hidden; box-shadow:0 24px 54px rgba(0,0,0,0.24); }}
      .section-head {{ padding:20px 24px 14px; border-bottom:1px solid rgba(255,255,255,0.05); }}
      .section-head strong {{ display:block; color:var(--blue); font-size:10px; text-transform:uppercase; letter-spacing:.2em; margin-bottom:10px; }}
      .section-head h2 {{ margin:0; font-family:Georgia, "Times New Roman", serif; font-size:24px; letter-spacing:-.03em; }}
      .section-head p {{ margin:10px 0 0; color:var(--muted); font-size:15px; line-height:1.55; }}
      .section-body {{ padding:24px; }}
      .stats-grid {{ display:grid; gap:18px; grid-template-columns:repeat(4,minmax(0,1fr)); }}
      .stat-card {{ border-radius:20px; padding:18px 18px 20px; border:1px solid rgba(255,255,255,0.06); background:linear-gradient(180deg, rgba(255,255,255,0.04), rgba(0,0,0,0.08)); }}
      .stat-card .label {{ color:#71839d; font-size:10px; text-transform:uppercase; letter-spacing:.16em; font-weight:800; }}
      .stat-card .value {{ margin-top:10px; font-size:36px; font-weight:900; }}
      .stat-card .sub {{ margin-top:10px; color:var(--muted); font-size:14px; line-height:1.45; }}
      .insight-grid {{ display:grid; gap:18px; grid-template-columns:1.35fr 1fr; }}
      .three-col {{ display:grid; gap:18px; grid-template-columns:repeat(3,minmax(0,1fr)); }}
      .two-col {{ display:grid; gap:18px; grid-template-columns:1fr 1fr; }}
      .panel {{ border-radius:22px; border:1px solid rgba(255,255,255,0.06); background:rgba(4,9,18,0.55); padding:22px; }}
      .panel h3 {{ margin:0 0 16px; font-size:18px; }}
      .panel-grid {{ display:grid; gap:14px; }}
      .metric-card {{ padding:16px; border:1px solid rgba(255,255,255,0.05); border-radius:18px; background:rgba(255,255,255,0.028); }}
      .metric-card .micro, .micro-label {{ color:#6f83a0; font-size:9px; text-transform:uppercase; letter-spacing:.16em; font-weight:800; }}
      .metric-card .title {{ margin-top:8px; font-size:15px; font-weight:800; }}
      .metric-card .desc {{ margin-top:8px; color:var(--muted); font-size:13px; line-height:1.5; }}
      .incident-grid {{ display:grid; gap:16px; }}
      .incident-card {{ border-radius:22px; border:1px solid rgba(255,255,255,0.06); background:rgba(4,9,18,0.6); overflow:hidden; }}
      .incident-top {{ display:grid; grid-template-columns:minmax(0,1fr) auto auto; gap:18px; align-items:center; padding:20px 22px; }}
      .incident-card h3 {{ margin:0; font-size:22px; font-weight:800; letter-spacing:-.03em; }}
      .incident-card .meta-text {{ margin-top:8px; color:var(--muted); font-size:13px; }}
      .tag {{ display:inline-flex; align-items:center; justify-content:center; padding:8px 12px; border-radius:999px; font-size:10px; font-weight:900; letter-spacing:.16em; text-transform:uppercase; }}
      .healthy {{ color:var(--green); background:rgba(73,215,158,0.12); border:1px solid rgba(73,215,158,0.14); }}
      .watch {{ color:var(--amber); background:rgba(246,196,106,0.12); border:1px solid rgba(246,196,106,0.14); }}
      .critical {{ color:var(--red); background:rgba(255,121,135,0.12); border:1px solid rgba(255,121,135,0.14); }}
      .score-stack {{ text-align:right; }}
      .score-stack .micro {{ color:#6f83a0; font-size:9px; text-transform:uppercase; letter-spacing:.16em; font-weight:800; }}
      .score-stack .value {{ margin-top:6px; font-size:28px; font-weight:900; }}
      .incident-bottom {{ padding:18px 22px 22px; border-top:1px solid rgba(255,255,255,0.05); background:rgba(255,255,255,0.02); }}
      .signal-pill {{
        display:inline-flex; align-items:center; padding:8px 10px; border-radius:999px; background:rgba(116,200,255,0.09); color:var(--blue); font-size:10px; font-weight:800; letter-spacing:.12em; text-transform:uppercase;
      }}
      .pill-stack {{ display:flex; flex-wrap:wrap; gap:10px; }}
      .meter-row + .meter-row {{ margin-top:14px; }}
      .meter-head {{ display:flex; justify-content:space-between; gap:16px; margin-bottom:8px; color:#cfe0f7; font-size:12px; font-weight:700; }}
      .meter-track {{ height:10px; border-radius:999px; background:rgba(255,255,255,0.05); overflow:hidden; }}
      .meter-fill {{ height:100%; border-radius:999px; }}
      .meter-fill.good {{ background:linear-gradient(90deg, #1e7fc7, #49d79e); }}
      .meter-fill.watch {{ background:linear-gradient(90deg, #2f82ff, #f6c46a); }}
      .meter-fill.hot {{ background:linear-gradient(90deg, #d14d6c, #ff7987); }}
      .mini-chart {{ border-radius:22px; border:1px solid rgba(255,255,255,0.06); background:rgba(4,9,18,0.55); padding:22px; }}
      .chart-head {{ display:flex; justify-content:space-between; gap:18px; align-items:flex-end; margin-bottom:16px; }}
      .chart-head h3 {{ margin:10px 0 0; font-size:17px; max-width:420px; line-height:1.35; }}
      .chart-legend span {{ display:inline-flex; align-items:center; gap:8px; color:var(--muted); font-size:11px; }}
      .chart-legend i {{ display:inline-block; width:12px; height:12px; border-radius:4px; background:linear-gradient(180deg, var(--blue), var(--indigo)); }}
      .chart-grid {{ display:flex; align-items:flex-end; justify-content:space-between; gap:12px; min-height:170px; margin-top:24px; }}
      .chart-col {{ flex:1; text-align:center; }}
      .chart-bar-wrap {{ display:flex; align-items:flex-end; justify-content:center; height:124px; }}
      .chart-bar {{ width:70px; max-width:100%; border-radius:16px 16px 8px 8px; background:linear-gradient(180deg, var(--blue), var(--indigo)); box-shadow:0 0 24px rgba(93,120,255,0.2); }}
      .chart-num {{ margin-top:12px; color:#f6f8fe; font-size:14px; font-weight:800; }}
      .chart-label {{ margin-top:6px; color:#96a9c6; font-size:10px; letter-spacing:.16em; text-transform:uppercase; }}
      .chart-foot {{ display:flex; justify-content:space-between; gap:12px; margin-top:18px; color:var(--muted); font-size:12px; }}
      .table-shell {{ overflow:hidden; border-radius:22px; border:1px solid rgba(255,255,255,0.06); background:rgba(4,9,18,0.58); }}
      table {{ width:100%; border-collapse:collapse; }}
      th, td {{ padding:16px 18px; text-align:left; vertical-align:top; }}
      thead th {{ color:#7385a0; font-size:10px; text-transform:uppercase; letter-spacing:.18em; font-weight:900; background:rgba(255,255,255,0.035); }}
      tbody tr + tr td {{ border-top:1px solid rgba(255,255,255,0.05); }}
      tbody tr:hover td {{ background:rgba(116,200,255,0.03); }}
      .subtext {{ margin-top:6px; color:var(--muted); font-size:12px; line-height:1.45; }}
      .log-shell {{ border-radius:22px; border:1px solid rgba(255,255,255,0.08); background:rgba(2,6,12,0.88); overflow:hidden; }}
      .log-head {{ padding:16px 18px; display:flex; align-items:center; gap:12px; border-bottom:1px solid rgba(255,255,255,0.08); background:rgba(255,255,255,0.03); }}
      .log-lights {{ display:flex; gap:8px; }}
      .log-lights i {{ width:11px; height:11px; border-radius:50%; display:block; }}
      .log-lights i:nth-child(1) {{ background:rgba(255,121,135,0.55); }}
      .log-lights i:nth-child(2) {{ background:rgba(246,196,106,0.55); }}
      .log-lights i:nth-child(3) {{ background:rgba(73,215,158,0.55); }}
      .log-head strong {{ color:var(--blue); font-size:10px; letter-spacing:.18em; text-transform:uppercase; }}
      .log-body {{ padding:18px 18px 8px; }}
      .log-line {{ display:grid; grid-template-columns:170px 180px minmax(0,1fr) 90px; gap:14px; align-items:start; padding:10px 12px; border-radius:14px; }}
      .log-line + .log-line {{ margin-top:8px; }}
      .log-line:hover {{ background:rgba(255,255,255,0.03); }}
      .log-time {{ color:#6f83a0; font-size:11px; font-family:"Cascadia Code", Consolas, monospace; }}
      .log-action {{ color:var(--blue); font-size:11px; font-family:"Cascadia Code", Consolas, monospace; font-weight:800; letter-spacing:.08em; }}
      .log-resource strong {{ display:block; font-size:12px; }}
      .log-resource span {{ display:block; margin-top:4px; color:var(--muted); font-size:12px; line-height:1.45; }}
      .result-good {{ color:var(--green); }}
      .result-bad {{ color:var(--red); }}
      .config-grid {{ display:grid; gap:18px; grid-template-columns:repeat(2,minmax(0,1fr)); }}
      .config-row {{ display:flex; align-items:flex-start; justify-content:space-between; gap:18px; padding:14px 16px; border-radius:16px; border:1px solid rgba(255,255,255,0.05); background:rgba(255,255,255,0.02); }}
      .config-row strong {{ display:block; font-size:13px; }}
      .config-row span {{ display:block; margin-top:6px; color:var(--muted); font-size:12px; }}
      .toggle {{ min-width:78px; text-align:center; padding:8px 12px; border-radius:999px; font-size:10px; font-weight:900; letter-spacing:.16em; text-transform:uppercase; }}
      .toggle.good {{ background:rgba(73,215,158,0.12); color:var(--green); border:1px solid rgba(73,215,158,0.18); }}
      .toggle.bad {{ background:rgba(255,121,135,0.12); color:var(--red); border:1px solid rgba(255,121,135,0.18); }}
      .integration-row {{ display:flex; align-items:center; justify-content:space-between; gap:14px; padding:14px 16px; border-radius:16px; border:1px solid rgba(255,255,255,0.05); background:rgba(255,255,255,0.02); }}
      .integration-row strong {{ display:block; font-size:13px; }}
      .integration-row span {{ display:block; margin-top:6px; color:var(--muted); font-size:12px; }}
      .code-panel {{ border-radius:22px; border:1px solid rgba(255,255,255,0.08); background:rgba(2,6,12,0.92); padding:18px 20px 20px; }}
      .code-head {{ display:flex; align-items:center; justify-content:space-between; padding-bottom:12px; margin-bottom:16px; border-bottom:1px solid rgba(255,255,255,0.08); }}
      .code-head span {{ color:var(--blue); font-size:10px; font-weight:800; text-transform:uppercase; letter-spacing:.18em; }}
      .lights {{ display:flex; gap:7px; }}
      .lights i {{ display:block; width:9px; height:9px; border-radius:50%; }}
      .lights i:nth-child(1) {{ background:rgba(255,121,135,0.7); }}
      .lights i:nth-child(2) {{ background:rgba(246,196,106,0.7); }}
      .lights i:nth-child(3) {{ background:rgba(73,215,158,0.7); }}
      pre {{ margin:0; white-space:pre-wrap; overflow:auto; color:#dce8fb; font-size:13px; line-height:1.6; font-family:"Cascadia Code", Consolas, monospace; }}
      @media (max-width: 1100px) {{
        .shell {{ grid-template-columns:1fr; }}
        .sidebar {{ display:none; }}
        .topbar {{ height:auto; padding:18px 20px; flex-direction:column; align-items:flex-start; gap:14px; }}
        .stats-grid, .insight-grid, .three-col, .two-col, .config-grid {{ grid-template-columns:1fr; }}
        .chart-foot {{ flex-direction:column; }}
        .incident-top {{ grid-template-columns:1fr; }}
        .log-line {{ grid-template-columns:1fr; }}
      }}
    </style>
  </head>
  <body>
    <div class="shell">
      <aside class="sidebar">
        <div class="brand">
          <div class="brand-mark">SE</div>
          <div>
            <strong>ServiceNow CyberArk Evidence Pipeline</strong>
            <span>instance: evidence-bus</span>
          </div>
        </div>
        <nav>{sidebar}</nav>
        <dl class="meta">
          <dt>Urgent incidents</dt>
          <dd>{summary["urgentCount"]} incidents</dd>
          <dt>Bundle-ready</dt>
          <dd>{summary["bundleReadyCount"]} records</dd>
          <dt>Lead incident</dt>
          <dd>{escape(summary["highestRiskIncident"])}</dd>
        </dl>
      </aside>
      <main>
        <header class="topbar">
          <div class="status-chip"><span class="status-dot"></span>Evidence pipeline live</div>
          <div class="topbar-right">
            <div class="meta-block"><span>Average evidence age</span><strong>{summary["averageEvidenceAge"]} days</strong></div>
            <div class="meta-block"><span>Exceptions</span><strong>{summary["exceptionCount"]} active</strong></div>
            <a class="action-pill" href="/docs">Open API docs</a>
          </div>
        </header>
        <div class="wrap">
          <section class="hero">
            <div class="hero-eyebrow">ServiceNow CyberArk Evidence Pipeline</div>
            <h1>{escape(title)}</h1>
            <p class="hero-subtitle">{escape(subtitle)}</p>
            <div class="hero-strip">
              <div class="hero-kpi"><div class="k">Incidents</div><div class="v">{summary["incidentCount"]}</div></div>
              <div class="hero-kpi"><div class="k">Urgent lanes</div><div class="v">{summary["urgentCount"]}</div></div>
              <div class="hero-kpi"><div class="k">Bundle-ready</div><div class="v">{summary["bundleReadyCount"]}</div></div>
              <div class="hero-kpi"><div class="k">Assignment groups</div><div class="v">{summary["assignmentGroupCount"]}</div></div>
            </div>
            <div class="hero-callout">
              <strong>Lead recommendation</strong>
              <p>{escape(summary["leadRecommendation"])}</p>
            </div>
            <div class="tab-row">{tabs}</div>
          </section>
          {body}
        </div>
      </main>
    </div>
  </body>
</html>"""


def _incident_card(incident: dict) -> str:
    flags = []
    if incident["staleEvidence"]:
        flags.append('<span class="signal-pill">Stale evidence</span>')
    if incident["ownerGap"]:
        flags.append('<span class="signal-pill">Owner gap</span>')
    if not incident["bundleReady"]:
        flags.append('<span class="signal-pill">Bundle incomplete</span>')
    if incident["exceptionCount"] > 0:
        flags.append(f'<span class="signal-pill">{incident["exceptionCount"]} exceptions</span>')
    return f"""
      <div class="incident-card">
        <div class="incident-top">
          <div>
            <h3>{escape(incident["incidentId"])}</h3>
            <div class="meta-text">{escape(incident["accountName"])} · {escape(incident["assignmentGroup"])} · {escape(incident["servicenowState"])}</div>
          </div>
          <span class="tag {_verdict_class(incident["verdict"])}">{escape(incident["verdict"])}</span>
          <div class="score-stack">
            <div class="micro">Risk score</div>
            <div class="value">{incident["riskScore"]}</div>
          </div>
        </div>
        <div class="incident-bottom">
          <div class="two-col">
            <div>
              <div class="meter-row">
                <div class="meter-head"><span>Evidence age</span><span>{incident["evidenceAgeDays"]}d</span></div>
                <div class="meter-track"><div class="meter-fill {'hot' if incident['evidenceAgeDays'] == 0 or incident['evidenceAgeDays'] > 90 else 'watch' if incident['evidenceAgeDays'] > 45 else 'good'}" style="width:{min(100, max(10, incident['evidenceAgeDays']))}%"></div></div>
              </div>
              <div class="meter-row">
                <div class="meter-head"><span>Approval artifacts</span><span>{incident["approvalArtifacts"]}</span></div>
                <div class="meter-track"><div class="meter-fill {'good' if incident['approvalArtifacts'] >= 3 else 'watch' if incident['approvalArtifacts'] >= 1 else 'hot'}" style="width:{min(100, incident['approvalArtifacts'] * 25)}%"></div></div>
              </div>
              <div class="meter-row">
                <div class="meter-head"><span>Last activity</span><span>{incident["lastActivityHours"]}h</span></div>
                <div class="meter-track"><div class="meter-fill {'good' if incident['lastActivityHours'] < 24 else 'watch' if incident['lastActivityHours'] < 48 else 'hot'}" style="width:{min(100, incident['lastActivityHours'])}%"></div></div>
              </div>
            </div>
            <div class="panel-grid">
              <div class="metric-card">
                <div class="micro">Top concern</div>
                <div class="title">{escape(incident["topConcern"])}</div>
                <div class="desc">{escape(incident["nextAction"])}</div>
              </div>
              <div class="pill-stack">{"".join(flags) or '<span class="signal-pill">Ready</span>'}</div>
            </div>
          </div>
        </div>
      </div>
    """


def render_overview() -> str:
    summary = _summary()
    catalog = SERVICE.incident_catalog()
    body = f"""
      <section class="page-section">
        <div class="section-head">
          <strong>Pipeline summary</strong>
          <h2>Incident evidence only helps if it closes the gap between ServiceNow workflow and CyberArk truth.</h2>
          <p>This pipeline treats incident closure, privileged review, and audit evidence as one lane. The point is to turn ticket state plus vault metadata into review-safe bundles before they harden into bad closure decisions.</p>
        </div>
        <div class="section-body">
          <div class="stats-grid">
            <div class="stat-card"><div class="label">Urgent incidents</div><div class="value">{summary["urgentCount"]}</div><div class="sub">Packets that should be forced through evidence refresh before closure.</div></div>
            <div class="stat-card"><div class="label">Watch lanes</div><div class="value">{summary["watchCount"]}</div><div class="sub">Incidents carrying enough evidence weakness to deserve review pressure soon.</div></div>
            <div class="stat-card"><div class="label">Stale evidence</div><div class="value">{summary["staleEvidenceCount"]}</div><div class="sub">Incidents whose evidence posture is too old or too thin to trust quietly.</div></div>
            <div class="stat-card"><div class="label">Exceptions</div><div class="value">{summary["exceptionCount"]}</div><div class="sub">Open exception pressure still sitting inside the packaging lane.</div></div>
          </div>
          <div class="insight-grid" style="margin-top:20px;">
            {_mini_chart()}
            <div class="panel">
              <h3>Why this pipeline exists</h3>
              <div class="panel-grid">
                <div class="metric-card">
                  <div class="micro">ServiceNow side</div>
                  <div class="title">Ticket state is not enough by itself.</div>
                  <div class="desc">An incident can look active and still be missing the approval chain that makes it defensible later.</div>
                </div>
                <div class="metric-card">
                  <div class="micro">CyberArk side</div>
                  <div class="title">Vault metadata should become evidence, not just context.</div>
                  <div class="desc">Safe ownership, dual approval, and target-system details all need to survive into the review packet.</div>
                </div>
                <div class="metric-card">
                  <div class="micro">Pipeline objective</div>
                  <div class="title">Turn incident handling into audit-ready records.</div>
                  <div class="desc">This repo is strongest when a reviewer can tell what happened, why it is risky, and what packet should move next.</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
      <section class="page-section">
        <div class="section-head">
          <strong>Pipeline board</strong>
          <h2>The incidents most likely to need evidence intervention first.</h2>
          <p>Every incident card combines ServiceNow state, CyberArk posture, evidence age, and owner quality so the riskiest packets stay visible.</p>
        </div>
        <div class="section-body">
          <div class="incident-grid">{"".join(_incident_card(item) for item in catalog[:3])}</div>
        </div>
      </section>
    """
    return _shell(
        "Control-plane summary for privileged-review evidence flow.",
        "Incident count, urgent lanes, bundle velocity, and operator recommendations at a glance.",
        "overview",
        body,
    )


def render_pipeline_board() -> str:
    queue = SERVICE.pipeline_board()
    body = f"""
      <section class="page-section">
        <div class="section-head">
          <strong>Pipeline board</strong>
          <h2>The incidents most likely to need containment or evidence intervention first.</h2>
          <p>This is the practical operator surface for deciding which ServiceNow records and CyberArk packets need manual attention before closure or certification moves ahead.</p>
        </div>
        <div class="section-body">
          <div class="incident-grid">{"".join(_incident_card(item) for item in queue)}</div>
        </div>
      </section>
    """
    return _shell(
        "Review queue for incident evidence pressure.",
        "The incidents most likely to need evidence refresh or privileged-review escalation first.",
        "pipeline",
        body,
    )


def render_bundles() -> str:
    bundles = SERVICE.evidence_bundles()
    rows = "".join(
        f"""
        <tr>
          <td><strong>{escape(item["incidentId"])}</strong><div class="subtext">{escape(item["accountName"])} · {escape(item["assignmentGroup"])}</div></td>
          <td>{escape(item["targetSystem"])}</td>
          <td>{escape(item["verdict"])}</td>
          <td>{"Yes" if item["bundleReady"] else "No"}</td>
          <td>{escape(", ".join(item["requiredEvidence"]))}</td>
        </tr>
        """
        for item in bundles
    )
    payload = json.dumps(bundles[0], indent=2)
    body = f"""
      <section class="page-section">
        <div class="section-head">
          <strong>Evidence bundles</strong>
          <h2>Every incident becomes a reusable packet, not just a ticket comment.</h2>
          <p>Bundle output preserves the governance targets, required evidence, and verdict so the record can move into audit and certification workflows cleanly.</p>
        </div>
        <div class="section-body">
          <div class="insight-grid">
            <div class="table-shell">
              <table>
                <thead>
                  <tr>
                    <th>Incident</th>
                    <th>Target system</th>
                    <th>Verdict</th>
                    <th>Bundle ready</th>
                    <th>Required evidence</th>
                  </tr>
                </thead>
                <tbody>{rows}</tbody>
              </table>
            </div>
            <div class="code-panel">
              <div class="code-head"><span>sample bundle</span><div class="lights"><i></i><i></i><i></i></div></div>
              <pre><code>{escape(payload)}</code></pre>
            </div>
          </div>
        </div>
      </section>
    """
    return _shell(
        "Evidence bundles for incident closure and audit workflows.",
        "A packaging surface for turning ServiceNow and CyberArk context into review-safe records.",
        "bundles",
        body,
    )


def render_audit_log() -> str:
    logs = SERVICE.audit_log()
    rows = []
    for item in logs:
        result_class = "result-good" if item["result"] == "Success" else "result-bad"
        rows.append(
            f"""
            <div class="log-line">
              <div class="log-time">{escape(item["timestamp"])}</div>
              <div class="log-action">{escape(item["action"])}</div>
              <div class="log-resource"><strong>{escape(item["resource"])}</strong><span>{escape(item["detail"])}</span></div>
              <div class="{result_class}">{escape(item["result"])}</div>
            </div>
            """
        )
    body = f"""
      <section class="page-section">
        <div class="section-head">
          <strong>Audit evidence</strong>
          <h2>A replayable log of incident pulls, vault enrichment, and bundle failures.</h2>
          <p>The useful part is not just that the pipeline emits events. It is that a reviewer can reconstruct what moved, what failed, and which lane stayed unresolved.</p>
        </div>
        <div class="section-body">
          <div class="log-shell">
            <div class="log-head">
              <div class="log-lights"><i></i><i></i><i></i></div>
              <strong>System runtime logs · evidence bus</strong>
            </div>
            <div class="log-body">{"".join(rows)}</div>
          </div>
        </div>
      </section>
    """
    return _shell(
        "Audit evidence for incident-to-vault packaging.",
        "A replayable log of sync actions, bundle gaps, and review-lane escalation.",
        "audit",
        body,
    )


def render_integrations() -> str:
    config = SERVICE.integration_posture()
    targets = "".join(
        f"""
        <div class="integration-row">
          <div>
            <strong>{escape(item["name"])}</strong>
            <span>{escape(item["type"])}</span>
          </div>
          <span class="toggle {'good' if item['enabled'] else 'bad'}">{'Enabled' if item['enabled'] else 'Standby'}</span>
        </div>
        """
        for item in config["targets"]
    )
    body = f"""
      <section class="page-section">
        <div class="section-head">
          <strong>Integration posture</strong>
          <h2>The connectors and thresholds that make the evidence lane believable.</h2>
          <p>This makes the repo feel like a real workflow component instead of a standalone analyzer. ServiceNow context, CyberArk context, and pipeline thresholds all stay visible together.</p>
        </div>
        <div class="section-body">
          <div class="config-grid">
            <div class="panel">
              <h3>ServiceNow input</h3>
              <div class="panel-grid">
                <div class="config-row">
                  <div><strong>Incident endpoint</strong><span>{escape(config["servicenow"]["apiBaseUrl"])}</span></div>
                  <span class="toggle good">Live</span>
                </div>
                <div class="config-row">
                  <div><strong>Authentication</strong><span>{escape(config["servicenow"]["authType"])}</span></div>
                  <span class="toggle good">Bound</span>
                </div>
                <div class="config-row">
                  <div><strong>State filter</strong><span>{escape(config["servicenow"]["stateFilter"])}</span></div>
                  <span class="toggle good">Scoped</span>
                </div>
              </div>
            </div>
            <div class="panel">
              <h3>CyberArk enrichment</h3>
              <div class="panel-grid">
                <div class="config-row">
                  <div><strong>Vault endpoint</strong><span>{escape(config["cyberark"]["apiBaseUrl"])}</span></div>
                  <span class="toggle good">Live</span>
                </div>
                <div class="config-row">
                  <div><strong>Authentication</strong><span>{escape(config["cyberark"]["authType"])}</span></div>
                  <span class="toggle good">Strict</span>
                </div>
                <div class="config-row">
                  <div><strong>Safe ownership sync</strong><span>Owner and dual-approval posture stay attached to each incident packet.</span></div>
                  <span class="toggle {'good' if config['cyberark']['safeOwnershipSync'] else 'bad'}">{'Enabled' if config['cyberark']['safeOwnershipSync'] else 'Disabled'}</span>
                </div>
              </div>
            </div>
          </div>
          <section class="page-section" style="margin-top:18px;">
            <div class="section-head">
              <strong>Target systems</strong>
              <h2>Where the packaged evidence is expected to land.</h2>
              <p>This is the practical handoff story: incidents, certification packs, and audit archives all consume the same structured record.</p>
            </div>
            <div class="section-body">
              <div class="panel-grid">{targets}</div>
            </div>
          </section>
        </div>
      </section>
    """
    return _shell(
        "Configuration and target-system posture for the evidence lane.",
        "ServiceNow inputs, CyberArk enrichment, and the systems this pipeline is meant to feed.",
        "integrations",
        body,
    )


def render_methodology() -> str:
    payload = json.dumps(SERVICE.sample_payload(), indent=2)
    body = f"""
      <section class="page-section">
        <div class="section-head">
          <strong>Methodology</strong>
          <h2>How the pipeline decides what belongs in the urgent lane.</h2>
          <p>The score is deliberately built from priority, evidence freshness, artifact depth, ownership quality, and exception pressure so the queue feels operational instead of arbitrary.</p>
        </div>
        <div class="section-body">
          <div class="insight-grid">
            <div class="panel">
              <h3>Scoring factors</h3>
              <div class="panel-grid">
                <div class="metric-card">
                  <div class="micro">Evidence freshness</div>
                  <div class="title">Old or missing evidence should rise quickly.</div>
                  <div class="desc">An incident cannot become governance-safe if the underlying proof is stale or absent.</div>
                </div>
                <div class="metric-card">
                  <div class="micro">Approval chain</div>
                  <div class="title">Artifacts and ticket links matter together.</div>
                  <div class="desc">The pipeline keeps dual approval, manager verification, and artifact depth close together so the packet stays defensible.</div>
                </div>
                <div class="metric-card">
                  <div class="micro">Exception pressure</div>
                  <div class="title">Repeated exceptions should not hide in routine workflow state.</div>
                  <div class="desc">The point is to surface exception-heavy records before they quietly age into audit debt.</div>
                </div>
              </div>
            </div>
            <div class="code-panel">
              <div class="code-head"><span>/api/sample</span><div class="lights"><i></i><i></i><i></i></div></div>
              <pre><code>{escape(payload)}</code></pre>
            </div>
          </div>
        </div>
      </section>
    """
    return _shell(
        "Methodology behind privileged-review evidence prioritization.",
        "How the pipeline turns ticket state and vault metadata into review priority and bundle readiness.",
        "methodology",
        body,
    )


def render_docs() -> str:
    payload = json.dumps(SERVICE.sample_payload(), indent=2)
    body = f"""
      <section class="page-section">
        <div class="section-head">
          <strong>API summary</strong>
          <h2>Structured outputs for incident, review, and audit workflows.</h2>
          <p>The payload is designed to plug into ServiceNow updates, governance archives, or certification packs without losing the operator-readable explanation layer.</p>
        </div>
        <div class="section-body">
          <div class="insight-grid">
            <div class="panel">
              <div class="panel-grid">
                <div class="metric-card">
                  <div class="micro">GET /api/incidents</div>
                  <div class="title">Incident catalog</div>
                  <div class="desc">Returns the ranked incident surface with vault context, evidence age, and next actions attached.</div>
                </div>
                <div class="metric-card">
                  <div class="micro">GET /api/bundles</div>
                  <div class="title">Bundle output</div>
                  <div class="desc">Returns the packaged evidence records for governance, audit, and certification handoff.</div>
                </div>
                <div class="metric-card">
                  <div class="micro">GET /api/integrations</div>
                  <div class="title">Integration posture</div>
                  <div class="desc">Returns the ServiceNow input, CyberArk enrichment, and target-system configuration story.</div>
                </div>
              </div>
            </div>
            <div class="code-panel">
              <div class="code-head"><span>/api/sample</span><div class="lights"><i></i><i></i><i></i></div></div>
              <pre><code>{escape(payload)}</code></pre>
            </div>
          </div>
        </div>
      </section>
    """
    return _shell(
        "API summary for evidence packaging and review workflows.",
        "The pipeline emits structured incident-review decisions that can feed broader governance systems.",
        "docs",
        body,
    )
