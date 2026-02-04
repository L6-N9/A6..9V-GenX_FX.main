## 2024-05-23 - Status Indicators
**Learning:** Pure color (red/green) status indicators are inaccessible to color-blind users. Adding shape-based indicators (icons) significantly improves clarity.
**Action:** Always pair status colors with semantic icons (Check/Alert/X) or text labels.

## 2024-05-24 - Semantic Lists
**Learning:** In a list of "success" items, a partial success or warning can be easily missed if it shares the same icon. Differentiating it with a distinct icon (warning vs check) improves scannability and honesty.
**Action:** When displaying lists of status items, ensure non-perfect states are visually distinct, even if they are technically "passed" but with caveats.

## 2024-05-25 - Screen Reader Context for Status Icons
**Learning:** Visual status icons (Check/Alert) paired with text descriptions often lack explicit status announcement for screen readers (e.g., reading "Configuration fixed" instead of "Success: Configuration fixed").
**Action:** Use `sr-only` prefix text (Success/Warning) alongside status icons to ensure the state is explicitly conveyed to non-visual users.

## 2024-05-26 - Action Feedback Latency
**Learning:** In critical financial actions (like payments), lack of immediate visual feedback during network latency causes anxiety and double-submissions. A simple spinner transforms "did it work?" into "it's working."
**Action:** Always include a disabled loading state with a spinner for primary form actions.

## 2024-05-27 - Mobile Form Usability
**Learning:** Standard text inputs for credit card details are frustrating on mobile devices and password managers. Users struggle with keyboard switching and lack of autofill.
**Action:** Use `inputMode="numeric"` for numerical data (card numbers, dates, CVC) and explicit `autoComplete` attributes (cc-number, cc-exp, cc-csc) to enable browser assistance and correct mobile keypads.

## 2024-05-28 - Skip Links for Keyboard Navigation
**Learning:** High-level navigation structures often block keyboard users from reaching main content quickly. A hidden "Skip to main content" link is essential for accessibility but often forgotten because it's invisible to mouse users.
**Action:** Always include a skip link as the first focusable element in the application root, pointing to a `<main>` landmark wrapping the primary route content.

## 2024-05-29 - Navigation Focus Visibility
**Learning:** Default browser focus outlines on navigation links are often suppressed or visually inconsistent with the design system, leading to a "lost" feeling for keyboard users navigating main menus.
**Action:** Explicitly implement `focus-visible` styles on navigation links that match the button focus styles (ring, offset) to create a cohesive and accessible keyboard navigation experience.
