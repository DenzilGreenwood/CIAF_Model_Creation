# CIAF Testing Guide

Complete testing guide for frontend UX and backend APIs.

## Quick Start

### Frontend Tests (UX)

```bash
cd frontend

# Install dependencies (if not done)
npm install --legacy-peer-deps

# Run all tests
npm run test

# Run tests in watch mode
npm run test -- --watch

# Generate coverage report
npm run coverage

# Run specific test file
npm run test -- src/api/hooks.test.ts
```

### Backend Tests (API)

```bash
# Setup environment
cd ciaf/vault
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run all API tests
pytest api.test.py -v

# Run specific test
pytest api.test.py::TestVaultAPI::test_05_end_to_end_workflow -v

# Run with coverage
pytest api.test.py --cov=ciaf/vault --cov-report=html
```

## Test Structure

### Frontend Tests (Vitest + React Testing Library)

Located in: `frontend/src/`

#### 1. **API Client Tests** (`api/client.test.ts`)
- APIClient initialization
- Request/response handling
- Interceptor functionality
- Error handling
- Authentication header management

**Coverage:**
- ✅ 10+ test cases
- ✅ Axios mocking
- ✅ Request interceptors
- ✅ Response interceptors

#### 2. **React Query Hooks Tests** (`api/hooks.test.ts`)
- useVerifyOutput (query + mutation)
- useAuditTrail
- useComplianceReport
- useOrganizationStats
- useHealthCheck
- useRefreshCache

**Coverage:**
- ✅ 15+ test cases
- ✅ Query enabled/disabled states
- ✅ Error handling
- ✅ Refetch intervals
- ✅ Query invalidation

#### 3. **Dashboard Component Tests** (`pages/Dashboard.test.tsx`)
- Organization selector
- Stats calculation
- Loading states
- Error states
- Data rendering

**Coverage:**
- ✅ 12+ test cases
- ✅ Component rendering
- ✅ User interactions
- ✅ Data binding
- ✅ Edge cases

### Backend Tests (Pytest)

Located in: `ciaf/vault/api.test.py`

#### Vault API Integration Tests

**Endpoints Tested:**

1. **Health & Status**
   - GET /health
   - GET /stats

2. **Proof Management**
   - POST /submit (proof submission)
   - GET /verify/{proof_id} (proof verification)
   - POST /certificate/{proof_id} (certificate generation)

3. **Audit & Compliance**
   - GET /audit-trail (retrieve audit entries)
   - GET /audit-trail?filters (filtered audit trail)
   - GET /audit-summary (audit summary)

4. **Organization**
   - GET /organization (org details)
   - GET /organization/proofs (org proofs list)
   - GET /organization/proofs?limit=N (pagination)

**Coverage:**
- ✅ 10 comprehensive test scenarios
- ✅ Authentication flow
- ✅ End-to-end workflows
- ✅ Error cases
- ✅ Data validation
- ✅ Pagination
- ✅ State persistence

## Running Tests

### All Tests

```bash
# Frontend
cd frontend && npm run test

# Backend
cd ciaf/vault && pytest api.test.py -v
```

### Specific Test Suites

```bash
# Frontend API client only
npm run test -- src/api/client.test.ts

# Frontend hooks only
npm run test -- src/api/hooks.test.ts

# Frontend components only
npm run test -- src/pages/Dashboard.test.tsx

# Backend health tests only
pytest api.test.py::TestVaultAPI::test_01_health_check -v
```

### With Coverage

```bash
# Frontend coverage
npm run coverage

# Backend coverage
pytest api.test.py --cov=ciaf/vault --cov-report=html
```

## Test Results Interpretation

### Frontend Test Output

```
✓ src/api/client.test.ts (32 tests)
  ✓ APIClient
    ✓ Initialization
      ✓ should create client with default base URL
      ✓ should setup request interceptor
    ✓ verifyOutput
      ✓ should verify output with tag ID
    ...
```

### Backend Test Output

```
test_01_health_check PASSED
test_02_stats_endpoint PASSED
test_03_submit_proof_success PASSED
...
========== 10 passed in 2.34s ==========
```

## Expected Test Coverage

