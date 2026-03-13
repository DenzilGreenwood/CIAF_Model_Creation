import React from 'react';
import { useNotificationStore } from '@/store/notifications.store';
import { AlertCircle, CheckCircle2, AlertTriangle, Info } from 'lucide-react';

export const NotificationToast: React.FC = () => {
  const { notifications, removeNotification } = useNotificationStore();

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2">
      {notifications.map((notification) => {
        const icons = {
          success: <CheckCircle2 size={20} />,
          error: <AlertCircle size={20} />,
          warning: <AlertTriangle size={20} />,
          info: <Info size={20} />,
        };

        const styles = {
          success: 'bg-green-500',
          error: 'bg-red-500',
          warning: 'bg-yellow-500',
          info: 'bg-blue-500',
        };

        return (
          <div
            key={notification.id}
            className={`${styles[notification.type]} text-white px-4 py-3 rounded-lg shadow-lg flex items-center gap-3`}
          >
            {icons[notification.type]}
            <span className="flex-1">{notification.message}</span>
            <button
              onClick={() => removeNotification(notification.id)}
              className="ml-2 hover:opacity-75"
            >
              ×
            </button>
          </div>
        );
      })}
    </div>
  );
};
