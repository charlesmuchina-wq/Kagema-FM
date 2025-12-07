# Pull Request

## Description
<!-- Provide a brief description of the changes in this PR -->

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Refactoring (no functional changes)
- [ ] Performance improvement

## Design Token Compliance Checklist
- [ ] I have used `DESIGN_TOKENS` for all colors (no hardcoded hex values)
- [ ] I have used `DESIGN_TOKENS.spacing` for padding/margin (no magic numbers)
- [ ] I have used `DESIGN_TOKENS.typography` for font sizes and weights
- [ ] I have used `DESIGN_TOKENS.borderRadius` for rounded corners
- [ ] If I added new design values, I added them to `designTokens.ts` first

## Testing Checklist
- [ ] I have tested this on web preview
- [ ] I have tested this on iOS (simulator or device)
- [ ] I have tested this on Android (simulator or device)
- [ ] All existing tests pass
- [ ] I have added new tests for new functionality

## Configuration Changes
- [ ] No configuration files were modified
- [ ] If config files were modified, I have documented the reason and validated with `/app/scripts/validate_config.sh`

## Code Quality Checklist
- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] My changes generate no new warnings
- [ ] I have run the linter and fixed all issues

## Documentation
- [ ] I have updated relevant documentation
- [ ] I have added/updated code comments where necessary
- [ ] I have updated the CHANGELOG.md (if applicable)

## Screenshots (if applicable)
<!-- Add screenshots to demonstrate the changes -->

### Before
<!-- Screenshot before changes -->

### After
<!-- Screenshot after changes -->

## Additional Notes
<!-- Any additional information that reviewers should know -->

## Related Issues
<!-- Link to related issues, e.g., Closes #123 -->

---

**Reviewer Guidelines:**
1. ✅ Verify design tokens are used consistently
2. ✅ Check for no hardcoded colors or spacing values
3. ✅ Ensure configuration files are not unnecessarily modified
4. ✅ Validate that the PR doesn't break existing functionality
5. ✅ Confirm adequate testing has been performed
