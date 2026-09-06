"""Apply Benjamin's reader corrections after all historical-site generators."""
from pathlib import Path
import re, shutil, sys
from html import escape
root=Path(sys.argv[1]); source=Path(__file__).resolve().parents[1]
logo_files={"e3m":"e3m.png","nesta":"nesta.svg","tsip":"tsip.png","redquadrant":"redquadrant.png","basis":"basis.png","localgov-digital":"localgov-digital.png","browne-jacobson":"browne-jacobson.svg"}
names={"e3m":"E3M","nesta":"Nesta","tsip":"The Social Innovation Partnership","redquadrant":"RedQuadrant","basis":"Basis","localgov-digital":"LocalGov Digital","browne-jacobson":"Browne Jacobson"}
(root/'assets/partner-logos').mkdir(exist_ok=True)
for retired in ['apace','fractal-consulting']: shutil.rmtree(root/'partners'/retired,ignore_errors=True)
for file in logo_files.values(): shutil.copyfile(source/'assets/partner-logos'/file,root/'assets/partner-logos'/file)
css='.partner-logo-wrap{display:flex;align-items:center;justify-content:center;min-height:120px;padding:20px;background:#fff}.partner-logo-wrap img{display:block;width:100%;height:90px;max-width:250px;max-height:none;object-fit:contain}.partner-logo-wrap.logo-tsip{background:#182a32}.partner-profile-logo{max-width:360px;margin:20px 0}.partner-grid h3 a{color:inherit}.partner-programmes{margin-top:28px}.programme-logo{width:180px;height:95px;object-fit:contain}.partner-programme-list{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:24px}.partner-programme-list article{padding:24px;border:1px solid #d6dde0}.programme-fees{margin:24px 0;padding:24px;border-left:4px solid #b98736;background:#f1f5f6}'
for page in root.rglob('*.html'):
 text=page.read_text(); route=page.relative_to(root).as_posix()
 if 'READER_REVIEW_20260906' in text: continue
 text=text.replace('http://eepurl.com','https://eepurl.com')
 text=text.replace('Choose what meets your needs, not by course title','Find a programme for your work')
 text=text.replace('The PSTA is a not-for-profit social enterprise built around collaboration. We describe formal and informal partner relationships plainly.','The PSTA brings together organisations with experience in public services, social enterprise, innovation, and practical learning.')
 text=text.replace('This is an example of how the academy can support a specialist partner to make a proven learning offer visible, credible and connected to a wider public service network.','Participants build the skills to lead change through practical exercises, simulation, and application to their own work.')
 text=text.replace('Useful and active relationships, without implying a formal corporate partnership.','Organisations with whom we share ideas, experience, and opportunities for public-service improvement.')
 for slug,name in names.items():
  image='<img src="/assets/partner-logos/'+logo_files[slug]+'" alt="'+name+'" loading="lazy">'
  text=text.replace('<span class="partner-logo-fallback">'+name+'</span>',image)
  # Replace legacy remote/fallback markup as well as the partner-index cards.
  text=re.sub(r'<img[^>]*src="[^"]*(?:partner-logos/'+slug+r'\.[^"?]+|/partners/'+slug+r'\.[^"?]+)[^"]*"[^>]*>',lambda m:image,text)
  if slug=='tsip':text=text.replace('<div class="partner-logo-wrap" aria-hidden="true">'+image,'<div class="partner-logo-wrap logo-tsip">'+image)
  if route=='partners/index.html': text=text.replace('<h3>'+name+'</h3>','<h3><a href="/partners/'+slug+'/">'+name+'</a></h3>')
  if route=='partners/'+slug+'/index.html':
   text=re.sub(r'(<h1[^>]*>.*?</h1>)',lambda m:m.group(1)+'<div class="partner-logo-wrap partner-profile-logo'+(' logo-tsip' if slug=='tsip' else '')+'">'+image+'</div>',text,count=1,flags=re.S)
 if route=='programmes/leading-transformation/index.html':
  text=re.sub(r'<p>Current fees, VAT treatment,.*?</p>','<div class="programme-fees"><h3>Fees and accreditation</h3><p><strong>Leading Transformation modules: £295 plus VAT per person for a three- or four-module learning package.</strong> Each package includes a one-to-one support session with Benjamin Taylor, email support, and online questions and answers. A full organisational programme combines the modules and facilitated support to suit your team.</p><p><strong>The RedQuadrant Tool Shed: £495 per month plus VAT per person.</strong> Join a small practitioner cohort for live practice, peer inquiry, co-coaching, and mentoring.</p><p>Leading Transformation and the Tool Shed are accredited by the Public Service Transformation Academy.</p><p><a href="mailto:benjamin.taylor@redquadrant.com?subject=Leading%20Transformation">Ask Benjamin about Leading Transformation</a></p></div>',text,flags=re.S)
  text=text.replace('Discuss a programme','Join the programme')
 if route=='programmes/service-transformation-programme/index.html':
  text=re.sub(r'<section class="section guide-fee">.*?</section>','',text,flags=re.S)
  text=text.replace('<h1>The Service Transformation Programme</h1>','<h1>The Service Transformation Programme</h1><img class="programme-logo" src="/assets/partner-logos/basis.png" alt="Basis">')
  text=text.replace('Contact us to discuss the current curriculum, delivery options or accreditation.','<a href="https://www.basis.co.uk/">Explore training with Basis</a> or <a href="mailto:comms@basis.co.uk?subject=Service%20Transformation%20Programme">contact Basis about a place or a team programme</a>.')
  text=text.replace('Talk to the PSTA about the programme, an organisational cohort, or how it could be adapted to your context.','Delivered by Basis and accredited by the PSTA. Contact Basis for course dates, fees, and a programme for your organisation.')
  text=text.replace('mailto:david.mason@publicservicetransformation.org?subject=Service%20Transformation%20Programme','mailto:comms@basis.co.uk?subject=Service%20Transformation%20Programme').replace('Email David Mason','Email Basis')
 if route=='programmes/index.html':
  text=text.replace('</main>','<section class="section partner-programmes"><div class="shell"><h2>Accredited programmes with Basis</h2><img class="programme-logo" src="/assets/partner-logos/basis.png" alt="Basis"><div class="partner-programme-list"><article><h3><a href="/programmes/service-transformation-programme/">Service Transformation Programme</a></h3><p>Learning through doing for public-service managers and transformation practitioners, using simulation, exercises, and live work.</p></article><article><h3><a href="/programmes/agile-master-in-public-services/">Agile Master in Public Services</a></h3><p>Practise agile delivery, work in a team, and learn to test and adapt change in complex public-service settings.</p></article></div><p>Delivered by Basis and accredited by the PSTA.</p></div></section></main>')
 text=text.replace('</head>','<!-- READER_REVIEW_20260906 --><style>'+css+'</style></head>')
 page.write_text(text)
