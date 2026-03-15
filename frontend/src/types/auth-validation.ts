import { z } from 'zod';

// ============================================================
// Authentication Validation Schemas
// ============================================================

export const loginSchema = z.object({
  email: z
    .string()
    .email('Invalid email address')
    .min(3, 'Email is required'),
  password: z
    .string()
    .min(6, 'Password must be at least 6 characters')
    .max(100, 'Password too long'),
  rememberMe: z.boolean().optional(),
});

export type LoginFormData = z.infer<typeof loginSchema>;

export const registerSchema = z
  .object({
    email: z
      .string()
      .email('Invalid email address')
      .min(3, 'Email is required'),
    name: z
      .string()
      .min(2, 'Name must be at least 2 characters')
      .max(50, 'Name too long'),
    password: z
      .string()
      .min(8, 'Password must be at least 8 characters')
      .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
      .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
      .regex(/[0-9]/, 'Password must contain at least one number')
      .regex(/[^A-Za-z0-9]/, 'Password must contain at least one special character'),
    confirmPassword: z.string(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: 'Passwords do not match',
    path: ['confirmPassword'],
  });

export type RegisterFormData = z.infer<typeof registerSchema>;

export const passwordResetSchema = z.object({
  email: z
    .string()
    .email('Invalid email address')
    .min(3, 'Email is required'),
});

export type PasswordResetFormData = z.infer<typeof passwordResetSchema>;

export const passwordResetConfirmSchema = z
  .object({
    token: z.string().min(1, 'Reset token is required'),
    password: z
      .string()
      .min(8, 'Password must be at least 8 characters')
      .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
      .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
      .regex(/[0-9]/, 'Password must contain at least one number')
      .regex(/[^A-Za-z0-9]/, 'Password must contain at least one special character'),
    confirmPassword: z.string(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: 'Passwords do not match',
    path: ['confirmPassword'],
  });

export type PasswordResetConfirmFormData = z.infer<typeof passwordResetConfirmSchema>;

// ============================================================
// Form Error Types
// ============================================================

export interface FormError {
  field?: string;
  message: string;
  type: 'validation' | 'api' | 'network';
}
