# Here are your Instructions
Run npm run test or your project's test suite to check code health.Scan recent error logs or build outputs for broken audio stream APIs or missing dependencies
Fix broken imports, syntax errors, or outdated audio player packages flagged by your linter.Run npm audit fix or check for breaking changes in state-of-the-art radio/media streaming libraries
Stage verified changes using git add ..Commit using conventional commit format: git commit -m "fix(audio): update streaming dependency to latest state-of-the-art".Push safely to your remote branch: git push origin main

# Claude Code Automation Guide

## 1. Monitor App State
- Check running health: `npm run dev` or `npm start`
- Test audio stream endpoints: `npm test`
- Check for dependency alerts: `npm audit`
- Scan for syntax/style issues: `npm run lint`

## 2. Repair Code & Streams
- Install missing packages: `npm install`
- Fix security vulnerabilities: `npm audit fix`
- Fix linting problems: `npm run lint -- --fix`
- Debug instructions: "If a Radio API endpoint (Icecast/Shoutcast/Zeno) returns 404/503, verify the stream URL in `.env` and search for updated streaming endpoints."

## 3. Push State-of-the-Art Updates
- Stage all verified files: `git add .`
- Commit with standard prefix: `git commit -m "feat(radio): optimize stream handling and dependencies"`
- Deploy to GitHub remote: `git push origin main`