# Use the existing programme page shell for an equally visible accredited Basis offer.
p=root/'programmes/agile-master-in-public-services/index.html';p.parent.mkdir(exist_ok=True)
template=(root/'programmes/service-transformation-programme/index.html').read_text()
main='<main id="main-content"><section class="section"><div class="shell"><p><a href="/programmes/">Programmes</a></p><p class="eyebrow">Accredited programme delivered by Basis</p><h1>Agile Master in Public Services</h1><img class="programme-logo" src="/assets/partner-logos/basis.png" alt="Basis"><p class="lede">Learn to deliver and adapt change in the complexity of public services.</p><h2>Learn by working as an agile team</h2><p>The programme combines theory and practical exercises. Participants take on team roles and organise the learning as an agile project, building experience of how to prioritise, collaborate, test ideas, and review progress.</p><h2>Apply agile beyond digital projects</h2><p>For people leading public-service change, the focus is on learning from delivery and improving outcomes for citizens. Work with changing needs, make progress visible, and adapt plans as the team learns.</p><h2>Accreditation</h2><p>Delivered by Basis and accredited by the Public Service Transformation Academy. Participants complete a short assessment after the course.</p><h2>Book a place or a team programme</h2><p>Contact Basis for dates, fees, and delivery options for your organisation.</p><p><a class="button button-gold" href="mailto:comms@basis.co.uk?subject=Agile%20Master%20in%20Public%20Services">Ask Basis about the programme</a></p><p><a href="https://www.basis.co.uk/">Explore Basis</a> · <a href="/programmes/service-transformation-programme/">Service Transformation Programme</a></p></div></section></main>'
template=re.sub(r'<main\b.*?</main>',main,template,flags=re.S).replace('The Service Transformation Programme |','Agile Master in Public Services |').replace('/programmes/service-transformation-programme/"','/programmes/agile-master-in-public-services/"',1)
p.write_text(template)
# Give each named partner a useful profile with its complete logo.
profile_shell=(root/'partners/basis/index.html').read_text()
descriptions={"e3m":"E3M brings together leaders of social enterprises and public services to develop practical approaches to public-service innovation and social value.","nesta":"Nesta contributes evidence, innovation, and practical learning about improving people’s lives and public services.","tsip":"The Social Innovation Partnership contributes participatory research, community-led change, and work on inequality and social impact.","localgov-digital":"LocalGov Digital connects practitioners working on digital services and service design in local government.","browne-jacobson":"Browne Jacobson brings legal expertise and experience of public-service organisations and partnerships."}
urls={"e3m":"https://e3m.org.uk/","nesta":"https://www.nesta.org.uk/","tsip":"https://tsip.co.uk/","localgov-digital":"https://localgov.digital/","browne-jacobson":"https://www.brownejacobson.com/"}
for slug,description in descriptions.items():
 name=names[slug];profile=root/'partners'/slug/'index.html';profile.parent.mkdir(exist_ok=True)
 body='<main id="main-content"><section class="section"><div class="shell"><p><a href="/partners/">Partners</a></p><h1>'+name+'</h1><div class="partner-logo-wrap partner-profile-logo'+(' logo-tsip' if slug=='tsip' else '')+'"><img src="/assets/partner-logos/'+logo_files[slug]+'" alt="'+name+'"></div><p class="eyebrow">'+('Informal partner' if slug in ['localgov-digital','browne-jacobson'] else 'Formal partner')+'</p><p class="lede">'+description+'</p><p><a class="button button-gold" href="'+urls[slug]+'">Visit '+name+'</a></p><p><a href="/contact/">Talk to the PSTA about partnership work</a></p></div></section></main>'
 text=re.sub(r'<main\b.*?</main>',body,profile_shell,flags=re.S)
 text=re.sub(r'<title>.*?</title>','<title>'+name+' | The Public Service Transformation Academy</title>',text)
 text=text.replace('/partners/basis/','/partners/'+slug+'/')
 text=re.sub(r'<meta name="description" content="[^"]*"',lambda m:'<meta name="description" content="'+description+'"',text)
 profile.write_text(text)

