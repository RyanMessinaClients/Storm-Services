"""Merge bio, services, and faith-based pages into the existing single-page index.html
using hash-routed navigation (#/home, #/bio, #/services, #/faith).

Reads:
  - C:/Users/Ryanm/Downloads/index.html  (current home-only file)
  - C:/Users/Ryanm/Downloads/storm-handoff-extracted/.../storm-colleton.html
  - .../services.html
  - .../faith-based.html

Writes:
  - C:/Users/Ryanm/Downloads/index.html  (overwrites with combined version)
"""
import re
from pathlib import Path

HOME_PATH = Path('C:/Users/Ryanm/Downloads/index.html')
BUNDLE = Path('C:/Users/Ryanm/Downloads/storm-handoff-extracted/private-security-website-storm/project')

home = HOME_PATH.read_text(encoding='utf-8')
bio = (BUNDLE / 'storm-colleton.html').read_text(encoding='utf-8')
services = (BUNDLE / 'services.html').read_text(encoding='utf-8')
faith = (BUNDLE / 'faith-based.html').read_text(encoding='utf-8')

# ---------- helpers ----------
def get_style(html):
    m = re.search(r'<style>(.*?)</style>', html, re.DOTALL)
    return m.group(1) if m else ''

def get_body(html):
    m = re.search(r'<body[^>]*>(.*)</body>', html, re.DOTALL)
    return m.group(1) if m else ''

def page_css(html):
    """Return the page's full <style> block. Duplicates of shared rules are harmless —
    later cascade wins, and rules like .grad-blue / .section-h2 sizing are page-specific."""
    return get_style(html)

def strip_chrome(body):
    """Remove the page's own <nav>, <footer>, and trailing <script> blocks."""
    body = re.sub(r'<!--\s*NAV\s*-->\s*<nav[^>]*>.*?</nav>', '', body, count=1, flags=re.DOTALL)
    body = re.sub(r'<nav[^>]*id=["\']mainNav["\'].*?</nav>', '', body, count=1, flags=re.DOTALL)
    body = re.sub(r'<!--\s*FOOTER\s*-->\s*<footer[^>]*>.*?</footer>', '', body, count=1, flags=re.DOTALL)
    body = re.sub(r'<footer[^>]*>.*?</footer>', '', body, count=1, flags=re.DOTALL)
    # remove every <script>...</script> in the body (forms still have onsubmit attrs)
    body = re.sub(r'<script\b[^>]*>.*?</script>', '', body, flags=re.DOTALL)
    return body.strip()

def get_handler_funcs(html):
    """Pull out top-level `function handle*Submit(...) { ... }` declarations from inline scripts."""
    body = get_body(html)
    scripts = re.findall(r'<script[^>]*>(.*?)</script>', body, re.DOTALL)
    out = []
    for s in scripts:
        for m in re.finditer(r'function\s+(handle\w+Submit)\s*\([^)]*\)\s*\{', s):
            depth = 1
            i = m.end()
            while i < len(s) and depth > 0:
                if s[i] == '{':
                    depth += 1
                elif s[i] == '}':
                    depth -= 1
                i += 1
            out.append(s[m.start():i])
    return '\n\n'.join(out)

# ---------- extract page CSS, body, handlers ----------
bio_css      = page_css(bio)
services_css = page_css(services)
faith_css    = page_css(faith)

bio_body      = strip_chrome(get_body(bio))
services_body = strip_chrome(get_body(services))
faith_body    = strip_chrome(get_body(faith))

bio_funcs      = get_handler_funcs(bio)
services_funcs = get_handler_funcs(services)
faith_funcs    = get_handler_funcs(faith)

# ---------- assemble injected CSS ----------
ROUTING_CSS = """
/* ============ HASH-ROUTED PAGE WRAPPERS ============ */
.page{display:none;}
.page.active{display:block;}
/* Each non-home page renders its own footer; hide them when not active is automatic */

/* ============ BIO PAGE (storm-colleton) ============ */
""" + bio_css + """

/* ============ SERVICES PAGE ============ */
""" + services_css + """

/* ============ FAITH-BASED PAGE ============ */
""" + faith_css + """
"""

