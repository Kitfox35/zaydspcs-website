#!/usr/bin/env python3
"""Assembles the site. One direction now — Workshop print — written to site/index.html.

The four alternate stylesheets were deleted once the direction was chosen; this file no
longer builds a comparison index because there is nothing left to compare.
"""
import sys
# build.py is edited by hand between runs and its constants are short. Two different
# endpoint URLs of equal length, saved within the same second, look identical to the
# bytecode cache's (mtime, size) check — so a rebuild silently serves the old page.
sys.dont_write_bytecode = True

import pathlib, html, json
from build import (build_body, PHONE_DISPLAY, SERVICE_PATHS, ROOT,
                   SITE_URL, SITE_TITLE, SITE_DESC)
from themes import THEMES, RESET

# Display label -> branch key, emitted so the script cannot drift from build.py.
PATH_MAP = json.dumps({label: key for key, label in SERVICE_PATHS})

OUT = ROOT / "site"
OUT.mkdir(exist_ok=True)

FINISH = ("unreviewed and undocumented is unfinished; this build ends with the finish review, "
          "the verdict, DESIGN.md, and every shipping raster carrying its provenance")

# Progressive enhancement, in this order:
#   no JS  -> the form is a plain POST and the browser enforces `required` itself;
#   JS     -> native bubbles are suppressed and replaced with in-page messages that
#             name the problem and the fix, plus sending / sent / failed states.
# Nothing here hides content or blocks the page if the script fails to run.
FORM_JS = """
<script>
(function(){
  var f = document.getElementById('qform');
  if (!f) return;
  var ENDPOINT = f.getAttribute('data-endpoint') || '';
  var PHONE    = '__PHONE__';
  var PATHS    = __PATHS__;
  var WORDS    = {3:'Three',4:'Four',5:'Five',6:'Six',7:'Seven'};
  // Each path names its own service. The workshop line is deliberately not a promise of a
  // seat: dates are TBD, so it says so rather than implying a booking that does not exist.
  var DONE = {
    build:       'We’ll text you at {p} to talk through the build.',
    repair:      'We’ll text you at {p} about the repair.',
    upgrade:     'We’ll text you at {p} to talk through the upgrade.',
    maintenance: 'We’ll text you at {p} to set up the plan.',
    workshop:    'We’ll text you at {p}. Dates aren’t set yet — ' +
                 'we’ll let you know as soon as they are.'
  };
  // Human labels for the itemised slip. Keyed on the posted field names so a field that
  // is added without a label here simply does not print, rather than printing a raw key.
  var LABELS = {
    service:'Service', budget:'Budget', use_case:'Use', parts:'Parts requested',
    problem:'Problem', 'upgrade_targets[]':'Upgrading', upgrade_budget:'Budget',
    notes:'Notes', workshop:'Workshop', name:'Name', phone:'Phone', email:'Email'
  };
  var note = document.getElementById('qf-note');
  var btn  = document.getElementById('qf-submit');
  var done = document.getElementById('qf-done');
  var calm = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var submitted = false;

  // Only once the script is confirmed running. Without it the visitor keeps the browser's
  // own required-field enforcement on a plain form POST.
  f.noValidate = true;

  function pack(name){
    var g = f.elements[name];
    if (!g) return [];
    return (g.length === undefined) ? [g] : Array.prototype.slice.call(g);
  }
  function service(){ var g = f.elements['service']; return g ? g.value : ''; }
  function pathKey(){ return PATHS[service()] || ''; }
  function ctrls(){ return f.querySelectorAll('[data-err]:not(:disabled)'); }
  function digits(v){ return (v || '').replace(/[^0-9]/g, '').length; }

  function invalid(el){
    if (el.type === 'radio')    return !f.elements[el.name].value;
    if (el.type === 'checkbox') return !pack(el.name).some(function(c){ return c.checked; });
    var v = el.value.trim();
    if (el.required && !v)    return true;
    if (el.id === 'qf-phone') return digits(v) < 10;
    if (el.id === 'qf-email') return v !== '' && !el.checkValidity();
    return el.required && !el.checkValidity();
  }

  // aria-describedby is attached only while the message is visible: a hidden element
  // referenced by describedby is announced as nothing, which is worse than silence.
  function mark(el, show){
    var id = el.getAttribute('data-err');
    if (!id) return;
    var box = document.getElementById(id);
    if (!box) return;
    if (show) { box.textContent = el.getAttribute('data-msg'); box.hidden = false; }
    else      { box.hidden = true; }
    var group = (el.type === 'radio' || el.type === 'checkbox') ? pack(el.name) : [el];
    for (var i = 0; i < group.length; i++) {
      if (show) { group[i].setAttribute('aria-invalid', 'true');
                  group[i].setAttribute('aria-describedby', id); }
      else      { group[i].removeAttribute('aria-invalid');
                  group[i].removeAttribute('aria-describedby'); }
    }
  }

  // Show one branch, disable the rest. Disabling is what keeps another path's answers out
  // of the submission and out of validation; hiding alone does neither.
  function branch(){
    var key = pathKey();
    var qs = f.querySelectorAll('.qf-q[data-for]');
    for (var i = 0; i < qs.length; i++) {
      var on = qs[i].getAttribute('data-for') === key;
      qs[i].hidden = !on;
      var ctl = qs[i].querySelectorAll('input, textarea');
      for (var j = 0; j < ctl.length; j++) {
        ctl[j].disabled = !on;
        if (!on) mark(ctl[j], false);
      }
    }
    var c = document.getElementById('qf-count');
    if (c) {
      var n = f.querySelectorAll('.qf-q:not([hidden])').length;
      c.textContent = key ? (WORDS[n] || n) : 'A few';
    }
  }

  function bind(){
    Array.prototype.forEach.call(f.querySelectorAll('[data-err]'), function(el){
      if (el.type === 'radio' || el.type === 'checkbox') {
        pack(el.name).forEach(function(r){
          r.addEventListener('change', function(){ mark(el, false); });
        });
      } else {
        // Never on the first keystroke. A field the visitor has not reached yet stays
        // silent until they submit.
        el.addEventListener('blur', function(){
          if (submitted || el.value.trim() !== '') mark(el, invalid(el));
        });
        el.addEventListener('input', function(){
          if (el.getAttribute('aria-invalid') && !invalid(el)) mark(el, false);
        });
      }
    });
    // Delegated, not bound per radio: a bfcache restore (back button after submitting)
    // repopulates the radios without firing anything a per-input listener would catch,
    // which would leave a stale branch enabled and posting somebody else's answers.
    f.addEventListener('change', function(e){ if (e.target.name === 'service') branch(); });
    window.addEventListener('pageshow', branch);
  }

  function reveal(el){ el.scrollIntoView({block:'center', behavior: calm ? 'auto' : 'smooth'}); }

  // Itemise exactly what was sent, in the order it was asked. Multi-value fields collapse
  // to one line; empties and the honeypot never appear. Values go in as textContent, so a
  // name with an angle bracket in it stays a name.
  function receipt(){
    var dl = document.getElementById('qf-receipt');
    if (!dl) return;
    dl.textContent = '';
    var data = new FormData(f), seen = {}, order = [];
    data.forEach(function(v, k){
      // Every service-control field starts with an underscore (_subject, _gotcha,
      // _honeypot). None of them are the visitor's answers, so none belong on the slip.
      if (k.charAt(0) === '_' || !String(v).trim()) return;
      if (!seen[k]) { seen[k] = []; order.push(k); }
      seen[k].push(String(v).trim());
    });
    order.forEach(function(k){
      if (!LABELS[k]) return;
      var row = document.createElement('div'); row.className = 'rc-row';
      var dt = document.createElement('dt'); dt.textContent = LABELS[k];
      var dd = document.createElement('dd'); dd.textContent = seen[k].join(', ');
      row.appendChild(dt); row.appendChild(dd); dl.appendChild(row);
    });
    var stamp = document.getElementById('qf-stamp');
    if (stamp) {
      // Not a fabricated ticket number — the actual moment it was logged, which is the one
      // reference both sides can check against.
      stamp.textContent = 'Logged ' + new Date().toLocaleString(undefined,
        {day:'numeric', month:'short', year:'numeric', hour:'numeric', minute:'2-digit'});
    }
  }

  var printBtn = document.getElementById('qf-print');
  if (printBtn) {
    printBtn.addEventListener('click', function(){
      document.documentElement.classList.add('printing-receipt');
      window.print();
    });
    window.addEventListener('afterprint', function(){
      document.documentElement.classList.remove('printing-receipt');
    });
  }

  // "Tell us you're interested" on a workshop card lands in the form with Workshop and
  // that workshop already picked, so the visitor arrives at question 03, not question 01.
  Array.prototype.forEach.call(document.querySelectorAll('[data-workshop]'), function(a){
    a.addEventListener('click', function(){
      var svc = pack('service').filter(function(r){ return r.value === 'Workshop'; })[0];
      if (!svc) return;
      svc.checked = true;
      branch();
      var want = a.getAttribute('data-workshop');
      pack('workshop').forEach(function(r){ if (r.value === want) r.checked = true; });
    });
  });

  f.addEventListener('submit', function(ev){
    ev.preventDefault();
    submitted = true;

    var first = null;
    Array.prototype.forEach.call(ctrls(), function(el){
      var bad = invalid(el);
      mark(el, bad);
      if (bad && !first) first = el;
    });
    if (first) {
      note.hidden = true;
      first.focus({preventScroll: true});
      reveal((first.type === 'radio' || first.type === 'checkbox')
             ? first.closest('.qf-q') : first);
      return;
    }

    if (!ENDPOINT) {
      note.textContent = 'This form is not connected yet. Text ' + PHONE +
        ' and we will take your requirements that way.';
      note.hidden = false;
      reveal(note);
      return;
    }

    // A readable subject line, so the inbox is scannable at a glance rather than fifty
    // rows of the same words.
    var subj = document.getElementById('qf-subject');
    if (subj) subj.value = service() + ' request \u2014 ' + f.elements['name'].value.trim();

    var label = btn.textContent;
    btn.disabled = true;
    btn.textContent = 'Sending…';
    note.hidden = true;

    fetch(ENDPOINT, {method:'POST', body:new FormData(f),
                     headers:{'Accept':'application/json'}})
      .then(function(r){ if (!r.ok) throw new Error(r.status); })
      .then(function(){
        receipt();
        var msg = DONE[pathKey()] || DONE.build;
        document.getElementById('qf-done-msg').textContent =
          'Thanks, ' + f.elements['name'].value.trim() + '. ' +
          msg.replace('{p}', f.elements['phone'].value.trim());
        f.hidden = true;
        done.hidden = false;
        done.focus();
        reveal(done);
      })
      .catch(function(){
        btn.disabled = false;
        btn.textContent = label;
        // Nothing is cleared. Retyping the whole form because a network blipped is how you
        // lose the only conversion on the site.
        note.textContent = 'That did not send — your answers are still here. ' +
          'Try again, or text ' + PHONE + '.';
        note.hidden = false;
        reveal(note);
      });
  });

  bind();
  branch();
})();
</script>
""".replace("__PHONE__", PHONE_DISPLAY).replace("__PATHS__", PATH_MAP)


