from __future__ import annotations

import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.evidence_pipeline_service import build_service


SERVICE = build_service()
OUT_DIR = ROOT / "screenshots"
OUT_DIR.mkdir(exist_ok=True)
WIDTH = 1600
HEIGHT = 980


def _page_shell(title: str, subtitle: str, body: str, active: str) -> str:
    tabs = [
        ("Dashboard", "overview"),
        ("Security & Architecture", "architecture"),
        ("Audit Trail", "audit"),
    ]
    tab_markup = []
    x = 384
    for label, key in tabs:
        if key == active:
            tab_markup.append(
                f"<rect x='{x}' y='22' width='176' height='54' rx='16' fill='#5d5cf6'/>"
                f"<text x='{x + 88}' y='56' text-anchor='middle' fill='white' font-size='14' font-family='Segoe UI' font-weight='700'>{escape(label)}</text>"
            )
            x += 188
        else:
            tab_markup.append(
                f"<text x='{x + 88}' y='56' text-anchor='middle' fill='#b9c5dc' font-size='14' font-family='Segoe UI' font-weight='700'>{escape(label)}</text>"
            )
            x += 214
    return f"""<svg xmlns='http://www.w3.org/2000/svg' width='{WIDTH}' height='{HEIGHT}' viewBox='0 0 {WIDTH} {HEIGHT}'>
  <defs>
    <linearGradient id='nav' x1='0' x2='0' y1='0' y2='1'>
      <stop offset='0%' stop-color='#141d33'/>
      <stop offset='100%' stop-color='#121a2f'/>
    </linearGradient>
    <filter id='shadow' x='-20%' y='-20%' width='140%' height='140%'>
      <feDropShadow dx='0' dy='18' stdDeviation='22' flood-color='rgba(22,32,55,0.12)'/>
    </filter>
  </defs>
  <rect width='{WIDTH}' height='{HEIGHT}' fill='#eef2f7'/>
  <rect x='0' y='0' width='{WIDTH}' height='96' fill='url(#nav)'/>
  <rect x='30' y='22' width='52' height='52' rx='12' fill='#5d5cf6'/>
  <text x='56' y='57' text-anchor='middle' fill='white' font-size='26' font-family='Segoe UI' font-weight='700'>P</text>
  <text x='106' y='44' fill='white' font-size='22' font-family='Segoe UI' font-weight='700'>Evidence Pipeline</text>
  <text x='106' y='67' fill='#b9c5dc' font-size='12' font-family='Segoe UI'>ServiceNow → CyberArk Bridge</text>
  <rect x='356' y='16' width='642' height='64' rx='18' fill='#202a41'/>
  {''.join(tab_markup)}
  <rect x='1110' y='22' width='132' height='52' rx='16' fill='#1f2a42' stroke='rgba(255,255,255,0.08)'/>
  <text x='1176' y='55' text-anchor='middle' fill='#cad5ea' font-size='14' font-family='Segoe UI' font-weight='700'>Monitor</text>
  <rect x='1256' y='22' width='140' height='52' rx='16' fill='#1f2a42' stroke='rgba(255,255,255,0.08)'/>
  <text x='1326' y='55' text-anchor='middle' fill='#cad5ea' font-size='14' font-family='Segoe UI' font-weight='700'>Terminal</text>
  <circle cx='1422' cy='48' r='6' fill='#14d18a'/>
  <text x='1442' y='54' fill='#14d18a' font-size='16' font-family='Segoe UI' font-weight='700'>SYSTEM ACTIVE</text>
  <rect x='28' y='124' width='1544' height='826' rx='28' fill='white' filter='url(#shadow)'/>
  <text x='60' y='168' fill='#7c8ea9' font-size='11' font-family='Segoe UI' font-weight='700' letter-spacing='3'>{escape(title.upper())}</text>
  <text x='60' y='206' fill='#1b2a41' font-size='24' font-family='Segoe UI' font-weight='700'>{escape(subtitle)}</text>
  {body}
</svg>"""


