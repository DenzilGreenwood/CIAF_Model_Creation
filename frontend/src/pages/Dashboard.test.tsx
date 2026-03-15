import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Dashboard } from './Dashboard';
import * as hooks from '@/api/hooks';

// Mock the API hooks
vi.mock('@/api/hooks', () => ({
  useHealthCheck: vi.fn(),
  useOrganizationStats: vi.fn(),
}));

// Mock components that may have external dependencies
vi.mock('recharts', () => ({
  ResponsiveContainer: ({ children }: any) => React.createElement('div', {}, children),
  PieChart: ({ children }: any) => React.createElement('div', {}, children),
  Pie: () => React.createElement('div'),
  Cell: () => null,
  BarChart: ({ children }: any) => React.createElement('div', {}, children),
  Bar: () => React.createElement('div'),
  Tooltip: () => React.createElement('div'),
}));

vi.mock('@/components/common/Badges', () => ({
  RiskBadge: ({ level }: any) => React.createElement('span', {}, `Badge: ${level}`),
}));

vi.mock('@/components/common/Spinner', () => ({
  Spinner: ({ message }: any) => React.createElement('div', {}, message),
}));

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(
      BrowserRouter,
      {},
      React.createElement(QueryClientProvider, { client: queryClient }, children)
    );
};

