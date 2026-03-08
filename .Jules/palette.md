## 2024-05-18 - Maintaining Accessibility in Label-less Designs
**Learning:** In "Hyper-WIMP" or other custom UI templates where standard `<label>` elements are intentionally omitted for aesthetic or design purposes, screen reader accessibility can easily be compromised.
**Action:** When working with label-less design patterns, ensure dynamically generated inputs bind template variables (e.g., `data_item.prompt` or `query.prompt`) to the `aria-label` attribute to maintain accessibility.