def _progress(x: int, y: int, width: int, progress: int, fill: str) -> str:
    return (
        f"<rect x='{x}' y='{y}' width='{width}' height='8' rx='4' fill='#edf1f6'/>"
        f"<rect x='{x}' y='{y}' width='{round(width * (progress / 100))}' height='8' rx='4' fill='{fill}'/>"
    )


def overview_svg() -> str:
    summary = SERVICE.summary()
    monitor = SERVICE.health_monitor()
    cards = []
    card_specs = [
        ("TOTAL SYNCS (24H)", f"{summary['totalSyncs24h']:,}", "#5d5cf6", 78),
        ("CYBERARK LATENCY", f"{summary['cyberarkLatencyMs']}ms", "#5d5cf6", 24),
        ("PIPELINE SUCCESS", f"{summary['pipelineSuccess']}%", "#16c784", 99),
        ("CRITICAL ALERTS", str(summary["criticalAlerts"]), "#e7ecf3", 2),
    ]
    x = 60
    for label, value, color, progress in card_specs:
        cards.append(
            f"""
            <rect x='{x}' y='240' width='352' height='132' rx='22' fill='white' stroke='#dfe6f0'/>
            <text x='{x + 24}' y='278' fill='#6f86a4' font-size='12' font-family='Segoe UI' font-weight='700'>{label}</text>
            <text x='{x + 24}' y='328' fill='#1b2a41' font-size='40' font-family='Georgia' font-style='italic' font-weight='700'>{value}</text>
            {_progress(x + 24, 344, 300, progress, color)}
            """
        )
        x += 382
    component_cards = []
    x = 60
    for component in monitor["components"]:
        fill = "#ff5c7a" if component["status"] == "watch" else "#16c784"
        component_cards.append(
            f"""
            <rect x='{x}' y='406' width='352' height='122' rx='22' fill='white' stroke='#dfe6f0'/>
            <rect x='{x + 26}' y='434' width='64' height='64' rx='18' fill='#eef6f2'/>
            <text x='{x + 58}' y='474' text-anchor='middle' fill='#16c784' font-size='28' font-family='Segoe UI' font-weight='700'>{escape(component["name"][0])}</text>
            <text x='{x + 112}' y='452' fill='#1b2a41' font-size='16' font-family='Segoe UI' font-weight='700'>{escape(component["name"])}</text>
            <text x='{x + 306}' y='452' text-anchor='end' fill='{fill}' font-size='14' font-family='Segoe UI' font-weight='700'>{component["cpu"]}% CPU</text>
            {_progress(x + 112, 464, 208, component["cpu"], fill)}
            <text x='{x + 112}' y='500' fill='#6f86a4' font-size='12' font-family='Segoe UI' font-weight='700'>{component["ramGb"]}GB RAM</text>
            <text x='{x + 306}' y='500' text-anchor='end' fill='#6f86a4' font-size='12' font-family='Segoe UI' font-weight='700'>{component["networkMb"]}MB/S NET</text>
            <circle cx='{x + 334}' cy='436' r='5' fill='#39dca1'/>
            """
        )
        x += 382
    trend_points = []
    series = SERVICE.sync_velocity()
    max_syncs = max(item["syncs"] for item in series)
    base_x = 90
    step = 124
    for index, item in enumerate(series):
        px = base_x + step * index
        py = 700 - round((item["syncs"] / max_syncs) * 88)
        trend_points.append(f"{px},{py}")
    labels = "".join(
        f"<text x='{90 + index * 124}' y='760' text-anchor='middle' fill='#93a5bf' font-size='12' font-family='Segoe UI'>{escape(item['hour'])}</text>"
        for index, item in enumerate(series)
    )
    distribution_rows = []
    y = 636
    for row in monitor["distribution"]:
        distribution_rows.append(
            f"""
            <text x='1140' y='{y}' fill='white' font-size='16' font-family='Segoe UI' font-weight='700'>{escape(row["name"])}</text>
            <text x='1510' y='{y}' text-anchor='end' fill='#8da2c7' font-size='14' font-family='Segoe UI' font-weight='700'>{row["share"]}%</text>
            {_progress(1140, y + 16, 370, row["share"], "#5d5cf6")}
            """
        )
        y += 64
    body = f"""
      {''.join(cards)}
      {''.join(component_cards)}
      <rect x='60' y='560' width='980' height='288' rx='24' fill='white' stroke='#dfe6f0'/>
      <text x='88' y='598' fill='#7c8ea9' font-size='11' font-family='Segoe UI' font-weight='700' letter-spacing='2'>SYNC VOLUME TRENDS</text>
      <polyline fill='none' stroke='#5d5cf6' stroke-width='4' stroke-linecap='round' stroke-linejoin='round' points='{' '.join(trend_points)}'/>
      <polygon fill='rgba(93,92,246,0.08)' points='{' '.join(trend_points)} 834,720 90,720'/>
      <line x1='90' y1='624' x2='1000' y2='624' stroke='#dfe5ee' stroke-dasharray='5 8'/>
      <line x1='90' y1='672' x2='1000' y2='672' stroke='#dfe5ee' stroke-dasharray='5 8'/>
      <line x1='90' y1='720' x2='1000' y2='720' stroke='#dfe5ee' stroke-dasharray='5 8'/>
      {labels}
      <rect x='1072' y='560' width='480' height='288' rx='24' fill='#141d34'/>
      <text x='1100' y='598' fill='#8da2c7' font-size='11' font-family='Segoe UI' font-weight='700' letter-spacing='2'>NODE DISTRIBUTION</text>
      {''.join(distribution_rows)}
      <text x='1100' y='810' fill='#8da2c7' font-size='11' font-family='Segoe UI' font-weight='700' letter-spacing='2'>ACTIVE PROCESSES</text>
      <text x='1508' y='810' text-anchor='end' fill='#16d48f' font-size='24' font-family='Segoe UI' font-weight='700'>{monitor["totals"]["activeProcesses"]} UNITS</text>
      <rect x='60' y='872' width='1492' height='40' rx='20' fill='#f8fbff' stroke='#e5ebf3'/>
      <text x='90' y='898' fill='#5d5cf6' font-size='12' font-family='Segoe UI' font-weight='700'>Connected to: ServiceNow-Instance-01</text>
      <text x='1508' y='898' text-anchor='end' fill='#16c784' font-size='12' font-family='Segoe UI' font-weight='700'>Worker Node #12 Health: Excellent</text>
    """
    return _page_shell("dashboard", "Bridge summary for the ServiceNow to CyberArk evidence lane.", body, "overview")


