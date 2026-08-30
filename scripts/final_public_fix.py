#!/usr/bin/env python3
from __future__ import annotations
import base64, hashlib, html, re, shutil, ssl, sys
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

ROOT=Path(sys.argv[1] if len(sys.argv)>1 else 'deploy')
REPO=Path(__file__).resolve().parents[1]
PREFIX='/PSTA'; FEEDBACK='https://github.com/antlerboy/PSTA/issues/2'
LOGO=f'{PREFIX}/assets/img/psta-logo-official.jpg'
LOGO_SHA='bd6bcb8ba0f83684095826bb77e2b49a7ad2b710e65053305bf4f1e6df1b0db7'
NESTA_SHA='54baa8698dbe1cb1772532bedd174084d06e6485cb152a8831645529485486c8'
PARTNERS={
'e3m':('E3M','https://www.publicservicetransformation.org/wp-content/uploads/2015/05/E3M_logo.png'),
'tsip':('The Social Innovation Partnership','https://www.publicservicetransformation.org/wp-content/uploads/2018/03/TSIP.png'),
'localgov-digital':('LocalGov Digital','https://www.publicservicetransformation.org/wp-content/uploads/2018/03/LocGovDigital.png'),
'browne-jacobson':('Browne Jacobson','https://www.publicservicetransformation.org/wp-content/uploads/2015/05/BrowneJacobson.png'),
'redquadrant':('RedQuadrant','https://www.publicservicetransformation.org/wp-content/uploads/2015/05/RedQuadrant.png'),
'basis':('Basis','https://www.publicservicetransformation.org/wp-content/uploads/2019/03/Basis_logo_400x400.jpg')}

def decode_pinned(name, sha, target):
    p=REPO/'assets'/name
    raw=base64.b64decode(re.sub(r'\s+','',p.read_text(encoding='ascii')))
    if hashlib.sha256(raw).hexdigest()!=sha: raise SystemExit(f'checksum mismatch: {name}')
    target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(raw); return raw

def fetch(url):
    try:
        req=Request(url,headers={'User-Agent':'Mozilla/5.0 PSTA-site-builder/4.0'})
        with urlopen(req,timeout=25,context=ssl.create_default_context()) as r:return r.read()
    except (URLError,HTTPError,TimeoutError,ssl.SSLError,ValueError) as e:
        print(f'Could not download {url}: {e}'); return None

def ext(data,url):
    x=data[:300].lstrip().lower()
    if data.startswith(b'\x89PNG\r\n\x1a\n'):return '.png'
    if data.startswith(b'\xff\xd8\xff'):return '.jpg'
    if x.startswith(b'<svg') or b'<svg' in x:return '.svg'
    return Path(url.split('?',1)[0]).suffix.lower()

def install_assets():
    decode_pinned('psta-logo-official.b64',LOGO_SHA,ROOT/'assets/img/psta-logo-official.jpg')
    (ROOT/'assets/img/psta-logo-path.txt').write_text(LOGO,encoding='utf-8')
    folder=ROOT/'assets/img/partners'; folder.mkdir(parents=True,exist_ok=True); out={}
    decode_pinned('nesta-logo.b64',NESTA_SHA,folder/'nesta.jpg'); out['nesta']=f'{PREFIX}/assets/img/partners/nesta.jpg'
    for key,(name,url) in PARTNERS.items():
        data=fetch(url)
        if data and len(data)>250:
            suffix=ext(data,url)
            if suffix in {'.png','.jpg','.jpeg','.svg','.gif','.webp'}:
                p=folder/f'{key}{suffix}'; p.write_bytes(data); out[key]=f'{PREFIX}/assets/img/partners/{p.name}'; continue
        old=[p for p in folder.glob(f'{key}.*') if p.is_file() and p.stat().st_size>250]
        if old:
            p=max(old,key=lambda q:q.stat().st_size); out[key]=f'{PREFIX}/assets/img/partners/{p.name}'
    print('Partner image assets:',', '.join(sorted(out)))
    return out

