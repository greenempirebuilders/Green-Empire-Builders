#!/usr/bin/env python3
"""
Green Empire Landscaping — Static Site Generator
Run: python3 generate.py
Generates all pages from site.config.json + templates
"""

import json, os, re, shutil

# ── Load config ───────────────────────────────────────────
with open("site.config.json", encoding="utf-8") as f:
    cfg = json.load(f)

B = cfg["brand"]
SERVICES = cfg["services"]
AREAS = cfg["serviceAreas"]
REVIEWS = cfg["reviews"]
FAQS = cfg["faqs"]
GALLERY = cfg.get("gallery", [])
VIDEOS = cfg.get("videos", [])

PHONE = B["phone"]
PHONE_RAW = B["phoneRaw"]
NAME = B["name"]
WEBHOOK = "https://formsubmit.co/" + B["email"]  # FormSubmit endpoint (same setup as GOAT)
ADDRESS = f"{B['address']}, {B['city']}, {B['state']} {B['zip']}"
PRIMARY = B["primaryColor"]
SECONDARY = B["secondaryColor"]
FONT    = B.get("font", "Inter")
FONT_URL = B.get('fontUrl', 'https://fonts.googleapis.com/css2?family=' + FONT.replace(' ', '+') + ':wght@400;500;600;700;800&display=swap')

# ── Lucide icon helpers ───────────────────────────────────
def _svg(paths, size=16):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}"'
            f' viewBox="0 0 24 24" fill="none" stroke="currentColor"'
            f' stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
            f' aria-hidden="true">{paths}</svg>')

ICON = {
    'phone':    _svg("<path d='M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.1 12 19.79 19.79 0 0 1 1.1 3.38 2 2 0 0 1 3.08 1h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L7.09 8.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 21 16z'/>"),
    'pin':      _svg("<path d='M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z'/><circle cx='12' cy='10' r='3'/>"),
    'clock':    _svg("<circle cx='12' cy='12' r='10'/><polyline points='12 6 12 12 16 14'/>"),
    'star':     _svg("<polygon points='12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2'/>"),
    'shield':   _svg("<path d='M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z'/><path d='m9 12 2 2 4-4'/>"),
    'home':     _svg("<path d='m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z'/><polyline points='9 22 9 12 15 12 15 22'/>"),
    'dollar':   _svg("<line x1='12' x2='12' y1='2' y2='22'/><path d='M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6'/>"),
    'check':    _svg("<polyline points='20 6 9 17 4 12'/>"),
    'check-circle': _svg("<path d='M22 11.08V12a10 10 0 1 1-5.93-9.14'/><polyline points='22 4 12 14.01 9 11.01'/>"),
    'clipboard':_svg("<rect width='8' height='4' x='8' y='2' rx='1'/><path d='M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2'/><path d='M12 11h4'/><path d='M12 16h4'/>"),
    'camera':   _svg("<path d='M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3z'/><circle cx='12' cy='13' r='3'/>"),
    'timer':    _svg("<line x1='10' x2='14' y1='2' y2='2'/><line x1='12' x2='15' y1='14' y2='11'/><circle cx='12' cy='14' r='8'/>"),
    'ruler':    _svg("<path d='M21.3 8.7 8.7 21.3c-1 1-2.5 1-3.4 0l-2.6-2.6c-1-1-1-2.5 0-3.4L15.3 2.7c1-1 2.5-1 3.4 0l2.6 2.6c1 1 1 2.5 0 3.4Z'/><path d='m7.5 10.5 2 2'/><path d='m10.5 7.5 2 2'/><path d='m13.5 4.5 2 2'/><path d='m4.5 13.5 2 2'/>"),
    'phone_lg': _svg("<path d='M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.1 12 19.79 19.79 0 0 1 1.1 3.38 2 2 0 0 1 3.08 1h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L7.09 8.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 21 16z'/>", 24),
    'pin_lg':   _svg("<path d='M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z'/><circle cx='12' cy='10' r='3'/>", 24),
    'clock_lg': _svg("<circle cx='12' cy='12' r='10'/><polyline points='12 6 12 12 16 14'/>", 24),
    'timer_lg': _svg("<line x1='10' x2='14' y1='2' y2='2'/><line x1='12' x2='15' y1='14' y2='11'/><circle cx='12' cy='14' r='8'/>", 24),
    'star_lg':  _svg("<polygon points='12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2'/>", 20),
    'dollar_lg':_svg("<line x1='12' x2='12' y1='2' y2='22'/><path d='M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6'/>", 24),
    'ruler_lg': _svg("<path d='M21.3 8.7 8.7 21.3c-1 1-2.5 1-3.4 0l-2.6-2.6c-1-1-1-2.5 0-3.4L15.3 2.7c1-1 2.5-1 3.4 0l2.6 2.6c1 1 1 2.5 0 3.4Z'/><path d='m7.5 10.5 2 2'/><path d='m10.5 7.5 2 2'/><path d='m13.5 4.5 2 2'/><path d='m4.5 13.5 2 2'/>", 24),
    'home_lg':  _svg("<path d='m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z'/><polyline points='9 22 9 12 15 12 15 22'/>", 24),
    'shield_lg':_svg("<path d='M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z'/><path d='m9 12 2 2 4-4'/>", 24),
    'clipboard_lg': _svg("<rect width='8' height='4' x='8' y='2' rx='1'/><path d='M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2'/><path d='M12 11h4'/><path d='M12 16h4'/>", 24),
    'check_lg': _svg("<polyline points='20 6 9 17 4 12'/>", 20),
    'check-circle_lg': _svg("<path d='M22 11.08V12a10 10 0 1 1-5.93-9.14'/><polyline points='22 4 12 14.01 9 11.01'/>", 24),
}
# ─────────────────────────────────────────────────────────


pages_created = []
pages_failed = []

# ── Helpers ───────────────────────────────────────────────

def make_theme_css():
    primary_dark   = B.get("primaryDark", B["primaryColor"])
    secondary_dark = B.get("secondaryDark", B["secondaryColor"])
    accent         = B.get("accentColor", "")
    accent_line    = f"  --accent:       {accent};\n  --accent-dark:  {accent};" if accent else ""
    content = f"""/* Auto-generated by generate.py — do not edit manually */
:root {{
  --green:        {B["primaryColor"]};
  --green-dark:   {primary_dark};
  --green-light:  {B["secondaryColor"]};
  --green-hover:  {secondary_dark};
{accent_line}
}}
"""
    write("css/theme.css", content)

def _minify_css(css):
    """Conservative CSS minifier: strips comments, collapses whitespace.
    String-aware so content/url values are never mangled."""
    out = []
    i, n = 0, len(css)
    in_str = None
    while i < n:
        c = css[i]
        if in_str:
            out.append(c)
            if c == in_str and css[i - 1] != '\\':
                in_str = None
            i += 1
            continue
        if c in ('"', "'"):
            in_str = c
            out.append(c)
            i += 1
            continue
        if c == '/' and i + 1 < n and css[i + 1] == '*':
            j = css.find('*/', i + 2)
            i = n if j == -1 else j + 2
            continue
        if c in ' \t\r\n':
            j = i
            while j < n and css[j] in ' \t\r\n':
                j += 1
            if out and j < n:
                prev, nxt = out[-1], css[j]
                if (prev.isalnum() or prev in '_-#.%') and (nxt.isalnum() or nxt in '_-#.%'):
                    out.append(' ')
            i = j
            continue
        if c in '{}:;,>~':
            if out and out[-1] == ' ':
                out.pop()
            out.append(c)
            i += 1
            while i < n and css[i] in ' \t\r\n':
                i += 1
            continue
        out.append(c)
        i += 1
    return ''.join(out).replace(';}', '}').strip()

def make_bundle_css():
    """Bundle + minify the three stylesheets into css/bundle.css (source order)."""
    parts = []
    for f in ("css/main.css", "css/theme.css", "css/builders-design.css"):
        with open(f, encoding="utf-8") as fh:
            parts.append(_minify_css(fh.read()))
    write("css/bundle.css", "/* Auto-generated by generate.py — do not edit manually */\n" + "".join(parts))

def make_llms():
    svc_lines = "\n".join(
        f"- [{s['name']}]https://{B['domain']}/services/{s['slug']}/): {s['description']}"
        for s in SERVICES
    )
    area_lines = "\n".join(
        f"- [{a['name']}, NY](https://{B['domain']}/service-areas/{a['slug']}/): {B['industry']} in {a['name']}."
        for a in AREAS
    )
    content = f"""# {NAME}

> {NAME} is a general contractor and home builder serving Nassau & Suffolk Counties, Long Island, NY. Phone: {PHONE}. Office: {ADDRESS}. Hours: {B['hours']}. Request service: https://{B['domain']}/request-service.html


{NAME} provides professional {B['industryLower']} across Long Island, New York. The site lists {len(SERVICES)} services and {len(AREAS)} service-area towns in Nassau and Suffolk Counties. All services are performed by licensed and insured professionals; free estimates are available by phone or through the request-service form.


## Services

{svc_lines}
- [All Services](https://{B['domain']}/services/): Full list of services offered.


## Service Areas

- [All Service Areas](https://{B['domain']}/service-areas/): Full list of towns served on Long Island.
{area_lines}


## Company

- [About](https://{B['domain']}/about/): About {NAME}.
- [Reviews](https://{B['domain']}/reviews/): Customer reviews.
- [FAQ](https://{B['domain']}/faq/): Frequently asked questions.
- [Request Service](https://{B['domain']}/request-service.html): Request a free estimate.
"""
    write("llms.txt", content)

def mkdir(path):
    os.makedirs(path, exist_ok=True)

def write(path, content):
    d = os.path.dirname(path)
    if d:
        mkdir(d)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    pages_created.append(path.replace(os.getcwd() + "/", ""))