### Frontend
- **Line Coverage:** 85%+
- **Branch Coverage:** 80%+
- **Function Coverage:** 90%+

### Backend
- **Line Coverage:** 90%+
- **Endpoint Coverage:** 100%
- **Scenario Coverage:** 95%+

## Debugging Failed Tests

### Frontend

```bash
# Run with verbose output
npm run test -- --reporter=verbose

# Stop on first failure
npm run test -- --bail

# Run specific test with debugging
npm run test -- src/api/client.test.ts --inspect-brk
```

### Backend

```bash
# Verbose output
pytest api.test.py -vv

# Show print statements
pytest api.test.py -s

# Stop on first failure
pytest api.test.py -x

# Show local variables
pytest api.test.py -l
```

## Common Issues & Solutions

### Frontend

**Issue:** "Cannot find module '@/types'"
- **Solution:** Ensure vitest.config.ts has alias configuration

**Issue:** Hooks test failing with "Missing QueryClientProvider"
- **Solution:** All hooks tests must use createWrapper() fixture

**Issue:** Component not rendering in test
- **Solution:** Wrap with BrowserRouter and QueryClientProvider

### Backend

**Issue:** "Connection refused" when connecting to API
- **Solution:** Ensure API is running: `docker-compose up`

**Issue:** "401 Unauthorized" in tests
- **Solution:** Verify API key in headers: `Authorization: Bearer <key>`

**Issue:** Tests pass locally but fail in CI/CD
- **Solution:** Check environment variables and database state

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Test Suite
on: [push, pull_request]

jobs:
  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: cd frontend && npm install && npm run test

  backend-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: cd ciaf/vault && pip install -r requirements.txt && pytest api.test.py
```

## Test Data Management

### Frontend Mock Data

All hooks tests use mocked API responses:

```typescript
const mockResult = {
  tag_id: 'tag-123',
  verified: true,
  timestamp: '2026-03-14T00:00:00Z',
  agent_ids: ['agent-1'],
};
```

### Backend Test Data

Tests use realistic proof submission payloads:

```json
{
  "content": "AI model inference output",
  "agent_ids": ["agent-1", "agent-2"],
  "policies_applied": ["policy-1"],
  "timestamp": "2026-03-14T00:00:00Z",
  "metadata": {
    "model_name": "gpt-4",
    "inference_type": "multi_agent"
  }
}
```

## Performance Benchmarks

Expected test execution times:

- **Frontend Tests:** ~2-5 seconds (unit tests only)
- **Backend Tests:** ~5-10 seconds (full integration)
- **Coverage Reports:** ~3-5 seconds additional

## Best Practices

1. **Isolate Tests**
   - Each test should be independent
   - Use proper setup/teardown
   - Clean localStorage/mocks between tests

2. **Mock External Dependencies**
   - Mock API calls
   - Mock localStorage
   - Mock environment variables

3. **Test User Interactions**
   - Click buttons
   - Type in inputs
   - Change selections
   - Submit forms

4. **Test Error States**
   - Network failures
   - Invalid responses
   - Missing data
   - Timeouts

5. **Meaningful Assertions**
   - Check exact values
   - Verify DOM updates
   - Confirm API calls
   - Validate state changes

## Continuous Testing

### Watch Mode (Development)

```bash
# Frontend - auto-rerun on changes
npm run test -- --watch

# Backend - auto-rerun on changes
pytest api.test.py --looponfail
```

### Pre-commit Hooks

Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
npm run test --prefix frontend
pytest ciaf/vault/api.test.py
```

## Future Test Coverage

Planned additions:

1. ✅ **E2E Tests** - Playwright/Cypress for full workflows
2. ✅ **Performance Tests** - API response time benchmarks
3. ✅ **Security Tests** - Auth/encryption validation
4. ✅ **Load Tests** - Concurrent request handling
5. ✅ **Accessibility Tests** - WCAG compliance

## Support & Resources

- **Jest/Vitest Docs:** https://vitest.dev
- **React Testing Library:** https://testing-library.com/react
- **Pytest Docs:** https://docs.pytest.org
- **Testing Best Practices:** https://testingjavascript.com

---

**Last Updated:** 2026-03-14
**Test Suite Version:** 1.0
**Maintainer:** Development Team
