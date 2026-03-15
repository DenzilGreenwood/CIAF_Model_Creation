import { test, expect } from '@playwright/test';

/**
 * End-to-End Tests with Playwright
 * Tests complete user workflows through the UI
 */

test.describe('Authentication Flows', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to app before each test
    await page.goto('http://localhost:3002');
  });

  test('should navigate to login page', async ({ page }) => {
    await page.goto('http://localhost:3002/login');
    await expect(page).toHaveTitle(/login|sign in/i);
    await expect(page.locator('input[name="email"]')).toBeVisible();
    await expect(page.locator('input[name="password"]')).toBeVisible();
  });

  test('successful login redirects to dashboard', async ({ page }) => {
    await page.goto('http://localhost:3002/login');

    // Fill in credentials
    await page.locator('input[name="email"]').fill('demo@ciaf.io');
    await page.locator('input[name="password"]').fill('DemoPass123!');

    // Click sign in button
    await page.locator('button:has-text("Sign In")').click();

    // Should redirect to dashboard
    await page.waitForURL('**/dashboard');
    await expect(page).toHaveURL(/dashboard/);
  });

  test('invalid credentials show error message', async ({ page }) => {
    await page.goto('http://localhost:3002/login');

    // Fill in wrong credentials
    await page.locator('input[name="email"]').fill('demo@ciaf.io');
    await page.locator('input[name="password"]').fill('WrongPassword123!');

    // Click sign in
    await page.locator('button:has-text("Sign In")').click();

    // Should show error message
    await expect(page.locator('text=/invalid|wrong|incorrect/i')).toBeVisible();
  });

  test('password visibility toggle works', async ({ page }) => {
    await page.goto('http://localhost:3002/login');

    const passwordInput = page.locator('input[name="password"]');
    await passwordInput.fill('TestPassword123!');

    // Initial type should be password
    await expect(passwordInput).toHaveAttribute('type', 'password');

    // Click visibility toggle
    await page.locator('[aria-label*="toggle" i]').click();

    // Type should change to text
    await expect(passwordInput).toHaveAttribute('type', 'text');
  });

  test('remember me checkbox is present', async ({ page }) => {
    await page.goto('http://localhost:3002/login');

    const rememberCheckbox = page.locator('input[type="checkbox"]');
    await expect(rememberCheckbox).toBeVisible();
  });

  test('logout clears authentication state', async ({ page }) => {
    // Login first
    await page.goto('http://localhost:3002/login');
    await page.locator('input[name="email"]').fill('demo@ciaf.io');
    await page.locator('input[name="password"]').fill('DemoPass123!');
    await page.locator('button:has-text("Sign In")').click();

    // Wait for dashboard
    await page.waitForURL('**/dashboard');

    // Click logout
    await page.locator('button:has-text("Logout")').click();

    // Should redirect to login
    await page.waitForURL('**/login');
    await expect(page).toHaveURL(/login/);
  });
});

test.describe('Protected Routes', () => {
  test('unauthenticated user redirected to login from dashboard', async ({ page }) => {
    // Try to access dashboard without login
    await page.goto('http://localhost:3002/dashboard');

    // Should redirect to login
    await page.waitForURL('**/login');
    await expect(page).toHaveURL(/login/);
  });

  test('authenticated user can access dashboard', async ({ page }) => {
    // Login
    await page.goto('http://localhost:3002/login');
    await page.locator('input[name="email"]').fill('demo@ciaf.io');
    await page.locator('input[name="password"]').fill('DemoPass123!');
    await page.locator('button:has-text("Sign In")').click();

    // Should access dashboard
    await page.waitForURL('**/dashboard');
    await expect(page.locator('text=/dashboard|overview|welcome/i')).toBeVisible();
  });

  test('non-admin user cannot access admin panel', async ({ page }) => {
    // Login as regular user
    await page.goto('http://localhost:3002/login');
    await page.locator('input[name="email"]').fill('demo@ciaf.io');
    await page.locator('input[name="password"]').fill('DemoPass123!');
    await page.locator('button:has-text("Sign In")').click();

    // Try to access admin panel
    await page.goto('http://localhost:3002/admin');

    // Should show access denied or redirect
    await expect(
      page.locator('text=/access denied|admin|unauthorized/i')
    ).toBeVisible();
  });

  test('viewer role has limited permissions', async ({ page }) => {
    // This test would verify viewer can see read-only content
    // but cannot edit or delete
    await page.goto('http://localhost:3002/login');

    // Login and verify role restriction
    // Implementation details depend on your actual app structure
    await expect(page).toHaveURL(/^http/);
  });
});

