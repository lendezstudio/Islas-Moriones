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
V = '12.1'

# ---------- reusable verified chunks from the current pages (read before overwriting) ----------
MENU, FAQ, PETS = rd('_tools/content/menu.html'), rd('_tools/content/faq.html'), rd('_tools/content/pets.html')
MENU = MENU.replace('<h3 class="visually-hidden">', '<h3 class="visually-hidden">')
# FAQ updates from the 2026 brochure (Wi-Fi and 24-hour electricity are now client-confirmed)
FAQ = FAQ.replace('<p>Yes. The resort has a 75 kVA backup diesel generator.</p>',
                  '<p>Yes. The resort lists 24-hour electricity, supported by a 75 kVA backup diesel generator.</p>')
FAQ = FAQ.replace('<span>Is there backup power?</span>', '<span>Is there electricity and Wi-Fi?</span>')
FAQ = FAQ.replace('supported by a 75 kVA backup diesel generator.</p>', 'supported by a 75 kVA backup diesel generator, and high-speed Starlink Wi-Fi.</p>')

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
    'maniwaya-aerial': '45% 55%', 'sea-rocks': '40% 60%', 'snorkel2': '55% 50%', 'snorkel3': '55% 50%', 'kubo-ext2': '50% 55%', 'e-palad': '45% 70%', 'e-tent-lime': '50% 100%', 'e-tent-teal': '50% 100%', 'e-sand-morion': '50% 70%', 'e-tidepool-p': '50% 55%', 'e-warrior-w': '100% 50%', 'e-warrior-p': '50% 50%', 'e-morion-bust': '50% 50%', 'e-kayak-lake': '53% 55%', 'e-pool-night-c': '42% 40%', 'e-sunglasses': '50% 20%', 'e-pool-bikes': '50% 55%', 'e-beach-tower': '52% 62%', 'e-beach-tower-p': '50% 60%', 'rock-cove': '50% 50%', 'vball': '50% 62%', 'pingpong2': '60% 72%', 'darts2': '50% 50%', 'deck-table': '50% 38%',
    'lobby-lounge': '50% 88%', 'lobby2': '50% 70%', 'maniwaya-cove': '0% 50%', 'beach-loungers': '50% 82%', 'sandbar-boat': '55% 70%',
    'tower-wide': '50% 92%', 'tower-blue': '50% 90%', 'tower-storm': '50% 38%', 'ecart': '50% 100%',
    'bikes-crop': '50% 35%', 'e-bikes-w': '60% 75%', 'e-bikes-p': '50% 90%', 'e-rock-w': '40% 50%', 'e-rock-p': '50% 65%', 'e-sanddollars-w': '50% 50%', 'e-sanddollars': '50% 64%', 'bikes': '50% 100%', 'kayak-pov': '50% 55%', 'kayak-pov-2': '40% 45%', 'beach-loungers': '50% 62%', 'kayak-clear': '50% 100%', 'kayak-clear-2': '50% 100%', 'tents-campsite': '32% 96%',
    'tent': '50% 78%', 'ungab-arch': '50% 70%', 'main-building': '50% 45%', 'genesis-front': '50% 70%',
    'n-coconut': '58% 20%', 'n-tower-sunset-w': '62% 55%', 'n-tower-sunset-p': '50% 55%', 'n-beach-sports': '50% 50%', 'n-beach-sports-p': '8% 50%', 'n-kayak-w': '45% 60%', 'n-kayak-p': '50% 60%', 'n-dive-shop-p': '50% 60%',
    'n-boodle-p': '50% 50%', 'n-celebrate-w': '50% 70%', 'n-celebrate-p': '50% 75%', 'n-cake': '50% 55%', 'n-dive-shop': '50% 60%', 'n-dive-gear': '50% 65%', 'n-hall-floral': '50% 70%',
    'e-tt-w': '50% 75%', 'badminton': '50% 55%', 'e-cliff-tree': '50% 45%', 'bonfire-smores': '42% 50%', 'e-loungers': '50% 60%', 'old:bamboo-raft': '50% 45%', 'e-boat-water': '50% 62%', 'poolsuite-bed': '50% 60%', 'e-sandbar-people': '50% 55%', 'e-vball': '45% 55%', 'darts2-full': '50% 50%',
    'n7-clown': '50% 55%',
    'genesis-lawn': '50% 75%', 'palms-sky': '50% 40%', 'maniwaya-rocks': '50% 70%', 'kubo-exterior': '50% 50%',
}

LB_FULL = {'tents-campsite': 'tents-campsite-full', 'darts2': 'darts2-full', 'e-pool-night-c': 'e-pool-night', 'e-kubo-cart-c': 'e-kubo-cart', 'e-morion-bust': 'e-morion-bust-full', 'e-warrior-l': 'e-warrior-w', 'e-warrior-p': 'e-warrior-p-full', 'e-sanddollars-w': 'e-sanddollars', 'bikes-crop': 'bikes', 'kayak-pov': 'kayak-clear', 'kayak-pov-2': 'kayak-clear-2', 'maniwaya-cove': 'maniwaya-cove-full', 'sunset-boat-beach': 'sunset-boat-beach-full', 'deck-table': 'deck-table-full'}  # cropped page images open uncropped in the lightbox
def full(jid):
    """Largest file for the lightbox."""
    jid = LB_FULL.get(jid, jid)
    if jid in SIZES:
        w, h = SIZES[jid][-1]; return f'assets/img/v5/{jid}-{w}.jpg', w, h
    widths, w, h = OLD[jid]; return f'assets/img/{jid}-{widths[-1]}.jpg', w, h

def ratio(jid):
    """Width / height of a derivative, so a slide can show the whole photo at its own shape."""
    w, h = SIZES[jid][-1] if jid in SIZES else OLD[jid][1:]
    return w / h
def slide(media, ar, label, inner_cls='tile__media'):
    return f'<li class="slide-item" style="--ar: {ar:.4f}" aria-roledescription="slide" aria-label="{label}"><figure class="tile"><div class="{inner_cls}">{media}</div></figure></li>'

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

