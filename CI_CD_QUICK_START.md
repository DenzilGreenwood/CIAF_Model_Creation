# 🚀 CI/CD QUICK START GUIDE

**Last Updated**: 2026-03-15
**Status**: Ready for activation

---

## ⚡ 5-Minute Setup

### Step 1: Add GitHub Secrets (2 minutes)
Go to: **Settings → Secrets and variables → Actions**

Add these secrets (minimum required):
```
DOCKER_HUB_USERNAME      # Your Docker Hub username
DOCKER_HUB_TOKEN         # Your Docker Hub token
SLACK_WEBHOOK            # Your Slack webhook URL (optional but recommended)
```

Optional (for production deployment):
```
AWS_ACCESS_KEY_ID        # For AWS deployments
AWS_SECRET_ACCESS_KEY    # For AWS deployments
PYPI_TOKEN               # For PyPI package publishing
```

### Step 2: Configure Branch Protection (2 minutes)
Go to: **Settings → Branches → main**

Enable these options:
- ✅ Require status checks to pass before merging
- ✅ Require reviews

### Step 3: Configure Codecov (optional, 1 minute)
1. Go to https://codecov.io
2. Login with GitHub
3. Set up coverage tracking
4. GitHub Actions will auto-comment on PRs

**That's it!** 🎉 CI/CD is now active

---

## 📋 AVAILABLE WORKFLOWS

### 1. Backend Tests (`backend-tests.yml`)
**Trigger**: On push/PR to main/develop when `ciaf/` or `tests/` changes
**Duration**: 5-10 minutes
**Runs**:
- ✅ Python 3.9, 3.10, 3.11 tests
- ✅ PostgreSQL + Redis services
- ✅ Security scanning (Bandit)
- ✅ Dependency checks (Safety)
- ✅ Coverage reporting (Codecov)

```bash
# View results
- Go to Actions tab
- Click "Backend Tests & Security Scanning"
- View latest run
```

### 2. Frontend Tests (`frontend-tests.yml`)
**Trigger**: On push/PR when `frontend/` changes
**Duration**: 3-5 minutes
**Runs**:
- ✅ Node 18, 20 tests
- ✅ ESLint (code quality)
- ✅ Prettier (formatting)
- ✅ TypeScript (type checking)
- ✅ Vitest (unit tests)

```bash
# View results
- Go to Actions tab
- Click "Frontend Tests & Linting"
- Check build artifacts
```

### 3. Security Scanning (`security-scanning.yml`)
**Trigger**: On push, PR, + daily at 2 AM UTC
**Duration**: 15-20 minutes
**Runs**:
- ✅ CodeQL security analysis (Python + TypeScript)
- ✅ Bandit (Python-specific)
- ✅ Dependency vulnerabilities
- ✅ SARIF report generation

```bash
# View security findings
- Go to Security tab
- Click "Code scanning"
- Review alerts
```

### 4. Staging Deployment (`deploy.yml`)
**Trigger**: On push to main branch only
**Duration**: 10-15 minutes
**Deploys To**: Staging environment

```bash
# View deployment status
- Go to Actions tab
- Click "Build & Deploy"
- Check deployment logs
```

### 5. Release Management (`release.yml`)
**Trigger**: GitHub Release published or manual
**Duration**: 5-10 minutes
**Actions**:
- ✅ Version bump (pyproject.toml, package.json)
- ✅ Changelog update
- ✅ PyPI package publish
- ✅ GitHub Release creation
- ✅ Docker image push

```bash
# Create a release
1. Go to Releases
2. Click "Create a new release"
3. Enter version (v1.2.3)
4. Workflow runs automatically
```

### 6. Dependency Updates (`dependencies.yml`)
**Trigger**: Weekly (Mondays 9 AM UTC)
**Duration**: 5-10 minutes
**Actions**:
- ✅ Check for outdated packages
- ✅ Create PRs with updates
- ✅ Run security audits
- ✅ Auto-label for filtering

```bash
# View dependency PRs
- Go to Pull Requests
- Filter by label: "dependencies"
- Review and merge
```

---

## 🎯 TYPICAL WORKFLOW

### For Feature Development
```
1. Create feature branch
   git checkout -b feature/my-feature

2. Make changes to code

3. Push to GitHub
   git push origin feature/my-feature

4. Create Pull Request
   - Workflows automatically run
   - Tests must pass
   - Status checks green

5. Request review & merge
   - GitHub Actions comment added
   - Coverage changes shown
   - Security scan clean
```

