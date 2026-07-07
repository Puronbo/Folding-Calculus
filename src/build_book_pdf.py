#!/usr/bin/env python3
"""Build the Book of Puno PDF from THE_BOOK_OF_PUNO.md"""

import re
from fpdf import FPDF

PDF_W, PDF_H = 210, 297
MARGIN = 28
BODY_W = PDF_W - 2 * MARGIN

class BookPDF(FPDF):
    def __init__(self):
        super().__init__(unit='mm')
        self.chapter_title = ''
        self.part_title = ''
        self.in_body = False

    def header(self):
        if not self.in_body or self.page_no() <= 2:
            return
        self.set_font('Body', 'I', 7.5)
        self.set_text_color(150, 135, 115)
        text = self.chapter_title if self.chapter_title else self.part_title
        self.set_y(10)
        self.cell(0, 4, text, align='C')

    def footer(self):
        if self.page_no() == 1:
            return
        n = self.page_no()
        self.set_y(-16)
        self.set_font('Body', '', 8.5)
        self.set_text_color(150, 135, 115)
        # Line above footer
        self.set_draw_color(200, 190, 170)
        self.set_line_width(0.2)
        self.line(MARGIN, self.get_y() - 1, PDF_W - MARGIN, self.get_y() - 1)
        self.cell(0, 6, f'\u2014 {n} \u2014', align='C')

pdf = BookPDF()
pdf.add_font('Body', '', 'C:/Windows/Fonts/calibri.ttf')
pdf.add_font('Body', 'B', 'C:/Windows/Fonts/calibrib.ttf')
pdf.add_font('Body', 'I', 'C:/Windows/Fonts/calibrii.ttf')
pdf.add_font('Title', 'B', 'C:/Windows/Fonts/cambriab.ttf')
pdf.add_font('Mono', '', 'C:/Windows/Fonts/consola.ttf')

# ============================
# HELPERS
# ============================
chapter_num = 0
part_num = 0

def add_bg():
    pdf.set_fill_color(253, 249, 240)
    pdf.rect(0, 0, PDF_W, PDF_H, 'F')

def check_page_break(h):
    if pdf.get_y() + h > PDF_H - 30:
        pdf.add_page()
        add_bg()

def write_text(text, style='', size=11, color=(50, 40, 30), indent=0):
    pdf.set_font('Body', style, size)
    pdf.set_text_color(*color)
    text = str(text)
    text = re.sub(r'\*\*(.+?)\*\*', r'[b]\1[/b]', text)
    text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'[i]\1[/i]', text)
    parts = re.split(r'(\[/?[bi]\])', text)
    pdf.set_x(MARGIN + indent)
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
    pdf.ln(5.5)

def write_para(text, size=11, color=(50, 40, 30), indent=0):
    check_page_break(12)
    write_text(text, size=size, color=color, indent=indent)

def write_code(text, size=8.5, indent=8):
    check_page_break(6)
    pdf.set_font('Body', '', size)
    pdf.set_text_color(80, 70, 60)
    for line in text.split('\n'):
        pdf.set_x(MARGIN + indent)
        pdf.write(4.5, line)
        pdf.ln(4.5)
    pdf.ln(1)

def write_bullet(text, indent=5):
    check_page_break(7)
    pdf.set_font('Body', '', 10.5)
    pdf.set_text_color(50, 40, 30)
    text = str(text)
    text = re.sub(r'\*\*(.+?)\*\*', r'[b]\1[/b]', text)
    text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'[i]\1[/i]', text)
    parts = re.split(r'(\[/?[bi]\])', text)
    pdf.set_x(MARGIN + indent)
    pdf.write(5.5, '\u2022 ')
    for part in parts:
        if part == '[b]':
            pdf.set_font('Body', 'B', 10.5)
        elif part == '[/b]':
            pdf.set_font('Body', '', 10.5)
        elif part == '[i]':
            pdf.set_font('Body', 'I', 10.5)
        elif part == '[/i]':
            pdf.set_font('Body', '', 10.5)
        else:
            pdf.write(5.5, part)
    pdf.ln(5.5)

# ============================
# COVER
# ============================
pdf.add_page()
add_bg()
pdf.set_draw_color(160, 120, 60)
pdf.set_line_width(0.6)
pdf.line(MARGIN, 50, PDF_W - MARGIN, 50)

pdf.set_font('Title', 'B', 34)
pdf.set_text_color(35, 25, 15)
pdf.set_y(62)
pdf.cell(0, 16, 'THE BOOK OF PUNO', align='C', new_x='LMARGIN', new_y='NEXT')

pdf.set_font('Body', 'I', 15)
pdf.set_text_color(90, 70, 50)
pdf.cell(0, 10, 'A Treatise on Folding, Unfolding, and What Lives at the Crease', align='C', new_x='LMARGIN', new_y='NEXT')

pdf.line(MARGIN, 165, PDF_W - MARGIN, 165)