BACK = '''      <div class="wrap"><a class="back-link" href="index.html" data-back><span aria-hidden="true">←</span> Back</a></div>
'''
def intro(eyebrow, h1, text, extra='', back=False):  # back: sub pages only, not the main menu pages
    return f'''    <section class="page-intro" aria-labelledby="page-title">
{BACK if back else ''}      <div class="prose center">
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
INCLUDED = [  # (photo id, alt, title, caption) all from the resort's inclusion list; whole photo, natural shape
    ('e-loungers', 'White sun loungers beside the turquoise pool, shaded by palms', 'Swimming pool', 'The outdoor pool, with loungers in the shade.'),
    ('bonfire-smores', 'Marshmallows toasting on skewers over a crackling bonfire at night', 'Bonfire', 'Toast marshmallows around the fire.'),
    ('e-pickleball', 'Aerial view of the green pickleball court and net, framed by garden beds and trees', 'Pickleball', 'A pickleball court, coming soon.'),
    ('old:bamboo-raft', 'The covered bamboo raft with a long table on turquoise water', 'Bamboo raft', 'Float off the shore on the resort’s bamboo raft.'),
    ('e-fire', 'A fire dancer spinning flames on the sand at night while guests watch from long tables', 'Fire show', 'Evenings by the fire on the sand.'),
    ('e-tt-w', 'Two table-tennis paddles and a ball on a blue table by the net, palms and the beach behind', 'Ping-pong', 'Table tennis in the shade of the palms.'),
    ('darts-terrace-d', 'A guest in a grey T-shirt taking aim at a dartboard on a wooden stand on the covered terrace', 'Darts', 'A dartboard for friendly games.'),
    ('badminton', 'Two badminton rackets and shuttlecocks resting on grass', 'Badminton', 'Rackets for a game on the lawn.'),
    ('e-vball', 'The volleyball net on the white-sand beach beside the lifeguard tower, an outrigger boat in the water beyond', 'Beach volleyball', 'A net on the sand, a few steps from the water.'),
]
def included_grid(sizes='(min-width: 600px) 46vw, 84vw'):
    out = []
    for jid, alt, t, c in INCLUDED:
        if jid.startswith('old:'):
            media, ar = old(jid[4:], alt, sizes), ratio(jid[4:])
        else:
            media, ar = pic(jid, alt, sizes), ratio(jid)
        out.append('            ' + slide(media, ar, t.replace('&amp;', 'and')))
    return '\n'.join(out)

CLOSER = [  # resort photographs, no overlaid text
    ('maniwaya-aerial', 'Marinduque coastline', 'Aerial view of a long white-sand beach lined with coconut palms, outrigger boats moored in the shallows'),
    ('e-warrior-w', 'Morion warrior beneath the reef', 'An underwater statue of a Morion warrior bust among coral on the sandy seabed'),
    ('e-beach-tower', 'Shade on the sand', 'Wicker sun loungers in the shade of a tree on the beach, the lifeguard tower and mountains beyond'),
    ('sandbar-boat', 'Palad Sandbar', 'Aerial view of an outrigger boat moored at the tip of a long white sandbar in turquoise water'),
    ('e-cliff-tree', 'Century Cliff Tree', 'A lone wind-shaped tree on a grassy clifftop above the blue sea'),
    ('e-pool-night2', 'The pool at night', 'The white main building and its lit pool after dark, palms in the courtyard'),
    ('e-sandbar-people', 'Sandbar from above', 'Aerial view of visitors walking along a white sandbar in turquoise water, boats moored off its tip'),
    ('n7-clown', 'Clownfish in the anemone', 'A red and black clownfish nestled among the golden tentacles of a sea anemone, brain coral and bright blue water behind'),
    ('e-pool-bikes', 'The pool and palms', 'The sunlit pool deck with bicycles beside the white resort buildings and palms'),
    ('e-sunglasses', 'Beach days', 'The white lifeguard tower and volleyball net on the sand, outrigger boats in the calm blue sea beyond'),
    ('e-kayak-lake', 'Crystal-clear kayak', 'A guest in a sun hat paddling a transparent kayak, mountains on the horizon'),
    ('e-sunset-coast', 'Sunset on the coast', 'A golden sunset over the rocky coastline'),
]
def closer_slides():
    sz = "(min-width: 600px) 46vw, 84vw"
    return '\n'.join('            ' + slide(pic(j, alt, sz), ratio(j), t) for j, t, alt in CLOSER)

home = f'''    <section class="film flow-hero" aria-label="Islas Moriones from the air and on the beach">
      <div class="film__frame">
        <video class="film__video" autoplay muted loop playsinline preload="auto" poster="assets/video/islas-moriones-hero-poster.jpg?v=3" aria-label="Aerial and beach views of Islas Moriones on Maniwaya Island" data-film>
          <source src="assets/video/islas-moriones-hero.mp4?v=5" type="video/mp4">
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
        <p>On Maniwaya Island, Islas Moriones is where island escapes, seaside moments, and good food come together.</p>
        <p>Whether you’re settling into a cozy room, trying out a tent stay, spending lazy days by the water, or sharing a few unforgettable days with your favorite people, there’s a little something here for every kind of getaway.</p>
        <p>Come for the island, stay for the memories.</p>
        <div class="actions actions--center">
          <a class="btn btn--teal" href="rooms.html">Explore the stays</a>
          <a class="btn btn--line" href="gallery.html">View the gallery</a>
        </div>
      </div>
    </section>

    <section class="section section--linen" aria-labelledby="glance-title">
      <div class="wrap">
        <div class="feature">
          <div class="glance-photos" data-reveal>
            <figure class="feature__media">{pic('e-dusk', 'The Islas Moriones sign at dusk, the lit main building and palms behind', '(min-width: 900px) 46vw, 92vw', '60% 50%')}</figure>
          </div>
          <div class="feature__text" data-reveal>
            <p class="eyebrow">The resort at a glance</p>
            <h2 class="h-section" id="glance-title">Everything in one island getaway</h2>
            <p>A beachfront resort on Maniwaya Island, with places to stay, eat, gather and unwind within a few steps of each other.</p>
            <ul class="glance">
              <li><strong>16</strong> air-conditioned rooms</li>
              <li>Beachfront white sands</li>
              <li>Outdoor infinity swimming pool</li>
              <li>Spacious camping grounds and bonfire area</li>
              <li>Easter Sunday Café and Restaurant</li>
              <li>Skylight Dining and Karaoke Bar</li>
              <li>The Genesis Events Place, conference room and facilities</li>
              <li>Seagrass 200 Dive Centre (scuba diving dive shop)</li>
              <li>Strong Wi-Fi (Starlink and Globe) and mobile signal</li>
              <li>24-hour electricity and water</li>
              <li class="glance__wide"><span class="glance__label">Relaxation and recreation</span>Pickleball, volleyball, badminton, football, ping-pong, darts, mountain bike and e-cart island exploration, crystal-clear kayaks, bamboo raft, snorkelling, massage and island hopping</li>
            </ul>
          </div>
        </div>
      </div>
    </section>

    <section class="section section--tight" aria-labelledby="closer-title">
      <div class="wrap">
        <header class="section-head center">
          <h2 class="h-section" id="closer-title">A closer look at island life</h2>
          <p>Explore the shoreline, the sea and island life around Islas Moriones.</p>
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
          <a class="pair__item" href="rooms.html#luxury-kubo" data-reveal>{pic('e-kubo-cart-c', 'The thatched Luxury Kubo with its white-railed veranda under coconut palms, a wooden cart on the lawn', '(min-width: 700px) 46vw, 92vw', '50% 58%')}<span class="pair__label">Luxury Kubo<small>A thatched-roof stay with a loft and kitchen</small></span></a>
          <a class="pair__item" href="rooms.html#tents" data-reveal>{pic('e-campsite', 'Dome tents and picnic tables on the sunny campsite beneath tall coconut palms', '(min-width: 700px) 46vw, 92vw', '50% 74%')}<span class="pair__label">Tent stays<small>Camp on the grounds under the palms</small></span></a>
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
{card(pic('sandbar-hop', 'Aerial view of outrigger boats anchored around a white sandbar in turquoise water', '(min-width: 900px) 30vw, 92vw', '50% 55%'), 'Island hopping', 'Visit Palad Sandbar, Sunong Bato, Ungab Rock Formation, the Century Cliff Tree and more around Maniwaya.', 'activities.html#island-hopping', 'Island-hopping stops')}
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
          <figure class="feature__media feature__media--wide" data-reveal>{pic('snorkel2', 'A snorkeller diving down through clear blue water in a trail of bubbles', '(min-width: 900px) 56vw, 92vw', '55% 50%')}</figure>
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
    ('n-dive-shop', 'Seagrass 200 Dive Centre', 'The glass shopfront of Seagrass 200 Dive Centre under a white pergola, dive gear on the terrace'),
    ('tower-wide', 'The beach', 'The white lifeguard tower and resort flags on the beach under a clear blue sky'),
    ('n-beach-sports', 'Jet skis on the beach', 'Jet skis pulled up on the resort beach, the white lifeguard tower and flags along the shore'),
    ('n-coconut', 'Lazy days by the pool', 'A fresh coconut with a frangipani flower beside an open book on the pool deck'),
    ('e-palad', 'Palad Sandbar (island hopping)', 'Palad Sandbar, a long white sandbar curving into turquoise water under a blue sky'),
    ('n-kayak-w', 'Crystal-clear kayak', 'Looking down through a crystal-clear kayak, life vests and a paddle over turquoise water, the island shore beyond'),
    ('n7-dog-w', 'A friendly face on the beach', 'A happy white dog standing on the sand, tongue out, with the sea and shady trees behind'),
    ('room-suiteloft', 'Suite Loft Room', 'A loft room with a staircase above the bed'),
    ('e-rock-w', 'Sunset over the coastal rocks', 'A pitted coastal rock topped with greenery above the sea, the sun setting gold on the horizon'),
    ('e-boat-water', 'By the shore', 'A small boat moored in clear water off the beach, a resort flag on the sand'),
    ('n-tower-sunset-w', 'Sunset on the beach', 'The lit lifeguard tower on the sand beside the volleyball net, the sky pink and orange at sunset'),
    ('e-bikes-w', 'Mountain bikes on Maniwaya', 'Two mountain bikes resting against a fallen palm trunk on the grass beneath tall coconut palms'),
    ('n5-dog-w', 'A friend on the sand', 'A happy bulldog on a leash lying on the warm sand by the sea at dusk'),
    ('e-sanddollars-w', 'Shells on the shore', 'A hand holding five white sand dollars above clear turquoise water'),
]
items = []
for i, (jid, cap, alt) in enumerate(STRIP, 1):
    media = f'<button class="slide-open" type="button" data-lightbox="strip" data-start="s{i}" aria-label="Open photo: {cap}">{pic(jid, alt, "(min-width: 600px) 46vw, 84vw")}</button>'
    items.append('          ' + slide(media, ratio(jid), cap))
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
    ('ps-034', 'Pool Suite Room, bedroom and lounge', 'The queen bed, sofa and breakfast bar under a timber ceiling'),
    ('ps-026', 'Pool Suite Room, queen bed', 'A queen bed with a padded bench at its foot'),
    ('ps-027', 'Pool Suite Room, the loft above the bedroom', 'The bedroom with the loft gallery above'),
    ('ps-033', 'Pool Suite Room, kitchen and breakfast bar', 'A kitchen with a hob and a long timber breakfast bar'),
    ('ps-028', 'Pool Suite Room, kitchen', 'A gas hob and range hood beside a garden window'),
    ('ps-025', 'Pool Suite Room, kitchen sink', 'A sink and dish rack below a garden window'),
    ('ps-030', 'Pool Suite Room, pantry', 'Open shelves with cups, a kettle and a refrigerator'),
    ('ps-029', 'Pool Suite Room, desk and clothes rack', 'A small desk and an open metal clothes rack'),
    ('ps-024', 'Pool Suite Room, bed by the balcony doors', 'A bed beside glass doors to the balcony'),
    ('ps-032', 'Pool Suite Room, view from the loft', 'Looking down from the loft over the kitchen'),
    ('ps-021', 'Pool Suite Room, beds upstairs', 'Beds and a sofa on the upper level'),
    ('ps-022', 'Pool Suite Room, beds upstairs', 'Double beds on the upper level beside the stair rail'),
    ('ps-023', 'Pool Suite Room, upper level', 'Beds below louvred windows on the upper level'),
    ('ps-020', 'Pool Suite Room, bathroom', 'A glass shower, toilet and stone basin'),
    ('ps-031', 'Pool Suite Room, bathroom', 'A glass shower, toilet and basin'),
])
kubo_set = lb_set('kubo', [
    ('kubo-ext2', 'The Luxury Kubo', 'The thatched Luxury Kubo and its veranda'),
    ('e-kubo-cart', 'The Luxury Kubo and the garden', 'The thatched Kubo under coconut palms, a wooden cart on the lawn'),
    ('e-kubo-palms', 'The Luxury Kubo under the palms', 'The thatched Kubo with umbrella tables on the lawn'),
    ('kubo-living2', 'Luxury Kubo, living area', 'A kitchenette, armchair and glass doors, the bedroom beyond'),
    ('kubo-lounge2', 'Luxury Kubo, lounge', 'A white sofa, TV and glass doors to the garden'),
    ('kubo-bed2', 'Luxury Kubo, bedroom', 'A queen bed under window blinds'),
    ('kubo-bed3', 'Luxury Kubo, bedroom', 'The queen bed made up with fresh towels beside an armchair'),
    ('kubo-loftbeds', 'Luxury Kubo, loft beds', 'Four single beds in the timber loft'),
    ('kubo-bath', 'Luxury Kubo, bathroom', 'A glass shower and toilet'),
])
def gallery_btn(setname, count):
    return f'<button class="btn btn--line btn--sm" type="button" data-lightbox="{setname}">View {count} photos</button>'