def monitor_svg() -> str:
    monitor = SERVICE.health_monitor()
    cards = []
    positions = [(80, 248), (420, 248), (80, 456), (420, 456)]
    for component, (x, y) in zip(monitor["components"], positions):
        fill = "#ff5c7a" if component["status"] == "watch" else "#5d5cf6"
        cards.append(
            f"""
            <rect x='{x}' y='{y}' width='300' height='172' rx='22' fill='#f7f9fd' stroke='#e3eaf3'/>
            <rect x='{x + 30}' y='{y + 30}' width='54' height='54' rx='16' fill='white' stroke='#e5ebf3'/>
            <text x='{x + 57}' y='{y + 66}' text-anchor='middle' fill='#5d5cf6' font-size='24' font-family='Segoe UI' font-weight='700'>{escape(component["name"][0])}</text>
            <text x='{x + 110}' y='{y + 66}' fill='#1b2a41' font-size='16' font-family='Segoe UI' font-weight='700'>{escape(component["name"])}</text>
            <text x='{x + 270}' y='{y + 100}' text-anchor='end' fill='#647b99' font-size='12' font-family='Segoe UI' font-weight='700'>{component["cpu"]}%</text>
            <text x='{x + 30}' y='{y + 100}' fill='#94a6c0' font-size='11' font-family='Segoe UI' font-weight='700'>CPU LOAD</text>
            {_progress(x + 30, y + 110, 240, component["cpu"], fill)}
            <rect x='{x + 30}' y='{y + 130}' width='74' height='44' rx='12' fill='white' stroke='#e5ebf3'/>
            <rect x='{x + 114}' y='{y + 130}' width='74' height='44' rx='12' fill='white' stroke='#e5ebf3'/>
            <rect x='{x + 198}' y='{y + 130}' width='74' height='44' rx='12' fill='white' stroke='#e5ebf3'/>
            <text x='{x + 67}' y='{y + 149}' text-anchor='middle' fill='#94a6c0' font-size='10' font-family='Segoe UI' font-weight='700'>MEMORY</text>
            <text x='{x + 67}' y='{y + 166}' text-anchor='middle' fill='#1b2a41' font-size='12' font-family='Segoe UI' font-weight='700'>{component["ramGb"]}GB</text>
            <text x='{x + 151}' y='{y + 149}' text-anchor='middle' fill='#94a6c0' font-size='10' font-family='Segoe UI' font-weight='700'>N/W I/O</text>
            <text x='{x + 151}' y='{y + 166}' text-anchor='middle' fill='#1b2a41' font-size='12' font-family='Segoe UI' font-weight='700'>{component["networkMb"]}MB/S</text>
            <text x='{x + 235}' y='{y + 149}' text-anchor='middle' fill='#94a6c0' font-size='10' font-family='Segoe UI' font-weight='700'>ERRORS</text>
            <text x='{x + 235}' y='{y + 166}' text-anchor='middle' fill='#16c784' font-size='12' font-family='Segoe UI' font-weight='700'>{component["errorRate"]}%</text>
            """
        )
    body = f"""
      <rect x='60' y='200' width='1480' height='720' rx='32' fill='white' stroke='#dfe6f0'/>
      <rect x='1040' y='248' width='420' height='468' rx='24' fill='#141d34'/>
      <text x='1100' y='284' fill='white' font-size='18' font-family='Segoe UI' font-weight='700'>System Health Monitor</text>
      <text x='1100' y='308' fill='#8fa1bf' font-size='11' font-family='Segoe UI' font-weight='700' letter-spacing='2'>REAL-TIME INFRASTRUCTURE TELEMETRY</text>
      <text x='1100' y='356' fill='#8da2c7' font-size='11' font-family='Segoe UI' font-weight='700' letter-spacing='2'>AGGREGATE RESOURCE POOL</text>
      <polyline fill='none' stroke='#ff4fa0' stroke-width='4' points='1088,520 1160,498 1232,510 1304,420 1376,392 1448,448'/>
      <polyline fill='none' stroke='#6c63ff' stroke-width='4' points='1088,540 1160,512 1232,530 1304,436 1376,388 1448,520'/>
      <text x='1100' y='598' fill='#8fa1bf' font-size='11' font-family='Segoe UI' font-weight='700'>AVG CPU</text>
      <text x='1100' y='632' fill='white' font-size='24' font-family='Segoe UI' font-weight='700'>{monitor["totals"]["avgCpu"]}%</text>
      <text x='1240' y='598' fill='#8fa1bf' font-size='11' font-family='Segoe UI' font-weight='700'>AVG MEM</text>
      <text x='1240' y='632' fill='white' font-size='24' font-family='Segoe UI' font-weight='700'>{monitor["totals"]["avgMemGb"]}GB</text>
      <text x='1380' y='598' fill='#16d48f' font-size='11' font-family='Segoe UI' font-weight='700'>NOMINAL</text>
      {''.join(cards)}
    """
    return _page_shell("monitor", "Infrastructure telemetry behind the evidence bridge.", body, "overview")


