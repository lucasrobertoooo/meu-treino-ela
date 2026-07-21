#!/usr/bin/env python3
"""Gera _revisao-fotos.html a partir do index.html (fonte da verdade). Rodar: python3 _gerar-revisao.py"""
import re, html, os
src = open('index.html', encoding='utf-8').read()
def block(m):
    i = src.index(m); return src[i:src.index("\n};", i)]
wk, casa = block('let WK = {'), block('const WK_CASA = {')
photo = dict(re.findall(r'^\s*"([^"]+)"\s*:\s*"([^"]+)"\s*,', block('const PHOTO_LOCAL = {'), re.M))
EXRE = re.compile(r'\{id:"([^"]+)",\s*n:"([^"]+)",\s*s:(\d+),\s*r:"([^"]+)",\s*t:"([^"]+)"')
DAYRE = re.compile(r'\n  ([ABCD]):\{name:"([^"]+)",\s*focus:"([^"]+)"')
def parse(b):
    days=[]; marks=[(m.start(),m.group(1),m.group(2),m.group(3)) for m in DAYRE.finditer(b)]
    for k,(pos,key,name,focus) in enumerate(marks):
        end = marks[k+1][0] if k+1<len(marks) else len(b)
        days.append(dict(key=key,name=name,focus=focus,
                         ex=[dict(id=i,n=n,s=int(s),r=r,t=t) for i,n,s,r,t in EXRE.findall(b[pos:end])]))
    return days
gym, hom = parse(wk), parse(casa)
TIPO={"comp":("composto","#b3122a"),"iso":("isolador","#8b7378"),"core":("core","#6b21a8"),"cardio":("cardio","#0f766e")}
faltando={}; usadas={}
def card(e,dia):
    f=photo.get(e['n']); tl,tc=TIPO.get(e['t'],(e['t'],"#8b7378"))
    if f:
        usadas.setdefault(f,[]).append(e['n']); ok=os.path.exists(os.path.join('img',f))
        img=(f'<img src="img/{html.escape(f)}" alt="" loading="lazy">' if ok else
             '<div class="nophoto broke">arquivo não encontrado<br><b>'+html.escape(f)+'</b></div>')
        tag=(f'<div class="fname">{html.escape(f)}</div>' if ok else '<div class="fname err">QUEBRADA</div>')
    else:
        faltando.setdefault(e['n'],[]).append(dia)
        img='<div class="nophoto">📷<br>sem foto</div>'; tag='<div class="fname err">SEM FOTO</div>'
    return (f'<div class="card{"" if f else " miss"}"><div class="ph">{img}</div><div class="body">'
            f'<div class="nm">{html.escape(e["n"])}</div><div class="meta">'
            f'<span class="pill" style="background:{tc}">{tl}</span> {e["s"]}×{html.escape(e["r"])}</div>{tag}</div></div>')
def section(days,titulo,sub,pref):
    out=[f'<h2 class="sec">{titulo} <span class="secsub">{sub}</span></h2>']
    for d in days:
        out.append(f'<div class="day"><div class="dh"><span class="dk">{d["key"]}</span>'
                   f'<span class="dn">{html.escape(d["name"])}</span><span class="df">{html.escape(d["focus"])}</span>'
                   f'<span class="dc">{len(d["ex"])} exercícios</span></div><div class="grid">')
        out += [card(e,f'{pref}{d["key"]}') for e in d['ex']]
        out.append('</div></div>')
    return "\n".join(out)
body_gym, body_casa = section(gym,"🏋️ Academia","o treino principal dela",""), section(hom,"🏠 Casa","plano B quando não dá pra ir","casa ")
tot=sum(len(d['ex']) for d in gym+hom); nmiss=sum(len(v) for v in faltando.values())
falt="".join(f'<li><b>{html.escape(n)}</b> <span class="dias">{" · ".join(ds)}</span></li>'
             for n,ds in sorted(faltando.items(), key=lambda kv:-len(kv[1])))
reuso="".join(f'<li><code>{html.escape(f)}</code> <span class="dias">→ {len(set(ns))} exercícios: {html.escape(", ".join(sorted(set(ns))))}</span></li>'
              for f,ns in sorted(usadas.items(), key=lambda kv:-len(set(kv[1]))) if len(set(ns))>1)
