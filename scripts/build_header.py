"""Build the animated 3D space header for the GitHub profile README.

Deep-space hero: a black-hole glow hangs from the top edge, stars twinkle,
and tech tiles orbit the photo in 3D (tiles behind the orbit pass under
the photo, tiles in front pass over it). Pure SVG + SMIL, no JavaScript.

Usage:
    python scripts/build_header.py                         # uses assets/avatar.jpg
    python scripts/build_header.py --avatar other.png
    python scripts/build_header.py --avatar github         # pull current GitHub avatar
"""
import argparse, base64, math, mimetypes, random, urllib.request

P = argparse.ArgumentParser()
P.add_argument("--user", default="vinayak-neoflo")
P.add_argument("--name", default="Vinayak Shukla")
P.add_argument("--badge", default="AI Engineering Intern at Neoflo")
P.add_argument("--head1", default="Making AI assistants")
P.add_argument("--head2a", default="run on")
P.add_argument("--head2b", default="clean data.")
P.add_argument("--body1", default="I build the pipelines that get documents chunked,")
P.add_argument("--body2", default="embedded and searchable, and keep them tidy at scale.")
P.add_argument("--cta", default="See my work")
P.add_argument("--tiles", default="Py,JS,TS,S3,SQL,Git,AI,{ }",
               help="comma-separated labels for the orbiting tiles")
P.add_argument("--avatar", default="assets/avatar.jpg")
P.add_argument("--out", default="assets/header.svg")
A = P.parse_args()

# ---- tokens ------------------------------------------------------------------
SPACE, NIGHT, VIOLET, LILAC, CYAN, MIST, DIM = (
    "#05030F", "#0E0826", "#7C3AED", "#C4B5FD", "#38BDF8", "#EDE9FE", "#9A93B8")
W, H = 1200, 600
OX, OY = 905, 340            # orbit centre (photo)
RX, RY, TILT = 228, 84, -14  # orbit radii and tilt in degrees
AV = 84                      # photo radius
FRAMES, DUR = 48, 26
FONT = '"Inter", "Segoe UI Variable Display", "Segoe UI", "SF Pro Display", "Helvetica Neue", Ubuntu, sans-serif'


def avatar_href():
    try:
        if A.avatar == "github":
            req = urllib.request.Request(f"https://github.com/{A.user}.png?size=320",
                                         headers={"User-Agent": "profile-header"})
            with urllib.request.urlopen(req, timeout=20) as r:
                raw, mime = r.read(), r.headers.get_content_type() or "image/png"
        else:
            raw = open(A.avatar, "rb").read()
            mime = mimetypes.guess_type(A.avatar)[0] or "image/jpeg"
        return f"data:{mime};base64,{base64.b64encode(raw).decode()}"
    except Exception as e:
        print("avatar unavailable, using monogram:", e)
        return None


f1 = lambda v: (lambda s: s[:-2] if s.endswith(".0") else s)(f"{v:.1f}")
ANG = [2 * math.pi * f / FRAMES for f in range(FRAMES + 1)]

# ---- stars -------------------------------------------------------------------
rnd = random.Random(7)
stars = []
for i in range(170):
    x, y = rnd.uniform(0, W), rnd.uniform(0, H)
    r = rnd.choice([0.6, 0.7, 0.8, 1.0, 1.3])
    o = rnd.uniform(0.25, 0.8)
    tw = ""
    if i % 6 == 0:
        d = rnd.uniform(2.5, 6)
        tw = (f'<animate attributeName="opacity" values="{o:.2f};0.08;{o:.2f}" dur="{d:.1f}s" '
              f'begin="{rnd.uniform(0, 4):.1f}s" repeatCount="indefinite"/>')
    stars.append(f'<circle cx="{f1(x)}" cy="{f1(y)}" r="{r}" fill="#fff" opacity="{o:.2f}">{tw}</circle>')

# ---- orbit grid (static, like an instrument dial) -----------------------------
grid = []
for rr in (110, 175, 245, 310):
    grid.append(f'<circle cx="{OX}" cy="{OY}" r="{rr}" fill="none" stroke="{LILAC}" stroke-opacity="0.08"/>')
for k in range(8):
    a = math.pi * k / 8
    grid.append(f'<line x1="{f1(OX + 320*math.cos(a))}" y1="{f1(OY + 320*math.sin(a))}" '
                f'x2="{f1(OX - 320*math.cos(a))}" y2="{f1(OY - 320*math.sin(a))}" stroke="{LILAC}" stroke-opacity="0.06"/>')
orbit_ring = (f'<ellipse cx="{OX}" cy="{OY}" rx="{RX}" ry="{RY}" fill="none" stroke="{LILAC}" '
              f'stroke-opacity="0.28" stroke-dasharray="2 6" transform="rotate({TILT} {OX} {OY})"/>')

