#!/usr/bin/env python3
"""
Generates 5 style variations for Zayd's Custom PCs.

Architecture: ONE markup template + FIVE stylesheets. The brief requires identical
content, copy, and structure across all five, with style as the only variable, so
differentiation lives entirely in CSS. Nothing here invents a price, date, review,
or turnaround; unknowns render as visible TODO chips.
"""
import html, pathlib, re

ROOT = pathlib.Path(__file__).parent
# The generated page and the assets it references live in one directory, so the output
# is self-contained: site/ can be served as-is by any host, with no path rewriting.
ASSETS = ROOT / "site" / "assets"
OUT = ROOT / "variations"

PHONE_DISPLAY = "(949) 878-0884"
# Absolute origin of the deployed site, with the trailing slash. Only social/canonical
# tags need it — every in-page reference stays relative so the local preview works.
# CHANGE THIS ONE LINE when the custom domain goes live; nothing else refers to the host.
SITE_URL = "https://zaydspcs.com/"

# 60 characters, so Google shows the whole thing instead of truncating the location away.
# "Orange County" in full still appears in the description, the hero lead, the footer and
# the structured data, so shortening it here does not drop the term from the page.
SITE_TITLE = "Zayd's Custom PCs — PC Builds, Repairs & Upgrades in OC & LA"
SITE_DESC = ("Custom PC builds, repairs, upgrades and maintenance in Orange County and the "
             "LA area. Every build quoted. Starting at $700.")

PHONE_HREF = "tel:+19498780884"
# The persistent mobile bar opens a message instead of dialling. Every other phone
# link on the page still calls; this is the one that sits under the visitor's thumb.
SMS_HREF = "sms:+19498780884"
IG_DISPLAY = "@zaydspcs"
IG_HREF = "https://instagram.com/zaydspcs"

# Facts Google reads as structured data. Kept here beside the rest of the business truth so
# there is one place to correct them, not a second copy buried in the markup.
#
# HOURS is a single range applied to all seven days: the hours given were "9am-9pm" with no
# weekday qualification. If it is really weekdays only, change OPEN_DAYS to the five and
# rebuild — nothing else needs touching.
OPEN_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
OPEN_FROM, OPEN_TO = "09:00", "21:00"
AREAS_SERVED = ["Orange County, California", "Los Angeles, California"]

# (folder slug, CPU, GPU, pinned image base). Labels carry the CPU/GPU from the folder
# name and nothing more, per the brief. The image is pinned per build rather than picked
# alphabetically — a folder's first filename is not its best photograph, and the
# alphabetical pick had been serving a sideways shot for the 5060 Ti.
BUILDS = [
    ("ryzen-5-7600x-rtx-5070-pc-1",        "Ryzen 5 7600X",      "RTX 5070",    "img-3054"),
    ("ryzen-5-5500-rtx-3050-pc-2",         "Ryzen 5 5500",       "RTX 3050",    "img-2757"),
    ("ryzen-5-3500x-rtx-3060-ti-pc-3",     "Ryzen 5 3500X",      "RTX 3060 Ti", "img-2616"),
    ("intel-core-ultra-5-rtx-5060ti-pc-4", "Intel Core Ultra 5", "RTX 5060 Ti", "img-2588"),
    ("ryzen-3-3200g-pc-5",                 "Ryzen 3 3200G",      None,          "img-2522"),
]

SERVICES = [
    ("Custom PC builds", "Quoted to your requirements and budget. No fixed tiers.", "Starting at $700"),
    ("Repairs",          "Diagnosis, then a quote before any work starts.", "Starting at $45"),
    ("Upgrades",         "Add or swap parts in a machine you already own.", "Starting at $45"),
    ("Maintenance plans","Ongoing cleaning, servicing, and software upkeep.", "Starting at $35/month"),
]

# (name, description, standing note). The note is a real, supplied offer; the date is
# announced as TBD rather than a TODO chip because "not yet scheduled" is a genuine state,
# not missing data. Workshop pricing carries no placeholder — removed at the client's
# direction, so the sections simply do not quote a price.
WORKSHOPS = [
    ("Build Your Own PC",        "Hands-on. You build the machine yourself.", None),
    ("Cybersecurity Awareness",  "Practical security for people who aren't engineers.",
     "Free for nonprofits"),
]

# Structural facts only. Never a named retailer, price, benchmark, or fabricated
# side-by-side; the right column states what is definitionally true of a sealed box.
# The row key carries the claim itself, so the section reads as a list of
# differentiators even before the columns are scanned.
# The hosted form service the quote form POSTs to. None means it is not wired up yet:
# the form still validates and reports, but it renders a visible TODO chip and tells the
# visitor to text instead of pretending a submission went somewhere.
#
# Plan cap: 50 submissions/month. Two consequences worth remembering, because neither is
# visible from the site itself:
#   - Spam burns real slots, which is why the honeypot below is not optional decoration.
#   - Once the cap is hit the POST fails, and the form falls back to "text us" with every
#     answer preserved. Requests going quiet is a quota symptom before it is a bug.
#
# GOING LIVE — this is the only line that changes:
#   Formspree  ->  "https://formspree.io/f/XXXXXXXX"
#   Basin      ->  "https://usebasin.com/f/XXXXXXXXXX"
# The honeypot field name and the TODO chip follow from it automatically.
FORM_ENDPOINT = "https://formspree.io/f/xnpaoovd"


def honeypot_field():
    """Each service watches a differently-named bait field, and a honeypot the service
    does not know about is just an extra field in the inbox. Derived from the endpoint so
    the two can never drift apart."""
    return "_honeypot" if (FORM_ENDPOINT or "").find("usebasin.com") > -1 else "_gotcha"

