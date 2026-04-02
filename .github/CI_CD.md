# CI/CD Workflow Guide

## Automated Build and Release

This project uses GitHub Actions to automatically build Windows executables and create releases.

## Build Workflow

The `.github/workflows/build.yml` workflow:

1. **Triggers on:**
   - Push to `main` branch
   - Creation of version tags (e.g., `v1.0.0`)
   - Pull requests to `main`
   - Manual trigger (workflow_dispatch)

2. **Builds:**
   - Sets up Python 3.11
   - Installs dependencies from `requirements.txt`
   - Creates application icon
   - Builds standalone Windows executable with PyInstaller

3. **Artifacts:**
   - Uploads executable to GitHub for 30 days
   - Creates a Release with attached executable (for version tags)

## How to Create a Release

### Method 1: Using Git Tags (Recommended)

1. **Update version in code** (optional, for documentation):
   ```bash
   # Edit files that have version numbers if you want to track them
   # The app reads version from code at runtime
   ```

2. **Create and push a tag:**
   ```bash
   git tag -a v1.0.0 -m "Release v1.0.0: Initial release"
   git push origin v1.0.0
   ```

3. **The workflow automatically:**
   - Builds the executable
   - Creates a GitHub release
   - Attaches the executable and README

### Method 2: Manual Release on GitHub

1. Go to your repository
2. Click "Releases" → "Create a new release"
3. Enter tag name (e.g., `v1.0.0`)
4. Add release title and description
5. Attach the built executable manually from the artifact

## Accessing Built Artifacts

### During Development (Push/PR)
1. Go to your repository
2. Click "Actions" tab
3. Select the latest workflow run
4. Scroll to "Artifacts" section
5. Download `minecraft-server-manager-exe`

### Releases (Tagged Versions)
1. Go to your repository
2. Click "Releases" tab
3. Click on a release
4. Download the attached executable under "Assets"

## Version Tagging Convention

Use semantic versioning:
- `v1.0.0` — Major release
- `v1.0.1` — Bug fixes
- `v1.1.0` — New features
- `v2.0.0-alpha` — Pre-releases (optional)

Example:
```bash
git tag -a v1.1.0 -m "Add password management UI improvements"
git push origin v1.1.0
```

## Workflow Status Badge

Add to your README.md to show build status:

```markdown
![Build Status](https://github.com/YOUR_USERNAME/minecraft-server-manager/workflows/Build%20Executable/badge.svg)
```

## Troubleshooting

### Build Fails
- Check that all dependencies are in `requirements.txt`
- Ensure `build.spec` references correct files
- View logs in GitHub Actions tab

### Release Not Created
- Verify the tag follows `v*` pattern (e.g., `v1.0.0`)
- Check that workflow has permission to create releases
- Verify `GITHUB_TOKEN` secret is available (GitHub provides this automatically)

### Icon Missing
- `create_icon.py` uses PIL/Pillow (included in requirements.txt)
- If it fails, the build continues without custom icon
- Add your own `.ico` file to `assets/app_icon.ico` for custom branding

## Next Steps

1. Push your main branch
2. Create a version tag: `git tag -a v1.0.0 -m "Initial release"`
3. Push the tag: `git push origin v1.0.0`
4. Check GitHub Actions for build progress
5. Download from Releases when complete
