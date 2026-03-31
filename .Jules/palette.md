## 2026-03-31 - Explicit aria-labels for Label-less Custom UI Designs
**Learning:** In custom UI templates (like Hyper-WIMP) where explicit HTML `<label>` elements are omitted for aesthetic or design purposes, screen readers lose necessary context for forms.
**Action:** Dynamically generated inputs must map template variables (like `data_item.prompt`) to the `aria-label` attribute to ensure accessibility.