ROOMS = [
    ('Single Standard Room', pic('e-room-blue', 'Single Standard Room: a single bed against a blue accent wall', '(min-width: 900px) 30vw, (min-width: 600px) 46vw, 92vw', '50% 55%'), ['1–2 guests', '10 sqm', 'Ground floor, main building'], 'One single bed'),
    ('Double Standard Room', old('room-double-standard', 'Double Standard Room: a timber-framed bed with white pillows', '(min-width: 900px) 30vw, (min-width: 600px) 46vw, 92vw', '60% 55%'), ['2 guests', '15 sqm', 'Ground floor, main building'], None),
    ('Deluxe Room', pic('e-room-red', 'Deluxe Room: a queen bed against a red feature wall with framed art', '(min-width: 900px) 30vw, (min-width: 600px) 46vw, 92vw', '50% 55%'), ['2–3 guests', '30 sqm', 'Second floor, balcony, sea view'], 'One queen bed and one pull-out single bed'),
    ('Superior Room', pic('r-superior-3', 'Superior Room: two double beds made up with towels against a yellow feature wall, a curtained window beside them', '(min-width: 900px) 30vw, (min-width: 600px) 46vw, 92vw', '40% 50%'), ['4 guests', '25 sqm', 'Ground floor, main building'], 'Two twin beds'),
    ('Suite Room', pic('e-room-three', 'Suite Room: three beds made up with white linen under bright windows', '(min-width: 900px) 30vw, (min-width: 600px) 46vw, 92vw', '50% 55%'), ['5–6 guests', '36 sqm', 'Ground floor, main building'], 'Two twin beds plus one single, or plus two pull-out singles, depending on the room'),
    ('Suite Loft Room', pic('r-suiteloft-1', 'Suite Loft Room: a king bed beneath the timber staircase to the loft', '(min-width: 900px) 30vw, (min-width: 600px) 46vw, 92vw', '50% 55%'), ['5–6 guests', '50 sqm', 'Second floor, balcony, sea view'], 'One king bed and three single loft beds'),
    ('Executive Loft Room', pic('e-room-loft', 'Executive Loft Room: two wooden twin beds below the staircase to the loft', '(min-width: 900px) 30vw, (min-width: 600px) 46vw, 92vw', '50% 55%'), ['5–7 guests', '50 sqm', 'Second floor, balcony, sea view'], 'Two twin beds and three single loft beds'),
]
room_sets = {
    'single': ('Single Standard Room', [
        ('e-room-blue', 'Single Standard Room, bedroom', 'Single Standard Room, bedroom'),
        ('r-single-1', 'Single Standard Room, bedroom', 'Single Standard Room, bedroom'),
        ('r-single-2', 'Single Standard Room, another Single Standard Room', 'Single Standard Room, another Single Standard Room'),
        ('r-single-3', 'Single Standard Room, another Single Standard Room', 'Single Standard Room, another Single Standard Room'),
        ('r-single-bath', 'Single Standard Room, bathroom', 'Single Standard Room, bathroom'),
        ('r-single-bath2', 'Single Standard Room, bathroom', 'Single Standard Room, bathroom'),
        ('r-single-bath3', 'Single Standard Room, bathroom', 'Single Standard Room, bathroom'),
    ]),
    'deluxe': ('Deluxe Room', [
        ('e-room-red', 'Deluxe Room, bedroom', 'Deluxe Room, bedroom'),
        ('r-deluxe-1', 'Deluxe Room, bedroom', 'Deluxe Room, bedroom'),
        ('r-deluxe-2', 'Deluxe Room, bed and balcony curtains', 'Deluxe Room, bed and balcony curtains'),
        ('r-deluxe-3', 'Deluxe Room, another Deluxe Room', 'Deluxe Room, another Deluxe Room'),
        ('r-deluxe-4', 'Deluxe Room, another Deluxe Room', 'Deluxe Room, another Deluxe Room'),
        ('r-deluxe-bath', 'Deluxe Room, bathroom', 'Deluxe Room, bathroom'),
        ('r-deluxe-bath2', 'Deluxe Room, bathroom', 'Deluxe Room, bathroom'),
    ]),
    'superior': ('Superior Room', [
        ('r-superior-3', 'Superior Room, beds', 'Superior Room, beds'),
        ('r-superior-1', 'Superior Room, bedroom', 'Superior Room, bedroom'),
        ('r-superior-2', 'Superior Room, another Superior Room', 'Superior Room, another Superior Room'),
        ('r-superior-4', 'Superior Room, beds', 'Superior Room, beds'),
        ('r-superior-bath', 'Superior Room, bathroom', 'Superior Room, bathroom'),
        ('r-superior-bath2', 'Superior Room, bathroom', 'Superior Room, bathroom'),
        ('r-superior-bath3', 'Superior Room, bathroom', 'Superior Room, bathroom'),
    ]),
    'suite': ('Suite Room', [
        ('e-room-three', 'Suite Room, bedroom', 'Suite Room, bedroom'),
        ('r-suite-1', 'Suite Room, bedroom', 'Suite Room, bedroom'),
        ('r-suite-2', 'Suite Room, another Suite Room', 'Suite Room, another Suite Room'),
        ('e-room-yellow', 'Suite Room, beds with a pull-out bed', 'Two beds against a yellow-green wall, a pull-out bed beneath one'),
        ('r-suite-bath', 'Suite Room, bathroom', 'Suite Room, bathroom'),
        ('r-suite-bath2', 'Suite Room, bathroom', 'Suite Room, bathroom'),
        ('r-suite-bath3', 'Suite Room, bathroom', 'Suite Room, bathroom'),
    ]),
    'suiteloft': ('Suite Loft Room', [
        ('r-suiteloft-1', 'Suite Loft Room, bedroom', 'Suite Loft Room, bedroom'),
        ('r-suiteloft-2', 'Suite Loft Room, another Suite Loft Room', 'Suite Loft Room, another Suite Loft Room'),
        ('r-suiteloft-3', 'Suite Loft Room, another Suite Loft Room', 'Suite Loft Room, another Suite Loft Room'),
        ('r-suiteloft-4', 'Suite Loft Room, seating corner', 'Suite Loft Room, seating corner'),
        ('r-loftbeds', 'Suite Loft Room, single beds in the loft', 'Suite Loft Room, single beds in the loft'),
        ('r-suiteloft-5', 'Suite Loft Room, bedroom', 'Suite Loft Room, bedroom'),
        ('r-suiteloft-6', 'Suite Loft Room, bedroom', 'Suite Loft Room, bedroom'),
        ('r-suiteloft-7', 'Suite Loft Room, bedroom', 'Suite Loft Room, bedroom'),
        ('r-suiteloft-8', 'Suite Loft Room, stairs to the loft', 'Suite Loft Room, stairs to the loft'),
        ('r-suiteloft-9', 'Suite Loft Room, bedroom', 'Suite Loft Room, bedroom'),
        ('r-suiteloft-10', 'Suite Loft Room, bedroom', 'Suite Loft Room, bedroom'),
        ('r-suiteloft-11', 'Suite Loft Room, bedroom', 'Suite Loft Room, bedroom'),
        ('r-suiteloft-bath', 'Suite Loft Room, bathroom', 'Suite Loft Room, bathroom'),
        ('r-suiteloft-bath2', 'Suite Loft Room, bathroom', 'Suite Loft Room, bathroom'),
        ('r-suiteloft-bath3', 'Suite Loft Room, bathroom', 'Suite Loft Room, bathroom'),
    ]),
    'execloft': ('Executive Loft Room', [
        ('e-room-loft', 'Executive Loft Room, bedroom', 'Executive Loft Room, bedroom'),
        ('r-exec-2', 'Executive Loft Room, bedroom', 'Executive Loft Room, bedroom'),
        ('r-exec-1', 'Executive Loft Room, stairs to the loft', 'Executive Loft Room, stairs to the loft'),
        ('r-exec-3', 'Executive Loft Room, the loft', 'Executive Loft Room, the loft'),
        ('r-exec-5', 'Executive Loft Room, the loft', 'Three single beds under the sloping loft ceiling'),
        ('r-exec-4', 'Executive Loft Room, bedroom', 'Executive Loft Room, bedroom'),
        ('r-exec-bath', 'Executive Loft Room, bathroom', 'Executive Loft Room, bathroom'),
        ('r-exec-bath2', 'Executive Loft Room, bathroom', 'Executive Loft Room, bathroom'),
    ]),
}
rooms_lb = ''.join(lb_set('room-' + k, v[1]) for k, v in room_sets.items())
set_for = {v[0]: ('room-' + k, len(v[1])) for k, v in room_sets.items()}
room_cards = []
for name, img, facts, beds in ROOMS:
    f = ''.join(f'<li>{x}</li>' for x in facts)
    b = f'\n          <p>{beds}</p>' if beds else ''
    if name in set_for:
        b += '\n          ' + gallery_btn(*set_for[name])
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
              {gallery_btn('poolsuite', 15)}
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="section" id="luxury-kubo" aria-labelledby="kubo-title">
      <div class="wrap">
        <div class="feature feature--flip">
          <figure class="feature__media feature__media--tall" data-reveal>{pic('e-kubo-cart-c', 'The thatched Luxury Kubo with its white-railed veranda under coconut palms, a wooden cart on the lawn', '(min-width: 900px) 44vw, 92vw', '50% 58%')}</figure>
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
              {gallery_btn('kubo', 9)}
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
          <div class="feature__stack" data-reveal><figure class="feature__media">{pic('e-campsite-bamboo', 'Dome tents around bamboo picnic tables on the sunlit campsite beneath coconut palms', '(min-width: 900px) 52vw, 92vw', '50% 72%')}</figure><div class="feature__duo"><figure class="feature__media">{pic('e-tent-teal', 'A turquoise and white dome tent pitched on the lawn under coconut palms', '(min-width: 900px) 26vw, 46vw', '50% 100%')}</figure><figure class="feature__media">{pic('e-tent-lime', 'A lime-green dome tent on the grass in the palm garden', '(min-width: 900px) 26vw, 46vw', '50% 100%')}</figure></div></div>
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
            <a class="btn btn--line" href="ask-tents.html">Ask about tent stays</a>
          </div>
        </div>
      </div>
    </section>

