## 2024-03-24 - Accessibility in Custom UI Templates
**Learning:** In custom UI templates (like Hyper-WIMP) where explicit HTML `<label>` elements are omitted for design purposes, dynamically generated inputs must map template variables (e.g., `data_item.prompt`) to the `aria-label` attribute to ensure screen reader accessibility.
**Action:** Always add `aria-label` dynamically to form inputs and standalone buttons when labels are visually hidden or omitted in creative designs.
