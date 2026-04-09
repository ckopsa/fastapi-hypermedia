## 2024-04-09 - Missing ARIA Labels on Inputs
**Learning:** The dynamic template (`future.html`) generates inputs and search text boxes without explicit ARIA labels. Because it intentionally avoids explicit HTML `<label>` elements for its minimalist UI, mapping `data_item.prompt` to `aria-label` is crucial for accessibility.
**Action:** Add `aria-label` mapped to `data_item.prompt` or similar descriptive text for dynamic inputs, and "Execute Command..." for the main HUD filter input.