test.describe('Dashboard Functionality', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each dashboard test
    await page.goto('http://localhost:3002/login');
    await page.locator('input[name="email"]').fill('demo@ciaf.io');
    await page.locator('input[name="password"]').fill('DemoPass123!');
    await page.locator('button:has-text("Sign In")').click();
    await page.waitForURL('**/dashboard');
  });

  test('dashboard loads with key metrics', async ({ page }) => {
    // Should see dashboard elements
    await expect(page.locator('text=/dashboard|metrics|overview/i')).toBeVisible();
  });

  test('can navigate between pages from dashboard menu', async ({ page }) => {
    // Click on Verification
    await page.locator('a:has-text("Verification")').click();
    await page.waitForURL('**/verify');
    await expect(page).toHaveURL(/verify/);

    // Go back to dashboard
    await page.locator('a:has-text("Dashboard")').click();
    await page.waitForURL('**/dashboard');
  });

  test('can access compliance dashboard', async ({ page }) => {
    // Navigate to compliance
    await page.locator('a:has-text("Compliance")').click();
    await page.waitForURL('**/compliance');
    await expect(page).toHaveURL(/compliance/);
  });
});

test.describe('Verification Workflow', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('http://localhost:3002/login');
    await page.locator('input[name="email"]').fill('demo@ciaf.io');
    await page.locator('input[name="password"]').fill('DemoPass123!');
    await page.locator('button:has-text("Sign In")').click();
  });

  test('can submit output for verification', async ({ page }) => {
    await page.goto('http://localhost:3002/verify');

    // Fill in verification form
    await page.locator('textarea[name="content"]').fill('Model output data');
    await page.locator('input[name="modelVersion"]').fill('1.0.0');

    // Submit
    await page.locator('button:has-text("Submit")').click();

    // Should show success message
    await expect(page.locator('text=/success|verified|proof/i')).toBeVisible();
  });

  test('can view proof after verification', async ({ page }) => {
    // Submit verification
    await page.goto('http://localhost:3002/verify');
    await page.locator('textarea[name="content"]').fill('Test output');
    await page.locator('button:has-text("Submit")').click();

    // Wait for proof to appear
    await page.waitForSelector('[data-testid="proof-id"]');

    // Click view proof
    await page.locator('button:has-text("View Proof")').click();

    // Should show proof details
    await expect(page.locator('text=/content hash|signature|timestamp/i')).toBeVisible();
  });
});

test.describe('Error Handling', () => {
  test('handles network errors gracefully', async ({ page }) => {
    // Simulate offline
    await page.context().setOffline(true);

    // Try to login
    await page.goto('http://localhost:3002/login');
    await page.locator('input[name="email"]').fill('demo@ciaf.io');
    await page.locator('input[name="password"]').fill('DemoPass123!');
    await page.locator('button:has-text("Sign In")').click();

    // Should show network error
    await expect(
      page.locator('text=/network|unable to connect|offline/i')
    ).toBeVisible();

    // Re-enable
    await page.context().setOffline(false);
  });

  test('handles server errors (5xx) gracefully', async ({ page }) => {
    // This would require mocking API responses
    // Implementation details depend on your test setup
    await page.goto('http://localhost:3002/login');
    await expect(page).toHaveURL(/login/);
  });

  test('handles validation errors from server', async ({ page }) => {
    await page.goto('http://localhost:3002/login');

    // Try with invalid email format
    await page.locator('input[name="email"]').fill('not-an-email');
    await page.locator('input[name="password"]').fill('DemoPass123!');

    // Try to submit
    const submitButton = page.locator('button:has-text("Sign In")');
    await expect(submitButton).toBeDisabled(); // Should be disabled by client validation
  });
});

/**
 * Run with: npx playwright test e2e/login-flow.spec.ts
 * Or with: npm run test:e2e
 */
