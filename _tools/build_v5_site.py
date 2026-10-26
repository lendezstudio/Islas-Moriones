"""Version 5 site generator (Amanpulo-inspired 'Warm Island Elegance').
Writes every page with a shared header/footer. Reuses the verified Café menu, FAQ and pet policy
from the current pages. Run from the project root:  python _tools/build_v5_site.py"""
import os, re, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def rd(p):
    with open(os.path.join(ROOT, p), encoding='utf-8') as f: return f.read()
def wr(p, s):
    with open(os.path.join(ROOT, p), 'w', encoding='utf-8', newline='\n') as f: f.write(s)
    print('wrote', p)

BOOK = 'https://book-directonline.com/properties/IslasMorionesBeachResortdirect'
FB = 'https://www.facebook.com/islasmorionesbeachresort'
WA = 'https://wa.me/639178925752'
BCOM = 'https://www.booking.com/hotel/ph/islas-moriones-beach-resort.html'
MAIL = 'islasmoriones.cmhi@gmail.com'
NEWTAB = '<span class="visually-hidden"> (opens in a new tab)</span>'
BOOKTAB = '<span class="visually-hidden"> (opens the booking site in a new tab)</span>'
V = '8.0'

# ---------- reusable verified chunks from the current pages (read before overwriting) ----------
MENU, FAQ, PETS = rd('_tools/content/menu.html'), rd('_tools/content/faq.html'), rd('_tools/content/pets.html')
MENU = MENU.replace('<h3 class="visually-hidden">', '<h3 class="visually-hidden">')
# FAQ updates from the 2026 brochure (Wi-Fi and 24-hour electricity are now client-confirmed)
FAQ = FAQ.replace('<p>Yes. The resort has a 75 kVA backup diesel generator.</p>',
                  '<p>Yes. The resort lists 24-hour electricity, supported by a 75 kVA backup diesel generator.</p>')
FAQ = FAQ.replace('<span>Is there backup power?</span>', '<span>Is there electricity and Wi-Fi?</span>')
FAQ = FAQ.replace('supported by a 75 kVA backup diesel generator.</p>', 'supported by a 75 kVA backup diesel generator, and Wi-Fi.</p>')

# ---------- image helpers ----------
SIZES = {}
for line in rd('assets/img/v5/manifest.txt').strip().splitlines():
    jid, sizes, _ = line.split('|')
    SIZES[jid] = [tuple(int(n) for n in s.split('x')) for s in sizes.split()]

def pic(jid, alt, sizes='100vw', pos=None, eager=False, cls=''):
    """<picture> for a v5 derivative: WebP with JPEG fallback, responsive widths, reserved size."""
    pos = pos or FOCUS.get(jid, '50% 50%')
    s = SIZES[jid]
    w, h = s[-1]
    webp = ', '.join(f'assets/img/v5/{jid}-{a}.webp {a}w' for a, _ in s)
    jpg = ', '.join(f'assets/img/v5/{jid}-{a}.jpg {a}w' for a, _ in s)
    load = 'fetchpriority="high" decoding="async"' if eager else 'loading="lazy" decoding="async"'
    c = f' class="{cls}"' if cls else ''
    return (f'<picture><source type="image/webp" srcset="{webp}" sizes="{sizes}">'
            f'<img{c} src="assets/img/v5/{jid}-{s[0][0]}.jpg" srcset="{jpg}" sizes="{sizes}" width="{w}" height="{h}" {load} style="--pos: {pos}" alt="{html.escape(alt, quote=True)}"></picture>')

OLD = {  # earlier derivatives (assets/img) still used: id -> (widths, w, h)
    'bamboo-raft': ((720, 1100), 1200, 1600), 'bonfire-circle': ((560, 936), 936, 856),
    'bonfire-night': ((560, 638), 638, 954), 'beach-volleyball': ((720, 1400), 1774, 837),
    'dining-veranda-night': ((560, 936), 936, 856), 'pool-grounds-day': ((720, 1100), 1600, 1200),
    'room-double-standard': ((570,), 570, 364), 'room-suite': ((520,), 520, 398),
    'sunong-bato': ((720, 940), 940, 588), 'palad-sandbar': ((720, 940), 940, 608),
    'beach-outrigger': ((720, 1100), 1290, 1601), 'sunset-boat': ((720, 1400), 1400, 661),
    'hero-dusk-pool': ((720, 1100), 1536, 1880), 'beach-sunset-path': ((560, 900), 1200, 1600),
    'garden-path-beach': ((560, 936), 936, 856), 'kubo-interior-loft': ((560, 936), 936, 856),
    'exp-snorkel': ((700, 1200), 1200, 1500), 'campsite-tents': ((560, 936), 936, 856),
    'night-facade': ((720, 1100), 1600, 1200), 'kubo-exterior': ((560, 936), 936, 856), 'dining-table': ((600,), 600, 600), 'exp-massage': ((800, 1400), 1400, 933), 'exp-karaoke': ((800, 1400), 1400, 788), 'exp-laundry': ((800, 1400), 1400, 933),
}
def old(jid, alt, sizes='100vw', pos='50% 50%'):
    pos = FOCUS.get('old:' + jid, pos)
    widths, w, h = OLD[jid]
    srcset = ', '.join(f'assets/img/{jid}-{a}.jpg {a}w' for a in widths)
    return (f'<img src="assets/img/{jid}-{widths[0]}.jpg" srcset="{srcset}" sizes="{sizes}" width="{w}" height="{h}" '
            f'loading="lazy" decoding="async" style="--pos: {pos}" alt="{html.escape(alt, quote=True)}">')

FOCUS = {  # subject positions for photos whose subject sits off-centre
    'lobby-lounge': '50% 88%', 'maniwaya-cove': '40% 45%', 'beach-loungers': '50% 82%', 'sandbar-boat': '55% 70%',
    'tower-wide': '50% 92%', 'tower-blue': '50% 90%', 'tower-storm': '50% 85%', 'ecart': '50% 100%',
    'bikes-crop': '50% 35%', 'bikes': '50% 100%', 'kayak-pov': '50% 55%', 'kayak-pov-2': '40% 45%', 'beach-loungers': '50% 62%', 'kayak-clear': '50% 100%', 'kayak-clear-2': '50% 100%', 'tents-campsite': '32% 96%',
    'tent': '50% 78%', 'ungab-arch': '50% 70%', 'main-building': '50% 45%', 'genesis-front': '50% 70%',
    'genesis-lawn': '50% 75%', 'palms-sky': '50% 40%', 'maniwaya-rocks': '50% 70%', 'kubo-exterior': '50% 50%',
}

def full(jid):
    """Largest file for the lightbox."""
    if jid in SIZES:
        w, h = SIZES[jid][-1]; return f'assets/img/v5/{jid}-{w}.jpg', w, h
    widths, w, h = OLD[jid]; return f'assets/img/{jid}-{widths[-1]}.jpg', w, h

# ---------- shared layout ----------
NAV = [('rooms.html', 'Stay'), ('activities.html', 'Experiences'), ('dining.html', 'Dining'),
       ('groups.html', 'Gatherings'), ('gallery.html', 'Gallery'), ('getting-here.html', 'Getting Here'),
       ('contact.html', 'Contact')]

def header(cur):
    def a(href, label):
        c = ' aria-current="page"' if href == cur else ''
        return f'<a href="{href}"{c}>{label}</a>'
    nav = '\n'.join(f'          <li>{a(h, t)}</li>' for h, t in NAV)
    menu_items = [('index.html', 'The Resort')] + NAV + [('good-to-know.html', 'Good to Know')]
    menu = '\n'.join(f'          <li style="--i:{i}">{a(h, t)}</li>' for i, (h, t) in enumerate(menu_items))
    return f'''  <header class="site-header" id="top">
    <div class="masthead">
      <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="mobile-menu">
        <span class="menu-toggle__bars" aria-hidden="true"><span></span><span></span></span>
        <span class="menu-toggle__label">Menu</span>
      </button>
      <a class="brand" href="index.html" aria-label="Islas Moriones Beach Resort, home">
        <img src="assets/brand/logo-islas-moriones-teal-380.png" srcset="assets/brand/logo-islas-moriones-teal-380.png 380w, assets/brand/logo-islas-moriones-teal-760.png 760w" sizes="160px" width="380" height="165" alt="Islas Moriones Beach Resort, Marinduque">
      </a>
      <a class="btn btn--teal btn--sm header-cta" href="{BOOK}" target="_blank" rel="noopener">Check Availability{BOOKTAB}</a>
    </div>
    <nav class="subnav" aria-label="Main">
      <ul>
{nav}
      </ul>
    </nav>
    <div class="mobile-menu" id="mobile-menu" hidden>
      <nav aria-label="Main">
        <ol>
{menu}
        </ol>
      </nav>
      <a class="btn btn--teal" href="{BOOK}" target="_blank" rel="noopener">Check Availability{BOOKTAB}</a>
      <p class="mobile-menu__contact"><a href="{WA}" target="_blank" rel="noopener">WhatsApp +63 917 892 5752{NEWTAB}</a><br><a href="mailto:{MAIL}">{MAIL}</a></p>
    </div>
  </header>
'''