# Quick-answer options. Budget starts AT the $700 floor rather than "under $1,000",
# so nobody taps a band that cannot be built. "Not sure yet" is deliberate — the
# uncertain buyer is the one this site is written for, and forcing a guess is where
# they leave.
BUDGETS = ["$700–$1,000", "$1,000–$1,500", "$1,500–$2,500", "$2,500+"]
USE_CASES = ["Gaming", "Workstation", "General use", "Not sure yet"]

# The form's first question. Its value decides which middle questions are shown, and
# every other branch stays hidden AND disabled — a hidden-but-enabled field still posts,
# which would put an empty budget on every repair request that lands in the inbox.
SERVICE_PATHS = [
    ("build",       "New build"),
    ("repair",      "Repair"),
    ("upgrade",     "Upgrade"),
    ("maintenance", "Maintenance plan"),
    ("workshop",    "Workshop"),
]
# Sized to the $45 upgrade floor, not to the $700 build floor. Repairs deliberately have
# no budget question: the service card promises diagnosis first, and asking for a number
# before the machine is open anchors a quote neither side can honour.
UPGRADE_BUDGETS = ["Under $150", "$150–$350", "$350–$700", "$700+"]
UPGRADE_TARGETS = ["Graphics", "Storage", "Memory", "Cooling", "Not sure"]
# Register interest, not booking. Dates are TBD, so nothing on this path may imply a seat.
WORKSHOP_PICK = ["Build Your Own PC", "Cybersecurity Awareness"]

VERSUS = [
    ("No proprietary parts", "Standard sizes and connectors.",   "Proprietary sizes"),
    ("No bloatware",         "Nothing you didn’t ask for.",      "Sky’s the limit"),
    ("Custom aesthetics",    "You pick the case and the lighting.", "One size fits all"),
    ("Quality Control",      "Individually inspected and tested.", "Batch tested"),
]


# 1 column at <=640 inside 1.1rem padding, 2 columns at <=980, 3 above, both inside 2rem.
GAL_SIZES = ("(max-width: 640px) calc(100vw - 2.2rem), "
             "(max-width: 980px) calc(50vw - 2rem), "
             "calc(33.33vw - 1.33rem)")


def webp_size(path):
    """(width, height) of a .webp, straight from its header. No dependency, because the
    alternative is hard-coding numbers that go stale the moment an image is replaced."""
    b = path.read_bytes()
    if b[:4] != b"RIFF" or b[8:12] != b"WEBP":
        raise ValueError(f"not a webp: {path}")
    chunk = b[12:16]
    if chunk == b"VP8X":                      # extended: 24-bit canvas size, minus one
        return (int.from_bytes(b[24:27], "little") + 1,
                int.from_bytes(b[27:30], "little") + 1)
    if chunk == b"VP8 ":                      # lossy: 14-bit dimensions after the start code
        return (int.from_bytes(b[26:28], "little") & 0x3FFF,
                int.from_bytes(b[28:30], "little") & 0x3FFF)
    if chunk == b"VP8L":                      # lossless: 14-bit each, packed across 4 bytes
        n = int.from_bytes(b[21:25], "little")
        return ((n & 0x3FFF) + 1, ((n >> 14) & 0x3FFF) + 1)
    raise ValueError(f"unknown webp chunk {chunk!r} in {path}")


def srcset(slug, base):
    """Return (avif, webp, fallback, w, h) for one pinned image base, or None if absent.

    The `w` descriptors are the files' REAL pixel widths, read from the files. The naming
    convention is longest-EDGE, not width: every portrait photograph here is 576-647px wide
    at "-800" and 1152-1294px at "-1600". Declaring 800w/1600w told the browser it had more
    resolution than it did, so it confidently picked the small file for a slot the small
    file could not fill, and every photograph on the site rendered soft."""
    d = ASSETS / slug
    small, large = d / f"{base}-800.webp", d / f"{base}-1600.webp"
    if not (small.exists() and large.exists()):
        return None
    (sw, _), (lw, lh) = webp_size(small), webp_size(large)
    return (
        f"assets/{slug}/{base}-800.avif {sw}w, assets/{slug}/{base}-1600.avif {lw}w",
        f"assets/{slug}/{base}-800.webp {sw}w, assets/{slug}/{base}-1600.webp {lw}w",
        f"assets/{slug}/{base}-1600.webp", lw, lh,
    )


def picture(slug, base, alt, sizes, cls="", eager=False):
    s = srcset(slug, base)
    if not s:
        return f'<div class="ph {cls}" role="img" aria-label="{alt}"></div>'
    avif, webp, fallback, w, h = s
    # The hero image is the LCP element; lazy-loading it would delay the largest paint.
    load = 'loading="eager" fetchpriority="high"' if eager else 'loading="lazy"'
    # width/height reserve the box before any CSS arrives, so the page cannot jolt as
    # photographs land. --ar carries the true ratio to the stylesheet instead of the
    # stylesheet hard-coding one image's proportions and silently cropping the next one.
    return (f'<picture class="{cls}" style="--ar:{w}/{h}">'
            f'<source type="image/avif" srcset="{avif}" sizes="{sizes}">'
            f'<source type="image/webp" srcset="{webp}" sizes="{sizes}">'
            f'<img src="{fallback}" alt="{alt}" width="{w}" height="{h}" {load} decoding="async">'
            f'</picture>')


def todo(label):
    return f'<span class="todo">TODO: {label}</span>'


