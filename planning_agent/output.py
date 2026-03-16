"""위키 스타일 HTML 문서 생성"""

import html
import os
from datetime import datetime
from pathlib import Path
from typing import Optional


def _esc(text) -> str:
    return html.escape(str(text)) if text else ""


def _priority_tag(p: str) -> str:
    p = str(p).strip()
    cls = {"높음": "tag-red", "중간": "tag-orange", "낮음": "tag-green"}.get(p, "tag-blue")
    return f'<span class="tag {cls}">{_esc(p)}</span>'


def _status_tag(s: str) -> str:
    s = str(s).strip()
    if "TBD" in s.upper():
        return f'<span class="tag tag-red">{_esc(s)}</span>'
    if "잠정" in s:
        return f'<span class="tag tag-orange">{_esc(s)}</span>'
    return f'<span class="tag tag-blue">{_esc(s)}</span>'


def _impact_tag(i: str) -> str:
    i = str(i).strip()
    cls = {"높음": "tag-red", "중간": "tag-orange", "낮음": "tag-green"}.get(i, "tag-blue")
    return f'<span class="tag {cls}">{_esc(i)}</span>'


def _build_nav(req: dict, plan: dict) -> str:
    phase_subs = ""
    for i, phase in enumerate(plan.get("phases", [])):
        phase_subs += f'    <a class="nav-sub" data-page="plan" data-scroll="phase-{i}">{_esc(phase.get("name", f"Phase {i+1}"))}</a>\n'

    tbd_count = len(plan.get("tbd", []))
    tbd_badge = f'<span class="nav-badge tag tag-red">{tbd_count}</span>' if tbd_count else ""
    task_count = sum(len(p.get("tasks", [])) for p in plan.get("phases", []))

    return f"""
    <div class="nav-section">요구사항</div>
    <a class="nav-item active" data-page="overview"><span class="nav-icon">&#9889;</span> 프로젝트 개요</a>
    <a class="nav-sub" data-page="overview" data-scroll="goals">핵심 목표</a>
    <a class="nav-sub" data-page="overview" data-scroll="features">기능 요구사항</a>
    <a class="nav-sub" data-page="overview" data-scroll="nonfunc">비기능 요구사항</a>
    <a class="nav-sub" data-page="overview" data-scroll="tech">기술 스택</a>
    <a class="nav-sub" data-page="overview" data-scroll="constraints">제약사항</a>
    <div class="nav-section">구현 계획</div>
    <a class="nav-item" data-page="plan"><span class="nav-icon">&#128203;</span> 실행 계획 <span class="nav-badge tag tag-blue">{task_count}</span></a>
    <a class="nav-sub" data-page="plan" data-scroll="architecture">아키텍처</a>
{phase_subs}
    <a class="nav-item" data-page="risks"><span class="nav-icon">&#9888;&#65039;</span> 리스크 & 미결 {tbd_badge}</a>
    <a class="nav-sub" data-page="risks" data-scroll="risk-table">리스크 대응</a>
    <a class="nav-sub" data-page="risks" data-scroll="tbd-table">미결 사항</a>
    <div class="nav-section">관리</div>
    <a class="nav-item" data-page="milestones"><span class="nav-icon">&#128197;</span> 마일스톤</a>"""