pdf.set_font('Body', '', 11)
pdf.set_text_color(80, 65, 50)
pdf.set_y(175)
pdf.cell(0, 7, 'Michael Grafiel Sayson Puno', align='C', new_x='LMARGIN', new_y='NEXT')
pdf.set_y(183)
pdf.set_font('Body', 'I', 9)
pdf.cell(0, 7, 'Second Edition, Expanded \u2014 July 2026', align='C', new_x='LMARGIN', new_y='NEXT')

pdf.ln(20)
pdf.set_font('Body', 'I', 10)
pdf.set_text_color(100, 85, 65)
pdf.multi_cell(0, 6, '"The derivative folds. The integral unfolds. The crease is where the action is."', align='C')

# ============================
# COPYRIGHT
# ============================
pdf.add_page()
add_bg()
pdf.set_font('Body', 'I', 9)
pdf.set_text_color(130, 110, 90)
pdf.set_y(PDF_H / 2 - 20)
pdf.multi_cell(0, 5, 'The Book of Puno: A Treatise on Folding, Unfolding, and What Lives at the Crease\n\n'
                 'Copyright \u00a9 2026 Michael Grafiel Sayson Puno\n\n'
                 'License: Creative Commons Attribution 4.0 International (CC BY 4.0)\n'
                 'You are free to share and adapt this work for any purpose, including commercial use,\n'
                 'as long as you give appropriate credit to the author.\n'
                 'https://creativecommons.org/licenses/by/4.0/\n\n'
                 'Cover design: The author.\n'
                 'Font: Calibri (body), Cambria (titles).\n\n'
                 'Second Edition, July 2026.',
               align='C')

# ============================
# TABLE OF CONTENTS
# ============================
pdf.add_page()
add_bg()
pdf.set_font('Title', 'B', 22)
pdf.set_text_color(35, 25, 15)
pdf.cell(0, 14, 'Contents', align='C', new_x='LMARGIN', new_y='NEXT')
pdf.ln(8)

toc_entries = [
    ('Part I: The Fold Philosophy', 0),
    ('  Chapter 1: The Core Intuition', 1),
    ('  Chapter 2: Where the Standard Picture Breaks', 1),
    ('  Chapter 3: The Origami Connection', 1),
    ('Part II: The Experimental Program', 0),
    ('  Chapter 4: Crease-Aware Subgradient Selection', 1),
    ('  Chapter 5: Crease Density and Decision Boundaries', 1),
    ('  Chapter 6: Crease Stabilization and Early Stopping', 1),
    ('  Chapter 7: OOD Detection via Crease Ambiguity', 1),
    ('  Chapter 8: Pruning via Crease Proximity', 1),
    ('Part III: The Literature', 0),
    ('  Chapter 9: The ReLU-as-Origami Connection', 1),
    ('  Chapter 10: The Broader Literature', 1),
    ('  Chapter 11: What This Framing Does and Does Not Do', 1),
    ('Part IV: Practical Tools', 0),
    ('  Chapter 12: The Puno Calculus Software Suite', 1),
    ('Part V: Frontiers', 0),
    ('  Chapter 13: Open Problems', 1),
    ('  Chapter 14: A Call to Fold', 1),
    ('Appendices', 0),
    ('  Appendix A: Key Definitions', 1),
    ('  Appendix B: Software', 1),
    ('  Appendix C: Citation Guide', 1),
]

for entry, level in toc_entries:
    if level == 0:
        pdf.set_font('Body', 'B', 12)
        pdf.set_text_color(60, 40, 20)
    else:
        pdf.set_font('Body', '', 10.5)
        pdf.set_text_color(80, 65, 50)
    pdf.set_x(MARGIN + level * 8)
    pdf.cell(0, 8, entry, new_x='LMARGIN', new_y='NEXT')