def nav(active=""):
    service_links = "\n".join(
        f'<li><a href="/services/{s["slug"]}/">{s["name"]}</a></li>'
        for s in SERVICES
    )
    mobile_service_links = "\n".join(
        f'<a href="/services/{s["slug"]}/">{s["name"]}</a>'
        for s in SERVICES
    )
    return f"""
<header class="site-header">
  <nav class="main-nav" aria-label="Main navigation">
    <div class="container nav-inner">
      <a href="/" class="nav-logo">
        <img src="/images/logo.png" alt="{NAME} logo" width="96" height="96" />
      </a>
      <ul class="nav-links">
        <li class="has-dropdown">
          <a href="/services/" class="{'active' if active=='services' else ''}">Services ▾</a>
          <ul class="dropdown">
            <li><span class="dropdown-label">Our Services</span></li>
            {service_links}
            <li><a href="/services/" class="dropdown-all">View All Services →</a></li>
          </ul>
        </li>
        <li><a href="/about/" class="{'active' if active=='about' else ''}">About Us</a></li>
        <li><a href="/service-areas/" class="{'active' if active=='areas' else ''}">Service Areas</a></li>
        <li><a href="/reviews/" class="{'active' if active=='reviews' else ''}">Reviews</a></li>
        <li><a href="/blog/" class="{'active' if active=='blog' else ''}">Articles</a></li>
        <li><a href="/faq/" class="{'active' if active=='faq' else ''}">FAQ</a></li>
      </ul>
      <div class="nav-cta">
        <a href="tel:{PHONE_RAW}" class="nav-phone">{PHONE}</a>
        <a href="/request-service.html" class="btn btn-primary btn-sm">Get Started</a>
      </div>
      <button class="hamburger" id="hamburger" aria-label="Open menu">
        <span></span><span></span><span></span>
      </button>
    </div>
  </nav>
</header>
<div class="mobile-menu" id="mobile-menu">
  <div class="mobile-menu-header">
    <img src="/images/logo.png" alt="{NAME}" width="40" height="40" />
    <button id="mobile-close" aria-label="Close">✕</button>
  </div>
  <a href="/request-service.html" class="btn btn-primary mobile-cta">Get Free Estimate</a>
  <a href="tel:{PHONE_RAW}" class="btn btn-outline mobile-cta">{PHONE}</a>
  <div class="mobile-nav-section">Services</div>
  {mobile_service_links}
  <div class="mobile-nav-section">Company</div>
  <a href="/about/">About Us</a>
  <a href="/service-areas/">Service Areas</a>
  <a href="/reviews/">Reviews</a>
  <a href="/faq/">FAQ</a>
</div>"""

def footer():
    service_links = "\n".join(
        f'<li><a href="/services/{s["slug"]}/">{s["name"]}</a></li>'
        for s in SERVICES
    )
    nassau = [a for a in AREAS if a["county"] == "Nassau"][:6]
    suffolk = [a for a in AREAS if a["county"] == "Suffolk"][:6]
    nassau_links = "\n".join(f'<li><a href="/service-areas/{a["slug"]}/">{a["name"]}</a></li>' for a in nassau)
    suffolk_links = "\n".join(f'<li><a href="/service-areas/{a["slug"]}/">{a["name"]}</a></li>' for a in suffolk)
    return f"""
<footer class="site-footer">
  <div class="footer-main">
    <div class="container footer-grid">
      <div class="footer-brand">
        <a href="/"><img src="/images/logo-light.png" alt="{NAME}" width="72" height="72" class="footer-logo" /></a>
        <p>{B.get('footerTagline', f"{NAME} — locally based in {B['city']}, NY.")}</p>
        <a href="tel:{PHONE_RAW}" class="footer-phone">{PHONE}</a>
        <p class="footer-address">{ADDRESS}</p>
        <div class="footer-social">
          <a href="{B['facebook']}" target="_blank" rel="noopener" aria-label="Facebook">
            <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20"><path d="M18 2h-3a5 5 0 00-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 011-1h3z"/></svg>
          </a>
          <a href="{B['instagram']}" target="_blank" rel="noopener" aria-label="Instagram">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20"><rect x="2" y="2" width="20" height="20" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1.5" fill="currentColor" stroke="none"/></svg>
          </a>
        </div>
      </div>
      <div class="footer-col">
        <h4>Our Services</h4>
        <ul>{service_links}</ul>
      </div>
      <div class="footer-col">
        <h4>Nassau County</h4>
        <ul>{nassau_links}<li><a href="/service-areas/">All Areas →</a></li></ul>
      </div>
      <div class="footer-col">
        <h4>Suffolk County</h4>
        <ul>{suffolk_links}<li><a href="/service-areas/">All Areas →</a></li></ul>
      </div>
    </div>
  </div>
  <div class="footer-bottom">
    <div class="container footer-bottom-inner">
      <span>&copy; <span id="yr"></span> {NAME}. All rights reserved.</span>
      <div class="footer-legal">
        <a href="/privacy-policy.html">Privacy Policy</a>
        <a href="/terms.html">Terms of Use</a>
        <a href="/accessibility.html">Accessibility</a>
      </div>
    </div>
  </div>
</footer>
<div class="social-side" aria-label="Follow us on social media">
  <span class="social-side-label">Follow Us</span>
  <a href="{B['facebook']}" target="_blank" rel="noopener" aria-label="Green Empire Builders on Facebook"><svg viewBox="0 0 24 24" fill="currentColor" width="18" height="18"><path d="M18 2h-3a5 5 0 00-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 011-1h3z"/></svg></a>
  <a href="{B['instagram']}" target="_blank" rel="noopener" aria-label="Green Empire Builders on Instagram"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18"><rect x="2" y="2" width="20" height="20" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1.5" fill="currentColor" stroke="none"/></svg></a>
</div>
<script>document.getElementById('yr').textContent = new Date().getFullYear();</script>
<script src="/js/main.js"></script>"""

def head(title, desc, canonical, schema="", extra=""):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>
  <meta name="description" content="{desc}" />
  <link rel="canonical" href="https://{B['domain']}{canonical}" />
  <meta property="og:title" content="{title}" />
  <meta property="og:description" content="{desc}" />
  <meta property="og:type" content="website" />
  <meta property="og:url" content="https://{B['domain']}{canonical}" />
  <meta property="og:image" content="/images/drive-hero-kitchen.jpg" />
  <meta name="robots" content="index, follow" />
  <link rel="icon" href="/images/favicon.svg" type="image/svg+xml" />
  <link rel="apple-touch-icon" href="/images/logo.png" />
  <link rel="manifest" href="/manifest.json" />
  <link rel="sitemap" type="application/xml" href="/sitemap.xml" />
  {schema}
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="{FONT_URL}" rel="stylesheet" media="print" onload="this.media='all'" />
  <noscript><link href="{FONT_URL}" rel="stylesheet" /></noscript>
  <link rel="stylesheet" href="/css/bundle.css?v=8" />
  {extra}
</head>
<body>"""

FILLED_STAR = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" class="filled-star"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>'

def filled_stars(n=5):
    return FILLED_STAR * n

GOOGLE_G_SVG = '<svg class="rb-g" viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path fill="#4285F4" d="M23.5 12.3c0-.9-.1-1.5-.3-2.2H12v4.3h6.5c-.1 1.1-.8 2.7-2.4 3.8l3.7 2.9c2.3-2.1 3.7-5.2 3.7-9z"/><path fill="#34A853" d="M12 24c3.2 0 5.9-1.1 7.9-2.9l-3.7-2.9c-1 .7-2.4 1.2-4.2 1.2-3.2 0-5.9-2.2-6.9-5.1L1.2 17.2C3.2 21.2 7.3 24 12 24z"/><path fill="#FBBC05" d="M5.1 14.3c-.2-.7-.4-1.5-.4-2.3s.1-1.6.4-2.3L1.2 6.8C.4 8.3 0 10.1 0 12s.4 3.7 1.2 5.2l3.9-2.9z"/><path fill="#EA4335" d="M12 4.7c1.8 0 3 .8 3.7 1.4l3.3-3.2C17.9 1.1 15.2 0 12 0 7.3 0 3.2 2.8 1.2 6.8l3.9 2.9c1-2.9 3.7-5 6.9-5z"/></svg>'

def reviews_badge():
    return f'<div class="reviews-badge">{GOOGLE_G_SVG}<span class="rb-stars">{filled_stars(5)}</span><span class="rb-text"><strong>5.0</strong> from 14 Google reviews</span></div>'

BENEFIT_TAIL = [
    "Free custom design preview",
    "Written quote before any work starts",
    "One dedicated team, start to finish",
    "Family-owned, Long Island based",
    "Workmanship warranty",
]

TRUST_1 = "Green Empire Builders is a family-owned remodeling company based in Massapequa Park, with over 10 years of remodeling experience. We remodel kitchens, bathrooms and basements and build additions across Nassau and Suffolk."
TRUST_2 = "We work for homeowners, and we come to you: there's no showroom to drive to."

PROCESS_STEPS = [
    ("Tell us about the project", "Send the form or call. We call you back to set a time that suits you."),
    ("We come to your home", "We measure, look at what's there now and talk through the design, the materials and your budget."),
    ("You get a design preview and a written quote", "A preview of your new space, and one price for the project, in writing, before any work starts."),
    ("One team manages it, start to finish", "We keep you posted while the work is under way."),
]

def _first_sentence(text):
    part = text.split(". ")[0].strip()
    return part if part.endswith(".") else part + "."

def towns_faq_html():
    links = ", ".join(f'<a href="/service-areas/{a["slug"]}/">{a["name"]}</a>' for a in AREAS)
    return ("We work across all of Nassau County, and in Suffolk County for kitchens, bathrooms, "
            f"basements and additions. Some of the towns we cover: {links}. "
            "Not on the list? Put your ZIP in the form and we'll tell you.")

def towns_faq_text():
    names = ", ".join(a["name"] for a in AREAS)
    return ("We work across all of Nassau County, and in Suffolk County for kitchens, bathrooms, "
            f"basements and additions. Some of the towns we cover: {names}. "
            "Not on the list? Put your ZIP in the form and we'll tell you.")

def service_faq_items(s):
    items = []
    for q, a in s["faqs"]:
        items.append(f"""
    <div class="faq-item">
      <button class="faq-question">{q} <span class="faq-icon">+</span></button>
      <div class="faq-answer"><p>{a}</p></div>
    </div>""")
    items.append(f"""
    <div class="faq-item">
      <button class="faq-question">Do you come out to my town? <span class="faq-icon">+</span></button>
      <div class="faq-answer"><p>{towns_faq_html()}</p></div>
    </div>""")
    return "\n".join(items)

def service_faq_schema(s):
    faqs = list(s["faqs"]) + [["Do you come out to my town?", towns_faq_text()]]
    items = json.dumps([{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs])
    return f'<script type="application/ld+json">{{"@context":"https://schema.org","@type":"FAQPage","mainEntity":{items}}}</script>'

def booking_form(compact=False):
    service_opts = "\n".join(
        f'<option value="{s["slug"]}">{s["name"]}</option>'
        for s in SERVICES
    )
    if compact:
        return f"""
