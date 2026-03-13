import { create } from 'zustand';

export type NotificationType = 'success' | 'error' | 'warning' | 'info';

export interface Notification {
  id: string;
  type: NotificationType;
  message: string;
  duration?: number;
}

interface NotificationStore {
  notifications: Notification[];
  addNotification: (notification: Omit<Notification, 'id'>) => void;
  removeNotification: (id: string) => void;
  clearNotifications: () => void;
}

export const useNotificationStore = create<NotificationStore>((set) => ({
  notifications: [],

  addNotification: (notification) => {
    const id = Math.random().toString(36).substr(2, 9);
    const newNotification = { ...notification, id };

    set((state) => ({
      notifications: [...state.notifications, newNotification],
    }));

    // Auto-remove after duration
    if (notification.duration !== Infinity) {
      const duration = notification.duration || 3000;
      setTimeout(() => {
        set((state) => ({
          notifications: state.notifications.filter((n) => n.id !== id),
        }));
      }, duration);
    }
  },

  removeNotification: (id) => {
    set((state) => ({
      notifications: state.notifications.filter((n) => n.id !== id),
    }));
  },

  clearNotifications: () => {
    set({ notifications: [] });
  },
}));

// Convenience functions
export const useNotifications = () => {
  const { addNotification } = useNotificationStore();

  return {
    success: (message: string) =>
      addNotification({ type: 'success', message, duration: 3000 }),
    error: (message: string) =>
      addNotification({ type: 'error', message, duration: 5000 }),
    warning: (message: string) =>
      addNotification({ type: 'warning', message, duration: 4000 }),
    info: (message: string) =>
      addNotification({ type: 'info', message, duration: 3000 }),
  };
};
