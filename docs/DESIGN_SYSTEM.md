# SparkCert design system — professional, accessible, animated

This is a design/engineering contract, not an instruction to invent simulated GPU data. The shipped interface is implemented in `web/index.html`, `web/styles.css`, and `web/app.js`; an animated architecture tour lives in `docs/ARCHITECTURE.html`.

## Brand and interaction character

- **Tone:** engineering-grade, premium, precise, private, calm, evidence-led.
- **Theme:** deep navy-charcoal, softly layered panels, jade/teal focus and success, muted blue-grey copy, amber warnings, rose errors.
- **Typeface:** Inter when available, platform system fallback. Avoid remote font/CDN dependencies in offline builds.
- **Sizing:** 250px main navigation on desktop; collapsible sidebar at small widths; content max width and generous breathing room.
- **Spacing:** consistent 4/8px cadence; cards with 14–18px radii; subtle 1px dividers; visual contrast between primary/secondary actions.
- **Hierarchy:** eyebrow -> strong section title -> clear text -> concise metadata -> meaningful action. Never bury scope limitations.
- **Iconography:** coherent lightweight outline SVG symbols; no emoji, no decorative stock photos or flashy gradients unrelated to content.

## Motion specification

| Interaction | Motion | Constraint |
| --- | --- | --- |
| Page swap | 220–380ms reveal with 5–9px lift | UI must work if animations are disabled |
| Cards/summary | 200ms entrance stagger | No number-count simulations presented as measurements |
| Navigation hover | 140–220ms background/translate | Must preserve layout and focus visibility |
| Primary button hover | Small elevation and glow | Never dim text below accessible contrast |
| Architecture links | Slow teal flow / moving dash | Illustrates *data path*, not live traffic |
| Modal | Quick gentle scale/reveal | Keyboard focus, Escape and overlay closure |
| Loading/progress | Spinner only while a real request is running | Do not show permanent loading or fake telemetry |
| Device state | Passive status indicator; pulse ONLY for real connected/active state | Avoid decorative 'green online' claims for unprobed hosts |

`@media (prefers-reduced-motion: reduce)` should disable/short-circuit all nonessential animation and smooth scrolling. Never use constant large-scale motion, flicker, autoplay sound, or inaccessible color-only distinctions.

## Pages and design goals

1. **Overview:** honest metrics, immediate primary actions, empty state with connection CTA, latest actual assessment. No fabricated GPU charts.
2. **Connections:** add/manual/import mode, available profiles, connection actions, clear distinction among saved profile vs connected health.
3. **AI Evaluations:** scope explanation, selectable/custom deterministic test cases, API target, explicit privacy disclosure, measured pass conditions.
4. **Evidence Reports:** actual saved run history, filter, inspect, PDF; clear assessment scope and measured time.
5. **System Architecture:** animated diagram explaining client/OpenSSH/host/evaluation boundaries with implementation status labels.
6. **Settings & Security:** transparent local-data model, SSH host verification, limits and caveats.

## Accessibility & QA requirements

- Semantic buttons, labels, role/status, visible focus ring, keyboard-only workflows, dialog focus management.
- No placeholder-only form instructions; errors should identify actionable correction.
- Color contrast: target WCAG AA for body and controls; test with real tooling before release.
- System respects OS reduced motion, 200–400% browser zoom, high-DPI Windows scaling, macOS accessibility settings.
- Narrow/mobile rendering is a convenience, **not** a claim of phone-native distribution.
- Avoid animations that falsely imply SSH login or GPU activity.

## Next visual engineering tasks

- Extract current compressed `web/styles.css` into maintained modules/components as the design expands, with linter and regression visuals.
- Replace one-shot full view rerenders with controlled focus retention for keyboard users.
- Add storybook-style design states or screenshot fixtures and automated Playwright tests.
- Add first-run onboarding, real connection state machine, accessible success/error logs, and cancelable operations.
- Provide real longitudinal charts only once time-series GPU telemetry exists; label sample/demo measurements explicitly.


## GitHub README visual language — 2026-10-25

- Treat \`assets/sparkcert-hero.svg\` as the canonical branded repository banner.
- Treat \`assets/sparkcert-workflow-animated.svg\` as an **illustrative workflow**, not a measured UI video.
- Treat \`assets/sparkcert-architecture.svg\` as an implementation-faithful visual; update when the actual trust boundaries or components change.
- Keep product claims consistent with \`docs/PROJECT_STATUS.md\` and \`docs/VERIFICATION.md\`; use explicit MVP labels and no invented live metrics.
- SVG animation is subtle, looping and CSS-only with \`prefers-reduced-motion\` fallback. Do not use remote trackers or external assets.
- Use descriptive \`alt\` text, internal navigation, legible typography, adequate contrast and mobile-friendly widths.
- When adding a **real** GIF/video in future, capture the actual working UI and label platform, test environment, and demo data source.