def logo_box(key,name,logos):
    if key in logos:return f'<div class="partner-logo-wrap"><img class="partner-logo" src="{html.escape(logos[key],quote=True)}" alt="{html.escape(name,quote=True)}"></div>'
    return f'<div class="partner-logo-wrap"><span class="partner-logo-fallback">{html.escape(name)}</span></div>'

def card(key,name,role,copy,logos):
    return f'<article class="card partner-card">{logo_box(key,name,logos)}<p class="eyebrow">{role}</p><h3>{name}</h3><p>{copy}</p></article>'

def partners_page(logos):
    formal=''.join([
      card('e3m','E3M','Formal partner','Contributes experience of social enterprise, public service markets, and enterprise models.',logos),
      card('nesta','Nesta','Formal partner','Contributes evidence, innovation, and practical approaches to public service change.',logos),
      card('tsip','The Social Innovation Partnership','Formal partner','Contributes social innovation, evidence, evaluation, and impact expertise.',logos),
      card('redquadrant','RedQuadrant','Formal partner','Contributes public service transformation practice, programme design, delivery capability, and a wide network of experienced practitioners.',logos),
      card('basis','Basis','Formal partner','Delivers the PSTA-accredited Service Transformation Programme and contributes practical transformation learning and facilitation.',logos)])
    informal=''.join([
      card('localgov-digital','LocalGov Digital','Informal partner','An active informal relationship connecting the PSTA with digital, service design, and user-centred practice in local government.',logos),
      card('browne-jacobson','Browne Jacobson','Informal partner','An active informal relationship bringing legal and public service expertise.',logos)])
    nav=f'<nav class="site-nav" aria-label="Main navigation"><a href="{PREFIX}/programmes/">Programmes</a><a href="{PREFIX}/tools/">Tools</a><a href="{PREFIX}/in-house/">In-house</a><a href="{PREFIX}/community/">Community</a><a href="{PREFIX}/partners/" aria-current="page">Partners</a><a href="{PREFIX}/news/">News</a><a href="{PREFIX}/insights/">Insights</a><a href="{PREFIX}/about/">About</a><a class="nav-cta" href="{PREFIX}/contact/">Talk to us</a></nav>'
    page=f'''<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Partners | The Public Service Transformation Academy</title><meta name="description" content="Formal and informal partner relationships of the Public Service Transformation Academy."><link rel="stylesheet" href="{PREFIX}/assets/css/site.css"></head><body><a class="skip-link" href="#main">Skip to content</a><div class="announcement"><div class="shell"><span>The National Commissioning Academy: September 2026 to February 2027</span><a href="{PREFIX}/programmes/national-commissioning-academy/">Find out more →</a></div></div><header class="site-header"><div class="shell header-inner"><a class="brand" href="{PREFIX}/" aria-label="The Public Service Transformation Academy home"><img src="{LOGO}" alt="The Public Service Transformation Academy"></a>{nav}</div></header><main id="main"><section class="page-hero"><div class="shell"><p class="eyebrow">A partnership by design</p><h1>Partners</h1><p class="lede">The PSTA is a not-for-profit social enterprise built around collaboration. We describe formal and informal partner relationships plainly.</p></div></section><section class="section"><div class="shell"><div class="section-heading"><div><p class="eyebrow">The partnership</p><h2>Formal partners</h2></div><p>These five organisations are formal partners in the PSTA.</p></div><div class="card-grid partner-grid">{formal}</div></div></section><section class="section section-wash"><div class="shell"><div class="section-heading"><div><p class="eyebrow">Connected practice</p><h2>Informal partner relationships</h2></div><p>Useful and active relationships, without implying a formal corporate partnership.</p></div><div class="card-grid partner-grid">{informal}</div></div></section><section class="section section-blue"><div class="shell"><p class="eyebrow">Work with the PSTA</p><h2>Bring something useful to public service transformation</h2><p class="lede">We work with organisations that add useful practice, evidence, reach, or specialist expertise.</p><a class="button button-gold" href="{PREFIX}/contact/">Talk to us about working together</a></div></section></main><footer class="site-footer"><div class="shell footer-grid"><div class="footer-brand"><div class="footer-logo"><img src="{LOGO}" alt="The Public Service Transformation Academy"></div><p>Practical development for people changing public services from inside the work.</p></div><div><h2>Explore</h2><a href="{PREFIX}/programmes/">Programmes</a><a href="{PREFIX}/tools/">Tools</a><a href="{PREFIX}/news/">News</a></div><div><h2>Work with us</h2><a href="{PREFIX}/in-house/">In-house</a><a href="{PREFIX}/partners/">Partners</a><a href="{PREFIX}/contact/">Contact</a></div><div><h2>Assurance</h2><a href="{PREFIX}/policies/">Policies</a><a href="{PREFIX}/privacy/">Privacy</a><a href="{PREFIX}/accessibility/">Accessibility</a></div></div><div class="shell footer-legal"><span>Registered Social Enterprise. The Public Service Transformation Academy Limited is a company limited by guarantee, registered in England and Wales, company number 10046052. VAT number 244 4776 87.</span><span>7 Bell Yard, London, WC2A 2JR, UK</span></div></footer><a class="iteration-secret-link" href="{FEEDBACK}" aria-label="Website feedback" title="Website feedback"></a><script>document.addEventListener('keydown',e=>{{if(e.altKey&&e.shiftKey&&e.key.toLowerCase()==='n')location.href='{FEEDBACK}'}})</script></body></html>'''
    p=ROOT/'partners/index.html'; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(page,encoding='utf-8')

