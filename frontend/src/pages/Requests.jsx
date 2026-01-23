import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Check, X } from 'lucide-react';
import { AlertDialog } from '../components/AlertDialog';

const API_URL = "/api";

function Requests() {
  const [activeTab, setActiveTab] = useState('vacations');
  const [vacations, setVacations] = useState([]);
  const [absences, setAbsences] = useState([]);
  const [loading, setLoading] = useState(false);

  // Modal Rejection State
  const [showRejectModal, setShowRejectModal] = useState(false);
  const [rejectReason, setRejectReason] = useState('');
  const [selectedRequest, setSelectedRequest] = useState(null);

  // Alert Dialog State
  const [alertDialog, setAlertDialog] = useState({ isOpen: false, message: '' });

  useEffect(() => {
    fetchRequests();
  }, []);

  const fetchRequests = async () => {
    setLoading(true);
    try {
      const [vacRes, absRes] = await Promise.all([
        axios.get(`${API_URL}/requests/vacations`),
        axios.get(`${API_URL}/requests/absences`)
      ]);
      setVacations(Array.isArray(vacRes.data) ? vacRes.data : []);
      setAbsences(Array.isArray(absRes.data) ? absRes.data : []);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleAction = async (type, id, action) => {
    const user = JSON.parse(localStorage.getItem('user'));
    if (!user) return;

    if (action === 'reject') {
        setSelectedRequest({ type, id });
        setRejectReason('');
        setShowRejectModal(true);
        return;
    }

    try {
      await axios.post(`${API_URL}/requests/${type}/${id}/${action}`, {
        admin_id: user.id
      });
      fetchRequests();
    } catch (error) {
      setAlertDialog({ isOpen: true, message: "Error al procesar solicitud: " + (error.response?.data?.detail || error.message) });
    }
  };

  const confirmReject = async (e) => {
      e.preventDefault();
      if (!rejectReason.trim()) return;

      const user = JSON.parse(localStorage.getItem('user'));
      try {
          await axios.post(`${API_URL}/requests/${selectedRequest.type}/${selectedRequest.id}/reject`, {
              admin_id: user.id,
              reason: rejectReason
          });
          setShowRejectModal(false);
          fetchRequests();
      } catch (error) {
          setAlertDialog({ isOpen: true, message: "Error al rechazar solicitud: " + (error.response?.data?.detail || error.message) });
      }
  };

  const RequestsList = ({ items, type }) => (
    <div className="space-y-4">
      {items.length === 0 ? (
        <div className="text-center py-10 text-slate-400">No hay solicitudes pendientes.</div>
      ) : (
        items.map((req) => (
          <div key={req.id} className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex justify-between items-center">
            <div>
              <h4 className="font-bold text-slate-800 text-lg">{req.empleado}</h4>
              <p className="text-sm text-slate-500 mb-2">{req.dni}</p>
              <div className="flex gap-4 text-sm">
                <span className="bg-slate-100 px-3 py-1 rounded-lg text-slate-600 font-medium">
                  {req.fecha_inicio} - {req.fecha_fin}
                </span>
                {req.dias && <span className="bg-blue-50 text-blue-600 px-3 py-1 rounded-lg font-bold">{req.dias} días</span>}
              </div>
              {req.motivo && <p className="mt-3 text-sm text-slate-600 italic">"{req.motivo}"</p>}
            </div>
            
            <div className="flex gap-3">
              <button 
                onClick={() => handleAction(type, req.id, 'approve')}
                className="bg-emerald-100 hover:bg-emerald-200 text-emerald-700 p-3 rounded-xl transition-colors"
                title="Aprobar"
              >
                <Check size={20} strokeWidth={3} />
              </button>
              <button 
                onClick={() => handleAction(type, req.id, 'reject')}
                className="bg-red-100 hover:bg-red-200 text-red-700 p-3 rounded-xl transition-colors"
                title="Rechazar"
              >
                <X size={20} strokeWidth={3} />
              </button>
            </div>
          </div>
        ))
      )}
    </div>
  );

  return (
    <div className="p-8">
      <h2 className="text-2xl font-bold text-slate-800 mb-8">Solicitudes y Permisos</h2>

      <div className="flex gap-4 mb-6 border-b border-slate-200 pb-1">
        <button 
          onClick={() => setActiveTab('vacations')}
          className={`px-6 py-3 font-bold text-sm transition-colors relative ${activeTab === 'vacations' ? 'text-primary' : 'text-slate-400 hover:text-slate-600'}`}
        >
          Vacaciones
          {vacations.length > 0 && <span className="ml-2 bg-red-500 text-white text-[10px] px-2 py-0.5 rounded-full">{vacations.length}</span>}
          {activeTab === 'vacations' && <div className="absolute bottom-[-5px] left-0 w-full h-1 bg-primary rounded-t-full"></div>}
        </button>
        <button
          onClick={() => setActiveTab('absences')}
          className={`px-6 py-3 font-bold text-sm transition-colors relative ${activeTab === 'absences' ? 'text-primary' : 'text-slate-400 hover:text-slate-600'}`}
        >
          Permisos y Ausencias
          {absences.length > 0 && <span className="ml-2 bg-red-500 text-white text-[10px] px-2 py-0.5 rounded-full">{absences.length}</span>}
          {activeTab === 'absences' && <div className="absolute bottom-[-5px] left-0 w-full h-1 bg-primary rounded-t-full"></div>}
        </button>
      </div>

      {loading ? (
        <div className="text-center py-20 text-slate-400">Cargando solicitudes...</div>
      ) : (
        <>
          {activeTab === 'vacations' && <RequestsList items={vacations} type="vacations" />}
          {activeTab === 'absences' && <RequestsList items={absences} type="absences" />}
        </>
      )}

      {/* Modal de Rechazo */}
      {showRejectModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-md p-6 animate-in zoom-in-95">
            <h3 className="text-xl font-bold text-slate-800 mb-4">Rechazar Solicitud</h3>
            <form onSubmit={confirmReject}>
              <div className="mb-4">
                <label className="block text-sm font-bold text-slate-700 mb-2">
                  Motivo del rechazo <span className="text-red-500">*</span>
                </label>
                <textarea
                  required
                  rows="3"
                  className="w-full p-3 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500 resize-none"
                  placeholder="Explica por qué se rechaza la solicitud..."
                  value={rejectReason}
                  onChange={(e) => setRejectReason(e.target.value)}
                ></textarea>
              </div>
              <div className="flex gap-3 justify-end">
                <button
                  type="button"
                  onClick={() => setShowRejectModal(false)}
                  className="px-4 py-2 text-slate-500 font-medium hover:bg-slate-100 rounded-lg transition-colors"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={!rejectReason.trim()}
                  className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white font-bold rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Confirmar Rechazo
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Alert Dialog */}
      <AlertDialog
        isOpen={alertDialog.isOpen}
        onClose={() => setAlertDialog({ isOpen: false, message: '' })}
        message={alertDialog.message}
        variant="error"
      />
    </div>
  );
}

export default Requests;
