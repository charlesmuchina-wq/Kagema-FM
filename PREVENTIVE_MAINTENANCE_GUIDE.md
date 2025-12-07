# Preventive Maintenance Guide - Dragon KARAU AI Mobile App

## Overview
This guide outlines automated and manual preventative measures to ensure UI stability, consistent rendering, and robust mobile app development practices.

## 1. Design & Development Strategies

### ✅ Implemented in Current Codebase

#### Flexible Layouts
- **Current Implementation**: All feature tiles use responsive sizing
  ```typescript
  // components/FeatureTile.tsx
  const { width } = Dimensions.get('window');
  const tileWidth = (width - 60) / 2; // Dynamic sizing based on screen width
  ```
- **Best Practice**: Using `Dimensions` API and flexible containers (`flex: 1`)

#### Vector Graphics
- **Current Implementation**: Using `@expo/vector-icons` (Ionicons)
  ```typescript
  import { Ionicons } from '@expo/vector-icons';
  // Scalable vector icons that adapt to any screen density
  ```
- **Benefit**: Single asset file, no scaling artifacts, works across all densities

#### Typography System
- **Current Implementation**: Consistent font sizing with relative units
  ```typescript
  title: { fontSize: 16, fontWeight: '700' }
  tagline: { fontSize: 12, color: '#8B92B0' }
  ```
- **Best Practice**: Using sp-equivalent sizing for React Native

### 🔄 To Be Enhanced

#### Design Tokens System
- **Action Required**: Centralize all design values
- **Implementation**:
  ```typescript
  // constants/designTokens.ts
  export const DESIGN_TOKENS = {
    colors: { primary: '#FF6B35', secondary: '#1E88E5' },
    spacing: { xs: 4, sm: 8, md: 16, lg: 24, xl: 32 },
    typography: { title: 16, body: 14, caption: 12 },
    borderRadius: { sm: 8, md: 16, lg: 20 }
  }
  ```

#### Multi-Density Asset Strategy
- **Current**: Vector icons (✅)
- **Action**: For bitmap images (logos, photos), provide @2x, @3x variants
- **Structure**:
  ```
  assets/
    ├── images/
    │   ├── logo.png      (1x - mdpi)
    │   ├── logo@2x.png   (2x - xhdpi)
    │   └── logo@3x.png   (3x - xxhdpi)
  ```

## 2. Testing & Validation Procedures

### Automated Testing Checklist

#### Device Testing Matrix
- [ ] iOS: iPhone SE (small), iPhone 14 (medium), iPhone 14 Pro Max (large)
- [ ] Android: Pixel 4 (360x800), Galaxy S21 (360x800), Tablet (800x1280)
- [ ] Web: Desktop (1920x1080), Tablet (768x1024), Mobile (375x667)

#### Pre-Deployment Validation
```bash
# Run before each deployment
npm run test                    # Unit tests
npm run lint                    # Code quality
expo doctor                     # Expo config validation
npm run test:visual             # Screenshot regression tests
```

### Manual UI Audit Schedule
- **Weekly**: Quick visual check on 3 primary screens (home, favorites, settings)
- **Monthly**: Comprehensive audit of all screens
- **Per Release**: Full device matrix testing

### Performance Monitoring
```typescript
// Implement performance tracking
import { Performance } from 'expo-performance';

Performance.mark('screen-render-start');
// ... render logic
Performance.mark('screen-render-end');
Performance.measure('screen-render', 'screen-render-start', 'screen-render-end');
```

## 3. Service Health Monitoring

### Automated Health Checks

#### Service Status Monitoring
```bash
#!/bin/bash
# scripts/health_check.sh
# Run every 5 minutes via cron

STATUS=$(supervisorctl status expo backend | grep -v RUNNING)
if [ ! -z "$STATUS" ]; then
    echo "Service down detected: $STATUS"
    supervisorctl restart expo backend
    # Send alert to monitoring system
fi
```

#### Frontend Build Validation
```json
// package.json
{
  "scripts": {
    "prebuild": "npm run lint && npm run type-check",
    "build": "expo export:web",
    "postbuild": "npm run test:build"
  }
}
```

### Error Tracking Integration
```typescript
// app/_layout.tsx - Add error boundary
import * as Sentry from '@sentry/react-native';

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  enableAutoSessionTracking: true,
  tracesSampleRate: 1.0,
});
```

## 4. Configuration Stability

### Protected Configuration Files
**Never modify these without explicit reason:**
- `metro.config.js` - Bundler configuration
- `app.json` - Expo configuration
- `.env` files - Environment variables
- `package.json` main field