FOOTER = f'''  <footer class="site-footer">
    <div class="footer__top">
      <a class="footer__logo" href="index.html" aria-label="Islas Moriones Beach Resort, home">
        <img src="assets/brand/logo-islas-moriones-white-380.png" srcset="assets/brand/logo-islas-moriones-white-380.png 380w, assets/brand/logo-islas-moriones-white-760.png 760w" sizes="190px" width="380" height="165" loading="lazy" alt="Islas Moriones Beach Resort, Marinduque">
      </a>
      <div class="footer__cols">
        <div>
          <p class="footer__label">Islas Moriones Beach Resort</p>
          <p>Maniwaya Island, Santa Cruz,<br>Marinduque, Philippines</p>
        </div>
        <nav aria-label="Footer">
          <p class="footer__label">Explore</p>
          <ul>
            <li><a href="index.html">The Resort</a></li>
            <li><a href="rooms.html">Stay</a></li>
            <li><a href="activities.html">Experiences</a></li>
            <li><a href="dining.html">Dining</a></li>
            <li><a href="groups.html">Gatherings &amp; Events</a></li>
            <li><a href="gallery.html">Gallery</a></li>
            <li><a href="getting-here.html">Getting Here</a></li>
            <li><a href="good-to-know.html">Good to Know</a></li>
            <li><a href="contact.html">Contact</a></li>
          </ul>
        </nav>
        <div>
          <p class="footer__label">Contact</p>
          <ul>
            <li><a href="{BOOK}" target="_blank" rel="noopener">Check Availability{NEWTAB}</a></li>
            <li><a href="{WA}" target="_blank" rel="noopener">WhatsApp +63 917 892 5752{NEWTAB}</a></li>
            <li><a href="mailto:{MAIL}">{MAIL}</a></li>
            <li><a href="{FB}" target="_blank" rel="noopener">Facebook{NEWTAB}</a></li>
            <li><a href="{BCOM}" target="_blank" rel="noopener">Booking.com{NEWTAB}</a></li>
          </ul>
        </div>
      </div>
    </div>
    <div class="footer__base">
      <p>© <span data-year>2026</span> Islas Moriones Beach Resort</p>
      <p class="credit">Designed by <a href="https://lendezstudio.com/" target="_blank" rel="noopener">Lendez Studio{NEWTAB}</a></p>
    </div>
  </footer>

  <a class="mobile-cta btn btn--teal" href="{BOOK}" target="_blank" rel="noopener" data-mobile-cta>Check Availability{BOOKTAB}</a>
'''

LIGHTBOX = '''  <dialog class="lightbox" id="lightbox" aria-label="Photo viewer">
    <div class="lightbox__stage">
      <figure class="lightbox__figure">
        <img alt="" data-lb-img>
        <figcaption><span data-lb-caption></span> <span class="lightbox__count" data-lb-count></span></figcaption>
      </figure>
      <button class="icon-btn lightbox__prev" type="button" data-lb-prev aria-label="Previous image"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 5l-7 7 7 7"/></svg></button>
      <button class="icon-btn lightbox__next" type="button" data-lb-next aria-label="Next image"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 5l7 7-7 7"/></svg></button>
      <button class="icon-btn lightbox__close" type="button" data-lb-close aria-label="Close viewer"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg></button>
    </div>
  </dialog>
'''

def lb_set(name, items):
    """Hidden photo set opened in the lightbox. items: (jid, caption, alt)"""
    lis = []
    for jid, cap, alt in items:
        src, w, h = full(jid)
        lis.append(f'      <li data-full="{src}" data-w="{w}" data-h="{h}" data-caption="{html.escape(cap, quote=True)}" data-alt="{html.escape(alt, quote=True)}"></li>')
    return f'    <ul data-set="{name}">\n' + '\n'.join(lis) + '\n    </ul>\n'

def head(title, desc, preload=''):
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <meta name="theme-color" content="#F1E9DC">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Islas Moriones Beach Resort">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{desc}">
  <meta property="og:image" content="https://lendezstudio.github.io/Islas-Moriones/assets/img/share-preview.jpg">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="The Islas Moriones Beach Resort logo beside outrigger boats on the resort's beach">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" type="image/png" sizes="32x32" href="favicon-32.png">
  <link rel="icon" type="image/png" sizes="48x48" href="favicon-48.png">
  <link rel="icon" type="image/png" sizes="192x192" href="favicon-192.png">
  <link rel="apple-touch-icon" href="apple-touch-icon.png">{preload}
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400&display=swap">
  <link rel="stylesheet" href="assets/css/styles.css?v={V}">
  <script src="assets/js/main.js?v={V}" defer></script>
</head>
'''

def page(fname, cur, title, desc, main, sets='', preload='', canonical=None, extra_head=''):
    canon = canonical or ('https://lendezstudio.github.io/Islas-Moriones/' + ('' if fname == 'index.html' else fname))
    h = head(title, desc, preload).replace('</head>', f'  <link rel="canonical" href="{canon}">\n{extra_head}</head>')
    body = (f'<body class="{"home" if fname == "index.html" else "inner"}">\n  <a class="skip-link" href="#main">Skip to content</a>\n\n'
            + header(cur) + f'\n  <main id="main">\n{main}\n  </main>\n\n' + FOOTER.replace(f'<li><a href="{cur}">', f'<li><a href="{cur}" aria-current="page">', 1)
            + (f'\n  <div hidden>\n{sets}  </div>\n' if sets else '') + '\n' + LIGHTBOX + '</body>\n</html>\n')
    wr(fname, h + body)

def intro(eyebrow, h1, text, extra=''):
    return f'''    <section class="page-intro" aria-labelledby="page-title">
      <div class="prose center">
        <p class="eyebrow">{eyebrow}</p>
        <h1 class="h-display" id="page-title">{h1}</h1>
        <p class="lead">{text}</p>{extra}
      </div>
    </section>
'''

def closing(heading, text):
    return f'''    <section class="closing" aria-labelledby="closing-title">
      <div class="prose center" data-reveal>
        <h2 class="h-section" id="closing-title">{heading}</h2>
        <p>{text}</p>
        <div class="actions actions--center">
          <a class="btn btn--teal" href="{BOOK}" target="_blank" rel="noopener">Check Availability{BOOKTAB}</a>
          <a class="btn btn--line" href="contact.html">Message the Resort</a>
        </div>
      </div>
    </section>
