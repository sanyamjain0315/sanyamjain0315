from base64 import b64encode
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
painting = b64encode((ASSETS / "aivazovsky-1858.jpeg").read_bytes()).decode()

MOTION = """
  :root {
    --ease-out: cubic-bezier(.23, 1, .32, 1);
    --ease-in-out: cubic-bezier(.45, 0, .55, 1);
  }
  .title { fill: var(--ink); font-family: Georgia, 'Times New Roman', serif; }
  .label { fill: var(--muted); font-family: Arial, Helvetica, sans-serif; }
  .thread { fill: none; stroke: var(--gold); stroke-width: 1.3; }
  @media (max-width: 600px) {
    .name { font-size: 108px; }
    .role { font-size: 30px; }
    .study { display: none; }
    .credit { font-size: 24px; }
  }
  @media (prefers-reduced-motion: no-preference) {
    .name { animation: arrive 1.8s var(--ease-out) both; }
    .role { animation: arrive 1.8s .18s var(--ease-out) both; }
    .study { animation: arrive 1.8s .36s var(--ease-out) both; }
    .thread { animation: unspool 2.4s .25s var(--ease-out) both; }
    .glint { animation: glint 14s var(--ease-in-out) infinite; }
    .swell { animation: swell 12s var(--ease-in-out) infinite alternate; }
  }
  @keyframes arrive {
    from { opacity: 0; transform: translateY(9px); }
    to { opacity: 1; transform: translateY(0); }
  }
  @keyframes unspool {
    from { stroke-dasharray: 0 1100; }
    to { stroke-dasharray: 1100 1100; }
  }
  @keyframes glint {
    0% { transform: translateX(-240px); opacity: 0; }
    15%, 80% { opacity: .65; }
    100% { transform: translateX(1100px); opacity: 0; }
  }
  @keyframes swell {
    from { transform: translateX(-25px); opacity: .35; }
    to { transform: translateX(25px); opacity: .65; }
  }
"""

for theme, ink, muted, gold in [
    ("light", "oklch(30% .045 230)", "oklch(45% .035 230)", "oklch(56% .065 85)"),
    ("dark", "oklch(91% .025 85)", "oklch(74% .025 200)", "oklch(73% .065 85)"),
]:
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 1100 1040" role="img" aria-labelledby="title desc">
  <title id="title">Sanyam Jain — Backend systems and local AI</title>
  <desc id="desc">The complete original painting Ship on a Stormy Sea, Ivan Aivazovsky, 1858. Only the surrounding typography and ornamental lines animate.</desc>
  <style>
    :root {{ --ink: {ink}; --muted: {muted}; --gold: {gold}; }}
    {MOTION}
  </style>
  <defs>
    <linearGradient id="gleam"><stop stop-color="{gold}" stop-opacity="0"/><stop offset=".5" stop-color="{gold}"/><stop offset="1" stop-color="{gold}" stop-opacity="0"/></linearGradient>
    <clipPath id="edge"><rect width="1100" height="1040"/></clipPath>
  </defs>
  <text class="title name" x="0" y="94" font-size="88" letter-spacing="-2">Sanyam Jain</text>
  <text class="label role" x="3" y="137" font-size="22" letter-spacing="2">BACKEND SYSTEMS · LOCAL AI</text>
  <text class="label study" x="1097" y="137" text-anchor="end" font-size="18">M.S. Computer Science · Boston University</text>
  <path class="thread" d="M0 169 H1100"/>
  <g clip-path="url(#edge)"><path class="glint" d="M0 169 H220" stroke="url(#gleam)" stroke-width="3"/></g>
  <image x="0" y="190" width="1100" height="776.66015625" preserveAspectRatio="xMidYMid meet" xlink:href="data:image/jpeg;base64,{painting}"/>
  <text class="label credit" x="0" y="1000" font-size="16" letter-spacing=".5">IVAN AIVAZOVSKY</text>
  <text class="title credit" x="1099" y="1000" text-anchor="end" font-size="19" font-style="italic">Ship on a Stormy Sea, 1858</text>
  <g clip-path="url(#edge)">
    <path class="swell" d="M-40 1025 C150 1018 250 1033 420 1025 S730 1017 900 1025 S1080 1033 1140 1025" fill="none" stroke="{gold}" stroke-width="1.2"/>
  </g>
</svg>
'''
    (ASSETS / f"header-{theme}.svg").write_text(svg)

(ASSETS / "current.svg").write_text('''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 44" role="presentation">
  <style>
    :root { --sea: oklch(61% .045 210); --gold: oklch(66% .06 85); --ease-in-out: cubic-bezier(.45,0,.55,1); }
    @media (prefers-reduced-motion: no-preference) {
      .near { animation: current 10s var(--ease-in-out) infinite alternate; }
      .far { animation: current 14s -5s var(--ease-in-out) infinite alternate-reverse; }
    }
    @keyframes current {
      from { transform: translateX(-32px); opacity: .35; }
      to { transform: translateX(32px); opacity: .7; }
    }
  </style>
  <defs><linearGradient id="fade"><stop stop-color="white" stop-opacity="0"/><stop offset=".2" stop-color="white"/><stop offset=".8" stop-color="white"/><stop offset="1" stop-color="white" stop-opacity="0"/></linearGradient><mask id="edges"><rect width="1100" height="44" fill="url(#fade)"/></mask></defs>
  <g mask="url(#edges)" fill="none" stroke-width="1.1">
    <path class="far" opacity=".5" stroke="var(--sea)" d="M-80 22 C90 5 210 39 380 22 S670 5 840 22 S1130 39 1220 22"/>
    <path class="near" opacity=".6" stroke="var(--gold)" d="M-80 24 C90 38 210 10 380 24 S670 38 840 24 S1130 10 1220 24"/>
  </g>
</svg>
''')
