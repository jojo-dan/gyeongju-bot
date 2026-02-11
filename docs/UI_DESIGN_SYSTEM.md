# UI/UX Design System

## Design Reference

All UI design references are stored in `/ref-image/`.

## Core Design Principles

- **Hardware Skeuomorphism**: UI should feel like a premium physical device (Braun/Dieter Rams)
- **Dot-Matrix LED Display**: Primary data readouts use pixel/monospace font on dark backgrounds
- **Warm Neutral Palette**: Base is light gray (#E5E5E5), device housing is white with soft shadows
- **Accent Color**: Orange (#E85D2A) for active indicators only -- use very sparingly
- **Control Metaphors**: Buttons look like physical toggles (embossed), sliders look like VU meters
- **Typography Split**: Serif (Didone family) for hero headlines, monospace/pixel font for device UI
- **Color Swatches**: Muted palette -- cream, olive, lavender, charcoal, white
- **Active State**: Black fill with white text. Inactive: white/light fill with dark text
- **Minimal Color**: Almost monochrome. Color only appears in swatches and the orange accent

## Component Patterns

1. **Device Card**: White rounded container with dark screen area + control buttons below
2. **Settings Panel**: White card with labeled sections in SMALL CAPS monospace
3. **Toggle Group**: Row of 2-3 buttons, one black (active), rest white (inactive)
4. **Level Meter**: Horizontal bar with fine tick marks and orange position indicator
5. **Circular Knob**: Small volume-style control with label below
6. **Status Badge**: Small colored text (e.g., green "ACTIVATED", orange "RE/DY")

## Reference Images

- **takt1.png**: Main player interface, device housing, LED display, controls
- **takt2.png**: Settings/maintenance panel, color swatches, toggle groups
- **takt3.png**: Full composition with timer + settings side by side, pricing/access layout
