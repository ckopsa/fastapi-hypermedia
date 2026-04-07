## 2024-04-07 - Accessibility in Label-less Custom UI Designs
**Learning:** Highly customized UI designs (like command palettes or HUDs) often omit explicit HTML `<label>` elements for aesthetic reasons. However, dynamically generated input fields in these interfaces become completely opaque to screen readers without them.
**Action:** Always map template variables (like `data_item.prompt` or fallback to `data_item.name`) directly to the `aria-label` attribute on inputs/textareas to maintain a11y without compromising the visual design constraints.
