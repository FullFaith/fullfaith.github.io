#!/usr/bin/env python3
"""Build every page of the site from the two templates in this folder.

  _src/en.html  English template (all sections)
  _src/et.html  Estonian template (all sections)

Edit the templates, then run:  python3 _src/build.py
It writes index.html, work/index.html, ... and et/..., plus sitemap.xml.
Jekyll on GitHub Pages ignores folders starting with "_", so _src is not published.
"""
import json, os, re, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://fullfaith.github.io'
LANGS = {'en': '/', 'et': '/et/'}
ORDER = ['home', 'work', 'services', 'about', 'give', 'partners', 'contact', 'privacy', 'terms']

META = {
 'en': {
  'home': None,  # keeps the template's own head
  'work': ('Our work | FullFaith', 'Films, behind-the-scenes photos and scenes by FullFaith, a Christian film studio in Estonia.'),
  'services': ('Video production services and prices | FullFaith', 'Social reels from €100, event videos from €300, promos from €400 and music videos from €500. Free for churches and Christian projects.'),
  'about': ('About us | FullFaith', 'How FullFaith started: an ad for a youth night that became almost a short film. Now a registered nonprofit (MTÜ) in Estonia.'),
  'give': ('Give | FullFaith', 'Help keep Christian video work free. Give once or monthly by card, through your Estonian bank or by bank transfer.'),
  'partners': ('Partner with us | FullFaith', 'Companies can support free Christian video work with equipment or funding, and get a place on our site.'),
  'contact': ('Contact | FullFaith', 'Write to FullFaith at fullfaithproduction@gmail.com. Based in Estonia, working with people anywhere in the world.'),
  'privacy': ('Privacy and cookies | FullFaith', 'How FullFaith MTÜ handles personal data. No cookies, no analytics, no ads.'),
  'terms': ('Terms | FullFaith', 'Terms for free and paid video work by FullFaith MTÜ.'),
 },
 'et': {
  'home': None,
  'work': ('Meie tööd | FullFaith', 'FullFaithi filmid, kaadritagused fotod ja stseenid. Kristlik filmistuudio Eestis.'),
  'services': ('Videoproduktsiooni teenused ja hinnad | FullFaith', 'Sotsiaalmeedia klipid alates 100 €, ürituste videod alates 300 €, promod alates 400 € ja muusikavideod alates 500 €. Kirikutele ja kristlikele projektidele tasuta.'),
  'about': ('Meist | FullFaith', 'Kuidas FullFaith alguse sai: noorteõhtu reklaamist sai peaaegu lühifilm. Nüüd oleme Eestis registreeritud mittetulundusühing (MTÜ).'),
  'give': ('Toeta | FullFaith', 'Aita hoida kristlik videotöö tasuta. Anneta ühekordselt või igakuiselt kaardiga, Eesti panga kaudu või pangaülekandega.'),
  'partners': ('Saa meie partneriks | FullFaith', 'Ettevõtted saavad toetada tasuta kristlikku videotööd tehnika või rahaga ning saada koha meie kodulehel.'),
  'contact': ('Kontakt | FullFaith', 'Kirjuta FullFaithile aadressil fullfaithproduction@gmail.com. Asume Eestis ja teeme koostööd inimestega üle maailma.'),
  'privacy': ('Privaatsus ja küpsised | FullFaith', 'Kuidas FullFaith MTÜ isikuandmeid käsitleb. Küpsiseid, analüütikat ega reklaame ei ole.'),
  'terms': ('Tingimused | FullFaith', 'FullFaith MTÜ tasuta ja tasuliste videotööde tingimused.'),
 },
}

# Films on the Work page (also used for Google video results).
VIDEOS = [
 {'id': 'ji3WDWdXO7M', 'name': 'Valga ühisnoorteka reklaam', 'date': '2024-12-25T06:38:30Z', 'dur': 'PT2M22S',
  'en': 'Ad for a joint youth night in Valga, made by FullFaith.',
  'et': 'Valga ühisnoorteka reklaam, tehtud FullFaithi poolt.'},
 {'id': 'Ggp6rOvbjsk', 'name': 'Joh316 - Sa Oled Siin (Ametlik Muusikavideo)', 'date': '2025-02-22T20:00:06Z', 'dur': 'PT2M48S',
  'en': 'Official music video for "Sa Oled Siin" by Joh316, made by FullFaith.',
  'et': 'Joh316 loo „Sa Oled Siin“ ametlik muusikavideo, tehtud FullFaithi poolt.'},
 {'id': 'i9i2gl2ln28', 'name': 'TCS Ameerikast ja ELU Kogudus korraldavad Noorteka!', 'date': '2024-12-26T13:09:52Z', 'dur': 'PT53S',
  'en': 'Short ad for a youth night in Tallinn by TCS from America and ELU Kogudus, made by FullFaith.',
  'et': 'Lühireklaam TCS Ameerikast ja ELU Koguduse noortekale Tallinnas, tehtud FullFaithi poolt.'},
]


def url(lang, page):
    return SITE + LANGS[lang] + ('' if page == 'home' else page + '/')


def path(lang, page):
    return LANGS[lang] + ('' if page == 'home' else page + '/')


def sub(s, pattern, repl, count=1, flags=0):
    new, n = re.subn(pattern, repl, s, flags=flags)
    assert n == count, (pattern, n)
    return new


