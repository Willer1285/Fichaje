import React from 'react';
import { CheckCircle, X } from 'lucide-react';

export function SuccessModal({ isOpen, onClose, message, title = "Operación Exitosa" }) {
    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4 animate-in fade-in duration-200">
            <div className="bg-white rounded-3xl w-full max-w-sm shadow-2xl p-8 text-center relative overflow-hidden animate-in zoom-in-95">
                <button onClick={onClose} className="absolute top-4 right-4 text-slate-400 hover:text-slate-600 transition-colors">
                    <X size={20} />
                </button>
                
                <div className="flex justify-center mb-6">
                    <div className="p-4 bg-emerald-100 text-emerald-600 rounded-full animate-bounce">
                        <CheckCircle size={48} strokeWidth={2.5} />
                    </div>
                </div>
                
                <h3 className="text-xl font-bold text-slate-800 mb-2">{title}</h3>
                <p className="text-slate-500 mb-8">{message}</p>
                
                <button 
                    onClick={onClose} 
                    className="w-full py-3 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl shadow-lg shadow-emerald-600/30 transition-all"
                >
                    Aceptar
                </button>
            </div>
        </div>
    );
}
