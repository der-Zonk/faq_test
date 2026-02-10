# Branch Protection Setup

This document explains how to configure GitHub branch protection to block merges when validation fails.

## Steps to Enable Branch Protection

### 1. Go to Repository Settings
1. Navigate to your repository on GitHub: `https://github.com/der-Zonk/faq_test`
2. Click on **Settings** (top menu)
3. In the left sidebar, click **Branches** (under "Code and automation")

### 2. Add Branch Protection Rule
1. Click **Add rule** or **Add branch protection rule**
2. In **Branch name pattern**, enter: `main`

### 3. Configure Protection Settings

#### Required Status Checks ✅
- ✅ Check: **Require status checks to pass before merging**
- ✅ Check: **Require branches to be up to date before merging**
- In the search box, find and select:
  - `validate-faq` (from the PR Validation workflow)
  - `validate` (from the Build Index workflow)

#### Pull Request Requirements
- ✅ Check: **Require a pull request before merging**
- Optional: Set **Required number of approvals** (e.g., 1 reviewer)
- ✅ Check: **Dismiss stale pull request approvals when new commits are pushed**

#### Additional Settings (Optional)
- ✅ Check: **Require conversation resolution before merging** (good practice)
- ✅ Check: **Do not allow bypassing the above settings** (enforces rules for everyone)
- ⚠️ **Allow force pushes**: Leave unchecked
- ⚠️ **Allow deletions**: Leave unchecked

### 4. Save Changes
1. Scroll down and click **Create** or **Save changes**

## What This Does

### ✅ Blocked Actions
- Pull requests **cannot be merged** if validation fails
- Direct pushes to `main` are blocked (must use PRs)
- Force pushes to `main` are prevented

### ✅ Required Actions
- All FAQ entries must pass validation
- PRs must be approved (if you set required reviewers)
- Status checks must pass before merge button is enabled

## Testing the Protection

### Test 1: Create a PR with invalid FAQ
1. Create a new branch: `git checkout -b test-validation`
2. Create an invalid FAQ file (e.g., missing `answer` field)
3. Commit and push: `git push origin test-validation`
4. Open a Pull Request on GitHub
5. **Expected**: The PR validation check should fail and merge is blocked

### Test 2: Fix and verify
1. Fix the validation errors
2. Commit and push again
3. **Expected**: The PR validation check passes and merge is allowed

## Workflow Files

Two workflows validate PRs:

1. **pr-validation.yml**: Runs `validate_faq.py` on every PR
2. **build-index.yml**: Also validates on push to main and PRs

## Troubleshooting

### "No status checks found"
- Wait for a PR to be created and the workflow to run at least once
- GitHub needs to see the workflow run before it appears in the list

### Validation not running
- Check that PR modifies files in `data/faq/**`
- Check workflow syntax: `.github/workflows/pr-validation.yml`
- View workflow runs: `Actions` tab on GitHub

### Bypass protection (Emergency)
If you need to merge despite failed checks:
1. Go to Settings → Branches → Edit rule
2. Temporarily uncheck "Require status checks to pass"
3. Merge the PR
4. **Important**: Re-enable the protection immediately after!

## Alternative: Require Reviews

Instead of (or in addition to) status checks, you can require manual approval:
1. In branch protection settings
2. Check "Require a pull request before merging"
3. Set "Required number of approvals before merging" to 1 or more
4. This means a human must review and approve every change

## Summary

✅ **Validation workflow created**: `.github/workflows/pr-validation.yml`  
✅ **Validator checks**: question, answer, category, no duplicates  
⚠️ **Action required**: Set up branch protection in GitHub UI (steps above)

Once configured, **no PR can be merged if FAQ validation fails**! 🛡️
