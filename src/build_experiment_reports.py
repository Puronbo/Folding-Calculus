#!/usr/bin/env python3
"""Extract experiment chapters (4-8) from THE_BOOK_OF_PUNO.md into standalone PDFs."""

import re, os
from fpdf import FPDF

PDF_W, PDF_H = 210, 297
MARGIN = 28
BODY_W = PDF_W - 2 * MARGIN

with open('THE_BOOK_OF_PUNO.md', 'r', encoding='utf-8') as f:
    lines = f.read().split('\n')

# Find chapter boundaries
chapter_bounds = {}
current_ch = None
current_start = None

for i, line in enumerate(lines):
    m = re.match(r'^## (Chapter \d+: .+)$', line)
    if m:
        if current_ch:
            chapter_bounds[current_ch] = (current_start, i)
        current_ch = m.group(1)
        current_start = i
    m2 = re.match(r'^# Part\s+\w+:', line)
    if m2 and current_ch and current_start:
        chapter_bounds[current_ch] = (current_start, i)
        current_ch = None
        current_start = None

if current_ch and current_start:
    chapter_bounds[current_ch] = (current_start, len(lines))

exp_chapters = {k: v for k, v in chapter_bounds.items()
                if any(k.startswith(f'Chapter {n}:') for n in ['4', '5', '6', '7', '8'])}

short_names = {
    'Chapter 4: Crease-Aware Subgradient Selection (Experiment 1)': 'exp1_crease_subgradient',
    'Chapter 5: Crease Density and Decision Boundary Complexity (Experiment 2)': 'exp2_crease_density',
    'Chapter 6: Crease Stabilization and Early Stopping (Experiment 3)': 'exp3_early_stop',
    'Chapter 7: OOD Detection via Crease Ambiguity (Experiment 4)': 'exp4_ood_detection',
    'Chapter 8: Pruning via Crease Proximity (Experiment 5)': 'exp5_crease_pruning',
}

class ReportPDF(FPDF):
    def footer(self):
        n = self.page_no()
        if n <= 1:
            return
        self.set_y(-16)
        self.set_font('Body', '', 8)
        self.set_text_color(150, 135, 115)
        self.set_draw_color(200, 190, 170)
        self.set_line_width(0.2)
        self.line(MARGIN, self.get_y() - 1, PDF_W - MARGIN, self.get_y() - 1)
        self.cell(0, 6, f'\u2014 {n} \u2014', align='C')