{closing('Ready to choose your room?', 'See current rates and availability on the booking page, or message the resort about tent stays and group arrangements.')}'''
page('rooms.html', 'rooms.html', 'Stay | Islas Moriones Beach Resort',
     'Accommodations at Islas Moriones on Maniwaya Island: the Pool Suite Room, the Luxury Kubo, rooms in the main building and tent stays.',
     stay, sets=ps_set + kubo_set + rooms_lb)

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
              <figure class="inset">{pic('e-kayak', 'A guest in a sun hat paddling a transparent kayak on calm blue water', '(min-width: 900px) 16vw, 44vw', '55% 50%')}</figure>
              <figure class="inset">{pic('kayak-pov-2', 'Looking through the transparent hull of a clear kayak to the green water below', '(min-width: 900px) 16vw, 44vw')}</figure>
              <figure class="inset">{pic('kayak-sign', 'A crystal-clear kayak on the sand beside the Islas Moriones sign', '(min-width: 900px) 12vw, 30vw', '50% 62%')}</figure>
            </div>
          </div>
        </div>

        <div class="feature feature--flip jetskis" id="jet-skis">
          <figure class="feature__media" data-reveal>{pic('n-beach-sports', 'Jet skis pulled up on the resort beach, the white lifeguard tower and flags along the shore', '(min-width: 900px) 46vw, 92vw')}</figure>
          <div class="feature__text" data-reveal>
            <h3 class="h-section h-section--sm">Jet skis</h3>
            <p>Pick up the pace on the open water off Maniwaya. Ask the team about jet ski availability and arrangements for your dates.</p>
            <a class="btn btn--line" href="ask-jet-skis.html">Ask about jet skis</a>
          </div>
        </div>

        <div class="feature jetskis" id="banana-boat">
          <figure class="feature__media banana-frame" data-reveal>{pic('n7-banana-c', 'A bright yellow banana boat pulled up on the resort beach, clear kayaks on the sand and a jet ski out on the water', '(min-width: 900px) 46vw, 92vw')}</figure>
          <div class="feature__text" data-reveal>
            <h3 class="h-section h-section--sm">Banana boat</h3>
            <p>Gather your group, climb on and hold tight for a splash across the water off Maniwaya. Ask the team about rides and availability for your dates.</p>
            <a class="btn btn--line" href="ask-banana-boat.html">Ask about the banana boat</a>
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
{card(pic('biker', 'A rider in a helmet on a mountain bike on a grassy hilltop', '(min-width: 900px) 30vw, 92vw', '50% 15%'), 'Mountain bikes', 'Tour Maniwaya by mountain bike, with stops such as the Moriones Statue, Maniwaya Port, the Century Cliff Tree and the island’s old Chinese and Japanese mansion houses. A tour guide can be arranged.')}
{card(pic('e-ecart-roses', 'The resort’s white electric cart, decorated with yellow flowers, under coconut palms', '(min-width: 900px) 30vw, 92vw', '50% 60%'), 'Maniwaya Island tour', 'A land tour by electric cart to the Moriones Statue, Maniwaya Pier, Sunong Bato, the Century Cliff Tree and the Butterfly Farm. Senior and child friendly.')}
{card(old('exp-snorkel', 'A snorkeller swimming through clear blue water', '(min-width: 900px) 30vw, 92vw', '50% 35%'), 'Snorkelling gear', 'Masks, snorkels and fins are available.')}
{card(old('exp-massage', 'Hands giving a relaxing back massage to a guest lying under a white towel', '(min-width: 900px) 30vw, 92vw', '60% 50%'), 'In-room massage', 'Unwind after a day outdoors with a massage in your room.')}
{card(old('exp-karaoke', 'A microphone lit in purple stage light', '(min-width: 900px) 30vw, 92vw', '35% 50%'), 'Karaoke', 'A night in with your group and a few favourite songs.')}
{card(old('exp-laundry', 'Clothes being loaded into a front-loading washing machine', '(min-width: 900px) 30vw, 92vw', '45% 50%'), 'Laundry service', 'For longer stays, so you can pack light.')}
        </div>
      </div>
    </section>

    <section class="section" id="marine-life" aria-labelledby="sea-title">
      <div class="wrap">
        <header class="section-head section-head--split">
          <div>
            <p class="eyebrow">Beneath the water</p>
            <h2 class="h-section" id="sea-title">Meet Maniwaya’s marine life</h2>
          </div>
          <p>Snorkel the reefs around the island and you may meet clownfish, sea stars, sea turtles and reef octopus. Look, but never touch: some reef creatures, such as the blue-ringed octopus, are venomous.</p>
        </header>
        <div class="cards cards--4">
{card(pic('n5-anemone-w', 'Black, white and yellow clownfish sheltering among the long tentacles of a sea anemone on the reef', '(min-width: 900px) 22vw, (min-width: 600px) 46vw, 92vw'), 'Clownfish', 'Small clownfish shelter among the tentacles of a sea anemone. Watch them from a distance and leave the anemone untouched.')}
{card(pic('e-seastars', 'Orange and blue sea stars resting on the reef in clear shallow water', '(min-width: 900px) 22vw, (min-width: 600px) 46vw, 92vw', '50% 50%'), 'Sea stars', 'Orange and blue sea stars in the clear shallows. Admire them in the water and leave them where they live.')}
{card(pic('e-turtle', 'A sea turtle resting on the sand at night', '(min-width: 900px) 22vw, (min-width: 600px) 46vw, 92vw', '45% 62%'), 'Sea turtles', 'If you are lucky enough to see one, give it space and keep lights low.')}
{card(pic('e-octopus', 'A blue-ringed octopus on the sand among seagrass', '(min-width: 900px) 22vw, (min-width: 600px) 46vw, 92vw', '40% 60%'), 'Blue-ringed octopus', 'Beautiful and venomous. Admire it from a distance and never pick it up.')}
        </div>
        <div class="feature feature--flip shells" id="shells">
          <figure class="feature__media" data-reveal>{pic('e-sanddollars', 'A hand holding five white sand dollars above clear turquoise water and rippled sand', '(min-width: 900px) 46vw, 92vw', '50% 64%')}</figure>
          <div class="feature__text" data-reveal>
            <p class="eyebrow">On the shore</p>
            <h3 class="h-section h-section--sm">Pick up shells on Maniwaya</h3>
            <p>Walk the clear shallows and white sand at low tide and you can pick up shells and sand dollars along Maniwaya’s shore. Keep only empty, sun-bleached ones and leave anything still living in the water.</p>
          </div>
        </div>
        <div class="shells" id="birds">
          <header class="section-head section-head--split">
            <div>
              <p class="eyebrow">In the trees</p>
              <h3 class="h-section h-section--sm">Birds among the leaves</h3>
            </div>
            <p>Sea life is not the only wildlife on Maniwaya. Look up into the trees and you may spot songbirds bringing food to their young. Watch quietly from a distance and leave nests undisturbed.</p>
          </header>
          <div class="bird-photos" data-reveal>
            <figure class="feature__media">{pic('n5-birds-w', 'Two yellow-vented songbirds perched on a weathered branch among green leaves, one with an insect in its beak', '(min-width: 600px) 46vw, 46vw')}</figure>
            <figure class="feature__media">{pic('n5-nest-w', 'Three nestlings with bright red open beaks in a woven grass nest among green leaves', '(min-width: 600px) 46vw, 46vw')}</figure>
          </div>
        </div>
        <div class="friend" id="island-friend" data-reveal>
          <figure class="feature__media friend__media">{pic('n5-dog-p', 'A happy bulldog on a leash lying on the warm sand by the sea at dusk', '(min-width: 800px) 40vw, 92vw', '50% 75%')}</figure>
          <div class="friend__text">
            <p class="eyebrow">Golden hour</p>
            <h3 class="h-section">Friends on the sand</h3>
            <p>Some of the best company on Maniwaya has four paws. As the day cools and the sky turns gold, you may find these happy souls out on the warm sand, tongues out and in no hurry at all.</p>
          </div>
        </div>
        <div class="bird-photos friend-photos" data-reveal>
          <figure class="feature__media">{pic('n7-dog-p', 'A happy white dog standing on the sand, tongue out, with the sea and shady trees behind', '46vw', '50% 100%')}</figure>
          <figure class="feature__media">{pic('n7-chow-p', 'A fluffy golden Chow Chow sitting on the sand with its eyes closed and nose in the air, the volleyball net, resort flags and sea behind', '46vw')}</figure>
        </div>
        <div class="dive-photos" id="diving" data-reveal>
          <figure class="feature__media">{pic('n-dive-shop', 'The glass shopfront of Seagrass 200 Dive Centre under a white pergola, wetsuits hanging inside and dive gear on the terrace', '(min-width: 900px) 46vw, 92vw')}</figure>
          <figure class="feature__media">{pic('n-dive-gear', 'Scuba tanks, buoyancy vests, fins and gear boxes laid out on the terrace of the dive centre', '(min-width: 900px) 46vw, 92vw')}</figure>
        </div>
        <div class="extras-band dive-band" data-reveal>
          <div>
            <p class="eyebrow">Scuba diving</p>
            <h3 class="h-section h-section--sm">Seagrass 200 Dive Centre</h3>
          </div>
          <p>The resort is home to Seagrass 200 Dive Centre, a scuba diving dive shop. Ask the team about dives and arrangements during your stay.</p>
          <a class="btn btn--teal" href="ask-diving.html">Ask about diving</a>
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
{stop(pic('e-palad', 'Palad Sandbar, a long white sandbar curving into turquoise water under a blue sky', '(min-width: 900px) 30vw, 46vw', '50% 50%'), 'Palad Sandbar', 'Offshore', 'A natural sandbar that fully appears at low tide.')}
{stop(pic('sunong-bato-b', 'Sunong Bato, a stacked rock formation in clear turquoise water', '(min-width: 900px) 30vw, 46vw', '50% 50%'), 'Sunong Bato', 'South-east Maniwaya', 'A stacked-rock formation above clear water.')}
{stop(pic('e-ungab', 'Ungab Rock Formation, a natural rock arch topped with greenery above calm green water', '(min-width: 900px) 30vw, 46vw', '50% 50%'), 'Ungab Rock Formation', 'Mompong Island', 'Limestone arches around a sheltered cove.')}
{stop(pic('reef-raft2', 'A floating bamboo raft with a canopy and resort flags', '(min-width: 900px) 30vw, 46vw', '50% 55%'), 'Morion Reef Raft', 'Off the west coast', 'A floating raft above the Morion Reef snorkelling area.')}
{stop(pic('e-cliff-tree', 'The Century Cliff Tree, a lone wind-shaped tree on a grassy clifftop above the blue sea', '(min-width: 900px) 30vw, 46vw', '50% 40%'), 'Century Cliff Tree', 'South-east Maniwaya', 'A lone tree on a clifftop above the sea.')}
{stop(pic('e-statues', 'Statues of Morion warriors beside tall stone columns under palms', '(min-width: 900px) 30vw, 46vw', '50% 50%'), 'Morion Statues', 'Island-hopping stop', 'Statues of Marinduque’s Morion warriors.')}
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
     'Experiences at Islas Moriones on Maniwaya Island: included amenities, crystal-clear kayaks, scuba diving, boat rentals, island hopping, bikes and e-cart land tours.',
     exp, sets=island_set)

# =====================================================================================  DINING
BA_ALT = 'A breakfast plate of garlic rice, a fried egg, dried fish and mango on a table by the beach, palms and the sea behind'
dining = intro('Dining', 'A table for your island stay', 'From everyday meals to dining together as a group, explore the food experiences available at Islas Moriones.') + f'''
    <section class="section section--sandbg2" aria-labelledby="sky-title">
      <div class="wrap">
        <div class="feature">
          <figure class="feature__media feature__media--wide" data-reveal>{pic('skylight', 'Skylight Dining: tables and chairs beneath a glass-roofed pavilion beside the main building, framed by coconut palms', '(min-width: 900px) 56vw, 92vw', '45% 55%', eager=True)}</figure>
          <div class="feature__text" data-reveal>
            <p class="eyebrow">New</p>
            <h2 class="h-section" id="sky-title">Skylight Dining</h2>
            <p>The resort’s newest dining space: a pavilion with a glass roof beside the main building, with long tables under the palms. Explore it during your stay.</p>
            <a class="btn btn--line" href="ask-dining.html?about=Skylight%20Dining">Ask about dining</a>
          </div>
        </div>
      </div>
    </section>

    <section class="section" aria-labelledby="cafe-title">
      <div class="wrap">
        <header class="section-head section-head--split">
          <div class="cafe-head">
            <img class="cafe-logo" src="assets/img/v5/cafe-logo-480.jpg" width="480" height="476" alt="Easter Sunday Café at Islas Moriones Beach Resort logo" loading="lazy" decoding="async">
            <div>
              <p class="eyebrow">Easter Sunday Café</p>
              <h2 class="h-section" id="cafe-title">Find your favourites</h2>
            </div>
          </div>
          <div>
            <p>Filipino, American and continental breakfasts in the morning, then soups, grilled dishes, seafood and pasta through the afternoon and evening.</p>
            <dl class="hours"><div><dt>Breakfast</dt><dd>7:00 – 9:00 AM</dd></div><div><dt>Lunch &amp; dinner</dt><dd>11:00 AM – 8:00 PM</dd></div></dl>
          </div>
        </header>
        {MENU}
      </div>
    </section>

    <section class="section section--dune" aria-labelledby="plates-title">
      <div class="wrap">
        <div class="venue">
          <figure class="venue__a has-alt" data-reveal><span class="v-land">{pic('n-breakfast', BA_ALT, '(min-width: 900px) 30vw, 92vw', '50% 88%')}</span><span class="v-port">{pic('n-breakfast', BA_ALT, '(min-width: 900px) 30vw, 92vw', '50% 70%')}</span></figure>
          <figure class="venue__b" data-reveal>{pic('n-boodle-p', 'A boodle fight spread on banana leaves: grilled fish, crab, shrimp, rice, plantains and fruit with dipping sauces', '(min-width: 900px) 24vw, 46vw')}</figure>
          <figure class="venue__c" data-reveal>{pic('n-breakfast-brand', 'Pancakes, toast and scrambled egg beside an Islas Moriones table sign, the beach beyond', '(min-width: 900px) 24vw, 46vw')}</figure>
          <div class="venue__text" data-reveal>
            <p class="eyebrow">From the kitchen</p>
            <h2 class="h-section" id="plates-title">Island plates, morning to night</h2>
            <p>Start the day with breakfast a few steps from the sand, then gather your group around a boodle fight of grilled seafood, rice and fruit laid out on banana leaves.</p>
            <a class="btn btn--line" href="ask-dining.html?about=Meals%20during%20my%20stay">Ask about meals</a>
          </div>
        </div>
      </div>
    </section>

    <section class="section section--linen" aria-labelledby="pk-title">
      <div class="wrap">
        <header class="section-head center">
          <p class="eyebrow">Dining packages</p>
          <h2 class="h-section" id="pk-title">Make a meal part of the occasion</h2>
        </header>
        <div class="cards cards--3">
{card(pic('deck-table', 'A long wicker dining table and chairs on a timber deck, open to the garden and coconut palms', '(min-width: 900px) 30vw, 92vw', '50% 38%'), 'Meal packages', 'Ask about meal packages for your stay and the arrangements available for your group.')}
{card(old('bamboo-raft', 'The covered bamboo raft with a long bamboo table on turquoise water', '(min-width: 900px) 30vw, 92vw', '50% 45%'), 'Boodle fight dining', 'Gather around a shared boodle fight setup and make a meal part of the occasion. It can also be set up on the bamboo raft.')}
{card(pic('e-beach-dining', 'Long tables set on the beach at dusk beneath string lights', '(min-width: 900px) 30vw, 92vw', '50% 55%'), 'Bonfire menu packages', 'Explore the resort’s bonfire menu packages for another way to spend an evening together.')}
        </div>
        <div class="actions actions--center">
          <a class="btn btn--teal" href="ask-dining.html?about=Meal%20packages">Ask about dining packages</a>
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
    ('e-pavilion', 'The Genesis and its al fresco cocktail area', 'Cocktail tables dressed in white on the lawn in front of The Genesis'),
    ('genesis-tables', 'Round tables inside The Genesis', 'Round tables with gold chairs and flowers'),
    ('n-hall-floral', 'Flowers on the long tables', 'Bright flower arrangements down a long table set with gold chargers inside The Genesis'),
    ('n-hall-round', 'A round-table reception', 'Round tables with gold chargers, flowers and gold chairs beneath draped fabric'),
    ('genesis-setup', 'The Genesis, banquet setup', 'Dining tables set for an event'),
    ('genesis-dinner', 'The Genesis, evening setup', 'Tables set with linen and flowers'),
    ('genesis-front', 'The Genesis from the lawn', 'The venue entrance with cocktail tables on the lawn'),
    ('genesis-lawn', 'Cocktail tables on the lawn', 'White-dressed cocktail tables on the lawn'),
])
CA_ALT = 'A long garden table at dusk dressed with pink runners, roses and candles beneath string lights and palms'
groups = intro('Gatherings &amp; Events', 'An island setting for getting together', 'Explore the events venue at Islas Moriones and speak with the team about bringing your group to Maniwaya.') + f'''
    <section class="section section--sandbg5" aria-labelledby="gen-title">
      <div class="wrap">
        <div class="venue">
          <figure class="venue__a" data-reveal>{pic('genesis-hall', 'The Genesis Events Place: white fabric draped from a high ceiling over long dining tables, with glass walls to the garden', '(min-width: 900px) 46vw, 92vw', '50% 50%', eager=True)}</figure>
          <figure class="venue__b" data-reveal>{pic('e-pavilion', 'The Genesis from the garden, with white-dressed cocktail tables on the lawn', '(min-width: 900px) 24vw, 46vw', '50% 60%')}</figure>
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
              <a class="btn btn--teal" href="ask-gatherings.html">Tell us about your gathering</a>
              {gallery_btn('genesis', 9)}
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="section" id="weddings" aria-labelledby="wed-title">
      <div class="wrap">
        <div class="feature">
          <figure class="feature__media feature__media--tall" data-reveal>{pic('e-wedding-aisle', 'A beach wedding aisle at sunset: a white runner lined with lanterns and flowers leading to a draped arch by the sea', '(min-width: 900px) 44vw, 92vw', '50% 55%')}</figure>
          <div class="feature__text" data-reveal>
            <p class="eyebrow">Weddings</p>
            <h2 class="h-section" id="wed-title">Begin your forever by the sea</h2>
            <p>Celebrate at The Genesis and its al fresco cocktail and lounge area. Each wedding package is designed for 100 guests and includes exclusive venue use, accommodation, round-trip private boat transfers from Buyabod Port in Santa Cruz, food and beverages, wedding styling and an in-house coordinator on the day.</p>
            <dl class="spec">
              <div><dt>The Minimalist</dt><dd>A simple, beautiful celebration: an overnight stay for the couple and family, reception styling, an arch-mirror photo area, and a bridal e-cart with floral styling.</dd></div>
              <div><dt>The Romantic</dt><dd>Premium catering and décor: an overnight stay for the couple and entourage, a floral portrait wall, dance-floor and party lighting, and a fireworks display.</dd></div>
              <div><dt>The Luxury</dt><dd>A grand celebration: three days and two nights for the couple and entourage, fresh and premium flowers, a professional DJ and host, fireworks, a buko station and full supplier coordination.</dd></div>
            </dl>
            <p class="note">Extra guests, a ceremony setup, a wedding singer and a <em>putong</em> ceremonial dance can be added to any package.</p>
            <div class="inset-row inset-row--wide">
              <figure class="inset">{pic('e-ecart-roses', 'The bridal e-cart decorated with yellow flowers', '(min-width: 900px) 16vw, 44vw', '50% 60%')}</figure>
              <figure class="inset">{pic('e-beach-dining', 'Long tables set on the beach at dusk beneath string lights', '(min-width: 900px) 16vw, 44vw', '50% 55%')}</figure>
              <figure class="inset">{pic('genesis-tables', 'Round tables with gold chairs and flower arrangements inside The Genesis', '(min-width: 900px) 16vw, 44vw', '50% 60%')}</figure>
            </div>
            <div class="actions">
              <a class="btn btn--teal" href="ask-gatherings.html?about=Wedding">Ask about wedding packages</a>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="section section--dune" id="celebrations" aria-labelledby="cele-title">
      <div class="wrap">
        <div class="feature feature--flip">
          <figure class="feature__media feature__media--wide has-alt" data-reveal><span class="v-land">{pic('n-celebrate-w', CA_ALT, '(min-width: 900px) 56vw, 92vw')}</span><span class="v-port">{pic('n-celebrate-p', CA_ALT, '(min-width: 900px) 56vw, 92vw')}</span></figure>
          <div class="feature__text" data-reveal>
            <p class="eyebrow">Celebrations</p>
            <h2 class="h-section" id="cele-title">Birthdays, reunions and milestones</h2>
            <p>Mark the occasion with the people who matter, from a birthday dinner under the palms to a family reunion by the sea. Share your date, guest count and plans, and the team will talk you through the group packages and arrangements available.</p>
            <div class="inset-row">
              <figure class="inset">{pic('n-cake', 'A floral birthday cake on a table set with pink roses, candles and glassware', '(min-width: 900px) 16vw, 44vw')}</figure>
              <figure class="inset">{pic('n-hall-floral', 'Bright flower arrangements down a long table set with gold chargers', '(min-width: 900px) 16vw, 44vw')}</figure>
              <figure class="inset">{pic('n-longtable', 'A long outdoor table laid with bowls, plates and a colourful tropical runner under the trees', '(min-width: 900px) 16vw, 44vw', '50% 40%')}</figure>
            </div>
            <a class="btn btn--teal" href="ask-gatherings.html?about=Birthday%20or%20celebration">Plan a celebration</a>
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
            <a class="btn btn--teal" href="ask-gatherings.html?about=Company%20outing%20or%20team%20building">Plan a team visit</a>
          </div>
        </div>
      </div>
    </section>

    <section class="section" aria-label="Group options">
      <div class="wrap">
        <div class="cards cards--3">
{card(pic('e-resort-path', 'The white resort buildings beside the palm-lined pool and garden path', '(min-width: 900px) 30vw, 92vw', '50% 55%'), 'Day visits', 'Spend the day enjoying the beach, pool, and selected resort amenities, 8 AM to 5 PM. Day tours are subject to availability.')}
{card(pic('e-boat-water', 'A small boat moored in clear water off the beach, a resort flag on the sand', '(min-width: 900px) 30vw, 92vw', '50% 60%'), 'Group packages', 'Ask the team about packages for reunions, celebrations and other group stays.')}
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
G = [  # (category, id, caption, alt), in viewing order
    ('resort', 'e-dusk', 'The resort at dusk', 'The resort sign and lit main building at dusk'),
    ('resort', 'e-sign', 'Welcome to Islas Moriones', 'The wooden resort sign in the garden'),
    ('resort', 'e-resort-pool', 'The pool and main building', 'The white main building beside the palm-lined pool'),
    ('resort', 'e-pool-night2', 'The pool at night', 'The white main building and lit pool after dark'),
    ('resort', 'main-building', 'The main building', 'The white main building with its gabled roof'),
    ('resort', 'reception', 'Reception', 'The reception desk below a double-height staircase'),
    ('resort', 'lobby2', 'The lobby lounge', 'A lounge with a leaf-pattern mural'),
    ('resort', 'e-resort-path', 'The garden path', 'A path beside the palm-lined pool'),
    ('resort', 'e-pool-bikes', 'Poolside', 'Bicycles by the sunlit pool deck'),
    ('resort', 'e-loungers', 'Pool loungers', 'White sun loungers beside the pool'),
    ('resort', 'n-coconut', 'Lazy days by the pool', 'A fresh coconut and an open book on the pool deck'),
    ('resort', 'dusk-pool', 'The pool at dusk', 'The pool beside the main building at dusk'),
    ('resort', 'e-pool-night', 'The pool at night', 'The lit pool beneath the main building after dark'),
    ('resort', 'e-pool-pergola', 'Evening by the pool', 'The pool seen through pergola beams at night'),
    ('resort', 'palms-sky', 'Coconut palms', 'Coconut palms against a blue sky'),
    ('resort', 'n-palm-lawn', 'The palm garden', 'Tall coconut palms over a green lawn under a blue sky'),
    ('resort', 'beach-palms', 'Palms along the shore', 'Palms shading the sand in front of the resort'),
    ('resort', 'e-beach-tower', 'Sun loungers on the beach', 'Wicker loungers in the shade, the lifeguard tower and mountains beyond'),
    ('resort', 'e-sunglasses', 'Beach days', 'Sunglasses on a lounger, the lifeguard tower beyond'),
    ('resort', 'tower-blue', 'The lifeguard tower', 'The white lifeguard tower against a deep blue sky'),
    ('resort', 'tower-wide', 'The beachfront', 'The lifeguard tower and resort flags on the beach'),
    ('resort', 'n-beach-sports', 'Jet skis on the beach', 'Jet skis on the sand, the lifeguard tower and flags along the shore'),
    ('resort', 'e-vball-wide', 'The beachfront', 'The volleyball net on the beach beneath shady trees'),
    ('resort', 'tower-storm', 'Before the rain', 'The lifeguard tower under dark storm clouds'),
    ('resort', 'e-dog', 'Pet-friendly stays', 'A bulldog on a leash on the sandy resort path'),
    ('resort', 'n5-dog-p', 'A friend on the sand', 'A happy bulldog on a leash lying on the warm sand by the sea at dusk'),
    ('resort', 'n7-dog-p', 'A friendly face on the beach', 'A happy white dog standing on the sand, tongue out, with the sea and shady trees behind'),
    ('resort', 'n7-chow-w', 'Sun on the sand', 'A fluffy golden Chow Chow sitting on the wide sandy beach, the volleyball net, resort flags and sea behind'),
    ('stays', 'poolsuite-room', 'Pool Suite Room', 'Queen bed, sofa and kitchen in the Pool Suite Room'),
    ('stays', 'poolsuite-loft', 'Pool Suite Room, loft view', 'Looking down from the loft over the kitchen'),
    ('stays', 'poolsuite-family', 'Pool Suite Room, upstairs', 'Double beds on the upper level'),
    ('stays', 'poolsuite-bar', 'Pool Suite breakfast bar', 'A timber breakfast bar with stools'),
    ('stays', 'poolsuite-bath', 'Pool Suite bathroom', 'A bathroom with a glass shower'),
    ('stays', 'e-kubo-cart', 'The Luxury Kubo', 'The thatched Kubo and a wooden cart under the palms'),
    ('stays', 'e-kubo-palms', 'The Luxury Kubo', 'The thatched Kubo with umbrella tables on the lawn'),
    ('stays', 'kubo-living', 'Luxury Kubo lounge', 'A white sofa beside glass doors'),
    ('stays', 'kubo-loftbeds', 'Luxury Kubo, loft beds', 'Four single beds in the timber loft'),
    ('stays', 'e-room-blue', 'Single Standard Room', 'A single bed against a blue accent wall'),
    ('stays', 'room-single', 'Single Standard Room', 'A single bed beside a teal wall'),
    ('stays', 'e-room-red', 'Deluxe Room', 'A queen bed against a red feature wall'),
    ('stays', 'room-deluxe', 'Deluxe Room', 'A queen bed against a red feature wall'),
    ('stays', 'e-room-yellow', 'Suite Room', 'Two beds against a yellow-green wall, a pull-out bed beneath one'),
    ('stays', 'room-superior', 'Superior Room', 'Two beds against a yellow wall'),
    ('stays', 'e-room-three', 'Suite Room', 'Three beds under bright windows'),
    ('stays', 'e-room-loft', 'Executive Loft Room', 'Two twin beds below the loft staircase'),
    ('stays', 'room-execloft', 'Executive Loft Room', 'Two beds below a staircase to the loft'),
    ('stays', 'room-suiteloft', 'Suite Loft Room', 'A bed beneath a staircase to the loft'),
    ('stays', 'room-loftsingles', 'Single loft beds', 'Three single beds on a loft level'),
    ('stays', 'e-room-family', 'Guest room', 'A room with several beds and a grey accent wall'),
    ('stays', 'e-room-two', 'Guest room', 'Two neatly made beds in a bright room'),
    ('stays', 'e-room-teal', 'Guest room', 'A bed with a trundle against a teal wall'),
    ('stays', 'e-campsite', 'The campsite', 'Dome tents and picnic tables beneath tall coconut palms'),
    ('stays', 'e-tent-teal', 'Tent stays', 'A turquoise dome tent under coconut palms'),
    ('stays', 'e-tent-lime', 'Tent stays', 'A lime-green dome tent in the palm garden'),
    ('stays', 'tent', 'Tent stay', 'A tent on the lawn under coconut palms'),
    ('dining', 'skylight', 'Skylight Dining', 'Tables beneath the glass-roofed Skylight Dining pavilion'),
    ('dining', 'skylight-2', 'Skylight Dining', 'The Skylight Dining pavilion beside the main building'),
    ('dining', 'n-breakfast', 'Breakfast by the beach', 'A breakfast plate of garlic rice, egg, dried fish and mango'),
    ('dining', 'n-breakfast-brand', 'Morning by the sea', 'Pancakes and toast beside an Islas Moriones table sign, the beach beyond'),
    ('dining', 'n-boodle-p', 'Boodle fight', 'Grilled seafood, rice and fruit laid out on banana leaves'),
    ('dining', 'n-seafood-p', 'Seafood on banana leaves', 'Crab, shrimp and grilled seafood with plantains on banana leaves'),
    ('dining', 'n-watermelon-p', 'Watermelon by the water', 'A hand holding watermelon slices above the clear sea'),
    ('dining', 'deck-table', 'Dining on the deck', 'A wicker dining table on the timber deck'),
    ('dining', 'n-longtable', 'A table for the group', 'A long outdoor table laid with bowls and a tropical runner'),
    ('dining', 'e-beach-dining', 'Dinner on the beach', 'Long tables on the sand under string lights at dusk'),
    ('gatherings', 'genesis-hall', 'The Genesis Events Place', 'Long tables beneath draped fabric inside The Genesis'),
    ('gatherings', 'n-hall-round', 'A round-table reception', 'Round tables with gold chargers and flowers inside The Genesis'),
    ('gatherings', 'genesis-tables', 'Round-table setup', 'Round tables with gold chairs inside The Genesis'),
    ('gatherings', 'n-hall-floral', 'Flowers on the long tables', 'Bright flower arrangements down a long table inside The Genesis'),
    ('gatherings', 'genesis-dinner', 'Evening setup', 'Tables set with linen and flowers'),
    ('gatherings', 'genesis-front', 'The Genesis from the lawn', 'Cocktail tables on the lawn in front of The Genesis'),
    ('gatherings', 'e-pavilion', 'The Genesis lawn', 'Cocktail tables on the lawn in front of The Genesis'),
    ('gatherings', 'e-wedding-aisle', 'Beach wedding', 'A lantern-lined wedding aisle on the beach at sunset'),
    ('gatherings', 'n-celebrate-w', 'Celebrations under the palms', 'A long garden table with pink runners and roses beneath string lights at dusk'),
    ('gatherings', 'n-cake', 'A birthday table', 'A floral birthday cake among pink roses and candles'),
    ('gatherings', 'e-fire', 'Fire show', 'A fire dancer performing for guests at night'),
    ('experiences', 'e-kayak', 'Crystal-clear kayak', 'A guest paddling a transparent kayak'),
    ('experiences', 'kayak-float', 'Crystal-clear kayak', 'A swimmer beside a transparent kayak, seen from above'),
    ('experiences', 'kayak-clear', 'Crystal-clear kayak', 'A crystal-clear kayak on calm water'),
    ('experiences', 'kayak-sign', 'Crystal-clear kayak', 'A clear kayak beside the resort sign'),
    ('experiences', 'n-dive-shop', 'Seagrass 200 Dive Centre', 'The glass shopfront of the dive centre under a white pergola'),
    ('experiences', 'n-dive-gear', 'Ready to dive', 'Scuba tanks, vests and fins on the dive centre terrace'),
    ('experiences', 'n7-beach-p', 'Banana boat on the beach', 'A yellow banana boat and clear kayaks on the sand beneath a palm and resort flags'),
    ('experiences', 'e-tt-w', 'Table tennis', 'Paddles and a ball on the table tennis table under the palms'),
    ('experiences', 'vball', 'Beach volleyball', 'A volleyball on the sand'),
    ('experiences', 'e-vball', 'Beach volleyball', 'The volleyball net by the lifeguard tower'),
    ('experiences', 'darts-terrace-d', 'Darts', 'A guest in a grey T-shirt taking aim at a dartboard on a wooden stand on the covered terrace'),
    ('experiences', 'bikes-crop', 'Mountain bikes', 'Two mountain bikes on the rocky shore'),
    ('experiences', 'n7-bikes-p', 'Mountain bikes, ready to ride', 'Mountain bikes hung in neat rows along a white wall in the covered walkway'),
    ('experiences', 'ecart', 'E-cart land tour', 'An electric cart on the seawall'),
    ('experiences', 'e-ecart-roses', 'Island tour by e-cart', 'The electric cart decorated with yellow flowers'),
    ('experiences', 'n-picnic', 'A picnic by the sea', 'A picnic blanket on the rocky shore above a clear cove'),
    ('experiences', 'boat-longinus', 'M/V St. Longinus', 'The resort’s boat St. Longinus in clear water'),
    ('experiences', 'boat-omon', 'M/V Omon Express', 'The resort’s big outrigger boat in shallow water'),
    ('experiences', 'boat-rogelius', 'M/V Rogelius', 'A white outrigger boat with a canopy'),
    ('experiences', 'e-boat-beach', 'Outrigger boat', 'An outrigger boat pulled up on the sand by the resort flags'),
    ('experiences', 'e-boat-water', 'Boat by the shore', 'A small boat moored off the beach'),
    ('experiences', 'e-sanddollars', 'Sand dollars', 'Five white sand dollars held over turquoise water'),
    ('experiences', 'e-seastars', 'Sea stars', 'Orange and blue sea stars on the reef'),
    ('experiences', 'e-turtle', 'Sea turtle', 'A sea turtle on the sand at night'),
    ('experiences', 'e-octopus', 'Blue-ringed octopus', 'A blue-ringed octopus among seagrass'),
    ('experiences', 'n5-anemone-p', 'Clownfish', 'Clownfish among the tentacles of a sea anemone'),
    ('experiences', 'n7-clown', 'Clownfish in the anemone', 'A red and black clownfish nestled among the golden tentacles of a sea anemone, brain coral behind'),
    ('experiences', 'e-warrior-w', 'The Morion warrior beneath the reef', 'A Morion warrior bust among coral on the seabed'),
    ('experiences', 'e-sand-morion', 'A Morion in the sand', 'A sandcastle carved as a Morion warrior by the volleyball net'),
    ('experiences', 'n5-birds-p', 'Birds among the leaves', 'Two songbirds perched on a weathered branch, one with an insect in its beak'),
    ('experiences', 'n5-nest-p', 'Nestlings', 'Three nestlings with bright red open beaks in a woven nest'),
    ('experiences', 'e-palad', 'Palad Sandbar (island hopping, not resort grounds)', 'A long white sandbar in turquoise water'),
    ('experiences', 'e-sandbar-people', 'Palad Sandbar from the air (island hopping)', 'Visitors walking along the sandbar'),
    ('experiences', 'sandbar-aerial', 'Palad Sandbar (island hopping, not resort grounds)', 'A white sandbar in turquoise water'),
    ('experiences', 'e-sandbar-aerial', 'Sandbar and boats (island hopping)', 'Outrigger boats moored along a sandbar, from above'),
    ('experiences', 'n-sandbar', 'A sandbar at low tide (island hopping, not resort grounds)', 'A narrow sandbar stretching into turquoise water'),
    ('experiences', 'e-ungab', 'Ungab Rock Formation (island hopping)', 'A natural rock arch above calm water'),
    ('experiences', 'ungab-arch', 'Ungab Rock Formation (island hopping, not resort grounds)', 'A rock arch above a cove'),
    ('experiences', 'n-rock-arch', 'Through the rock arch (island hopping, not resort grounds)', 'Turquoise water seen through a natural rock arch'),
    ('experiences', 'e-cliff-tree', 'Century Cliff Tree (island hopping)', 'A lone tree on a grassy clifftop'),
    ('experiences', 'e-statues', 'Moriones Statue (island tour)', 'Morion warrior statues beside stone columns'),
    ('experiences', 'maniwaya-rocks', 'Maniwaya shoreline (not resort grounds)', 'Rocks and the Maniwaya sign above the shore'),
    ('experiences', 'n-rocky-coast', 'Century Tree on the rocky coast (not resort grounds)', 'The Century Tree on a rocky clifftop above clear water'),
    ('resort', 'e-sunset-coast', 'Sunset on the coast', 'A golden sunset over the rocky coastline'),
    ('experiences', 'e-sunset-rocks', 'Sunset over the coastal rocks', 'The sun setting behind a rock formation at sea'),
    ('resort', 'n-sunset-sea', 'Sunset over the sea', 'The sun setting on the horizon beneath an orange sky'),
    ('resort', 'n-tower-sunset-w', 'Sunset on the beach', 'The lit lifeguard tower against a pink and orange sunset'),
]
FILTERS = [('all', 'All'), ('resort', 'The Resort'), ('stays', 'Stays'), ('dining', 'Dining'), ('experiences', 'Experiences'), ('gatherings', 'Gatherings')]
fbtn = '\n'.join(f'          <button type="button" class="chip{" is-active" if k == "all" else ""}" data-gallery-filter="{k}" aria-pressed="{"true" if k == "all" else "false"}">{t}</button>' for k, t in FILTERS)
gitems = []
for cat, jid, cap, alt in G:
    gs = "(min-width: 900px) 30vw, (min-width: 600px) 40vw, 60vw"
    if jid.endswith('-old'):
        base = jid[:-4]; widths, w, h = OLD[base]; src = f'assets/img/{base}-{widths[-1]}.jpg'; img = old(base, alt, gs)
    else:
        src, w, h = full(jid); img = pic(jid, alt, gs)
    tw, th = SIZES[jid][-1] if jid in SIZES else OLD[jid][1:]
    gitems.append(f'          <li data-cat="{cat}" class="g" style="--ar: {tw / th:.4f}"><button type="button" data-full="{src}" data-w="{w}" data-h="{h}" data-caption="{html.escape(cap, quote=True)}" aria-label="Open photo: {html.escape(cap, quote=True)}">{img}</button></li>')
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
    <section class="section section--sandbg6" aria-labelledby="where-title">
      <div class="wrap">
        <div class="feature">
          <figure class="feature__media feature__media--wide" data-reveal>{pic('n-rocky-coast', 'The Century Tree rooted on the edge of a rocky limestone cliff, a sea cave and boulders below and clear turquoise water along the shore', '(min-width: 900px) 56vw, 92vw', '55% 50%')}</figure>
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
              <li>Take a bus from the Superlines or Daet Express terminal in Cubao, Quezon City, signed Aurora, Mulanay or Unisan. The recommended departure is about 11:30 PM, and the trip takes 4 to 6 hours.</li>
              <li>Get off at the General Luna crossing in Quezon and take a tricycle to General Luna Port, about 10 minutes away.</li>
              <li>Cross to Maniwaya Port by public boat. Boats usually leave between 9:00 and 9:30 AM, and the crossing takes about 45 minutes. Confirm the day’s schedule before you travel.</li>
              <li>From Maniwaya Port, Islas Moriones is a 5 to 10 minute walk.</li>
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
            <p>Round trips from Manila to General Luna and back in the resort’s two Foton high-roof vans, each with comfortable seating for 14, with the driver, fuel, tolls and parking included.</p>
            <a class="text-link" href="ask-van.html">Ask about the van <span aria-hidden="true">→</span></a>
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
here = here.replace('VANIMG', pic('e-vans', 'The resort’s two white Foton high-roof vans parked side by side', '(min-width: 900px) 46vw, 92vw', '50% 55%'))
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

# =====================================================================================  TOPIC ENQUIRY PAGES
# Each "Ask about…" button opens a page with the topic's key details and a short form.
# The form writes the guest's answers into a WhatsApp message or an email (no server needed).
def field(kind, name, label, opts=None, req=False, ph=''):
    r = ' required' if req else ''
    fid = 'f-' + name
    if kind == 'select':
        o = ''.join(f'<option value="{html.escape(v)}">{html.escape(v)}</option>' for v in opts)
        ctl = f'<select id="{fid}" name="{name}" data-label="{label}"{r}><option value="">Choose one</option>{o}</select>'
    elif kind == 'textarea':
        ctl = f'<textarea id="{fid}" name="{name}" rows="4" data-label="{label}" placeholder="{ph}"{r}></textarea>'
    else:
        extra = ' min="1" inputmode="numeric"' if kind == 'number' else ''
        ctl = f'<input id="{fid}" name="{name}" type="{kind}" data-label="{label}"{extra}{f" placeholder={chr(34)}{ph}{chr(34)}" if ph else ""}{r}>'
    return f'<div class="ask-field{" ask-field--full" if kind in ("textarea", "select") or name == "name" else ""}"><label for="{fid}">{label}</label>{ctl}</div>'

ASK = [  # file, nav parent, eyebrow, h1, lead, photo, alt, focus, facts, topic phrase, fields
    ('ask-diving.html', 'activities.html', 'Scuba diving', 'Ask about diving',
     'Plan a dive with Seagrass 200 Dive Centre during your stay. Read the essentials, then send the team your dates and experience so they can reply with the options available.',
     'n-dive-shop', 'The glass shopfront of Seagrass 200 Dive Centre under a white pergola, dive gear on the terrace', '50% 60%',
     [('Where', 'Seagrass 200 Dive Centre, a scuba diving dive shop at the resort'), ('Arranging', 'Dives and arrangements are confirmed with the team'), ('Charges', 'Arranged separately from your stay; additional charges apply')],
     'scuba diving with Seagrass 200 Dive Centre',
     [('date', 'dive_date', 'Preferred dive date'), ('number', 'divers', 'Number of divers'), ('select', 'experience', 'Diving experience', ['Certified diver', 'First dive', 'Not sure yet'])]),
    ('ask-jet-skis.html', 'activities.html', 'Jet skis', 'Ask about jet skis',
     'Pick up the pace on the open water off Maniwaya. Send the team your date and group size and they will let you know what is available.',
     'n-beach-sports', 'Jet skis pulled up on the resort beach, the white lifeguard tower and flags along the shore', '50% 50%',
     [('Where', 'On the resort beach'), ('Arranging', 'Ask the team about availability for your dates'), ('Charges', 'Arranged separately from your stay; additional charges apply')],
     'jet skis',
     [('date', 'ride_date', 'Preferred date'), ('number', 'riders', 'Number of riders')]),
    ('ask-banana-boat.html', 'activities.html', 'Banana boat', 'Ask about the banana boat',
     'Gather your group for a splash across the water off Maniwaya. Send the team your date and group size and they will let you know what is available.',
     'n7-banana-c', 'A bright yellow banana boat pulled up on the resort beach, clear kayaks on the sand and a jet ski out on the water', '50% 80%',
     [('Where', 'On the resort beach'), ('Arranging', 'Ask the team about availability for your dates'), ('Charges', 'Arranged separately from your stay; additional charges apply')],
     'the banana boat',
     [('date', 'ride_date', 'Preferred date'), ('number', 'riders', 'Number of riders')]),
    ('ask-dining.html', 'dining.html', 'Dining', 'Ask about meals and dining',
     'From breakfast at the Easter Sunday Café to a boodle fight for your group, tell the team what you have in mind and they will help you plan it.',
     'skylight', 'Skylight Dining: tables beneath a glass-roofed pavilion framed by coconut palms', '45% 55%',
     [('Breakfast', '7:00 – 9:00 AM: Filipino, American and continental'), ('Lunch & dinner', '11:00 AM – 8:00 PM: soups, grilled dishes, seafood and pasta'), ('Packages', 'Meal packages, boodle fight dining (also on the bamboo raft) and bonfire menu packages'), ('Good to know', 'Kitchen use, griller use and paluto can be arranged. Corkage applies to outside food and drinks')],
     'dining',
     [('select', 'about', 'I’m asking about', ['Meals during my stay', 'Skylight Dining', 'Meal packages', 'Boodle fight', 'Bonfire menu package', 'Kitchen, griller or paluto']), ('date', 'dine_date', 'Preferred date'), ('number', 'guests', 'Number of guests')]),
    ('ask-tents.html', 'rooms.html', 'Tent stays', 'Ask about tent stays',
     'Sleep under the palms on the resort’s camping grounds. Share your dates and group size and the team will reply with the setups available.',
     'e-campsite-bamboo', 'Dome tents around bamboo picnic tables on the sunlit campsite beneath coconut palms', '50% 72%',
     [('Tent accommodation', 'A waterproof big tent with mattress, pillows and linens'), ('Tent pitching', 'Bring your own tent and set up on the camping grounds'), ('Facilities', 'Communal toilets and showers, and a charging station'), ('Included', 'Use of the pool, bonfire, volleyball, bamboo raft and badminton')],
     'tent stays',
     [('select', 'stay', 'Type of stay', ['Tent accommodation', 'Bring my own tent (tent pitching)', 'Not sure yet']), ('date', 'check_in', 'Check-in date'), ('number', 'guests', 'Number of guests')]),
    ('ask-gatherings.html', 'groups.html', 'Gatherings & events', 'Plan your gathering',
     'Weddings, celebrations, reunions and company events at The Genesis Events Place. Share your date, guest count and occasion and the team will reply with the options available.',
     'genesis-hall', 'The Genesis Events Place: white fabric draped from a high ceiling over long dining tables, with glass walls to the garden', '50% 60%',
     [('Venue', 'The Genesis Events Place, for 100 to 120 guests'), ('Options', 'Air-conditioned or non-air-conditioned use'), ('Hire', 'Up to 5 hours, with exclusive use of the events area. Extra hours and setup time by arrangement'), ('Weddings', 'The Minimalist, The Romantic and The Luxury packages, each designed for 100 guests'), ('Teams', 'Packages customised around group size, activities, rooms, meals, length of stay and budget')],
     'a gathering at Islas Moriones',
     [('select', 'about', 'Occasion', ['Wedding', 'Birthday or celebration', 'Reunion', 'Company outing or team building', 'Seminar or meeting', 'Something else']), ('date', 'event_date', 'Preferred date'), ('number', 'guests', 'Number of guests'), ('select', 'rooms', 'Overnight rooms needed', ['Yes', 'No', 'Not sure yet'])]),
    ('ask-van.html', 'getting-here.html', 'Van rental', 'Ask about the van',
     'Travel to the port together in the resort’s van. Send your travel date, group size and pick-up point and the team will confirm availability.',
     'e-vans', 'The resort’s two white Foton high-roof vans', '50% 55%',
     [('Route', 'Round trips from Manila to General Luna Port and back'), ('Vans', 'Two Foton high-roof vans, each with comfortable seating for 14'), ('Included', 'Driver, fuel, tolls and parking')],
     'renting the van',
     [('date', 'travel_date', 'Travel date'), ('number', 'passengers', 'Number of passengers'), ('text', 'pickup', 'Pick-up point')]),
]
for fname, parent, eyebrow, h1, lead, img, alt, focus, facts, topic, fields in ASK:
    flds = [field('text', 'name', 'Your name', req=True)] + [field(f[0], f[1], f[2], f[3] if len(f) > 3 else None) for f in fields] \
        + [field('textarea', 'message', 'Your question', ph='Anything else the team should know')]
    spec = ''.join(f'<div><dt>{t}</dt><dd>{d}</dd></div>' for t, d in facts)
    body = intro(eyebrow, h1, lead, back=True) + f'''
    <section class="section section--dune" aria-label="Details and enquiry">
      <div class="wrap ask">
        <div class="ask__info" data-reveal>
          <figure class="feature__media">{pic(img, alt, '(min-width: 900px) 44vw, 92vw', focus, eager=True)}</figure>
          <h2 class="h-section h-section--sm">Good to know</h2>
          <dl class="spec">{spec}</dl>
        </div>
        <div class="contact-card ask__form" data-reveal>
          <p class="eyebrow">Send your question</p>
          <h2 class="h-section h-section--sm">Tell us what you need</h2>
          <p>Fill in what you know, then choose how to send it. Your answers are written into the message for you.</p>
          <form class="ask-form" data-ask data-topic="{topic}" data-wa="{WA}" data-mail="{MAIL}">
            {''.join(flds)}
            <div class="ask-actions">
              <button class="btn btn--teal" type="submit" value="wa">Send on WhatsApp</button>
              <button class="btn btn--line" type="submit" value="mail">Send by email</button>
            </div>
          </form>
          <p class="note">Prefer Facebook? <a href="{FB}" target="_blank" rel="noopener">Message Islas Moriones Beach Resort{NEWTAB}</a>.</p>
        </div>
      </div>
    </section>
'''
    page(fname, parent, f'{h1} | Islas Moriones Beach Resort', lead, body)

# =====================================================================================  GOOD TO KNOW
know = intro('Good to Know', 'Before you arrive', 'Answers to common questions, from location to what is included, plus the resort’s pet policy.', back=True) + f'''
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
