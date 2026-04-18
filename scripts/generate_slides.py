"""
Generate Shop Sergeant presentation slides as Excalidraw files.
Outputs 13 .excalidraw files to output/slides/
"""
import base64
import json
import os

# Canvas dimensions (widescreen 16:9)
W, H = 1280, 720

# Colors from palette
C = {
    'primary_fill': '#3b82f6',
    'primary_stroke': '#1e3a5f',
    'secondary_fill': '#60a5fa',
    'tertiary_fill': '#93c5fd',
    'start_fill': '#fed7aa',
    'start_stroke': '#c2410c',
    'end_fill': '#a7f3d0',
    'end_stroke': '#047857',
    'warn_fill': '#fee2e2',
    'warn_stroke': '#dc2626',
    'decision_fill': '#fef3c7',
    'decision_stroke': '#b45309',
    'ai_fill': '#ddd6fe',
    'ai_stroke': '#6d28d9',
    'title': '#1e40af',
    'subtitle': '#3b82f6',
    'body': '#64748b',
    'on_light': '#374151',
    'white': '#ffffff',
    'canvas': '#ffffff',
}

LOGO_FILE_ID = "makersmiths_logo_v1"
_seed = [1000]


def _sid():
    _seed[0] += 17
    return _seed[0]


def logo_elem(x, y, w=240, h=41):
    s = _sid()
    return {
        "type": "image", "id": f"logo_{s}",
        "x": x, "y": y, "width": w, "height": h,
        "strokeColor": "transparent", "backgroundColor": "transparent",
        "fillStyle": "solid", "strokeWidth": 1, "strokeStyle": "solid",
        "roughness": 0, "opacity": 100, "angle": 0,
        "seed": s, "version": 1, "versionNonce": s * 2,
        "isDeleted": False, "groupIds": [], "boundElements": None,
        "link": None, "locked": False,
        "fileId": LOGO_FILE_ID, "status": "saved", "scale": [1, 1]
    }


def txt(x, y, w, h, text, size, color, align="center", va="middle", cid=None, angle=0):
    s = _sid()
    return {
        "type": "text", "id": f"txt_{s}",
        "x": x, "y": y, "width": w, "height": h,
        "text": text, "originalText": text,
        "fontSize": size, "fontFamily": 1,
        "textAlign": align, "verticalAlign": va,
        "strokeColor": color, "backgroundColor": "transparent",
        "fillStyle": "solid", "strokeWidth": 1, "strokeStyle": "solid",
        "roughness": 2, "opacity": 100, "angle": angle,
        "seed": s, "version": 1, "versionNonce": s * 2,
        "isDeleted": False, "groupIds": [], "boundElements": None,
        "link": None, "locked": False,
        "containerId": cid, "lineHeight": 1.25
    }


def rect(x, y, w, h, fill, stroke, sw=2, ss="solid", rounded=True):
    s = _sid()
    eid = f"rect_{s}"
    e = {
        "type": "rectangle", "id": eid,
        "x": x, "y": y, "width": w, "height": h,
        "strokeColor": stroke, "backgroundColor": fill,
        "fillStyle": "solid", "strokeWidth": sw, "strokeStyle": ss,
        "roughness": 2, "opacity": 100, "angle": 0,
        "seed": s, "version": 1, "versionNonce": s * 2,
        "isDeleted": False, "groupIds": [], "boundElements": [],
        "link": None, "locked": False,
        "roundness": {"type": 3} if rounded else None
    }
    return eid, e


def ellipse(x, y, w, h, fill, stroke, sw=2):
    s = _sid()
    eid = f"ell_{s}"
    e = {
        "type": "ellipse", "id": eid,
        "x": x, "y": y, "width": w, "height": h,
        "strokeColor": stroke, "backgroundColor": fill,
        "fillStyle": "solid", "strokeWidth": sw, "strokeStyle": "solid",
        "roughness": 2, "opacity": 100, "angle": 0,
        "seed": s, "version": 1, "versionNonce": s * 2,
        "isDeleted": False, "groupIds": [], "boundElements": [],
        "link": None, "locked": False
    }
    return eid, e


def arrow(x1, y1, x2, y2, color, sw=2):
    s = _sid()
    dx, dy = x2 - x1, y2 - y1
    return {
        "type": "arrow", "id": f"arr_{s}",
        "x": x1, "y": y1, "width": abs(dx), "height": abs(dy),
        "strokeColor": color, "backgroundColor": "transparent",
        "fillStyle": "solid", "strokeWidth": sw, "strokeStyle": "solid",
        "roughness": 2, "opacity": 100, "angle": 0,
        "seed": s, "version": 1, "versionNonce": s * 2,
        "isDeleted": False, "groupIds": [], "boundElements": None,
        "link": None, "locked": False,
        "points": [[0, 0], [dx, dy]],
        "startArrowhead": None, "endArrowhead": "arrow",
        "startBinding": None, "endBinding": None
    }


def line(x, y, pts, color, sw=2):
    s = _sid()
    return {
        "type": "line", "id": f"ln_{s}",
        "x": x, "y": y,
        "width": max(abs(p[0]) for p in pts),
        "height": max(abs(p[1]) for p in pts),
        "strokeColor": color, "backgroundColor": "transparent",
        "fillStyle": "solid", "strokeWidth": sw, "strokeStyle": "solid",
        "roughness": 2, "opacity": 100, "angle": 0,
        "seed": s, "version": 1, "versionNonce": s * 2,
        "isDeleted": False, "groupIds": [], "boundElements": None,
        "link": None, "locked": False, "points": pts
    }