'''

def card(img, title, text, href=None, link=None, extra=''):
    a = f'\n          <a class="text-link" href="{href}">{link} <span aria-hidden="true">→</span></a>' if href else ''
    return f'''        <article class="card" data-reveal>
          <figure class="card__media">{img}</figure>
          <h3 class="h-card">{title}</h3>
          <p>{text}</p>{extra}{a}
        </article>'''

# =====================================================================================  HOME
INCLUDED = [  # (image html, title, caption) all from the resort's inclusion list
    (lambda s: pic('pool-loungers', 'Sun loungers and umbrellas beside the turquoise outdoor pool, shaded by tropical trees', s, '50% 62%'), 'Swimming pool', 'The outdoor pool, with loungers in the shade.'),
    (lambda s: old('beach-volleyball', 'A volleyball net on the resort beach beside clear water', s, '40% 50%'), 'Beach volleyball', 'A net on the sand, a few steps from the water.'),
    (lambda s: old('bamboo-raft', 'The covered bamboo raft with a long table on turquoise water', s, '50% 45%'), 'Bamboo raft', 'Float off the shore on the resort’s bamboo raft.'),
    (lambda s: pic('bonfire-smores', 'Marshmallows toasting on skewers over a campfire at night', s, '55% 50%'), 'Bonfire', 'Evenings around the fire. Photo for illustration.'),
    (lambda s: pic('pingpong-darts', 'A ping-pong table in the resort’s open-sided games room', s, '50% 60%'), 'Ping-pong', 'A games room open to the breeze.'),
    (lambda s: pic('darts', 'A dartboard with darts on a rustic timber board', s, '50% 40%'), 'Darts', 'A dartboard for friendly games.'),
    (lambda s: pic('badminton', 'Two badminton rackets and shuttlecocks resting on grass', s, '50% 55%'), 'Badminton', 'Rackets for a game on the lawn.'),
]
def included_grid(sizes='(min-width: 900px) 30vw, (min-width: 600px) 46vw, 82vw'):
    out = []
    for f, t, c in INCLUDED:
        label = t.replace('&amp;', 'and')
        out.append(f'''            <li class="slide-item" aria-roledescription="slide" aria-label="{label}"><figure class="tile">
              <div class="tile__media">{f(sizes)}</div>            </figure></li>''')
    return '\n'.join(out)


CLOSER = [  # resort photographs, no overlaid text
    ('maniwaya-cove', 'Maniwaya shoreline', 'A small sandy cove below the Maniwaya sign on the rocks, waves washing onto the beach'),
    ('dusk-pool', 'The pool at dusk', 'The pool glowing turquoise beside the two-storey main building at dusk'),
    ('beach-loungers', 'Shade on the sand', 'Wicker sun loungers in the shade of a tree on the beach, the lifeguard tower beyond'),
    ('sandbar-boat', 'Palad Sandbar', 'Aerial view of an outrigger boat moored at the tip of a long white sandbar in turquoise water'),
    ('beach-palms', 'Palms along the shore', 'Palms shading the sand in front of the resort buildings'),
    ('tower-blue', 'The lifeguard tower', 'The lifeguard tower on white sand under a deep blue sky'),
    ('lobby-lounge', 'The lobby lounge', 'The lobby lounge with a leaf-pattern mural and dark sofas'),
]
def closer_slides():
    return '\n'.join(f'''            <li class="slide-item" aria-roledescription="slide" aria-label="{t}"><figure class="tile"><div class="tile__media">{pic(j, alt, "(min-width: 600px) 300px, 68vw")}</div></figure></li>''' for j, t, alt in CLOSER)

home = f'''    <section class="film flow-hero" aria-label="Islas Moriones from the air and on the beach">
      <div class="film__frame">
        <video class="film__video" autoplay muted loop playsinline preload="auto" poster="assets/video/islas-moriones-hero-poster.jpg?v=2" aria-label="Aerial and beach views of Islas Moriones on Maniwaya Island" data-film>
          <source src="assets/video/islas-moriones-hero.mp4?v=4" type="video/mp4">
        </video>
        <div class="film__controls" data-film-controls>
          <button class="film__btn" type="button" data-film-toggle aria-pressed="false" aria-label="Pause the film">
            <svg class="i-pause" viewBox="0 0 24 24" aria-hidden="true"><path d="M9 6v12M15 6v12"/></svg>
            <svg class="i-play" viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5.5l11 6.5-11 6.5z"/></svg>
          </button>
          <button class="film__btn" type="button" data-film-mute aria-pressed="true" aria-label="Turn sound on">
            <svg class="i-muted" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 9h4l5-4v14l-5-4H4zM17 9l4 6M21 9l-4 6"/></svg>
            <svg class="i-sound" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 9h4l5-4v14l-5-4H4zM16.5 8.5a5 5 0 0 1 0 7M19 6a8.5 8.5 0 0 1 0 12"/></svg>
          </button>
          <label class="film__vol"><span class="visually-hidden">Film volume</span><input type="range" min="0" max="1" step="0.05" value="0.6" data-film-volume></label>
        </div>
      </div>
    </section>

    <section class="resort-intro" id="resort" aria-labelledby="resort-title">
      <div class="prose center">
        <p class="eyebrow">Maniwaya Island, Marinduque</p>
        <h1 class="h-display" id="resort-title">Islas Moriones Beach Resort</h1>
        <p class="h-sub">Island days, shared your way.</p>
        <p>On Maniwaya Island, Islas Moriones brings together places to stay, time by the water, and meals worth gathering for. Settle into a room, explore a tent stay, or make space for a few days with your favourite people.</p>
        <div class="actions actions--center">
          <a class="btn btn--teal" href="rooms.html">Explore the stays</a>
          <a class="btn btn--line" href="gallery.html">View the gallery</a>
        </div>
      </div>
    </section>

    <section class="section section--linen" aria-labelledby="glance-title">
      <div class="wrap">
        <div class="feature">
          <figure class="feature__media feature__media--wide" data-reveal>{pic('resort-sign', 'The Islas Moriones Beach Resort sign on the sandy grounds, palms and the main building behind', '(min-width: 900px) 56vw, 92vw', '50% 55%')}</figure>
          <div class="feature__text" data-reveal>
            <p class="eyebrow">The resort at a glance</p>
            <h2 class="h-section" id="glance-title">Everything in one island getaway</h2>
            <p>A beachfront resort on Maniwaya Island, with places to stay, eat, gather and unwind within a few steps of each other.</p>
            <ul class="glance">
              <li><strong>16</strong> air-conditioned rooms</li>
              <li>Outdoor swimming pool</li>
              <li>Spacious camping grounds</li>
              <li>Restaurant and bar</li>
              <li>The Genesis Events Place and conference facilities</li>
              <li>Recreational spaces</li>
              <li>Wi-Fi and 24-hour electricity</li>
            </ul>
          </div>
        </div>
      </div>
    </section>

    <section class="section section--tight" aria-labelledby="closer-title">
      <div class="wrap">
        <header class="section-head center">
          <h2 class="h-section" id="closer-title">A closer look at island life</h2>
          <p>Explore the shoreline, pool, and places to spend time together at Islas Moriones.</p>
        </header>
        <div class="slider slider--plain" data-slider aria-roledescription="carousel" aria-label="Photographs of the resort">
          <ul class="slider__track" data-slider-track tabindex="0">
{closer_slides()}
          </ul>
          <button class="slider__arrow slider__arrow--prev" type="button" data-slider-prev aria-label="Previous photo"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 5l-7 7 7 7"/></svg></button>
          <button class="slider__arrow slider__arrow--next" type="button" data-slider-next aria-label="Next photo"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 5l7 7-7 7"/></svg></button>
        </div>
      </div>
    </section>

    <section class="section section--dune" aria-labelledby="stay-title">
      <div class="wrap">
        <div class="feature">
          <figure class="feature__media" data-reveal>{pic('poolsuite-room', 'Inside the Pool Suite Room: a queen bed with a padded bench, a sofa and a kitchen with a brick breakfast bar', '(min-width: 900px) 56vw, 92vw', '55% 70%')}</figure>
          <div class="feature__text" data-reveal>
            <p class="eyebrow">Stay</p>
            <h2 class="h-section" id="stay-title">Find your place on Maniwaya</h2>
            <p>Discover the resort's accommodations, from the featured Pool Suite Room to tent stays. Take a closer look at each setting before choosing your island escape.</p>
            <p class="label-line">Featured · Pool Suite Room, a standalone building with a balcony and sea view</p>
            <a class="btn btn--teal" href="rooms.html">Explore accommodations</a>
          </div>
        </div>
        <div class="pair">
          <a class="pair__item" href="rooms.html#luxury-kubo" data-reveal>{old('kubo-exterior', 'The thatched Luxury Kubo with its white-railed veranda on the lawn under coconut palms', '(min-width: 700px) 46vw, 92vw', '50% 50%')}<span class="pair__label">Luxury Kubo<small>A thatched-roof stay with a loft and kitchen</small></span></a>
          <a class="pair__item" href="rooms.html#tents" data-reveal>{pic('tents-campsite', 'Tents pitched on the lawn under tall coconut palms beside a thatched cottage', '(min-width: 700px) 46vw, 92vw', '32% 96%')}<span class="pair__label">Tent stays<small>Camp on the grounds under the palms</small></span></a>
        </div>
      </div>
    </section>

    <section class="section" aria-labelledby="included-title">
      <div class="wrap">
        <header class="section-head center">
          <p class="eyebrow">Included with your stay</p>
          <h2 class="h-section" id="included-title">Time to enjoy, already part of your stay</h2>
          <p>Take a closer look at the activities and amenities included for staying guests.</p>
        </header>
        <div class="slider" data-slider aria-roledescription="carousel" aria-label="Included amenities">
          <ul class="slider__track" data-slider-track tabindex="0">
{included_grid()}
          </ul>
          <button class="slider__arrow slider__arrow--prev" type="button" data-slider-prev aria-label="Previous amenities"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 5l-7 7 7 7"/></svg></button>
          <button class="slider__arrow slider__arrow--next" type="button" data-slider-next aria-label="Next amenities"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 5l7 7-7 7"/></svg></button>
        </div>
        <p class="soon center"><span>Coming soon</span> A pickleball court is being built at the resort.</p>
      </div>
    </section>

    <section class="section section--linen" aria-labelledby="exp-title">
      <div class="wrap">
        <header class="section-head section-head--split">
          <div>
            <p class="eyebrow">Experiences</p>
            <h2 class="h-section" id="exp-title">More ways to enjoy the island</h2>
          </div>
          <div>
            <p>Take to the water in a crystal-clear kayak, ask about boat rentals, or explore the experiences available during your visit.</p>
            <a class="text-link" href="activities.html">Discover the experiences <span aria-hidden="true">→</span></a>
          </div>
        </header>
        <div class="cards cards--3">
{card(pic('kayak-float', 'Seen from above, a swimmer floats beside a transparent kayak on turquoise water', '(min-width: 900px) 30vw, 92vw', '50% 50%'), 'Crystal-clear kayaks', 'See the water from a different perspective. Ask the resort about availability and rental arrangements.', 'activities.html#kayaks', 'About the kayaks')}
{card(pic('boat-longinus', 'The resort’s outrigger boat St. Longinus moored in clear shallow water', '(min-width: 900px) 30vw, 92vw', '50% 55%'), 'Boat rentals', 'Plan time on the water with the resort’s boats, from a small boat for six to a big boat for twenty-five.', 'activities.html#boats', 'See the boats')}
{card(pic('sunong-bato-b', 'Sunong Bato, a stacked rock formation rising from clear turquoise water', '(min-width: 900px) 30vw, 92vw', '50% 50%'), 'Island hopping', 'Visit Palad Sandbar, Sunong Bato, Ungab Rock Formation, the Century Cliff Tree and more around Maniwaya.', 'activities.html#island-hopping', 'Island-hopping stops')}
        </div>
      </div>
    </section>

    <section class="section" aria-labelledby="dining-title">
      <div class="wrap">
        <div class="feature feature--flip">
          <figure class="feature__media" data-reveal>{pic('skylight', 'Skylight Dining: rows of tables and chairs beneath a glass-roofed pavilion, framed by coconut palms', '(min-width: 900px) 56vw, 92vw', '45% 55%')}</figure>
          <div class="feature__text" data-reveal>
            <p class="eyebrow">Dining</p>
            <h2 class="h-section" id="dining-title">Gather around the island table</h2>
            <p>Make shared meals part of your stay, with meal packages, boodle fight dining setups, and bonfire menu packages. Explore the resort's dining spaces and ask the team about arrangements for your visit.</p>
            <ul class="inline-list"><li>Skylight Dining</li><li>Easter Sunday Café</li><li>Meal packages</li><li>Boodle fight</li><li>Bonfire menus</li></ul>
            <a class="btn btn--teal" href="dining.html">Explore dining</a>
          </div>
        </div>
      </div>
    </section>

    <section class="section section--sandbg" aria-labelledby="events-title">
      <div class="wrap">
        <div class="events">
          <figure class="events__main" data-reveal>{pic('genesis-hall', 'The Genesis Events Place set for a reception, white fabric draped from the ceiling over long dining tables', '(min-width: 900px) 50vw, 92vw', '50% 50%')}</figure>
          <div class="events__text" data-reveal>
            <p class="eyebrow">Gatherings &amp; Events</p>
            <h2 class="h-section" id="events-title">Bring everyone together on Maniwaya</h2>
            <p>Explore the resort's events venue and picture your next gathering at Islas Moriones. Share your plans with the team to discuss the space and arrangements for your group.</p>
            <a class="btn btn--teal" href="groups.html">Explore the venue</a>
          </div>
          <figure class="events__side" data-reveal>{pic('genesis-lawn', 'Cocktail tables dressed in white on the lawn in front of The Genesis', '(min-width: 900px) 24vw, 46vw', '50% 75%')}</figure>
          <figure class="events__side" data-reveal>{pic('genesis-tables', 'Round tables with gold chairs and flowers inside The Genesis', '(min-width: 900px) 24vw, 46vw', '50% 60%')}</figure>
        </div>
      </div>
    </section>

    <section class="section section--tight" aria-labelledby="strip-title">
      <div class="wrap">
        <header class="section-head section-head--split">
          <h2 class="h-section" id="strip-title">Picture your time here</h2>
          <div>
            <p>Explore more of the rooms, dining spaces, activities, and island setting.</p>
            <a class="text-link" href="gallery.html">View the full gallery <span aria-hidden="true">→</span></a>
          </div>
        </header>
      </div>
      <div class="slider slider--plain" data-slider aria-roledescription="carousel" aria-label="Photo gallery preview">
        <ul class="slider__track" data-slider-track tabindex="0">