def architecture_svg() -> str:
    architecture = SERVICE.security_architecture()
    body = f"""
      <rect x='60' y='220' width='1040' height='700' rx='24' fill='white' stroke='#dfe6f0'/>
      <text x='92' y='258' fill='#1b2a41' font-size='18' font-family='Segoe UI' font-weight='700'>SYSTEM ARCHITECTURE DIAGRAM</text>
      <rect x='136' y='520' width='156' height='156' rx='24' fill='white' stroke='#dfe6ff'/>
      <text x='214' y='604' text-anchor='middle' fill='#5d5cf6' font-size='52' font-family='Segoe UI' font-weight='700'>◫</text>
      <text x='214' y='732' text-anchor='middle' fill='#1b2a41' font-size='20' font-family='Segoe UI' font-weight='700'>SERVICENOW</text>
      <text x='214' y='758' text-anchor='middle' fill='#6f86a4' font-size='12' font-family='Segoe UI'>ITSM / GRC MODULE</text>
      <circle cx='300' cy='504' r='12' fill='#16c784'/>
      <rect x='458' y='470' width='250' height='250' rx='125' fill='#f7f8ff' stroke='#dfe6ff'/>
      <rect x='528' y='536' width='110' height='110' rx='28' fill='#5d5cf6'/>
      <text x='583' y='603' text-anchor='middle' fill='white' font-size='56' font-family='Segoe UI' font-weight='700'>▣</text>
      <text x='583' y='736' text-anchor='middle' fill='#5d5cf6' font-size='22' font-family='Segoe UI' font-weight='700'>EVIDENCE PIPELINE</text>
      <text x='583' y='762' text-anchor='middle' fill='#6f86a4' font-size='12' font-family='Segoe UI'>FASTAPI CORE</text>
      <rect x='880' y='500' width='164' height='164' rx='24' fill='#172038'/>
      <text x='962' y='590' text-anchor='middle' fill='#20d698' font-size='52' font-family='Segoe UI' font-weight='700'>◔</text>
      <text x='962' y='720' text-anchor='middle' fill='#1b2a41' font-size='20' font-family='Segoe UI' font-weight='700'>CYBERARK VAULT</text>
      <text x='962' y='746' text-anchor='middle' fill='#6f86a4' font-size='12' font-family='Segoe UI'>PAM ENTERPRISE</text>
      <circle cx='1032' cy='482' r='12' fill='#16c784'/>
      <line x1='292' y1='596' x2='458' y2='596' stroke='#d7dff0' stroke-width='4'/>
      <line x1='708' y1='596' x2='880' y2='596' stroke='#d7dff0' stroke-width='4'/>
      <polygon points='862,590 880,596 862,602' fill='#8db0d6'/>
      <rect x='1140' y='220' width='400' height='210' rx='24' fill='white' stroke='#dfe6f0'/>
      <text x='1180' y='266' fill='#1b2a41' font-size='18' font-family='Segoe UI' font-weight='700'>CREDENTIAL MGMT</text>
      <rect x='1180' y='300' width='320' height='84' rx='18' fill='#f7f9fd' stroke='#e7edf6'/>
      <text x='1204' y='330' fill='#1b2a41' font-size='16' font-family='Segoe UI' font-weight='700'>{escape(architecture["credentials"][0]["title"])}</text>
      <text x='1204' y='356' fill='#6f86a4' font-size='13' font-family='Segoe UI'>{escape(architecture["credentials"][0]["detail"])}</text>
      <rect x='1140' y='456' width='400' height='210' rx='24' fill='white' stroke='#dfe6f0'/>
      <text x='1180' y='502' fill='#1b2a41' font-size='18' font-family='Segoe UI' font-weight='700'>TRANSIT SECURITY</text>
      {''.join(f"<text x='1206' y='{550 + index * 40}' fill='#16c784' font-size='14' font-family='Segoe UI'>◉</text><text x='1234' y='{550 + index * 40}' fill='#1b2a41' font-size='14' font-family='Segoe UI'>{escape(item)}</text>" for index, item in enumerate(architecture['transitControls']))}
      <rect x='1140' y='692' width='400' height='228' rx='24' fill='#141d34'/>
      <text x='1180' y='738' fill='white' font-size='18' font-family='Segoe UI' font-weight='700'>ACCESS CONTROL</text>
      <text x='1180' y='786' fill='#8fa1bf' font-size='14' font-family='Segoe UI' font-weight='700'>{escape(architecture["accessRoles"][0]["name"])}</text>
      <text x='1180' y='812' fill='#b9c5dc' font-size='13' font-family='Segoe UI'>{escape(architecture["accessRoles"][0]["detail"])}</text>
      <text x='1180' y='856' fill='#8fa1bf' font-size='14' font-family='Segoe UI' font-weight='700'>{escape(architecture["accessRoles"][1]["name"])}</text>
      <text x='1180' y='882' fill='#b9c5dc' font-size='13' font-family='Segoe UI'>{escape(architecture["accessRoles"][1]["detail"])}</text>
    """
    return _page_shell("security & architecture", "Security review surface for credentials, transport, and role posture.", body, "architecture")