def chips(qid, name, options, err_id, msg, kind="radio"):
    """A choice group rendered as tap targets. Real inputs, hidden and styled through their
    labels — so keyboard navigation, grouping and the checked state come from the browser
    rather than from script. `required` on the first radio makes the whole group required
    natively; checkbox groups carry data-min instead and are checked in script, because
    HTML has no native "at least one of these"."""
    out = []
    for i, opt in enumerate(options):
        cid = f"{qid}-{i}"
        extra = ""
        if i == 0:
            extra = f' data-err="{err_id}" data-msg="{html.escape(msg, quote=True)}"'
            extra += ' data-min="1"' if kind == "checkbox" else ' required'
        nm = f"{name}[]" if kind == "checkbox" else name
        out.append(
            f'<input class="qf-pick" type="{kind}" id="{cid}" name="{nm}" '
            f'value="{html.escape(opt, quote=True)}"{extra}>'
            f'<label class="qf-chip" for="{cid}">{html.escape(opt)}</label>')
    return "".join(out)


def question(body, path=None):
    """One numbered line of the ticket. `path` ties it to a service branch; questions with
    no path (the service picker, name, contact) are always on.

    Branch controls ship DISABLED, not merely hidden, and script enables the chosen path.
    Two reasons, both load-bearing: a hidden-but-enabled field still posts, so every repair
    would arrive carrying an empty budget; and `required` on a field the visitor cannot
    reach makes the browser refuse to submit at all, which would break the form outright
    for anyone without JavaScript."""
    if not path:
        return '        <li class="qf-q">\n' + body + '\n        </li>'
    body = re.sub(r'<(input|textarea)\b', r'<\1 disabled', body)
    return ('        <li class="qf-q" data-for="' + path + '" hidden>\n'
            + body + '\n        </li>')


def legend(text, tag="legend", extra=""):
    # The 01/02/03 marker is a CSS counter, not a literal: hidden branches generate no box
    # and so do not increment it, which is what keeps a repair numbered 01-04 with no gaps.
    return (f'          <{tag} class="qf-legend"{extra}>'
            f'<span class="qf-n" aria-hidden="true"></span>{text}</{tag}>')


def service_main(sp, prefix):
    """One service page's <main>: the homepage's service card, unfolded.

    The four blocks answer the four questions this visitor arrives with, in the order they
    arrive — what is this, what do I get, what does it cost, what happens next. Someone who
    searched "pc repair orange county" is not undecided about what they need, so nothing
    here re-pitches the business; it answers.

    Prose strings carry deliberate <b>/<em> and are authored constants in this file, so they
    are interpolated raw. Anything derived from a name or a slug is escaped."""
    # "Starting at $700" -> ("Starting at", "$700"). Splitting on the last space keeps
    # "$35/month" whole, which a split on "$" would not.
    lab, num = sp["price"].rsplit(" ", 1)

    intro = "\n".join(f'      <p>{t}</p>' for t in sp["intro"])
    incl  = "\n".join(f'        <li>{t}</li>' for t in sp["incl"])
    cost  = "\n".join(f'      <p>{t}</p>' for t in sp["price_body"])
    note  = "\n".join(f'      <p>{t}</p>' for t in sp["aside"])
    steps = "\n".join(
        f'''        <li class="step">
          <h3>{html.escape(h)}</h3>
          <p>{html.escape(d)}</p>
        </li>''' for h, d in sp["steps"])
    # Every service page links to the other three. Four pages that only link upward are four
    # dead ends; this is also the cheapest internal linking a four-page site can have.
    others = "\n".join(
        f'      <a class="more-go" href="{prefix}{o["slug"]}/">{html.escape(o["h1"])}</a>'
        for o in SERVICE_PAGES if o["slug"] != sp["slug"])

    return f'''
  <section class="sp-hero" id="top">
    <nav class="crumb" aria-label="Breadcrumb">
      <a href="{prefix}">Zayd’s Custom PCs</a>
      <span class="crumb-sep" aria-hidden="true">/</span>
      <span aria-current="page">{html.escape(sp["h1"])}</span>
    </nav>
    <h1>{html.escape(sp["h1"])}</h1>
    <p class="lead">{sp["lead"]}</p>
    <p class="price"><span class="price-lab">{lab}</span> <b>{num}</b></p>
    <div class="hero-act">
      <a class="cta cta-lg" href="#quote">Start your quote</a>
      <a class="tel-lg" href="{PHONE_HREF}">{PHONE_DISPLAY}</a>
    </div>
  </section>

  <section class="sp-what">
    <div class="prose">
{intro}
    </div>
    <h2>{html.escape(sp["incl_head"])}</h2>
    <ul class="sp-list">
{incl}
    </ul>
  </section>

  <section class="sp-cost">
    <h2>What it costs</h2>
    <div class="prose">
{cost}
    </div>
  </section>

  <!-- The one thing this service's visitor is most likely to be wrong about, answered
       before they ask. It is the section that costs us jobs — repair-or-replace talks
       people out of repairs — which is exactly why it earns its place. -->
  <section class="sp-note">
    <h2>{html.escape(sp["aside_h"])}</h2>
    <div class="prose">
{note}
    </div>
  </section>

  <section class="sp-next">
    <h2>What happens next</h2>
    <ol class="steps">
{steps}
    </ol>
    <a class="inline-cta" href="#quote">Start your quote</a>
  </section>

  <section class="sp-more">
    <h2>Other services</h2>
    <div class="more-grid">
{others}
    </div>
  </section>
'''


