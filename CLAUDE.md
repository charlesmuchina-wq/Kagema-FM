# Here are your Instructions
Run npm run test or your project's test suite to check code health.Scan recent error logs or build outputs for broken audio stream APIs or missing dependencies
Fix broken imports, syntax errors, or outdated audio player packages flagged by your linter.Run npm audit fix or check for breaking changes in state-of-the-art radio/media streaming libraries
Stage verified changes using git add ..Commit using conventional commit format: git commit -m "fix(audio): update streaming dependency to latest state-of-the-art".Push safely to your remote branch: git push origin main

# Claude Code Automation Guide

## 1. Monitor App State
- Test Radio Browser API integration: `npm test`
- Check active stream health: `node scripts/test-streams.js`
- Audit dependency vulnerabilities: `npm audit`
- Lint code formatting: `npm run lint`

## 2. Repair Code & Streams
- Clean auto-fix dependencies: `npm audit fix`
- Resolve linting issues: `npm run lint -- --fix`
- Endpoint Troubleshooting: "If the Radio Browser API returns broken station URLs, execute `node scripts/refresh-stations.js` to query `de1.api.radio-browser.info` for working mirrors."

## 3. Push State-of-the-Art Updates
- Stage changes safely: `git add .`
- Commit with conventional semantic formatting: `git commit -m "fix(radio): update radio-browser stream resolution"`
- Push to GitHub remote: `git push origin main`