<div class="booking-card">
  <div class="booking-card-header">
    <h3>Get Your Free Design Preview</h3>
    {reviews_badge()}
    <p>Free, no obligation — we call you back the same business day, 8am–6pm.</p>
  </div>
  <form action="{WEBHOOK}" method="POST" class="booking-form" data-phone="{PHONE}">
    <div class="form-group"><label for="c-name">Name *</label><input type="text" id="c-name" name="name" required placeholder="Your full name" /></div>
    <div class="form-group"><label for="c-phone">Phone *</label><input type="tel" id="c-phone" name="phone" required placeholder="{PHONE}" /></div>
    <div class="form-group"><label for="c-service">Service</label>
      <select id="c-service" name="service"><option value="">Select a service...</option>{service_opts}</select>
    </div>
    <div class="form-group"><label for="c-message">Details</label><textarea id="c-message" name="message" rows="3" placeholder="Tell us about your project..."></textarea></div>
    <input type="text" name="_honey" style="display:none" />
    <input type="hidden" name="_next" value="https://greenempirebuild.com/thank-you.html" />
    <input type="hidden" name="_captcha" value="false" />
    <button type="submit" class="btn btn-primary btn-block">Get My Free Design Preview →</button>
  </form>
</div>"""
    return f"""
<div class="booking-card">
  <div class="booking-card-header">
    <h3>Request Your Free Design Preview</h3>
    {reviews_badge()}
    <p>Free, no obligation — we call you back the same business day, 8am–6pm.</p>
  </div>
  <form action="{WEBHOOK}" method="POST" class="booking-form" data-phone="{PHONE}">
    <div class="form-row">
      <div class="form-group"><label for="f-first-name">First Name *</label><input type="text" id="f-first-name" name="first_name" required placeholder="John" /></div>
      <div class="form-group"><label for="f-last-name">Last Name *</label><input type="text" id="f-last-name" name="last_name" required placeholder="Smith" /></div>
    </div>
    <div class="form-row">
      <div class="form-group"><label for="f-phone">Phone *</label><input type="tel" id="f-phone" name="phone" required placeholder="{PHONE}" /></div>
      <div class="form-group"><label for="f-zip">ZIP Code *</label><input type="text" id="f-zip" name="zip" required placeholder="{B['zip']}" maxlength="5" /></div>
    </div>
    <div class="form-group"><label for="f-email">Email</label><input type="email" id="f-email" name="email" placeholder="you@email.com" /></div>
    <div class="form-group"><label for="f-service">Service Needed *</label>
      <select id="f-service" name="service" required><option value="">Select a service...</option>{service_opts}<option value="other">Other / Not Sure</option></select>
    </div>
    <div class="form-group"><label for="f-message">Project Details</label><textarea id="f-message" name="message" rows="4" placeholder="Describe your project, property size, timeline..."></textarea></div>
    <input type="text" name="_honey" style="display:none" />
    <input type="hidden" name="_subject" value="New Estimate Request - {NAME}" />
    <input type="hidden" name="_next" value="https://greenempirebuild.com/thank-you.html" />
    <input type="hidden" name="_captcha" value="false" />
    <button type="submit" class="btn btn-primary btn-block">Get My Free Design Preview →</button>
    <p class="form-disclaimer">We respect your privacy. No spam, ever.</p>
  </form>
</div>"""

def review_cards(city=None):
    cards = []
    for r in REVIEWS:
        loc = r["location"]
        stars = filled_stars(r["rating"])
        parts = r["name"].split()
        initials = (parts[0][0] + parts[-1][0]).upper() if len(parts) > 1 else parts[0][:2].upper()
        cards.append(f"""
    <div class="review-card">
      <div class="review-stars">{stars}</div>
      <p class="review-text">"{r['text']}"</p>
      <div class="review-footer">
        <div class="review-avatar">{initials}</div>
        <div>
          <div class="review-author">{r['name']}</div>
          <div class="review-location">{loc}</div>
        </div>
      </div>
    </div>""")
    return "\n".join(cards)

def service_area_links():
    return "\n".join(
        f'<a href="/service-areas/{a["slug"]}/" class="city-pill">{a["name"]}</a>'
        for a in AREAS
    )

def breadcrumbs(crumbs):
    items = []
    schema_items = []
    for i, (label, url) in enumerate(crumbs):
        if url:
            items.append(f'<li><a href="{url}">{label}</a></li>')
        else:
            items.append(f'<li>{label}</li>')
        if url:
            schema_items.append(f'{{"@type":"ListItem","position":{i+1},"name":"{label}","item":"https://{B["domain"]}{url}"}}')
        else:
            schema_items.append(f'{{"@type":"ListItem","position":{i+1},"name":"{label}"}}')
    schema = f"""<script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{",".join(schema_items)}]}}
  </script>"""
    return f'<nav class="breadcrumbs" aria-label="Breadcrumb"><div class="container"><ol class="breadcrumb-list">{"".join(items)}</ol></div></nav>', schema

# Build sameAs array (only include non-empty social links)
_same_as = [s for s in [B.get('facebook',''), B.get('instagram','')] if s]
_same_as_json = f',"sameAs":{json.dumps(_same_as)}' if _same_as else ''

# Build reviews array with datePublished
_reviews_json = json.dumps([{
    "@type": "Review",
    "author": {"@type": "Person", "name": r["name"]},
    "datePublished": r.get("date", "2025-01-01"),
    "reviewRating": {"@type": "Rating", "ratingValue": str(r["rating"]), "bestRating": "5"},
    "reviewBody": r["text"]
} for r in REVIEWS])

# Build aggregateRating
# Aggregate matches the Google Business Profile (verified Nov 16, 2026): 5.0 from 14 reviews.
_aggregate_rating = json.dumps({
    "@type": "AggregateRating",
    "ratingValue": "5.0",
    "reviewCount": "14",
    "bestRating": "5",
    "worstRating": "1"
})

LOCAL_BIZ_SCHEMA = f"""<script type="application/ld+json">
  {{
    "@context":"https://schema.org",
    "@type":"{B.get('schemaType','LocalBusiness')}",
    "name":"{NAME}",
    "url":"https://{B['domain']}/",
    "telephone":"{PHONE}",
    "address":{{"@type":"PostalAddress","streetAddress":"{B['address']}","addressLocality":"{B['city']}","addressRegion":"{B['state']}","postalCode":"{B['zip']}","addressCountry":"US"}},
    "priceRange":"$$",
    "openingHours":"Mo-Sa 07:00-18:00",
    "geo":{{"@type":"GeoCoordinates","latitude":40.7065,"longitude":-73.6212}},
    "areaServed":{json.dumps([{"@type":"City","name":a["name"]} for a in AREAS])}{_same_as_json},
    "aggregateRating": {_aggregate_rating},
    "review": {_reviews_json}
  }}
  </script>"""

# ─────────────────────────────────────────────────────────
# HELPER: Service card header (photo or emoji icon)
# ─────────────────────────────────────────────────────────

def service_card_header(s):
    img = s.get("cardImage") or s.get("image")
    if img:
        return f'<img class="service-card-img" src="{img}" alt="{s["name"]}" loading="lazy" />'
    return f'<div class="service-card-placeholder" aria-hidden="true"></div>'


# ─────────────────────────────────────────────────────────
# HELPER: Gallery section (Our Work)
# ─────────────────────────────────────────────────────────

def gallery_section():
    if not GALLERY:
        return ""
    items = []
    for item in GALLERY:
        if item.get("src"):
            items.append(f"""      <figure class="gallery-item">
        <img src="{item['src']}" alt="{item['alt']}" loading="lazy" />
        <figcaption>{item['label']}</figcaption>
      </figure>""")
        else:
            items.append(f"""      <div class="gallery-item gallery-placeholder-slot">
        <span class="gallery-slot-icon">{item.get('icon','')}</span>
        <span class="gallery-slot-label">{item['label']}</span>
      </div>""")
    items_html = "\n".join(items)
    return f"""
<!-- OUR WORK -->
<section class="section" id="our-work">
  <div class="container">
    <div class="section-header">
      <span class="eyebrow">Our Work</span>
      <h2>Recent Projects on Long Island</h2>
      <p>See the quality of our work across Nassau &amp; Suffolk Counties — from custom landscapes and patios to full outdoor renovation projects.</p>
    </div>
    <div class="gallery-grid">
{items_html}
    </div>
    <div class="text-center mt-4">
      <a href="/request-service.html" class="btn btn-primary">Start Your Project</a>
    </div>
  </div>
</section>"""


# ─────────────────────────────────────────────────────────
# HELPER: Our Work / Recent Projects section
# ─────────────────────────────────────────────────────────

def work_section():
    if not GALLERY:
        return ""
    items = []
    for item in GALLERY:
        if item.get("src"):
            items.append(f"""<div class="work-item">
        <img src="{item['src']}" alt="{item['alt']}" loading="lazy" />
        <div class="work-item-label">{item['label']}</div>
      </div>""")
        else:
            items.append(f"""<div class="work-item work-item-placeholder">
        <div class="work-item-label">{item['label']}</div>
      </div>""")
    items_html = "\n      ".join(items)
    return f"""
<section class="section our-work-section" id="our-work">
  <div class="container">
    <div class="section-header">
      <span class="eyebrow">Portfolio</span>
      <h2>Recent Projects</h2>
      <p>A sample of our construction and renovation work across Nassau and Suffolk Counties.</p>
    </div>
    <div class="work-grid">
      {items_html}
    </div>
    <div class="text-center mt-4">
      <a href="/request-service.html" class="btn btn-primary">Start Your Project</a>
    </div>
  </div>
