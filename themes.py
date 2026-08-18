#!/usr/bin/env python3
"""Five separate visual worlds. Same markup, five stylesheets — no blending."""

RESET = """
*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;overflow-x:hidden}
/* height:auto is not cosmetic here. Once an <img> carries width/height attributes, the
   attribute height becomes a used value and wins over aspect-ratio, so a 1200x1600 photo
   lays out 1600px tall inside a tile meant to be 516px. Global, so the next image added
   cannot reintroduce it; .brand img sets its own height and out-specifies this. */
img,picture,video{max-width:100%;display:block}
img{height:auto}
h1,h2,h3,p,ul,figure{margin:0}
h1 em{font-style:normal}
ul{list-style:none;padding:0}
a{color:inherit}
.skip{position:absolute;left:-9999px;top:0;z-index:99;padding:.7rem 1rem}
.skip:focus{left:0}
.ph{background:currentColor;opacity:.12;aspect-ratio:4/3}
/* Reduced motion is not "no motion". Every keyframed thing on this site has its FINISHED
   state as its base state, so dropping the animations hides nothing — the rail is simply
   ruled, the headline simply set, the receipt simply printed. What stays is colour and
   border feedback, because that is how a control confirms it was pressed; killing it too
   makes the interface feel broken rather than calm. Only the two wipes are forced instant,
   since a wipe IS travel. */
@media (prefers-reduced-motion:reduce){
  *{animation:none!important}
  .nav-links a::after{transition:none}
  .nav .cta,.nav .cta:hover,.nav .cta:focus-visible{transition:none}
  html{scroll-behavior:auto}
  /* These wait for an animation to reveal them. With animations off there is no animation
     to do it, so they have to start revealed or they never appear at all. */
  .js .services::after{transform:none}
  .js .vs-table:not(.is-set) .vs-k,
  .js .vs-table:not(.is-set) .vs-a,
  .js .vs-table:not(.is-set) .vs-b{clip-path:none}
  /* The crop marks still appear — they are hover feedback and removing them entirely
     would make the gallery feel dead. They just stop travelling. */
  .shot picture::before,.shot picture::after{transition:none}
}
"""