### For Production Release
```
1. Update version
   - Manually update or let release workflow handle

2. Update CHANGELOG
   - Add release notes

3. Create GitHub Release
   - Tag: v1.2.3
   - Release: published

4. Workflow runs:
   - Version bump
   - PyPI publish
   - Docker image push
   - Slack notification
```

---

## 📊 MONITORING & TROUBLESHOOTING

### Check Workflow Runs
```bash
# In GitHub UI:
- Actions tab
- Select workflow
- View logs for specific job
- Download artifacts

# Via GitHub CLI:
gh workflow list
gh run list -w backend-tests
gh run view <run-id> -v
```

### Common Issues

**Tests failing locally but passing in CI?**
- Check Python/Node version match
- Verify environment variables before running
- Use same commands as CI (pytest, npm test)

**Coverage lower than expected?**
- Coverage only includes tested files
- Missing test files not counted
- Aim for 80%+ on changed files

**Security findings in CodeQL?**
- High/critical: Address before merging
- Medium: Review and decide
- Low: Can be ignored if intentional

**Deployment failed to staging?**
- Check AWS credentials in secrets
- Verify staging environment running
- Review deployment logs

---

## 🔧 ADVANCED: Customizing Workflows

### Adjust Python Versions
Edit `.github/workflows/backend-tests.yml`:
```yaml
python-version: ['3.9', '3.10', '3.11', '3.12']  # Add 3.12
```

### Adjust Node Versions
Edit `.github/workflows/frontend-tests.yml`:
```yaml
node-version: ['16.x', '18.x', '20.x']  # Add 16.x
```

### Change Schedule
Edit `.github/workflows/dependencies.yml`:
```yaml
schedule:
  - cron: '0 0 * * 0'  # Weekly Sunday instead of Monday
```

### Add More Security Checks
Add to `.github/workflows/security-scanning.yml`:
```yaml
- name: Run custom security check
  run: your-custom-security-tool
```

---

## 📈 EXPECTED RESULTS

### After First Push
- ✅ Backend tests run (1st time: ~10 min, cache improves)
- ✅ Frontend tests run
- ✅ Coverage reported to Codecov
- ✅ Security scan initiated
- ⏳ PR gets status check badge

### After PR Review
- ✅ All status checks should be green
- ✅ Coverage change shown in PR
- ✅ Security findings listed in PR
- ✅ Ready to merge

### After Main Branch Merge
- ✅ Staging deployment starts automatically
- ✅ Health checks run
- ✅ Slack notification sent
- ✅ Staging environment updated

### After Creating Release
- ✅ Version bump committed
- ✅ CHANGELOG updated
- ✅ Package published to PyPI
- ✅ Docker image pushed
- ✅ Release notes on GitHub

---

## 🎓 BEST PRACTICES

✅ **Always push to develop first** - Test before main
✅ **Use conventional commits** - Required by pre-checks (feat:, fix:, etc.)
✅ **Keep PRs focused** - Easier to review and test
✅ **Wait for all checks** - Don't merge with failing tests
✅ **Review security findings** - Don't ignore CodeQL alerts
✅ **Use branch protection** - Enforce quality gates
✅ **Monitor dependencies** - Merge update PRs regularly
✅ **Keep CHANGELOG updated** - Aid for release notes

---

## 📞 NEED HELP?

### GitHub Actions Documentation
- https://docs.github.com/en/actions
- https://github.com/actions

### Codecov Documentation
- https://docs.codecov.io

### Security Tools
- CodeQL: https://codeql.github.com
- Bandit: https://bandit.readthedocs.io

### These Docs
- `PHASE3_CI_CD_AUTOMATION_COMPLETE.md` - Full documentation
- `.github/workflows/*.yml` - Individual workflow definitions

---

## ✨ SUMMARY

**With these workflows enabled, your repository now has:**
- ✅ Automated testing on every commit
- ✅ Security scanning daily + on-demand
- ✅ Code quality enforcement
- ✅ Automated deployment to staging
- ✅ Release management automation
- ✅ Dependency update tracking

**All with zero additional setup after the initial configuration!**

---

**Created**: 2026-03-15
**Status**: Ready to use
