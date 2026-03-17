## 2024-03-17 - Add ARIA Labels to Highly Stylized UIs
**Learning:** Highly stylized user interfaces (like Hyper-WIMP) that intentionally omit explicit HTML `<label>` elements for aesthetic purposes often become inaccessible to screen readers.
**Action:** Always map template variables (e.g., `data_item.prompt` or `query.prompt`) and static hints to `aria-label` attributes for form inputs and icon-only interactive elements in such designs to ensure a baseline of screen reader accessibility without compromising the aesthetic.