STRIPITEMS
        </ul>
        <button class="slider__arrow slider__arrow--prev" type="button" data-slider-prev aria-label="Previous photo"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 5l-7 7 7 7"/></svg></button>
        <button class="slider__arrow slider__arrow--next" type="button" data-slider-next aria-label="Next photo"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 5l7 7-7 7"/></svg></button>
      </div>
    </section>

    <section class="section section--linen" aria-labelledby="journey-title">
      <div class="wrap">
        <div class="feature">
          <figure class="feature__media feature__media--wide" data-reveal>{pic('boat-omon', 'The resort’s big outrigger boat Omon Express in shallow water off Maniwaya', '(min-width: 900px) 56vw, 92vw', '50% 55%')}</figure>
          <div class="feature__text" data-reveal>
            <h2 class="h-section" id="journey-title">Your journey to Maniwaya</h2>
            <p>Find Islas Moriones on Maniwaya Island in Santa Cruz, Marinduque. Speak with the resort about your route and arrival arrangements before you travel.</p>
            <a class="btn btn--line" href="getting-here.html">Plan your journey</a>
          </div>
        </div>
      </div>
    </section>

{closing('Make time for an island stay', 'Explore availability through our booking page, or message the resort for help with accommodations, dining, activities, and group plans.')}'''

STRIP = [
    ('poolsuite-bed', 'The Pool Suite Room', 'A queen bed and seating area in the Pool Suite Room'),
    ('skylight-2', 'Skylight Dining', 'Tables beneath the glass roof of Skylight Dining'),
    ('tower-blue', 'The beach', 'The lifeguard tower on the white-sand beach under a clear sky'),
    ('kubo-living', 'The Luxury Kubo', 'The Luxury Kubo lounge with a white sofa and glass doors'),
    ('genesis-setup', 'The Genesis Events Place', 'Dining tables set beneath draped fabric in The Genesis'),
    ('kayak-clear-2', 'Crystal-clear kayak', 'A crystal-clear kayak on calm water off Maniwaya'),
    ('room-suiteloft', 'Suite Loft Room', 'A loft room with a staircase above the bed'),
    ('ungab-arch', 'Ungab Rock Formation (island hopping)', 'A natural rock arch above a quiet cove at Ungab Rock Formation'),
    ('lobby-lounge', 'The lobby lounge', 'The lobby lounge with leaf-pattern wall and dark sofas'),
    ('bikes-crop', 'Mountain bikes on Maniwaya', 'Two mountain bikes on the rocky shore of Maniwaya'),
]
items = []
for i, (jid, cap, alt) in enumerate(STRIP, 1):
    items.append(f'          <li class="slide-item" aria-roledescription="slide" aria-label="{cap}"><figure class="tile"><div class="tile__media"><button class="slide-open" type="button" data-lightbox="strip" data-start="s{i}" aria-label="Open photo: {cap}">{pic(jid, alt, "(min-width: 600px) 420px, 76vw")}</button></div></figure></li>')
home = home.replace('STRIPITEMS', '\n'.join(items))
strip_set = lb_set('strip', [(j, c, a) for j, c, a in STRIP]).replace('<li data-full', '<li data-id="sX" data-full')
n = 0
def _num(m):
    global n; n += 1; return f'data-id="s{n}"'
strip_set = re.sub(r'data-id="sX"', _num, strip_set)

page('index.html', 'index.html', 'Islas Moriones Beach Resort | Maniwaya Island, Marinduque',
     'Islas Moriones Beach Resort on Maniwaya Island, Marinduque: rooms and tent stays, a pool by the beach, island experiences, dining and an events venue. Check availability or message the resort.',
     home, sets=strip_set,
     preload='\n  <link rel="preload" as="image" href="assets/video/islas-moriones-hero-poster.jpg" fetchpriority="high">')

# =====================================================================================  STAY
ps_set = lb_set('poolsuite', [
    ('poolsuite-room', 'Pool Suite Room', 'Queen bed, sofa and kitchen in the Pool Suite Room'),
    ('poolsuite-bed', 'Pool Suite Room, bedroom', 'The queen bed and bench in the Pool Suite Room'),
    ('poolsuite-bar', 'Pool Suite Room, breakfast bar', 'A timber breakfast bar with stools and a kitchen'),
    ('poolsuite-pantry', 'Pool Suite Room, kitchen', 'Open shelves, kettle and refrigerator in the kitchen'),
    ('poolsuite-loft', 'Pool Suite Room, view from the loft', 'Looking down from the loft over the kitchen'),
    ('poolsuite-family', 'Pool Suite Room, beds upstairs', 'Double beds on the upper level of the Pool Suite'),
    ('poolsuite-bath', 'Pool Suite Room, bathroom', 'A bathroom with a glass shower and stone basin'),
])
kubo_set = lb_set('kubo', [
    ('kubo-exterior', 'The Luxury Kubo', 'The thatched Luxury Kubo and its veranda'),
    ('kubo-living', 'Luxury Kubo, lounge', 'A white sofa beside glass doors'),
    ('kubo-bedroom', 'Luxury Kubo, bedroom', 'A queen bed under window blinds'),
    ('kubo-loftbeds', 'Luxury Kubo, loft beds', 'Four single beds in the timber loft'),
    ('kubo-bath', 'Luxury Kubo, bathroom', 'A glass shower and toilet'),
])
def gallery_btn(setname, count):
    return f'<button class="btn btn--line btn--sm" type="button" data-lightbox="{setname}">View {count} photos</button>'

ROOMS = [
    ('Single Standard Room', pic('room-single', 'Single Standard Room: a single bed beside a teal accent wall', '(min-width: 900px) 30vw, (min-width: 600px) 46vw, 92vw', '40% 55%'), ['1–2 guests', '10 sqm', 'Ground floor, main building'], 'One single bed'),
    ('Double Standard Room', old('room-double-standard', 'Double Standard Room: a timber-framed bed with white pillows', '(min-width: 900px) 30vw, (min-width: 600px) 46vw, 92vw', '60% 55%'), ['2 guests', '15 sqm', 'Ground floor, main building'], None),
    ('Deluxe Room', pic('room-deluxe', 'Deluxe Room: a queen bed against a red feature wall, with sheer curtains to the balcony', '(min-width: 900px) 30vw, (min-width: 600px) 46vw, 92vw', '50% 60%'), ['2–3 guests', '30 sqm', 'Second floor, balcony, sea view'], 'One queen bed and one pull-out single bed'),
    ('Superior Room', pic('room-superior', 'Superior Room: two beds against a yellow feature wall', '(min-width: 900px) 30vw, (min-width: 600px) 46vw, 92vw', '50% 60%'), ['4 guests', '25 sqm', 'Ground floor, main building'], 'Two twin beds'),
    ('Suite Room', old('room-suite', 'Suite Room: two twin beds and a single bed under bright windows', '(min-width: 900px) 30vw, (min-width: 600px) 46vw, 92vw', '50% 60%'), ['5–6 guests', '36 sqm', 'Ground floor, main building'], 'Two twin beds plus one single, or plus two pull-out singles, depending on the room'),
    ('Suite Loft Room', pic('room-suiteloft', 'Suite Loft Room: a bed beneath a timber staircase to the loft, teal accent wall', '(min-width: 900px) 30vw, (min-width: 600px) 46vw, 92vw', '50% 60%'), ['5–6 guests', '50 sqm', 'Second floor, balcony, sea view'], 'One king bed and three single loft beds'),
    ('Executive Loft Room', pic('room-execloft', 'Executive Loft Room: two beds below a staircase to the loft, teal accent wall', '(min-width: 900px) 30vw, (min-width: 600px) 46vw, 92vw', '50% 60%'), ['5–7 guests', '50 sqm', 'Second floor, balcony, sea view'], 'Two twin beds and three single loft beds'),
]
room_cards = []
for name, img, facts, beds in ROOMS:
    f = ''.join(f'<li>{x}</li>' for x in facts)
    b = f'\n          <p>{beds}</p>' if beds else ''
    room_cards.append(f'''        <article class="card card--room" data-reveal>
          <figure class="card__media">{img}</figure>
          <h3 class="h-card">{name}</h3>
          <ul class="facts">{f}</ul>{b}
        </article>''')

stay = intro('Stay', 'Your stay on Maniwaya', 'Explore the accommodations at Islas Moriones, from rooms for your island escape to tent stays. Browse the photographs and find the setting that suits your visit.') + f'''
    <section class="section section--sandbg2" id="pool-suite" aria-labelledby="ps-title">
      <div class="wrap">
        <div class="suite">
          <figure class="suite__main" data-reveal>{pic('poolsuite-room', 'Inside the Pool Suite Room: queen bed, sofa and a kitchen with a brick breakfast bar', '(min-width: 900px) 48vw, 92vw', '55% 70%', eager=True)}</figure>
          <figure class="suite__a" data-reveal>{pic('poolsuite-loft', 'Looking down from the Pool Suite loft over the kitchen and dining counter', '(min-width: 900px) 24vw, 46vw', '50% 60%')}</figure>
          <figure class="suite__b" data-reveal>{pic('poolsuite-family', 'Double beds on the upper level of the Pool Suite Room', '(min-width: 900px) 24vw, 46vw', '50% 60%')}</figure>
          <div class="suite__text" data-reveal>
            <p class="eyebrow">Featured stay</p>
            <h2 class="h-section" id="ps-title">Pool Suite Room</h2>
            <p>A standalone setting with a balcony and views towards the beach and sea, with a kitchen, a breakfast bar and space to spread out. Choose the Couple Suite or the Family Suite for your visit.</p>
            <dl class="spec">
              <div><dt>Couple Suite</dt><dd>Ideal for 2–3 guests · one queen bed and two sofa beds</dd></div>
              <div><dt>Family Suite</dt><dd>Ideal for 8–10 guests · three double beds</dd></div>
              <div><dt>Comfort</dt><dd>Air-conditioned · private toilet and bath with hot shower</dd></div>
              <div><dt>Included</dt><dd>Breakfast for two guests and use of the included amenities</dd></div>
            </dl>
            <div class="actions">
              <a class="btn btn--teal" href="{BOOK}" target="_blank" rel="noopener">Check Availability{BOOKTAB}</a>
              {gallery_btn('poolsuite', 7)}
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="section" id="luxury-kubo" aria-labelledby="kubo-title">
      <div class="wrap">
        <div class="feature feature--flip">
          <figure class="feature__media feature__media--tall" data-reveal>{pic('kubo-exterior', 'The thatched Luxury Kubo with a white-railed veranda, a bamboo cart on the lawn in front', '(min-width: 900px) 44vw, 92vw', '50% 40%')}</figure>
          <div class="feature__text" data-reveal>
            <p class="eyebrow">Campsite area</p>
            <h2 class="h-section" id="kubo-title">Luxury Kubo</h2>
            <p>A thatched-roof stay with loft sleeping spaces, a private kitchen, and a dining area for shared meals.</p>
            <dl class="spec">
              <div><dt>Guests</dt><dd>Ideal for 6–8</dd></div>
              <div><dt>Beds</dt><dd>One queen bed and four single loft beds, plus a couch</dd></div>
              <div><dt>Space</dt><dd>70 sqm · two air-conditioning units · private toilet and bath with hot shower</dd></div>
              <div><dt>Kitchen</dt><dd>Private kitchen, dining area and a small refrigerator</dd></div>
            </dl>
            <div class="mini-row">
              <figure>{pic('kubo-living', 'The Kubo lounge with a white sofa and glass doors', '(min-width: 900px) 14vw, 30vw', '50% 60%')}</figure>
              <figure>{pic('kubo-loftbeds', 'Four single beds in the Kubo’s timber loft', '(min-width: 900px) 14vw, 30vw', '50% 55%')}</figure>
              <figure>{pic('kubo-bedroom', 'A queen bed in the Kubo', '(min-width: 900px) 14vw, 30vw', '50% 55%')}</figure>
            </div>
            <div class="actions">
              <a class="btn btn--teal" href="{BOOK}" target="_blank" rel="noopener">Check Availability{BOOKTAB}</a>
              {gallery_btn('kubo', 5)}
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="section section--linen" aria-labelledby="rooms-title">
      <div class="wrap">
        <header class="section-head section-head--split">
          <div>
            <p class="eyebrow">Main building</p>
            <h2 class="h-section" id="rooms-title">Rooms for every kind of visit</h2>
          </div>
          <p>The resort has 16 air-conditioned rooms. Every room has a private toilet and bath with a hot shower, and includes breakfast for two guests. Children aged 7 and below stay free.</p>
        </header>
        <div class="cards cards--3">
{chr(10).join(room_cards)}
        </div>
        <div class="rates-note" data-reveal>
          <p>For current rates and availability, check the booking page or message the resort on <a href="{FB}" target="_blank" rel="noopener">Facebook{NEWTAB}</a>.</p>
          <a class="btn btn--teal" href="{BOOK}" target="_blank" rel="noopener">Check Availability{BOOKTAB}</a>
        </div>
      </div>
    </section>

    <section class="section" id="tents" aria-labelledby="tents-title">
      <div class="wrap">
        <div class="feature">
          <div class="feature__stack" data-reveal><figure class="feature__media">{pic('tents-campsite', 'Tents pitched on the resort lawn under tall coconut palms, beside a thatched cottage', '(min-width: 900px) 52vw, 92vw', '32% 96%')}</figure><figure class="feature__media">{pic('tent', 'A dome tent beneath tall coconut palms', '(min-width: 900px) 52vw, 92vw', '50% 78%')}</figure></div>
          <div class="feature__text" data-reveal>
            <p class="eyebrow">Tent stays</p>
            <h2 class="h-section" id="tents-title">A different way to stay</h2>
            <p>Prefer a tent stay? Explore the resort's tent accommodations and contact the team for the available setups and arrangements.</p>
            <dl class="spec">
              <div><dt>Tent accommodation</dt><dd>A waterproof big tent with mattress, pillows and linens</dd></div>
              <div><dt>Tent pitching</dt><dd>Bring your own tent and set up on the camping grounds</dd></div>
              <div><dt>Facilities</dt><dd>Communal toilets and showers, and a charging station</dd></div>
              <div><dt>Included</dt><dd>Use of the pool, bonfire, volleyball, bamboo raft and badminton</dd></div>
            </dl>
            <a class="btn btn--line" href="contact.html">Ask about tent stays</a>
          </div>
        </div>
      </div>
    </section>

