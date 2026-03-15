# CIAF Testing - Complete Getting Started Guide

> ✅ **Dependencies are now installed!** You're ready to run tests.

## 🎯 Run Tests Now

### **If you're on Windows:**
```cmd
test-frontend.bat
```

### **If you're on Mac/Linux:**
```bash
./test-frontend.sh
```

### **Or run everything:**
```bash
python run_tests.py
```

---

## 📋 What You Have

I've created a complete testing suite with:

✅ **50+ Test Cases**
- Frontend: API client, React hooks, components, E2E workflows
- Backend: Vault API endpoints (health, submit, verify, certificates, audit, organization)

✅ **Test Runners** (Pick one):
- `test-frontend.bat` - Windows, frontend tests only
- `test-frontend.sh` - Mac/Linux, frontend tests only
- `test-backend.bat` - Windows, backend tests only
- `test-backend.sh` - Mac/Linux, backend tests only
- `python run_tests.py` - All platforms, all tests

✅ **4 Documentation Files**
- `RUN_TESTS.md` ← How to run tests (START HERE)
- `QUICK_TEST_REFERENCE.md` ← 1-page cheat sheet
- `TESTING.md` ← Comprehensive guide (200+ lines)
- `TEST_SUMMARY.md` ← What was created

---

## 🚀 Quick Commands

```bash
# ===== FRONTEND TESTS =====
test-frontend.bat                    # Run all frontend tests (Windows)
./test-frontend.sh                   # Run all frontend tests (Mac/Linux)
test-frontend.bat coverage           # With coverage report
./test-frontend.sh coverage          # With coverage report (Mac/Linux)

# ===== BACKEND TESTS =====
test-backend.bat                     # Run all backend tests (Windows)
./test-backend.sh                    # Run all backend tests (Mac/Linux)
test-backend.bat coverage            # With coverage report
./test-backend.sh coverage           # With coverage report (Mac/Linux)

# ===== ALL TESTS =====
python run_tests.py                  # All platforms, all tests
python run_tests.py --coverage       # With coverage reports
python run_tests.py --frontend       # Frontend only
python run_tests.py --backend        # Backend only
```

---

## 📊 Expected Results

When you run tests, you should see:
- ✅ **Frontend:** ~7 seconds, 50+ tests passing
- ✅ **Backend:** ~8 seconds, 10 scenarios passing
- ✅ **Total:** ~15 seconds

Example output:
```
✓ src/api/client.test.ts (10 tests)
✓ src/api/hooks.test.ts (15 tests)
✓ src/pages/Dashboard.test.tsx (12 tests)
✓ src/test/integration.test.tsx (20+ scenarios)
test_01_health_check PASSED
test_02_stats_endpoint PASSED
... (8 more backend tests)
```

---

## 📁 Test Files Locations

```
frontend/src/
├── api/
│   ├── client.test.ts           ← API client tests
│   └── hooks.test.ts            ← React hooks tests
├── pages/
│   └── Dashboard.test.tsx       ← Component tests
└── test/
    ├── setup.ts                 ← Test initialization
    ├── test-utils.ts            ← Helper utilities
    └── integration.test.tsx     ← E2E tests

ciaf/vault/
└── api.test.py                  ← Vault API tests
```

---

## 🎓 Learn More

1. **Need step-by-step?** → Read `RUN_TESTS.md`
2. **Want quick reference?** → Read `QUICK_TEST_REFERENCE.md`
3. **Need all details?** → Read `TESTING.md`
4. **Curious what was created?** → Read `TEST_SUMMARY.md`

---

## ❓ FAQ

### Q: Do I need to install anything?
**A:** No! Dependencies are already installed. Just run the tests.

### Q: What if I get an npm error?
**A:** Run: `cd frontend && npm install --legacy-peer-deps`

### Q: Can I run just one test?
**A:** Yes! See `QUICK_TEST_REFERENCE.md` for specific test commands.

### Q: How do I see coverage reports?
**A:** Run with `coverage` flag: `test-frontend.bat coverage`

### Q: Where are my test results?
**A:** In terminal output. Coverage reports go in:
- Frontend: `frontend/coverage/`
- Backend: `ciaf/vault/htmlcov/`

---

## 🔗 Key Files

| File | Purpose |
|------|---------|
| `test-frontend.bat` | Run frontend tests (Windows) |
| `test-frontend.sh` | Run frontend tests (Mac/Linux) |
| `test-backend.bat` | Run backend tests (Windows) |
| `test-backend.sh` | Run backend tests (Mac/Linux) |
| `run_tests.py` | Master test runner (all platforms) |
| `RUN_TESTS.md` | Getting started guide |
| `QUICK_TEST_REFERENCE.md` | 1-page cheat sheet |
| `TESTING.md` | Comprehensive guide |

---

## ⚡ TL;DR

```bash
# Windows users
test-frontend.bat

# Mac/Linux users
./test-frontend.sh

# Everyone
python run_tests.py
```

**Done!** Tests will run and show results.

---

**Next Step:** Pick a test runner above and run it! 🚀
