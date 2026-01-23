import React from 'react';
import { AlertCircle, CheckCircle, Info, X } from 'lucide-react';

export function AlertDialog({ isOpen, onClose, title, message, variant = "error" }) {
  if (!isOpen) return null;

  const variantConfig = {
    error: {
      icon: AlertCircle,
      bg: 'bg-red-50',
      text: 'text-red-600',
      button: 'bg-red-600 hover:bg-red-700',
      iconColor: 'text-red-500',
      title: title || 'Error'
    },
    success: {
      icon: CheckCircle,
      bg: 'bg-emerald-50',
      text: 'text-emerald-600',
      button: 'bg-emerald-600 hover:bg-emerald-700',
      iconColor: 'text-emerald-500',
      title: title || 'Éxito'
    },
    info: {
      icon: Info,
      bg: 'bg-blue-50',
      text: 'text-blue-600',
      button: 'bg-blue-600 hover:bg-blue-700',
      iconColor: 'text-blue-500',
      title: title || 'Información'
    }
  };

  const config = variantConfig[variant] || variantConfig.error;
  const IconComponent = config.icon;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full animate-fade-in-scale">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-slate-100">
          <div className="flex items-center gap-3">
            <div className={`w-12 h-12 rounded-full ${config.bg} flex items-center justify-center`}>
              <IconComponent className={config.iconColor} size={24} />
            </div>
            <h3 className="text-xl font-bold text-slate-800">{config.title}</h3>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 transition-colors"
          >
            <X size={24} />
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          <p className="text-slate-600 text-base leading-relaxed whitespace-pre-line">{message}</p>
        </div>

        {/* Actions */}
        <div className="flex justify-end p-6 bg-slate-50 rounded-b-2xl">
          <button
            onClick={onClose}
            className={`px-8 py-3 rounded-xl font-bold text-white ${config.button} transition-all shadow-lg`}
          >
            Aceptar
          </button>
        </div>
      </div>
    </div>
  );
}
