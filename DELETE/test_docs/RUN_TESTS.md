# CIAF Testing - Getting Started

Welcome! I've created a comprehensive testing suite for the Artificial Intelligence Evidence Vault system. Here's how to run tests.

## ⚡ Fastest Way to Run Tests

### Windows Users
```cmd
# Frontend tests
test-frontend.bat

# Backend tests
test-backend.bat

# Both with coverage reports
test-frontend.bat coverage
test-backend.bat coverage
```

### Linux/Mac Users
```bash
# Frontend tests
./test-frontend.sh

# Backend tests
./test-backend.sh

# Both with coverage reports
./test-frontend.sh coverage
./test-backend.sh coverage
```

### All Platforms
```bash
# Run everything
python run_tests.py

# With coverage
python run_tests.py --coverage
```

---

## 📋 What Gets Tested

✅ **Frontend (React/TypeScript)**
- API Client (initialization, requests, interceptors)
- React Query Hooks (state management, caching)
- Dashboard Component (rendering, interactions)
- End-to-End Workflows (multi-page scenarios)

✅ **Backend (FastAPI/Python)**
- Vault API (all 8+ endpoints)
- Proof submission and verification
- Certificate generation
- Audit trail and compliance
- Error handling

✅ **Total: 50+ test cases**

---

## 🗂️ Test Runner Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `test-frontend.bat` | Frontend tests (Windows) | `test-frontend.bat [coverage]` |
| `test-frontend.sh` | Frontend tests (Linux/Mac) | `./test-frontend.sh [coverage]` |
| `test-backend.bat` | Backend tests (Windows) | `test-backend.bat [coverage]` |
| `test-backend.sh` | Backend tests (Linux/Mac) | `./test-backend.sh [coverage]` |
| `run_tests.py` | All tests (Python) | `python run_tests.py [options]` |

---

## 📊 Expected Results

### Execution Time
- Frontend: ~7 seconds
- Backend: ~8 seconds
- **Total: ~15 seconds**

### Coverage
- Lines: 80%+
- Branches: 75%+
- Functions: 85%+

---

## 📚 Documentation

1. **QUICK_TEST_REFERENCE.md** ← Start here (1-page guide)
2. **TESTING.md** ← Comprehensive guide (all details)
3. **TEST_SUMMARY.md** ← What was created
4. **frontend/src/test/README.md** ← Frontend details

---

## 📋 First-Time Setup

### **Step 1: Install Frontend Dependencies**
```bash
cd frontend
npm install --legacy-peer-deps
```

### **Step 2: (Optional) Install Backend Test Dependencies**
```bash
cd ciaf/vault
pip install pytest pytest-asyncio httpx
```

### **Step 3: Run Tests**
- **Windows:** `test-frontend.bat`
- **Linux/Mac:** `./test-frontend.sh`
- **All:** `python run_tests.py`

---

## 🆘 Troubleshooting

### **Error: "peer vite dependency conflict"**
- Solution: Use `--legacy-peer-deps` flag
- Command: `npm install --legacy-peer-deps`
- This is safe and won't break anything

### **Error: "npm not found"**
- **Windows:** Make sure Node.js is installed: https://nodejs.org
- **Mac:** Run `brew install node`
- **Linux:** Run `sudo apt install nodejs npm`

### **Error: "pytest error"**
- Add `-p no:langsmith` to pytest command (already included in scripts)

### **Error: "Module not found"**
- Frontend: `cd frontend && npm install`
- Backend: Already configured, shouldn't happen

### **Port already in use**
- If backend API is running on same machine, it's fine
- Tests can share the same API instance

---

## 🎯 Common Commands

```bash
# Quick frontend test
test-frontend.bat

# Frontend with coverage report
test-frontend.bat coverage

# Frontend in watch mode (auto-rerun)
cd frontend && npm run test -- --watch

# Specific backend test
cd ciaf/vault && pytest api.test.py::TestVaultAPI::test_05_end_to_end_workflow -v

# All tests with detailed output
python run_tests.py --coverage
```

---

## ✨ Features

✅ Works out of the box
✅ No configuration needed
✅ Multiple test runners (batch, shell, Python)
✅ Coverage reports included
✅ 50+ test cases
✅ Tests both UX and APIs
✅ End-to-end workflows
✅ Well documented

---

## 📖 Next Steps

1. **Pick your preferred test runner:**
   - Windows user? Use `test-frontend.bat`
   - Mac/Linux user? Use `./test-frontend.sh`
   - Want everything? Use `python run_tests.py`

2. **Read one-page quick reference:**
   - `QUICK_TEST_REFERENCE.md`

3. **Explore test files:**
   - `frontend/src/api/client.test.ts`
   - `frontend/src/api/hooks.test.ts`
   - `ciaf/vault/api.test.py`

4. **Generate coverage reports:**
   - `test-frontend.bat coverage`
   - `test-backend.bat coverage`

---

## 📞 Questions?

Check these files in order:
1. **This file** (you're reading it)
2. **QUICK_TEST_REFERENCE.md** (1-page cheat sheet)
3. **TESTING.md** (comprehensive guide)
4. **frontend/src/test/README.md** (frontend specifics)

---

**Happy Testing! 🎉**