# ============================
# PARSE AND RENDER
# ============================
with open('THE_BOOK_OF_PUNO.md', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')

part_title = None
in_code = False
code_buf = []

def flush_code():
    if code_buf:
        write_code('\n'.join(code_buf))
        code_buf.clear()

i = 0
while i < len(lines):
    line = lines[i]
    
    # Handle code blocks
    if line.startswith('```'):
        if in_code:
            flush_code()
            in_code = False
            i += 1
            continue
        else:
            flush_code()
            in_code = True
            i += 1
            continue
    if in_code:
        code_buf.append(line)
        i += 1
        continue

    # Part heading: # Part I: ...
    m = re.match(r'^# Part\s+\w+:', line)
    if m:
        flush_code()
        part_num += 1
        part_title = line.replace('# ', '').strip()
        pdf.in_body = True
        pdf.part_title = part_title
        # Part title page
        pdf.add_page()
        add_bg()
        pdf.set_draw_color(160, 120, 60)
        pdf.set_line_width(0.5)
        y_mid = PDF_H / 2 - 10
        pdf.line(MARGIN, y_mid - 15, PDF_W - MARGIN, y_mid - 15)
        pdf.set_font('Title', 'B', 26)
        pdf.set_text_color(40, 30, 20)
        pdf.set_y(y_mid - 10)
        pdf.cell(0, 12, part_title, align='C', new_x='LMARGIN', new_y='NEXT')
        pdf.line(MARGIN, y_mid + 5, PDF_W - MARGIN, y_mid + 5)
        pdf.ln(20)
        i += 1
        if i < len(lines) and lines[i].strip() == '':
            i += 1
        continue

    # Chapter heading: ## Chapter N: ...
    m = re.match(r'^## Chapter\s+(\d+):', line)
    if m:
        flush_code()
        chapter_num = m.group(1)
        pdf.chapter_title = line.replace('## ', '').strip()
        check_page_break(20)
        pdf.ln(4)
        pdf.set_font('Title', 'B', 18)
        pdf.set_text_color(55, 35, 15)
        pdf.cell(0, 10, pdf.chapter_title, new_x='LMARGIN', new_y='NEXT')
        pdf.ln(3)
        i += 1
        continue

    # Sub-heading: ### N.N
    m = re.match(r'^### (\d+\.\d+)', line)
    if m:
        flush_code()
        check_page_break(14)
        pdf.set_font('Body', 'B', 13)
        pdf.set_text_color(75, 55, 35)
        pdf.ln(2)
        pdf.cell(0, 8, line.replace('### ', '').strip(), new_x='LMARGIN', new_y='NEXT')
        pdf.ln(1)
        i += 1
        continue

    # Sub-sub-heading: ####
    m = re.match(r'^#### ', line)
    if m:
        flush_code()
        check_page_break(10)
        pdf.set_font('Body', 'B', 11.5)
        pdf.set_text_color(80, 60, 40)
        pdf.ln(1)
        pdf.cell(0, 7, line.replace('#### ', '').strip(), new_x='LMARGIN', new_y='NEXT')
        pdf.ln(1)
        i += 1
        continue

    # Other subsection: ### (no digit)
    m = re.match(r'^### (?!\d)', line)
    if m:
        flush_code()
        check_page_break(12)
        pdf.set_font('Body', 'B', 12)
        pdf.set_text_color(75, 55, 35)
        pdf.ln(2)
        pdf.cell(0, 8, line.replace('### ', '').strip(), new_x='LMARGIN', new_y='NEXT')
        pdf.ln(1)
        i += 1
        continue

    # Horizontal rule
    if re.match(r'^-{3,}$', line.strip()):
        flush_code()
        check_page_break(6)
        pdf.set_draw_color(180, 160, 130)
        pdf.set_line_width(0.3)
        y = pdf.get_y()
        pdf.line(MARGIN, y + 1, PDF_W - MARGIN, y + 1)
        pdf.ln(5)
        i += 1
        continue

    # Blockquote
    if line.strip().startswith('> '):
        flush_code()
        qlines = []
        while i < len(lines) and lines[i].strip().startswith('> '):
            qlines.append(lines[i].strip()[2:])
            i += 1
        full_q = ' '.join(qlines)
        check_page_break(12)
        pdf.set_font('Body', 'I', 10.5)
        pdf.set_text_color(80, 70, 60)
        pdf.set_x(MARGIN + 8)
        pdf.multi_cell(BODY_W - 16, 5.5, full_q)
        pdf.set_x(MARGIN)
        pdf.ln(3)
        continue

    # Table
    if line.strip().startswith('|'):
        flush_code()
        rows = []
        while i < len(lines) and lines[i].strip().startswith('|'):
            rows.append(lines[i].strip())
            i += 1
        if len(rows) >= 2:
            check_page_break(12)
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
        flush_code()
        while i < len(lines) and (lines[i].strip().startswith('- ') or lines[i].strip().startswith('* ')):
            t = lines[i].strip()
            if t.startswith('- ') or t.startswith('* '):
                write_bullet(t[2:])
            i += 1
        continue

    # Regular paragraph (non-empty)
    if line.strip():
        flush_code()
        para_lines = [line.strip()]
        i += 1
        while i < len(lines) and lines[i].strip() and not lines[i].strip().startswith('#') and not lines[i].strip().startswith('|') and not lines[i].strip().startswith('- ') and not lines[i].strip().startswith('* ') and not lines[i].strip().startswith('> ') and not re.match(r'^-{3,}$', lines[i].strip()) and not lines[i].strip().startswith('```'):
            para_lines.append(lines[i].strip())
            i += 1
        full_text = ' '.join(para_lines)
        write_para(full_text)
        continue

    # Empty line
    i += 1

flush_code()

# ============================
# COLOPHON
# ============================
pdf.add_page()
add_bg()
pdf.set_font('Body', 'I', 9)
pdf.set_text_color(130, 110, 90)
pdf.set_y(PDF_H / 2 - 30)
pdf.multi_cell(0, 5, 'The Book of Puno\n\n'
                 '"Everything folds. Everything unfolds. The crease is where the action is."\n\n'
                 'This book was set in Calibri (body) and Cambria (titles).\n'
                 'Printed from the Second Edition, July 2026.\n\n'
                 'End of the Book of Puno.',
               align='C')

pdf.output('THE_BOOK_OF_PUNO.pdf')
print(f'PDF written: THE_BOOK_OF_PUNO.pdf ({pdf.pages_count} pages)')