def header(slide_n, total, title):
    """Blue top bar with slide number and title."""
    elems = []
    _, bar = rect(0, 0, W, 68, C['primary_fill'], C['primary_stroke'], sw=0, rounded=False)
    elems.append(bar)
    elems.append(txt(18, 14, 50, 40, f"{slide_n}/{total}", 20, C['white'], align="left"))
    elems.append(txt(78, 8, 1160, 52, title, 30, C['white'], align="left"))
    return elems


def footer_note(note):
    return txt(20, H - 28, W - 40, 24, note, 14, C['body'], align="center")


def wrap(elements):
    # Always place logo at bottom-right corner (220x38, original 790x136)
    logo_w, logo_h = 220, 38
    all_elems = list(elements) + [logo_elem(W - logo_w - 14, H - logo_h - 12, logo_w, logo_h)]
    return {
        "type": "excalidraw", "version": 2,
        "source": "https://excalidraw.com",
        "elements": all_elems,
        "appState": {"viewBackgroundColor": C['canvas'], "gridSize": 20},
        "files": {
            LOGO_FILE_ID: {
                "mimeType": "image/png",
                "id": LOGO_FILE_ID,
                "created": 1713427200000,
                "dataURL": LOGO_DATA_URL
            }
        }
    }


# ─────────────────────────────────────────────────────────
# SLIDE BUILDERS
# ─────────────────────────────────────────────────────────

TOTAL = 13


def slide01():
    """Title slide."""
    e = []
    # Background hero band
    _, bg = rect(0, 0, W, H, C['primary_fill'], C['primary_stroke'], sw=0, rounded=False)
    e.append(bg)
    # White card in center
    _, card = rect(60, 90, W - 120, H - 160, C['white'], C['primary_stroke'], sw=3)
    e.append(card)
    # Decorative corner accent (orange)
    _, acc1 = rect(60, 90, 12, H - 160, C['start_fill'], C['start_stroke'], sw=0, rounded=False)
    e.append(acc1)
    _, acc2 = rect(W - 72, 90, 12, H - 160, C['end_fill'], C['end_stroke'], sw=0, rounded=False)
    e.append(acc2)
    # Main title
    e.append(txt(80, 120, W - 160, 120, "SHOP SERGEANT", 96, C['title'], align="center"))
    # Subtitle
    e.append(txt(80, 255, W - 160, 50, "Automated Volunteer Task Tracking", 36, C['subtitle'], align="center"))
    # Divider
    e.append(line(200, 318, [[0, 0], [W - 400, 0]], C['body'], sw=2))
    # Org & status
    e.append(txt(80, 330, W - 160, 36, "Makersmiths Leesburg (MSL)  ·  April 2026  ·  Phase 0 Underway", 22, C['body'], align="center"))
    # 4 pipeline pills
    pip_labels = [
        ("Task Database", C['secondary_fill'], C['primary_stroke']),
        ("Task Sheet", C['end_fill'], C['end_stroke']),
        ("Task Capture", C['start_fill'], C['start_stroke']),
        ("Task Reporting", C['ai_fill'], C['ai_stroke']),
    ]
    pill_w, pill_h = 240, 52
    start_x = (W - (4 * pill_w + 3 * 24)) // 2
    for i, (label, fill, stroke) in enumerate(pip_labels):
        px = start_x + i * (pill_w + 24)
        py = H - 180
        _, p = rect(px, py, pill_w, pill_h, fill, stroke, sw=2)
        e.append(p)
        e.append(txt(px, py, pill_w, pill_h, label, 20, stroke))
    e.append(txt(80, H - 112, W - 160, 30, "Four Pipelines · Slack Interface · Google Sheets · Claude AI · No Paper", 18, C['body'], align="center"))
    return wrap(e)


