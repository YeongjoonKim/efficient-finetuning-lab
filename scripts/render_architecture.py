"""Render reviewed architecture definitions as SVG and Mermaid using stdlib."""
import argparse
from html import escape
import json
from pathlib import Path
import textwrap

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'docs/architecture'

def render(spec):
    width = 1440
    height = 190 + len(spec['lanes']) * 215
    title = escape(spec['title'])
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
             f'<title id="title">{title}</title>',
             '<desc id="desc">'+escape(spec['scope']+'. '+spec['note'])+'</desc>',
             '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0L8 4L0 8" fill="#53808d"/></marker></defs>',
             f'<rect width="{width}" height="{height}" rx="18" fill="#f3f6fa"/>',
             '<g font-family="Arial, sans-serif">',
             f'<text x="40" y="52" font-size="32" font-weight="700" fill="#142b43">{title}</text>',
             f'<text x="40" y="87" font-size="19" fill="#536477">{escape(spec["scope"])}</text>']
    mmd = ['flowchart TB']
    colors = ['#18796e','#375c98','#7a5899']
    for row, lane in enumerate(spec['lanes']):
        y = 153 + row*215
        color = colors[row % len(colors)]
        parts.append(f'<text x="40" y="{y-22}" font-size="17" font-weight="700" fill="{color}">{escape(lane["title"])}</text>')
        mmd.append(f'  subgraph lane{row}["{lane["title"]}"]')
        mmd.append('    direction LR')
        count = len(lane['nodes'])
        bw = (1360-(count-1)*32)/count
        for col, node in enumerate(lane['nodes']):
            x = 40+col*(bw+32)
            nid = f'n{row}_{col}'
            if col and lane['serial']:
                parts.append(f'<path d="M{x-30} {y+67} H{x-5}" stroke="#53808d" stroke-width="2" fill="none" marker-end="url(#arrow)"/>')
            parts.append(f'<g data-node="{nid}"><rect x="{x}" y="{y}" width="{bw}" height="134" rx="10" fill="#fff" stroke="#c8d5df"/>')
            parts.append(f'<rect x="{x}" y="{y}" width="5" height="134" rx="2" fill="{color}"/>')
            lines = textwrap.wrap(node['title'],width=int((bw-38)/11))
            for index,line in enumerate(lines):
                parts.append(f'<text x="{x+19}" y="{y+32+index*25}" font-size="21" font-weight="700" fill="#17314b">{escape(line)}</text>')
            base = y+65+(len(lines)-1)*25
            for index,line in enumerate(node['lines']):
                parts.append(f'<text x="{x+19}" y="{base+index*24}" font-size="18" fill="#4a6075">{escape(line)}</text>')
            parts.append('</g>')
            label = '<br/>'.join([node['title']]+node['lines']).replace('"', "'")
            mmd.append(f'    {nid}["{label}"]')
        if lane['serial']:
            mmd.extend(f'    n{row}_{c} --> n{row}_{c+1}' for c in range(count-1))
        mmd.append('  end')
    for index,line in enumerate(textwrap.wrap(spec['note'],width=125)):
        parts.append(f'<text x="40" y="{height-46+index*24}" font-size="18" fill="#536477">{escape(line)}</text>')
    parts.extend(['</g>','</svg>'])
    return '\n'.join(parts)+'\n', '\n'.join(mmd)+'\n'

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    specs=json.loads((DIRECTORY/'diagrams.json').read_text())
    mismatches=[]
    for spec in specs:
        for extension,content in zip(['svg','mmd'],render(spec)):
            path=DIRECTORY/(spec['file']+'.'+extension)
            if args.check:
                if not path.exists() or path.read_text()!=content: mismatches.append(str(path.relative_to(ROOT)))
            else: path.write_text(content)
    print(json.dumps({'diagrams':len(specs),'mode':'check' if args.check else 'write','mismatches':mismatches}))
    return bool(mismatches)

if __name__=='__main__':
    raise SystemExit(main())