### Configuration Validation Script
```typescript
// scripts/validate-config.ts
import { readFileSync } from 'fs';

const requiredEnvVars = [
  'EXPO_PUBLIC_BACKEND_URL',
  'EXPO_PACKAGER_PROXY_URL',
  'EXPO_PACKAGER_HOSTNAME'
];

const validateConfig = () => {
  const env = readFileSync('.env', 'utf8');
  requiredEnvVars.forEach(varName => {
    if (!env.includes(varName)) {
      throw new Error(`Missing required env var: ${varName}`);
    }
  });
  console.log('✅ Configuration validated');
};

validateConfig();
```

## 5. Continuous Improvement Procedures

### User Feedback Loop
1. **Collection**: In-app feedback form, app store reviews, analytics
2. **Analysis**: Weekly review of UI-related issues
3. **Prioritization**: Tag issues as "ui-bug", "ui-enhancement", "accessibility"
4. **Implementation**: Address in sprint planning

### Regular Dependency Updates
```bash
# Monthly maintenance routine
npm outdated                    # Check for updates
expo upgrade                    # Upgrade Expo SDK
npm audit fix                   # Security patches
npm run test                    # Verify nothing broke
```

### Design System Documentation
- Maintain living style guide with Storybook or similar
- Document all components with usage examples
- Include accessibility guidelines
- Version control design decisions

## 6. Incident Response Playbook

### Issue: Icons/UI Elements Not Rendering

**Diagnosis Steps:**
1. Check service status: `supervisorctl status`
2. Check browser console for errors
3. Verify font loading in network tab
4. Check metro bundler logs: `supervisorctl tail expo`

**Common Fixes:**
1. Restart services: `supervisorctl restart expo backend`
2. Clear metro cache: `cd frontend && npx expo start -c`
3. Verify font configuration in `_layout.tsx`
4. Check `metro.config.js` has font extensions: `['ttf', 'otf']`

### Issue: Blank Screen / 502 Error

**Diagnosis Steps:**
1. Check all services running: `supervisorctl status`
2. Check port availability: `netstat -tulpn | grep :3000`
3. Check environment variables loaded correctly

**Common Fixes:**
1. Restart all services: `supervisorctl restart all`
2. Verify `.env` files not corrupted
3. Check backend API is responding: `curl localhost:8001/api/`

## 7. Automated Checks to Implement

### Pre-commit Hooks
```json
// .husky/pre-commit
#!/bin/sh
npm run lint-staged
npm run type-check
```

### CI/CD Pipeline Checks
```yaml
# .github/workflows/quality-check.yml
name: Quality Check
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Lint Code
        run: npm run lint
      - name: Type Check
        run: npm run type-check
      - name: Run Tests
        run: npm run test
      - name: Build Check
        run: expo export:web
```

### Accessibility Validation
```typescript
// Add to test suite
import { render } from '@testing-library/react-native';
import { axe, toHaveNoViolations } from 'jest-axe';

expect.extend(toHaveNoViolations);

test('FeatureTile is accessible', async () => {
  const { container } = render(<FeatureTile {...props} />);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
```

## 8. Performance Benchmarks

### Target Metrics
- **Time to Interactive**: < 3 seconds
- **Icon Render Time**: < 100ms per icon
- **Screen Transition**: < 300ms
- **Memory Usage**: < 150MB on average device
- **Bundle Size**: < 5MB for web builds

### Monitoring Script
```typescript
// utils/performanceMonitor.ts
export const monitorPerformance = () => {
  const metrics = {
    renderTime: performance.now(),
    memoryUsage: (performance as any).memory?.usedJSHeapSize,
    screenTransitions: 0
  };
  
  // Log to analytics
  console.log('Performance Metrics:', metrics);
  return metrics;
};
```

## 9. Version Control Best Practices

### Branching Strategy
- `main` - Production-ready code
- `develop` - Integration branch
- `feature/*` - Feature development
- `fix/*` - Bug fixes
- `maintenance/*` - Technical debt & refactoring

### Commit Message Format
```
type(scope): subject

[optional body]
[optional footer]

Types: feat, fix, docs, style, refactor, test, chore
Example: fix(icons): add font preloading for web platform
```

## 10. Documentation Requirements

### Component Documentation
Every component should include:
- Purpose and usage
- Props interface with types
- Code examples
- Accessibility considerations
- Known issues/limitations

### Change Log
Maintain `CHANGELOG.md` with:
- Version numbers (semantic versioning)
- Date of release
- Added, Changed, Fixed, Removed sections
- Migration guides for breaking changes

## Summary

This preventive maintenance guide should be:
- ✅ Reviewed monthly by the development team
- ✅ Updated when new issues are discovered
- ✅ Integrated into onboarding for new developers
- ✅ Referenced during sprint planning
- ✅ Used as basis for automated tooling development

**Last Updated**: December 2024
**Next Review**: January 2025