def slide02():
    """Problem Statement — 5 weaknesses as fan-out."""
    e = header(2, TOTAL, "The Problem: Why Paper Falls Short")

    # Center circle
    cx, cy = W // 2, H // 2 + 20
    cr_w, cr_h = 200, 90
    _, cen = ellipse(cx - cr_w // 2, cy - cr_h // 2, cr_w, cr_h,
                     C['warn_fill'], C['warn_stroke'], sw=3)
    e.append(cen)
    e.append(txt(cx - cr_w // 2, cy - cr_h // 2, cr_w, cr_h,
                 "Paper-Only\nProcess", 20, C['warn_stroke']))

    # Problems: (label, short desc, angle offset)
    problems = [
        ("Incomplete Records", "No reliable who/what/when", -120),
        ("No History", "Sheets discarded; 501c3 at risk", -60),
        ("No Monitoring", "Stewards fly blind", 0),
        ("No Scheduling", "Periodic tasks forgotten", 60),
        ("Unrecognized\nContributors", "Top members go unnoticed", 120),
    ]
    import math
    box_w, box_h = 200, 72
    radius = 220

    for i, (label, desc, angle_deg) in enumerate(problems):
        angle = math.radians(angle_deg - 90)
        bx = cx + radius * math.cos(angle) - box_w // 2
        by = cy + radius * math.sin(angle) - box_h // 2
        # Arrow from center edge to box
        ax1 = cx + (cr_w // 2 + 5) * math.cos(angle)
        ay1 = cy + (cr_h // 2 + 5) * math.sin(angle)
        ax2 = bx + box_w // 2 - 5 * math.cos(angle)
        ay2 = by + box_h // 2 - 5 * math.sin(angle)
        e.append(arrow(ax1, ay1, ax2, ay2, C['warn_stroke'], sw=2))
        _, b = rect(int(bx), int(by), box_w, box_h, C['warn_fill'], C['warn_stroke'], sw=2)
        e.append(b)
        e.append(txt(int(bx), int(by), box_w, 36, label, 16, C['warn_stroke']))
        e.append(txt(int(bx), int(by) + 36, box_w, 32, desc, 13, C['body']))

    e.append(footer_note("§3 Problem Statement · All five gaps are addressed by Shop Sergeant"))
    return wrap(e)


def slide03():
    """System Overview — 4 pipelines + tech stack."""
    e = header(3, TOTAL, "System Overview: Four Pipelines")

    pipes = [
        ("Task Database", "Maintain master task\ncatalog in Google Sheets",
         C['secondary_fill'], C['primary_stroke']),
        ("Task Sheet", "Generate printable\nsign-up sheets",
         C['end_fill'], C['end_stroke']),
        ("Task Capture", "Record completions\nvia QR or OCR",
         C['start_fill'], C['start_stroke']),
        ("Task Reporting", "NL queries & scheduled\nreports via Slack",
         C['ai_fill'], C['ai_stroke']),
    ]
    bw, bh = 270, 120
    gap = 30
    start_x = (W - (2 * bw + gap)) // 2
    positions = [
        (start_x, 100),
        (start_x + bw + gap, 100),
        (start_x, 240),
        (start_x + bw + gap, 240),
    ]
    for (label, desc, fill, stroke), (px, py) in zip(pipes, positions):
        _, b = rect(px, py, bw, bh, fill, stroke, sw=2)
        e.append(b)
        e.append(txt(px, py + 8, bw, 36, label, 22, stroke))
        e.append(txt(px, py + 48, bw, 64, desc, 15, C['on_light']))

    # Bottom row: key components
    e.append(txt(60, 385, W - 120, 30, "Key Components", 24, C['title'], align="center"))
    comps = [
        ("Slack", "Primary UI\nfor all actors", C['primary_fill'], C['primary_stroke']),
        ("Google Sheets", "Single source\nof truth", C['end_fill'], C['end_stroke']),
        ("Claude AI\nclaude-sonnet-4-6", "OCR + NL\nqueries", C['ai_fill'], C['ai_stroke']),
        ("APScheduler", "Recurring\nreminders", C['decision_fill'], C['decision_stroke']),
        ("Slack Bolt\n(Python 3.11+)", "Bot framework\n& event listener", C['secondary_fill'], C['primary_stroke']),
    ]
    cw, ch = 210, 90
    cx_start = (W - (len(comps) * cw + (len(comps) - 1) * 16)) // 2
    for i, (label, desc, fill, stroke) in enumerate(comps):
        px = cx_start + i * (cw + 16)
        _, b = rect(px, 422, cw, ch, fill, stroke, sw=2)
        e.append(b)
        e.append(txt(px, 422 + 4, cw, 40, label, 16, stroke))
        e.append(txt(px, 422 + 48, cw, 38, desc, 13, C['on_light']))

    e.append(footer_note("§4 System Overview · Phase 0 complete: Task Sheet Pipeline tooling"))
    return wrap(e)


def slide04():
    """Human Actors — staircase hierarchy."""
    e = header(4, TOTAL, "Human Actors")

    actors = [
        ("Member", "Any active\nMakersmiths member",
         "* Log own tasks\n* Query own history\n* View public reports",
         C['tertiary_fill'], C['primary_stroke']),
        ("Steward", "Responsible for\na specific location",
         "* All Member actions\n* Task CRUD (own location)\n* Generate sign-up sheets",
         C['secondary_fill'], C['primary_stroke']),
        ("Shop Steward", "Oversees entire\nshop",
         "* All Steward actions\n* Shop-wide access\n* Trigger reminders",
         C['primary_fill'], C['primary_stroke']),
        ("Shop Sergeant", "Manages the\nentire process",
         "* All Shop Steward actions\n* Bot errors & audit log\n* Full system config",
         C['start_fill'], C['start_stroke']),
    ]

    bw = 270
    bh_base = 140
    gap = 20
    total_w = len(actors) * bw + (len(actors) - 1) * gap
    sx = (W - total_w) // 2

    for i, (name, who, access, fill, stroke) in enumerate(actors):
        # Staircase: each box is taller on the right
        extra_h = i * 30
        py = 90 + (len(actors) - 1 - i) * 30
        bh = bh_base + extra_h
        px = sx + i * (bw + gap)
        _, b = rect(px, py, bw, bh, fill, stroke, sw=2)
        e.append(b)
        e.append(txt(px, py + 8, bw, 34, name, 22, stroke))
        e.append(line(px + 20, py + 46, [[0, 0], [bw - 40, 0]], stroke, sw=1))
        e.append(txt(px + 10, py + 54, bw - 20, 32, who, 14, C['on_light'], align="left"))
        e.append(txt(px + 10, py + 90, bw - 20, bh - 95, access, 13, C['on_light'], align="left", va="top"))

    # Escalation arrow
    e.append(arrow(sx - 10, 430, sx + total_w + 10, 430, C['body'], sw=2))
    e.append(txt(sx, 445, total_w, 24, "Escalating Access & Responsibility →", 16, C['body'], align="center"))

    e.append(footer_note("§2.2 Human Actors · Permissions enforce least-privilege per role"))
    return wrap(e)


def slide05():
    """System Actors — hub & spoke."""
    e = header(5, TOTAL, "System Actors")

    import math
    # Central hub: Agentic Workers
    cx, cy = W // 2, H // 2 + 20
    hw, hh = 200, 80
    _, hub = rect(cx - hw // 2, cy - hh // 2, hw, hh,
                  C['primary_fill'], C['primary_stroke'], sw=3)
    e.append(hub)
    e.append(txt(cx - hw // 2, cy - hh // 2, hw, hh, "Agentic\nWorkers", 20, C['white']))

    satellites = [
        ("Slack", "Primary UI", C['secondary_fill'], C['primary_stroke'], -90),
        ("Google Sheets", "Source of Truth", C['end_fill'], C['end_stroke'], -30),
        ("Claude AI\nModel", "OCR + NL", C['ai_fill'], C['ai_stroke'], 30),
        ("APScheduler", "Reminders", C['decision_fill'], C['decision_stroke'], 90),
        ("Mobile Web\nForm", "QR target", C['start_fill'], C['start_stroke'], 150),
        ("Physical\nSign-Up Sheet", "Floor touchpoint", C['tertiary_fill'], C['primary_stroke'], -150),
    ]
    orbit_r = 240
    sat_w, sat_h = 160, 68

    for label, desc, fill, stroke, angle_deg in satellites:
        angle = math.radians(angle_deg)
        sx2 = cx + orbit_r * math.cos(angle)
        sy2 = cy + orbit_r * math.sin(angle)
        # Arrow from hub edge to satellite edge
        ax1 = cx + (hw // 2 + 5) * math.cos(angle)
        ay1 = cy + (hh // 2 + 5) * math.sin(angle)
        ax2 = sx2 - (sat_w // 2 - 5) * math.cos(angle)
        ay2 = sy2 - (sat_h // 2 - 5) * math.sin(angle)
        e.append(arrow(ax1, ay1, ax2, ay2, stroke, sw=2))
        _, b = rect(int(sx2 - sat_w // 2), int(sy2 - sat_h // 2),
                    sat_w, sat_h, fill, stroke, sw=2)
        e.append(b)
        e.append(txt(int(sx2 - sat_w // 2), int(sy2 - sat_h // 2), sat_w, 38, label, 15, stroke))
        e.append(txt(int(sx2 - sat_w // 2), int(sy2 - sat_h // 2) + 38, sat_w, 26, desc, 12, C['body']))

    # QR Code and Mobile Phone as small notes
    e.append(txt(20, 80, 200, 24, "Also: QR Code, Mobile Phone", 14, C['body'], align="left"))

    e.append(footer_note("§2.3 System Actors · Agentic Workers is the bot brain connecting all parts"))
    return wrap(e)


def slide06():
    """Task Database Pipeline."""
    e = header(6, TOTAL, "Pipeline 1: Task Database")

    # Flow: YAML → Agentic Workers → Google Sheets
    nodes = [
        ("YAML Files\n(bulk import)", C['decision_fill'], C['decision_stroke'], 80, 180),
        ("Slack #shop-admin\n(individual CRUD)", C['secondary_fill'], C['primary_stroke'], 80, 300),
        ("Agentic\nWorkers", C['primary_fill'], C['primary_stroke'], 380, 240),
        ("Google\nSheets", C['end_fill'], C['end_stroke'], 660, 240),
        ("Slack #shop-alerts\n(notifications)", C['tertiary_fill'], C['primary_stroke'], 900, 180),
    ]
    nw, nh = 200, 80
    ids_added = {}
    for label, fill, stroke, nx, ny in nodes:
        _, b = rect(nx, ny, nw, nh, fill, stroke, sw=2)
        e.append(b)
        e.append(txt(nx, ny, nw, nh, label, 16, stroke))
        ids_added[label] = (nx, ny, nw, nh)

    # Arrows
    e.append(arrow(80 + nw, 180 + nh // 2, 380, 240 + nh // 2, C['primary_stroke']))
    e.append(arrow(80 + nw, 300 + nh // 2, 380, 240 + nh // 2, C['primary_stroke']))
    e.append(arrow(380 + nw, 240 + nh // 2, 660, 240 + nh // 2, C['end_stroke']))
    e.append(arrow(660 + nw, 240 + nh // 2, 900, 180 + nh // 2, C['primary_stroke']))

    # Requirements list
    e.append(txt(855, 290, 400, 30, "Requirements", 20, C['title'], align="left"))
    reqs = [
        "DB-1  Google Sheets is single source of truth",
        "DB-2  Bulk-load tasks from YAML files",
        "DB-3  CRUD via Slack #shop-admin",
        "DB-4  Only stewards/shop stewards may modify",
        "DB-5  Every task: ID, name, frequency, location",
        "DB-6  Reject duplicate task IDs & names",
        "DB-7  Every change notifies #shop-alerts",
    ]
    for i, r in enumerate(reqs):
        e.append(txt(860, 325 + i * 46, 400, 40, r, 14, C['on_light'], align="left", va="top"))

    e.append(footer_note("§5.1 Task Database Pipeline"))
    return wrap(e)


def slide07():
    """Task Sheet Pipeline."""
    e = header(7, TOTAL, "Pipeline 2: Task Sheet")

    # Flow left-to-right
    steps = [
        ("Google Sheets\n(task catalog)", C['end_fill'], C['end_stroke']),
        ("Jinja2\nTemplate", C['decision_fill'], C['decision_stroke']),
        ("HTML\nRender", C['secondary_fill'], C['primary_stroke']),
        ("PDF\n(wkhtmltopdf)", C['tertiary_fill'], C['primary_stroke']),
        ("Print &\nPost", C['start_fill'], C['start_stroke']),
    ]
    nw, nh = 170, 80
    gap = 50
    total_w = len(steps) * nw + (len(steps) - 1) * gap
    sx = (W - total_w) // 2
    sy = 160

    for i, (label, fill, stroke) in enumerate(steps):
        px = sx + i * (nw + gap)
        _, b = rect(px, sy, nw, nh, fill, stroke, sw=2)
        e.append(b)
        e.append(txt(px, sy, nw, nh, label, 16, stroke))
        if i < len(steps) - 1:
            e.append(arrow(px + nw, sy + nh // 2, px + nw + gap, sy + nh // 2, stroke))

    # Slack notification branch
    e.append(txt(W // 2 - 100, 270, 200, 24, "Notify #shop-bulletin", 15, C['body'], align="center"))
    _, notif = rect(W // 2 - 130, 298, 260, 60, C['secondary_fill'], C['primary_stroke'])
    e.append(notif)
    e.append(txt(W // 2 - 130, 298, 260, 60, "#shop-bulletin\nNew sheet ready!", 15, C['primary_stroke']))
    e.append(arrow(W // 2, 240, W // 2, 298, C['primary_stroke']))

    # Requirements
    e.append(txt(60, 388, W - 120, 30, "Requirements", 20, C['title'], align="left"))
    reqs = [
        ("TS-1", "Generate sheet for single location or all locations"),
        ("TS-2", "Only stewards (own location) / shop stewards / Shop Sergeant"),
        ("TS-3", "Via Slack command in #shop-admin or CLI script"),
        ("TS-4", "#shop-bulletin notified when sheets are ready"),
        ("TS-5", "#shop-alerts notified on every generation"),
        ("TS-6", "Bot reminds stewards when task changes make refresh advisable"),
    ]
    cols = 2
    per_col = (len(reqs) + 1) // 2
    col_w = (W - 120) // cols
    for i, (rid, rdesc) in enumerate(reqs):
        col = i // per_col
        row = i % per_col
        px = 60 + col * col_w
        py = 424 + row * 48
        e.append(txt(px, py, 80, 36, rid, 16, C['subtitle'], align="left", va="top"))
        e.append(txt(px + 85, py, col_w - 95, 36, rdesc, 14, C['on_light'], align="left", va="top"))

    e.append(footer_note("§5.2 Task Sheet Pipeline · Phase 0 tooling complete and tested"))
    return wrap(e)


def slide08():
    """Task Capture Pipeline — 3 methods."""
    e = header(8, TOTAL, "Pipeline 3: Task Capture")

    # 3 method columns
    methods = [
        ("Method 1\nOCR Photo", "Admin photographs\ncompleted sheet →\nClaude vision extracts\nnames & dates",
         "Alternative\n(fallback)", C['tertiary_fill'], C['primary_stroke'], False),
        ("Method 2\nPer-Task QR", "Each task row has\nits own QR code →\npre-fills Slack\nmessage",
         "Alternative\n(complex UX)", C['decision_fill'], C['decision_stroke'], False),
        ("Method 3\nSingle-Sheet QR", "One QR per sheet →\nMobile web form →\nSelect task →\nSubmit",
         "LIKELY SELECTION\n≤ 2 taps!", C['end_fill'], C['end_stroke'], True),
    ]
    mw, mh = 330, 310
    gap = 30
    total_w = len(methods) * mw + (len(methods) - 1) * gap
    sx = (W - total_w) // 2

    for i, (title, desc, status, fill, stroke, selected) in enumerate(methods):
        px = sx + i * (mw + gap)
        py = 86
        sw_val = 4 if selected else 2
        ss_val = "solid" if selected else "dashed"
        _, b = rect(px, py, mw, mh, fill, stroke, sw=sw_val, ss=ss_val)
        e.append(b)
        e.append(txt(px, py + 10, mw, 52, title, 22, stroke))
        e.append(line(px + 20, py + 68, [[0, 0], [mw - 40, 0]], stroke, sw=1))
        e.append(txt(px + 15, py + 78, mw - 30, 150, desc, 15, C['on_light'], align="left", va="top"))
        # Status badge
        badge_fill = C['end_fill'] if selected else C['warn_fill']
        badge_stroke = C['end_stroke'] if selected else C['body']
        _, badge = rect(px + 20, py + mh - 80, mw - 40, 60, badge_fill, badge_stroke, sw=2)
        e.append(badge)
        e.append(txt(px + 20, py + mh - 80, mw - 40, 60, status, 16, badge_stroke))

    # Common requirements
    reqs = [
        "TC-1  Record: Member name, Task ID, completion date, capture method",
        "TC-2  Write to Google Sheets immediately on submission",
        "TC-3  Confirm in #shop-log for every logged completion",
        "TC-5  ≤ 2 taps from QR scan to confirmation (Method 3)",
        "TC-6  No account, no login, no app installation required",
    ]
    e.append(txt(60, 420, W - 120, 28, "Common Requirements (all methods)", 18, C['title'], align="left"))
    col_w = (W - 120) // 2
    for i, r in enumerate(reqs):
        col = i % 2
        row = i // 2
        e.append(txt(60 + col * (col_w + 10), 452 + row * 38, col_w, 34, r, 13, C['on_light'], align="left", va="top"))

    e.append(footer_note("§5.3 Task Capture Pipeline · Method selected after Phase 0 trial with stewards & members"))
    return wrap(e)


def slide09():
    """Task Reporting Pipeline."""
    e = header(9, TOTAL, "Pipeline 4: Task Reporting")

    # Left: query flow
    e.append(txt(50, 88, 400, 28, "Natural Language Query Flow", 18, C['title'], align="left"))
    flow_items = [
        ("Member asks question\nin #shop-queries", C['secondary_fill'], C['primary_stroke'], 50, 120),
        ("Agentic Workers\npasses to Claude", C['primary_fill'], C['primary_stroke'], 50, 230),
        ("Google Sheets\nquery executed", C['end_fill'], C['end_stroke'], 50, 340),
        ("Response posted\nin Slack", C['ai_fill'], C['ai_stroke'], 50, 450),
    ]
    fw, fh = 280, 72
    for i, (label, fill, stroke, fx, fy) in enumerate(flow_items):
        _, b = rect(fx, fy, fw, fh, fill, stroke, sw=2)
        e.append(b)
        e.append(txt(fx, fy, fw, fh, label, 15, stroke))
        if i < len(flow_items) - 1:
            e.append(arrow(fx + fw // 2, fy + fh, fx + fw // 2, flow_items[i + 1][4], stroke))

    # Right: report types
    e.append(txt(380, 88, 870, 28, "Report Types & Access", 18, C['title'], align="left"))
    reports = [
        ("Member Report", "Tasks completed, compliance status",
         "Member (own), Stewards+ (any)", C['secondary_fill'], C['primary_stroke']),
        ("Location Report", "Task status for a location, overdue",
         "All Members (public data)", C['end_fill'], C['end_stroke']),
        ("Shop Report", "Aggregate compliance, top contributors",
         "All Members (public data)", C['tertiary_fill'], C['primary_stroke']),
        ("Compliance Report", "Who met / didn't meet 2hr/month",
         "Shop Steward & Shop Sergeant ONLY", C['warn_fill'], C['warn_stroke']),
    ]
    rw, rh = 570, 100
    for i, (name, desc, access, fill, stroke) in enumerate(reports):
        rx = 390
        ry = 122 + i * (rh + 14)
        _, b = rect(rx, ry, rw, rh, fill, stroke, sw=2)
        e.append(b)
        e.append(txt(rx + 10, ry + 6, rw - 20, 34, name, 18, stroke, align="left"))
        e.append(txt(rx + 10, ry + 42, rw - 20, 26, desc, 14, C['on_light'], align="left"))
        e.append(txt(rx + 10, ry + 68, rw - 20, 26, f"Access: {access}", 13, C['body'], align="left"))

    # Scheduled reports note
    _, note = rect(390, 570, 570, 66, C['decision_fill'], C['decision_stroke'], sw=2)
    e.append(note)
    e.append(txt(390, 570, 570, 66,
                 "Scheduled: Monthly summary & top-contributors → #shop-bulletin\nWeekly: errors & availability → #shop-bulletin",
                 14, C['decision_stroke']))

    e.append(footer_note("§5.4 Task Reporting Pipeline · TR-1 through TR-7"))
    return wrap(e)


def slide10():
    """Physical Sign-Up Sheet Requirements."""
    e = header(10, TOTAL, "Physical Sign-Up Sheet")

    # Left: visual mockup of the sheet
    e.append(txt(50, 88, 440, 28, "Sheet Layout (8.5×11\" Landscape)", 18, C['title'], align="left"))
    # Outer sheet border
    _, sheet = rect(50, 118, 560, 370, '#f8fafc', C['primary_stroke'], sw=2)
    e.append(sheet)
    # Sheet header band
    _, sh_hdr = rect(50, 118, 560, 50, C['secondary_fill'], C['primary_stroke'], sw=1, rounded=False)
    e.append(sh_hdr)
    e.append(txt(60, 122, 380, 42, "Metalshop  ·  Steward: Brad Hess  ·  2026-04-18", 14, C['on_light'], align="left"))
    # QR code placeholder (top right of header)
    _, qr_box = rect(548, 122, 54, 42, C['white'], C['primary_stroke'], sw=1, rounded=False)
    e.append(qr_box)
    e.append(txt(548, 122, 54, 42, "QR", 13, C['body']))
    # Column headers
    cols_data = [
        ("Task Name", 160), ("Freq", 70), ("Supv?", 60),
        ("Date", 90), ("Member Name", 140)
    ]
    col_x = 58
    for col_label, col_w in cols_data:
        _, ch = rect(col_x, 168, col_w - 4, 28, C['tertiary_fill'], C['primary_stroke'], sw=1, rounded=False)
        e.append(ch)
        e.append(txt(col_x, 168, col_w - 4, 28, col_label, 12, C['on_light']))
        col_x += col_w
    # Sample rows
    sample_tasks = [
        ("Dust & Wipe Down Machines", "Weekly", "No", "", ""),
        ("Vacuum Floor", "Daily", "No", "", ""),
        ("Check Dust Collection", "Weekly", "Yes", "", ""),
        ("Empty Shop Vac", "Bi-Wkly", "No", "", ""),
    ]
    for ri, row in enumerate(sample_tasks):
        row_y = 196 + ri * 36
        col_x = 58
        fill = C['white'] if ri % 2 == 0 else '#f1f5f9'
        for ci, (col_label, col_w) in enumerate(cols_data):
            _, cell = rect(col_x, row_y, col_w - 4, 32, fill, C['body'], sw=1, rounded=False)
            e.append(cell)
            e.append(txt(col_x + 4, row_y, col_w - 8, 32, row[ci], 12, C['on_light'], align="left"))
            col_x += col_w

    # Right: Requirements
    e.append(txt(650, 88, 600, 28, "Requirements", 18, C['title'], align="left"))
    req_groups = [
        ("Format (§6.1)", [
            "8.5×11\" landscape, one sheet per location",
            "Legible in black & white print",
            "Logo + location name + steward + date in header",
        ]),
        ("Columns (§6.2)", [
            "Task Name, Frequency, Supervisor Required",
            "Completion Date (blank — handwritten)",
            "Member Name (blank — handwritten)",
        ]),
        ("Display Rules (§6.3)", [
            "Group by location; omit TBD tasks silently",
            "Order by frequency (most frequent first)",
        ]),
        ("QR Placement (§6.4)", [
            "Method 2: one QR per task row",
            "Method 3: one QR in header (likely)",
        ]),
    ]
    ry = 120
    for group_title, items in req_groups:
        e.append(txt(650, ry, 600, 28, group_title, 16, C['subtitle'], align="left"))
        ry += 30
        for item in items:
            e.append(txt(670, ry, 580, 24, f"* {item}", 13, C['on_light'], align="left", va="top"))
            ry += 26
        ry += 10

    e.append(footer_note("§6 Physical Sign-Up Sheet Requirements · Primary member touchpoint on the shop floor"))
    return wrap(e)


def slide11():
    """Slack Bot & Channel Structure."""
    e = header(11, TOTAL, "Slack Bot & Channel Structure")

    # Channel table (left)
    e.append(txt(50, 88, 580, 28, "Slack Channels", 18, C['title'], align="left"))
    channels = [
        ("#shop-log", "All Members (read)", "Task completion confirmations", C['end_fill'], C['end_stroke']),
        ("#shop-bulletin", "All Members (read)", "Announcements, reminders, reports", C['secondary_fill'], C['primary_stroke']),
        ("#shop-queries", "All Members", "NL queries, public reports", C['ai_fill'], C['ai_stroke']),
        ("#shop-admin 🔒", "Stewards+ only", "Task CRUD, OCR uploads, restricted reports", C['decision_fill'], C['decision_stroke']),
        ("#shop-alerts 🔒", "Shop Sergeant only", "Bot errors, full audit trail", C['warn_fill'], C['warn_stroke']),
    ]
    cw, ch = 550, 78
    for i, (ch_name, access, purpose, fill, stroke) in enumerate(channels):
        _, b = rect(50, 118 + i * (ch + 10), cw, ch, fill, stroke, sw=2)
        e.append(b)
        e.append(txt(60, 118 + i * (ch + 10) + 6, cw - 20, 28, ch_name, 18, stroke, align="left"))
        e.append(txt(60, 118 + i * (ch + 10) + 36, cw - 20, 22, f"Access: {access}", 13, C['on_light'], align="left"))
        e.append(txt(60, 118 + i * (ch + 10) + 56, cw - 20, 18, purpose, 12, C['body'], align="left"))

    # Right: Key permission highlights
    e.append(txt(650, 88, 600, 28, "Permission Highlights", 18, C['title'], align="left"))
    perms = [
        ("All Actors",
         "Log task completions · query own history · view open tasks",
         C['secondary_fill'], C['primary_stroke']),
        ("Stewards",
         "Task CRUD (own location) · generate sign-up sheets\nOCR photo upload · suspend/restore own location",
         C['tertiary_fill'], C['primary_stroke']),
        ("Shop Stewards",
         "All Steward actions · any member's history\ntrigger reminder blasts · area suspend/restore",
         C['primary_fill'], C['primary_stroke']),
        ("Shop Sergeant",
         "All Shop Steward actions · full audit log\nsystem config · shop-wide suspend/restore",
         C['start_fill'], C['start_stroke']),
    ]
    for i, (role, perm, fill, stroke) in enumerate(perms):
        py = 118 + i * 122
        _, b = rect(650, py, 590, 110, fill, stroke, sw=2)
        e.append(b)
        e.append(txt(660, py + 6, 570, 28, role, 18, stroke, align="left"))
        e.append(txt(660, py + 38, 570, 68, perm, 13, C['on_light'], align="left", va="top"))

    e.append(footer_note("§7.2 Channel Structure · §7.3 Permission Model · Steward scope is always own-location"))
    return wrap(e)


def slide12():
    """KPIs & Success Criteria."""
    e = header(12, TOTAL, "Success Criteria & KPIs")

    # Left column: Member KPIs
    e.append(txt(50, 88, 570, 28, "Member-Facing Metrics", 18, C['title'], align="left"))
    mkpis = [
        ("M1", "Member Compliance Rate",
         "% members logging ≥ 1 completion/month", "Target: ≥ 50% monthly",
         C['secondary_fill'], C['primary_stroke']),
        ("M2", "Task Completion Rate",
         "% tasks completed within frequency window", "Target: ≥ 90%",
         C['end_fill'], C['end_stroke']),
        ("M3", "Data Completeness Rate",
         "% records with full name + Task ID + date", "Target: ≥ 95%",
         C['ai_fill'], C['ai_stroke']),
    ]
    for i, (kid, kname, kdesc, ktarget, fill, stroke) in enumerate(mkpis):
        _, b = rect(50, 118 + i * 148, 570, 130, fill, stroke, sw=2)
        e.append(b)
        e.append(txt(65, 118 + i * 148 + 8, 80, 40, kid, 28, stroke))
        e.append(txt(148, 118 + i * 148 + 8, 460, 32, kname, 18, stroke, align="left"))
        e.append(txt(65, 118 + i * 148 + 52, 545, 30, kdesc, 14, C['on_light'], align="left"))
        _, badge = rect(65, 118 + i * 148 + 86, 545, 30, C['white'], stroke, sw=1)
        e.append(badge)
        e.append(txt(65, 118 + i * 148 + 86, 545, 30, ktarget, 14, stroke))

    # Right column: Operational KPIs
    e.append(txt(660, 88, 580, 28, "Operational Metrics", 18, C['title'], align="left"))
    okpis = [
        ("O1", "Steward Adoption Rate",
         "% Stewards issuing ≥ 1 bot command", "Target: 100% within 60 days",
         C['primary_fill'], C['primary_stroke']),
        ("O2", "Sheet Refresh Latency",
         "Slack command → PDF available", "Target: ≤ 24 hours",
         C['decision_fill'], C['decision_stroke']),
        ("O3", "Overdue Task Alert Rate",
         "% overdue tasks triggering auto-reminder", "Target: 100%",
         C['start_fill'], C['start_stroke']),
        ("O4", "Top Contributor Recognition",
         "Monthly report posted to #shop-bulletin", "Target: 100% monthly",
         C['tertiary_fill'], C['primary_stroke']),
    ]
    for i, (kid, kname, kdesc, ktarget, fill, stroke) in enumerate(okpis):
        _, b = rect(660, 118 + i * 108, 580, 94, fill, stroke, sw=2)
        e.append(b)
        e.append(txt(672, 118 + i * 108 + 6, 70, 36, kid, 24, stroke))
        e.append(txt(744, 118 + i * 108 + 6, 484, 28, kname, 16, stroke, align="left"))
        e.append(txt(672, 118 + i * 108 + 42, 560, 24, kdesc, 13, C['on_light'], align="left"))
        e.append(txt(672, 118 + i * 108 + 66, 560, 22, ktarget, 13, stroke, align="left"))

    e.append(footer_note("§9 Success Criteria · Gap: need a 'members' sheet in Google Sheets for M1 & O1 denominators"))
    return wrap(e)


def slide13():
    """Out of Scope + Summary."""
    e = header(13, TOTAL, "Out of Scope & Key Open Questions")

    # Left: Out of scope
    e.append(txt(50, 88, 570, 28, "Out of Scope (Initial Release)", 18, C['title'], align="left"))
    oos = [
        ("Makersmiths Purcellville (MSP)", "Architecture must support it; no deployment planned"),
        ("Un-selected capture methods", "Once Method chosen; others documented only"),
        ("Email & SMS notifications", "Slack is the sole notification channel"),
        ("Native mobile app", "Web form + Slack only; no iOS/Android app"),
        ("Real-time dashboards", "On-demand NL queries + scheduled reports only"),
    ]
    for i, (item, note) in enumerate(oos):
        _, b = rect(50, 118 + i * 92, 570, 78, C['warn_fill'], C['warn_stroke'], sw=1, ss="dashed")
        e.append(b)
        e.append(txt(60, 118 + i * 92 + 6, 550, 28, f"✕  {item}", 16, C['warn_stroke'], align="left"))
        e.append(txt(60, 118 + i * 92 + 38, 550, 26, note, 13, C['body'], align="left"))

    # Right: Open Questions from Appendix
    e.append(txt(660, 88, 580, 28, "Open Design Questions (Appendix)", 18, C['title'], align="left"))
    questions = [
        "Retire Method 1 (OCR) & Method 2 (per-task QR) after Phase 0 trial?",
        "Is the permission model too open?\n(Stewards can suspend but not trigger reminders)",
        "Add OCR proof-of-concept to Phase 0 prototyping?",
        "Is the paper fallback permanent, or a launch-period hedge with a sunset?",
        "Should the mobile form be a PWA (offline + home screen icon)?",
        "Add 'time' field to task schema now to track estimated volunteer hours?",
    ]
    for i, q in enumerate(questions):
        e.append(txt(660, 118 + i * 90, 30, 30, "?", 22, C['decision_stroke']))
        _, qb = rect(692, 118 + i * 90, 556, 82, C['decision_fill'], C['decision_stroke'], sw=1)
        e.append(qb)
        e.append(txt(700, 118 + i * 90 + 6, 540, 70, q, 13, C['on_light'], align="left", va="top"))

    e.append(footer_note("§10 Out of Scope · Appendix: 6 open design questions to resolve before Phase 1"))
    return wrap(e)


# ─────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────

def main():
    # Load logo
    logo_path = os.path.join(os.path.dirname(__file__), '..', 'logos_images', 'makersmiths-logo.png')
    with open(logo_path, 'rb') as f:
        logo_b64 = base64.b64encode(f.read()).decode()
    global LOGO_DATA_URL
    LOGO_DATA_URL = f"data:image/png;base64,{logo_b64}"

    out_dir = os.path.join(os.path.dirname(__file__), '..', 'output', 'slides')
    os.makedirs(out_dir, exist_ok=True)

    slides = [
        (1, slide01),
        (2, slide02),
        (3, slide03),
        (4, slide04),
        (5, slide05),
        (6, slide06),
        (7, slide07),
        (8, slide08),
        (9, slide09),
        (10, slide10),
        (11, slide11),
        (12, slide12),
        (13, slide13),
    ]

    for n, builder in slides:
        data = builder()
        path = os.path.join(out_dir, f"slide-{n:02d}.excalidraw")
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"  wrote {path}")


if __name__ == '__main__':
    main()
