# Xiaohongshu article browser pagination rewrite

**Date:** 2026-06-28
**Status:** Approved
**Goal:** Replace the current estimate-first body pagination with browser-measured pagination so article slides render like book pages: no clipped text, no awkward previous-page endings, and stable continuation onto the next page.

## Problem

The article card renderer currently combines:

- `article_paginator.py`: Python-side height estimates and sentence/clause splitting
- `article_overflow.py`: Playwright passes that peel overflow and pull underfilled content
- `article.py`: final HTML rendering and continuation indentation

This two-stage model is fragile. The Python estimator does not fully match Chromium layout: font fallback, Chinese wrapping, text indent, letter spacing, flex sizing, and CSS gaps all affect the final screenshot. The later underfill pass can also move content forward after dangling-break cleanup has already run, reintroducing bad page endings.

The desired result is a page-turning reading flow:

- Previous pages should end at natural reading points whenever possible.
- Next pages may continue the same paragraph without first-line indentation.
- Body slides should never clip text at the bottom.
- Middle slides should be reasonably full, but not at the cost of bad breaks.

## Decision

Use Chromium as the source of truth for pagination. Python still parses article content, preserves source paragraph identity, and renders final HTML. Playwright decides whether a candidate page fits by rendering the same HTML/CSS used for screenshot output and measuring real overflow.

The stable path is:

1. Parse markdown into `ContentBlock`s with `kind` and `text`.
2. Assign stable pagination `source_id`s to the original block stream.
3. Expand content into candidate text units while preserving those `source_id`s.
4. Greedily add units to the current page.
5. After each addition, render the page in Chromium and check whether `.article-body-text` overflows.
6. If it fits, keep it.
7. If a whole block overflows the current non-empty page, try placing its leading sentence or clause on the current page before opening a new page.
8. If no natural leading piece fits, revert the last addition, open a new page, and continue.
9. If a single unit cannot fit on an empty page, split it more finely.
10. After pagination, run a small semantic cleanup for page endings, validating every move with Chromium.
11. Render final body slide HTML from the browser-measured pages.

## Scope

In scope:

- Add a browser-measured body paginator.
- Wire `render_article_slides()` to use it for article body pages.
- Preserve paragraph `source_id` so continuation indentation remains correct.
- Keep cover and end slide rendering unchanged.
- Keep existing output filenames and manifest behavior unchanged.
- Add tests for no clipping, text completeness, and page-ending quality.

Out of scope:

- Redesigning the slide visual style.
- Changing cover generation or CTA generation.
- Supporting inline images in body slides.
- Rewriting the Cursor Skill workflow.

## Architecture

### New module

Create `scripts/xhs/xhs_cards/article_browser_paginator.py`.

Primary API:

```python
def paginate_blocks_with_browser(
    blocks: list[ContentBlock],
    render_page_html: Callable[..., str],
    *,
    max_chars: int = 340,
) -> list[list[ContentBlock]]:
    ...
```

The function owns one Playwright Chromium page for the full pagination run. This avoids launching a browser for each probe while still using real rendering for every fit decision.

The parser currently returns `ContentBlock`s with the default `source_id=0`. The browser paginator must normalize the input before splitting by assigning each original block a stable, sequential `source_id`. Every derived sentence, clause, or character chunk inherits the `source_id` of its original block. This keeps paragraph continuation and same-source merging local to pagination, without making the parser responsible for pagination identity.

### Rendering probe

`article.py` already has `_render_body_page()` and a probe function shape for overflow correction. The browser paginator should reuse that pattern so fit checks use the final body slide CSS and markup.

The probe receives:

- candidate page blocks
- current page index
- current all-pages snapshot, when needed for continuation indentation
- a provisional total

The actual page number and total do not affect body text height, but passing them keeps the renderer contract close to final rendering.

### Measurement

Use Playwright to set page content, then evaluate:

```js
const textArea = document.querySelector('.slide-article .article-body-text');
return textArea.scrollHeight <= textArea.clientHeight + 1;
```

The same check should be used in tests to verify final slides.

## Pagination Rules

### Text units

Generate candidate units in this order:

1. Original blocks from the parser.
2. Long paragraph blocks split into sentences.
3. Sentences that still do not fit split into clauses.
4. Clauses that still do not fit split into bounded character chunks.

All derived units keep the original `kind` and `source_id`.

### Greedy fit

For each unit:

- Try appending it to the current page.
- If Chromium says it fits, keep it.
- If Chromium says it overflows:
  - If the current page has content and the unit can be split naturally, try the leading sentence, then leading clause, then bounded leading chunk on the current page.
  - If a leading piece fits, keep that piece on the current page and retry the remainder.
  - If no leading piece fits, start a new page and retry the unit.
  - If the current page is empty, split the unit into smaller units and retry.

This makes overflow prevention deterministic and removes the need for a separate peel-after-render pass in normal cases.

### Page endings

After initial browser pagination, perform a bounded cleanup pass:

- Non-final pages should not end with `，`, `,`, `、`, `；`, `;`, `：`, or `:`.
- Non-final pages should not leave extremely short fragments at the end.
- If a page ending is awkward, move the trailing clause or fragment to the next page.
- Every move must be followed by Chromium validation for both affected pages.
- If the move creates worse underfill or overflow, keep the original break.

The rule is best-effort. Never sacrifice no-clipping for a nicer ending.

### Fill behavior

Middle pages should be full enough to feel like book pages, but the paginator should not pull content forward purely to remove blank space after it has found a natural break. Stability and no clipping are more important than maximum fill density.

## Integration

`render_article_slides()` should change from:

1. `paginate_blocks()`
2. `balance_body_pages()`
3. `correct_body_page_overflows()`
4. `correct_body_page_underfills()`
5. merge blocks

to:

1. define the same `_render_probe_page()`
2. call `paginate_blocks_with_browser(article.blocks, _render_probe_page, max_chars=max_chars)`
3. merge adjacent same-source blocks
4. render final body pages

The old estimate-based modules may remain temporarily for existing tests or fallback. They should not be part of the default article render path once the browser paginator is wired in.

## Error Handling

- If Playwright or Chromium is unavailable, fail with a clear message explaining that article pagination requires Playwright Chromium.
- If a non-empty text unit cannot fit even after bounded character splitting, raise a descriptive error with the first part of the offending text.
- If final verification finds overflow, raise before screenshots are written.

## Testing

Add focused tests around the browser paginator:

- Text completeness: joining all output blocks equals the parser-normalized source stream, not the raw cleaned markdown body. The expected text should be `"".join(block.text for block in article.blocks)`, because the parser strips quote markers, removes blank paragraph separators, and normalizes block boundaries before pagination.
- No clipping: every rendered body slide has no `.article-body-text` overflow in Chromium.
- Continuation indentation: a page that continues the same paragraph renders the first paragraph with `article-p-continue`.
- Page ending quality: non-final pages do not end with dangling flow punctuation when the next page continues the same source paragraph.
- Regression article: the summary article that produced bad 06/07-style pages renders without clipping and without awkward previous-page endings.

Existing estimate paginator tests can stay while the old module exists, but new stability assertions should target the browser paginator and final `render_article_slides()` path.

## Acceptance Criteria

- Running the article render command produces ordered PNGs without bottom clipping.
- The previous-page endings in the problematic article are natural enough for book-style reading.
- The next page continues the same source paragraph without first-line indentation.
- All article text is preserved exactly after footer stripping.
- Cover and end slide behavior remain unchanged.