describe('Dashboard Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  const mockHealthData = {
    status: 'healthy',
    service: 'CIAF Verification',
    version: '1.0.0',
    proof_store_stats: {
      output_tags: 50,
      task_batches: 10,
      org_batch_windows: 5,
    },
  };

  const mockStatsData = {
    organization_id: 'banking_org_001',
    total_tags: 100,
    verified_tags: 95,
    high_risk_tags: 5,
    critical_tags: 0,
    total_batch_windows: 8,
  };

  it('should render loading spinner while fetching data', () => {
    vi.mocked(hooks.useHealthCheck).mockReturnValue({
      isLoading: true,
      data: undefined,
      isSuccess: false,
      isError: false,
      error: null,
    } as any);

    vi.mocked(hooks.useOrganizationStats).mockReturnValue({
      isLoading: true,
      data: undefined,
      isSuccess: false,
      isError: false,
      error: null,
    } as any);

    render(<Dashboard />, { wrapper: createWrapper() });

    expect(screen.getByText(/Loading dashboard/i)).toBeInTheDocument();
  });

  it('should render organization selector', () => {
    vi.mocked(hooks.useHealthCheck).mockReturnValue({
      isLoading: false,
      data: mockHealthData,
      isSuccess: true,
      isError: false,
      error: null,
    } as any);

    vi.mocked(hooks.useOrganizationStats).mockReturnValue({
      isLoading: false,
      data: mockStatsData,
      isSuccess: true,
      isError: false,
      error: null,
    } as any);

    render(<Dashboard />, { wrapper: createWrapper() });

    expect(screen.getByText('Select Organization')).toBeInTheDocument();
    expect(screen.getByText('Banking Organization')).toBeInTheDocument();
    expect(screen.getByText('Healthcare Organization')).toBeInTheDocument();
  });

  it('should display quick stats cards', () => {
    vi.mocked(hooks.useHealthCheck).mockReturnValue({
      isLoading: false,
      data: mockHealthData,
      isSuccess: true,
      isError: false,
      error: null,
    } as any);

    vi.mocked(hooks.useOrganizationStats).mockReturnValue({
      isLoading: false,
      data: mockStatsData,
      isSuccess: true,
      isError: false,
      error: null,
    } as any);

    render(<Dashboard />, { wrapper: createWrapper() });

    expect(screen.getByText('Total Outputs')).toBeInTheDocument();
    expect(screen.getAllByText('100')[0]).toBeInTheDocument();

    expect(screen.getByText('Verification Rate')).toBeInTheDocument();
    expect(screen.getByText('95.0%')).toBeInTheDocument();

    expect(screen.getByText('High Risk Outputs')).toBeInTheDocument();
    expect(screen.getAllByText('5')[0]).toBeInTheDocument();

    expect(screen.getByText('Service Status')).toBeInTheDocument();
    expect(screen.getByText('Healthy')).toBeInTheDocument();
  });

  it('should display system health metrics', () => {
    vi.mocked(hooks.useHealthCheck).mockReturnValue({
      isLoading: false,
      data: mockHealthData,
      isSuccess: true,
      isError: false,
      error: null,
    } as any);

    vi.mocked(hooks.useOrganizationStats).mockReturnValue({
      isLoading: false,
      data: mockStatsData,
      isSuccess: true,
      isError: false,
      error: null,
    } as any);

    render(<Dashboard />, { wrapper: createWrapper() });

    expect(screen.getByText('System Health')).toBeInTheDocument();
    expect(screen.getByText('Output Tags')).toBeInTheDocument();
    expect(screen.getByText('50')).toBeInTheDocument();
    expect(screen.getByText('Task Batches')).toBeInTheDocument();
    expect(screen.getByText('10')).toBeInTheDocument();
  });

  it('should allow organization selection', async () => {
    vi.mocked(hooks.useHealthCheck).mockReturnValue({
      isLoading: false,
      data: mockHealthData,
      isSuccess: true,
      isError: false,
      error: null,
    } as any);

    vi.mocked(hooks.useOrganizationStats).mockReturnValue({
      isLoading: false,
      data: mockStatsData,
      isSuccess: true,
      isError: false,
      error: null,
    } as any);

    render(<Dashboard />, { wrapper: createWrapper() });

    const healthcareButton = screen.getByText('Healthcare Organization');
    fireEvent.click(healthcareButton);

    await waitFor(() => {
      expect(screen.getAllByText('healthcare_org_001')[0]).toBeInTheDocument();
    });
  });

  it('should display organization statistics section', () => {
    vi.mocked(hooks.useHealthCheck).mockReturnValue({
      isLoading: false,
      data: mockHealthData,
      isSuccess: true,
      isError: false,
      error: null,
    } as any);

    vi.mocked(hooks.useOrganizationStats).mockReturnValue({
      isLoading: false,
      data: mockStatsData,
      isSuccess: true,
      isError: false,
      error: null,
    } as any);

    render(<Dashboard />, { wrapper: createWrapper() });

    expect(screen.getByText('Organization Statistics')).toBeInTheDocument();
    expect(screen.getByText('Organization ID')).toBeInTheDocument();
    expect(screen.getByText('Total Tags')).toBeInTheDocument();
    expect(screen.getByText('Batch Windows')).toBeInTheDocument();
  });

  it('should display quick action buttons', () => {
    vi.mocked(hooks.useHealthCheck).mockReturnValue({
      isLoading: false,
      data: mockHealthData,
      isSuccess: true,
      isError: false,
      error: null,
    } as any);

    vi.mocked(hooks.useOrganizationStats).mockReturnValue({
      isLoading: false,
      data: mockStatsData,
      isSuccess: true,
      isError: false,
      error: null,
    } as any);

    render(<Dashboard />, { wrapper: createWrapper() });

    expect(screen.getByText('Quick Actions')).toBeInTheDocument();
    expect(screen.getByText('Verify Output')).toBeInTheDocument();
    expect(screen.getByText('View Audit Trail')).toBeInTheDocument();
    expect(screen.getByText('Compliance Report')).toBeInTheDocument();
    expect(screen.getByText('View Statistics')).toBeInTheDocument();
  });

  it('should calculate verification rate correctly', () => {
    const customStats = {
      ...mockStatsData,
      total_tags: 200,
      verified_tags: 150,
    };

    vi.mocked(hooks.useHealthCheck).mockReturnValue({
      isLoading: false,
      data: mockHealthData,
      isSuccess: true,
      isError: false,
      error: null,
    } as any);

    vi.mocked(hooks.useOrganizationStats).mockReturnValue({
      isLoading: false,
      data: customStats,
      isSuccess: true,
      isError: false,
      error: null,
    } as any);

    render(<Dashboard />, { wrapper: createWrapper() });

    expect(screen.getByText('75.0%')).toBeInTheDocument();
  });

  it('should handle missing health check data gracefully', () => {
    vi.mocked(hooks.useHealthCheck).mockReturnValue({
      isLoading: false,
      data: undefined,
      isSuccess: true,
      isError: false,
      error: null,
    } as any);

    vi.mocked(hooks.useOrganizationStats).mockReturnValue({
      isLoading: false,
      data: mockStatsData,
      isSuccess: true,
      isError: false,
      error: null,
    } as any);

    render(<Dashboard />, { wrapper: createWrapper() });

    expect(screen.getByText('Service Status')).toBeInTheDocument();
    expect(screen.getByText('Issues')).toBeInTheDocument();
  });

  it('should handle missing organization stats gracefully', () => {
    vi.mocked(hooks.useHealthCheck).mockReturnValue({
      isLoading: false,
      data: mockHealthData,
      isSuccess: true,
      isError: false,
      error: null,
    } as any);

    vi.mocked(hooks.useOrganizationStats).mockReturnValue({
      isLoading: false,
      data: undefined,
      isSuccess: true,
      isError: false,
      error: null,
    } as any);

    render(<Dashboard />, { wrapper: createWrapper() });

    const zeros = screen.getAllByText('0');
    expect(zeros.length).toBeGreaterThan(0);
  });
});