</section>"""


# ─────────────────────────────────────────────────────────
# HELPER: Video walkthroughs (click-to-play, no preload)
# Videos load only when the visitor presses play, so they
# never slow down the initial page load.
# ─────────────────────────────────────────────────────────

def video_section():
    if not VIDEOS:
        return ""
    cards = []
    for v in VIDEOS:
        cards.append(f"""<figure class="video-card">
        <div class="video-frame">
          <video preload="metadata" poster="{v['poster']}" playsinline controls src="{v['src']}" aria-label="{v['label']} video walkthrough"></video>
          <button class="video-play" type="button" aria-label="Play {v['label']} video">
            <svg xmlns="http://www.w3.org/2000/svg" width="26" height="26" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M8 5.5v13l11-6.5z"/></svg>
          </button>
          <span class="video-duration">{v['duration']}</span>
        </div>
        <figcaption class="video-caption">
          <h3>{v['label']}</h3>
          <p>Video walkthrough of a recently completed project</p>
        </figcaption>
      </figure>""")
    cards_html = "\n      ".join(cards)
    return f"""
<!-- VIDEO WALKTHROUGHS -->
<section class="section video-section" id="project-videos">
  <div class="container">
    <div class="section-header">
      <span class="eyebrow">Video Walkthroughs</span>
      <h2>Watch Our Recent Projects</h2>
      <p>Step inside two of our latest finished projects — real walkthroughs, no staging, no stock footage.</p>
    </div>
    <div class="video-grid">
      {cards_html}
    </div>
  </div>
</section>"""


# ─────────────────────────────────────────────────────────
# PAGE: Homepage
# ─────────────────────────────────────────────────────────

def make_homepage():
    hero_slides = B.get('heroSlides', ['/images/hero-bg.jpg'])
    hero_img = hero_slides[0]
    hero_alts = [
        "Open-plan kitchen, dining and living remodel with a designer island and staircase",
        "Bathroom renovation with a double vanity, patterned tile floor and glass walk-in shower",
        "Open-plan living and dining space with a custom wine wall",
    ]
    slide_tags = []
    for i, src in enumerate(hero_slides):
        alt = hero_alts[i] if i < len(hero_alts) else hero_alts[0]
        extra = ' fetchpriority="high"' if i == 0 else ' loading="lazy"'
        cls = "hero-photo first" if i == 0 else "hero-photo"
        slide_tags.append(f'<img class="{cls}" style="animation-delay:{i * 4}s" src="{src}" alt="{alt}"{extra} />')
    slides_html = "\n  ".join(slide_tags)
    service_cards_list = []
    for s in SERVICES:
        service_cards_list.append(f"""
    <div class="service-card">
      {service_card_header(s)}
      <div class="service-card-body">
        <h3>{s['name']}</h3>
        <p>{s['description']}</p>
        <a href="/services/{s['slug']}/" class="card-link">Learn More →</a>
      </div>
    </div>""")
    service_cards = "\n".join(service_cards_list)

    faq_items = "\n".join(f"""
    <div class="faq-item">
      <button class="faq-question">{f['q']} <span class="faq-icon">+</span></button>
      <div class="faq-answer"><p>{f['a']}</p></div>
    </div>""" for f in FAQS[:5])

    content = f"""{head(
        f"{B['industry']} in {B['city']}, NY | {NAME} | {PHONE}",
        f"{NAME} provides professional {B['industryLower']} in {B['city']}, NY. Call {PHONE} for a free estimate!",
        "/",
        LOCAL_BIZ_SCHEMA,
        extra=f'<link rel="preload" as="image" href="{hero_img}" fetchpriority="high" />'
    )}
{nav()}

<!-- HERO -->
<section class="hero" id="hero">
  {slides_html}
  <div class="hero-overlay"></div>
  <div class="container">
    <div class="hero-content">
      <span class="hero-brand-name">{NAME}</span>
      <span class="hero-badge">Nassau &amp; Suffolk Counties · Long Island, NY</span>
      <h1>{B['tagline']}</h1>
      <p id="hero-p">{B.get('heroSubtext', '')}</p>
      <div class="hero-actions">
        <a href="/request-service.html" class="btn btn-primary btn-lg">Get a Free Estimate</a>
        <a href="tel:{PHONE_RAW}" class="btn btn-outline-white btn-lg">Call {PHONE}</a>
      </div>
      <div class="hero-trust">
        <span>{ICON["star"]} 5-Star Rated</span>
        <span>{ICON["shield"]} Licensed &amp; Insured</span>
        <span>{ICON["pin"]} Long Island Based</span>
      </div>
    </div>
  </div>
</section>

<!-- CONTACT CARDS -->
<section class="contact-cards-section">
  <div class="container contact-cards-grid">
    <div class="contact-card">
      <div class="icon-circle">
        <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.69 12 19.79 19.79 0 0 1 1.61 3.44 2 2 0 0 1 3.6 1.25h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L7.91 8.82a16 16 0 0 0 6.29 6.29l.94-.94a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
      </div>
      <h3>Call Us</h3>
      <p>Speak directly with our team — quick response guaranteed</p>
      <a href="tel:{PHONE_RAW}" class="btn btn-outline-white">{PHONE}</a>
    </div>
    <div class="contact-card">
      <div class="icon-circle">
        <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>
      </div>
      <h3>Email Us</h3>
      <p>Send us your project details and we'll follow up promptly</p>
      <a href="mailto:{B['email']}" class="btn btn-outline-white">{B['email']}</a>
    </div>
    <div class="contact-card">
      <div class="icon-circle">
        <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" x2="8" y1="13" y2="13"/><line x1="16" x2="8" y1="17" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
      </div>
      <h3>Free Estimate</h3>
      <p>No pressure, no obligation — just honest pricing upfront</p>
      <a href="/request-service.html" class="btn btn-secondary">Get Started</a>
    </div>
  </div>
</section>



<!-- SERVICES -->
<section class="section" id="services">
  <div class="container">
    <div class="section-header">
      <span class="eyebrow">What We Do For You</span>
      <h2>{B.get('servicesHeadline', f'{B.get("industry","Professional")} Services for Long Island')}</h2>
      <p>{B.get('servicesSubtext', f'Professional {B.get("industryLower","services")} for Long Island homeowners and businesses.')}</p>
    </div>
    <div class="service-grid">
      {service_cards}
    </div>
  </div>
</section>

{video_section()}

<!-- BOOK A CONSULTATION -->
<section class="consultation-section">
  <div class="container consultation-content">
    <div class="consultation-text">
      <span class="eyebrow-light">Get Started</span>
      <h2>Book a Free Consultation</h2>
      <p>Ready to start your project? Schedule a free on-site consultation. We'll walk your property, listen to your goals, and give you a detailed quote — no pressure, no obligation.</p>
      <ul class="consult-list">
        <li>{ICON["check"]} Free on-site visit</li>
        <li>{ICON["check"]} Detailed written quote</li>
        <li>{ICON["check"]} Response within 1 hour</li>
        <li>{ICON["check"]} No commitment required</li>
      </ul>
    </div>
    <div class="consultation-form-wrap">
      {booking_form(compact=True)}
    </div>
  </div>
</section>

<!-- REVIEWS -->
<section class="section section-light" id="reviews">
  <div class="container">
    <div class="section-header">
      <span class="eyebrow">Client Reviews</span>
      <h2>What Long Island Homeowners Say</h2>
    </div>
    <div class="review-grid">
      {review_cards()}
    </div>
    <div class="text-center mt-4">
      <a href="/reviews/" class="btn btn-outline">Read More Reviews</a>
    </div>
  </div>
</section>

<!-- SERVICE AREAS -->
<section class="section">
  <div class="container">
    <div class="section-header">
      <span class="eyebrow">Service Areas</span>
      <h2>Serving Nassau &amp; Suffolk Counties</h2>
      <p>We cover all of Long Island. Don't see your city? Call us — we likely serve you.</p>
    </div>
    <div class="city-grid">
      {service_area_links()}
    </div>
  </div>
</section>

<!-- FAQ PREVIEW -->
<section class="section section-light">
  <div class="container">
    <div class="section-header">
      <span class="eyebrow">FAQ</span>
      <h2>Frequently Asked Questions</h2>
    </div>
    <div class="faq-list">
      {faq_items}
    </div>
    <div class="text-center mt-4">
      <a href="/faq/" class="btn btn-outline">See All FAQs</a>
    </div>
  </div>
</section>

<!-- CTA -->
<section class="cta-banner">
  <div class="container">
    <h2>Ready to Start Your Project?</h2>
    <p>No pressure, no obligation — just honest work and fair pricing from a team that knows Long Island.</p>
    <div class="cta-actions">
      <a href="/request-service.html" class="btn btn-secondary btn-lg">Get a Free Estimate</a>
      <a href="tel:{PHONE_RAW}" class="btn btn-outline-white btn-lg">Call {PHONE}</a>
    </div>
  </div>
</section>

