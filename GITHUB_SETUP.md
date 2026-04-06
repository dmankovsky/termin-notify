# GitHub Repository Setup Guide

## Option 1: Using GitHub CLI (Recommended)

### Install GitHub CLI (if not installed)

**macOS:**
```bash
brew install gh
```

**Login to GitHub:**
```bash
gh auth login
```

### Create Repository and Push

```bash
# Create repository (public or private)
gh repo create dmankovsky/termin-notify --public --source=. --remote=origin

# Push code
git push -u origin master

# Open repository in browser
gh repo view --web
```

---

## Option 2: Using GitHub Web Interface

### Step 1: Create Repository on GitHub

1. Go to https://github.com/dmankovsky
2. Click "+" → "New repository"
3. Settings:
   - **Repository name**: `termin-notify`
   - **Description**: `Automated appointment notification service for German government offices (Bürgeramt, Ausländerbehörde, KFZ-Zulassung)`
   - **Visibility**: Public (or Private if you prefer)
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
4. Click "Create repository"

### Step 2: Push Local Code

GitHub will show you commands. Use these:

```bash
git remote add origin https://github.com/dmankovsky/termin-notify.git
git branch -M main  # Rename master to main (GitHub standard)
git push -u origin main
```

### Step 3: Verify

Visit https://github.com/dmankovsky/termin-notify to see your repository!

---

## Option 3: Using SSH (More Secure)

### Step 1: Check for SSH Key

```bash
ls -al ~/.ssh
```

If you see `id_ed25519.pub` or `id_rsa.pub`, you have a key.

### Step 2: Generate SSH Key (if needed)

```bash
ssh-keygen -t ed25519 -C "your-email@example.com"
```

Press Enter to accept defaults.

### Step 3: Add SSH Key to GitHub

```bash
# Copy SSH key to clipboard
cat ~/.ssh/id_ed25519.pub | pbcopy  # macOS
# or manually copy the output
```

1. Go to GitHub → Settings → SSH and GPG keys
2. Click "New SSH key"
3. Paste your key and save

### Step 4: Create Repository and Push

```bash
# Create repository on GitHub (via web interface)
# Then:
git remote add origin git@github.com:dmankovsky/termin-notify.git
git branch -M main
git push -u origin main
```

---

## Repository Settings (After Creation)

### 1. Add Topics

Go to repository → Settings → Topics:
- `germany`
- `appointments`
- `burgeramt`
- `notification-service`
- `fastapi`
- `python`
- `saas`
- `automation`

### 2. Update Repository Description

Short description:
```
🇩🇪 Automated appointment notification service for German government offices - Never miss a Bürgeramt, Ausländerbehörde, or KFZ appointment again!
```

### 3. Add Website URL

```
https://termin-notify.de
```

### 4. Enable Discussions (Optional)

Settings → Features → Check "Discussions"

This allows users to ask questions and discuss features.

### 5. Create GitHub Pages (Optional)

Settings → Pages → Source: Deploy from branch `main`, folder `/docs`

(You'd need to create a docs folder first)

---

## Protecting Sensitive Data

### Before Pushing

Double-check `.gitignore` includes:
- `.env` ✅ (already included)
- `*.db` ✅
- `__pycache__` ✅
- Credentials ✅

### If You Accidentally Committed Secrets

```bash
# Remove file from git history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# Force push
git push origin --force --all
```

⚠️ **Better**: Use `git-secrets` or `detect-secrets` to prevent this.

---

## Creating Releases

### Tag a Version

```bash
git tag -a v1.0.0 -m "Release v1.0.0 - MVP Launch"
git push origin v1.0.0
```

### Create Release on GitHub

1. Go to repository → Releases
2. Click "Create a new release"
3. Choose tag: v1.0.0
4. Title: "v1.0.0 - Production MVP"
5. Description:
```markdown
## 🎉 Initial Release - Production MVP

### Features
- ✅ Multi-city appointment monitoring (Berlin, Munich, Hamburg, Frankfurt)
- ✅ Email notification system
- ✅ User authentication & subscription management
- ✅ RESTful API
- ✅ Docker deployment
- ✅ Comprehensive documentation (EN + DE)

### Installation
See [QUICKSTART.md](QUICKSTART.md) for installation instructions.

### Documentation
- [English](README_EN.md)
- [Deutsch](README_DE.md)

### Support
Email: support@termin-notify.de
```

---

## GitHub Actions (CI/CD) - Optional

Create `.github/workflows/tests.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    - name: Run tests
      run: pytest --cov=app tests/
```

---

## README Badges (Optional but Cool)

Add to top of README.md:

```markdown
![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)
![License](https://img.shields.io/badge/license-Proprietary-red.svg)
![Status](https://img.shields.io/badge/status-Production-green.svg)
![Made in Germany](https://img.shields.io/badge/made%20in-Germany%20🇩🇪-black.svg)
```

---

## Next Steps After Pushing

1. ✅ Repository created and code pushed
2. ⏳ Configure repository settings
3. ⏳ Add topics and description
4. ⏳ Create v1.0.0 release
5. ⏳ Share on social media
6. ⏳ Submit to directories (Product Hunt, etc.)

---

## Troubleshooting

### "Permission denied (publickey)"

Generate and add SSH key (see Option 3 above).

### "Repository not found"

Check:
- Repository name is correct
- You have access rights
- Using correct GitHub username

### "Large files detected"

If you accidentally committed large files:
```bash
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch path/to/large/file" \
  --prune-empty --tag-name-filter cat -- --all
```

Or use Git LFS for large files.

---

## Useful Commands

```bash
# View remote
git remote -v

# Change remote URL
git remote set-url origin NEW_URL

# View commit history
git log --oneline

# Create and switch to new branch
git checkout -b feature-name

# Push new branch
git push -u origin feature-name
```

---

**Ready to share your project with the world!** 🚀