def _build_overview(req: dict) -> str:
    name = _esc(req.get("project_name", "프로젝트"))
    summary = _esc(req.get("summary", ""))
    users = _esc(req.get("target_users", ""))
    techs = ", ".join(t.get("tech", "") for t in req.get("tech_stack", [])[:4])
    mc = len(req.get("features_must", []))
    nc = len(req.get("features_nice", []))

    goals = "".join(f"<li>{_esc(g)}</li>" for g in req.get("goals", []))
    must = "".join(
        f'<tr><td>{i}</td><td><strong>{_esc(f.get("name",""))}</strong></td><td>{_esc(f.get("desc",""))}</td><td>{_priority_tag("높음")}</td></tr>'
        for i, f in enumerate(req.get("features_must", []), 1)
    )
    nice = "".join(
        f'<tr><td>{i}</td><td><strong>{_esc(f.get("name",""))}</strong></td><td>{_esc(f.get("desc",""))}</td><td>{_priority_tag("낮음")}</td></tr>'
        for i, f in enumerate(req.get("features_nice", []), 1)
    )
    nf = "".join(f"<li>{_esc(n)}</li>" for n in req.get("non_functional", []))
    tech_rows = "".join(
        f'<tr><td>{_esc(t.get("area",""))}</td><td><strong>{_esc(t.get("tech",""))}</strong></td><td>{_esc(t.get("reason",""))}</td></tr>'
        for t in req.get("tech_stack", [])
    )
    cons = "".join(f"<li>{_esc(c)}</li>" for c in req.get("constraints", []))

    nice_section = f'<h3>선택 기능 (Nice-to-have)</h3><table><thead><tr><th>#</th><th>기능</th><th>설명</th><th>우선순위</th></tr></thead><tbody>{nice}</tbody></table>' if nice else ""

    return f"""
  <div class="page-header">
    <div class="breadcrumb">요구사항 &rsaquo; <span>프로젝트 개요</span></div>
    <h1>{name}</h1><p class="page-desc">{summary}</p>
  </div>
  <div class="content">
    <div class="infobox">
      <div class="infobox-title">{name}</div>
      <div class="infobox-row"><div class="infobox-label">상태</div><div class="infobox-value"><span class="tag tag-purple">계획 수립</span></div></div>
      <div class="infobox-row"><div class="infobox-label">필수 기능</div><div class="infobox-value">{mc}개</div></div>
      <div class="infobox-row"><div class="infobox-label">선택 기능</div><div class="infobox-value">{nc}개</div></div>
      <div class="infobox-row"><div class="infobox-label">기술 스택</div><div class="infobox-value">{_esc(techs)}</div></div>
      <div class="infobox-row"><div class="infobox-label">대상 사용자</div><div class="infobox-value">{users}</div></div>
    </div>
    <p>{summary}</p>
    <h2 id="goals">핵심 목표</h2><ul>{goals}</ul>
    <h2 id="features">기능 요구사항</h2>
    <h3>필수 기능 (Must-have)</h3>
    <table><thead><tr><th>#</th><th>기능</th><th>설명</th><th>우선순위</th></tr></thead><tbody>{must}</tbody></table>
    {nice_section}
    <h2 id="nonfunc">비기능 요구사항</h2><ul>{nf}</ul>
    <h2 id="tech">기술 스택</h2>
    <table><thead><tr><th>영역</th><th>기술</th><th>선택 이유</th></tr></thead><tbody>{tech_rows}</tbody></table>
    <h2 id="constraints">제약사항 및 가정</h2><ul>{cons}</ul>
  </div>"""


def _build_plan(plan: dict) -> str:
    arch = _esc(plan.get("architecture", ""))
    tech_rows = "".join(
        f'<tr><td>{_esc(t.get("area",""))}</td><td><strong>{_esc(t.get("tech",""))}</strong></td><td>{_esc(t.get("reason",""))}</td></tr>'
        for t in plan.get("tech_stack", [])
    )
    tech_section = f'<h3>기술 스택</h3><table><thead><tr><th>영역</th><th>기술</th><th>선택 이유</th></tr></thead><tbody>{tech_rows}</tbody></table>' if tech_rows else ""

    colors = ["tag-purple", "tag-blue", "tag-green", "tag-orange", "tag-cyan", "tag-red"]
    phases_html = ""
    for i, phase in enumerate(plan.get("phases", [])):
        c = colors[i % len(colors)]
        tasks = "".join(
            f'<li><div class="check" onclick="toggleCheck(this)"></div><div><div class="check-label">{_esc(t.get("name",""))}</div><div class="check-meta">{_esc(t.get("desc",""))} &middot; 의존성: {_esc(t.get("dependency","없음"))}</div></div><div>{_priority_tag(t.get("priority","중간"))}</div></li>'
            for t in phase.get("tasks", [])
        )
        tc = len(phase.get("tasks", []))
        phases_html += f"""
    <h2 id="phase-{i}"><span class="tag {c}">Phase {i+1}</span> {_esc(phase.get("name",""))}</h2>
    <div class="card">
      <p><strong>목표:</strong> {_esc(phase.get("goal",""))}</p>
      <p class="desc"><strong>예상 기간:</strong> {_esc(phase.get("duration",""))}</p>
      <div class="toggle open"><div class="toggle-header" onclick="toggleSection(this)"><span class="toggle-arrow">&#9654;</span><span class="toggle-label">태스크 ({tc})</span></div>
        <div class="toggle-body"><ul class="checklist">{tasks}</ul></div></div>
      <div class="note"><strong>산출물:</strong> {_esc(phase.get("deliverables",""))}</div>
    </div>"""

    return f"""
  <div class="page-header">
    <div class="breadcrumb">구현 계획 &rsaquo; <span>실행 계획</span></div>
    <h1>&#128203; 실행 계획</h1><p class="page-desc">구체화된 요구사항 기반 단계별 구현 계획</p>
  </div>
  <div class="content">
    <h2 id="architecture">아키텍처 개요</h2><div class="card"><p>{arch}</p></div>
    {tech_section}{phases_html}
  </div>"""