# ---------------------------------------------------------------- A
A = dict(
    name="Workshop print",
    fonts='<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Anton&family=Archivo:wght@400;600;700&display=swap" rel="stylesheet">',
    contract=dict(
        thesis="A workshop's own printed matter — hard tiles, flat color, hairline rules. Refuses the centered SaaS hero.",
        world="Cream ground #FFFDEB, safety orange #FD5719, navy #17255A, black hairlines. Anton caps over Archivo tables. Zero radius and zero shadow everywhere EXCEPT the quote form, where answers are circled the way they are on a paper ticket: pill chips, softened fields. Radius is a form affordance here, never a page style.",
        story="This is a bench that prints its own signage. The parts are listed because listing them is the point.",
        viewport="Orange tile block left, headline in condensed caps right, $700 set as a printed price stamp, quote button as a hard black tile.",
        form="Flat-color workshop print, extending the existing logo's own 2x2 tile grammar.",
    ),
    css="""
:root{--bg:#FFFDEB;--ink:#111;--orange:#FD5719;--navy:#17255A;--rule:#111;--dim:#4A463A;--on-navy:#CFD5EE;--r-pill:999px;--r-field:10px}
/* Ink on orange, never white. White on #FD5719 is 3.20:1 and fails AA at body sizes;
   ink is 5.89:1 and passes everywhere. It is also the correct print vernacular for
   safety orange. */
::selection{background:var(--orange);color:var(--ink)}
html{scrollbar-color:var(--ink) var(--bg)}
/* The nav is sticky, so an anchor jump lands its target heading underneath it. Every
   "Start your quote" link on the page shares this destination. */
html{scroll-padding-top:5rem}
body{background:var(--bg);color:var(--ink);font:400 17px/1.55 Archivo,sans-serif;caret-color:var(--orange)}
/* Two-layer ring: a cream gap then an ink outline. A single orange ring vanished on the
   orange hover fill, and any single colour fails against one of cream / ink / orange /
   navy. One of these two layers always contrasts, whatever it lands on. */
:focus-visible{outline:3px solid var(--ink);outline-offset:3px;box-shadow:0 0 0 3px var(--bg)}
h1,h2,h3{font-family:Anton,sans-serif;font-weight:400;text-transform:uppercase;letter-spacing:-.01em;line-height:.92}
.skip{background:var(--ink);color:var(--bg)}

.nav{display:flex;align-items:center;gap:1.5rem;padding:.9rem 2rem;border-bottom:2px solid var(--rule);flex-wrap:wrap;background:var(--bg);position:sticky;top:0;z-index:20}
.brand{display:flex;align-items:center;gap:.6rem;text-decoration:none}
.brand img{width:40px;height:40px}
/* One family across the whole lockup, matching the SVG wordmark. The hierarchy is
   carried by weight alone — setting only the first word in the display face read as
   two brands bolted together. */
.brand-txt{font-weight:400;letter-spacing:-.01em}
.brand-txt b{font-weight:400}
.nav-links{display:flex;gap:1.4rem;margin-left:auto;font-size:.86rem;text-transform:uppercase;letter-spacing:.06em;font-weight:600}
/* The orange rule is this world's own mark — it already sits printed under .tel and .ig,
   and runs down the hero as a 12px rail. Here it draws instead of appearing, so the nav
   carries three states of one device: unmarked, marking, marked. Exit is faster than
   entrance; the rule is withdrawn, not un-drawn. */
.nav-links a{position:relative;text-decoration:none;
  transition:color .14s cubic-bezier(.16,1,.3,1)}
.nav-links a::after{content:"";position:absolute;left:0;right:0;bottom:-.5em;height:2px;
  background:var(--orange);transform:scaleX(0);transform-origin:left;
  transition:transform .15s cubic-bezier(.16,1,.3,1)}
/* The rule already had three states — unmarked, marking, marked — but nothing ever held
   the marked one. The section you are actually in now holds it, drawn with the same stroke.
   Colour is deliberately NOT used to carry this: orange type on cream is 3.13:1 and fails
   AA at this size. aria-current carries it for anyone not looking at the rule. */
.nav-links a[aria-current]::after{transform:scaleX(1)}
.nav-links a:hover,.nav-links a:focus-visible{color:var(--orange);transition-duration:.22s}
.nav-links a:hover::after,.nav-links a:focus-visible::after{transform:scaleX(1);transition-duration:.28s}
.nav-act{display:flex;align-items:center;gap:1rem;font-size:.86rem;font-weight:600}
.nav-act .tel,.nav-act .ig{text-decoration:none;border-bottom:2px solid var(--orange);
  transition:color .14s cubic-bezier(.16,1,.3,1)}
.nav-act .tel:hover,.nav-act .ig:hover{color:var(--orange)}
.cta{background:var(--ink);color:var(--bg);padding:.75rem 1.2rem;text-decoration:none;font-family:Anton,sans-serif;text-transform:uppercase;letter-spacing:.03em;border:2px solid var(--ink)}
.cta:hover{background:var(--orange);border-color:var(--orange);color:var(--ink)}
/* Header CTA only. The orange arrives by the same gradient the hero rail is drawn with,
   wiped from the left rather than swapped — a bigger surface, so a longer draw.
   Two things this has to get right, both learned the hard way:
   1. It must sit AFTER .cta:hover and restate background-image in both states. That rule
      uses the `background` SHORTHAND, which resets background-image to none, and it ties
      .nav .cta on specificity — so source order decided it and the gradient was erased.
   2. The label must not cross-fade. Ink over a half-filled button is ink on black and the
      text disappears for the length of the wipe, so colour switches with zero duration,
      held until the orange has landed, and snaps straight back on exit. */
.nav .cta,.nav .cta:hover,.nav .cta:focus-visible{
  background-color:var(--ink);
  background-image:linear-gradient(var(--orange),var(--orange));
  background-repeat:no-repeat;background-position:0 0}
.nav .cta{background-size:0% 100%;color:var(--bg);
  transition:background-size .16s cubic-bezier(.16,1,.3,1),color 0s linear 0s,border-color .16s linear}
.nav .cta:hover,.nav .cta:focus-visible{background-size:100% 100%;color:var(--ink);
  border-color:var(--orange);
  transition:background-size .26s cubic-bezier(.16,1,.3,1),color 0s linear .22s,border-color .2s linear}

.hero{display:grid;grid-template-columns:1.2fr .8fr;border-bottom:2px solid var(--rule)}
.hero-txt{padding:4rem 2rem 3.5rem;border-right:2px solid var(--rule);background:
  linear-gradient(var(--orange),var(--orange)) 0 0/12px 100% no-repeat}
/* The rail is a ruled margin, so it draws downward rather than appearing. It runs against
   the headline's horizontal wipe — perpendicular strokes, one moment — and finishes first,
   which is the order the work actually happens in: rule the page, then set the type.
   Base state is the finished rail, so reduced motion leaves it simply drawn. */
@keyframes rule-down{from{background-size:12px 0%}to{background-size:12px 100%}}
.hero-txt{animation:rule-down .85s cubic-bezier(.25,.46,.45,.94) both}
.hero-txt>*{padding-left:1.6rem}
/* Sized so each sentence holds one line across the whole desktop range — the longest line
   runs ~8.5x the font size, and the column clears that from the 980px breakpoint up.
   Orphaned single words are what made the previous headline set badly. */
/* Looser than the shared .92 heading rule, and h1 only — h2/h3 stay tight. The marker
   stroke behind THE is anchored to its own content box, so the extra leading opens a real
   gap between the top of the stroke and the previous line's baseline instead of leaving
   them flush. */
h1{font-size:clamp(2.3rem,5.2vw,4.8rem);line-height:1.22}
/* The headline sets in all caps, so "THE" cannot carry its emphasis by case. A marker
   stroke does it instead — an orange highlight laid over the word, drawn with the same
   gradient idiom as the nav button. Ink on orange is 5.89:1, better than the 3.13:1 the
   orange-on-cream lettering was scraping by on. The .08em padding gives the stroke a
   little bleed past the glyphs so it reads as a marker, not a tight box; the matching
   negative margin keeps the line length unchanged. */
h1 em{color:var(--ink);
  background-image:linear-gradient(var(--orange),var(--orange));
  background-repeat:no-repeat;background-position:0 .10em;background-size:100% 1.42em;
  padding:0 .17em;margin:0 -.17em}
/* The headline prints rather than arrives: a hard-edged wipe crosses left to right the way
   a press bar crosses paper. No fade, no rise — this world has no soft edges.
   Easing matters more than duration here: cubic-bezier(.16,1,.3,1) was 97% complete by
   310ms, so the wipe was over before it registered. A quadratic ease-out is ~72% at the
   halfway mark, which is what makes the travel readable.
   The base state is the FINISHED headline, highlight included. Under prefers-reduced-motion
   the global reset kills both animations and the headline is simply there — never clipped
   away, never left unhighlighted. */
@keyframes print-line{from{clip-path:inset(-.35em 100% -.35em -.35em)}
                      to{clip-path:inset(-.35em -.35em -.35em -.35em)}}
/* The stroke height is explicit, not 100%: Anton's inline content box is 1.497em, so a
   full-height background spills past the line box and paints over the line above.
   Every number here is measured from the live font via canvas TextMetrics, not estimated.
   Anton at this size: ascent 1.174em, descent .323em, caps topping out .315em below the
   content-box top.
   The stroke runs .10em to 1.52em — .215em of orange above the caps and .346em below the
   baseline, about double the previous bleed on both edges, with .17em of horizontal bleed
   either side (the matching negative margin keeps the line length unchanged, so widening
   the marker never re-wraps the headline).
   Growing upward costs clearance against the line above, so the leading was opened from
   1.14 to 1.22 to pay for it: the gap from the previous line's baseline to the top of the
   stroke stays ~10px rather than collapsing to ~4px. The space below the baseline is empty
   because the line is all caps. */
@keyframes highlight-accent{from{background-size:0% 1.42em}to{background-size:100% 1.42em}}
h1{animation:print-line 1.45s cubic-bezier(.25,.46,.45,.94) both}
h1 em{animation:highlight-accent .6s cubic-bezier(.3,.7,.4,1) 1.3s both}
.lead{max-width:66ch;margin-top:1.6rem;font-size:1.06rem;color:var(--dim)}
.price{margin-top:2.2rem;display:inline-block;background:var(--navy);color:#fff;padding:.7rem 1.1rem;margin-left:1.6rem}
.price-lab{text-transform:uppercase;font-size:.7rem;letter-spacing:.12em;font-weight:700;display:block}
.price b{font-family:Anton,sans-serif;font-weight:400;font-size:2.3rem;line-height:1}
.hero-act{display:flex;gap:1rem;align-items:center;margin-top:2.2rem;flex-wrap:wrap}
.cta-lg{padding:1rem 1.6rem;font-size:1.15rem}
.tel-lg{font-weight:700;text-decoration:none;border-bottom:3px solid var(--orange)}
/* Every source photograph is portrait (3:4 to 4:5), so the box holds the source ratio
   rather than stretching to whatever height the text column happens to be. Filling a
   taller hero cropped 13% off the sides of the machine. */
.hero-media{height:auto;align-self:start}
.hero-media img{width:100%;height:auto;aspect-ratio:var(--ar,576/800);object-fit:cover;object-position:50% 45%}

section{padding:4.5rem 2rem;border-bottom:2px solid var(--rule)}
h2{font-size:clamp(1.9rem,3.6vw,3rem);margin-bottom:.4rem}
/* --- the sheet's other margin ------------------------------------------------
   The hero's rail is a ruled margin drawn before the type is set. This is the same
   device on the opposite edge in the SAME colour, and NOWHERE ELSE — two rails read as
   the two margins of one sheet, five would read as wallpaper and would cost the hero the
   thing that makes its entrance feel authored.
   It was navy for one revision. Orange is right: it keeps each colour to a single job —
   orange is the rule, the thing that marks and draws (this, the hero rail, the marker
   over THE, the hover marks, the Us column key); navy is fact, the thing that states
   (the $700 stamp, the price chips, the claim spine, the quote panel). Navy here made
   the rail argue with the price chips six inches away for the same meaning.
   Same 12px, same easing, same .85s, same downward draw: it is the same rule, so it is
   identical in every measurable way except side and colour. It reuses rule-down outright
   — only background-position differs, and that is static.
   Geometry is mirrored from the hero as MEASURED, not as assumed: its rail sits 32px in
   from the viewport edge with a ~40px gutter before the lettering. So this one sits 2rem
   in from the right edge with the same 40px gutter, which is what padding-right:5.25rem
   buys (32 inset + 12 rail + 40 gutter). Flush to the edge read as a page border rather
   than as the hero's rule. The left/right asymmetry is the point, not a mistake — a ruled
   margin takes space on paper too.
   The rail is a pseudo-element scaled on the Y axis, NOT a background-size animation like
   the hero's. The hero can afford that because it draws once at load with nothing else
   happening. This one draws mid-scroll down a section that is 814px on desktop and 1508px
   on mobile, and animating background-size repaints that whole area every frame while the
   compositor is already busy scrolling — which is what made it stutter and appear to
   restart. transform is compositor-only: no repaint, no re-rasterisation to snap back
   from. Same 12px, same easing, same .85s, same downward draw. */
.services{position:relative;padding-right:5.25rem}
.services::after{content:"";position:absolute;top:0;right:2rem;width:12px;height:100%;
  background:var(--orange);transform-origin:top;pointer-events:none}
/* THE BUG THIS FIXES: the rail's resting state is a full-height bar, so the section used
   to scroll into view with the rail already completely drawn — and then the trigger fired
   and animated it from zero, snapping it back to nothing and redrawing it. That is what
   read as "it completes, then restarts". It was never the animation re-running.
   With script present the rail waits at zero and is only ever drawn by the animation.
   Without .js there is no rule at all and the bar is simply there, which is still the
   right no-script outcome — the fail-safe is kept, it just no longer leaks into the
   scripted path. */
.js .services::after{transform:scaleY(0)}
@keyframes rule-draw{from{transform:scaleY(0)}to{transform:scaleY(1)}}
/* Gated behind the class, exactly like the versus table: with no script, or under reduced
   motion, the rail is simply there at full height. A section missing its edge is a worse
   failure than a section that does not animate, so the finished state is the default. */
.js .services.is-ruled::after{animation:rule-draw 1.1s cubic-bezier(.25,.46,.45,.94) forwards}
/* Once it has drawn, the animation is taken off the element entirely. Whatever restarts it
   — a re-rasterised layer, a style recalc, a mobile URL bar resize — cannot restart an
   animation that is no longer declared. Must stay AFTER the rule above: same specificity,
   so source order decides. The rail's resting state is a plain unscaled pseudo-element, so
   removing the animation changes nothing visually. */
.js .services.is-drawn::after{animation:none;transform:scaleY(1)}
.services h2,.wsh-h{margin-bottom:1.8rem}
.wsh-h{margin-top:4rem}
.svc-grid,.wsh-grid{display:grid;gap:2px;background:var(--rule);border:2px solid var(--rule)}
.svc-grid{grid-template-columns:repeat(4,1fr)}
.wsh-grid{grid-template-columns:repeat(2,1fr)}
.svc,.wsh{background:var(--bg);padding:1.7rem 1.4rem}
/* Banding, not a single odd card. nth-child(2) tinted exactly one of four services for
   no reason anybody could name; even-child banding is a real ruled-table device and it is
   what makes the stack scannable once these collapse to one column on a phone. */
.svc:nth-child(even),.wsh:nth-child(even){background:#FFF7DE}
.svc h3,.wsh h3{font-size:1.35rem;margin-bottom:.7rem}
.svc p,.wsh p{font-size:.95rem;color:var(--dim);max-width:40ch}
/* The hero sets $700 as a navy block with cream lettering. These are the same stamp at
   card scale, so the grid carries four of them: price is navy on this site, and a block
   says it louder than navy type did. 14.15:1. Alongside the outlined date chip and the
   solid orange offer chip, the meta row becomes a system — every card ends in a chip, and
   the chip's colour says what kind of fact it is. Scoped rather than !important: .svc p
   sets dim grey at (0,1,1) and .svc .svc-meta beats it at (0,2,0) on its own merits. */
.svc .svc-meta{margin-top:1rem;display:inline-block;background:var(--navy);color:var(--bg);
  padding:.25rem .6rem;font-weight:700;text-transform:uppercase;font-size:.78rem;letter-spacing:.07em}
.wsh-meta{margin-top:1rem;display:flex;gap:.5rem;flex-wrap:wrap;align-items:center}
/* TBD is content, not a placeholder, so it gets a solid outline rather than the hatched
   TODO treatment. The nonprofit offer is a real thing being given away — solid orange,
   ink on it at 5.89:1. Both sit at the TODO chip's scale so the row stays one line. */
.wsh-date{display:inline-block;border:2px solid var(--rule);padding:.16rem .5rem;
  text-transform:uppercase;font-size:.72rem;letter-spacing:.07em;font-weight:700}
.wsh-note{display:inline-block;background:var(--orange);color:var(--ink);padding:.2rem .55rem;
  text-transform:uppercase;font-size:.72rem;letter-spacing:.07em;font-weight:700}

.versus h2{margin-bottom:1.8rem}
.vs-table{border:2px solid var(--rule)}
.vs-head,.vs-row{display:grid;grid-template-columns:15.5rem 1fr 1fr}
/* Navy fills the label column; the header row no longer ships an empty cell to hold it
   open, so the bar's own background paints there and .vs-a starts at column 2. */
.vs-head{background:var(--navy);color:var(--bg);font-family:Anton,sans-serif;text-transform:uppercase;letter-spacing:.04em}
.vs-head span{padding:.85rem 1.1rem}
.vs-head .vs-a{grid-column:2;background:var(--orange);color:var(--ink)}
/* .vs-b sets dim ink for the body rows and ties .vs-head on specificity while coming
   later, so the header's own label was rendering #4A463A on near-black — about 1.8:1
   and effectively invisible. The header cell restates its own colours. */
.vs-head .vs-b{background:var(--ink);color:var(--bg)}
.vs-row{border-top:1px solid var(--rule)}
.vs-row span{padding:1.05rem 1.1rem}
/* The key column now carries the claim itself, not a filing label, so it is set in the
   display face at reading size rather than as small tracked-out caps. */
/* The claims run as one navy spine down the left, continuing the navy header cell
   directly above them. Desktop was the odd one out here — mobile has always set these
   bars in navy, so the two layouts were arguing. Row separation inside the spine has to
   be a light hairline: the table's ink rules are 1.31:1 on navy and simply vanish. */
.vs-k{font-family:Anton,sans-serif;font-weight:400;text-transform:uppercase;font-size:1.15rem;line-height:1.05;letter-spacing:0;display:flex;align-items:center;
  background:var(--navy);color:var(--bg)}
.vs-row .vs-k{border-top:1px solid var(--on-navy)}
/* No tint. The page already carries two creams; a third one here was decoration doing a
   job that weight and the orange header cell already do. */
/* The header keys the two sides in colour and then the body used to drop it, so every
   row read as one undifferentiated block — in the one section whose entire argument is
   that there are two sides. The keys now run the full height of each column, which is
   exactly what mobile already did with its top borders. Edges, not fills: a third cream
   would weaken the palette to do a job a 3px rule does outright. Orange clears the 3:1
   non-text threshold on cream at 3.13:1. */
.vs-a{font-weight:600}
.vs-row .vs-a{border-left:3px solid var(--orange)}
.vs-row .vs-b{border-left:3px solid var(--ink)}
.vs-b{color:var(--dim)}

/* --- the comparison assembles ------------------------------------------------
   Not a list appearing as a list — a confrontation. "Us" strikes in from the left,
   "A boxed prebuilt" from the right, and they meet at the divider. Two sides brought
   together is the argument this section makes, so it is the argument the motion makes.
   The row hairlines are NOT animated: the grid is already ruled and the cells fill into
   it, which is the same order the hero works in — rule the page, then set the type.
   Everything hangs off .is-set, added by script only once the table is properly on
   screen. Without it there is no animation at all, so a visitor with no JavaScript, or a
   reduced-motion visitor, gets the finished table rather than an empty one. That is why
   the class gates it instead of the animation running by default. */
@keyframes strike-left{from{clip-path:inset(0 100% 0 0)}to{clip-path:inset(0 0 0 0)}}
@keyframes strike-right{from{clip-path:inset(0 0 0 100%)}to{clip-path:inset(0 0 0 0)}}
/* Same fix as the services rail. The cells' resting state is visible, so the table used
   to scroll into view fully drawn and then strike itself in from nothing — the identical
   "completes, then restarts" the rail had, only less obvious because this trigger fires
   almost as soon as the table appears. With script present the cells wait clipped, which
   is exactly where each animation begins. Without .js there is no rule and the table is
   simply there.
   `both` stays on the animations below: it is what holds a row clipped through its stagger
   delay. :not(.is-set) covers before the trigger, `both` covers during. Between them there
   is no frame where a cell is drawn before its own wipe. */
.js .vs-table:not(.is-set) .vs-k,
.js .vs-table:not(.is-set) .vs-a{clip-path:inset(0 100% 0 0)}
.js .vs-table:not(.is-set) .vs-b{clip-path:inset(0 0 0 100%)}
.vs-table.is-set .vs-k,.vs-table.is-set .vs-a{
  animation:strike-left .45s cubic-bezier(.25,.46,.45,.94) both}
.vs-table.is-set .vs-b{
  animation:strike-right .45s cubic-bezier(.25,.46,.45,.94) both}
/* These MUST sit after the two rules above: `animation:` is a shorthand and resets
   animation-delay to 0, so a stagger declared earlier would be silently wiped. The header
   is child 1 and keeps delay 0, leading the four rows in. Total 280ms + 450ms — one
   sequence, capped, not a queue. */
.vs-table.is-set .vs-row:nth-child(2)>*{animation-delay:70ms}
.vs-table.is-set .vs-row:nth-child(3)>*{animation-delay:140ms}
.vs-table.is-set .vs-row:nth-child(4)>*{animation-delay:210ms}
.vs-table.is-set .vs-row:nth-child(5)>*{animation-delay:280ms}

/* Borders ride the items, not the container: 5 shots in 3 columns must not paint a 6th cell. */
.gal-grid{display:grid;grid-template-columns:repeat(3,1fr);border-top:2px solid var(--rule);border-left:2px solid var(--rule)}
.shot{background:var(--bg);border-right:2px solid var(--rule);border-bottom:2px solid var(--rule)}
/* Portrait box to match the source material. The old 4/3 landscape box was cropping
   roughly 44% off the height of every photograph in the set. */
.shot img{aspect-ratio:4/5;object-fit:cover;width:100%}
figcaption{padding:.9rem 1.1rem;border-top:1px solid var(--rule);display:flex;gap:.6rem;flex-wrap:wrap;text-transform:uppercase;font-size:.76rem;letter-spacing:.07em;font-weight:700}
/* Was orange type on cream: 3.13:1 at 12.16px bold, which is not large text, so AA
   wanted 4.5:1 and it failed. The site already has a solid-orange chip (the nonprofit
   offer), so the GPU becomes one — ink on orange is 5.89:1 and the part reads harder than
   it did as coloured text. */
.gpu{background:var(--orange);color:var(--ink);padding:.1rem .45rem}

/* --- marking the frame -------------------------------------------------------
   These tiles are not links, so the hover must not behave like one: no lift, no shadow,
   nothing that promises a click that does not exist. What a contact sheet actually gets is
   marked — the printer draws crop marks on the frame worth keeping. Two brackets wipe out
   from opposite corners in the same orange rule the nav links use, so hovering annotates
   the photograph rather than offering it.
   clip-path rather than scaling a bordered box: scaling would thin the 2px rule to
   sub-pixel through the whole reveal. Same tool the comparison table strikes with.
   (hover:hover) guards the lot — a touchscreen has no hover, and without it a tap would
   leave the marks stuck on until you tapped something else. */
@media (hover:hover){
  .shot picture{position:relative}
  /* 3.5rem arms against a 12px rule — roughly 1:4.7. At the old 2.6rem the brackets read
     as solid corner blocks once the rule reached rail weight; the shape only survives if
     the arms grow with the thickness. */
  .shot picture::before,.shot picture::after{content:"";position:absolute;
    width:3.5rem;height:3.5rem;pointer-events:none;
    transition:clip-path .24s cubic-bezier(.16,1,.3,1)}
  /* 12px — the same weight as the two section rails, deliberately: this is the same orange
     mark, drawn on a photograph instead of down a margin. Far clear of the 2px hairline
     that rules every tile and table, which the marks used to be mistaken for. box-sizing
     is border-box globally, so thickening never shortens the arms. */
  .shot picture::before{left:.7rem;top:.7rem;
    border-left:12px solid var(--orange);border-top:12px solid var(--orange);
    clip-path:inset(0 100% 100% 0)}
  .shot picture::after{right:.7rem;bottom:.7rem;
    border-right:12px solid var(--orange);border-bottom:12px solid var(--orange);
    clip-path:inset(100% 0 0 100%)}
  .shot:hover picture::before,.shot:hover picture::after{clip-path:inset(0)}
}
.inline-cta{display:inline-block;margin-top:2.5rem;background:var(--ink);color:var(--bg);padding:.85rem 1.4rem;text-decoration:none;font-family:Anton,sans-serif;text-transform:uppercase}
.inline-cta:hover{background:var(--orange);color:var(--ink)}

.quote{background:var(--navy);color:#fff}
.quote h2{color:#fff}
.q-lead{margin:.7rem 0 1.4rem;max-width:60ch}
.q-act{display:flex;gap:1rem;margin-top:1.6rem;flex-wrap:wrap}
/* The panel's fallback action sits directly under the submit button, so it takes the
   form's radius too. Scoped to .quote — the hero and nav buttons stay hard-edged,
   because the softening is a property of the form, not of the page. */
.quote .cta{background:var(--orange);border-color:var(--orange);color:var(--ink);
  border-radius:var(--r-field)}
.ig-lg{align-self:center;font-weight:700;border-bottom:3px solid var(--orange);text-decoration:none}
/* Touch gets no hover, so without this a tap on the only conversion on the site produces
   no acknowledgement at all until the browser decides to act. A press, in a world made of
   printed tiles, is the tile going down. 1px, instant — feedback this fast must not be
   transitioned or it reads as lag. */
.cta:active,.inline-cta:active,.qf-submit:active,.qf-chip:active,
.mobile-bar a:active,.rc-print:active,.wsh-go:active{transform:translateY(1px)}

.todo{display:inline-block;background:repeating-linear-gradient(45deg,#FFD8C4,#FFD8C4 6px,#FFE9DD 6px,#FFE9DD 12px);color:#8A2B00;border:1px dashed #8A2B00;padding:.16rem .5rem;font-size:.72rem;text-transform:uppercase;letter-spacing:.06em;font-weight:700}

/* ---------------------------------------------------------------- quote form
   The job ticket. Cream slips stamped onto the navy panel — the one place on the
   page where the visitor writes on the print instead of reading it.

   The 01–05 numbering is load-bearing, not ornament: it tells someone on a phone
   that there are exactly five things to answer before they commit to the first,
   which is the job a progress bar does worse. The cream rules between lines are
   the same 2px hairline the rest of the sheet uses, turned inside out for the
   dark ground.

   Orange is already carrying four jobs on this page (rail, marker stroke, hover
   mark, primary fill). It does NOT pick up error signalling as a fifth: an
   invalid answer prints a cream chip with ink type, which is louder here than
   any colour and does not compete with the submit button. */
.qf{max-width:46rem;margin-top:2.4rem}
/* The reset zeroes <ul> only. Left alone, the ordered list paints its own 1.–5.
   markers beside the printed 01–05 and indents every field 40px past the submit
   button it is supposed to line up with. */
.qf-list{list-style:none;margin:0;padding:0;counter-reset:q}
/* A hidden branch generates no box, so it never increments — which is the whole reason
   the numbering is a counter and not a literal. A repair reads 01-04 with no holes in it. */
.qf-q{padding:2rem 0;counter-increment:q}
/* Picking a service silently swaps the middle of the form — three questions vanish and
   another appears, with nothing to say what happened. The new lines print in with the same
   downward feed the receipt uses, because that is what this is: another line added to the
   ticket. Reusing the world's own device rather than inventing a second one is the whole
   reason it reads as meaning instead of decoration.
   `forwards`, never `backwards` or `both`, and no stagger delay. The from-state of this
   animation HIDES the line, so a backwards fill would leave form questions invisible to
   anything that stopped the animation advancing. A staggered print reads slightly better;
   an unanswerable form reads like a broken site. The default state stays visible and the
   lines feed in together. */
@keyframes feed-line{from{clip-path:inset(0 0 100% 0)}to{clip-path:inset(0 0 0 0)}}
.qf-q[data-for]:not([hidden]){
  animation:feed-line .34s cubic-bezier(.25,.46,.45,.94) forwards}
.qf-n::before{content:counter(q,decimal-leading-zero)}
.qf-q:first-child{padding-top:0}
.qf-q+.qf-q{border-top:2px solid var(--bg)}
/* Fieldset ships with a border, padding and an intrinsic min-width that fights grid;
   all three are cleared so <legend> can behave like an ordinary block label. */
.qf-set{border:0;margin:0;padding:0;min-width:0}
.qf-legend{display:block;width:100%;padding:0;margin:0 0 1rem;color:#fff;
  font-family:Anton,sans-serif;font-weight:400;font-size:1.35rem;line-height:1.1;
  text-transform:uppercase;letter-spacing:-.01em}
.qf-n{color:var(--orange);margin-right:.6rem;font-variant-numeric:tabular-nums}
/* Tinted from the navy rather than grayed — a neutral gray on a coloured ground reads
   as a rendering fault. 9.9:1 on the panel. */
.qf-opt{margin-left:.55rem;vertical-align:.12em;color:var(--on-navy);
  font-family:Archivo,sans-serif;font-weight:700;font-size:.72rem;letter-spacing:.1em}

/* Real radios and checkboxes, hidden and driven through their labels: keyboard
   navigation, the group semantics and the checked state all come from the browser, not
   from script. One pill serves both — pick-one and pick-many look identical because the
   legend already says which it is. */
.qf-chips{position:relative;display:flex;flex-wrap:wrap;gap:.6rem}
.qf-pick{position:absolute;width:1px;height:1px;opacity:0;pointer-events:none}
.qf-chip{display:flex;align-items:center;justify-content:center;min-height:52px;
  padding:.6rem 1.5rem;border:2px solid #fff;border-radius:var(--r-pill);color:#fff;
  font-weight:700;cursor:pointer;-webkit-user-select:none;user-select:none;text-align:center;
  transition:border-color .16s linear}
/* Hover moves the ring, not the fill. Orange type on navy is 4.5:1 at the margin, so the
   label stays white at 14.6:1 and the colour change happens on the edge instead. The
   nav's inset underline device does not survive here — a pill has no straight bottom
   edge to draw it along, and clipped to the radius it read as a smear. */
.qf-chip:hover{border-color:var(--orange)}
/* The fill SNAPS. Selection is a state, not feedback, and a 160ms background fade under
   a label that switches to ink instantly leaves ink on navy — 1.3:1 — for the length of
   the fade. Same failure the nav button had; the fix is the same: never cross-fade a
   surface out from under type that has already changed colour. */
.qf-pick:checked+.qf-chip{background-color:var(--orange);border-color:var(--orange);
  color:var(--ink);box-shadow:none}
.qf-pick:focus-visible+.qf-chip{outline:3px solid #fff;outline-offset:3px}

.qf-in{width:100%;font:inherit;background:var(--bg);color:var(--ink);
  border:0;border-radius:var(--r-field);padding:.85rem 1.05rem;min-height:52px}
textarea.qf-in{min-height:6rem;line-height:1.5;resize:vertical;display:block}
.qf-in::placeholder{color:var(--dim);opacity:1}
/* Ink underscore inside the field, not an orange one. Never the only signal — the
   error chip below carries the words. */
.qf-in[aria-invalid="true"]{box-shadow:inset 0 -5px 0 var(--ink)}
.qf-pair{display:grid;grid-template-columns:1fr 1fr;gap:1rem}
.qf-field{display:block}
.qf-sub{display:block;margin-bottom:.45rem;color:#fff;font-weight:700;
  text-transform:uppercase;font-size:.7rem;letter-spacing:.1em}

/* The page-wide focus ring is an ink outline over a cream gap. Ink on navy is 1.3:1 —
   effectively invisible — so the whole navy panel inverts it: navy gap, white outline.
   This covers the form, the phone tile and the Instagram link alike. */
.quote :focus-visible{outline:3px solid #fff;outline-offset:3px;box-shadow:0 0 0 3px var(--navy)}

.qf-err,.qf-note{background:var(--bg);color:var(--ink);font-weight:700;line-height:1.35}
.qf-err{display:inline-block;margin-top:.8rem;padding:.35rem .75rem;font-size:.85rem;
  border-radius:var(--r-field)}
.qf-note{display:block;margin-top:1.6rem;padding:.85rem 1.05rem;font-weight:600;
  border-radius:var(--r-field)}
.qf-err[hidden],.qf-note[hidden],.qf-done[hidden]{display:none}
.qf-todo{margin-top:1.6rem;color:var(--on-navy);font-size:.85rem}
.qf-todo .todo{margin-right:.5rem}
.qf-hp{position:absolute;width:1px;height:1px;overflow:hidden;
  clip-path:inset(50%);white-space:nowrap}

.qf-submit{display:block;width:100%;margin-top:2.2rem;padding:1.05rem 1.4rem;
  font:inherit;font-family:Anton,sans-serif;font-weight:400;font-size:1.3rem;
  text-transform:uppercase;letter-spacing:.03em;cursor:pointer;border-radius:var(--r-field);
  background:var(--orange);color:var(--ink);border:2px solid var(--orange);
  transition:background-color .16s linear,border-color .16s linear,color .16s linear}
/* Inverts to cream, not to ink: an ink tile on the navy panel is 1.3:1 against its own
   ground and the button would disappear on hover. */
.qf-submit:hover{background:var(--bg);border-color:var(--bg);color:var(--ink)}
.qf-submit[disabled]{cursor:progress;background:var(--bg);border-color:var(--bg)}

.qf-done{max-width:46rem;margin-top:2.4rem;padding:1.5rem 1.6rem 1.2rem;
  background:var(--bg);color:var(--ink);border-radius:var(--r-field)}
/* It feeds out of the machine rather than fading in. Same family as the headline's
   left-to-right press wipe, turned through ninety degrees — paper leaves a printer
   downward. The rows need no stagger of their own; the wipe already reveals them in
   order, which is what makes it read as printing rather than as a list animating.
   700ms is licensed here: this fires once, at the one milestone on the site. */
@keyframes feed{from{clip-path:inset(0 0 100% 0)}to{clip-path:inset(0 0 0 0)}}
.qf-done:not([hidden]){animation:feed .7s cubic-bezier(.25,.46,.45,.94) both}
.rc-head{font-size:.72rem;text-transform:uppercase;letter-spacing:.14em;font-weight:700;
  color:var(--dim);padding-bottom:.7rem;border-bottom:2px solid var(--rule)}
.qf-done h3{font-size:2rem;margin:1.1rem 0 1.2rem}
/* Label/value pairs on hairlines — the same ruled-row vocabulary as the versus table,
   because this is the same kind of document: two columns, one fact per line. */
.rc-list{margin:0;border-top:1px solid var(--rule)}
.rc-row{display:grid;grid-template-columns:9.5rem 1fr;border-bottom:1px solid var(--rule)}
.rc-list dt{padding:.6rem .8rem .6rem 0;text-transform:uppercase;font-size:.7rem;
  letter-spacing:.09em;font-weight:700;color:var(--dim);align-self:center}
.rc-list dd{margin:0;padding:.6rem 0;font-weight:600;overflow-wrap:anywhere}
.rc-msg{max-width:48ch;margin-top:1.2rem}
.rc-foot{display:flex;flex-wrap:wrap;gap:.8rem 1rem;align-items:center;justify-content:space-between;
  margin-top:1.2rem;padding-top:.9rem;border-top:2px solid var(--rule)}
.rc-stamp{text-transform:uppercase;font-size:.7rem;letter-spacing:.09em;font-weight:700;
  color:var(--dim)}
.rc-print{font:inherit;font-weight:700;font-size:.78rem;text-transform:uppercase;
  letter-spacing:.08em;background:none;color:var(--ink);border:0;border-bottom:2px solid var(--orange);
  padding:.15rem 0;cursor:pointer;border-radius:0}
.rc-print:hover{color:var(--orange)}
/* The slip sits on cream, so the navy-panel focus ring would be invisible on it. */
.qf-done :focus-visible{outline:3px solid var(--ink);outline-offset:3px;
  box-shadow:0 0 0 3px var(--bg)}

/* Workshops had no destination: a date that says TBD and nothing to do about it. This
   drops the visitor into the form with Workshop and the right workshop already chosen. */
.wsh-go{font-weight:700;font-size:.76rem;text-transform:uppercase;letter-spacing:.07em;
  text-decoration:none;border-bottom:2px solid var(--orange);padding-bottom:1px}
.wsh-go:hover{color:var(--orange)}
.q-or{margin-top:2.6rem;color:var(--on-navy);font-weight:700;
  text-transform:uppercase;font-size:.72rem;letter-spacing:.12em}
.q-act{margin-top:1rem}

.foot{padding:3rem 2rem;display:grid;grid-template-columns:1fr auto;align-items:center;gap:.7rem 3rem}
.foot-logo{grid-column:2;grid-row:1/3;justify-self:end;width:min(380px,32vw)}
.foot-meta{grid-column:1;grid-row:1;align-self:end;font-weight:600}
.foot-var{grid-column:1;grid-row:2;align-self:start}
.foot-var{color:var(--dim);font-size:.85rem;text-transform:uppercase;letter-spacing:.08em}
.mobile-bar{display:none}

/* ---------------------------------------------------------------- on paper
   A shop whose pitch is "you get the receipt" should hand over one that survives
   Ctrl+P. Two modes: the ordinary page prints legibly, and the slip prints alone.
   The receipt mode is a class the print button sets and afterprint clears, rather
   than a :has() selector — it is the state we actually control, and it cannot be
   confused by a visitor printing the page for some other reason. */
@media print{
  .nav,.mobile-bar,.skip,.rc-print,.qf-todo{display:none!important}
  html,body{background:#fff;color:#000}
  .quote{background:#fff;color:#000}
  .quote h2,.qf-legend,.qf-sub,.rc-msg,.q-or{color:#000}
  /* --on-navy is tinted for the navy panel; on white paper it is 1.5:1. */
  .qf-opt{color:#333}
  .qf-done{max-width:none;margin:0;border:2px solid #000;border-radius:0;background:#fff;
    animation:none;break-inside:avoid}
  .rc-head,.rc-stamp,.rc-list dt{color:#333}
  .hero-txt,.hero{animation:none;background-image:none}
  a{text-decoration:none}
  section{border-bottom:1px solid #000;padding:1rem 0}
  .foot-logo{width:220px}
  /* Receipt only. */
  .printing-receipt body>*:not(main){display:none!important}
  .printing-receipt main>section:not(.quote){display:none!important}
  .printing-receipt .quote>*:not(.qf-done){display:none!important}
  .printing-receipt .quote{padding:0;border:0}
  @page{margin:14mm}
}

@media (max-width:980px){
 .hero{grid-template-columns:1fr}.hero-txt{border-right:0;border-bottom:2px solid var(--rule)}
 .svc-grid{grid-template-columns:repeat(2,1fr)}.gal-grid{grid-template-columns:repeat(2,1fr)}
 .nav-links{display:none}
 .hero-media{height:auto}
 /* Inherits the base 576/800 source ratio; the old 4/5 box here cropped ~10% vertically. */
 .hero-media img{object-position:50% 50%}
 .vs-head,.vs-row{grid-template-columns:12.5rem 1fr 1fr}
 .foot-logo{width:min(320px,38vw)}
}
@media (max-width:640px){
 section{padding:3rem 1.1rem}
 /* The hero runs its rail flush to the screen edge at this width, so this one does too.
    1.1rem of padding minus a 12px rail leaves 5.6px, which reads as cramped rather than as
    a margin; 1.85rem restores the same 17.6px gutter the hero's rail has here. */
 .services{padding-right:1.85rem}
 .services::after{right:0}
 /* The rail draws the full height of the section, and stacking the cards makes that
    section 1506px here against 814px on desktop. At a shared 1.1s the bar therefore
    travels at nearly twice the speed on a phone — 1369px/s against 740 — which is why it
    felt hurried. Worse, only ~470px of it is ever on screen, so the part you actually
    watch was over in a third of a second. 2s restores both: the travel rate lands back
    near desktop's, and the visible stretch takes about as long to draw as it does there.
    A longhand after the shorthand, so only the duration is replaced. */
 .js .services.is-ruled::after{animation-duration:2s}
 /* The hero was paying horizontal padding twice — once as a <section>, once as .hero-txt —
    and a third time as the child indent, eating 21% of a 390px screen. Zeroing the section
    layer is what buys the headline its size; the top padding goes with it, closing the
    dead band above the headline. The rail and photo now run to the screen edge. */
 .hero{padding:0}
 .hero-txt{padding:1.5rem 1.1rem 2.2rem}
 .hero-txt>*{padding-left:.75rem}
 /* .price sets its own padding shorthand earlier in the sheet, so the indent rule above
    was overriding only its LEFT padding and pushing the $700 off centre inside its box.
    Restated here, with the indent moved to margin so the box stays symmetrical. */
 .price{padding:.7rem 1.1rem;margin-left:.75rem}
 h1{font-size:clamp(1.7rem,9.5vw,2.9rem)}
 .lead{font-size:.95rem}
 .svc-grid,.wsh-grid,.gal-grid{grid-template-columns:1fr}
 /* Pills hug their labels and wrap naturally rather than being stretched into an even
    grid — a stretched pill is just a rounded rectangle, and the shape is the point. */
 .qf-chips{gap:.55rem}
 .qf-chip{padding:.6rem 1.15rem;font-size:.94rem}
 .qf-pair{grid-template-columns:1fr;gap:1.2rem}
 .qf-q{padding:1.6rem 0}
 .qf-legend{font-size:1.18rem;margin-bottom:.85rem}
 /* The fixed bar owns the bottom 50px. Nothing scrolls the submit under it on the
    normal path, but any programmatic or anchor scroll that targets it must clear
    the bar — a tap on a half-covered Send lands on Text instead. */
 .qf-submit{font-size:1.15rem;padding:.95rem 1.1rem;scroll-margin-bottom:5rem}
 .qf-q,.qf-done,.qf-note{scroll-margin-bottom:5rem}
 .qf-done{padding:1.3rem 1.1rem 1rem}
 /* Two columns cost more than they pay on a phone: the label column sits empty while a
    sentence-length value wraps four times beside it. Stacked, the slip reads as a list. */
 .rc-row{grid-template-columns:1fr}
 .rc-list dt{padding:.6rem 0 .15rem}
 .rc-list dd{padding:0 0 .65rem}
 .rc-foot{gap:.5rem 1rem}
 .qf-done h3{font-size:1.6rem}
 .foot{grid-template-columns:1fr;gap:1rem}
 .foot-meta{grid-column:1;grid-row:1}
 .foot-var{grid-column:1;grid-row:2}
 .foot-logo{grid-column:1;grid-row:3;justify-self:start;width:min(420px,78%);margin-top:.6rem}
 /* A versus table compares two things at once. Stacking the sides turned that into prose:
    the reader had to hold one cell in memory and scroll to find its counterpart. The
    claim keeps the full width as a navy bar; the two answers sit side by side beneath it,
    divided by a rule, so the comparison survives the small screen. Viable only because
    the copy was distilled to two or three words on the right. */
 .vs-head{display:none}
 .vs-row{grid-template-columns:1fr 1fr;border-top:2px solid var(--rule)}
 .vs-row .vs-k{grid-column:1/-1;border-right:0;border-bottom:1px solid var(--rule);
   background:var(--navy);color:var(--bg);padding:.6rem .85rem;font-size:1.02rem}
 .vs-row .vs-a,.vs-row .vs-b{padding:.7rem .85rem .95rem;font-size:.92rem;line-height:1.4}
 /* Column key, repeated per row rather than left to a header that scrolls away. Text, not
    colour alone — the orange and ink edges are a second, redundant cue. */
 /* The column keys are top borders here, not left ones — reset the desktop edges or
    each cell wears both and reads as a bracket. */
 .vs-row .vs-a{grid-column:1;border-left:0;border-right:1px solid var(--rule);border-top:3px solid var(--orange)}
 .vs-row .vs-b{grid-column:2;border-left:0;border-top:3px solid var(--ink)}
 .vs-row .vs-k{border-top:0}
 .vs-a::before,.vs-b::before{display:block;margin-bottom:.3rem;font-weight:700;
   text-transform:uppercase;font-size:.62rem;letter-spacing:.1em}
 .vs-a::before{content:"Us";color:var(--ink)}
 .vs-b::before{content:"Prebuilt";color:var(--dim)}
 /* The whole nav action group goes: the fixed bar below already carries Text, Instagram
    and Quote. Keeping a second Quote button here forced the nav onto two rows — 144px,
    17.7% of a 640px viewport — which pushed the hero CTA down into the fixed bar's
    strip, where a tap on it opened Messages instead. */
 .nav-act{display:none}
 .nav{padding:.7rem 1.1rem}
 html{scroll-padding-top:4.5rem}
 body{padding-bottom:60px}
 .mobile-bar{display:grid;grid-template-columns:1fr auto auto;gap:2px;position:fixed;bottom:0;left:0;right:0;background:var(--rule);border-top:2px solid var(--rule);z-index:40}
 .mobile-bar a{background:var(--bg);padding:.85rem .7rem;text-decoration:none;font-weight:700;font-size:.82rem;text-align:center}
 .mobile-bar .mb-cta{background:var(--orange);color:var(--ink)}
}
/* Short viewports — SE-class phones and landscape. The fixed bar owns the bottom 50px,
   so every hero control must clear it while the page is at rest; a half-covered button
   invites a tap that lands on Text instead. Tighten the vertical rhythm for the context
   rather than scale the same spacing down. */
@media (max-width:640px) and (max-height:620px){
 .nav{padding:.4rem 1.1rem}
 .brand img{width:32px;height:32px}
 .hero-txt{padding:1rem 1.1rem 1.4rem}
 h1{font-size:clamp(1.35rem,6.6vw,1.9rem)}
 .lead{margin-top:.8rem;font-size:1rem}
 .price{margin-top:1.1rem;padding:.5rem .9rem}
 .price b{font-size:1.9rem}
 .hero-act{margin-top:1.1rem;gap:.7rem}
}
""")

THEMES = {"a": A}