def faq_section():
    """Placed immediately before the form, because objections are answered last — these are
    the questions a visitor is still holding when they reach the ask.

    A plain ruled list, not accordions. Six answers worth reading are worth showing, and a
    <details> the visitor has to open is one more thing standing between them and the only
    conversion on the site. It also means Google reads the answers as ordinary body copy,
    which is the mechanism that actually still works — FAQ rich results were restricted to
    government and health sites in 2023, so no FAQPage schema is emitted."""
    items = "\n".join(
        f'''      <div class="faq-item">
        <h3>{html.escape(q)}</h3>
        <p>{html.escape(a)}</p>
      </div>''' for q, a in FAQ)
    return f'''
  <section class="faq" id="faq">
    <h2>Common questions</h2>
    <div class="faq-grid">
{items}
    </div>
  </section>
'''


def build_body(page=None, prefix=""):
    """The homepage when `page` is None, otherwise the service page that `page` describes.

    One function rather than two because the shell, the quote form and every helper below
    are shared outright. Duplicating the form for four service pages would have meant four
    copies of the branch logic drifting apart on the first change to it."""
    hero_slug, hero_cpu, hero_gpu, hero_base = BUILDS[0]
    # Every breakpoint here is a real one from themes.py, and the widths are the real
    # column maths. The old "(max-width:860px) 100vw, 52vw" named a breakpoint the sheet
    # does not have, so between 861 and 980px the browser sized for a half-width column
    # while the hero was actually running full bleed.
    hero_img = picture(hero_slug, hero_base, f"Completed build: {hero_cpu}, {hero_gpu}",
                       "(max-width: 640px) 100vw, "
                       "(max-width: 980px) calc(100vw - 4rem), "
                       "calc(40vw - 1.6rem)", "hero-media", eager=True)

    def svc_card(n, d, p):
        slug = SERVICE_SLUGS.get(n)
        head = (f'<h3><a class="svc-go" href="{slug}/">{html.escape(n)}</a></h3>'
                if slug else f'<h3>{html.escape(n)}</h3>')
        return f'''      <li class="svc">
        {head}
        <p>{d}</p>
        <p class="svc-meta">{p if p else todo("pricing")}</p>
      </li>'''

    svc = "\n".join(svc_card(n, d, p) for n, d, p in SERVICES)

    wsh = "\n".join(
        f'''      <li class="wsh">
        <h3>{html.escape(n)}</h3>
        <p>{html.escape(d)}</p>
        <p class="wsh-meta"><span class="wsh-date">Next date: TBD</span>'''
        + (f'<span class="wsh-note">{html.escape(note)}</span>' if note else '')
        + f'<a class="wsh-go" href="#quote" data-workshop="{html.escape(n, quote=True)}">'
          'Tell us you’re interested</a>'
        + '''</p>
      </li>''' for n, d, note in WORKSHOPS)

    vs = "\n".join(
        f'''        <div class="vs-row">
          <span class="vs-k">{k}</span>
          <span class="vs-a">{a}</span>
          <span class="vs-b">{b}</span>
        </div>''' for k, a, b in VERSUS)

    gal = "\n".join(
        f'''      <figure class="shot">
        {picture(s, base, f"Completed build: {cpu}" + (f", {gpu}" if gpu else ""), GAL_SIZES)}
        <figcaption><span class="cpu">{cpu}</span>{f'<span class="gpu">{gpu}</span>' if gpu else ''}</figcaption>
      </figure>''' for s, cpu, gpu, base in BUILDS)

    svc_chips  = chips("svc", "service", [n for _, n in SERVICE_PATHS], "err-service", "Pick one")
    budget_chips = chips("bud", "budget", BUDGETS, "err-budget", "Pick a range")
    use_chips  = chips("use", "use_case", USE_CASES, "err-use", "Pick one")
    upg_chips  = chips("upg", "upgrade_targets", UPGRADE_TARGETS, "err-upg",
                       "Pick at least one", kind="checkbox")
    ubud_chips = chips("ubud", "upgrade_budget", UPGRADE_BUDGETS, "err-ubud", "Pick a range")
    wsh_chips  = chips("wsp", "workshop", WORKSHOP_PICK, "err-wsp", "Pick one")
    def gq(text, chips_html, err_id, path=None):
        """A choice question: fieldset, legend, pills, error slot."""
        return question(
            '          <fieldset class="qf-set">\n'
            + legend(text) + '\n'
            + f'            <div class="qf-chips">{chips_html}</div>\n'
            + '          </fieldset>\n'
            + f'          <p class="qf-err" id="{err_id}" hidden></p>', path)

    def tq(text, fid, name, placeholder, path=None, err_id=None, msg=None, optional=False):
        """A written question. Optional ones carry no error slot at all."""
        lab = text + ('<span class="qf-opt">Optional</span>' if optional else '')
        req = f' required data-err="{err_id}" data-msg="{html.escape(msg, quote=True)}"' if err_id else ''
        body = (legend(lab, tag="label", extra=f' for="{fid}"') + '\n'
                + f'          <textarea class="qf-in" id="{fid}" name="{name}" rows="3"'
                + f' placeholder="{html.escape(placeholder, quote=True)}"{req}></textarea>')
        if err_id:
            body += f'\n          <p class="qf-err" id="{err_id}" hidden></p>'
        return question(body, path)

    q_service = gq("What do you need?", svc_chips, "err-service")

    q_budget = gq("What\u2019s your budget?", budget_chips, "err-budget", "build")
    q_use    = gq("What\u2019s it for?", use_chips, "err-use", "build")
    q_parts  = tq("Any parts you already want?", "qf-parts", "parts",
                  "A GPU you have in mind, a case you like, a drive you want reused\u2026",
                  "build", optional=True)

    q_problem = tq("What\u2019s wrong?", "qf-problem", "problem",
                   "Won\u2019t turn on, blue screens when gaming, fans are loud\u2026",
                   "repair", err_id="err-problem", msg="Tell us what\u2019s wrong")

    q_upg  = gq("What do you want to upgrade?", upg_chips, "err-upg", "upgrade")
    q_ubud = gq("What\u2019s your budget?", ubud_chips, "err-ubud", "upgrade")

    q_maint = tq("Anything we should know?", "qf-notes", "notes",
                 "How many machines, what they\u2019re used for, where they live\u2026",
                 "maintenance", optional=True)

    q_wsp = gq("Which workshop?", wsh_chips, "err-wsp", "workshop")

    q_name = question(
        legend("Your name", tag="label", extra=' for="qf-name"') + '\n'
        '          <input class="qf-in" id="qf-name" name="name" type="text" autocomplete="name"\n'
        '            required data-err="err-name" data-msg="Name required">\n'
        '          <p class="qf-err" id="err-name" hidden></p>')

    q_contact = question(
        legend("How do we reach you?", tag="p") + '\n'
        '          <div class="qf-pair">\n'
        '            <span class="qf-field">\n'
        '              <label class="qf-sub" for="qf-phone">Phone</label>\n'
        '              <input class="qf-in" id="qf-phone" name="phone" type="tel" inputmode="tel"\n'
        '                autocomplete="tel" required data-err="err-phone" data-msg="10 digits needed">\n'
        '              <p class="qf-err" id="err-phone" hidden></p>\n'
        '            </span>\n'
        '            <span class="qf-field">\n'
        '              <label class="qf-sub" for="qf-email">Email<span class="qf-opt">Optional</span></label>\n'
        '              <input class="qf-in" id="qf-email" name="email" type="email"\n'
        '                autocomplete="email" data-err="err-email" data-msg="Check it, or leave blank">\n'
        '              <p class="qf-err" id="err-email" hidden></p>\n'
        '            </span>\n'
        '          </div>')

    endpoint_attr = (f' action="{FORM_ENDPOINT}" data-endpoint="{FORM_ENDPOINT}"'
                     if FORM_ENDPOINT else '')
    endpoint_todo = '' if FORM_ENDPOINT else (
        '<p class="qf-todo">' + todo("form endpoint")
        + ' Create a Formspree or Basin form, paste its URL into FORM_ENDPOINT in build.py.'
        + ' Until then this button reports honestly instead of pretending.</p>')

    # --- the shell -------------------------------------------------------------
    # Nav, persistent mobile bar, quote form and footer are identical on all five pages,
    # because they are one site and the form is the only conversion on it. What differs is
    # where the links point: a service page's nav goes home, the homepage's goes to its own
    # sections. `prefix` is the path back to site/ from this page's directory, so every
    # asset reference stays relative and the build still opens straight from the filesystem
    # — root-relative "/assets/" would have needed a server to preview.
    home_href = "#top" if page is None else prefix
    sec = "" if page is None else prefix

    # A visitor who searched "pc repair" and landed on /repairs/ has already answered
    # question 01. The form reads this and checks that radio on load, so they arrive at
    # "what's wrong?" instead of being asked something they have already told us. The
    # question stays visible and changeable: anyone who guessed wrong must be able to say so.
    preselect = f' data-preselect="{html.escape(page["chip"], quote=True)}"' if page else ""

    shell_top = f'''
<a class="skip" href="#main">Skip to content</a>

<header class="nav">
  <a class="brand" href="{home_href}" aria-label="Zayd's Custom PCs — home">
    <img src="{prefix}assets/logo/logo-square.svg" alt="" width="44" height="44">
    <span class="brand-txt"><b>Zayd’s</b> Custom PCs</span>
  </a>
  <nav class="nav-links" aria-label="Sections">
    <a href="{sec}#services">Services</a>
    <a href="{sec}#versus">Why choose us</a>
    <a href="{sec}#gallery">Builds</a>
  </nav>
  <div class="nav-act">
    <a class="tel" href="{PHONE_HREF}">{PHONE_DISPLAY}</a>
    <a class="ig" href="{IG_HREF}">{IG_DISPLAY}</a>
    <a class="cta" href="#quote">Start your quote</a>
  </div>
</header>

<!-- Directly after the header, not at the end of the document. It is position:fixed, so
     its visual placement is unaffected, but a keyboard user reaches the persistent
     contact actions early instead of at tab stop 16 of 18, after the footer. -->
<div class="mobile-bar">
  <a href="{SMS_HREF}">Text {PHONE_DISPLAY}</a>
  <a href="{IG_HREF}">{IG_DISPLAY}</a>
  <a class="mb-cta" href="#quote">Quote</a>
</div>

<main id="main">
'''
    quote = f'''  <!-- The job ticket. One form, one destination, five paths. Question 01 decides which
       middle questions exist; a repair answers four, a build answers six, and nobody ever
       reads a question meant for somebody else. Numbering is a CSS counter over the
       questions that actually render, so a repair runs 01-04 with no gaps.
       Nothing here is a select element — a native picker on mobile is two taps and a modal
       for what a chip does in one. -->
  <section class="quote" id="quote">
    <h2>Tell us what you need</h2>
    <!-- The count is exact once a path is chosen; before that it honestly does not
         know, because it depends on the answer to 01. -->
    <p class="q-lead"><span id="qf-count">A few</span> questions. We quote from there.</p>

    <form class="qf" id="qform" method="post"{endpoint_attr}{preselect}>
      <ol class="qf-list">

{q_service}

{q_budget}
{q_use}
{q_parts}

{q_problem}

{q_upg}
{q_ubud}

{q_maint}

{q_wsp}

{q_name}
{q_contact}

      </ol>

      <!-- Honeypot, not a captcha. Bots fill every field they find; people never see this
           one. A captcha would put a puzzle between a paying customer and the only
           conversion on the site. -->
      <div class="qf-hp" aria-hidden="true">
        <label for="qf-company">Company</label>
        <input id="qf-company" name="{honeypot_field()}" type="text" tabindex="-1" autocomplete="off">
      </div>

      <!-- Both Formspree and Basin use _subject as the email subject line. Without it every
           request arrives titled the same thing, and an inbox of identical subjects is an
           inbox you stop reading. Script fills it from the service and the name. -->
      <input type="hidden" name="_subject" id="qf-subject" value="New quote request">

{endpoint_todo}
      <p class="qf-note" id="qf-note" role="alert" hidden></p>
      <button class="qf-submit" id="qf-submit" type="submit">Send my request</button>
    </form>

    <!-- Not a thank-you panel: a receipt. The business's whole claim is that you are told
         exactly what went in and handed the paperwork, so the moment a stranger commits
         their phone number, the ticket they just filled in prints back at them — itemised,
         timestamped, and printable on actual paper. It answers the one fear this visitor
         arrives with: that the request vanished into a void. -->
    <div class="qf-done" id="qf-done" role="status" tabindex="-1" hidden>
      <p class="rc-head">Zayd’s Custom PCs · Orange County &amp; LA</p>
      <h3>Request received</h3>
      <dl class="rc-list" id="qf-receipt"></dl>
      <p class="rc-msg" id="qf-done-msg"></p>
      <p class="rc-foot">
        <span class="rc-stamp" id="qf-stamp"></span>
        <button type="button" class="rc-print" id="qf-print">Print this</button>
      </p>
    </div>

    <p class="q-or">Or skip the form</p>
    <div class="q-act">
      <a class="cta cta-lg" href="{PHONE_HREF}">{PHONE_DISPLAY}</a>
      <a class="ig-lg" href="{IG_HREF}">{IG_DISPLAY}</a>
    </div>
  </section>
'''
    shell_bot = f'''</main>

<footer class="foot">
  <img src="{prefix}assets/logo/logo-16x9.svg" alt="Zayd's Custom PCs" class="foot-logo"
    width="1440" height="810" loading="lazy" decoding="async">
  <p class="foot-meta">Orange County &amp; Los Angeles, California · {PHONE_DISPLAY} · {IG_DISPLAY}</p>
</footer>
'''

    if page is not None:
        return shell_top + service_main(page, prefix) + quote + shell_bot

    return shell_top + f'''  <section class="hero" id="top">
    <div class="hero-txt">
      <h1>Don’t get a computer,<br>get <em>the</em> computer</h1>
      <p class="lead">Custom PC builds, repairs, upgrades, and maintenance in Orange County,
        LA, and surrounding areas.</p>
      <p class="price"><span class="price-lab">Custom builds start at</span> <b>$700</b></p>
      <div class="hero-act">
        <a class="cta cta-lg" href="#quote">Start your quote</a>
        <a class="tel-lg" href="{PHONE_HREF}">{PHONE_DISPLAY}</a>
      </div>
    </div>
    {hero_img}
  </section>

  <section class="services" id="services">
    <h2>What we do</h2>
    <ul class="svc-grid">
{svc}
    </ul>
    <h2 class="wsh-h">Workshops</h2>
    <ul class="wsh-grid">
{wsh}
    </ul>
    <a class="inline-cta" href="#quote">Start your quote</a>
  </section>

  <section class="versus" id="versus">
    <h2>What sets us apart</h2>
    <div class="vs-table">
      <div class="vs-head">
        <span class="vs-a">Us</span>
        <span class="vs-b">A boxed prebuilt</span>
      </div>
{vs}
    </div>
    <a class="inline-cta" href="#quote">Start your quote</a>
  </section>

  <section class="gallery" id="gallery">
    <h2>Our previous systems</h2>
    <div class="gal-grid">
{gal}
    </div>
    <a class="inline-cta" href="#quote">Start your quote</a>
  </section>

''' + faq_section() + quote + shell_bot



