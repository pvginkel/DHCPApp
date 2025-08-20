# Dark Mode Implementation Plan

## Brief Description

Implement automatic dark mode support for the DHCP monitoring application that follows the user's system preference. The implementation will leverage the existing CSS custom properties and Tailwind CSS configuration to automatically apply dark theme based on the `prefers-color-scheme` media query.

## Files and Functions to Create/Modify

### New Files
- `src/hooks/use-system-theme.ts` - Custom hook for system theme detection and application

### Modified Files
- `src/index.css` - Update dark mode animations to use CSS custom properties instead of hardcoded colors
- `src/routes/__root.tsx` - Add system theme detection logic to root component

## Step-by-Step Implementation

### 1. System Theme Detection Hook (`src/hooks/use-system-theme.ts`)
- Create a custom hook that detects system theme preference using `window.matchMedia('(prefers-color-scheme: dark)')`
- Listen for changes to system preference and update theme accordingly
- Apply theme class to `document.documentElement` when system preference changes
- Handle SSR considerations by checking for window availability
- Return current system theme state for components that need it

### 2. CSS Animation Updates (`src/index.css`)
- Update lease animation keyframes to use CSS custom properties instead of hardcoded colors
- Replace `theme('colors.green.50')` with `hsl(var(--accent))` or appropriate semantic colors
- Replace `theme('colors.blue.50')` with appropriate semantic colors for dark mode compatibility
- Replace `theme('colors.red.50')` with appropriate semantic colors for dark mode compatibility
- Ensure animations work correctly in both light and dark themes
- Maintain existing animation timing and easing

### 3. Root Component System Theme Integration (`src/routes/__root.tsx`)
- Add system theme detection on app startup to prevent flash of unstyled content
- Apply system preference by adding/removing 'dark' class on document.documentElement
- Ensure theme is applied before React renders the application
- Handle initial theme application for SSR compatibility

## Algorithm Details

### System Theme Detection and Application
1. On initial load, detect system preference using `prefers-color-scheme` media query
2. Apply theme by adding/removing 'dark' class on document.documentElement
3. Set up media query listener to detect system preference changes
4. Automatically update theme when system preference changes
5. Clean up event listeners on component unmount

### Theme Application Logic
1. Check if window and matchMedia are available (SSR safety)
2. Query `(prefers-color-scheme: dark)` media query
3. Apply 'dark' class to document.documentElement if dark preference detected
4. Listen for changes to media query and update class accordingly
5. Ensure smooth transitions between theme changes

## Implementation Phases

### Phase 1: Core System Theme Infrastructure
- Implement `use-system-theme.ts` hook with system preference detection
- Update root component to initialize theme based on system preference
- Test basic theme switching with system preference changes

### Phase 2: CSS Animation Updates
- Update CSS animations to work with both light and dark themes
- Replace hardcoded colors with CSS custom properties
- Test animation behavior in both theme modes

## Technical Considerations

- No localStorage needed since theme follows system preference exclusively
- Leverage existing Tailwind CSS custom properties defined in `index.css`  
- Follow functional programming patterns established in the codebase
- Maintain type safety with TypeScript throughout implementation
- Ensure proper cleanup of event listeners to prevent memory leaks
- Handle SSR considerations by checking for window availability
- Test system preference changes work correctly in different browsers