def build(lang, page, tpl):
    s = tpl
    base = LANGS[lang]
    # keep only this page's section
    def keep(m):
        return m.group(0) if m.group(1) == page else ''
    s = re.sub(r'<section id="(\w+)" class="view[^"]*">.*?</section>\n?', keep, s, flags=re.S)
    assert f'<section id="{page}"' in s
    # hash links -> real page links
    def link(m):
        p = 'give' if m.group(1) == 'support' else m.group(1)
        return f'href="{path(lang, p)}"'
    s = re.sub(r'href="#(\w+)"', link, s)
    # nav: mark which link is which page
    nav = re.search(r'<nav [^>]*>.*?</nav>', s, re.S)
    navh = re.sub(r'<a href="([^"]*)">', lambda m: '<a href="%s" data-p="%s">' % (
        m.group(1), next(p for p in ORDER if path(lang, p) == m.group(1))), nav.group(0))
    s = s[:nav.start()] + navh + s[nav.end():]
    # language switch
    other = 'et' if lang == 'en' else 'en'
    s = sub(s, r'(<div class="lang"[^>]*>.*?<a href=")[^"]*(" data-base="[^"]*")',
            lambda m: m.group(1) + path(other, page) + m.group(2), flags=re.S)
    s = sub(s, r'<a href="[^"]*" hreflang="%s" lang="%s" aria-current="true">' % (lang, lang),
            f'<a href="{path(lang, page)}" hreflang="{lang}" lang="{lang}" aria-current="true">')
    s = s.replace('<body>', f'<body data-page="{page}" data-base="{base}">', 1)
    # head
    s = sub(s, r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{url(lang, page)}">')
    s = sub(s, r'<link rel="alternate" hreflang="en" href="[^"]*"><link rel="alternate" hreflang="et" href="[^"]*"><link rel="alternate" hreflang="x-default" href="[^"]*">',
            f'<link rel="alternate" hreflang="en" href="{url("en", page)}"><link rel="alternate" hreflang="et" href="{url("et", page)}"><link rel="alternate" hreflang="x-default" href="{url("en", page)}">')
    s = sub(s, r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{url(lang, page)}">')
    if META[lang][page]:
        title, desc = META[lang][page]
        s = sub(s, r'<title>[^<]*</title>', f'<title>{title}</title>')
        s = sub(s, r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{desc}">')
        s = sub(s, r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{title}">')
        s = sub(s, r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{desc}">')
        s = sub(s, r'<meta name="twitter:title" content="[^"]*">', f'<meta name="twitter:title" content="{title}">')
        s = sub(s, r'<meta name="twitter:description" content="[^"]*">', f'<meta name="twitter:description" content="{desc}">')
    m = re.search(r'<script type="application/ld\+json">(.*?)</script>', s, re.S)
    ld = json.loads(m.group(1))
    if META[lang][page]:
        title, desc = META[lang][page]
        for node in ld['@graph']:
            if node.get('@type') == 'WebPage':
                node.update({'@id': url(lang, page) + '#webpage', 'url': url(lang, page), 'name': title,
                             'description': desc, 'inLanguage': lang})
                node.pop('primaryImageOfPage', None)
        ld['@graph'].append({'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'FullFaith', 'item': url(lang, 'home')},
            {'@type': 'ListItem', 'position': 2, 'name': title.split(' | ')[0], 'item': url(lang, page)}]})
    if page == 'work':
        vids = []
        for v in VIDEOS:
            vids.append({'@type': 'VideoObject', '@id': url(lang, 'work') + '#video-' + v['id'],
                         'name': v['name'], 'description': v[lang],
                         'thumbnailUrl': [f'https://i.ytimg.com/vi/{v["id"]}/maxresdefault.jpg', f'https://i.ytimg.com/vi/{v["id"]}/hqdefault.jpg'],
                         'uploadDate': v['date'], 'duration': v['dur'],
                         'embedUrl': f'https://www.youtube-nocookie.com/embed/{v["id"]}',
                         'contentUrl': f'https://www.youtube.com/watch?v={v["id"]}',
                         'publisher': {'@id': SITE + '/#org'}})
        ld['@graph'].extend(vids)
        for node in ld['@graph']:
            if node.get('@type') == 'WebPage':
                node['video'] = [{'@id': v['@id']} for v in vids]
    s = s[:m.start(1)] + json.dumps(ld, ensure_ascii=False, separators=(',', ':')) + s[m.end(1):]
    return s


def main():
    today = datetime.date.today().isoformat()
    for lang in LANGS:
        tpl = open(os.path.join(ROOT, '_src', lang + '.html'), encoding='utf-8').read()
        for page in ORDER:
            out = os.path.join(ROOT, path(lang, page).strip('/'), 'index.html')
            os.makedirs(os.path.dirname(out), exist_ok=True)
            open(out, 'w', encoding='utf-8').write(build(lang, page, tpl))
    rows = []
    for lang in LANGS:
        for page in ORDER:
            alts = ''.join(f'\n    <xhtml:link rel="alternate" hreflang="{l}" href="{url(l, page)}"/>' for l in LANGS)
            alts += f'\n    <xhtml:link rel="alternate" hreflang="x-default" href="{url("en", page)}"/>'
            rows.append(f'  <url>\n    <loc>{url(lang, page)}</loc>\n    <lastmod>{today}</lastmod>{alts}\n  </url>')
    open(os.path.join(ROOT, 'sitemap.xml'), 'w').write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + '\n'.join(rows) + '\n</urlset>\n')
    print('built', len(rows), 'pages')


if __name__ == '__main__':
    main()