{footer()}
</body></html>"""
    write("index.html", content)


# ─────────────────────────────────────────────────────────
# PAGE: Service detail pages
# ─────────────────────────────────────────────────────────

SERVICE_WORK = {
    "kitchen-remodeling": [
        ("/images/kitchen-work1.jpg", "Bright white kitchen remodel with a large island and quartz countertops"),
        ("/images/kitchen-work2.jpg", "Light wood kitchen remodel with a waterfall-edge island"),
        ("/images/kitchen-work3.jpg", "White shaker kitchen with tall pantry cabinets"),
        ("/images/kitchen-work4.jpg", "White kitchen remodel with hardwood floors and a dark island"),
    ],
    "bathroom-remodeling": [
        ("/images/drive-work-bath9.jpg", "Sage-green tiled bathroom with a glass walk-in shower and wood vanity"),
        ("/images/drive-work-bath3.jpg", "Master bathroom remodel with a freestanding tub and marble-look glass shower"),
        ("/images/drive-work-bath7.jpg", "Bathroom remodel with natural stone tile, a glass shower and a jetted tub"),
        ("/images/drive-work-bath12.jpg", "Twin wood vanities with backlit mirrors in a renovated master bathroom"),
    ],
    "home-additions": [
        ("/images/drive-about-house.jpg", "Home addition with floor-to-ceiling glass walls"),
        ("/images/drive-gallery-living.jpg", "Addition living space opening to the pool and garden"),
        ("/images/drive-gallery-glass.jpg", "Finished addition space with sliding glass doors"),
    ],
    "dormer-construction": [],
    "basement-finishing": [
        ("/images/basement-living.jpg", "Finished basement with a wet bar, media wall and lounge seating"),
        ("/images/basement-work-lounge.jpg", "Finished basement living area with a sectional, wet bar and staircase"),
        ("/images/basement-work-room.jpg", "Newly finished basement room with wood-look flooring"),
        ("/images/basement-work-framing.jpg", "Basement framing and electrical work in progress by our crew"),
    ],
    "full-home-renovation": [],
    "custom-home-building": [],
}

def make_service_page(s):
    bc, bc_schema = breadcrumbs([("Home", "/"), ("Services", "/services/"), (s["name"], None)])
    benefits = "\n".join(f"<li>{b}</li>" for b in [s["lead"]] + BENEFIT_TAIL)
    covers = "\n".join(
        f'<div class="feature-card"><h3>{t}</h3><p>{d}</p></div>'
        for t, d in s["covers"]
    )
    steps = "\n".join(
        f'<div class="step-card"><div class="step-number">{i}</div><h3 class="step-title">{t}</h3><p class="step-desc">{d}</p></div>'
        for i, (t, d) in enumerate(PROCESS_STEPS, 1)
    )
    work_photos = SERVICE_WORK.get(s["slug"], [])
    work_html = ""
    if work_photos:
        imgs = "\n".join(f'        <img src="{src}" alt="{alt}" loading="lazy" />' for src, alt in work_photos)
        work_html = f'''      <h2>Our Work — Recent {s['name']} Projects</h2>
      <p>Real projects by our own crews — the standard your home gets too.</p>
      <div class="work-grid">
{imgs}
      </div>
'''
    faq_items = service_faq_items(s)
    faq_schema = service_faq_schema(s)
    svc_img = s.get("image", "")
    hero_class = "page-hero page-hero-photo" if svc_img else "page-hero"
    hero_style = f' style="background-image:url(\'{svc_img}\')"' if svc_img else ""
    other_services = "\n".join(
        f'<a href="/services/{o["slug"]}/" class="related-link">{o["name"]}</a>'
        for o in SERVICES if o["slug"] != s["slug"]
    )
    content = f"""{head(
        f"{s['name']} on Long Island, NY | {NAME}",
        f"{s['tagline']} Free custom design preview and a written quote before any work starts. Call {PHONE}.",
        f"/services/{s['slug']}/",
        bc_schema + faq_schema
    )}
{nav(active="services")}
{bc}

<section class="{hero_class}"{hero_style}>
  <div class="container">
    <p class="eyebrow">Family-owned remodeling on Long Island</p>
    <h1>{s['name']} on Long Island</h1>
    <p>{s['tagline']}</p>
    <ul class="check-list hero-benefits">
      {benefits}
    </ul>
    <div class="hero-actions">
      <a href="/request-service.html" class="btn btn-secondary btn-lg">Get My Free Design Preview</a>
      <a href="tel:{PHONE_RAW}" class="btn btn-outline-white">Call {PHONE}</a>
    </div>
  </div>
</section>

<section class="section">
  <div class="container content-sidebar-layout">
    <div class="content-main">
      <h2>Family-owned, Long Island based</h2>
      <p>{TRUST_1}</p>
      <p>{TRUST_2}</p>
      {reviews_badge()}
      <h2>{s['coversTitle']}</h2>
      <div class="features-grid covers-grid">
        {covers}
      </div>
      <h2>From first visit to finished room</h2>
      <div class="steps-grid">
        {steps}
      </div>
      <h2>{s['pricingTitle']}</h2>
      <p>{s['pricing']}</p>
      <div class="pricing-card">
        <h3>Your quote — {NAME}</h3>
        <ul class="check-list">
          <li>Free custom design preview</li>
          <li>One dedicated team, start to finish</li>
          <li>Written quote before any work starts</li>
        </ul>
        <p>{s['priceFactors']}</p>
        {reviews_badge()}
      </div>
{work_html}      <h2>Before you call</h2>
      <div class="faq-list">
        {faq_items}
      </div>
      <h2>{s['name']} across Long Island</h2>
      <p>We provide {s['name'].lower()} throughout Long Island including:</p>
      <div class="city-grid city-grid-sm">
        {service_area_links()}
      </div>
    </div>
    <aside class="content-sidebar">
      {booking_form(compact=True)}
      <div class="sidebar-contact">
        <h4>Contact Us</h4>
        <p>{ICON["phone"]} <a href="tel:{PHONE_RAW}">{PHONE}</a></p>
        <p>{ICON["pin"]} {ADDRESS}</p>
        <p>{ICON['clock']} {B['hours']}</p>
      </div>
    </aside>
  </div>
</section>

<section class="section section-light">
  <div class="container">
    <h2 class="text-center mb-4">What Customers Say</h2>
    <div class="review-grid">{review_cards()}</div>
  </div>
</section>

<section class="section">
  <div class="container">
    <h2 class="text-center mb-4">Other Services We Offer</h2>
    <div class="related-grid">{other_services}</div>
  </div>
</section>

<section class="cta-banner">
  <div class="container">
    <h2>Get a free custom {s['ctaNoun']} design preview</h2>
    <p>Free, no obligation. We call you back the same business day, 8am to 6pm.</p>
    <div class="cta-actions">
      <a href="/request-service.html" class="btn btn-secondary btn-lg">Get My Free Design Preview</a>
      <a href="tel:{PHONE_RAW}" class="btn btn-outline-white btn-lg">Call {PHONE}</a>
    </div>
  </div>
</section>
{footer()}
</body></html>"""
    write(f"services/{s['slug']}/index.html", content)


# ─────────────────────────────────────────────────────────
# PAGE: Services hub
# ─────────────────────────────────────────────────────────

def make_services_hub():
    cards_list = []
    for s in SERVICES:
        cards_list.append(f"""
    <div class="service-card">
      {service_card_header(s)}
      <div class="service-card-body">
        <h3><a href="/services/{s['slug']}/">{s['name']}</a></h3>
        <p>{s['description']}</p>
        <a href="/services/{s['slug']}/" class="card-link">Learn More →</a>
      </div>
    </div>""")
    cards = "\n".join(cards_list)

    bc, bc_schema = breadcrumbs([("Home", "/"), ("Services", None)])
    content = f"""{head(
        f"{B['industry']} | {NAME} | {PHONE}",
        f"{NAME} offers professional {B['industryLower']} in {B['city']}, NY. Call {PHONE} for a free estimate.",
        "/services/",
        bc_schema
    )}
{nav(active="services")}
{bc}
<section class="page-hero">
  <div class="container">
    <h1>Our {B['industry']} Services</h1>
    <p>Professional {B['industryLower']} for Long Island homeowners. Custom work, premium materials, and certified craftsmanship — locally based in {B['city']}, NY.</p>
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="service-grid">{cards}</div>
  </div>
</section>
<section class="cta-banner">
  <div class="container">
    <h2>Not Sure What You Need?</h2>
    <p>Call us and describe your property — we'll recommend the right services and give you a free design preview.</p>
    <div class="cta-actions">
      <a href="/request-service.html" class="btn btn-secondary btn-lg">Get My Free Design Preview</a>
      <a href="tel:{PHONE_RAW}" class="btn btn-outline-white btn-lg">Call {PHONE}</a>
    </div>
  </div>
</section>
{footer()}
</body></html>"""
    write("services/index.html", content)


# ─────────────────────────────────────────────────────────
# PAGE: City / Service Area pages
# ─────────────────────────────────────────────────────────

def make_city_page(area):
    city = area["name"]
    slug = area["slug"]
    county = area["county"]
    name2slug = {a["name"]: a["slug"] for a in AREAS}
    nearby = ", ".join(
        f'<a href="/service-areas/{name2slug[n]}/"><strong>{n}</strong></a>' if n in name2slug else f"<strong>{n}</strong>"
        for n in area["nearbyAreas"]
    )
    bc, bc_schema = breadcrumbs([("Home", "/"), ("Service Areas", "/service-areas/"), (city, None)])

    city_schema = f"""<script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"{B.get('schemaType','LocalBusiness')}",
    "name":"{NAME} — {city}","url":"https://{B['domain']}/service-areas/{slug}/",
    "telephone":"{PHONE}","priceRange":"$$",
    "address":{{"@type":"PostalAddress","addressLocality":"{city}","addressRegion":"{B['state']}","addressCountry":"US"}},
    "areaServed":{{"@type":"City","name":"{city}"}}
  }}
  </script>"""

    service_blocks = "\n".join(
        f"""<div class="city-service">
        <h4><a href="/services/{s["slug"]}/">{s["name"]} in {city}</a></h4>
        <p>{_first_sentence(s["description"])}</p>
      </div>"""
        for s in SERVICES
    )

    content = f"""{head(
        f"{B['industry']} in {city}, NY | {NAME} | {PHONE}",
        f"Professional {B['industryLower']} in {city}, NY. {NAME} serves {city} and {county} County. Call {PHONE} for a free estimate.",
        f"/service-areas/{slug}/",
        bc_schema + city_schema
    )}
{nav(active="areas")}
{bc}

<section class="page-hero">
  <div class="container">
    <h1>{B['industry']} in {city}, NY</h1>
    <p>{NAME} serves {city} and surrounding {county} County homeowners. Free custom design preview and a written quote before any work starts.</p>
    <div class="hero-actions">
      <a href="/request-service.html" class="btn btn-secondary btn-lg">Get My Free Design Preview</a>
      <a href="tel:{PHONE_RAW}" class="btn btn-outline-white">Call {PHONE}</a>
    </div>
  </div>
</section>

<section class="section">
  <div class="container content-sidebar-layout">
    <div class="content-main">
      <h2>Your Local {B['industry']} Experts in {city}</h2>
      <p>When {city} homeowners plan a remodel, an addition or a renovation, they call {NAME} — a family-owned remodeling company based in {B['city']}, serving all of {county} County. No national franchise and no rotating crews: one local team that knows Long Island homes, explains the work in plain language, and stands behind every project.</p>
      <p>From kitchen remodels and bathroom renovations to finished basements, dormers, home additions and full home renovations, we handle every phase of construction for homeowners in {city} — starting with a free custom design preview and one written quote before any work begins.</p>
      {reviews_badge()}

      <h3>Services We Offer in {city}, NY</h3>
      <div class="city-services">
        {service_blocks}
      </div>

      <h3>Areas Near {city} We Also Serve</h3>
      <p>In addition to {city}, we serve {nearby} and more throughout {county} County.
      <a href="/service-areas/">View all service areas →</a></p>
    </div>
    <aside class="content-sidebar">
      {booking_form(compact=True)}
      <div class="sidebar-contact">
        <h4>Contact Us</h4>
        <p>{ICON["phone"]} <a href="tel:{PHONE_RAW}">{PHONE}</a></p>
        <p>{ICON["pin"]} {ADDRESS}</p>
        <p>{ICON['clock']} {B['hours']}</p>
      </div>
    </aside>
  </div>
