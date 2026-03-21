---
name: vibeflow-ship
description: Use after testing to prepare release artifacts and shipping output.
---

# Ship Stage for VibeFlow

Prepare the project for release. Create release artifacts and shipping output.

**Announce at start:** "I'm using the vibeflow-ship skill to prepare the release."

## Purpose

After review approval, prepare and execute the release:
- Version updates
- Release notes
- Release artifacts
- Deployment preparation

## Prerequisites

Before running this skill:
- All features marked `"status": "passing"` in `feature-list.json`
- Whole-change review passed (vibeflow-review)
- All tests passing
- Release notes drafted

## Step 1: Load Release Context

### 1.1 Read Feature List

From `feature-list.json`:
- All completed features (status: passing)
- Feature categories
- New features in this release

### 1.2 Read Task Progress

From `task-progress.md`:
- Session log summary
- Known issues
- Open questions

### 1.3 Read Release Notes Draft

From current `RELEASE_NOTES.md`:
- Drafted release notes
- Listed changes

### 1.4 Determine Version

Based on change type:
- **Major** (breaking changes): X.0.0
- **Minor** (new features): X.Y.0
- **Patch** (bug fixes): X.Y.Z

Check existing version in project files.

## Step 2: Update Version

### 2.1 Update Project Version Files

Update version in:
- `package.json` (Node.js)
- `pyproject.toml` / `__version__` (Python)
- `pom.xml` / `build.gradle` (Java)
- Other project-specific version files

### 2.2 Git Tag

Create git tag:
```bash
git tag -a v1.2.3 -m "Release v1.2.3"
git push origin v1.2.3
```

## Step 3: Finalize Release Notes

### 3.1 Review Draft Release Notes

Verify release notes include:
- All new features (with feature IDs)
- All bug fixes (with issue references)
- All breaking changes (prominently marked)
- Migration instructions (if needed)
- Known limitations

### 3.2 Format Release Notes

Use Keep a Changelog format:
```markdown
## [1.2.3] - YYYY-MM-DD

### Added
- Feature 1 (#1)
- Feature 2 (#2)

### Changed
- Improvement to existing feature

### Fixed
- Bug fix description

### Breaking
- Breaking change description
```

### 3.3 Update RELEASE_NOTES.md

Add new release section to `RELEASE_NOTES.md`.

## Step 4: Create Release Artifacts

### 4.1 Build Production Artifacts

```bash
# Node.js
npm run build
npm pack  # creates .tgz

# Python
python -m build
# or
pip wheel .

# Java
mvn clean package -DskipTests
```

### 4.2 Verify Artifacts

For each artifact:
- [ ] Artifact exists
- [ ] Artifact size reasonable
- [ ] No unexpected files included
- [ ] Version matches expected

### 4.3 Sign Artifacts (if applicable)

If project uses signing:
- Sign artifacts with project key
- Verify signatures

## Step 5: Prepare Deployment

### 5.1 Create Deployment Package

For deployment-ready projects:
- Bundle artifacts
- Include deployment scripts
- Include configuration templates
- Include rollback procedure

### 5.2 Document Deployment Steps

Create or update `DEPLOY.md`:
- Pre-deployment checklist
- Deployment steps
- Post-deployment verification
- Rollback procedure

## Step 6: Git Commit Release State

### 6.1 Stage Changes

Stage files:
- Updated version files
- Updated RELEASE_NOTES.md
- Any deployment artifacts

### 6.2 Commit

```bash
git add .
git commit -m "chore: prepare release v1.2.3"
```

### 6.3 Tag

```bash
git tag -a v1.2.3 -m "Release v1.2.3"
```

## Step 7: Verify Release

### 7.1 Pre-Release Checklist

- [ ] Version updated in all files
- [ ] Git tag created and pushed
- [ ] Release notes updated
- [ ] All tests passing
- [ ] Artifacts built and verified
- [ ] Deployment package ready (if applicable)
- [ ] No uncommitted changes

### 7.2 Smoke Test Release

Run smoke test against release artifacts:
```bash
# Install/package
# Start application
# Verify health endpoint
# Run critical path tests
```

### 7.3 Archive Session

Update `task-progress.md`:
- Mark release as prepared
- Record release version
- Record artifacts created

## Checklist

Before marking ship complete:

- [ ] Version updated in all project files
- [ ] Git tag created (v1.2.3)
- [ ] Release notes finalized
- [ ] Production artifacts built
- [ ] Artifacts verified
- [ ] Deployment package ready (if applicable)
- [ ] Pre-release checklist complete
- [ ] Smoke tests passed
- [ ] Git commit created
- [ ] Ready for deployment

## Outputs

| Artifact | Location |
|----------|----------|
| Release tag | Git repository |
| Release notes | `RELEASE_NOTES.md` |
| Production artifacts | Project-specific |
| Deployment package | `dist/` or release directory |

## Integration

**Called by:** `vibeflow` router (after review approved)
**Requires:**
- All features passing
- Review approved
- `RELEASE_NOTES.md` draft
- `feature-list.json`
- `task-progress.md`
**Produces:**
- Version update
- Git tag
- Finalized release notes
- Release artifacts
**Chains to:** `vibeflow-reflect` (after ship)