for ch_name, (start, end) in exp_chapters.items():
    slug = short_names.get(ch_name, f'ch{ch_name.split(":")[0].split()[-1]}')
    filename = f'REPORT_{slug}.pdf'
    print(f'Building {filename} ... ', end='', flush=True)

    chapter_lines = lines[start:end]

    # Separate title from rest
    title_line = ''
    body_start = 0
    for j, l in enumerate(chapter_lines):
        if l.startswith('## '):
            title_line = l.replace('## ', '').strip()
            body_start = j + 1
            break

    pdf = ReportPDF(unit='mm')
    pdf.add_font('Body', '', 'C:/Windows/Fonts/calibri.ttf')
    pdf.add_font('Body', 'B', 'C:/Windows/Fonts/calibrib.ttf')
    pdf.add_font('Body', 'I', 'C:/Windows/Fonts/calibrii.ttf')
    pdf.add_font('Title', 'B', 'C:/Windows/Fonts/cambriab.ttf')
    pdf.add_font('Mono', '', 'C:/Windows/Fonts/consola.ttf')

    def add_bg():
        pdf.set_fill_color(253, 249, 240)
        pdf.rect(0, 0, PDF_W, PDF_H, 'F')

    def chk(h):
        if pdf.get_y() + h > PDF_H - 25:
            pdf.add_page()
            add_bg()

    # Cover
    pdf.add_page()
    add_bg()
    pdf.set_draw_color(160, 120, 60)
    pdf.set_line_width(0.5)
    y_mid = PDF_H / 2 - 20
    pdf.line(MARGIN, y_mid - 20, PDF_W - MARGIN, y_mid - 20)
    pdf.set_font('Title', 'B', 22)
    pdf.set_text_color(35, 25, 15)
    pdf.set_y(y_mid - 14)
    pdf.multi_cell(0, 12, title_line, align='C')
    pdf.set_font('Body', 'I', 11)
    pdf.set_text_color(100, 85, 65)
    pdf.set_y(y_mid + 8)
    pdf.cell(0, 7, 'A Technical Report from the Puno Calculus Research Program', align='C', new_x='LMARGIN', new_y='NEXT')
    pdf.set_font('Body', '', 9)
    pdf.set_y(y_mid + 18)
    pdf.cell(0, 6, 'Michael Grafiel Sayson Puno  |  July 2026', align='C', new_x='LMARGIN', new_y='NEXT')
    pdf.line(MARGIN, y_mid + 30, PDF_W - MARGIN, y_mid + 30)

    # Render body content
    in_code = False
    code_buf = []

    def flush_code():
        if code_buf:
            chk(6)
            pdf.set_font('Body', '', 8.5)
            pdf.set_text_color(80, 70, 60)
            for cl in code_buf:
                pdf.set_x(MARGIN + 8)
                pdf.write(4.5, cl)
                pdf.ln(4.5)
            pdf.ln(1)
            code_buf.clear()

    def render_inline(text, size=11, color=(50, 40, 30)):
        text = re.sub(r'\*\*(.+?)\*\*', r'[b]\1[/b]', text)
        text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'[i]\1[/i]', text)
        parts = re.split(r'(\[/?[bi]\])', text)
        pdf.set_font('Body', '', size)
        pdf.set_text_color(*color)
        for part in parts:
            if part == '[b]':
                pdf.set_font('Body', 'B', size)
            elif part == '[/b]':
                pdf.set_font('Body', '', size)
            elif part == '[i]':
                pdf.set_font('Body', 'I', size)
            elif part == '[/i]':
                pdf.set_font('Body', '', size)
            else:
                pdf.write(5.5, part)

    i = body_start
    while i < len(chapter_lines):
        line = chapter_lines[i].rstrip()

        if not line.strip():
            i += 1
            continue

        # Code block
        if line.startswith('```'):
            if in_code:
                flush_code()
                in_code = False
            else:
                flush_code()
                in_code = True
            i += 1
            continue
        if in_code:
            code_buf.append(line)
            i += 1
            continue

        flush_code()

        # Sub-heading
        m = re.match(r'^### (.+)', line)
        if m:
            chk(12)
            pdf.set_font('Body', 'B', 12)
            pdf.set_text_color(75, 55, 35)
            pdf.ln(2)
            pdf.cell(0, 8, m.group(1).strip(), new_x='LMARGIN', new_y='NEXT')
            pdf.ln(1)
            i += 1
            continue

        # Sub-sub-heading
        m = re.match(r'^#### (.+)', line)
        if m:
            chk(10)
            pdf.set_font('Body', 'B', 11)
            pdf.set_text_color(80, 60, 40)
            pdf.ln(1)
            pdf.cell(0, 7, m.group(1).strip(), new_x='LMARGIN', new_y='NEXT')
            pdf.ln(1)
            i += 1
            continue

        # Horizontal rule
        if re.match(r'^-{3,}$', line.strip()):
            chk(6)
            pdf.set_draw_color(180, 160, 130)
            pdf.set_line_width(0.3)
            y = pdf.get_y()
            pdf.line(MARGIN, y + 1, PDF_W - MARGIN, y + 1)
            pdf.ln(5)
            i += 1
            continue

        # Blockquote
        if line.strip().startswith('> '):
            qlines = []
            while i < len(chapter_lines) and chapter_lines[i].strip().startswith('> '):
                qlines.append(chapter_lines[i].strip()[2:])
                i += 1
            chk(10)
            pdf.set_font('Body', 'I', 10.5)
            pdf.set_text_color(80, 70, 60)
            pdf.set_x(MARGIN + 8)
            pdf.multi_cell(BODY_W - 16, 5.5, ' '.join(qlines))
            pdf.ln(2)
            continue

        # Table: collect all consecutive table rows
        if line.strip().startswith('|'):
            rows = []
            while i < len(chapter_lines) and chapter_lines[i].strip().startswith('|'):
                rows.append(chapter_lines[i].strip())
                i += 1
            if len(rows) >= 2:
                chk(12)
                headers = [h.strip() for h in rows[0].split('|') if h.strip()]
                data_rows = rows[2:] if len(rows) > 2 else []
                n_cols = len(headers)
                col_w = BODY_W / n_cols
                pdf.set_font('Body', 'B', 9)
                pdf.set_text_color(50, 40, 30)
                pdf.set_fill_color(240, 234, 222)
                x0 = MARGIN
                for j, h in enumerate(headers):
                    pdf.set_x(x0 + j * col_w)
                    pdf.cell(col_w, 6, h, border=0, fill=True)
                pdf.ln(6)
                pdf.set_font('Body', '', 9)
                pdf.set_text_color(60, 50, 40)
                for row in data_rows:
                    cells = [c.strip() for c in row.split('|') if c.strip()]
                    for j, c in enumerate(cells):
                        if j >= n_cols:
                            break
                        pdf.set_x(x0 + j * col_w)
                        pdf.cell(col_w, 5.5, c, border=0)
                    pdf.ln(5.5)
                pdf.ln(2)
            continue

        # Bullet list
        if line.strip().startswith('- ') or line.strip().startswith('* '):
            while i < len(chapter_lines) and (chapter_lines[i].strip().startswith('- ') or chapter_lines[i].strip().startswith('* ')):
                t = chapter_lines[i].strip()
                text = t[2:] if t.startswith('- ') else t[2:]
                chk(7)
                pdf.set_x(MARGIN + 5)
                pdf.write(5.5, '\u2022 ')
                render_inline(text, 10.5)
                pdf.ln(5.5)
                i += 1
            continue

        # Regular paragraph: collect consecutive non-empty, non-special lines
        para_lines = [line.strip()]
        i += 1
        while i < len(chapter_lines) and chapter_lines[i].strip() and not chapter_lines[i].strip().startswith('#') and not chapter_lines[i].strip().startswith('|') and not chapter_lines[i].strip().startswith('- ') and not chapter_lines[i].strip().startswith('* ') and not chapter_lines[i].strip().startswith('> ') and not re.match(r'^-{3,}$', chapter_lines[i].strip()) and not chapter_lines[i].strip().startswith('```'):
            para_lines.append(chapter_lines[i].strip())
            i += 1
        full_text = ' '.join(para_lines)
        chk(8)
        pdf.set_x(MARGIN)
        render_inline(full_text, 11)
        pdf.ln(5.5)

    flush_code()
    pdf.output(filename)
    print(f'done ({pdf.pages_count} pages)')

print('\nAll experiment reports built.')
