import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Check, X, Trash2 } from 'lucide-react';
import { AlertDialog } from '../components/AlertDialog';

const API_URL = "/api";

function Requests() {
  const [activeTab, setActiveTab] = useState('pendiente'); // 'pendiente', 'aprobada', 'rechazada'
  const [subTab, setSubTab] = useState('all'); // 'all', 'vacations', 'absences'
  const [vacations, setVacations] = useState([]);
  const [absences, setAbsences] = useState([]);
  const [loading, setLoading] = useState(false);

  // Modal Rejection State
  const [showRejectModal, setShowRejectModal] = useState(false);
  const [rejectReason, setRejectReason] = useState('');
  const [selectedRequest, setSelectedRequest] = useState(null);

  // Modal Delete State
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  // Alert Dialog State
  const [alertDialog, setAlertDialog] = useState({ isOpen: false, message: '' });

  useEffect(() => {
    fetchRequests();
  }, [activeTab]);

  const fetchRequests = async () => {
    setLoading(true);
    try {
      const [vacRes, absRes] = await Promise.all([
        axios.get(`${API_URL}/requests/vacations`, { params: { status: activeTab } }),
        axios.get(`${API_URL}/requests/absences`, { params: { status: activeTab } })
      ]);
      setVacations(Array.isArray(vacRes.data) ? vacRes.data.map(v => ({ ...v, sourceType: 'vacations' })) : []);
      setAbsences(Array.isArray(absRes.data) ? absRes.data.map(a => ({ ...a, sourceType: 'absences' })) : []);
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

  const handleDelete = (type, id) => {
      setSelectedRequest({ type, id });
      setShowDeleteModal(true);
  };

  const confirmDelete = async () => {
      try {
          await axios.delete(`${API_URL}/requests/${selectedRequest.type}/${selectedRequest.id}`);
          setShowDeleteModal(false);
          fetchRequests();
      } catch (error) {
          setAlertDialog({ isOpen: true, message: "Error al eliminar solicitud: " + (error.response?.data?.detail || error.message) });
      }
  };

  const RequestsList = ({ items }) => (
    <div className="space-y-4">
      {items.length === 0 ? (
        <div className="text-center py-4 text-slate-400 italic text-sm">No hay solicitudes en esta sección.</div>
      ) : (
        items.map((req) => (
          <div key={`${req.sourceType}-${req.id}`} className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex justify-between items-center group hover:shadow-md transition-all">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                  <span className={`text-[10px] uppercase font-bold px-2 py-1 rounded-md tracking-wider ${
                      req.sourceType === 'vacations' 
                      ? 'bg-blue-100 text-blue-700 border border-blue-200' 
                      : 'bg-purple-100 text-purple-700 border border-purple-200'
                  }`}>
                      {req.tipo || (req.sourceType === 'vacations' ? 'Vacaciones' : 'Ausencia')}
                  </span>
                  
                  {req.tipo_ausencia && req.tipo_ausencia !== req.tipo && (
                      <span className="text-[10px] uppercase font-bold px-2 py-1 rounded-md bg-slate-100 text-slate-600 border border-slate-200 tracking-wider">
                          {req.tipo_ausencia.replace(/_/g, ' ')}
                      </span>
                  )}

                  <span className={`text-[10px] uppercase font-bold px-2 py-1 rounded-md tracking-wider ${
                      req.estado === 'aprobada' ? 'bg-emerald-100 text-emerald-700 border border-emerald-200' :
                      req.estado === 'rechazada' ? 'bg-red-100 text-red-700 border border-red-200' :
                      'bg-amber-100 text-amber-700 border border-amber-200'
                  }`}>
                      {req.estado || 'Pendiente'}
                  </span>
              </div>

              <h4 className="font-bold text-slate-800 text-lg mb-0.5">{req.empleado}</h4>
              <p className="text-xs text-slate-400 font-medium mb-3 uppercase tracking-wider">{req.dni}</p>
              
              <div className="flex flex-wrap gap-4 text-sm items-center">
                <div className="bg-slate-50 px-3 py-1.5 rounded-lg border border-slate-100 text-slate-700 font-medium flex items-center gap-2">
                  <span className="text-slate-400 text-xs uppercase font-bold">Fecha:</span> 
                  {req.fecha_inicio} <span className="text-slate-300">→</span> {req.fecha_fin}
                </div>
                {req.dias && <span className="bg-blue-50 text-blue-600 px-3 py-1.5 rounded-lg font-bold border border-blue-100">{req.dias} días</span>}
              </div>
              
              {req.motivo && (
                  <div className="mt-3 bg-slate-50 p-3 rounded-xl border border-slate-100 text-sm text-slate-600 italic">
                      "{req.motivo}"
                  </div>
              )}
              
              {/* Mostrar motivo de rechazo si existe */}
              {req.motivo_rechazo && (
                  <p className="mt-2 text-sm text-red-600 bg-red-50 p-3 rounded-xl border border-red-100">
                      <strong className="block text-xs uppercase mb-1 opacity-70">Motivo rechazo:</strong> {req.motivo_rechazo}
                  </p>
              )}
              {/* Mostrar observaciones admin si existe */}
              {req.observaciones_admin && (
                  <p className="mt-2 text-sm text-blue-600 bg-blue-50 p-3 rounded-xl border border-blue-100">
                      <strong className="block text-xs uppercase mb-1 opacity-70">Observaciones:</strong> {req.observaciones_admin}
                  </p>
              )}
            </div>
            
            {/* Solo mostrar botones si está en pendiente */}
            {activeTab === 'pendiente' ? (
                <div className="flex flex-col gap-2 ml-4">
                <button 
                    onClick={() => handleAction(req.sourceType, req.id, 'approve')}
                    className="bg-emerald-50 hover:bg-emerald-500 text-emerald-600 hover:text-white p-3 rounded-xl transition-all border border-emerald-200 hover:border-emerald-500 hover:shadow-lg hover:shadow-emerald-500/30 group/btn"
                    title="Aprobar"
                >
                    <Check size={20} strokeWidth={3} className="group-hover/btn:scale-110 transition-transform" />
                </button>
                <button 
                    onClick={() => handleAction(req.sourceType, req.id, 'reject')}
                    className="bg-red-50 hover:bg-red-500 text-red-600 hover:text-white p-3 rounded-xl transition-all border border-red-200 hover:border-red-500 hover:shadow-lg hover:shadow-red-500/30 group/btn"
                    title="Rechazar"
                >
                    <X size={20} strokeWidth={3} className="group-hover/btn:scale-110 transition-transform" />
                </button>
                </div>
            ) : (
                <div className="flex flex-col gap-2 ml-4">
                    <button 
                        onClick={() => handleDelete(req.sourceType, req.id)}
                        className="bg-slate-50 hover:bg-red-50 text-slate-400 hover:text-red-600 p-3 rounded-xl transition-all border border-slate-200 hover:border-red-200 group/btn"
                        title="Eliminar"
                    >
                        <Trash2 size={20} strokeWidth={2} className="group-hover/btn:scale-110 transition-transform" />
                    </button>
                </div>
            )}
          </div>
        ))
      )}
    </div>
  );

  return (
    <div className="p-8">
      <h2 className="text-2xl font-bold text-slate-800 mb-8">Solicitudes y Permisos</h2>

      <div className="flex gap-4 mb-4 border-b border-slate-200 pb-1">
        {['pendiente', 'aprobada', 'rechazada'].map(tab => (
            <button 
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-6 py-3 font-bold text-sm transition-colors relative capitalize ${activeTab === tab ? 'text-primary' : 'text-slate-400 hover:text-slate-600'}`}
            >
            {tab === 'pendiente' ? 'Pendientes' : tab === 'aprobada' ? 'Aprobadas' : 'Rechazadas'}
            {/* Badge de contador total para la pestaña activa */}
            {activeTab === tab && (vacations.length + absences.length) > 0 && (
                <span className={`ml-2 text-white text-[10px] px-2 py-0.5 rounded-full ${
                    tab === 'pendiente' ? 'bg-amber-500' : 
                    tab === 'aprobada' ? 'bg-emerald-500' : 'bg-red-500'
                }`}>
                    {vacations.length + absences.length}
                </span>
            )}
            {activeTab === tab && <div className="absolute bottom-[-5px] left-0 w-full h-1 bg-primary rounded-t-full"></div>}
            </button>
        ))}
      </div>

      {/* Sub-Tabs Dinámicas */}
      <div className="flex gap-2 mb-6">
        <button 
            onClick={() => setSubTab('all')}
            className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all ${subTab === 'all' ? 'bg-slate-800 text-white shadow-md' : 'bg-white border border-slate-200 text-slate-500 hover:bg-slate-50'}`}
        >
            Todo
        </button>
        <button 
            onClick={() => setSubTab('vacations')}
            className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-2 ${subTab === 'vacations' ? 'bg-blue-600 text-white shadow-md shadow-blue-200' : 'bg-white border border-slate-200 text-slate-500 hover:bg-slate-50'}`}
        >
            Vacaciones 
            <span className={`px-1.5 py-0.5 rounded text-[9px] ${subTab === 'vacations' ? 'bg-white/20 text-white' : 'bg-slate-100 text-slate-600'}`}>
                {vacations.length}
            </span>
        </button>
        <button 
            onClick={() => setSubTab('absences')}
            className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-2 ${subTab === 'absences' ? 'bg-purple-600 text-white shadow-md shadow-purple-200' : 'bg-white border border-slate-200 text-slate-500 hover:bg-slate-50'}`}
        >
            Permisos
            <span className={`px-1.5 py-0.5 rounded text-[9px] ${subTab === 'absences' ? 'bg-white/20 text-white' : 'bg-slate-100 text-slate-600'}`}>
                {absences.length}
            </span>
        </button>
      </div>

      {loading ? (
        <div className="text-center py-20 text-slate-400">Cargando solicitudes...</div>
      ) : (
        <div className="animate-in fade-in slide-in-from-bottom-2 duration-300">
            {/* Lista Unificada o Filtrada */}
            {(() => {
                let itemsToShow = [];
                if (subTab === 'all') {
                    // Mezclar y ordenar por fecha (aunque ya deberían venir ordenados, al mezclar se pierde el orden relativo entre tipos si no se reordena)
                    // Como el backend las trae ordenadas DESC, podemos simplemente concatenar y reordenar o asumir que no importa tanto el orden estricto entre tipos
                    // Para mejor experiencia, ordenemos por fecha_inicio o fecha_solicitud si existiera consistente.
                    // Usaremos fecha_inicio como proxy de orden visual.
                    itemsToShow = [...vacations, ...absences].sort((a, b) => new Date(b.fecha_inicio) - new Date(a.fecha_inicio));
                } else if (subTab === 'vacations') {
                    itemsToShow = vacations;
                } else if (subTab === 'absences') {
                    itemsToShow = absences;
                }

                if (itemsToShow.length === 0) {
                    return (
                        <div className="text-center py-20 bg-slate-50 rounded-3xl border border-dashed border-slate-200">
                            <p className="text-slate-400 text-sm">No hay solicitudes de <span className="font-bold text-slate-500">{subTab === 'all' ? 'ningún tipo' : subTab === 'vacations' ? 'vacaciones' : 'permisos'}</span> en estado <span className="font-bold text-slate-500">{activeTab}</span></p>
                        </div>
                    );
                }

                return <RequestsList items={itemsToShow} />;
            })()}
        </div>
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

      {/* Modal de Eliminar */}
      {showDeleteModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-sm p-6 animate-in zoom-in-95">
            <h3 className="text-xl font-bold text-slate-800 mb-2">Eliminar Solicitud</h3>
            <p className="text-slate-600 mb-6 text-sm">
                ¿Estás seguro de que deseas eliminar esta solicitud? Esta acción no se puede deshacer.
            </p>
            <div className="flex gap-3 justify-end">
              <button
                type="button"
                onClick={() => setShowDeleteModal(false)}
                className="px-4 py-2 text-slate-500 font-medium hover:bg-slate-100 rounded-lg transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={confirmDelete}
                className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white font-bold rounded-lg transition-colors"
              >
                Eliminar
              </button>
            </div>
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