# ---------------------------------------------------------------------------
# Service pages
# ---------------------------------------------------------------------------
# One entry per page. Every line here is a fact already on the homepage or a direct
# consequence of one — nothing introduces a claim the client did not supply. The two
# figures that were open are now closed: diagnosis is free and $45 is the floor for a
# COMPLETED repair (client, 2026-09-01), and assembly takes days while the wait is parts
# shipping (client, 2026-09-01).
#
# `path` is the quote form's branch key, and `chip` is the exact radio value the form
# renders. Both are asserted against SERVICE_PATHS at import, so a page can never
# pre-answer question 01 with a value the form does not offer.
#
# Word counts are what the answers took. They were not padded to a target: a page that
# runs short because the service is simple is a better page than one inflated to a number.
SERVICE_PAGES = [
    dict(
        slug="custom-builds", path="build", chip="New build",
        title="Custom PC Builds in OC & LA — Zayd's Custom PCs",
        desc=("Custom gaming and workstation PCs built to order in Orange County and LA. "
              "Every part quoted before you commit. Starting at $700."),
        h1="Custom PC builds",
        lead=("A machine specified for what you actually do with it, quoted part by part "
              "before anything is ordered."),
        intro=[
            "There is no parts list on this page, because there isn’t one. Every build "
            "starts from what the machine is for and what you want to spend, and the parts "
            "are chosen after that conversation rather than before it.",
            "That is the whole difference between this and a box on a shelf, where the "
            "parts were picked to hit a price point by someone who has never met you — and "
            "where the sticker tells you the graphics card and stays quiet about the power "
            "supply, the drive, and the motherboard.",
        ],
        incl_head="What a build includes",
        incl=[
            "A written quote naming every part, before you commit to anything",
            "Assembly, cable routing, and BIOS setup",
            "Windows installed, updated, and free of the trial software prebuilts ship with",
            "Stress testing under load before it leaves — memory, processor, and graphics",
            "The receipt, listing every part by make and model",
        ],
        price="Starting at $700",
        price_body=[
            "$700 is a floor, not a package. It is the point below which a machine worth "
            "putting our name on stops being possible. Most builds land between $700 and "
            "$1,500.",
            "<b>What moves the number:</b> the graphics card, almost always. After that, how "
            "much storage you want and whether the machine needs to stay quiet under load.",
        ],
        aside_h="How long it takes",
        aside=[
            "Assembly takes a couple of days. The wait is parts shipping, not us — it "
            "depends on what is on the list and where it is coming from.",
            "You get an expected date when you approve the quote, and you hear from us if "
            "it moves.",
        ],
        steps=[
            ("Tell us what it’s for", "What you’ll run on it, and what you want to spend."),
            ("We come back with a parts list and a price",
             "Ask about any line on it. Every part is there to be questioned."),
            ("You approve, we order", "Nothing is bought before you say yes."),
            ("We build and test it", "Assembled, updated, and run under load."),
            ("You get the machine and the receipt",
             "Every part listed, so you know exactly what you own."),
        ],
    ),
    dict(
        slug="repairs", path="repair", chip="Repair",
        title="PC Repair in OC & LA — Free Diagnosis | Zayd's Custom PCs",
        desc=("PC and computer repair across Orange County and LA. Diagnosis is free, you "
              "get a quote before any work starts, and repairs start at $45."),
        h1="PC repairs",
        lead=("Diagnosis is free. You get a quote before any work starts, and nothing "
              "happens until you say yes."),
        intro=[
            "What people are actually afraid of with repairs is the open-ended bill — you "
            "hand over a machine, and the number arrives after the work is already done.",
            "That is not how this works. We find out what is wrong, we tell you what it "
            "costs to fix, and you decide. If you decide not to go ahead, you owe nothing.",
        ],
        incl_head="What a repair includes",
        incl=[
            "Free diagnosis — the fault is found before you are asked to commit any money",
            "A written quote naming the fault, the parts, and the labour",
            "No work starts without your approval",
            "An honest answer about whether the machine is worth fixing at all",
            "Testing under load afterwards, so a fix that only half-held gets caught here",
        ],
        price="Starting at $45",
        price_body=[
            "$45 is the floor for a <em>completed</em> repair, not a fee to look at it. "
            "Diagnosis costs nothing whether or not you go ahead.",
            "<b>What moves the number:</b> whether it needs a part. Faults that are labour "
            "only — a reinstall, a reseat, a thermal repaste — sit near the floor.",
        ],
        aside_h="Repair or replace?",
        aside=[
            "Sometimes the honest answer is that it isn’t worth it. A machine old enough "
            "that a failed board costs more than the machine is worth is not a repair we "
            "will talk you into.",
            "When that happens we say so, and the diagnosis was still free. We would rather "
            "lose the job than sell you a repair that doesn’t make sense.",
        ],
        steps=[
            ("Tell us what it’s doing", "Won’t turn on, blue screens, loud, slow, hot."),
            ("We diagnose it", "No charge, whatever we find."),
            ("You get a quote", "Naming the fault and what fixing it costs."),
            ("You approve or you don’t", "No pressure either way, and no bill if you don’t."),
            ("Fixed, tested, returned", "With the receipt for anything replaced."),
        ],
    ),
    dict(
        slug="upgrades", path="upgrade", chip="Upgrade",
        title="PC Upgrades in OC & LA — GPU, RAM, SSD | Zayd's Custom PCs",
        desc=("Graphics, memory, storage and cooling upgrades for the PC you already own. "
              "Orange County and LA. Work starts at $45, parts quoted separately."),
        h1="PC upgrades",
        lead=("Add or swap parts in a machine you already own — usually cheaper than "
              "replacing it, and often the right call."),
        intro=[
            "Most machines that feel slow do not need replacing. They need one part: a "
            "drive that is full, memory that is short, or a graphics card three generations "
            "behind the games being asked of it.",
            "Working out which one is the useful part of this. Replacing the oldest part is "
            "not the same as replacing the part that is actually holding the machine back, "
            "and the difference is usually a few hundred dollars.",
        ],
        incl_head="What an upgrade includes",
        incl=[
            "Finding the part that is actually the bottleneck, not just the oldest one",
            "Checking it fits — power supply headroom, physical clearance, socket and generation",
            "Installation, and the machine tested under load afterwards",
            "Your old part back, if you want it",
        ],
        price="Starting at $45",
        price_body=[
            "$45 is the floor for the work. Parts are quoted separately, and you see what "
            "they cost.",
            "<b>What moves the number:</b> the part. Fitting a drive is quick. A graphics "
            "card that also needs a bigger power supply is two parts and more work.",
        ],
        aside_h="Why some machines can’t be upgraded",
        aside=[
            "This is where a boxed prebuilt often cannot be helped. Big-box machines use "
            "proprietary motherboards, power supplies, and cases in non-standard sizes, so "
            "the part you want does not physically fit — and the only upgrade left is a "
            "whole new computer.",
            "Everything we build uses standard sizes and connectors. That is not a feature "
            "you notice on day one; it is the reason the machine is still worth upgrading "
            "in three years.",
        ],
        steps=[
            ("Tell us the machine and what’s frustrating you",
             "Slow, out of space, won’t run something, too loud."),
            ("We work out which part is the limit", "And check the upgrade actually fits."),
            ("You get a quote", "Work and parts, separately, so you can see both."),
            ("Fitted and tested", "Run under load before it goes back."),
        ],
    ),
    dict(
        slug="maintenance-plans", path="maintenance", chip="Maintenance plan",
        title="PC Maintenance Plans in OC & LA — Zayd's Custom PCs",
        desc=("Ongoing PC cleaning, servicing and software upkeep for homes and small "
              "offices in Orange County and LA. Plans start at $35 a month."),
        h1="Maintenance plans",
        lead=("Ongoing cleaning, servicing, and software upkeep, so a machine keeps running "
              "the way it did the week you got it."),
        intro=[
            "Computers fail suddenly less often than people think. They get slower, hotter, "
            "and dustier for a year, and then something gives — and the thing that gives is "
            "usually the part that was running hot the whole time.",
            "A maintenance plan is the cheap version of that problem: regular attention "
            "instead of one expensive failure and a week without the machine.",
        ],
        incl_head="What a plan covers",
        incl=[
            "Physical cleaning — dust out of the fans, filters, and heatsinks",
            "Thermal check under load, so throttling is caught before it becomes noticeable",
            "Drive health checks and free-space management",
            "Operating system and driver updates, done properly rather than deferred again",
            "A security check: confirming the machine’s protection is on and current",
        ],
        price="Starting at $35/month",
        price_body=[
            "$35 a month is per machine, and a floor rather than a fixed rate.",
            "<b>What moves the number:</b> how many machines, and where they are.",
        ],
        aside_h="Who this is actually for",
        aside=[
            "Households running several machines, and small offices with nobody whose job "
            "this is.",
            "If you have one PC and you are comfortable keeping it clean and updated "
            "yourself, you probably do not need this — and we would rather tell you that "
            "than sell you a plan you would not use.",
        ],
        steps=[
            ("Tell us what you’re running", "How many machines, and what they’re used for."),
            ("We quote the plan", "Based on the count and the visit, not a package tier."),
            ("Scheduled servicing", "Regular, so problems surface while they’re still small."),
            ("You hear from us when something needs attention",
             "Before it becomes the reason the machine is down."),
        ],
    ),
]