def _build_risks(plan: dict) -> str:
    rr = "".join(
        f'<tr><td><strong>{_esc(r.get("risk",""))}</strong></td><td>{_impact_tag(r.get("impact",""))}</td><td>{_esc(r.get("mitigation",""))}</td></tr>'
        for r in plan.get("risks", [])
    )
    tbd = "".join(
        f'<tr><td>{i:02d}</td><td><strong>{_esc(t.get("item",""))}</strong></td><td>{_status_tag(t.get("status","TBD"))}</td><td>{_esc(t.get("action",""))}</td></tr>'
        for i, t in enumerate(plan.get("tbd", []), 1)
    )
    tbd_sec = f'<h2 id="tbd-table">미결 사항 (TBD)</h2><table><thead><tr><th>#</th><th>항목</th><th>상태</th><th>결정 필요 내용</th></tr></thead><tbody>{tbd}</tbody></table>' if tbd else ""

    return f"""
  <div class="page-header">
    <div class="breadcrumb">구현 계획 &rsaquo; <span>리스크 & 미결</span></div>
    <h1>&#9888;&#65039; 리스크 & 미결 사항</h1><p class="page-desc">예상 리스크와 미결 사항</p>
  </div>
  <div class="content">
    <h2 id="risk-table">리스크 및 대응 방안</h2>
    <table><thead><tr><th>리스크</th><th>영향도</th><th>대응 방안</th></tr></thead><tbody>{rr}</tbody></table>
    {tbd_sec}
  </div>"""


def _build_milestones(plan: dict) -> str:
    colors = ["tag-purple", "tag-blue", "tag-green", "tag-orange", "tag-cyan", "tag-red"]
    rows = "".join(
        f'<tr><td><span class="tag {colors[i%len(colors)]}">{_esc(m.get("name",""))}</span></td><td>{_esc(m.get("target",""))}</td><td>{_esc(m.get("deliverable",""))}</td></tr>'
        for i, m in enumerate(plan.get("milestones", []))
    )
    return f"""
  <div class="page-header">
    <div class="breadcrumb">관리 &rsaquo; <span>마일스톤</span></div>
    <h1>&#128197; 마일스톤</h1><p class="page-desc">주요 이정표와 예상 일정</p>
  </div>
  <div class="content">
    <table><thead><tr><th>마일스톤</th><th>예상 완료</th><th>핵심 산출물</th></tr></thead><tbody>{rows}</tbody></table>
  </div>"""