def audit_svg() -> str:
    logs = SERVICE.audit_log()
    terminal = SERVICE.terminal_feed()
    rows = []
    y = 286
    for row in logs:
        result = "#16c784" if row["result"] == "Success" else "#ff5c7a"
        rows.append(
            f"""
            <rect x='60' y='{y}' width='1490' height='78' rx='16' fill='#182138'/>
            <text x='86' y='{y + 30}' fill='#8fa1bf' font-size='12' font-family='Consolas'>{escape(row["timestamp"])}</text>
            <text x='272' y='{y + 30}' fill='#6fc6ff' font-size='12' font-family='Consolas' font-weight='700'>{escape(row["action"])}</text>
            <text x='552' y='{y + 30}' fill='white' font-size='13' font-family='Segoe UI' font-weight='700'>{escape(row["resource"])}</text>
            <text x='552' y='{y + 52}' fill='#d9e3f5' font-size='12' font-family='Segoe UI'>{escape(row["detail"])}</text>
            <text x='1498' y='{y + 40}' text-anchor='end' fill='{result}' font-size='12' font-family='Segoe UI' font-weight='700'>{escape(row["result"].upper())}</text>
            """
        )
        y += 92
    terminal_lines = "".join(
        f"<text x='110' y='{786 + index * 22}' fill='#d9e3f5' font-size='13' font-family='Consolas'>{escape(line)}</text>"
        for index, line in enumerate(terminal[:4])
    )
    body = f"""
      <rect x='60' y='240' width='1490' height='520' rx='24' fill='#121a2f'/>
      <rect x='60' y='240' width='1490' height='62' rx='24' fill='#18213a'/>
      <circle cx='96' cy='271' r='6' fill='rgba(255,92,122,0.75)'/>
      <circle cx='114' cy='271' r='6' fill='rgba(245,185,76,0.75)'/>
      <circle cx='132' cy='271' r='6' fill='rgba(22,199,132,0.75)'/>
      <text x='158' y='276' fill='#c4d0e8' font-size='12' font-family='Segoe UI' font-weight='700'>ADVANCED FORENSIC AUDIT TRAIL</text>
      {''.join(rows)}
      <rect x='60' y='786' width='1490' height='126' rx='24' fill='#101728'/>
      <text x='96' y='822' fill='#c4d0e8' font-size='12' font-family='Segoe UI' font-weight='700'>OPERATOR TERMINAL</text>
      {terminal_lines}
    """
    return _page_shell("audit trail", "Replayable incident, enrichment, and bundle failure history.", body, "audit")


def main() -> None:
    for path in OUT_DIR.glob("*"):
        if path.is_file():
            path.unlink()
    (OUT_DIR / "overview-dashboard-proof.svg").write_text(overview_svg(), encoding="utf-8")
    (OUT_DIR / "system-monitor-proof.svg").write_text(monitor_svg(), encoding="utf-8")
    (OUT_DIR / "security-architecture-proof.svg").write_text(architecture_svg(), encoding="utf-8")
    (OUT_DIR / "audit-trail-proof.svg").write_text(audit_svg(), encoding="utf-8")
    print("rendered screenshots")


if __name__ == "__main__":
    main()