{closing('Ready to choose your room?', 'See current rates and availability on the booking page, or message the resort about tent stays and group arrangements.')}'''
page('rooms.html', 'rooms.html', 'Stay | Islas Moriones Beach Resort',
     'Accommodations at Islas Moriones on Maniwaya Island: the Pool Suite Room, the Luxury Kubo, rooms in the main building and tent stays.',
     stay, sets=ps_set + kubo_set)

# =====================================================================================  EXPERIENCES
def stop(img, name, where, text):
    return f'''          <article class="stop" data-reveal>
            <figure class="card__media">{img}</figure>
            <p class="eyebrow eyebrow--sm">{where}</p>
            <h3 class="h-card">{name}</h3>
            <p>{text}</p>
          </article>'''
exp = intro('Experiences', 'Make the most of island days', 'Spend time enjoying the resort, head onto the water, or ask about experiences further afield. Explore what is included with your stay and what can be arranged separately.') + f'''
    <section class="section section--sandbg3" aria-labelledby="inc-title">
      <div class="wrap">
        <header class="section-head center">
          <p class="eyebrow">1 · Included with your stay</p>
          <h2 class="h-section" id="inc-title">Time to enjoy, already part of your stay</h2>
          <p>Free for staying guests, from the resort’s own amenities list.</p>
        </header>
        <div class="slider" data-slider aria-roledescription="carousel" aria-label="Included amenities">
          <ul class="slider__track" data-slider-track tabindex="0">
{included_grid()}
          </ul>
          <button class="slider__arrow slider__arrow--prev" type="button" data-slider-prev aria-label="Previous amenities"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 5l-7 7 7 7"/></svg></button>
          <button class="slider__arrow slider__arrow--next" type="button" data-slider-next aria-label="Next amenities"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 5l7 7-7 7"/></svg></button>
        </div>
        <p class="soon center"><span>Coming soon</span> A pickleball court is being built at the resort. Ask the team for updates.</p>
      </div>
    </section>

    <section class="section" aria-labelledby="more-title">
      <div class="wrap">
        <header class="section-head section-head--split">
          <div>
            <p class="eyebrow">2 · Arranged with the resort</p>
            <h2 class="h-section" id="more-title">More ways to enjoy the island</h2>
          </div>
          <p>Head onto the water or explore Maniwaya with the resort’s rentals. Additional charges apply; ask the team about availability and arrangements for your dates.</p>
        </header>

        <div class="feature" id="kayaks">
          <figure class="feature__media feature__media--square" data-reveal>{pic('kayak-float', 'Seen from above, a swimmer floats beside a transparent kayak on bright turquoise water', '(min-width: 900px) 46vw, 92vw', '50% 50%')}</figure>
          <div class="feature__text" data-reveal>
            <h3 class="h-section h-section--sm">Crystal-clear kayaks</h3>
            <p>See the water from a different perspective in a crystal-clear kayak. Ask the resort about availability and rental arrangements. A rowing guide can be arranged.</p>
            <div class="inset-row">
              <figure class="inset">{pic('kayak-pov', 'Inside a crystal-clear kayak on calm water off Maniwaya, paddle and life vest in view', '(min-width: 900px) 16vw, 44vw')}</figure>
              <figure class="inset">{pic('kayak-pov-2', 'Looking through the transparent hull of a clear kayak to the green water below', '(min-width: 900px) 16vw, 44vw')}</figure>
            </div>
          </div>
        </div>

        <div class="boats" id="boats">
          <header class="section-head section-head--split">
            <h3 class="h-section h-section--sm">Boat rentals</h3>
            <p>Plan time on the water with the resort's boat rental options. Contact the team to discuss the available boats and arrangements for your visit.</p>
          </header>
          <div class="cards cards--3">
{card(pic('boat-rogelius', 'M/V Rogelius, a white outrigger boat with a canopy, in clear water', '(min-width: 900px) 30vw, 92vw', '50% 55%'), 'M/V Rogelius', 'Small boat for up to 6 people.')}
{card(pic('boat-longinus', 'M/V St. Longinus, a green and white outrigger boat with a Philippine flag', '(min-width: 900px) 30vw, 92vw', '50% 55%'), 'M/V St. Longinus', 'Medium boat for up to 16 people.')}
{card(pic('boat-omon', 'M/V Omon Express, a large outrigger boat with a covered deck', '(min-width: 900px) 30vw, 92vw', '50% 55%'), 'M/V Omon Express', 'Big boat for up to 25 people.')}
          </div>
          <p class="note">Boat trips depend on the weather and sea conditions. Boat rental is arranged separately from island-hopping packages and arrival transfers.</p>
        </div>

        <div class="cards cards--3 cards--spaced">
{card(pic('bikes-crop', 'Two mountain bikes resting on the rocky shoreline of Maniwaya, waves behind', '(min-width: 900px) 30vw, 92vw'), 'Mountain bikes', 'Ride Maniwaya at your own pace. A tour guide can be arranged.')}
{card(pic('ecart', 'An open-sided white electric cart parked on a seawall', '(min-width: 900px) 30vw, 92vw', '50% 100%'), 'Land tour by e-cart', 'See more of Maniwaya on a land tour by electric cart.')}
{card(old('exp-snorkel', 'A snorkeller swimming through clear blue water', '(min-width: 900px) 30vw, 92vw', '50% 35%'), 'Snorkelling gear', 'Masks, snorkels and fins are available. Photo for illustration.')}
{card(old('exp-massage', 'Hands giving a relaxing back massage to a guest lying under a white towel', '(min-width: 900px) 30vw, 92vw', '60% 50%'), 'In-room massage', 'Unwind after a day outdoors with a massage in your room. Photo for illustration.')}
{card(old('exp-karaoke', 'A microphone lit in purple stage light', '(min-width: 900px) 30vw, 92vw', '35% 50%'), 'Karaoke', 'A night in with your group and a few favourite songs. Photo for illustration.')}
{card(old('exp-laundry', 'Clothes being loaded into a front-loading washing machine', '(min-width: 900px) 30vw, 92vw', '45% 50%'), 'Laundry service', 'For longer stays, so you can pack light. Photo for illustration.')}
        </div>
      </div>
    </section>

    <section class="section section--linen" id="island-hopping" aria-labelledby="hop-title">
      <div class="wrap">
        <header class="section-head section-head--split">
          <div>
            <p class="eyebrow">Island hopping</p>
            <h2 class="h-section" id="hop-title">See what lies beyond the shore</h2>
          </div>
          <div>
            <p>Choose three destinations from the resort’s island-hopping options. A minimum of six guests applies, and separate ecological and barangay fees may apply. Routes and stops depend on tides, weather, and sea conditions.</p>
            <button class="text-link" type="button" data-lightbox="island" data-start="maniwaya-map">View the island map <span aria-hidden="true">→</span></button>
          </div>
        </header>
        <div class="cards cards--3">
{stop(pic('sandbar-aerial', 'Aerial view of a white sandbar in turquoise water with outrigger boats', '(min-width: 900px) 30vw, 46vw', '50% 50%'), 'Palad Sandbar', 'Offshore', 'A natural sandbar that fully appears at low tide.')}
{stop(pic('sunong-bato-b', 'Sunong Bato, a stacked rock formation in clear turquoise water', '(min-width: 900px) 30vw, 46vw', '50% 50%'), 'Sunong Bato', 'South-east Maniwaya', 'A stacked-rock formation above clear water.')}
{stop(pic('ungab-arch', 'A natural rock arch above a quiet cove', '(min-width: 900px) 30vw, 46vw', '50% 50%'), 'Ungab Rock Formation', 'Mompong Island', 'Limestone arches around a sheltered cove.')}
{stop(pic('reef-raft', 'A floating bamboo raft with a canopy and resort flags', '(min-width: 900px) 30vw, 46vw', '50% 55%'), 'Morion Reef Raft', 'Off the west coast', 'A floating raft above the Morion Reef snorkelling area.')}
{stop(pic('century-tree-b', 'A lone tree on a grassy clifftop above bright blue sea', '(min-width: 900px) 30vw, 46vw', '50% 55%'), 'Century Cliff Tree', 'South-east Maniwaya', 'A lone tree on a clifftop above the sea.')}
{stop(pic('morion-statues', 'Statues of Morion warriors beside white columns under a blue sky', '(min-width: 900px) 30vw, 46vw', '50% 50%'), 'Morion Statues', 'Island-hopping stop', 'Statues of Marinduque’s Morion warriors.')}
        </div>
      </div>
    </section>

    <section class="section" aria-labelledby="extras-title">
      <div class="wrap">
        <div class="extras-band" data-reveal>
          <div>
            <p class="eyebrow">3 · Useful extras</p>
            <h2 class="h-section h-section--sm" id="extras-title">Little things that help</h2>
          </div>
          <ul class="inline-list inline-list--wide"><li>Tour guide</li><li>Kitchen and griller use</li></ul>
          <p class="note">Additional charges apply. Ask the resort for current rates.</p>
        </div>
      </div>
    </section>