# ---- orbiting tiles ----------------------------------------------------------
labels = [t.strip() for t in A.tiles.split(",") if t.strip()]
back, front = [], []
for i, lab in enumerate(labels):
    off = 2 * math.pi * i / len(labels)
    pos, scl, ob, of = [], [], [], []
    for a in ANG:
        t = a + off
        dx, dy = RX * math.cos(t), RY * math.sin(t)
        c, sn = math.cos(math.radians(TILT)), math.sin(math.radians(TILT))
        x, y = OX + dx * c - dy * sn, OY + dx * sn + dy * c
        depth = (math.sin(t) + 1) / 2                          # 0 back .. 1 front
        pos.append(f"{f1(x)} {f1(y)}")
        scl.append(f"{0.62 + 0.5 * depth:.3f}")
        front_side = math.sin(t) >= 0
        ob.append(f"{0 if front_side else 0.25 + 0.5 * depth:.2f}")
        of.append(f"{0.75 + 0.25 * depth if front_side else 0:.2f}")
    fs = 22 if len(lab) <= 2 else 17
    tile = (f'<rect x="-30" y="-30" width="60" height="60" rx="14" fill="{NIGHT}" fill-opacity="0.92" '
            f'stroke="{LILAC}" stroke-opacity="0.35"/>'
            f'<rect x="-29" y="-29" width="58" height="22" rx="13" fill="#fff" fill-opacity="0.05"/>'
            f'<text y="{fs*0.36:.1f}" text-anchor="middle" font-family=\'{FONT}\' font-size="{fs}" '
            f'font-weight="800" fill="{MIST}">{lab.replace("&", "&amp;")}</text>')
    for layer, ops in ((back, ob), (front, of)):
        layer.append(
            f'<g transform="translate({pos[0]})" opacity="{ops[0]}">'
            f'<animateTransform attributeName="transform" type="translate" dur="{DUR}s" repeatCount="indefinite" values="{";".join(pos)}"/>'
            f'<animate attributeName="opacity" dur="{DUR}s" repeatCount="indefinite" values="{";".join(ops)}"/>'
            f'<g transform="scale({scl[0]})"><animateTransform attributeName="transform" type="scale" dur="{DUR}s" '
            f'repeatCount="indefinite" values="{";".join(scl)}"/>{tile}</g></g>')

# ---- photo ---------------------------------------------------------------
href = avatar_href()
if href:
    face = (f'<image href="{href}" x="{OX-AV}" y="{OY-AV}" width="{2*AV}" height="{2*AV}" '
            f'clip-path="url(#av)" preserveAspectRatio="xMidYMid slice"/>')
else:
    ini = "".join(w[0] for w in A.name.split()[:2]).upper()
    face = (f'<circle cx="{OX}" cy="{OY}" r="{AV}" fill="{NIGHT}"/><text x="{OX}" y="{OY+17}" '
            f'text-anchor="middle" font-family=\'{FONT}\' font-size="48" font-weight="800" fill="{MIST}">{ini}</text>')

esc = lambda s: s.replace("&", "&amp;").replace("<", "&lt;")
TX = 80
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(A.name)}, {esc(A.badge)}">
<title>{esc(A.name)}</title>
<defs>
  <clipPath id="card"><rect width="{W}" height="{H}" rx="28"/></clipPath>
  <clipPath id="av"><circle cx="{OX}" cy="{OY}" r="{AV}"/></clipPath>
  <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{NIGHT}"/><stop offset="0.55" stop-color="{SPACE}"/>
  </linearGradient>
  <radialGradient id="haze" cx="0.5" cy="0" r="0.6">
    <stop offset="0" stop-color="{VIOLET}" stop-opacity="0.55"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="hot" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{VIOLET}" stop-opacity="0"/><stop offset="0.5" stop-color="#fff"/>
    <stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="word" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#A78BFA"/><stop offset="1" stop-color="{CYAN}"/>
  </linearGradient>
  <radialGradient id="halo" cx="0.5" cy="0.5" r="0.5">
    <stop offset="0.6" stop-color="{VIOLET}" stop-opacity="0.55"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/>
  </radialGradient>
  <filter id="b30" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="30"/></filter>
  <filter id="b10" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="9"/></filter>
  <filter id="b3" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2.5"/></filter>
  <style>
    .t {{ font-family: {FONT}; }}
    .in {{ opacity: 0; animation: in 1s ease-out .2s forwards; }}
    .d2 {{ animation-delay: .45s; }} .d3 {{ animation-delay: .7s; }} .d4 {{ animation-delay: .95s; }}
    @keyframes in {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: none; }} }}
    @media (prefers-reduced-motion: reduce) {{ .in {{ animation: none; opacity: 1; }} }}
  </style>