</section>

<section class="section section-light">
  <div class="container">
    <h2 class="text-center mb-4">What Our Customers Say</h2>
    <div class="review-grid">{review_cards(city)}</div>
  </div>
</section>

<section class="cta-banner">
  <div class="container">
    <h2>Need {B['industry']} in {city}, NY?</h2>
    <p>We're nearby and ready. Get a free custom design preview — free, no obligation. We call you back the same business day, 8am to 6pm.</p>
    <div class="cta-actions">
      <a href="/request-service.html" class="btn btn-secondary btn-lg">Get My Free Design Preview</a>
      <a href="tel:{PHONE_RAW}" class="btn btn-outline-white btn-lg">Call {PHONE}</a>
    </div>
  </div>
</section>
{footer()}
</body></html>"""
    write(f"service-areas/{slug}/index.html", content)


# ─────────────────────────────────────────────────────────
# PAGE: Service Areas hub
# ─────────────────────────────────────────────────────────

def make_areas_hub():
    nassau = [a for a in AREAS if a["county"] == "Nassau"]
    suffolk = [a for a in AREAS if a["county"] == "Suffolk"]
    def area_cards(areas):
        return "\n".join(f"""
        <a href="/service-areas/{a['slug']}/" class="area-card">
          <h3>{a['name']}</h3>
          <span>{a['county']} County</span>
        </a>""" for a in areas)

    bc, bc_schema = breadcrumbs([("Home", "/"), ("Service Areas", None)])
    content = f"""{head(
        f"{B['industry']} Service Areas — Long Island, NY | {NAME}",
        f"{NAME} serves Nassau and Suffolk Counties on Long Island. Click your city to see local {B['industryLower']} services and get a free estimate.",
        "/service-areas/",
        bc_schema
    )}
{nav(active="areas")}
{bc}
<section class="page-hero">
  <div class="container">
    <h1>Long Island {B['industry']} Service Areas</h1>
    <p>{NAME} covers Nassau and Suffolk Counties. Select your city for local {B['industryLower']} information and a free design preview.</p>
  </div>
</section>
<section class="section">
  <div class="container">
    <h2>Nassau County</h2>
    <div class="area-grid">{area_cards(nassau)}</div>
    <h2 class="mt-4">Suffolk County</h2>
    <div class="area-grid">{area_cards(suffolk)}</div>
    <p class="mt-4" style="color:var(--text-mid)">Don't see your city? <a href="tel:{PHONE_RAW}">Call us at {PHONE}</a> — we likely serve your area.</p>
  </div>
</section>
<section class="cta-banner">
  <div class="container">
    <h2>Serving All of Long Island</h2>
    <p>Call or request online for service in your area.</p>
    <div class="cta-actions">
      <a href="/request-service.html" class="btn btn-secondary btn-lg">Get My Free Design Preview</a>
      <a href="tel:{PHONE_RAW}" class="btn btn-outline-white btn-lg">Call {PHONE}</a>
    </div>
  </div>
</section>
{footer()}
</body></html>"""
    write("service-areas/index.html", content)


# ─────────────────────────────────────────────────────────
# PAGE: About
# ─────────────────────────────────────────────────────────

def make_about():
    bc, bc_schema = breadcrumbs([("Home", "/"), ("About Us", None)])
    content = f"""{head(
        f"About Us | {NAME} — {B['city']}, NY",
        f"Learn about {NAME}, Long Island's trusted {B['industryLower']} company based in {B['city']}, NY. Locally owned, licensed, and insured.",
        "/about/",
        bc_schema
    )}
{nav(active="about")}
{bc}
<section class="page-hero">
  <div class="container">
    <h1>About {NAME}</h1>
    <p>Long Island's locally owned {B['industryLower']} company — based in {B['city']}, NY.</p>
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="split-section">
      <div class="split-img about-photo"><img src="/images/custom-home-exterior.jpg" alt="A Long Island home built by {NAME}" width="1200" height="800" /></div>
      <div class="split-content">
        <span class="eyebrow">Who We Are</span>
        <h2>Built for Long Island</h2>
        <p>{NAME} is a locally owned construction and renovation company based in {B['city']}, NY. We serve residential homeowners throughout Nassau and Suffolk Counties.</p>
        <p>We are not a national franchise. Every project is managed by our experienced team, every estimate is honest, and every job is backed by our 100% satisfaction guarantee.</p>
        <ul class="check-list">
          <li>Fully licensed and insured in New York State</li>
          <li>Locally owned — based in {B['city']}, NY</li>
          <li>Experienced crews with background checks</li>
          <li>100% satisfaction guarantee</li>
          <li>Every project starts with a free on-site consultation</li>
        </ul>
      </div>
    </div>
  </div>
</section>
<section class="section section-light">
  <div class="container">
    <div class="section-header">
      <span class="eyebrow">Our Promise</span>
      <h2>The Green Empire Difference</h2>
    </div>
    <div class="features-grid">
      <div class="feature-card"><h3>Local Expertise</h3><p>We know Long Island's building codes, municipalities, and neighborhoods. Our work is designed for this market.</p></div>
      <div class="feature-card"><h3>Transparent Pricing</h3><p>You will always know what you are paying before we start. Detailed written quotes, no surprises, no hidden fees.</p></div>
      <div class="feature-card"><h3>Satisfaction Guaranteed</h3><p>The job is not finished until it meets your standard. Every project is backed by our full satisfaction guarantee.</p></div>
      <div class="feature-card"><h3>Custom Approach</h3><p>Every project is designed around your home, your vision, and your budget. No cookie-cutter solutions.</p></div>
    </div>
  </div>
</section>
<section class="cta-banner">
  <div class="container">
    <h2>Ready to Work with Us?</h2>
    <p>Call or request a free estimate today.</p>
    <div class="cta-actions">
      <a href="/request-service.html" class="btn btn-secondary btn-lg">Get Free Estimate</a>
      <a href="tel:{PHONE_RAW}" class="btn btn-outline-white btn-lg">Call {PHONE}</a>
    </div>
  </div>
</section>
{footer()}
</body></html>"""
    write("about/index.html", content)


# ─────────────────────────────────────────────────────────
# PAGE: FAQ
# ─────────────────────────────────────────────────────────

def make_faq():
    faq_items = "\n".join(f"""
    <div class="faq-item">
      <button class="faq-question">{f['q']} <span class="faq-icon">+</span></button>
      <div class="faq-answer"><p>{f['a']}</p></div>
    </div>""" for f in FAQS)

    faq_schema_items = json.dumps([{"@type":"Question","name":f["q"],"acceptedAnswer":{"@type":"Answer","text":f["a"]}} for f in FAQS])
    faq_schema = f'<script type="application/ld+json">{{"@context":"https://schema.org","@type":"FAQPage","mainEntity":{faq_schema_items}}}</script>'

    bc, bc_schema = breadcrumbs([("Home", "/"), ("FAQ", None)])
    content = f"""{head(
        f"FAQ — {B['industry']} Questions Answered | {NAME}",
        f"Common questions about {NAME}'s {B['industryLower']} services in {B['city']}, NY. Get answers about cost, permits, timelines, and more.",
        "/faq/",
        bc_schema + faq_schema
    )}
{nav(active="faq")}
{bc}
<section class="page-hero">
  <div class="container">
    <h1>Frequently Asked Questions</h1>
    <p>Everything you need to know about {NAME}'s services on Long Island.</p>
  </div>
</section>
<section class="section">
  <div class="container" style="max-width:800px">
    <div class="faq-list">{faq_items}</div>
    <div class="cta-inline mt-4">
      <p>Still have questions? <a href="tel:{PHONE_RAW}">Call or text us at {PHONE}</a> — we respond within 1 business hour.</p>
    </div>
  </div>
</section>
<section class="cta-banner">
  <div class="container">
    <h2>Ready to Get Started?</h2>
    <div class="cta-actions">
      <a href="/request-service.html" class="btn btn-secondary btn-lg">Get Free Estimate</a>
      <a href="tel:{PHONE_RAW}" class="btn btn-outline-white btn-lg">Call {PHONE}</a>
    </div>
  </div>
</section>
{footer()}
</body></html>"""
    write("faq/index.html", content)


# ─────────────────────────────────────────────────────────
# PAGE: Reviews
# ─────────────────────────────────────────────────────────

def make_reviews():
    all_reviews = "\n".join(f"""
    <div class="review-card">
      <div class="review-stars">{filled_stars(r['rating'])}</div>
      <p class="review-text">"{r['text']}"</p>
      <div class="review-author">{r['name']}</div>
      <div class="review-location">{r['location']}</div>
    </div>""" for r in REVIEWS)

    bc, bc_schema = breadcrumbs([("Home", "/"), ("Reviews", None)])
    content = f"""{head(
        f"Customer Reviews | {NAME} — Long Island, NY",
        f"Read reviews from satisfied customers of {NAME} in {B['city']}, NY and Long Island. See why we're rated 5 stars.",
        "/reviews/",
        bc_schema
    )}
{nav(active="reviews")}
{bc}
<section class="page-hero">
  <div class="container">
    <h1>Customer Reviews</h1>
    <p>See what Long Island homeowners say about {NAME}.</p>
    {reviews_badge()}
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="review-grid">{all_reviews}</div>
    <div class="cta-inline mt-4 text-center">
      <p>Want to leave a review? <a href="https://g.page/r/GOOGLE_REVIEW_LINK/review" target="_blank" rel="noopener">Leave us a Google review →</a></p>
    </div>
  </div>
</section>
<section class="cta-banner">
  <div class="container">
    <h2>Join Our Happy Customers</h2>
    <div class="cta-actions">
      <a href="/request-service.html" class="btn btn-secondary btn-lg">Get Free Estimate</a>
      <a href="tel:{PHONE_RAW}" class="btn btn-outline-white btn-lg">Call {PHONE}</a>
    </div>
  </div>
