# Palette's Journal

## 2025-03-09 - Implementing ARIA for Custom Command Palette
**Learning:** Custom command palettes (like Hyper-WIMP) often lack semantic structure, making them invisible to screen readers. The "Combobox" pattern is the correct semantic model: an input (`role="combobox"`) controlling a list (`role="listbox"`) of options (`role="option"`). Managing `aria-activedescendant` via JavaScript is critical for telling the screen reader which option is "focused" while the actual DOM focus remains on the text input.
**Action:** When encountering custom "filter + list" interfaces, immediately check for `role="combobox"`. If missing, refactor to use the Combobox pattern, ensuring unique IDs for all options so `aria-activedescendant` can point to them.