{closing('Plan your days on the water', 'Kayaks, boats and island hopping are arranged with the resort. Check availability for your stay, then message the team.')}'''
island_set = '''    <ul data-set="island">
      <li data-id="maniwaya-map" data-full="assets/img/maniwaya-map-1528.jpg" data-w="1528" data-h="1281" data-caption="Maniwaya Island map shared by the resort (not to scale)" data-alt="Annotated map of Maniwaya Island with Islas Moriones on the west coast, Palad Sandbar, Morion Reef, Sunong Bato and the Cliff Century Tree"></li>
    </ul>
'''
page('activities.html', 'activities.html', 'Experiences | Islas Moriones Beach Resort',
     'Experiences at Islas Moriones on Maniwaya Island: included amenities, crystal-clear kayaks, boat rentals, island hopping, bikes and e-cart land tours.',
     exp, sets=island_set)

# =====================================================================================  DINING
dining = intro('Dining', 'A table for your island stay', 'From everyday meals to dining together as a group, explore the food experiences available at Islas Moriones.') + f'''
    <section class="section section--sandbg2" aria-labelledby="sky-title">
      <div class="wrap">
        <div class="feature">
          <figure class="feature__media feature__media--wide" data-reveal>{pic('skylight', 'Skylight Dining: tables and chairs beneath a glass-roofed pavilion beside the main building, framed by coconut palms', '(min-width: 900px) 56vw, 92vw', '45% 55%', eager=True)}</figure>
          <div class="feature__text" data-reveal>
            <p class="eyebrow">New</p>
            <h2 class="h-section" id="sky-title">Skylight Dining</h2>
            <p>The resort’s newest dining space: a pavilion with a glass roof beside the main building, with long tables under the palms. Explore it during your stay.</p>
            <a class="btn btn--line" href="contact.html">Ask about dining</a>
          </div>
        </div>
      </div>
    </section>

    <section class="section" aria-labelledby="cafe-title">
      <div class="wrap">
        <header class="section-head section-head--split">
          <div>
            <p class="eyebrow">Easter Sunday Café</p>
            <h2 class="h-section" id="cafe-title">Find your favourites</h2>
          </div>
          <div>
            <p>Filipino, American and continental breakfasts in the morning, then soups, grilled dishes, seafood and pasta through the afternoon and evening.</p>
            <dl class="hours"><div><dt>Breakfast</dt><dd>7:00 – 9:00 AM</dd></div><div><dt>Lunch &amp; dinner</dt><dd>11:00 AM – 8:00 PM</dd></div></dl>
          </div>
        </header>
        {MENU}
      </div>
    </section>

    <section class="section section--linen" aria-labelledby="pk-title">
      <div class="wrap">
        <header class="section-head center">
          <p class="eyebrow">Dining packages</p>
          <h2 class="h-section" id="pk-title">Make a meal part of the occasion</h2>
        </header>
        <div class="cards cards--3">
{card(old('dining-veranda-night', 'Timber dining tables along tall glass doors on the café veranda in the evening', '(min-width: 900px) 30vw, 92vw', '40% 50%'), 'Meal packages', 'Ask about meal packages for your stay and the arrangements available for your group.')}
{card(old('bamboo-raft', 'The covered bamboo raft with a long bamboo table on turquoise water', '(min-width: 900px) 30vw, 92vw', '50% 45%'), 'Boodle fight dining', 'Gather around a shared boodle fight setup and make a meal part of the occasion. It can also be set up on the bamboo raft.')}
{card(pic('bonfire-smores', 'Marshmallows toasting on skewers over a campfire at night', '(min-width: 900px) 30vw, 92vw', '55% 50%'), 'Bonfire menu packages', 'Explore the resort’s bonfire menu packages for another way to spend an evening together. Photo for illustration.')}
        </div>
        <div class="actions actions--center">
          <a class="btn btn--teal" href="contact.html">Ask about dining packages</a>
        </div>
        <p class="note center">Prefer to cook? Kitchen use, griller use and paluto can be arranged. Corkage applies to outside food and drinks.</p>
      </div>
    </section>

{closing('Hungry for an island stay?', 'Check availability for your dates, then message the resort about meals, boodle fights and bonfire menus.')}'''
page('dining.html', 'dining.html', 'Dining | Islas Moriones Beach Resort',
     'Dining at Islas Moriones on Maniwaya Island: Skylight Dining, the Easter Sunday Café menu, meal packages, boodle fights and bonfire menu packages.',
     dining)

# =====================================================================================  GATHERINGS
gen_set = lb_set('genesis', [
    ('genesis-hall', 'The Genesis Events Place set for a reception', 'Long tables beneath draped white fabric'),
    ('genesis-tables', 'Round tables inside The Genesis', 'Round tables with gold chairs and flowers'),
    ('genesis-setup', 'The Genesis, banquet setup', 'Dining tables set for an event'),
    ('genesis-dinner', 'The Genesis, evening setup', 'Tables set with linen and flowers'),
    ('genesis-front', 'The Genesis from the lawn', 'The venue entrance with cocktail tables on the lawn'),
    ('genesis-lawn', 'Cocktail tables on the lawn', 'White-dressed cocktail tables on the lawn'),
])
WA_EVT = WA + '?text=' + 'Hi%20Islas%20Moriones!%20We%27re%20planning%20a%20gathering.%20Preferred%20date%3A%20%20%7C%20Number%20of%20guests%3A%20%20%7C%20Occasion%3A%20'
groups = intro('Gatherings &amp; Events', 'An island setting for getting together', 'Explore the events venue at Islas Moriones and speak with the team about bringing your group to Maniwaya.') + f'''
    <section class="section section--dune" aria-labelledby="gen-title">
      <div class="wrap">
        <div class="venue">
          <figure class="venue__a" data-reveal>{pic('genesis-hall', 'The Genesis Events Place: white fabric draped from a high ceiling over long dining tables, with glass walls to the garden', '(min-width: 900px) 46vw, 92vw', '50% 50%', eager=True)}</figure>
          <figure class="venue__b" data-reveal>{pic('genesis-front', 'The Genesis from the lawn, with white-dressed cocktail tables', '(min-width: 900px) 24vw, 46vw', '50% 65%')}</figure>
          <figure class="venue__c" data-reveal>{pic('genesis-tables', 'Round tables with gold chairs and flower arrangements inside The Genesis', '(min-width: 900px) 24vw, 46vw', '50% 60%')}</figure>
          <div class="venue__text" data-reveal>
            <p class="eyebrow">The Genesis Events Place</p>
            <h2 class="h-section" id="gen-title">A versatile space for your group</h2>
            <p>Ideal for company programs, team-building activities, workshops, celebrations, meetings and group gatherings, from a corporate presentation to an evening program.</p>
            <dl class="spec">
              <div><dt>Guests</dt><dd>For 100 to 120 guests</dd></div>
              <div><dt>Options</dt><dd>Air-conditioned or non-air-conditioned use</dd></div>
              <div><dt>Hire</dt><dd>Up to 5 hours, with exclusive use of the events area during the rental. Extra hours and setup time by arrangement</dd></div>
            </dl>
            <div class="actions">
              <a class="btn btn--teal" href="{WA_EVT}" target="_blank" rel="noopener">Tell us about your gathering<span class="visually-hidden"> (opens WhatsApp in a new tab)</span></a>
              {gallery_btn('genesis', 6)}
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="section section--linen" aria-labelledby="team-title">
      <div class="wrap">
        <div class="feature feature--flip">
          <figure class="feature__media feature__media--wide" data-reveal>{pic('main-palms', 'The resort’s main building framed by coconut palms, with the pool at its edge', '(min-width: 900px) 56vw, 92vw', '50% 55%')}</figure>
          <div class="feature__text" data-reveal>
            <p class="eyebrow">Teams &amp; companies</p>
            <h2 class="h-section" id="team-title">Where teams grow beyond the workplace</h2>
            <p>Bring your team together for team-building activities, leadership seminars, company outings and corporate retreats in a beachfront setting, with conference facilities, event spaces, island dining and island hopping all in one place.</p>
            <p>Packages can be customised around your group size, preferred activities, accommodation, meals, length of stay and budget.</p>
            <a class="btn btn--teal" href="{WA_EVT}" target="_blank" rel="noopener">Plan a team visit<span class="visually-hidden"> (opens WhatsApp in a new tab)</span></a>
          </div>
        </div>
      </div>
    </section>

    <section class="section" aria-label="Group options">
      <div class="wrap">
        <div class="cards cards--3">
{card(old('pool-grounds-day', 'The pool in daylight with the palm-shaded lawn beyond', '(min-width: 900px) 30vw, 92vw', '50% 82%'), 'Day visits', 'Spend the day enjoying the beach, pool, and selected resort amenities, 8 AM to 5 PM. Day tours are subject to availability.')}
{card(pic('lobby-lounge', 'The lobby lounge with a leaf-pattern mural and dark sofas', '(min-width: 900px) 30vw, 92vw', '50% 55%'), 'Group packages', 'Ask the team about packages for reunions, celebrations and other group stays.')}
{card(pic('beach-palms', 'Palms shading the sand in front of the resort buildings', '(min-width: 900px) 30vw, 92vw', '50% 55%'), 'Exclusive stays', 'Planning something for your whole group? Ask about exclusive-stay arrangements, which are separate from venue hire.')}
        </div>
        <p class="note center">Group stays pair well with <a href="rooms.html">the rooms</a>, <a href="dining.html">dining packages</a> and the resort’s <a href="getting-here.html#van">van</a> and <a href="activities.html#boats">boats</a>.</p>
      </div>
    </section>