</section>
{footer()}
</body></html>"""
    write("reviews/index.html", content)


# ─────────────────────────────────────────────────────────
# PAGE: Request Service
# ─────────────────────────────────────────────────────────

def make_request_service():
    bc, bc_schema = breadcrumbs([("Home", "/"), ("Request Service", None)])
    content = f"""{head(
        f"Request a Free Estimate | {NAME} | {PHONE}",
        f"Request a free {B['industryLower']} estimate from {NAME} in {B['city']}, NY. We serve all of Long Island and respond within 1 business hour.",
        "/request-service.html",
        bc_schema
    )}
{nav()}
{bc}
<section class="page-hero">
  <div class="container">
    <h1>Request a Free Estimate</h1>
    <p>Fill out the form and we'll get back to you within 1 business hour. No pressure, no obligation.</p>
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="content-sidebar-layout">
      <div class="content-main">
        <h2>Let's Talk About Your Project</h2>
        <p>Whether it is a single room remodel or a full home addition, we are here to help. Tell us about your project and we will provide a free, transparent estimate.</p>
        <div class="features-grid" style="margin-top:2rem">
          <div class="feature-card">{ICON["phone_lg"]}<h3>Call or Text</h3><p><a href="tel:{PHONE_RAW}">{PHONE}</a><br/>Mon–Sat, 7am–6pm</p></div>
          <div class="feature-card">{ICON["pin_lg"]}<h3>Our Location</h3><p>{ADDRESS}</p></div>
          <div class="feature-card">{ICON["timer_lg"]}<h3>Response Time</h3><p>Within 1 business hour</p></div>
        </div>
        <div style="margin-top:2rem;border-radius:8px;overflow:hidden">
          <iframe src="{B['googleMapsEmbed']}" width="100%" height="300" style="border:0;display:block" allowfullscreen loading="lazy" title="{NAME} Location Map"></iframe>
        </div>
      </div>
      <aside class="content-sidebar">
        {booking_form()}
      </aside>
    </div>
  </div>
</section>
{footer()}
</body></html>"""
    write("request-service.html", content)


# ─────────────────────────────────────────────────────────
# PAGE: Thank You
# ─────────────────────────────────────────────────────────

def make_thank_you():
    content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" /><meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Request Received | {NAME}</title>
  <meta name="robots" content="noindex" />
  <link rel="icon" href="/images/favicon.svg" type="image/svg+xml" />
  <link rel="apple-touch-icon" href="/images/logo.png" />
  <link rel="manifest" href="/manifest.json" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="{FONT_URL}" rel="stylesheet" media="print" onload="this.media='all'" />
  <noscript><link href="{FONT_URL}" rel="stylesheet" /></noscript>
  <link rel="stylesheet" href="/css/bundle.css?v=8" />
</head>
<body>
<header class="site-header">
  <nav class="main-nav"><div class="container nav-inner">
    <a href="/" class="nav-logo"><img src="/images/logo.png" alt="{NAME}" width="48" height="48" /></a>
    <a href="tel:{PHONE_RAW}" class="nav-phone">{PHONE}</a>
  </div></nav>
</header>

<section class="ty-hero">
  <div class="container ty-hero-inner">
    <div class="ty-check">
      <svg viewBox="0 0 52 52" fill="none" xmlns="http://www.w3.org/2000/svg" width="64" height="64">
        <circle cx="26" cy="26" r="26" fill="var(--green-light)"/>
        <path d="M15 27l8 8 14-16" stroke="#fff" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </div>
    <h1>Your Request Was Received</h1>
    <p>Thanks for contacting {NAME}. A member of our team will reach out to you within <strong>1 business hour</strong>.</p>
    <a href="tel:{PHONE_RAW}" class="btn btn-primary btn-lg">Call Us Now — {PHONE}</a>
  </div>
</section>

<section class="section section-light">
  <div class="container">
    <div class="section-header">
      <span class="eyebrow">What Happens Next</span>
      <h2>Here's What to Expect</h2>
    </div>
    <div class="steps-grid">
      <div class="step-card">
        <div class="step-number">1</div>
        <h3 class="step-title">We'll Be in Touch</h3>
        <p class="step-desc">Expect a call or text from our team the same business day. We'll confirm your request and answer any questions you have right away.</p>
      </div>
      <div class="step-card">
        <div class="step-number">2</div>
        <h3 class="step-title">Free On-Site Consultation</h3>
        <p class="step-desc">We'll visit your property, walk the space with you, and listen to your vision. No pressure — just an honest conversation about what's possible.</p>
      </div>
      <div class="step-card">
        <div class="step-number">3</div>
        <h3 class="step-title">Your Custom Quote</h3>
        <p class="step-desc">You'll receive a detailed, transparent quote before any work begins. No surprises, no hidden fees — just clear pricing for exactly what you asked for.</p>
      </div>
    </div>
  </div>
</section>

<section class="section">
  <div class="container" style="text-align:center;max-width:560px;margin:0 auto">
    <h2>While You Wait</h2>
    <p style="color:var(--gray-mid);margin-bottom:2rem">Browse our services to get inspired, or read what Long Island homeowners are saying about us.</p>
    <div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap">
      <a href="/services/" class="btn btn-outline">Browse Services</a>
      <a href="/reviews/" class="btn btn-outline">Read Reviews</a>
    </div>
  </div>
</section>

{footer()}
</body></html>"""
    write("thank-you.html", content)


# ─────────────────────────────────────────────────────────
# PAGES: Blog articles
# ─────────────────────────────────────────────────────────

ARTICLES = [
    {
        "slug": "15-amp-vs-20-amp-outlets",
        "img": "/images/drive-article-outlets.jpg",
        "imgAlt": "Installing a new GFCI electrical outlet",
        "title": "15 Amp vs. 20 Amp Outlets: What's the Difference?",
        "desc": "15 amp and 20 amp outlets look almost the same, but they are not interchangeable. How to tell them apart, where each one belongs, and the mistakes that cause trouble — from the Green Empire Builders team.",
        "body": """
<p>Walk into any Long Island home and you will see both kinds of outlets — often in the same room. A 15 amp outlet and a 20 amp outlet look nearly identical, and most homeowners never think about the difference. Until a breaker keeps tripping, or an inspection flags it during a remodel. Here is how to tell them apart, and where each one actually belongs.</p>
<h2>How to Spot the Difference</h2>
<p>Look at the slots. A <strong>15 amp outlet</strong> has two vertical slots and a roundish ground hole below them. A <strong>20 amp outlet</strong> looks the same at first glance — but one of the vertical slots also has a horizontal line branching off it, forming a sideways "T". That little T is the giveaway: it is shaped to accept a 20 amp plug, which has one horizontal prong.</p>
<h2>Where 15 Amp Outlets Belong</h2>
<ul>
  <li>Standard household items: TVs, lamps, toasters, vacuums and computers</li>
  <li>They must be on a 15 amp circuit — or on a 20 amp circuit that has multiple receptacles</li>
  <li>They accept 15 amp plugs only</li>
  <li>Never install one as the only outlet on a 20 amp circuit</li>
</ul>
<h2>Where 20 Amp Outlets Belong</h2>
<ul>
  <li>High-powered items: sump pumps, large refrigerators, window air conditioners and shop tools</li>
  <li>They must be on a 20 amp circuit</li>
  <li>Required when the circuit has only one receptacle</li>
  <li>They accept both 15 amp and 20 amp plugs</li>
  <li>Never install one on a 15 amp circuit — the outlet would promise power the wiring cannot safely deliver</li>
</ul>
<h2>Why This Comes Up in Almost Every Remodel</h2>
<p>Kitchens and bathrooms are the rooms we remodel most, and they are exactly where outlet ratings matter. Modern kitchen countertop circuits are 20 amp circuits, because kettles, air fryers and espresso machines draw real power. When we open up a kitchen or bathroom during a <a href="/services/kitchen-remodeling/">kitchen remodel</a> or a <a href="/services/bathroom-remodeling/">bathroom remodel</a>, checking the circuits and outlets is part of the job — it is far cheaper to correct while the walls are open than after the tile is set.</p>
<p>Not sure what is behind your walls? That is what the first visit is for. <a href="/request-service.html">Request a free design preview</a> and we will walk the space with you, answer questions like these in plain language, and put one written price in front of you before any work starts.</p>"""
    },
    {
        "slug": "how-a-bathroom-remodel-works",
        "img": "/images/drive-hero-bath.jpg",
        "imgAlt": "Bathroom remodel with a double vanity and glass walk-in shower by Green Empire Builders",
        "title": "How a Bathroom Remodel Actually Works, Step by Step",
        "desc": "Design, demolition, plumbing, waterproofing, tile and finishing — the real order of a bathroom remodel, what happens at each stage, and how long it takes on Long Island.",
        "body": f"""
<p>Most homeowners know what they want their new bathroom to look like. What they don't know — and what causes most of the stress — is what actually happens between the first visit and the final walkthrough. Here is the order we work in at {NAME}, and why the order matters.</p>
<h2>Step 1: Design and Materials Come First</h2>
<p>Before anything is demolished, the design is settled and the materials are chosen: tile, vanity, fixtures, glass. This is not paperwork — tile and fixtures can take weeks to arrive, and ordering them first is the difference between a remodel that flows and one that stalls halfway. At this stage you also get your design preview and one written price for the whole project.</p>
<h2>Step 2: Demolition</h2>
<p>The old bathroom comes out — fixtures, tile, vanity, and down to the studs where the room needs it. Demo is fast, usually a day or two, and it is the moment hidden problems show themselves: old water damage, tired plumbing, wiring that was never right. Better to find them now than after the new tile is up.</p>
<h2>Step 3: Plumbing and Electrical Rough-In</h2>
<p>With the walls open, the plumber and electrician set everything that will live behind them: shower valves, drains, supply lines, lighting and exhaust. If the layout is changing — a tub becoming a <a href="/services/bathroom-remodeling/">walk-in shower</a>, a vanity moving across the room — this is when it happens.</p>
<h2>Step 4: Waterproofing</h2>
<p>The step nobody sees and everybody depends on. The shower and wet areas are waterproofed before a single tile is set. Skipping or rushing this stage is how new bathrooms end up leaking into the floor below within a few years.</p>
<h2>Step 5: Tile, Then Fixtures</h2>
<p>Floor and wall tile go in, then the room starts looking like a bathroom again: vanity, mirror, toilet, lighting, and the shower glass or door. This is the longest visible stretch of the project, and the stage where craftsmanship shows.</p>
<h2>Step 6: Finishing and Walkthrough</h2>
<p>Paint, trim, hardware, a full clean — and then we walk the room with you, item by item, before the job is called done.</p>
<h2>How Long Does It All Take?</h2>
<p>A full bathroom remodel usually takes <strong>3 to 5 weeks</strong> once work starts. The biggest variables are the size of the room, whether the layout changes, and how early the materials were ordered — which is why step 1 happens before anyone picks up a hammer.</p>
<p>Thinking about your own bathroom? Start with a <a href="/request-service.html">free design preview</a>: we come to your home, measure the room, talk through what you want, and give you one written price before any work begins.</p>"""
    },
    {
        "slug": "signs-your-roof-needs-replacing",
        "img": "/images/drive-article-roof.jpg",
        "imgAlt": "A finished architectural shingle roof by Green Empire Builders",
        "title": "Signs Your Roof Needs Replacing — and Why Waiting Costs More",
        "desc": "Curling shingles, leaks and granules in the gutters are warnings, not quirks. The signs a roof is at the end of its life — and why the roof you replace too late costs the most.",
        "body": """
<p>There is an old line in our business: the most expensive roof is the one you waited too long to replace. A roof rarely fails all at once. It warns you first — quietly, for a season or two — and the cost of the job depends mostly on whether you act on the warnings or on the leak.</p>
<h2>Signs Your Roof Is at the End of Its Life</h2>
<ul>
  <li><strong>Age.</strong> Most asphalt shingle roofs last 20 to 25 years. If yours is in that range, it is on borrowed time even if it looks fine from the street.</li>
  <li><strong>Curling, cracked or missing shingles.</strong> Shingles that curl at the edges or blow off in every storm have lost their ability to shed water.</li>
  <li><strong>Granules in the gutters.</strong> Those sand-like grains are the shingles' protective surface. When they wash off in quantity, the shingles are wearing out.</li>
  <li><strong>Stains and leaks inside.</strong> Water spots on ceilings or walls mean water is already getting past the roof — the visible stain is the last stop, not the first.</li>
  <li><strong>A sagging roofline.</strong> A dip or sag can mean the decking underneath is soft from moisture. That is no longer just a roofing question.</li>
  <li><strong>Daylight in the attic.</strong> If you can see light through the roof boards, water has a way in too.</li>
</ul>
<h2>Why Waiting Costs More</h2>
<p>A roof replacement is a defined job. A roof replacement plus rotted decking, soaked insulation, mold remediation and a repaired ceiling is a much bigger one. Water that gets under tired shingles does not stay in one place — it travels, and it damages structure, wiring and finishes on the way. Replacing a roof on time is really about protecting everything underneath it: your home's structure, its energy efficiency, and the rooms you have already invested in.</p>
<h2>Planning an Addition or Renovation? Check the Roof First</h2>
<p>This is the conversation we have most often. A homeowner planning a <a href="/services/home-additions/">second-story addition</a>, a <a href="/services/dormer-construction/">dormer</a> or a <a href="/services/full-home-renovation/">full home renovation</a> is about to build on top of the existing roof. If that roof has only a few good years left, the plan should account for it — building new work over a failing roof means paying to open the same areas twice.</p>
<p>If you are planning a project and are not sure about your roof, ask us to look while we are there. The first visit is free: <a href="/request-service.html">request a free design preview</a> and we will give you an honest read — and one written price — before any work starts.</p>"""
    },
]


