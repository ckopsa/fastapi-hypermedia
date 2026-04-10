## 2024-04-10 - Dynamic ARIA Labels in Custom UIs

**Learning:** In custom UI templates like 'Hyper-WIMP' (`future.html`) where explicit HTML `<label>` elements are omitted for design purposes, dynamic inputs generated from JSON-based configuration (e.g., Collection+JSON `data` items) lack accessible names for screen readers. Since the placeholders might just serve as visual hints, they don't fulfill the role of a proper label.
**Action:** When working on UI structures that dynamically generate inputs and omit explicit `<label>` elements for layout/aesthetic reasons, ensure you add dynamic `aria-label` attributes to the input elements mapped from template variables (e.g., `data_item.prompt`) so they inherit the appropriate descriptive name.
