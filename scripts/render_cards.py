"""Paper-and-ink profile cards, independently implemented for Antonio Potenza."""
import base64
from html import escape
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "cards"
PAPER, INK, MUTED, RULE = "#f3f3f1", "#111111", "#6e6e73", "#dcdcd7"
BLUE, RED, YELLOW = "#2f55ff", "#ef3b2d", "#ffc81a"
SERIF, SANS, MONO = "'Instrument Serif',Georgia,serif", "Geist,Arial,sans-serif", "'Geist Mono',Consolas,monospace"
FONTS = {"serif": ("Instrument Serif", "normal",400,"serif.woff"),
         "italic": ("Instrument Serif","italic",400,"serif-italic.woff"),
         "sans": ("Geist","normal",400,"sans.woff"),
         "bold": ("Geist","normal",600,"sans-bold.woff"),
         "mono": ("Geist Mono","normal",400,"mono.woff")}
CSS = """@keyframes rise{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}
@keyframes pop{from{opacity:0;transform:scale(.3)}to{opacity:1;transform:scale(1)}}
@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-3px)}}
.bob{animation:bob 3.6s ease-in-out infinite}
.rise{animation:rise .8s cubic-bezier(.2,.7,.2,1) both}
.pop{animation:pop .35s both;transform-box:fill-box;transform-origin:center}
@media(prefers-reduced-motion:reduce){.rise,.pop,.bob{animation:none!important}.scan{display:none}}
"""


def txt(x,y,value,size=14,color=INK,family=SANS,extra=""):
    return f'<text x="{x}" y="{y}" fill="{color}" font-family="{family}" font-size="{size}" {extra}>{escape(str(value))}</text>'


def rect(x,y,w,h,fill,rx=0,extra=""):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" {extra}/>'


def start(w,h,title,description,fonts=("serif","italic","sans","mono"),background=PAPER,gap=16):
    faces=[]
    for key in fonts:
        family,style,weight,filename=FONTS[key]
        b64=base64.b64encode((ROOT/"fonts"/filename).read_bytes()).decode()
        faces.append(f"@font-face{{font-family:'{family}';font-style:{style};font-weight:{weight};src:url(data:font/woff;base64,{b64}) format('woff')}}")
    p=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h+gap}" viewBox="0 0 {w} {h+gap}" role="img" aria-labelledby="title desc">',
       f'<title id="title">{escape(title)}</title><desc id="desc">{escape(description)}</desc>',
       '<style>'+''.join(faces)+CSS+'</style>']
    if background:
        p.append(rect(0,0,w,h,background,14))
    return p


def write(name,parts):
    (OUT/name).write_text('\n'.join(parts+['</svg>'])+'\n',encoding='utf-8')


def hero(profile):
    p=start(880,420,profile['name'],"Industrial Data & Automation. Student at Politecnico di Torino. ASCII portrait made from Antonio's cartoon photograph.")
    p += [rect(48,49,8,8,BLUE,2),txt(66,57,"INDUSTRIAL DATA & AUTOMATION",11,MUTED,MONO),
          '<g class="rise">',txt(44,185,"Antonio",108,family=SERIF),
          txt(44,287,"Potenza",108,family=SERIF,extra='font-style="italic"'),
          txt(45,337,"I turn machine data into real-time insights.",17),
          txt(45,364,"Automation, data engineering & SCADA.",17),
          txt(46,397,"Politecnico di Torino",12,MUTED,MONO),
          txt(251,397,"↗",14,BLUE),'</g>']
    lines=(ROOT/'data/portrait-ascii.txt').read_text().splitlines()
    x,y,width,height=538,46,300,336
    step=height/len(lines)
    p.append('<g aria-label="ASCII portrait of Antonio">')
    for i,line in enumerate(lines):
        p.append(txt(x, y+(i+1)*step,line,step*.88,"#414141",MONO,
                     f'xml:space="preserve" textLength="{width}" lengthAdjust="spacingAndGlyphs"'))
    p += ['</g>',f'<rect class="scan" x="{x-1}" y="{y-1}" width="{width+2}" height="0" fill="{PAPER}"><animate attributeName="y" from="{y-1}" to="{y+height+2}" dur="3.4s" fill="freeze"/><animate attributeName="height" from="{height+3}" to="0" dur="3.4s" fill="freeze"/></rect>']
    write('hero.svg',p)