def patch_pages():
    for p in ROOT.rglob('*.html'):
        s=p.read_text(encoding='utf-8',errors='ignore')
        s=re.sub(r'(?<=src=["\'])(?:/PSTA)?/assets/img/psta-logo[^"\']*',LOGO,s,flags=re.I)
        s=s.replace('https://www.publicservicetransformation.org/wp-content/uploads/2017/11/twitter-white.png',LOGO)
        s=re.sub(r'<a\b[^>]*class=["\'][^"\']*footer-partner-logo[^"\']*["\'][^>]*>.*?</a>','',s,flags=re.I|re.S)
        s=s.replace('Lead partner RedQuadrant','RedQuadrant').replace('lead partner RedQuadrant','RedQuadrant')
        s=s.replace('See what the system is producing','See what your system is producing').replace('Choose by pressure, not by course title','Choose what meets your needs, not by course title')
        p.write_text(s,encoding='utf-8')
    h=ROOT/'index.html'
    if h.exists():
        s=h.read_text(encoding='utf-8')
        s=re.sub(r'<div class="credibility-item"><strong>1,500\+</strong><span>(?:National )?Commissioning Academy graduates across public services</span></div>','<div class="credibility-item"><strong>2,500+</strong><span>Academy and Programme graduates across public services</span></div>',s,flags=re.I)
        h.write_text(s,encoding='utf-8')

def retire_old_partners():
    for rel in ('partners/apace','partners/fractal-consulting'):
        p=ROOT/rel
        if p.exists():shutil.rmtree(p)
    legacy=ROOT/'the-psta/partners/index.html'
    if legacy.exists():legacy.write_text(f'<!doctype html><meta http-equiv="refresh" content="0; url={PREFIX}/partners/"><a href="{PREFIX}/partners/">View the PSTA partners</a>',encoding='utf-8')
    for p in ROOT.rglob('*.xml'):
        s=p.read_text(encoding='utf-8',errors='ignore')
        s=re.sub(r'<url>.*?(?:partners/apace|partners/fractal-consulting).*?</url>','',s,flags=re.I|re.S)
        p.write_text(s,encoding='utf-8')