# The nav's orange rule always had a "marked" state that nothing ever held. This holds it
# for the section actually on screen. Read-only and passive: it sets aria-current and lets
# CSS draw, so there is no scroll handler and nothing to throttle.
NAV_JS = """
<script>
(function(){
  var nav = document.querySelector('.nav');
  var links = {}, sections = [];
  Array.prototype.forEach.call(document.querySelectorAll('.nav-links a[href^="#"]'), function(a){
    var el = document.getElementById(a.getAttribute('href').slice(1));
    if (el) { links[el.id] = a; sections.push(el); }
  });
  if (!nav || !sections.length) return;

  // Deliberately a position test rather than an IntersectionObserver band: "the section
  // whose top has passed under the sticky nav and whose bottom has not yet left" is a rule
  // that can be reasoned about and checked at any scroll offset, where a tuned rootMargin
  // percentage can only be eyeballed. The hero and the quote panel have no nav link, so
  // over them nothing is marked — which is correct, not a gap.
  function currentId(){
    var navH = nav.getBoundingClientRect().height, found = null;
    for (var i = 0; i < sections.length; i++) {
      var b = sections[i].getBoundingClientRect();
      if (b.top - navH - 8 <= 0 && b.bottom > navH) found = sections[i].id;
    }
    return found;
  }

  function paint(){
    var id = currentId();
    for (var k in links) {
      if (k === id) links[k].setAttribute('aria-current', 'true');
      else links[k].removeAttribute('aria-current');
    }
  }

  // All reads happen inside currentId, then one attribute write — no interleaving, so no
  // layout thrash. Throttled to a frame; passive so it never delays the scroll itself.
  // The comparison table plays once, when it is properly on screen rather than when its
  // first pixel appears — a sequence the visitor scrolls past mid-way is worse than none.
  var vs  = document.querySelector('.vs-table');
  var svc = document.querySelector('.services');
  function inView(el, at){
    var b = el.getBoundingClientRect();
    return b.top < innerHeight * at && b.bottom > 0;
  }
  function reveal(){
    if (vs && !vs.classList.contains('is-set') && inView(vs, 0.82))
      vs.classList.add('is-set');
    // NOT earlier than the table, which is what this used to be. At 0.9 the rail began
    // drawing with 13% of the section on screen and its top pinned to the bottom edge, so
    // a 0.85s draw down an 814px section ran almost entirely below the fold and nobody
    // ever saw it. The table can afford a late threshold because it is short; this section
    // is three times its height, so it needs the draw to start once its top is genuinely
    // in the reading area.
    if (svc && !svc.classList.contains('is-ruled') && inView(svc, 0.45))
      svc.classList.add('is-ruled');
  }

  // Retire the animation the moment it finishes. A one-shot class stops it being RE-ADDED,
  // but nothing stopped the browser re-running an animation that was still declared on the
  // element. e.target is the section itself for a ::after animation, so this cannot be
  // triggered by anything animating inside the section.
  if (svc) svc.addEventListener('animationend', function(e){
    if (e.target === svc) svc.classList.add('is-drawn');
  });

  function tick(){ paint(); reveal(); }

  var queued = false;
  addEventListener('scroll', function(){
    if (queued) return;
    queued = true;
    requestAnimationFrame(function(){ tick(); queued = false; });
  }, {passive: true});
  addEventListener('resize', tick, {passive: true});
  tick();

  // Exposed so both scroll rules can be exercised at any offset rather than eyeballed.
  window.__navPaint = paint;
  window.__scrollTick = tick;
})();
</script>
"""


