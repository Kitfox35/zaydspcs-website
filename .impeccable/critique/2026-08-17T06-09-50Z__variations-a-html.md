---
target: the homepage hero
total_score: 20
max_score: 36
na_heuristics: 7
p0_count: 2
p1_count: 2
timestamp: 2026-08-17T06-09-50Z
slug: variations-a-html
---
**Method: dual-agent** (A: `a85cdd8774acffa2d` · B: `a9c708d7c8833d45c`)

# Critique — Landing page hero, Variation A

**Target:** `variations/a.html` → `<section class="hero">` · Mode: **Persuade**

## Design Health Score

| # | Heuristic | Score | Key Issue |
|---|-----------|-------|-----------|
| 1 | Visibility of System Status | 2 | Clicking the sole CTA produces no confirming feedback; the jump is instant and lands wrong |
| 2 | Match System / Real World | 3 | "Custom builds start at $700" is customer language; but the square logo says GAMING PCS 6px from a wordmark saying Custom PCs |
| 3 | User Control and Freedom | 3 | Nothing traps the user, but the anchor jump is one-way with no return |
| 4 | Consistency and Standards | 2 | "Start your quote" appears 3x in one mobile viewport at three weights with no rank; hero photo is the only build photo with no CPU/GPU caption |
| 5 | Error Prevention | 2 | The mis-tap trap below; nothing prevents reading $700 as *the* price rather than the floor of a $700-$1,500 range |
| 6 | Recognition Rather Than Recall | 3 | Price, services, geography, both contact channels all shown — but "$700" gives no anchor for what $700 *buys* |
| 7 | Flexibility and Efficiency | n/a | A first-visit local-business hero has no repeat users, accelerators, or novice/expert split |
| 8 | Aesthetic and Minimalist Design | 3 | Real discipline — flat color, no radius, no shadow. But the desktop composition is unfinished, not minimal |
| 9 | Error Recovery | 1 | The primary action lands its destination heading entirely behind the sticky nav — the click reads as failed |
| 10 | Help and Documentation | 1 | "Start your quote" never says whether a quote is free, binding, instant, or a conversation |
| **Total** | | **20/36** | **Acceptable (56%)** |

Visual craft is scoring well above interaction craft. The gap is almost entirely microcopy and mobile chrome.

## Design Specificity Verdict

**LLM assessment: the visual world is authored for this business; the argument is not.**

Cannot be swapped: the palette is extracted from `logo-square.svg`, not chosen — which is why the logo sits natively instead of pasted on. The photograph is unmistakably first-party (Lian Li build in a real living room, shutters, framed art, marble floor).

Any PC shop could paste in unchanged: the headline is a pun communicating nothing about custom-built, quoted, itemized, or local. The lead is a four-item service list plus a county name — swap the county and a competitor runs it verbatim.

~70% of the hero's pixels are unique to this business; ~0% of its reasoning is. PRODUCT.md hands the hero five true, unused weapons — part-level transparency, you keep the receipt, no bloatware, upgradeable later, a local human answers the phone — and the hero deploys none.

**Deterministic scan.** The bundled detector runs DEGRADED as installed: `htmlparser2`, `css-select`, `css-tree`, `domutils` absent from skill, project, and global npm root. Exits 0 with `[]` and warns findings are "an undercount, not a clean bill of health." Assessment B supplied deps to a byte-identical scratchpad copy: **exit 2, 18 findings** — 10 low-contrast, 2 cramped-padding, 1 each gray-on-color, all-caps-body, clipped-overflow-container, flat-type-hierarchy, cream-palette, repeating-stripes-gradient. Tool emits `"line": 0` for all 18.

**Agreement:** white `#FFFFFF` on orange `#FD5719` = 3.20:1, failing AA on `.cta:hover` and the resting `.mobile-bar .mb-cta`.

**False positives (3 of 10 contrast hits):** both engines read `.hero-txt`'s `linear-gradient(orange,orange) 0 0/12px 100%` as a full-surface fill, reporting the headline `<em>` at 1.0:1 and the lead at 2.9:1. It is a 12px left rule; text starts 89.6px away. Real values: 3.13:1 and 9.20:1. `clipped-overflow-container` also false. `flat-type-hierarchy` half-right — sampled 10 sizes, missed the display tier (real range 5.95:1), but the six-size cluster between 11.2-15.2px is genuine.

**Visual overlays:** injection succeeded, in-page detector logged 9 findings, live server on port 8400 stopped and verified closed with `a.html` byte-identical. No overlay currently visible.

## Overall Impression

Made by someone with taste and shipped by someone who never used it on a phone. Print-world craft is genuinely good. But the single control the business depends on is physically covered by another button on short screens, its hover state fails the contrast rule PRODUCT.md calls binding, and it asks a stranger for $700-$1,500 while giving no reason to trust anyone.

Biggest opportunity is the cheapest: five true differentiators sitting unused in PRODUCT.md, and a 400x270px hole in the desktop composition to put them in.

## What's Working

**The $700 stamp is correctly conceived, built, and placed.** Only navy object in the composition; constructed as a single unit (11px tracked label welded to 37px Anton numeral) so it resolves in one fixation; 14.5:1, highest-contrast object after the CTA. Satisfies the binding first-viewport constraint at every width including 320x640.

