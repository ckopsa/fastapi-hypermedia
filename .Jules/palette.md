## 2024-05-20 - Hyper-WIMP Command Palette Input Accessibility
**Learning:** In highly customized interfaces like the "Hyper-WIMP" command palette where `<label>` elements are intentionally omitted for design reasons, interactive inputs like `#hud-filter-input` rely entirely on placeholder text, which is not reliably read by all screen readers.
**Action:** Always ensure visually label-less inputs in dynamic overlay interfaces explicitly define an `aria-label` attribute describing their function.
