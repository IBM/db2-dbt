# Release Guide for ibm-dbt-db2

This document provides step-by-step instructions for releasing the `ibm-dbt-db2` package to PyPI.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Release Methods](#release-methods)
- [Method 1: Tag-Based Release (Recommended)](#method-1-tag-based-release-recommended)
- [Method 2: Manual Workflow Dispatch](#method-2-manual-workflow-dispatch)
- [Environment Setup (One-Time)](#environment-setup-one-time)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Authorized Users
Only the following GitHub users can approve and publish releases:
- `shubhamkapoor992`
- `amitkumar293`

### Required Permissions
- Write access to the repository
- Approval rights for `pypi` and `test-pypi` environments

---

## Release Methods

### Method 1: Tag-Based Release (Recommended)

This is the **recommended approach** for production releases. The workflow automatically triggers when you push a version tag.

#### Step 1: Prepare Your Code
```bash
# Ensure you're on the main branch
git checkout main
git pull origin main

# Verify all tests pass locally
pytest tests/

# Update version in pyproject.toml if needed
# version = "1.0.17"
```

#### Step 2: Create and Push Version Tag
```bash
# Create a version tag (must start with 'v')
git tag v1.0.17

# Push the tag to GitHub
git push origin v1.0.17
```

#### Step 3: Workflow Auto-Triggers
- GitHub automatically detects the tag push
- Workflow starts immediately
- No manual action needed at this point

#### Step 4: Monitor Workflow Progress
1. Go to **GitHub Repository** → **Actions** tab
2. You'll see a new workflow run: "Build and Publish Release"
3. The workflow will:
   - ✅ Check authorization (verifies you're an authorized user)
   - ✅ Build the package
   - ✅ Run tests on multiple platforms (Ubuntu, macOS)
   - ✅ Test installation with Python 3.10 and 3.12
   - 🛑 **PAUSE** and wait for deployment approval

#### Step 5: Approve Deployment
1. Click on the running workflow
2. You'll see: **"Review pending deployments"**
3. Click **"Review deployments"** button
4. You'll see two environment options:
   - ☑️ **test-pypi** - For testing the release
   - ☑️ **pypi** - For production release

5. **For Testing (Recommended First):**
   - Select ☑️ `test-pypi`
   - Click **"Approve and deploy"**
   - Package publishes to https://test.pypi.org/p/ibm-dbt-db2

6. **For Production:**
   - Select ☑️ `pypi`
   - Click **"Approve and deploy"**
   - Package publishes to https://pypi.org/p/ibm-dbt-db2

#### Step 6: Verify Release
**For Test PyPI:**
```bash
# Install from Test PyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ ibm-dbt-db2

# Test the installation
python -c "from dbt.adapters.db2 import Db2Adapter; print('Success!')"
```

**For Production PyPI:**
```bash
# Install from PyPI
pip install ibm-dbt-db2

# Verify version
python -c "import dbt.adapters.db2; print(dbt.adapters.db2.__version__)"
```

---

### Method 2: Manual Workflow Dispatch

**When to use this method:**
- You want to re-release an existing tag without creating a new one
- You need to release from a branch other than main (e.g., hotfix branch)
- The automatic tag-based workflow failed and you want to retry
- You want to test the workflow without creating a tag
- You need to release an older version

**Note:** For normal releases, use Method 1 (Tag-Based). This method is for special cases.

#### Step 1: Navigate to Actions
1. Go to **GitHub Repository** → **Actions** tab
2. Select **"Build and Publish Release"** workflow
3. Click **"Run workflow"** button (top right)

#### Step 2: Configure Release
You'll see a form with three fields:

1. **Use workflow from:**
   - Select the branch to run the workflow from (usually `main`)

2. **Where to publish?**
   - Choose `test-pypi` for testing
   - Choose `pypi` for production

3. **Git ref (tag/branch) to release from:** (Optional)
   - Leave **empty** to release from current branch
   - Enter `v1.0.17` to release from a specific tag
   - Enter `main` to release from main branch

#### Step 3: Run Workflow
- Click **"Run workflow"** button
- Workflow starts immediately

#### Step 4: Approve Deployment
- Same as Method 1, Step 5
- Workflow will pause and wait for your approval
- Select environment and approve

---

## Environment Setup (One-Time)

This setup is required **once** per repository. Only repository administrators can configure environments.

### Step 1: Access Environment Settings
1. Go to **Repository Settings** → **Environments**
2. You should see or create two environments: `pypi` and `test-pypi`

### Step 2: Configure `pypi` Environment

#### A. Create Environment (if not exists)
- Click **"New environment"**
- Name: `pypi`
- Click **"Configure environment"**

#### B. Set Required Reviewers
- Under **"Deployment protection rules"**
- ✅ Enable **"Required reviewers"**
- Click **"Add reviewers"**
- Add: `shubhamkapoor992`
- Add: `amitkumar293`
- ✅ Enable **"Prevent self-review"** (optional)

#### C. Set Deployment Branches and Tags
- Under **"Deployment branches and tags"**
- Select **"Selected branches and tags"**
- Click **"Add deployment branch or tag rule"**
  - **Rule 1:** Enter `main` → Click "Add rule"
  - **Rule 2:** Enter `v*` → Click "Add rule"

#### D. Save
- Click **"Save protection rules"**

### Step 3: Configure `test-pypi` Environment
- Repeat all steps from Step 2
- Use environment name: `test-pypi`
- Same reviewers and branch rules

### Step 4: Verify Configuration
Both environments should show:
```
Required reviewers: shubhamkapoor992, amitkumar293
Deployment branches and tags:
  ✓ main
  ✓ v*
```

---

## Troubleshooting

### Issue: "User not authorized to release"
**Cause:** Your GitHub username is not in the authorized users list.

**Solution:** 
1. Check the workflow file: `.github/workflows/build_release.yaml`
2. Line 34 should contain your username in `AUTHORIZED_USERS`
3. If not, add your username and commit the change

### Issue: "Workflow doesn't trigger on tag push"
**Cause:** Tag doesn't match the pattern `v*`

**Solution:**
- Ensure tag starts with lowercase `v`
- Examples: `v1.0.0`, `v2.1.3`, `v1.0.0-beta`
- Invalid: `V1.0.0`, `1.0.0`, `release-1.0.0`

### Issue: "Cannot approve deployment"
**Cause:** You're not listed as a required reviewer in the environment.

**Solution:**
1. Go to **Settings** → **Environments** → `pypi` (or `test-pypi`)
2. Check if your username is in "Required reviewers"
3. If not, ask a repository admin to add you

### Issue: "Deployment blocked - branch not allowed"
**Cause:** Trying to deploy from a branch that's not in the allowed list.

**Solution:**
1. Only deploy from `main` branch or version tags (`v*`)
2. If deploying from a feature branch, merge to `main` first
3. Or update environment rules to allow your branch

### Issue: "Build fails during tests"
**Cause:** Code has failing tests or build errors.

**Solution:**
1. Run tests locally: `pytest tests/`
2. Fix any failing tests
3. Commit and push fixes
4. Create a new tag for the release

### Issue: "Package already exists on PyPI"
**Cause:** Version number already published.

**Solution:**
1. Update version in `pyproject.toml`
2. Create a new tag with the new version
3. Push and release again

---

## Best Practices

### 1. Always Test First
- Release to `test-pypi` first
- Install and test the package
- Only then release to production `pypi`

### 2. Version Numbering
Follow semantic versioning (semver):
- **Major** (v2.0.0): Breaking changes
- **Minor** (v1.1.0): New features, backward compatible
- **Patch** (v1.0.1): Bug fixes, backward compatible

### 3. Release Checklist
Before creating a release tag:
- [ ] All tests pass locally
- [ ] Version updated in `pyproject.toml`
- [ ] CHANGELOG updated (if applicable)
- [ ] Documentation updated
- [ ] Code reviewed and merged to `main`

### 4. Tag Naming Convention
- Use lowercase `v` prefix
- Follow semver: `v{major}.{minor}.{patch}`
- Examples: `v1.0.0`, `v1.2.3`, `v2.0.0`

### 5. Communication
- Announce releases in team channels
- Update release notes on GitHub
- Notify users of breaking changes

---

## Quick Reference

### Tag-Based Release (Quick)
```bash
git tag v1.0.17
git push origin v1.0.17
# Go to Actions → Review deployments → Select environment → Approve
```

### Manual Release (Quick)
```
Actions → Build and Publish Release → Run workflow
→ Select target → Run → Review deployments → Approve
```

### Test Installation
```bash
# Test PyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ ibm-dbt-db2

# Production PyPI
pip install ibm-dbt-db2
```

---

## Support

For issues or questions:
- Open an issue on GitHub
- Contact: `shubhamkapoor992` or `amitkumar293`
- Check workflow logs in Actions tab

---

**Last Updated:** 2026-05-18
**Package:** ibm-dbt-db2
**Repository:** https://github.com/IBM/db2-dbt