{closing('Bring your group to Maniwaya', 'Share your date, guest count and occasion with the team, and check room availability for overnight stays.')}'''
page('groups.html', 'groups.html', 'Gatherings & Events | Islas Moriones Beach Resort',
     'The Genesis Events Place at Islas Moriones on Maniwaya Island, for 100 to 120 guests, plus day visits, group packages and exclusive stays.',
     groups, sets=gen_set)

# =====================================================================================  GALLERY
G = [  # (category, id, caption, alt, wide?)
    ('resort', 'tower-wide', 'The beachfront', 'The lifeguard tower and resort flags on the beach', 0),
    ('stays', 'poolsuite-room', 'Pool Suite Room', 'Queen bed, sofa and kitchen in the Pool Suite Room', 0),
    ('dining', 'skylight', 'Skylight Dining', 'Tables beneath the glass-roofed Skylight Dining pavilion', 0),
    ('gatherings', 'genesis-hall', 'The Genesis Events Place', 'Long tables beneath draped fabric inside The Genesis', 0),
    ('experiences', 'kayak-clear', 'Crystal-clear kayak', 'A crystal-clear kayak on calm water', 0),
    ('resort', 'dusk-pool', 'The pool at dusk', 'The pool beside the main building at dusk', 0),
    ('stays', 'kubo-exterior-old', 'The Luxury Kubo', 'The thatched Luxury Kubo and veranda', 0),
    ('experiences', 'boat-longinus', 'M/V St. Longinus', 'The resort’s boat St. Longinus in clear water', 1),
    ('stays', 'tents-campsite', 'Tent stays on the campsite', 'Tents on the lawn under coconut palms', 0),
    ('stays', 'tent', 'Tent stay', 'A tent on the lawn under coconut palms', 0),
    ('experiences', 'kayak-float', 'Crystal-clear kayak', 'A swimmer beside a transparent kayak, seen from above', 0),
    ('resort', 'main-building', 'The main building', 'The white main building with its gabled roof', 0),
    ('stays', 'room-deluxe', 'Deluxe Room', 'A queen bed against a red feature wall', 0),
    ('gatherings', 'genesis-front', 'The Genesis from the lawn', 'Cocktail tables on the lawn in front of The Genesis', 0),
    ('resort', 'beach-loungers', 'Sun loungers on the beach', 'Wicker loungers in the shade on the beach', 1),
    ('resort', 'beach-palms', 'Palms along the shore', 'Palms shading the sand in front of the resort', 1),
    ('stays', 'poolsuite-loft', 'Pool Suite Room, loft view', 'Looking down from the loft over the kitchen', 0),
    ('experiences', 'boat-omon', 'M/V Omon Express', 'The resort’s big outrigger boat in shallow water', 0),
    ('dining', 'skylight-2', 'Skylight Dining', 'The Skylight Dining pavilion beside the main building', 0),
    ('stays', 'room-suiteloft', 'Suite Loft Room', 'A bed beneath a staircase to the loft', 0),
    ('resort', 'tower-blue', 'The lifeguard tower', 'The white lifeguard tower against a deep blue sky', 0),
    ('gatherings', 'genesis-tables', 'Round-table setup', 'Round tables with gold chairs inside The Genesis', 0),
    ('stays', 'kubo-loftbeds', 'Luxury Kubo, loft beds', 'Four single beds in the timber loft', 0),
    ('experiences', 'pingpong-darts', 'Games room', 'A ping-pong table and dartboard', 0),
    ('resort', 'lobby-lounge', 'The lobby lounge', 'A lounge with a leaf-pattern mural', 1),
    ('stays', 'poolsuite-family', 'Pool Suite Room, upstairs', 'Double beds on the upper level', 0),
    ('experiences', 'ecart', 'E-cart land tour', 'An electric cart on the seawall', 0),
    ('stays', 'room-superior', 'Superior Room', 'Two beds against a yellow wall', 0),
    ('resort', 'reception', 'Reception', 'The reception desk below a double-height staircase', 0),
    ('gatherings', 'genesis-dinner', 'Evening setup', 'Tables set with linen and flowers', 0),
    ('stays', 'room-execloft', 'Executive Loft Room', 'Two beds below a staircase to the loft', 0),
    ('experiences', 'boat-rogelius', 'M/V Rogelius', 'A white outrigger boat with a canopy', 0),
    ('stays', 'kubo-living', 'Luxury Kubo lounge', 'A white sofa beside glass doors', 0),
    ('resort', 'tower-storm', 'Before the rain', 'The lifeguard tower under dark storm clouds', 0),
    ('stays', 'poolsuite-bath', 'Pool Suite bathroom', 'A bathroom with a glass shower', 0),
    ('experiences', 'bikes-crop', 'Mountain bikes', 'Two mountain bikes on the rocky shore', 0),
    ('stays', 'room-single', 'Single Standard Room', 'A single bed beside a teal wall', 0),
    ('experiences', 'ungab-arch', 'Ungab Rock Formation (island hopping, not resort grounds)', 'A rock arch above a cove', 0),
    ('experiences', 'sandbar-aerial', 'Palad Sandbar (island hopping, not resort grounds)', 'A white sandbar in turquoise water', 1),
    ('stays', 'room-loftsingles', 'Single loft beds', 'Three single beds on a loft level', 0),
    ('resort', 'palms-sky', 'Coconut palms', 'Coconut palms against a blue sky', 0),
    ('experiences', 'maniwaya-rocks', 'Maniwaya shoreline (not resort grounds)', 'Rocks and the Maniwaya sign above the shore', 0),
    ('stays', 'poolsuite-bar', 'Pool Suite breakfast bar', 'A timber breakfast bar with stools', 0),
]
FILTERS = [('all', 'All'), ('resort', 'The Resort'), ('stays', 'Stays'), ('dining', 'Dining'), ('experiences', 'Experiences'), ('gatherings', 'Gatherings')]
fbtn = '\n'.join(f'          <button type="button" class="chip{" is-active" if k == "all" else ""}" data-gallery-filter="{k}" aria-pressed="{"true" if k == "all" else "false"}">{t}</button>' for k, t in FILTERS)
gitems = []
for cat, jid, cap, alt, wide in G:
    gs = "(min-width: 900px) 24vw, (min-width: 600px) 32vw, 46vw"
    if jid.endswith('-old'):
        base = jid[:-4]; widths, w, h = OLD[base]; src = f'assets/img/{base}-{widths[-1]}.jpg'; img = old(base, alt, gs)
    else:
        src, w, h = full(jid); img = pic(jid, alt, gs)
    gitems.append(f'          <li data-cat="{cat}" class="g{" g--wide" if wide else ""}"><button type="button" data-full="{src}" data-w="{w}" data-h="{h}" data-caption="{html.escape(cap, quote=True)}" aria-label="Open photo: {html.escape(cap, quote=True)}">{img}</button></li>')
gallery = intro('Gallery', 'Explore Islas Moriones', 'A closer look at the places, spaces, and experiences that make up a stay on Maniwaya.') + f'''
    <section class="section section--tight" aria-label="Photo gallery">
      <div class="wrap">
        <div class="gallery-filter" role="group" aria-label="Filter photos">
{fbtn}
        </div>
        <ul class="gallery-grid" data-gallery-grid>
{chr(10).join(gitems)}
        </ul>
        <p class="note">Captions marked “not resort grounds” show nearby island-hopping destinations.</p>
      </div>
    </section>