def make_blog_pages():
    cards = "\n".join(f"""
    <div class="blog-card">
      <a href="/blog/{p['slug']}/"><img class="blog-card-img" src="{p['img']}" alt="{p['imgAlt']}" loading="lazy" /></a>
      <h3><a href="/blog/{p['slug']}/">{p['title']}</a></h3>
      <p>{p['desc']}</p>
      <a href="/blog/{p['slug']}/" class="read-more">Read the article →</a>
    </div>""" for p in ARTICLES)
    bc, bc_schema = breadcrumbs([("Home", "/"), ("Articles", None)])
    index = f"""{head(
        f"Articles & Guides | {NAME}",
        f"Remodeling know-how from {NAME}: practical, plain-language guides for Long Island homeowners — outlets, bathrooms, roofs and planning a project.",
        "/blog/",
        bc_schema
    )}
{nav(active="blog")}
{bc}
<section class="page-hero">
  <div class="container">
    <p class="eyebrow">From the Green Empire Builders team</p>
    <h1>Articles &amp; Guides</h1>
    <p>Practical answers to the questions Long Island homeowners ask us — the same topics we share on Instagram and Facebook, in full, readable form.</p>
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="blog-grid">{cards}</div>
  </div>
</section>
<section class="cta-banner">
  <div class="container">
    <h2>Have a Project in Mind?</h2>
    <p>Free, no obligation. We call you back the same business day, 8am to 6pm.</p>
    <div class="cta-actions">
      <a href="/request-service.html" class="btn btn-secondary btn-lg">Get My Free Design Preview</a>
      <a href="tel:{PHONE_RAW}" class="btn btn-outline-white btn-lg">Call {PHONE}</a>
    </div>
  </div>
</section>
{footer()}
</body></html>"""
    write("blog/index.html", index)

    for post in ARTICLES:
        bc, bc_schema = breadcrumbs([("Home", "/"), ("Articles", "/blog/"), (post["title"][:40] + "…", None)])
        content = f"""{head(
            f"{post['title']} | {NAME}",
            post["desc"],
            f"/blog/{post['slug']}/",
            bc_schema
        )}
{nav(active="blog")}{bc}
<section class="page-hero">
  <div class="container">
    <h1>{post['title']}</h1>
  </div>
</section>
<section class="section">
  <div class="container blog-post-layout">
    <article class="blog-post-body">
      <img class="article-hero-img" src="{post['img']}" alt="{post['imgAlt']}" />
      {post['body']}
      <div class="blog-post-cta">
        <h3>Planning a Project Like This?</h3>
        <p>{NAME} serves all of Long Island — Nassau &amp; Suffolk Counties. Start with a free custom design preview and one written quote before any work begins.</p>
        <a href="/request-service.html" class="btn btn-primary">Get My Free Design Preview</a>
      </div>
    </article>
    <aside class="blog-post-sidebar">
      {booking_form(compact=True)}
      <div class="sidebar-services">
        <h4>Our Services</h4>
        <ul>{"".join(f'<li><a href="/services/{s["slug"]}/">{s["name"]}</a></li>' for s in SERVICES)}</ul>
      </div>
    </aside>
  </div>
</section>
{footer()}
</body></html>"""
        write(f"blog/{post['slug']}/index.html", content)


# ─────────────────────────────────────────────────────────
# PAGE: Privacy Policy & Terms (boilerplate)
# ─────────────────────────────────────────────────────────

def make_legal():
    for slug, title, body in [
        ("privacy-policy", "Privacy Policy", f"<p>{NAME} respects your privacy. We collect contact information submitted through our forms solely to respond to your service inquiry. We do not sell or share your information with third parties. For questions, call {PHONE}.</p>"),
        ("terms", "Terms of Use", f"<p>By using this website, you agree to these terms of use. All content on this site is owned by {NAME}. Unauthorized reproduction is prohibited. For questions, contact us at {PHONE}.</p>"),
        ("accessibility", "Accessibility", f"<p>{NAME} is committed to ensuring this website is accessible to people with disabilities. If you experience any difficulty, please call us at {PHONE} and we will assist you.</p>"),
    ]:
        bc, bc_schema = breadcrumbs([("Home", "/"), (title, None)])
        content = f"""{head(f"{title} | {NAME}", f"{title} for {NAME}, {B['city']}, NY.", f"/{slug}.html", bc_schema)}
{nav()}{bc}
<section class="page-hero"><div class="container"><h1>{title}</h1></div></section>
<section class="section"><div class="container" style="max-width:800px">{body}</div></section>
{footer()}</body></html>"""
        write(f"{slug}.html", content)


# ─────────────────────────────────────────────────────────
# PAGE: Sitemap + Robots
# ─────────────────────────────────────────────────────────

def make_sitemap():
    from datetime import date
    today = date.today().isoformat()
    urls = [("/", "1.0", "weekly")]
    urls += [(f"/services/{s['slug']}/", "0.9", "monthly") for s in SERVICES]
    urls += [("/services/", "0.8", "monthly")]
    urls += [(f"/service-areas/{a['slug']}/", "0.8", "monthly") for a in AREAS]
    urls += [("/service-areas/", "0.7", "monthly")]
    urls += [("/about/", "0.6", "monthly"), ("/faq/", "0.7", "monthly"),
             ("/reviews/", "0.6", "monthly"), ("/request-service.html", "0.8", "monthly")]
    urls += [("/blog/", "0.7", "weekly")]
    urls += [(f"/blog/{p['slug']}/", "0.6", "monthly") for p in ARTICLES]
    items = "\n".join(f"""  <url>
    <loc>https://{B['domain']}{u}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>{freq}</changefreq>
    <priority>{pri}</priority>
  </url>""" for u, pri, freq in urls)
    write("sitemap.xml", f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{items}
</urlset>""")

def make_robots():
    write("robots.txt", f"""User-agent: *
Allow: /
Disallow: /thank-you.html

Sitemap: https://{B['domain']}/sitemap.xml
""")


# ─────────────────────────────────────────────────────────
# RUN ALL GENERATORS
# ─────────────────────────────────────────────────────────

print(f"Generating {NAME} site...\n")

make_theme_css()
make_bundle_css()
make_homepage()
make_services_hub()
for s in SERVICES:
    make_service_page(s)
make_areas_hub()
for a in AREAS:
    make_city_page(a)
make_about()
make_faq()
make_reviews()
make_blog_pages()
make_request_service()
make_thank_you()
make_legal()
make_sitemap()
make_robots()
make_llms()

print(f"[OK] {len(pages_created)} pages generated:\n")
for p in sorted(pages_created):
    print(f"   {p}")

if pages_failed:
    print(f"\n[FAIL] {len(pages_failed)} failed:")
    for p in pages_failed:
        print(f"   {p}")

print(f"\nTotal: {len(pages_created)} pages")
