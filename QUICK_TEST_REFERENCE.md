# CIAF Testing - Quick Reference Card

## 🚀 Quick Start (Fastest Way to Run Tests)

### Windows Users - Easiest Method

```bash
# Run all frontend tests
test-frontend.bat

# Run all backend tests
test-backend.bat

# Frontend with coverage
test-frontend.bat coverage

# Backend with coverage
test-backend.bat coverage
```

### Linux/Mac Users - Easiest Method

```bash
# Run all frontend tests
./test-frontend.sh

# Run all backend tests
./test-backend.sh

# Frontend with coverage
./test-frontend.sh coverage

# Backend with coverage
./test-backend.sh coverage
```

### Using Python Test Runner (All Platforms)

```bash
python run_tests.py
```

With coverage:
```bash
python run_tests.py --coverage
```

---

## 🧪 Frontend Tests

### Location
`frontend/src/`

### Quickest Way (Windows)
```bash
test-frontend.bat
```

### Quickest Way (Linux/Mac)
```bash
./test-frontend.sh
```

### Manual NPM Command
```bash
cd frontend && npm run test
```

### Run Specific Tests
```bash
# API Client
npm run test -- src/api/client.test.ts

# Hooks
npm run test -- src/api/hooks.test.ts

# Dashboard Component
npm run test -- src/pages/Dashboard.test.tsx

# Integration/E2E
npm run test -- src/test/integration.test.tsx
```

### Watch Mode (Auto-rerun)
```bash
npm run test -- --watch
```

### Coverage Report
```bash
npm run coverage
```

### Test Count
- API Client: 10+ tests
- React Query Hooks: 15+ tests
- Dashboard Component: 12+ tests
- Integration Tests: 20+ scenarios
- **Total: 50+ tests**

---

## 🔧 Backend Tests

### Location
`ciaf/vault/`

### Quickest Way (Windows)
```bash
test-backend.bat
```

### Quickest Way (Linux/Mac)
```bash
./test-backend.sh
```

### Manual Pytest Command
```bash
cd ciaf/vault && pytest api.test.py -v -p no:langsmith
```

### Run Specific Tests
```bash
# Just health check
pytest api.test.py::TestVaultAPI::test_01_health_check -v

# Complete workflow
pytest api.test.py::TestVaultAPI::test_05_end_to_end_workflow -v

# All organization tests
pytest api.test.py -k "organization" -v
```

### Coverage Report
```bash
pytest api.test.py --cov=ciaf/vault --cov-report=html
```

### Show Debug Output
```bash
pytest api.test.py -s
```

### Test Count
- Health & Status: 2 tests
- Proof Management: 3 tests
- Audit Operations: 2 tests
- Organization: 2 tests
- **Total: 10 scenarios**

---

## 📊 Endpoints Tested

| Endpoint | Method | Tests |
|----------|--------|-------|
| `/health` | GET | ✅ |
| `/stats` | GET | ✅ |
| `/submit` | POST | ✅ |
| `/verify/{id}` | GET | ✅ |
| `/certificate/{id}` | POST | ✅ |
| `/audit-trail` | GET | ✅ |
| `/audit-summary` | GET | ✅ |
| `/organization` | GET | ✅ |
| `/organization/proofs` | GET | ✅ |

---

## 🎯 Common Testing Scenarios

### Run Frontend Only
```bash
python run_tests.py --frontend
```

### Run Backend Only
```bash
python run_tests.py --backend
```

### Run Frontend in Watch Mode
```bash
cd frontend && npm run test -- --watch
```

### Generate All Coverage Reports
```bash
python run_tests.py --coverage
```

### Stop on First Failure
```bash
# Frontend
npm run test -- --bail

# Backend
pytest api.test.py -x
```

---

## 📈 Expected Results

### Test Execution Time
- Frontend: ~7 seconds
- Backend: ~8 seconds
- **Both: ~15 seconds**

### With Coverage
- Frontend: ~10 seconds
- Backend: ~10 seconds
- **Both: ~20 seconds**

### Coverage Targets
- Lines: 80%+
- Branches: 75%+
- Functions: 85%+

---

## 🐛 Debugging Tips

### Frontend Debug
```bash
# Verbose output
npm run test -- --reporter=verbose

# Stop at first error
npm run test -- --bail

# Show all console output
npm run test -- 2>&1 | grep -A5 "console"
```

### Backend Debug
```bash
# Show print statements
pytest api.test.py -s

# Very verbose
pytest api.test.py -vv

# Drop into debugger
pytest api.test.py --pdb
```

---

## 📁 Key Test Files

```
frontend/src/api/client.test.ts           ← API client tests
frontend/src/api/hooks.test.ts            ← React query hooks
frontend/src/pages/Dashboard.test.tsx     ← Component tests
frontend/src/test/integration.test.tsx    ← E2E tests
ciaf/vault/api.test.py                    ← Backend tests
frontend/vitest.config.ts                 ← Frontend config
ciaf/vault/pytest.ini                     ← Backend config
```

---

## ⚙️ Configuration

### Frontend (`vitest.config.ts`)
- Environment: jsdom
- Timeout: 10s
- Coverage threshold: 80% lines

### Backend (`pytest.ini`)
- Asyncio: auto-mode
- Discovery: `test_*.py`, `*_test.py`
- Timeout: 30s

---

## 📚 Documentation

- **TESTING.md** - Complete testing guide
- **TEST_SUMMARY.md** - What was created
- **frontend/src/test/README.md** - Frontend guide
- **Test files** - Inline comments with examples

---

## ❓ Troubleshooting

| Problem | Solution |
|---------|----------|
| npm peer dependency conflict | Run `npm install --legacy-peer-deps` in frontend dir |
| Tests hang | Check API is running: `docker-compose up` |
| 401 errors | Verify API key in test headers |
| Module not found | Run `npm install --legacy-peer-deps` in frontend dir |
| ModuleNotFoundError | Run `pip install -r requirements.txt` in backend |
| Timeout errors | Increase timeout or check network |

---

## 🔄 Pre-commit Hook

Add to `.git/hooks/pre-commit`:
```bash
#!/bin/bash
npm run test --prefix frontend || exit 1
pytest ciaf/vault/api.test.py > /dev/null || exit 1
```

Make executable:
```bash
chmod +x .git/hooks/pre-commit
```

---

## 📊 Test Statistics

| Metric | Value |
|--------|-------|
| Total Test Files | 5 |
| Total Test Cases | 50+ |
| Endpoints Covered | 8+ |
| Components Tested | 1 |
| Hooks Tested | 6 |
| E2E Scenarios | 20+ |
| Lines of Test Code | 2000+ |
| Documentation Pages | 4 |

---

## 🎓 Learn More

- Vitest: https://vitest.dev
- React Testing Library: https://testing-library.com
- Pytest: https://docs.pytest.org

---

**Last Updated:** 2026-03-14
**Version:** 1.0
**Status:** Ready to Use ✅
