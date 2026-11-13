"""Paper-and-ink profile cards, independently implemented for Antonio Potenza."""
import base64
from collections import defaultdict
from datetime import date, timedelta
from html import escape
import json
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
@keyframes grow{from{transform:scaleY(0)}to{transform:scaleY(1)}}
.rise{animation:rise .8s cubic-bezier(.2,.7,.2,1) both}
.pop{animation:pop .35s both;transform-box:fill-box;transform-origin:center}
.bar{animation:grow .8s both;transform-box:fill-box;transform-origin:bottom}
@media(prefers-reduced-motion:reduce){.rise,.pop,.bar{animation:none!important}.scan{display:none}}
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


def calendar(data):
    p=start(880,248,"Every day, in blue",f"Real GitHub contribution calendar for {data['username']}; updated {data['generated_at']}")
    p += [txt(42,57,"Every day,",34,family=SERIF),txt(169,57,"in blue",34,BLUE,SERIF,'font-style="italic"'),
          txt(838,53,"REFRESHED DAILY",10,MUTED,MONO,'text-anchor="end"')]
    days=data['days']
    first=date.fromisoformat(days[0]['date'])
    sunday=first-timedelta(days=(first.weekday()+1)%7)
    cols=((date.fromisoformat(days[-1]['date'])-sunday).days//7)+1
    step=796/cols
    palette=['#e2e2de','#cdd4ff','#a4b2ff','#7087ff',BLUE]
    labels=set()
    for d in days:
        day=date.fromisoformat(d['date'])
        col,row=divmod((day-sunday).days,7)
        x,y=44+col*step,90+row*15
        cell=rect(round(x,2),y,round(step-3,2),12,palette[d['level']],2,
                  f'class="pop" style="animation-delay:{col*.018+row*.035:.3f}s"')
        p.append(cell.removesuffix('/>')+f'><title>{d["date"]}: {d["count"]} contributions</title></rect>')
        month=(day.year,day.month)
        if month not in labels and day.day<=7 and col<cols-1:
            labels.add(month)
            p.append(txt(round(x,2),213,day.strftime('%b'),9,MUTED,MONO))
    p += [txt(670,232,'less',9,MUTED,MONO),txt(837,232,'more',9,MUTED,MONO,'text-anchor="end"')]
    for i,color in enumerate(palette):
        p.append(rect(707+i*17,223,12,10,color,2))
    write('heatmap.svg',p)


def activity(data):
    days,stats=data['days'],data['stats']
    months=defaultdict(int)
    for d in days:
        months[d['date'][:7]]+=d['count']
    months=list(sorted(months.items()))[-12:]
    maximum=max([count for _,count in months]+[1])
    best=max(days,key=lambda d:d['count'])
    p=start(880,338,"The last 12 months on GitHub",f"{stats['total']} contributions, {stats['current_streak']} day current streak, {stats['longest_streak']} day longest streak")
    p += [txt(40,53,"THE LAST 12 MONTHS ON GITHUB",11,MUTED,MONO),
          txt(38,109,f"{stats['total']:,}",50,family=SERIF),
          txt(100 if stats['total']<100 else 145,109,"contributions",50,family=SERIF,extra='font-style="italic"')]
    for i,(month,count) in enumerate(months):
        x=40+i*47.5
        h=138*count/maximum
        if count:
            p.append(rect(x,285-h,36,round(h,2),BLUE if count==maximum else INK,4,
                          f'class="bar" style="animation-delay:{i*.055:.3f}s"'))
        else:
            p.append(rect(x,283,36,2,RULE,1))
        p.append(txt(x+18,309,date.fromisoformat(month+'-01').strftime('%b'),10,MUTED,MONO,'text-anchor="middle"'))
        if count==maximum and count:
            p.append(txt(x+18,276-h,str(count),10,BLUE,MONO,'text-anchor="middle"'))
    p += [txt(648,95,str(stats['current_streak']),42,family=SERIF),txt(685,95,"day" if stats['current_streak']==1 else "days",42,family=SERIF,extra='font-style="italic"'),
          txt(649,119,f"current streak · longest {stats['longest_streak']}d",11,MUTED),
          rect(648,138,190,1,RULE),txt(648,184,f"{stats['active_days']} / {len(days)}",40,family=SERIF),
          txt(649,208,"days with a contribution",12,MUTED),rect(648,228,190,1,RULE),
          txt(648,272,best['count'],40,family=SERIF),txt(649,299,"on the busiest day",12,MUTED)]
    write('activity.svg',p)


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
        p=start(880,70,"What I'm building","Current projects and areas of work",background=None,gap=0)
        p += [txt(0,45,"What I'm",34,color,SERIF),txt(132,45,'building',34,color,SERIF,'font-style="italic"')]
        write('title-'+theme+'.svg',p)
    for index,(name,title,lines,stack,color) in enumerate([
        ('scada','SCADA & telemetry',['Compressor monitoring, alarms,','energy dashboards and industrial','time-series visualization.'],'Python · FastAPI · React',BLUE),
        ('data','Data & simulation',['Stochastic processes, epidemic','models, random graphs and','time-series forecasting.'],'NumPy · Pandas · Matplotlib',RED),
        ('profile','This GitHub profile',['Animated SVG artwork with a','daily calendar generated from','real GitHub contribution data.'],'Python · SVG · GitHub Actions',YELLOW)]):
        p=start(293.333,180,title,' '.join(lines),fonts=('sans','bold','mono'),background=None)
        p += [f'<g transform="translate({index*4},0)">',rect(0,0,285.333,180,PAPER,14),rect(24,27,8,8,color,1),txt(40,36,title,16,extra='font-weight="600"')]
        for i,line in enumerate(lines):
            p.append(txt(24,67+i*21,line,12,'#3a3a3c'))
        p.append(txt(24,155,stack,9,MUTED,MONO))
        p.append('</g>')
        write('project-'+name+'.svg',p)


def main():
    OUT.mkdir(exist_ok=True)
    profile=json.loads((ROOT/'profile.json').read_text())
    data=json.loads((ROOT/'data/contributions.json').read_text())
    if profile['username']!=data['username']:
        raise ValueError('Contribution account mismatch')
    hero(profile)
    calendar(data)
    activity(data)
    pillars()
    projects()
    print('Rendered 11 paper-and-ink profile cards')


if __name__=='__main__':
    main()