orfas=sorted(set(os.listdir('img'))-set(usadas.keys()))
orf="".join(f'<li><code>{html.escape(o)}</code></li>' for o in orfas) or '<li class="ok">nenhuma</li>'
doc=f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Revisão de fotos · Treino da Pri</title><style>
:root{{--bg:#f6ebeb;--paper:#fff;--ink:#1c1518;--muted:#8b7378;--line:#ead2d3;--red:#b3122a}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",system-ui,sans-serif;line-height:1.5}}
.wrap{{max-width:1180px;margin:0 auto;padding:0 20px 80px}}header{{text-align:center;padding:34px 0 8px}}
h1{{margin:6px 0;font-size:27px;letter-spacing:-.02em}}.sub{{color:var(--muted);margin:0}}
.stats{{display:flex;gap:12px;justify-content:center;flex-wrap:wrap;margin:22px 0 8px}}
.stat{{background:var(--paper);border:1px solid var(--line);border-radius:14px;padding:12px 20px;text-align:center;min-width:118px}}
.stat b{{display:block;font-size:26px;line-height:1.1;color:var(--red)}}.stat span{{font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.04em}}
.sec{{margin:40px 0 4px;font-size:21px;border-bottom:2px solid var(--line);padding-bottom:8px}}.secsub{{font-size:13px;color:var(--muted);font-weight:400}}
.day{{margin:22px 0}}.dh{{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:10px}}
.dk{{background:var(--red);color:#fff;width:30px;height:30px;border-radius:9px;display:flex;align-items:center;justify-content:center;font-weight:800}}
.dn{{font-weight:800}}.df{{color:var(--muted);font-size:14px}}.dc{{margin-left:auto;font-size:12px;color:var(--muted)}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:14px}}
.card{{background:var(--paper);border:1px solid var(--line);border-radius:14px;overflow:hidden;display:flex;flex-direction:column}}
.card.miss{{border-color:#f0a5b0;box-shadow:0 0 0 2px #fde8ec inset}}
.ph{{aspect-ratio:4/3;background:#fbf3f3;overflow:hidden;display:flex;align-items:center;justify-content:center}}
.ph img{{width:100%;height:100%;object-fit:cover;display:block}}
.nophoto{{color:#c99;font-size:13px;text-align:center;font-weight:700;line-height:1.6}}.nophoto.broke{{color:var(--red);font-size:11px;padding:6px}}
.body{{padding:10px 12px 12px}}.nm{{font-weight:700;font-size:14px;line-height:1.3}}
.meta{{margin-top:6px;font-size:12px;color:var(--muted);display:flex;align-items:center;gap:6px}}
.pill{{color:#fff;border-radius:20px;padding:1px 8px;font-size:10.5px;font-weight:800;text-transform:uppercase}}
.fname{{margin-top:7px;font-size:10.5px;color:#b6a0a4;font-family:ui-monospace,Menlo,monospace;word-break:break-all}}
.fname.err{{color:var(--red);font-weight:800;font-family:inherit;letter-spacing:.04em}}
.panel{{background:var(--paper);border:1px solid var(--line);border-radius:16px;padding:18px 22px;margin-top:18px}}
.panel h3{{margin:0 0 10px;font-size:16px}}.panel ul{{margin:0;padding-left:20px}}.panel li{{margin:7px 0;font-size:14.5px}}
.dias{{color:var(--muted);font-size:12.5px}}code{{background:#fbf3f3;border:1px solid var(--line);border-radius:5px;padding:1px 6px;font-size:12.5px}}
.ok{{color:#16a34a}}.note{{background:#fbf1de;border:1px solid #eecf96;border-radius:12px;padding:12px 16px;margin-top:14px;font-size:14px}}
</style></head><body><div class="wrap">
<header><div style="font-size:38px">📷</div><h1>Revisão de fotos do treino</h1>
<p class="sub">Todos os exercícios que ela vê hoje no app — com a foto que aparece em cada um.</p></header>
<div class="stats"><div class="stat"><b>{tot}</b><span>em uso</span></div><div class="stat"><b>{tot-nmiss}</b><span>com foto</span></div>
<div class="stat"><b>{nmiss}</b><span>sem foto</span></div><div class="stat"><b>{len(faltando)}</b><span>fotos a buscar</span></div></div>
<div class="panel"><h3>🎯 O que falta ({len(faltando)} fotos resolvem {nmiss} lugares)</h3><ul>{falt}</ul>
<div class="note">Procure fotos <b>femininas</b>, fundo simples, mostrando a posição. Salve em <code>img/</code> e me diga o nome — eu ligo no app.</div></div>
<div class="panel"><h3>♻️ Fotos reaproveitadas (mesma imagem em vários exercícios)</h3><ul>{reuso or '<li class="ok">nenhuma</li>'}</ul>
<div class="note">Não é erro — mas se alguma ficou <b>estranha</b> pro exercício, me avisa que eu troco.</div></div>
<div class="panel"><h3>🗑️ Fotos no acervo que não são mais usadas</h3><ul>{orf}</ul></div>
{body_gym}
{body_casa}
<p style="text-align:center;color:#b6a0a4;font-size:12px;margin-top:36px">Meu Treino · gerado direto do código do app</p>
</div></body></html>'''
open('_revisao-fotos.html','w',encoding='utf-8').write(doc)
print(f"em uso {tot} | sem foto {nmiss} | fotos a buscar {len(faltando)}")