{closing('Seen a place you like?', 'Check availability for your dates, or message the resort with any questions.')}'''
page('gallery.html', 'gallery.html', 'Gallery | Islas Moriones Beach Resort',
     'Photographs of Islas Moriones Beach Resort on Maniwaya Island: the resort, rooms and tent stays, dining, experiences and The Genesis Events Place.',
     gallery)

# =====================================================================================  GETTING HERE
here = intro('Getting Here', 'Your journey to Maniwaya', 'Islas Moriones Beach Resort is on Maniwaya Island, Santa Cruz, Marinduque. Plan your route and confirm arrival arrangements with the resort before setting out.') + f'''
    <section class="section section--dune" aria-labelledby="where-title">
      <div class="wrap">
        <div class="feature">
          <figure class="feature__media feature__media--wide" data-reveal>{pic('sunset-boat-beach', 'An outrigger boat pulled up on the beach beneath an orange sunset over the water', '(min-width: 900px) 56vw, 92vw', '20% 75%')}</figure>
          <div class="feature__text" data-reveal>
            <p class="eyebrow">Where to find us</p>
            <h2 class="h-section" id="where-title">On the west coast of Maniwaya</h2>
            <p>Maniwaya is an island off Santa Cruz, Marinduque, reached by boat. Most guests from Metro Manila travel to General Luna Port in Quezon, then cross to Maniwaya.</p>
            <button class="text-link" type="button" data-lightbox="island" data-start="maniwaya-map">View the island map <span aria-hidden="true">→</span></button>
          </div>
        </div>
      </div>
    </section>

    <section class="section" aria-labelledby="cross-title">
      <div class="wrap">
        <header class="section-head center">
          <p class="eyebrow">Planning your crossing</p>
          <h2 class="h-section" id="cross-title">Two ways to reach the port</h2>
          <p>From the resort’s own travel guides. Confirm current schedules and arrangements before travelling.</p>
        </header>
        <div class="routes">
          <article class="route" data-reveal>
            <h3 class="h-card">By public transport</h3>
            <ol class="steps">
              <li>Take a bus from the Superlines or Daet Express terminal in Cubao, Quezon City. The resort’s guide lists buses signed Aurora, Mulanay or Unisan.</li>
              <li>Get off at the General Luna crossing in Quezon and take a tricycle to General Luna Port.</li>
              <li>Cross to Maniwaya Port by public boat. Check the current departure time before you travel.</li>
              <li>Confirm with the resort how you will get from Maniwaya Port to Islas Moriones.</li>
            </ol>
          </article>
          <article class="route" data-reveal>
            <h3 class="h-card">By private vehicle</h3>
            <ol class="steps">
              <li>Drive from Metro Manila to General Luna Port, Quezon Province, via the Pan-Philippine Highway. The route passes the Bondoc Peninsula.</li>
              <li>Park at the port (a parking fee applies) and meet the resort’s port coordinator. Ask the resort for contact details before you set out.</li>
              <li>Cross by public boat or by one of the resort’s private boats. Life vests must be worn.</li>
            </ol>
          </article>
        </div>
        <button class="text-link" type="button" data-lightbox="guides">View the resort’s travel guides <span aria-hidden="true">→</span></button>
      </div>
    </section>

    <section class="section section--linen" aria-label="Boats and van">
      <div class="wrap">
        <div class="cards cards--2">
{card(pic('boat-longinus', 'The resort’s outrigger boat St. Longinus in clear shallow water', '(min-width: 900px) 46vw, 92vw', '50% 55%'), 'Private boat arrangements', 'The resort’s boats can make round trips from General Luna Port in Quezon or from Alobo/Buyabod Port on mainland Marinduque. Message the resort for availability.', 'activities.html#boats', 'See the boats')}
          <article class="card" id="van" data-reveal>
            <figure class="card__media">VANIMG</figure>
            <h3 class="h-card">Van arrangements for groups</h3>
            <p>Round trips from Manila to General Luna and back in Foton high-roof vans seating 12 to 14 passengers, with the driver, fuel, tolls and parking included.</p>
            <a class="text-link" href="contact.html">Ask about the van <span aria-hidden="true">→</span></a>
          </article>
        </div>
      </div>
    </section>

    <section class="section" aria-labelledby="before-title">
      <div class="wrap">
        <div class="extras-band" data-reveal>
          <div>
            <p class="eyebrow">Before you travel</p>
            <h2 class="h-section h-section--sm" id="before-title">Confirm your crossing</h2>
          </div>
          <p>Boat crossings are subject to weather and sea conditions. Confirm current schedules and arrangements with the resort before travelling.</p>
          <a class="btn btn--teal" href="contact.html">Message the Resort</a>
        </div>
      </div>
    </section>
'''
VAN = '<img src="assets/img/van-720.jpg" srcset="assets/img/van-720.jpg 720w, assets/img/van-1100.jpg 1100w" sizes="(min-width: 900px) 46vw, 92vw" width="1100" height="704" loading="lazy" decoding="async" style="--pos: 45% 55%" alt="The resort’s white Foton high-roof van parked on a tree-lined street">'
here = here.replace('VANIMG', VAN)
guides_set = '''    <ul data-set="guides">
      <li data-full="assets/img/guide-commute-1073.jpg" data-w="1073" data-h="598" data-caption="The resort's public transport guide" data-alt="Illustrated route from the Cubao bus terminal to General Luna Port and by boat to Maniwaya Island"></li>
      <li data-full="assets/img/guide-drive-1143.jpg" data-w="1143" data-h="1600" data-caption="The resort's self-drive guide to Maniwaya Island" data-alt="Illustrated road-trip guide from Metro Manila to General Luna Port, then by boat to Maniwaya Island"></li>
    </ul>
'''
page('getting-here.html', 'getting-here.html', 'Getting Here | Islas Moriones Beach Resort',
     'How to reach Islas Moriones on Maniwaya Island, Santa Cruz, Marinduque: routes to General Luna Port, the boat crossing, private boats and group van rental.',
     here, sets=island_set + guides_set)

# =====================================================================================  CONTACT
ICONS = {
    'fb': '<path fill="currentColor" d="M13.5 22v-8.2h2.8l.4-3.2h-3.2V8.5c0-.9.3-1.6 1.6-1.6h1.7V4.1c-.3 0-1.3-.1-2.5-.1-2.5 0-4.2 1.5-4.2 4.3v2.4H7.3v3.2h2.8V22h3.4z"/>',
    'wa': '<path fill="currentColor" d="M12 2.2a9.7 9.7 0 0 0-8.4 14.6L2.3 21.7l5-1.3A9.7 9.7 0 1 0 12 2.2zm0 17.7c-1.5 0-2.9-.4-4.1-1.1l-.3-.2-3 .8.8-2.9-.2-.3A8 8 0 1 1 12 19.9zm4.4-6c-.2-.1-1.4-.7-1.7-.8-.2-.1-.4-.1-.5.1l-.8 1c-.1.2-.3.2-.5.1a6.6 6.6 0 0 1-3.3-2.9c-.2-.4.2-.4.7-1.3.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.5-.4h-.5c-.2 0-.4.1-.6.3-.2.2-.8.8-.8 2s.8 2.3 1 2.5c.1.2 1.6 2.5 4 3.5 1.5.6 2 .7 2.8.6.4-.1 1.4-.6 1.6-1.1.2-.5.2-1 .1-1.1l-.4-.3z"/>',
    'mail': '<path fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round" d="M3.5 5.5h17v13h-17z M3.5 6l8.5 7 8.5-7"/>',
}
def cicon(href, key, label, text, tab=True):
    t = ' target="_blank" rel="noopener"' if tab else ''
    nt = NEWTAB if tab else ''
    return f'<li><a class="contact-row" href="{href}"{t}><span class="contact-row__icon"><svg viewBox="0 0 24 24" aria-hidden="true">{ICONS[key]}</svg></span><span><small>{label}</small>{text}</span>{nt}</a></li>'
contact = intro('Contact', 'Let’s plan your time at Islas Moriones', 'For room availability, visit our booking page. For tent stays, dining packages, experiences, or group arrangements, get in touch with the resort.') + f'''
    <section class="section section--dune" aria-label="Booking and contact">
      <div class="wrap contact-grid">
        <div class="contact-card" data-reveal>
          <p class="eyebrow">Rooms</p>
          <h2 class="h-section h-section--sm">Check availability</h2>
          <p>See current room rates and book direct through the resort’s booking page.</p>
          <a class="btn btn--teal" href="{BOOK}" target="_blank" rel="noopener">Check Availability{BOOKTAB}</a>
          <p class="note">The resort is also listed on <a href="{BCOM}" target="_blank" rel="noopener">Booking.com{NEWTAB}</a>.</p>
        </div>
        <div class="contact-card" data-reveal>
          <p class="eyebrow">Everything else</p>
          <h2 class="h-section h-section--sm">Message the Resort</h2>
          <ul class="contact-rows">
            {cicon(FB, 'fb', 'Facebook', 'Islas Moriones Beach Resort')}
            {cicon(WA, 'wa', 'WhatsApp', '+63 917 892 5752')}
            {cicon('mailto:' + MAIL, 'mail', 'Email', MAIL, tab=False)}
          </ul>
          <p class="note">Islas Moriones Beach Resort, Maniwaya Island, Santa Cruz, Marinduque, Philippines</p>
        </div>
      </div>
    </section>

    <section class="section" aria-labelledby="faq-title">
      <div class="wrap faq-grid">
        <div>
          <p class="eyebrow">Good to know</p>
          <h2 class="h-section" id="faq-title">Before you arrive</h2>
          <a class="text-link" href="good-to-know.html">Pet policy and more <span aria-hidden="true">→</span></a>
        </div>
        {FAQ}
      </div>
    </section>
'''
page('contact.html', 'contact.html', 'Contact | Islas Moriones Beach Resort',
     'Check availability at Islas Moriones Beach Resort, or message the resort on Facebook, WhatsApp or email about tent stays, dining, experiences and group plans.',
     contact)

# =====================================================================================  GOOD TO KNOW
know = intro('Good to Know', 'Before you arrive', 'Answers to common questions, from location to what is included, plus the resort’s pet policy.') + f'''
    <section class="section" aria-label="Questions and pet policy">
      <div class="wrap faq-grid">
        {PETS}
        {FAQ}
      </div>
    </section>

{closing('Ready to choose your dates?', 'Check availability on the booking page, or message the resort with your questions.')}'''
page('good-to-know.html', 'good-to-know.html', 'Good to Know | Islas Moriones Beach Resort',
     'Common questions about Islas Moriones on Maniwaya Island: location, getting there, booking, what is included, Wi-Fi and the pet policy.',
     know)