# A page whose chip is not a real form option would silently pre-answer question 01 with a
# value no radio carries, leaving the visitor on a form that looks broken. Cheaper to fail
# the build.
_CHIPS = {label for _, label in SERVICE_PATHS}
_KEYS = {key for key, _ in SERVICE_PATHS}
for _sp in SERVICE_PAGES:
    assert _sp["chip"] in _CHIPS, f'{_sp["slug"]}: chip {_sp["chip"]!r} is not in SERVICE_PATHS'
    assert _sp["path"] in _KEYS, f'{_sp["slug"]}: path {_sp["path"]!r} is not in SERVICE_PATHS'

# The service card on the homepage and the page it opens are the same service, so the link
# is derived rather than repeated. A card with no page keeps its old inert markup.
SERVICE_SLUGS = {
    "Custom PC builds": "custom-builds",
    "Repairs": "repairs",
    "Upgrades": "upgrades",
    "Maintenance plans": "maintenance-plans",
}

# ---------------------------------------------------------------------------
# FAQ
# ---------------------------------------------------------------------------
# Written to answer what people actually type into Google, in the same voice as the rest of
# the page. No FAQPage schema is emitted: Google restricted those rich results to
# government and health sites in 2023, so the markup would render nothing. This section
# earns its place as text Google can read and quote, which is the mechanism that still works.
FAQ = [
    ("How much does a custom PC cost?",
     "Builds start at $700, and most land between $700 and $1,500. There are no fixed "
     "tiers — the price follows the parts, and you see the parts list before you commit. "
     "The graphics card moves the number more than anything else."),
    ("Is it cheaper to repair a PC or replace it?",
     "Usually repair, but not always, and we will tell you which. Diagnosis is free, so "
     "finding out costs you nothing. If a machine is old enough that the repair costs more "
     "than the machine is worth, we say so rather than take the job."),
    ("How long does a custom build take?",
     "Assembly takes a couple of days. The real wait is parts shipping, which depends on "
     "what is on the list and where it is coming from. You get an expected date when you "
     "approve the quote, and you hear from us if it moves."),
    ("Will I know exactly what parts are in my PC?",
     "Yes, and you get the receipt. Every part is listed by make and model, before you buy "
     "and again afterwards. This is the part boxed prebuilts do not do, and it is the "
     "reason you can upgrade the machine later instead of replacing it."),
    ("Do you charge to look at a broken computer?",
     "No. Diagnosis is free whether or not you go ahead with the repair. Completed repairs "
     "start at $45, and you get a quote naming the fault and the fix before any work begins."),
    ("Where do you work?",
     "Orange County, Los Angeles, and the surrounding areas. Call or text "
     f"{PHONE_DISPLAY}, or send a request through the form below."),
]