# Align search/share metadata for every newly created route and index each public page.
for path in [root/'programmes/agile-master-in-public-services/index.html']+[root/'partners'/slug/'index.html' for slug in descriptions]:
 text=path.read_text(); title=re.search(r'<h1[^>]*>(.*?)</h1>',text,re.S).group(1); title=re.sub('<[^>]+>','',title)
 desc=descriptions.get(path.parent.name,'Learn agile delivery in public services with Basis on a programme accredited by the PSTA.')
 canonical='https://www.publicservicetransformation.org/'+path.parent.relative_to(root).as_posix()+'/'
 text=re.sub(r'<title>.*?</title>','<title>'+escape(title)+' | The Public Service Transformation Academy</title>',text,flags=re.S)
 text=re.sub(r'<meta[^>]+(?:name|property)="(?:description|og:title|og:description|og:url|twitter:title|twitter:description)"[^>]*>','',text)
 text=re.sub(r'<link[^>]+rel="canonical"[^>]*>','',text)
 text=text.replace('</head>','<meta name="description" content="'+escape(desc,quote=True)+'"><meta property="og:title" content="'+escape(title,quote=True)+'"><meta property="og:description" content="'+escape(desc,quote=True)+'"><meta property="og:url" content="'+canonical+'"><link rel="canonical" href="'+canonical+'"></head>')
 path.write_text(text)
sitemap=root/'sitemap.xml'
if sitemap.exists():
 text=sitemap.read_text()
 for path in [root/'programmes/agile-master-in-public-services/index.html']+[root/'partners'/slug/'index.html' for slug in descriptions]:
  url='https://www.publicservicetransformation.org/'+path.parent.relative_to(root).as_posix()+'/'
  if url not in text:text=text.replace('</urlset>','<url><loc>'+url+'</loc></url>\n</urlset>')
 sitemap.write_text(text)

# Enforce the user's punctuation preference on the delivered public text.
for page in list(root.rglob('*.html'))+list(root.rglob('*.js'))+list(root.rglob('*.json')):
 text=page.read_text();text=text.replace('http://eepurl.com','https://eepurl.com');text=text.replace('—',', ').replace('–','-').replace('&mdash;',', ').replace('&ndash;','-').replace('&#8212;',', ').replace('&#8211;','-');page.write_text(text)
print('Applied reader corrections, full partner logos, accredited offers, and punctuation.')
