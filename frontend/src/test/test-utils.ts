/**
 * Test utilities and helpers for CIAF frontend tests.
 */

import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';


/**
 * Create a wrapper component with all necessary providers for testing.
 * @returns Wrapper component for render()
 */
export function createTestWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0,
      },
      mutations: {
        retry: false,
      },
    },
  });

  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(
      BrowserRouter,
      {},
      React.createElement(
        QueryClientProvider,
        { client: queryClient },
        children
      )
    );
}


/**
 * Mock API responses for common queries.
 */
export const mockApiResponses = {
  healthCheck: {
    status: 'healthy',
    service: 'CIAF Verification',
    version: '1.0.0',
    proof_store_stats: {
      output_tags: 50,
      task_batches: 10,
      org_batch_windows: 5,
    },
  },

  organizationStats: {
    organization_id: 'org-1',
    total_tags: 100,
    verified_tags: 95,
    high_risk_tags: 5,
    critical_tags: 0,
    total_batch_windows: 8,
  },

  verificationResult: {
    tag_id: 'tag-123',
    verified: true,
    timestamp: '2026-03-14T00:00:00Z',
    agent_ids: ['agent-1', 'agent-2'],
    merkle_proof: {
      root: 'root-hash',
      leaves: ['leaf-1', 'leaf-2'],
    },
  },

  auditTrail: {
    tag_id: 'tag-123',
    agent_ids: ['agent-1', 'agent-2'],
    inference_type: 'multi_agent',
    actions: [
      {
        timestamp: '2026-03-14T00:00:00Z',
        agent_id: 'agent-1',
        action: 'inference',
        details: {},
      },
    ],
  },

  complianceReport: {
    organization_id: 'org-1',
    compliance_status: 'compliant',
    policies: [
      {
        policy_id: 'policy-1',
        status: 'compliant',
        evidence_count: 10,
      },
    ],
  },
};


/**
 * Wait for element with retry logic.
 * @param callback Function that returns element
 * @param options Wait options
 */
export async function waitForElement(
  callback: () => HTMLElement | null,
  options = { timeout: 1000, interval: 50 }
) {
  const startTime = Date.now();

  while (Date.now() - startTime < options.timeout) {
    const element = callback();
    if (element) return element;
    await new Promise(resolve => setTimeout(resolve, options.interval));
  }

  throw new Error('Element not found within timeout');
}


/**
 * Create mock localStorage for testing.
 */
export function setupMockStorage() {
  const store: Record<string, string> = {};

  const mockStorage = {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => {
      store[key] = value;
    },
    removeItem: (key: string) => {
      delete store[key];
    },
    clear: () => {
      Object.keys(store).forEach(key => delete store[key]);
    },
  };

  Object.defineProperty(window, 'localStorage', {
    value: mockStorage,
  });

  return mockStorage;
}


/**
 * Assert API call was made with correct parameters.
 * @param mockFn Mock function to check
 * @param expectedCall Expected call signature
 */
export function assertApiCall(
  mockFn: any,
  expectedCall: { method: string; url: string; params?: any }
) {
  const calls = mockFn.mock.calls;

  const found = calls.some(call => {
    const [url, config] = call;
    return (
      url.includes(expectedCall.url) &&
      (!expectedCall.params ||
        JSON.stringify(config?.params) ===
          JSON.stringify(expectedCall.params))
    );
  });

  if (!found) {
    throw new Error(
      `API call not found. Expected: ${expectedCall.url}\nActual calls: ${calls
        .map(c => c[0])
        .join(', ')}`
    );
  }
}


/**
 * Create delayed promise for testing async behavior.
 */
export function createDelayedPromise<T>(
  value: T,
  delayMs: number = 100
): Promise<T> {
  return new Promise(resolve => setTimeout(() => resolve(value), delayMs));
}


/**
 * Mock fetch for testing API calls.
 */
export function setupMockFetch(
  responses: Record<string, any> = {}
) {
  const mockFetch = (url: string) => {
    const urlStr = typeof url === 'string' ? url : url.toString();
    const response = responses[urlStr] || { ok: true, data: {} };

    return Promise.resolve({
      ok: response.ok ?? true,
      status: response.status ?? 200,
      json: () => Promise.resolve(response.data ?? response),
    } as any);
  };

  global.fetch = mockFetch as any;
  return mockFetch;
}