# Inject CSS before final </style> in <head>
home_new = re.sub(r'</style>', ROUTING_CSS + '\n</style>', home, count=1)

# ---------- update nav links to route hashes ----------
# Original nav block (in home):
#   <li><a href="index.html">Home</a></li>
#   <li><a href="storm-colleton.html">Storm Colleton</a></li>
#   <li><a href="faith-based.html" style="color:var(--blue-b);">Faith-Based</a></li>
#   <li><a href="#contact">Contact</a></li>
new_nav_links = '''<ul class="nav-links">
    <li><a href="#/home" data-route="home" class="active">Home</a></li>
    <li><a href="#/bio" data-route="bio">Storm Colleton</a></li>
    <li><a href="#/services" data-route="services">Services</a></li>
    <li><a href="#/faith" data-route="faith" style="color:var(--blue-b);">Faith-Based</a></li>
    <li><a href="#" onclick="event.preventDefault();scrollToContact();">Contact</a></li>
  </ul>'''

home_new = re.sub(
    r'<ul class="nav-links">.*?</ul>',
    new_nav_links,
    home_new,
    count=1,
    flags=re.DOTALL,
)

# Make nav-right "Consultation" / "Request Protection" buttons context-aware too
home_new = re.sub(
    r'<a href="#contact" class="btn btn-ghost">Consultation</a>',
    '<a href="#" onclick="event.preventDefault();scrollToContact();" class="btn btn-ghost">Consultation</a>',
    home_new,
    count=1,
)
home_new = re.sub(
    r'<a href="#contact" class="btn btn-blue">Request Protection</a>',
    '<a href="#" onclick="event.preventDefault();scrollToContact();" class="btn btn-blue">Request Protection</a>',
    home_new,
    count=1,
)

# ---------- swap inter-page anchor hrefs to route hashes ----------
# These appear in home (More Services button) and inside the included pages' bodies (back-to-main, etc).
def route_swap(html):
    html = re.sub(r'href="index\.html(?:#contact)?"', 'href="#/home"', html)
    html = re.sub(r'href="storm-colleton\.html"', 'href="#/bio"', html)
    html = re.sub(r'href="services\.html"', 'href="#/services"', html)
    html = re.sub(r'href="faith-based\.html"', 'href="#/faith"', html)
    return html

home_new = route_swap(home_new)
bio_body = route_swap(bio_body)
services_body = route_swap(services_body)
faith_body = route_swap(faith_body)

# ---------- wrap home content in <div class="page active" id="page-home"> ----------
# Open div right after </nav>
home_new = home_new.replace(
    '</nav>',
    '</nav>\n\n<!-- ============ HOME PAGE ============ -->\n<div class="page active" id="page-home">',
    1,
)
# Close div right after the home page's </footer> (before the trailing inline <script> blocks)
# Match the FIRST </footer> after the page-home opener (home has only one footer).
home_new = home_new.replace(
    '</footer>',
    '</footer>\n</div>\n',
    1,
)

# ---------- inject the other three pages right after </div> close ----------
SHARED_FOOTER = '''<footer>
  <div class="footer-copy">© 2025 Storm Colleton & Associates. All rights reserved.</div>
  <div style="font-size:12px;color:var(--text-3);">Aberdeen, NJ &nbsp;·&nbsp; Mon–Fri: 9:00 AM – 6:00 PM</div>
  <a href="#/home" class="footer-back">← Back to Home</a>
</footer>'''

other_pages = f'''
<!-- ============ BIO PAGE ============ -->
<div class="page" id="page-bio">
{bio_body}
{SHARED_FOOTER}
</div>

<!-- ============ SERVICES PAGE ============ -->
<div class="page" id="page-services">
{services_body}
{SHARED_FOOTER}
</div>

<!-- ============ FAITH-BASED PAGE ============ -->
<div class="page" id="page-faith">
{faith_body}
{SHARED_FOOTER}
</div>
'''