def tool_icon(name, x, y, index):
    if name == 'timescale':
        return rect(x,y,38,38,'#ffdb36',10)+txt(x+19,y+26,'TS',17,INK,MONO,'text-anchor="middle"')
    raw=(ROOT/'assets/tool-icons'/f'{name}.svg').read_text(encoding='utf-8')
    for ident in re.findall(r'id="([^"]+)"',raw):
        raw=raw.replace(f'id="{ident}"',f'id="tool{index}-{ident}"').replace(f'#{ident})',f'#tool{index}-{ident})').replace(f'href="#{ident}"',f'href="#tool{index}-{ident}"')
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    root=ET.fromstring(raw)
    root.set('x',str(x))
    root.set('y',str(y))
    root.set('width','38')
    root.set('height','38')
    return ET.tostring(root,encoding='unicode')


def toolkit():
    tools=[
        ('python','Python','#3776ab'),('fastapi','FastAPI','#009688'),
        ('react','React','#149eca'),('docker','Docker','#2496ed'),
        ('postgresql','PostgreSQL','#4169e1'),('timescale','TimescaleDB','#c99b00'),
        ('numpy','NumPy','#4d77cf'),('pandas','Pandas','#150458'),
        ('matplotlib','Matplotlib','#11557c'),('c','C','#659ad2'),
        ('mysql','MySQL','#00758f'),('visualstudio','Visual Studio','#a65ce5')]
    p=start(880,436,'The tools behind the work',
            'Python, FastAPI, React, Docker, PostgreSQL, TimescaleDB, NumPy, Pandas, Matplotlib, C, MySQL and Visual Studio.',
            fonts=('serif','sans','bold','mono'),background=None)
    p += ['<defs><clipPath id="board-clip"><rect width="880" height="436" rx="14"/></clipPath>'
          '<pattern id="board-grid" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M32 0H0V32" fill="none" stroke="#87a2db" stroke-opacity=".13" stroke-width=".6"/></pattern></defs>',
          '<g clip-path="url(#board-clip)">',rect(0,0,880,436,'#101c36'),
          rect(0,0,880,436,'url(#board-grid)'),
          '<g fill="none" stroke="#7e9deb" stroke-opacity=".14">'
          '<circle cx="873" cy="-54" r="215"/><circle cx="873" cy="-54" r="270"/><circle cx="873" cy="-54" r="325"/></g>',
          txt(40,58,'The tools behind the work.',40,'#f6f7fb',SERIF),
          txt(42,87,'From machine data to the interface. This is my workbench.',13,'#aebcda')]
    p.append('<path d="M70 244H810" stroke="#5276c9" stroke-width="1.5" fill="none"/>')
    for col in range(6):
        center=100+col*136
        p += [f'<path d="M{center} 216V272" stroke="#5276c9" stroke-width="1.5"/>',
              f'<circle cx="{center}" cy="244" r="3" fill="#101c36" stroke="#86a5ff"/>']
    roles=['Code','APIs','Interfaces','Deployment','Database','Time series',
           'Arrays','Analysis','Charts','Systems','Database','IDE']
    for i,(icon,label,color) in enumerate(tools):
        x,y=40+(i%6)*136,116+(i//6)*134
        p += [f'<g class="rise" style="animation-delay:{i*.065:.3f}s">',
              rect(x+1,y+5,120,114,'#050c1d',14,extra='opacity=".5"'),
              rect(x,y,120,114,'#f6f8ff',14,extra='stroke="#ffffff" stroke-opacity=".5"'),
              f'<circle cx="{x+105}" cy="{y+17}" r="3" fill="{color}"/>',
              f'<g class="bob" style="animation-delay:{i*.21:.2f}s">',
              tool_icon(icon,x+41,y+23,i),'</g>',
              txt(x+60,y+83,label,11,INK,SANS,'text-anchor="middle" font-weight="600"'),
              txt(x+60,y+101,roles[i],9,'#6c7891',SANS,'text-anchor="middle"'),'</g>']
    p += [txt(440,408,'collect  →  process  →  serve  →  ship',12,'#a8bcff',MONO,'text-anchor="middle"'),'</g>']
    write('toolkit.svg',p)


def pillars():
    settings=[('automate',BLUE,'AUTOMATE','Machines.', ['SCADA systems, PLC programming', 'and real-time machine telemetry.'], '#ffffff'),
              ('analyze',RED,'ANALYZE','Data.', ['Time-series analysis, simulations', 'and predictive maintenance.'], '#ffffff'),
              ('build',YELLOW,'BUILD','Systems.', ['Python, FastAPI and React.', 'From data pipelines to dashboards.'], INK)]
    for index,(name,color,label,title,lines,ink) in enumerate(settings):
        p=start(293.333,252,label,title,fonts=('serif','italic','sans','mono'),background=None)
        p += [f'<g transform="translate({index*4},0)">',rect(0,0,285.333,252,color,14),txt(24,35,label,11,ink,MONO),txt(257,35,'↗',15,ink,extra='text-anchor="end"'),
              txt(23,111,title,49,ink,SERIF,'font-style="italic" class="rise"')]
        for i,line in enumerate(lines):
            p.append(txt(24,153+i*22,line,12,ink))
        p.append('</g>')
        write(name+'.svg',p)


def projects():
    for theme,color in [('dark','#f3f3f1'),('light',INK)]:
        p=start(880,108,"What I'm building","Current projects and areas of work",fonts=('serif','sans'),background=None,gap=0)
        p += [txt(0,53,"What I'm building",46,color,SERIF),
              txt(1,82,'From industrial signals to everyday software.',13,'#929caa' if theme=='dark' else MUTED)]
        write('title-'+theme+'.svg',p)
    for index,(name,title,lines,stack,color) in enumerate([
        ('scada','SCADA & telemetry',['Compressor monitoring, alarms,','energy dashboards and industrial','time-series visualization.'],'Python · FastAPI · React',BLUE),
        ('data','Data & simulation',['Stochastic processes, epidemic','models, random graphs and','time-series forecasting.'],'NumPy · Pandas · Matplotlib',RED),
        ('aptios','Aptios',['Business workflows, documents','and automations, brought','together in one workspace.'],'APT Systems · Business software',YELLOW)]):
        p=start(293.333,258,title,' '.join(lines),fonts=('sans','bold','mono'),background=None)
        p += [f'<g transform="translate({index*4},0)">',rect(0,0,285.333,258,PAPER,14),
              rect(24,22,36,3,color,1.5),
              rect(24,42,237,64,['#e5eaff','#fce8e4','#fff2bf'][index],9)]
        if name=='scada':
            p += ['<g fill="none" stroke="#2f55ff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
                  '<path d="M38 75H63L71 60L82 88L93 69L101 75H124M175 75H246"/>'
                  '<rect x="132" y="57" width="36" height="36" rx="7"/>'
                  '<path d="M142 67H158M142 75H152M142 83H158"/></g>']
        elif name=='data':
            p += ['<g fill="none" stroke="#ef3b2d" stroke-width="2" stroke-linecap="round">'
                  '<path d="M40 55V93H245" stroke-opacity=".25"/>'
                  '<path d="M45 88C80 88 85 60 116 71S155 92 181 66S220 70 244 55"/>'
                  '</g><g fill="#ef3b2d"><circle cx="62" cy="80" r="3"/>'
                  '<circle cx="112" cy="65" r="3"/><circle cx="162" cy="80" r="3"/>'
                  '<circle cx="204" cy="59" r="3"/><circle cx="237" cy="65" r="3"/></g>']
        else:
            p += ['<g fill="none" stroke="#927000" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">'
                  '<rect x="42" y="54" width="31" height="40" rx="4"/>'
                  '<path d="M50 64H65M50 72H65M50 80H60M81 74H112M104 68L112 74L104 80"/>'
                  '<rect x="123" y="57" width="44" height="34" rx="5"/>'
                  '<path d="M133 68H157M133 78H150M176 74H205M197 68L205 74L197 80"/>'
                  '<circle cx="228" cy="74" r="16"/><path d="M221 74L226 79L236 68"/></g>']
        p += [txt(24,138,title,17,extra='font-weight="600"')]
        for i,line in enumerate(lines):
            p.append(txt(24,165+i*20,line,12,'#3a3a3c'))
        p += [rect(24,225,237,1,RULE),txt(24,245,stack,9,MUTED,MONO)]
        p.append('</g>')
        write('project-'+name+'.svg',p)


def main():
    OUT.mkdir(exist_ok=True)
    profile=json.loads((ROOT/'profile.json').read_text())
    hero(profile)
    toolkit()
    pillars()
    projects()
    print('Rendered 10 paper-and-ink profile cards')


if __name__=='__main__':
    main()
