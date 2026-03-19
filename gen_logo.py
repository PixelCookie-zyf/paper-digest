"""Generate a pixel-art SVG logo for Paper Digest."""

FONT = {
    'P': [
        "XXXX.",
        "X...X",
        "X...X",
        "XXXX.",
        "X....",
        "X....",
        "X....",
    ],
    'A': [
        ".XXX.",
        "X...X",
        "X...X",
        "XXXXX",
        "X...X",
        "X...X",
        "X...X",
    ],
    'E': [
        "XXXXX",
        "X....",
        "X....",
        "XXXX.",
        "X....",
        "X....",
        "XXXXX",
    ],
    'R': [
        "XXXX.",
        "X...X",
        "X...X",
        "XXXX.",
        "X.X..",
        "X..X.",
        "X...X",
    ],
    ' ': [
        "...",
        "...",
        "...",
        "...",
        "...",
        "...",
        "...",
    ],
    'D': [
        "XXXX.",
        "X...X",
        "X...X",
        "X...X",
        "X...X",
        "X...X",
        "XXXX.",
    ],
    'I': [
        "XXX",
        ".X.",
        ".X.",
        ".X.",
        ".X.",
        ".X.",
        "XXX",
    ],
    'G': [
        ".XXXX",
        "X....",
        "X....",
        "X.XXX",
        "X...X",
        "X...X",
        ".XXX.",
    ],
    'S': [
        ".XXXX",
        "X....",
        "X....",
        ".XXX.",
        "....X",
        "....X",
        "XXXX.",
    ],
    'T': [
        "XXXXX",
        "..X..",
        "..X..",
        "..X..",
        "..X..",
        "..X..",
        "..X..",
    ],
}

PIXEL = 10
GAP = 3
CHAR_GAP = 18
LINE_GAP = 24
CELL = PIXEL + GAP

COLORS = [
    "#22D3EE", "#06B6D4", "#0EA5E9", "#3B82F6",
    "#6366F1", "#8B5CF6", "#A855F7", "#C084FC",
    "#D946EF", "#EC4899", "#F472B6",
]


def interpolate_color(colors, t):
    idx = t * (len(colors) - 1)
    return colors[min(int(idx), len(colors) - 1)]


def render_text(text):
    pixels = []
    x_offset = 0
    total_cols = 0
    for ch in text:
        glyph = FONT.get(ch, FONT[' '])
        char_w = len(glyph[0])
        for row_idx, row in enumerate(glyph):
            for col_idx, cell in enumerate(row):
                if cell == 'X':
                    pixels.append((x_offset + col_idx, row_idx))
        total_cols = x_offset + char_w
        x_offset += char_w + (CHAR_GAP // CELL + 1)
    return pixels, total_cols


def generate_svg():
    line1, line2 = "PAPER", "DIGEST"
    pixels1, cols1 = render_text(line1)
    pixels2, cols2 = render_text(line2)
    max_cols = max(cols1, cols2)
    offset1 = (max_cols - cols1) / 2
    offset2 = (max_cols - cols2) / 2

    pad_x, pad_y = 60, 45
    text_w = max_cols * CELL
    text_h = 7 * CELL
    total_text_h = text_h * 2 + LINE_GAP

    chrome_h = 36
    subtitle_h = 56
    bottom_pad = 24

    svg_w = text_w + pad_x * 2
    svg_h = chrome_h + pad_y + total_text_h + subtitle_h + bottom_pad

    p = []
    p.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">')

    # Defs: glow filter + gradient for border
    p.append('  <defs>')
    p.append('    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">')
    p.append('      <feGaussianBlur in="SourceGraphic" stdDeviation="4" result="blur"/>')
    p.append('      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>')
    p.append('    </filter>')
    p.append(f'    <linearGradient id="border-grad" x1="0%" y1="0%" x2="100%" y2="100%">')
    p.append(f'      <stop offset="0%" stop-color="#22D3EE" stop-opacity="0.5"/>')
    p.append(f'      <stop offset="50%" stop-color="#8B5CF6" stop-opacity="0.5"/>')
    p.append(f'      <stop offset="100%" stop-color="#EC4899" stop-opacity="0.5"/>')
    p.append(f'    </linearGradient>')
    p.append('  </defs>')

    # Background with gradient border
    p.append(f'  <rect width="{svg_w}" height="{svg_h}" rx="16" fill="#0F172A"/>')
    p.append(f'  <rect width="{svg_w}" height="{svg_h}" rx="16" fill="none" stroke="url(#border-grad)" stroke-width="1.5"/>')

    # Window dots
    dot_y = 20
    for i, color in enumerate(["#EF4444", "#EAB308", "#22C55E"]):
        p.append(f'  <circle cx="{24 + i * 24}" cy="{dot_y}" r="7" fill="{color}"/>')

    # --- Pixel text ---
    base_y = chrome_h + pad_y // 2 + 5

    # Line 1: PAPER (with glow)
    p.append('  <g filter="url(#glow)">')
    for (px, py) in pixels1:
        x = pad_x + (offset1 + px) * CELL
        y = base_y + py * CELL
        t = (offset1 + px) / max_cols
        color = interpolate_color(COLORS, t)
        p.append(f'    <rect x="{x:.1f}" y="{y:.1f}" width="{PIXEL}" height="{PIXEL}" rx="2" fill="{color}"/>')
    p.append('  </g>')

    # Line 2: DIGEST (with glow)
    base_y2 = base_y + text_h + LINE_GAP
    p.append('  <g filter="url(#glow)">')
    for (px, py) in pixels2:
        x = pad_x + (offset2 + px) * CELL
        y = base_y2 + py * CELL
        t = (offset2 + px) / max_cols
        color = interpolate_color(COLORS, t)
        p.append(f'    <rect x="{x:.1f}" y="{y:.1f}" width="{PIXEL}" height="{PIXEL}" rx="2" fill="{color}"/>')
    p.append('  </g>')

    # Subtitle
    sub_y = base_y2 + text_h + subtitle_h - 8
    p.append(f'  <text x="{svg_w / 2}" y="{sub_y}" text-anchor="middle" '
             f'font-family="ui-monospace, SFMono-Regular, Menlo, monospace" '
             f'font-size="13" fill="#64748B" letter-spacing="4">'
             f'AI-POWERED PAPER READING PIPELINE</text>')

    p.append('</svg>')
    return '\n'.join(p)


if __name__ == '__main__':
    import os
    os.makedirs('assets', exist_ok=True)
    svg = generate_svg()
    with open('assets/logo.svg', 'w') as f:
        f.write(svg)
    print(f'Generated assets/logo.svg ({len(svg)} bytes)')
