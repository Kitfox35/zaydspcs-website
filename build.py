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

SITE_TITLE = "Zayd's Custom PCs — Custom PC Builds, Repairs and Upgrades in Orange County"
SITE_DESC = ("Custom PC builds, repairs, upgrades and maintenance in Orange County. "
             "Every build quoted. Starting at $700.")

PHONE_HREF = "tel:+19498780884"
# The persistent mobile bar opens a message instead of dialling. Every other phone
# link on the page still calls; this is the one that sits under the visitor's thumb.
SMS_HREF = "sms:+19498780884"
IG_DISPLAY = "@zaydspcs"
IG_HREF = "https://instagram.com/zaydspcs"

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


def build_body():
    hero_slug, hero_cpu, hero_gpu, hero_base = BUILDS[0]
    # Every breakpoint here is a real one from themes.py, and the widths are the real
    # column maths. The old "(max-width:860px) 100vw, 52vw" named a breakpoint the sheet
    # does not have, so between 861 and 980px the browser sized for a half-width column
    # while the hero was actually running full bleed.
    hero_img = picture(hero_slug, hero_base, f"Completed build: {hero_cpu}, {hero_gpu}",
                       "(max-width: 640px) 100vw, "
                       "(max-width: 980px) calc(100vw - 4rem), "
                       "calc(40vw - 1.6rem)", "hero-media", eager=True)

    svc = "\n".join(
        f'''      <li class="svc">
        <h3>{html.escape(n)}</h3>
        <p>{d}</p>
        <p class="svc-meta">{p if p else todo("pricing")}</p>
      </li>''' for n, d, p in SERVICES)

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

    return f'''
<a class="skip" href="#main">Skip to content</a>

<header class="nav">
  <a class="brand" href="#top" aria-label="Zayd's Custom PCs — home">
    <img src="assets/logo/logo-square.svg" alt="" width="44" height="44">
    <span class="brand-txt"><b>Zayd’s</b> Custom PCs</span>
  </a>
  <nav class="nav-links" aria-label="Sections">
    <a href="#services">Services</a>
    <a href="#versus">Why choose us</a>
    <a href="#gallery">Builds</a>
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
  <section class="hero" id="top">
    <div class="hero-txt">
      <h1>Don’t get a computer,<br>get <em>the</em> computer</h1>
      <p class="lead">Custom PC builds, repairs, upgrades, and maintenance in Orange County
        and surrounding areas.</p>
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

  <!-- The job ticket. One form, one destination, five paths. Question 01 decides which
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

    <form class="qf" id="qform" method="post"{endpoint_attr}>
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
      <p class="rc-head">Zayd’s Custom PCs · Orange County</p>
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
</main>

<footer class="foot">
  <img src="assets/logo/logo-16x9.svg" alt="Zayd's Custom PCs" class="foot-logo"
    width="1440" height="810" loading="lazy" decoding="async">
  <p class="foot-meta">Orange County, California · {PHONE_DISPLAY} · {IG_DISPLAY}</p>
</footer>
'''