</defs>
<g clip-path="url(#card)">
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <rect width="{W}" height="{H}" fill="url(#haze)"/>
  <g>{"".join(stars)}</g>

  <!-- black hole hanging from the top edge -->
  <g transform="translate(600 46)">
    <ellipse cx="0" cy="70" rx="250" ry="120" fill="{VIOLET}" opacity="0.45" filter="url(#b30)">
      <animate attributeName="opacity" values="0.42;0.6;0.42" dur="6s" repeatCount="indefinite"/>
    </ellipse>
    <path d="M -210 0 C -170 30, -150 150, 0 150 C 150 150, 170 30, 210 0" fill="none" stroke="#A78BFA" stroke-width="34" opacity="0.55" filter="url(#b10)"/>
    <path d="M -150 0 C -125 22, -115 112, 0 112 C 115 112, 125 22, 150 0" fill="none" stroke="#DDD6FE" stroke-width="14" filter="url(#b3)"/>
    <path d="M -150 0 C -125 22, -115 112, 0 112 C 115 112, 125 22, 150 0" fill="none" stroke="#fff" stroke-width="3"/>
    <path d="M -110 0 C -90 16, -80 82, 0 82 C 80 82, 90 16, 110 0 Z" fill="{SPACE}"/>
    <path d="M -280 0 C -200 8, -170 30, -150 0 M 150 0 C 170 30, 200 8, 280 0" fill="none" stroke="#C4B5FD" stroke-width="2" opacity="0.6" filter="url(#b3)"/>
    <rect x="-420" y="-3" width="840" height="5" fill="url(#hot)" filter="url(#b3)"/>
  </g>

  <!-- name -->
  <g class="in">
    <circle cx="{TX+14}" cy="44" r="14" fill="none" stroke="{LILAC}" stroke-width="1.6"/>
    <circle cx="{TX+14}" cy="44" r="4" fill="{CYAN}"/>
    <text x="{TX+38}" y="50" class="t" font-size="18" font-weight="700" fill="{MIST}">{esc(A.name)}</text>
  </g>

  <!-- orbit -->
  <g>{"".join(grid)}</g>
  <g transform="rotate({TILT} {OX} {OY})">{orbit_ring}</g>
  <g>{"".join(back)}</g>
  <circle cx="{OX}" cy="{OY}" r="{AV+40}" fill="url(#halo)"/>
  <circle cx="{OX}" cy="{OY}" r="{AV+5}" fill="{SPACE}"/>
  {face}
  <circle cx="{OX}" cy="{OY}" r="{AV+3}" fill="none" stroke="{LILAC}" stroke-opacity="0.7" stroke-width="2"/>
  <g>{"".join(front)}</g>

  <!-- copy -->
  <g class="in d2">
    <rect x="{TX}" y="222" width="{len(A.badge)*6.9+52:.0f}" height="34" rx="17" fill="{VIOLET}" fill-opacity="0.12" stroke="{VIOLET}" stroke-opacity="0.7"/>
    <path d="M {TX+21} 230 l2.4 6.6 6.6 2.4 -6.6 2.4 -2.4 6.6 -2.4 -6.6 -6.6 -2.4 6.6 -2.4 z" fill="{LILAC}"/>
    <text x="{TX+38}" y="244" class="t" font-size="14" font-weight="500" fill="{MIST}">{esc(A.badge)}</text>
  </g>
  <g class="in d3 t" font-size="52" font-weight="600" letter-spacing="-1.3" fill="#fff">
    <text x="{TX-3}" y="322">{esc(A.head1)}</text>
    <text x="{TX-3}" y="384">{esc(A.head2a)} <tspan fill="url(#word)">{esc(A.head2b)}</tspan></text>
  </g>
  <g class="in d4">
    <text x="{TX}" y="432" class="t" font-size="17" fill="{DIM}">{esc(A.body1)}</text>
    <text x="{TX}" y="458" class="t" font-size="17" fill="{DIM}">{esc(A.body2)}</text>
    <rect x="{TX}" y="490" width="158" height="44" rx="10" fill="{VIOLET}" fill-opacity="0.35" stroke="{VIOLET}"/>
    <text x="{TX+79}" y="518" text-anchor="middle" class="t" font-size="16" font-weight="600" fill="#fff">{esc(A.cta)}</text>
  </g>
</g>
</svg>'''

with open(A.out, "w", encoding="utf-8") as fh:
    fh.write(svg)
print(f"wrote {A.out} ({len(svg)//1024} KB, photo={'yes' if href else 'monogram'})")