**The palette is derived rather than decorated.** Every color exists in the client's own logo file — why "logo sits natively" is actually met.

**Engineering hygiene beats the interaction design.** One `<h1>`, real `<picture>` with AVIF/WebP, `fetchpriority="high"` on LCP, working skip link, honest `prefers-reduced-motion`, meaningful alt text, zero horizontal overflow at 320/375/1310 verified with `overflow-x:hidden` neutralized.

## Priority Issues

**[P0] The mobile bar covers half the hero's primary button — a tap dials the phone instead**
Verified independently at 320x640: CTA spans y=560-625, fixed bar starts y=590. 35px (53% of the button) covered; `elementFromPoint` at the lower half of "Start your quote" returns `"Call (949) 878-0884"`. Wrong-action mis-tap, not cosmetic occlusion.
Fix: bottom padding on `.hero-act` inside the <=640 block equal to bar height, or `position:sticky` in flow.
Command: `/impeccable adapt`

**[P0] White-on-orange fails AA on the one control the site exists to get clicked**
3.20:1. Hits `.cta:hover` (18.4px/400, not large text) and `.mobile-bar .mb-cta` at rest, on screen in every mobile viewport. PRODUCT.md:94 makes WCAG AA binding.
Fix: label to `var(--ink)` — `#111` on `#FD5719` is 5.88:1, passes at every size, and is the correct print vernacular.
Command: `/impeccable audit`

**[P1] The hero makes an ask and supplies no reason to say yes**
The lead spends itself on a service list and a county name. Every reason to prefer a quoted build over a boxed prebuilt is withheld until the versus table ~1,400px below the fold.
Fix: move one differentiator into the lead; add microcopy bound to the CTA by proximity ("Free, no obligation"). Both already true per PRODUCT.md.
Command: `/impeccable clarify`

**[P1] The primary action's destination lands behind the sticky nav**
At 375x812, `#quote` `<h2>` lands y=107-135 while nav bottom is y=144 — heading entirely invisible; user arrives mid-sentence at a hatched TODO. No `scroll-padding-top` anywhere; affects all six "Start your quote" links. Compounding: mobile nav is 144px tall (17.7% of viewport) because it wraps to two rows, so the headline starts at y=232 and the photograph sits at y=717 with ~44px visible.
Fix: `html{scroll-padding-top:150px}` with desktop override; drop `.nav .cta` below 640px since the bar carries "Quote," reclaiming ~64px.
Command: `/impeccable adapt`

**[P2] The desktop void and wrong `srcset` descriptors**
At 1440x900, ~269x400px of empty cream in the lower-left with the orange rail pointing into it; hero bottom rule falls below the fold at y=991, so nothing signals more page. Separately: the `w` descriptors are wrong on every `<picture>` — files named `-800`/`-1600` are actually 576x800 and 1152x1600, portrait assets named by long edge with the height written into the `w` descriptor, so the browser systematically under-selects at higher DPR.
Fix: fill the void with the P1 differentiators in the `.vs-table`'s hairline grammar; correct descriptors to `576w`/`1152w` in the converter.
Command: `/impeccable layout`

## Persona Red Flags

**Jordan (first-timer, a parent):** Largest text on the page doesn't say whether this is a store, repair shop, or service. Lead answers with a four-item list, multiplying the question. "$700" gives one end of a range; he invents the other and assumes the worst. Doesn't know if "quote" costs anything or commits him — won't click.

**Casey (distracted mobile):** 144px of chrome before content. Never sees a PC. Aims for the primary button and dials the phone. Three identically-labelled quote actions with no visual rank — the smallest (61px wide vs 215px for "Call") is the one permanently on screen.

**Riley (stress tester):** Mobile bar links are tab stops 16, 17, 18 of 18, after the footer — the always-visible "Quote" is the last thing a keyboard user reaches. `:focus-visible` orange and `.cta:hover` orange fill collide; a focused+hovered button loses its ring against its own background. Both hero interactives are properly focusable with 3px rings clearing 3:1.

## Minor Observations

- `.lead` at `1.06rem` computes to 16.96px — 0.04px smaller than the 17px body, because `rem` resolves against the 16px root.
- Hero photo uncaptioned while every gallery photo carries a CPU/GPU caption; the data is already in the alt text.
- Orange does four jobs: brand accent, focus ring, hover fill, headline emphasis.
- `sizes="(max-width: 860px) 100vw, 52vw"` but the CSS breakpoint is 980px — between 861-980px the browser under-fetches the LCP image.
- The headline's hard `<br>` pins the break at every width; any copy edit re-breaks it silently.
- The square logo reads ZAYD'S GAMING PCS — renders on any high-DPI screen, and "GAMING" narrows positioning to the kid when PRODUCT.md names the parent as purchaser.

## Questions to Consider

1. If you deleted the headline and led with "You get the itemized parts list and the receipt" — worse, or better? What is the pun buying that a fact wouldn't buy more?
2. The buyer is a parent; the photo is an RGB gaming rig in a living room. Whose room does that look like? Is the finished machine really the most persuasive frame you own?
3. PRODUCT.md says "a local human answers the phone." What changes if the hero says "I'm Zayd" instead of "we"?
4. Three ways to start a quote in the first mobile viewport. If you were allowed one, which survives?