def css_fix():
    p=ROOT/'assets/css/site.css'; s=p.read_text(encoding='utf-8') if p.exists() else ''
    mark='/* PSTA FINAL IDENTITY FIX */'; s=s.split(mark,1)[0].rstrip()+'\n'
    s+=mark+'''\n.brand{width:300px;min-height:100px;padding:8px 12px;background:#fff;border-radius:8px;display:flex;align-items:center;justify-content:flex-start}.brand img{display:block;width:auto;height:84px;max-width:100%;max-height:84px;object-fit:contain;object-position:left center;background:#fff}.footer-logo{display:inline-flex;align-items:center;padding:10px 12px;background:#fff;border-radius:8px;max-width:300px}.footer-logo img{display:block;width:auto;height:82px;max-width:100%;max-height:82px;object-fit:contain;background:#fff}.partner-logo-wrap{display:flex;align-items:center;justify-content:center;min-height:120px;margin-bottom:1rem;padding:1rem;background:#fff;border:1px solid var(--line);border-radius:12px}.partner-logo{display:block;width:auto;max-width:230px;height:auto;max-height:86px;object-fit:contain}.partner-logo-fallback{font-size:1.3rem;font-weight:800;color:var(--psta-dark)}.iteration-secret-link{background:#fff!important;opacity:1!important}.announcement{background:var(--psta-dark)!important}.skip-link{background:var(--psta-dark)!important}.cta-panel{background:var(--cyan-wash)!important;color:var(--ink)!important}.cta-panel h2,.cta-panel p{color:var(--ink)!important}.cta-panel .eyebrow,.cta-panel .text-link{color:var(--psta-dark)!important}.button:hover{background:var(--psta-mid)!important;border-color:var(--psta-mid)!important}@media(max-width:760px){.brand{width:230px;min-height:82px}.brand img{height:66px;max-height:66px}}\n'''
    p.parent.mkdir(parents=True,exist_ok=True); p.write_text(s,encoding='utf-8')

def feedback_redirect():
    p=ROOT/'iteration-notes-7d4f9c2b81e6a5/index.html'; p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(f'<!doctype html><html><head><meta charset="utf-8"><meta name="robots" content="noindex,nofollow"><meta http-equiv="refresh" content="0; url={FEEDBACK}"><title>The PSTA website feedback</title></head><body><a href="{FEEDBACK}">Open the running website feedback thread for the PSTA</a></body></html>',encoding='utf-8')

def audit(logos):
    fail=[]; logo=ROOT/'assets/img/psta-logo-official.jpg'
    if not logo.exists() or hashlib.sha256(logo.read_bytes()).hexdigest()!=LOGO_SHA:fail.append('full PSTA logo missing')
    p=ROOT/'partners/index.html'; t=p.read_text(encoding='utf-8') if p.exists() else ''; plain=re.sub(r'<[^>]+>',' ',t)
    for n in ('E3M','Nesta','The Social Innovation Partnership','RedQuadrant','Basis','LocalGov Digital','Browne Jacobson'):
        if n not in plain:fail.append('missing partner: '+n)
    if re.search(r'\bAPACE\b|Fractal Consulting|Alliance for Useful Evidence',plain,re.I):fail.append('retired/obsolete partner remains on partner page')
    if (ROOT/'partners/apace').exists() or (ROOT/'partners/fractal-consulting').exists():fail.append('retired partner profile remains')
    allhtml='\n'.join(x.read_text(encoding='utf-8',errors='ignore') for x in ROOT.rglob('*.html')); vis=re.sub(r'<[^>]+>',' ',allhtml)
    if '2,500+' not in vis or 'Academy and Programme graduates across public services' not in vis:fail.append('2,500+ statistic missing')
    if 'Lead partner RedQuadrant' in allhtml or 'twitter-white.png' in allhtml:fail.append('old identity wording/asset remains')
    if fail:raise SystemExit('Final public-site audit failed:\n- '+'\n- '.join(fail))
    print(f'Final audit passed; partner image assets {len(logos)}/7')

def main():
    logos=install_assets(); patch_pages(); retire_old_partners(); partners_page(logos); patch_pages(); css_fix(); feedback_redirect(); audit(logos)
if __name__=='__main__':main()
