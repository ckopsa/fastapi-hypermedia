## 2024-05-18 - Dynamic ARIA Labels in Custom UIs
**Learning:** In custom UIs (like the "Hyper-WIMP" HUD) where explicit HTML `<label>` elements are omitted for design purposes, `aria-label` attributes must be dynamically injected using template variables (e.g. `data_item.prompt`) to ensure inputs are accessible to screen readers.
**Action:** When creating form inputs that lack visual labels, always map the corresponding data prompt to the input's `aria-label` attribute.