def contract_comment(t):
    c = t["contract"]
    return (f"<!--\n  DIRECTION CONTRACT — {t['name']}\n"
            f"  THESIS: {c['thesis']}\n"
            f"  OWN-WORLD: {c['world']}\n"
            f"  STORY: {c['story']}\n"
            f"  FIRST VIEWPORT: {c['viewport']}\n"
            f"  FORM: {c['form']}\n"
            f"  FINISH: {FINISH}\n-->")


def page(t):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{SITE_TITLE}</title>
<meta name="description" content="{SITE_DESC}">
<link rel="canonical" href="{SITE_URL}">
<!-- The page is the business card people forward. Most of that forwarding happens by text
     message and Instagram DM, where a link with no card renders as a bare grey URL — so the
     share card is part of the design, not an afterthought. Absolute URLs are required here:
     scrapers do not resolve relative paths. -->
<meta property="og:type" content="website">
<meta property="og:site_name" content="Zayd's Custom PCs">
<meta property="og:title" content="{SITE_TITLE}">
<meta property="og:description" content="{SITE_DESC}">
<meta property="og:url" content="{SITE_URL}">
<meta property="og:image" content="{SITE_URL}assets/logo/og.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Zayd's Custom PCs — custom builds, repairs and upgrades in Orange County.">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{SITE_TITLE}">
<meta name="twitter:description" content="{SITE_DESC}">
<meta name="twitter:image" content="{SITE_URL}assets/logo/og.jpg">
<!-- The mark alone, without the wordmark: at 32px the lettering is mud, the four tiles read. -->
<link rel="icon" href="../assets/logo/logo-mark.svg" type="image/svg+xml">
<link rel="icon" href="../assets/logo/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="../assets/logo/apple-touch-icon.png">
<!-- Paints the mobile browser chrome the page's own cream instead of leaving a seam. -->
<meta name="theme-color" content="#FFFDEB">
<!-- Runs during head parse, before the body paints, so anything that should wait for
     script to draw it is never briefly shown in its finished state first. -->
<script>document.documentElement.classList.add('js')</script>
{t['fonts']}
<style>{RESET}{t['css']}</style>
</head>
<body>
{contract_comment(t)}
{build_body()}
{FORM_JS}{NAV_JS}
</body>
</html>
"""


if __name__ == "__main__":
    (OUT / "index.html").write_text(page(THEMES["a"]), encoding="utf-8")
    print("wrote site/index.html")