# Insert other_pages before the first <script> that follows the closing </div> we just added.
# Anchor: the very next <script> tag after our injected `</div>\n` marker.
home_new = home_new.replace(
    '</footer>\n</div>\n',
    '</footer>\n</div>\n' + other_pages,
    1,
)

# ---------- inject routing JS + page-specific form handlers before </body> ----------
ROUTING_JS = '''
<script>
/* =================== HASH ROUTING =================== */
(function(){
  function showPage(){
    var h = window.location.hash;
    var route = 'home';
    if (h.indexOf('#/') === 0) {
      route = h.slice(2) || 'home';
    } else if (h && h !== '#') {
      // Internal anchor (e.g. #contact). Don't switch pages — let browser scroll within the active page.
      return;
    }
    document.querySelectorAll('.page').forEach(function(p){ p.classList.remove('active'); });
    var target = document.getElementById('page-' + route) || document.getElementById('page-home');
    target.classList.add('active');
    // Update nav active state
    document.querySelectorAll('.nav-links a[data-route]').forEach(function(a){
      a.classList.toggle('active', a.dataset.route === target.id.replace('page-',''));
    });
    // Reset scroll
    window.scrollTo(0, 0);
    // Reveal animations on non-home pages (ScrollTriggers don't fire on display:none sections at load)
    if (target.id !== 'page-home') {
      target.querySelectorAll('.gs-up, .gs-fade, .gs-left, .gs-right, .gs-scale').forEach(function(el){
        el.style.opacity = '1';
        el.style.transform = 'none';
      });
    }
    // Close mobile nav if open
    var navLinks = document.querySelector('.nav-links');
    if (navLinks) navLinks.classList.remove('open');
    // Refresh ScrollTrigger so animations on the now-visible page recalibrate
    if (window.gsap && window.ScrollTrigger) {
      setTimeout(function(){ ScrollTrigger.refresh(); }, 50);
    }
  }
  window.addEventListener('hashchange', showPage);
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', showPage);
  } else {
    showPage();
  }

  // Smart "Contact" nav: scroll to whichever contact section exists on the active page
  window.scrollToContact = function() {
    var active = document.querySelector('.page.active') || document.getElementById('page-home');
    var ids = ['contact', 'sc-contact', 'sv-contact', 'fb-contact'];
    for (var i = 0; i < ids.length; i++) {
      var el = active.querySelector('#' + ids[i]);
      if (el) { el.scrollIntoView({behavior:'smooth', block:'start'}); return; }
    }
    // Fallback: route to home and scroll to its contact section
    if (active.id !== 'page-home') {
      window.location.hash = '#/home';
      setTimeout(function(){
        var c = document.getElementById('contact');
        if (c) c.scrollIntoView({behavior:'smooth'});
      }, 100);
    }
  };
})();
</script>

<script>
/* =================== PAGE FORM HANDLERS =================== */
''' + bio_funcs + '''

''' + services_funcs + '''

''' + faith_funcs + '''
</script>
'''

home_new = home_new.replace('</body>', ROUTING_JS + '\n</body>', 1)

# ---------- update title to be more general ----------
home_new = re.sub(
    r'<title>.*?</title>',
    '<title>Storm Colleton &amp; Associates | Elite Executive Protection</title>',
    home_new,
    count=1,
)

# ---------- write output ----------
HOME_PATH.write_text(home_new, encoding='utf-8')
print(f'Wrote {len(home_new):,} chars to {HOME_PATH}')
print(f'  bio_css: {len(bio_css):,}')
print(f'  services_css: {len(services_css):,}')
print(f'  faith_css: {len(faith_css):,}')
print(f'  bio_body: {len(bio_body):,}')
print(f'  services_body: {len(services_body):,}')
print(f'  faith_body: {len(faith_body):,}')
print(f'  bio_funcs: {len(bio_funcs):,}')
print(f'  services_funcs: {len(services_funcs):,}')
print(f'  faith_funcs: {len(faith_funcs):,}')