_TEMPLATE = """\
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} - 프로젝트 계획서</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&display=swap');
:root{{--bg:#0f1117;--sidebar-bg:#13151e;--surface:#1a1d27;--surface2:#232733;--border:#2e3344;--text:#e4e6ed;--text-dim:#8b90a0;--text-faint:#5a5f72;--accent:#7c6aef;--accent-glow:rgba(124,106,239,.15);--accent-hover:rgba(124,106,239,.08);--gold:#f0c040;--gold-dim:rgba(240,192,64,.12);--red:#ef4444;--green:#22c55e;--blue:#3b82f6;--orange:#f59e0b;--cyan:#06b6d4;--sidebar-w:270px}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Noto Sans KR',-apple-system,sans-serif;background:var(--bg);color:var(--text);line-height:1.7;font-size:15px}}
.sidebar{{position:fixed;top:0;left:0;width:var(--sidebar-w);height:100vh;background:var(--sidebar-bg);border-right:1px solid var(--border);display:flex;flex-direction:column;z-index:200;overflow:hidden}}
.sidebar-header{{padding:24px 20px 20px;border-bottom:1px solid var(--border)}}
.sidebar-logo{{font-size:11px;font-weight:500;color:var(--accent);letter-spacing:1.5px;text-transform:uppercase;margin-bottom:6px}}
.sidebar-title{{font-size:17px;font-weight:900;line-height:1.3}}.sidebar-title span{{color:var(--gold)}}
.sidebar-version{{font-size:11px;color:var(--text-faint);margin-top:5px}}
.search-box{{padding:10px 20px;border-bottom:1px solid var(--border)}}
.search-input{{width:100%;padding:7px 11px;background:var(--surface2);border:1px solid var(--border);border-radius:6px;color:var(--text);font-size:13px;font-family:inherit;outline:none}}
.search-input::placeholder{{color:var(--text-faint)}}.search-input:focus{{border-color:var(--accent)}}
.sidebar-nav{{flex:1;overflow-y:auto;padding:10px 0}}
.sidebar-nav::-webkit-scrollbar{{width:3px}}.sidebar-nav::-webkit-scrollbar-thumb{{background:var(--border);border-radius:3px}}
.nav-section{{padding:12px 20px 5px;font-size:10px;font-weight:700;color:var(--text-faint);letter-spacing:1.5px;text-transform:uppercase}}
.nav-item{{display:flex;align-items:center;gap:10px;padding:8px 20px;cursor:pointer;color:var(--text-dim);font-size:13.5px;font-weight:400;transition:all .12s;border-left:3px solid transparent;text-decoration:none}}
.nav-item:hover{{background:var(--accent-hover);color:var(--text)}}
.nav-item.active{{background:var(--accent-glow);color:var(--accent);border-left-color:var(--accent);font-weight:600}}
.nav-item .nav-icon{{font-size:15px;width:20px;text-align:center;flex-shrink:0}}
.nav-item .nav-badge{{margin-left:auto;font-size:10px;padding:1px 7px;border-radius:8px;font-weight:600}}
.nav-sub{{padding:4px 20px 4px 53px;font-size:12.5px;color:var(--text-faint);cursor:pointer;transition:all .12s;display:block;text-decoration:none}}
.nav-sub:hover{{color:var(--text)}}.nav-sub.active{{color:var(--accent);font-weight:500}}
.sidebar-footer{{padding:14px 20px;border-top:1px solid var(--border);font-size:11px;color:var(--text-faint)}}
.main{{margin-left:var(--sidebar-w);min-height:100vh}}
.page-header{{padding:36px 48px 28px;border-bottom:1px solid var(--border);background:linear-gradient(135deg,rgba(26,16,64,.3) 0%,transparent 50%)}}
.page-header .breadcrumb{{font-size:12px;color:var(--text-faint);margin-bottom:10px}}.page-header .breadcrumb span{{color:var(--text-dim)}}
.page-header h1{{font-size:26px;font-weight:900;margin-bottom:5px}}.page-header .page-desc{{color:var(--text-dim);font-size:14px;max-width:700px}}
.content{{padding:28px 48px 60px;max-width:960px}}
.wiki-page{{display:none}}.wiki-page.active{{display:block}}
.content h2{{font-size:19px;font-weight:800;margin:32px 0 14px;padding-bottom:8px;border-bottom:1px solid var(--border)}}.content h2:first-child{{margin-top:0}}
.content h3{{font-size:15px;font-weight:700;margin:20px 0 10px}}
ul{{margin:8px 0 8px 20px}}ul li{{margin-bottom:4px}}
.card{{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:22px;margin-bottom:14px}}
.infobox{{float:right;width:250px;background:var(--surface);border:1px solid var(--border);border-radius:10px;margin:0 0 18px 22px;font-size:13px;overflow:hidden}}
.infobox-title{{background:var(--accent-glow);padding:9px 14px;font-weight:700;font-size:13px;color:var(--accent);text-align:center}}
.infobox-row{{display:flex;padding:7px 14px;border-top:1px solid var(--border)}}.infobox-label{{width:72px;flex-shrink:0;color:var(--text-dim);font-weight:500}}.infobox-value{{flex:1}}
.toggle{{margin-bottom:10px}}
.toggle-header{{display:flex;align-items:center;gap:10px;padding:11px 14px;background:var(--surface2);border:1px solid var(--border);border-radius:8px;cursor:pointer;user-select:none;transition:background .15s}}
.toggle-header:hover{{background:#2a2e3e}}
.toggle-arrow{{font-size:11px;color:var(--text-dim);transition:transform .2s;flex-shrink:0}}
.toggle.open .toggle-arrow{{transform:rotate(90deg)}}.toggle-label{{font-weight:500;font-size:14px;flex:1}}
.toggle-body{{display:none;padding:12px 14px 6px;border:1px solid var(--border);border-top:none;border-radius:0 0 8px 8px;background:var(--surface)}}.toggle.open .toggle-body{{display:block}}
table{{width:100%;border-collapse:collapse;font-size:13.5px;margin:10px 0}}
th{{text-align:left;padding:8px 12px;background:var(--surface2);border-bottom:1px solid var(--border);font-weight:600;font-size:12px;color:var(--text-dim);text-transform:uppercase;letter-spacing:.5px}}
td{{padding:8px 12px;border-bottom:1px solid var(--border);vertical-align:top}}tr:last-child td{{border-bottom:none}}
.tag{{display:inline-block;padding:2px 9px;border-radius:5px;font-size:11px;font-weight:500}}
.tag-purple{{background:var(--accent-glow);color:var(--accent)}}.tag-gold{{background:var(--gold-dim);color:var(--gold)}}
.tag-red{{background:rgba(239,68,68,.12);color:var(--red)}}.tag-green{{background:rgba(34,197,94,.12);color:var(--green)}}
.tag-blue{{background:rgba(59,130,246,.12);color:var(--blue)}}.tag-orange{{background:rgba(245,158,11,.12);color:var(--orange)}}.tag-cyan{{background:rgba(6,182,212,.12);color:var(--cyan)}}
.checklist{{list-style:none;padding:0;margin:0}}
.checklist li{{display:flex;align-items:flex-start;gap:10px;padding:7px 0;border-bottom:1px solid rgba(46,51,68,.5);font-size:13.5px}}.checklist li:last-child{{border-bottom:none}}
.check{{width:17px;height:17px;border:2px solid var(--border);border-radius:4px;flex-shrink:0;margin-top:2px;cursor:pointer;transition:all .15s;display:flex;align-items:center;justify-content:center}}
.check:hover{{border-color:var(--accent)}}.check.checked{{background:var(--accent);border-color:var(--accent)}}.check.checked::after{{content:'\\2713';color:#fff;font-size:11px;font-weight:700}}
.check-label{{flex:1}}.check-meta{{color:var(--text-dim);font-size:12px}}
.note{{background:rgba(245,158,11,.08);border-left:3px solid var(--orange);padding:9px 14px;border-radius:0 8px 8px 0;font-size:13px;margin:12px 0;color:var(--text-dim)}}.note strong{{color:var(--orange)}}
.tbd{{background:rgba(239,68,68,.08);border-left:3px solid var(--red);padding:9px 14px;border-radius:0 8px 8px 0;font-size:13px;margin:12px 0}}.tbd strong{{color:var(--red)}}
p{{margin-bottom:10px}}.desc{{color:var(--text-dim);font-size:13px}}
.sidebar-toggle{{display:none;position:fixed;top:12px;left:12px;z-index:300;width:40px;height:40px;background:var(--surface);border:1px solid var(--border);border-radius:8px;color:var(--text);font-size:20px;cursor:pointer;align-items:center;justify-content:center}}
@media(max-width:900px){{.sidebar{{transform:translateX(-100%);transition:transform .25s}}.sidebar.open{{transform:translateX(0)}}.sidebar-toggle{{display:flex}}.main{{margin-left:0}}.content{{padding:20px}}.page-header{{padding:20px}}.infobox{{float:none;width:100%;margin:0 0 14px 0}}}}
</style>
</head>
<body>
<button class="sidebar-toggle" onclick="document.querySelector('.sidebar').classList.toggle('open')">&#9776;</button>
<nav class="sidebar">
  <div class="sidebar-header">
    <div class="sidebar-logo">Planning Agent</div>
    <div class="sidebar-title"><span>{title}</span><br>프로젝트 계획서</div>
    <div class="sidebar-version">{timestamp}</div>
  </div>
  <div class="search-box"><input type="text" class="search-input" placeholder="페이지 검색..." oninput="filterNav(this.value)"></div>
  <div class="sidebar-nav">{nav}</div>
  <div class="sidebar-footer">Generated by Planning Agent</div>
</nav>
<div class="main">
  <div class="wiki-page active" id="page-overview">{pg_overview}</div>
  <div class="wiki-page" id="page-plan">{pg_plan}</div>
  <div class="wiki-page" id="page-risks">{pg_risks}</div>
  <div class="wiki-page" id="page-milestones">{pg_milestones}</div>
</div>
<script>
document.querySelectorAll('.nav-item,.nav-sub').forEach(item=>{{item.addEventListener('click',e=>{{e.preventDefault();const page=item.dataset.page,s=item.dataset.scroll;document.querySelectorAll('.nav-item').forEach(n=>n.classList.remove('active'));document.querySelectorAll('.nav-sub').forEach(n=>n.classList.remove('active'));document.querySelector('.nav-item[data-page="'+page+'"]').classList.add('active');if(item.classList.contains('nav-sub'))item.classList.add('active');document.querySelectorAll('.wiki-page').forEach(p=>p.classList.remove('active'));document.getElementById('page-'+page).classList.add('active');if(s){{setTimeout(()=>{{const el=document.getElementById(s);if(el)el.scrollIntoView({{behavior:'smooth',block:'start'}})}},50)}}else{{window.scrollTo(0,0)}};document.querySelector('.sidebar').classList.remove('open')}})}});
function toggleSection(el){{el.parentElement.classList.toggle('open')}}
function toggleCheck(el){{el.classList.toggle('checked');saveState()}}
function saveState(){{const c=[];document.querySelectorAll('.check').forEach(el=>c.push(el.classList.contains('checked')));localStorage.setItem('plan-wiki-'+location.pathname,JSON.stringify(c))}}
function loadState(){{const s=localStorage.getItem('plan-wiki-'+location.pathname);if(s){{const c=JSON.parse(s);document.querySelectorAll('.check').forEach((el,i)=>{{if(c[i])el.classList.add('checked')}})}}}}
loadState();
function filterNav(q){{q=q.toLowerCase().trim();document.querySelectorAll('.nav-item,.nav-sub').forEach(el=>{{el.style.display=(!q||el.textContent.toLowerCase().includes(q))?'':'none'}});document.querySelectorAll('.nav-section').forEach(el=>{{el.style.display=q?'none':''}})}}
</script>
</body>
</html>"""


def save_plan(
    requirements: dict,
    plan: dict,
    output_dir: str,
    project_name: Optional[str] = None,
) -> str:
    """구조화된 요구사항과 계획을 위키 스타일 HTML로 저장합니다."""
    os.makedirs(output_dir, exist_ok=True)

    title = project_name or requirements.get("project_name", "프로젝트")
    ts_display = datetime.now().strftime("%Y-%m-%d %H:%M")

    content = _TEMPLATE.format(
        title=_esc(title),
        timestamp=ts_display,
        nav=_build_nav(requirements, plan),
        pg_overview=_build_overview(requirements),
        pg_plan=_build_plan(plan),
        pg_risks=_build_risks(plan),
        pg_milestones=_build_milestones(plan),
    )

    ts_file = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    filepath = Path(output_dir) / f"plan_{ts_file}.html"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return str(filepath)
