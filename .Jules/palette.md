
## 2024-04-01 - Accessible Command Palette Template Variables
**Learning:** In highly customized interfaces like the 'Hyper-WIMP' command palette where standard HTML `<label>` elements are omitted for aesthetic reasons, dynamic inputs generated from JSON-driven templates lack context for screen readers.
**Action:** When designing template-driven UIs without explicit labels, always map the underlying data structure's prompt or name directly to the `aria-label` attribute (e.g. `aria-label="{{ data_item.prompt | default(data_item.name) }}"`) to ensure inputs remain accessible without compromising the design.
