import React, { useState, useEffect, useRef } from 'react';
import { Clock, LogOut, Coffee, ArrowRight, AlertTriangle, CheckCircle, Calendar, Briefcase, Lock, Bell, X } from 'lucide-react';
import axios from 'axios';

const API_URL = "/api";

function EmployeeDashboard({ user, onLogout }) {
  const [status, setStatus] = useState('loading'); // loading, not_working, working, on_break, completed, working_overtime
  const [fichaje, setFichaje] = useState(null);
  const [currentTime, setCurrentTime] = useState(new Date());
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Modal states
  const [showClassificationModal, setShowClassificationModal] = useState(false);
  const [showOvertimeModal, setShowOvertimeModal] = useState(false);
  const [showVacationModal, setShowVacationModal] = useState(false);
  const [showAbsenceModal, setShowAbsenceModal] = useState(false);
  const [showForcedJustificationModal, setShowForcedJustificationModal] = useState(false);
  const [showHistoryModal, setShowHistoryModal] = useState(false);
  const [historyType, setHistoryType] = useState('vacation'); // 'vacation' | 'absence'
  
  const [notifications, setNotifications] = useState([]);
  const [showNotifications, setShowNotifications] = useState(false);
  
  const [overtimePin, setOvertimePin] = useState('');
  
  // Data states
  const [vacationBalance, setVacationBalance] = useState({ total: 0, consumido: 0, pendiente: 0 });
  const [vacationHistory, setVacationHistory] = useState([]);
  const [absenceHistory, setAbsenceHistory] = useState([]);
  const [pendingAbsenceData, setPendingAbsenceData] = useState(null);
  
  // Forms
  const [vacationForm, setVacationForm] = useState({ start: '', end: '', type: 'vacaciones_anuales', reason: '' });
  const [absenceForm, setAbsenceForm] = useState({ start: '', end: '', type: 'baja_medica', subtype: '', impact: 'it', reason: '' });
  const [forcedJustificationForm, setForcedJustificationForm] = useState({ type: 'ausencia_injustificada', reason: '' });

  // Auto-logout timer
  const logoutTimerRef = useRef(null);

  useEffect(() => {
    // Clock tick
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    
    // Fetch initial status
    fetchStatus();
    fetchNotifications();

    // Setup auto-logout (reset on interaction)
    resetLogoutTimer();
    window.addEventListener('mousemove', resetLogoutTimer);
    window.addEventListener('keypress', resetLogoutTimer);
    window.addEventListener('click', resetLogoutTimer);

    return () => {
      clearInterval(timer);
      if (logoutTimerRef.current) clearTimeout(logoutTimerRef.current);
      window.removeEventListener('mousemove', resetLogoutTimer);
      window.removeEventListener('keypress', resetLogoutTimer);
      window.removeEventListener('click', resetLogoutTimer);
    };
  }, []);

  const resetLogoutTimer = () => {
    if (logoutTimerRef.current) clearTimeout(logoutTimerRef.current);
    logoutTimerRef.current = setTimeout(() => {
      onLogout();
    }, 60000); // 60 seconds inactivity timeout
  };

  const fetchStatus = async () => {
    try {
      const response = await axios.get(`${API_URL}/attendance/status/${user.id}`);
      setStatus(response.data.status);
      setFichaje(response.data.fichaje);
      
      // Check blockage info from backend pre-validation
      if (response.data.is_blocked && response.data.absence_info) {
          setPendingAbsenceData(response.data.absence_info);
      } else {
          setPendingAbsenceData(null);
      }
    } catch (err) {
      console.error("Error fetching status:", err);
      setError("Error al conectar con el servidor");
    }
  };

  const fetchNotifications = async () => {
    try {
        const res = await axios.get(`${API_URL}/notifications/employee/${user.id}`);
        setNotifications(res.data);
    } catch (err) {
        console.error("Error fetching notifications", err);
    }
  };

  const fetchVacationData = async () => {
    try {
      const year = new Date().getFullYear();
      const balanceRes = await axios.get(`${API_URL}/requests/employee/${user.id}/vacation-balance/${year}`);
      setVacationBalance(balanceRes.data);
      
      const historyRes = await axios.get(`${API_URL}/requests/employee/${user.id}/vacations`);
      setVacationHistory(historyRes.data);
    } catch (err) {
      console.error(err);
    }
  };

  const fetchAbsenceData = async () => {
    try {
      const res = await axios.get(`${API_URL}/requests/employee/${user.id}/absences`);
      setAbsenceHistory(res.data.history);
    } catch (err) {
      console.error(err);
    }
  };

  const submitVacation = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await axios.post(`${API_URL}/requests/vacations`, {
        employee_id: user.id,
        fecha_inicio: vacationForm.start,
        fecha_fin: vacationForm.end,
        tipo: vacationForm.type,
        motivo: vacationForm.reason
      });
      setSuccess("Solicitud de vacaciones enviada");
      setShowVacationModal(false);
      setVacationForm({ start: '', end: '', type: 'vacaciones_anuales', reason: '' });
    } catch (err) {
      setError(err.response?.data?.detail || "Error al enviar solicitud");
    } finally {
      setLoading(false);
    }
  };

  const submitAbsence = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await axios.post(`${API_URL}/requests/absences`, {
        employee_id: user.id,
        fecha_inicio: absenceForm.start,
        fecha_fin: absenceForm.end,
        tipo: absenceForm.type,
        subtipo: absenceForm.subtype,
        motivo: absenceForm.reason,
        impacta_nomina: absenceForm.impact
      });
      setSuccess("Notificación de ausencia enviada");
      setShowAbsenceModal(false);
      setAbsenceForm({ start: '', end: '', type: 'baja_medica', subtype: '', impact: 'it', reason: '' });
    } catch (err) {
      setError(err.response?.data?.detail || "Error al enviar notificación");
    } finally {
      setLoading(false);
    }
  };

  const handleClockAction = async (action, type = "normal", pin = null) => {
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const payload = {
        employee_id: user.id,
        action: action,
        type: type,
        pin: pin
      };

      const response = await axios.post(`${API_URL}/attendance/clock`, payload);
      
      setSuccess(response.data.message);
      await fetchStatus();
      
      // Close modals
      setShowClassificationModal(false);
      setShowOvertimeModal(false);
      setOvertimePin('');

    } catch (err) {
        if (err.response && err.response.status === 409) {
            // Bloqueo por ausencias
            const absenceData = err.response.data.absence_data;
            setPendingAbsenceData(absenceData);
            setShowClassificationModal(false); // Cerrar otros
            setShowForcedJustificationModal(true);
        } else {
            setError(err.response?.data?.detail || "Error al registrar fichaje");
        }
    } finally {
      setLoading(false);
    }
  };

  const submitForcedJustification = async (e) => {
      e.preventDefault();
      setLoading(true);
      setError('');
      
      try {
          await axios.post(`${API_URL}/attendance/justify`, {
              employee_id: user.id,
              tipo: forcedJustificationForm.type,
              motivo: forcedJustificationForm.reason,
              fecha_inicio: pendingAbsenceData.start_date,
              fecha_fin: pendingAbsenceData.end_date
          });
          
          setSuccess("Ausencia justificada correctamente. Fichaje registrado.");
          setShowForcedJustificationModal(false);
          setPendingAbsenceData(null);
          setForcedJustificationForm({ type: 'ausencia_injustificada', reason: '' });
          
          await fetchStatus(); // Refrescar para ver que ya entró
          
      } catch (err) {
          setError(err.response?.data?.detail || "Error al justificar");
      } finally {
          setLoading(false);
      }
  };

  const handleEntryClick = async () => {
    // Check cached blockage first
    if (pendingAbsenceData) {
        setShowForcedJustificationModal(true);
        return;
    }

    // Double check with server to be sure before showing classification
    setLoading(true);
    try {
        const response = await axios.get(`${API_URL}/attendance/status/${user.id}`);
        const data = response.data;
        
        if (data.is_blocked && data.absence_info) {
            setPendingAbsenceData(data.absence_info);
            setShowForcedJustificationModal(true);
            return;
        }
        
        // If not blocked, proceed
        if (status === 'completed') {
            setShowOvertimeModal(true);
        } else {
            setShowClassificationModal(true);
        }
    } catch (err) {
        console.error("Error verifying status:", err);
        // Fallback to allowing entry if server check fails (or show error)
        setError("Error verificando estado. Inténtalo de nuevo.");
    } finally {
        setLoading(false);
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'working': return 'text-emerald-600';
      case 'on_break': return 'text-amber-600';
      case 'completed': return 'text-blue-600';
      case 'working_overtime': return 'text-purple-600';
      default: return 'text-slate-600';
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'working': return 'Trabajando';
      case 'on_break': return 'En Break';
      case 'completed': return 'Jornada Completada';
      case 'working_overtime': return 'Trabajando (Horas Extra)';
      default: return 'Sin fichar hoy';
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      {/* Header */}
      <header className="bg-white shadow-sm p-4 flex justify-between items-center">
        <div className="flex items-center gap-3">
          <div className="bg-primary/10 p-2 rounded-lg text-primary">
            <Clock size={24} />
          </div>
          <div>
            <h1 className="font-bold text-lg text-slate-800">{user.nombre} {user.apellidos}</h1>
            <p className="text-xs text-slate-500 capitalize">{user.tipo_jornada}</p>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
            <div className="relative">
                <button 
                    onClick={() => setShowNotifications(!showNotifications)}
                    className="p-2.5 hover:bg-slate-100 rounded-full relative transition-colors text-slate-500"
                >
                    <Bell size={20} />
                    {notifications.length > 0 && (
                        <span className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full ring-2 ring-white"></span>
                    )}
                </button>

                {showNotifications && (
                    <div className="absolute right-0 top-full mt-2 w-80 bg-white rounded-2xl shadow-xl border border-slate-100 z-50 overflow-hidden animate-in fade-in slide-in-from-top-2">
                        <div className="p-4 border-b border-slate-50 flex justify-between items-center">
                            <h4 className="font-bold text-slate-800">Notificaciones</h4>
                            <span className="text-xs text-slate-400">{notifications.length} nuevas</span>
                        </div>
                        <div className="max-h-80 overflow-y-auto">
                            {notifications.length === 0 ? (
                                <div className="p-8 text-center text-slate-400 text-sm">
                                    No hay notificaciones
                                </div>
                            ) : (
                                <div className="divide-y divide-slate-50">
                                    {notifications.map(notif => (
                                        <div key={notif.id} className="p-4 hover:bg-slate-50 transition-colors cursor-pointer flex gap-3">
                                            <div className={`mt-1 w-2 h-2 rounded-full flex-shrink-0 ${notif.type === 'success' ? 'bg-emerald-500' : 'bg-red-500'}`}></div>
                                            <div>
                                                <h5 className="text-sm font-bold text-slate-700">{notif.title}</h5>
                                                <p className="text-xs text-slate-500 mt-0.5">{notif.desc}</p>
                                                <span className="text-[10px] text-slate-400 font-medium mt-2 block">{notif.time}</span>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                )}
            </div>
            
            <button 
            onClick={onLogout}
            className="flex items-center gap-2 text-slate-500 hover:text-red-600 transition-colors px-4 py-2 rounded-lg hover:bg-red-50"
            >
            <LogOut size={20} />
            <span className="hidden sm:inline">Salir</span>
            </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 container mx-auto p-4 max-w-4xl flex flex-col gap-6">
        
        {/* Clock & Status */}
        <div className="bg-white rounded-3xl shadow-sm border border-slate-100 p-8 text-center relative overflow-hidden">
          <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-primary via-purple-500 to-emerald-500"></div>
          
          <p className="text-slate-400 text-lg mb-2 capitalize">
            {currentTime.toLocaleDateString('es-ES', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
          </p>
          <h2 className="text-6xl font-bold text-slate-800 font-mono tracking-tight mb-4">
            {currentTime.toLocaleTimeString('es-ES')}
          </h2>
          
          <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full bg-slate-100 ${getStatusColor()} font-bold text-sm`}>
            <div className={`w-2 h-2 rounded-full bg-current animate-pulse`}></div>
            {getStatusText()}
          </div>

          {fichaje && (
            <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm border-t border-slate-100 pt-6">
              <div>
                <p className="text-slate-400 mb-1">Entrada</p>
                <p className="font-bold text-slate-700">{fichaje.hora_entrada || '--:--'}</p>
              </div>
              <div>
                <p className="text-slate-400 mb-1">Salida</p>
                <p className="font-bold text-slate-700">{fichaje.hora_salida || '--:--'}</p>
              </div>
              <div className="col-span-2 md:col-span-2">
                <p className="text-slate-400 mb-1">Tipo</p>
                <p className="font-bold text-slate-700 capitalize">{fichaje.tipo?.replace('_', ' ') || 'Normal'}</p>
              </div>
            </div>
          )}
        </div>

        {/* Actions Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <button
            onClick={handleEntryClick}
            disabled={status === 'loading' || status === 'working' || status === 'on_break' || status === 'working_overtime' || loading}
            className="group relative overflow-hidden bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-200 disabled:cursor-not-allowed text-white p-6 rounded-2xl shadow-lg shadow-emerald-600/20 transition-all flex flex-col items-center gap-3"
          >
            <div className="bg-white/20 p-3 rounded-xl group-hover:scale-110 transition-transform">
              <CheckCircle size={32} />
            </div>
            <span className="font-bold text-lg">Entrada</span>
          </button>

          <button
            onClick={() => handleClockAction('break_start')}
            disabled={status !== 'working' || loading || user.tipo_jornada === 'parcial'}
            className="group relative overflow-hidden bg-amber-500 hover:bg-amber-600 disabled:bg-slate-200 disabled:cursor-not-allowed text-white p-6 rounded-2xl shadow-lg shadow-amber-500/20 transition-all flex flex-col items-center gap-3"
          >
            <div className="bg-white/20 p-3 rounded-xl group-hover:scale-110 transition-transform">
              <Coffee size={32} />
            </div>
            <span className="font-bold text-lg">Salir a Break</span>
          </button>

          <button
            onClick={() => handleClockAction('break_end')}
            disabled={status !== 'on_break' || loading}
            className="group relative overflow-hidden bg-amber-600 hover:bg-amber-700 disabled:bg-slate-200 disabled:cursor-not-allowed text-white p-6 rounded-2xl shadow-lg shadow-amber-600/20 transition-all flex flex-col items-center gap-3"
          >
            <div className="bg-white/20 p-3 rounded-xl group-hover:scale-110 transition-transform">
              <ArrowRight size={32} />
            </div>
            <span className="font-bold text-lg">Volver de Break</span>
          </button>

          <button
            onClick={() => handleClockAction('exit')}
            disabled={(status !== 'working' && status !== 'working_overtime') || loading}
            className="group relative overflow-hidden bg-red-600 hover:bg-red-700 disabled:bg-slate-200 disabled:cursor-not-allowed text-white p-6 rounded-2xl shadow-lg shadow-red-600/20 transition-all flex flex-col items-center gap-3"
          >
            <div className="bg-white/20 p-3 rounded-xl group-hover:scale-110 transition-transform">
              <LogOut size={32} />
            </div>
            <span className="font-bold text-lg">Salida</span>
          </button>
        </div>

        {/* Quick Links */}
        <div className="grid grid-cols-2 gap-4">
          <button 
            onClick={() => {
              fetchVacationData();
              setShowVacationModal(true);
            }}
            className="bg-white p-4 rounded-xl border border-slate-100 hover:border-primary/50 hover:shadow-md transition-all flex items-center gap-3 group"
          >
            <div className="bg-blue-50 text-blue-600 p-2 rounded-lg group-hover:bg-blue-600 group-hover:text-white transition-colors">
              <Calendar size={20} />
            </div>
            <div className="text-left">
              <p className="font-bold text-slate-700">Mis Vacaciones</p>
              <p className="text-xs text-slate-400">Ver saldo y solicitar</p>
            </div>
          </button>
          <button 
            onClick={() => {
              fetchAbsenceData();
              setShowAbsenceModal(true);
            }}
            className="bg-white p-4 rounded-xl border border-slate-100 hover:border-primary/50 hover:shadow-md transition-all flex items-center gap-3 group"
          >
            <div className="bg-purple-50 text-purple-600 p-2 rounded-lg group-hover:bg-purple-600 group-hover:text-white transition-colors">
              <Briefcase size={20} />
            </div>
            <div className="text-left">
              <p className="font-bold text-slate-700">Mis Ausencias</p>
              <p className="text-xs text-slate-400">Justificar o notificar</p>
            </div>
          </button>
        </div>

        {/* Messages */}
        {error && (
          <div className="bg-red-50 text-red-700 p-4 rounded-xl flex items-center gap-3 animate-in slide-in-from-bottom-2">
            <AlertTriangle size={20} />
            <p className="font-medium">{error}</p>
          </div>
        )}
        
        {success && (
          <div className="bg-emerald-50 text-emerald-700 p-4 rounded-xl flex items-center gap-3 animate-in slide-in-from-bottom-2">
            <CheckCircle size={20} />
            <p className="font-medium">{success}</p>
          </div>
        )}

      </main>

      {/* Modal Classification */}
      {showClassificationModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl shadow-2xl w-full max-w-md p-6 animate-in zoom-in-95">
            <h3 className="text-xl font-bold text-slate-800 mb-4">Clasificar Jornada</h3>
            <p className="text-slate-500 text-sm mb-6">Selecciona el tipo de día para este fichaje:</p>
            
            <div className="grid gap-3">
              {[
                { id: 'normal', label: 'Día Normal', icon: '☀️' },
                { id: 'feriado', label: 'Feriado', icon: '🎉' },
                { id: 'fin_semana', label: 'Fin de Semana', icon: '📅' },
                { id: 'salida_vacaciones', label: 'Salida Vacaciones', icon: '✈️' },
                { id: 'entrada_vacaciones', label: 'Vuelta Vacaciones', icon: '🏠' },
              ].map((type) => (
                <button
                  key={type.id}
                  onClick={() => handleClockAction('entry', type.id)}
                  className="w-full text-left p-4 rounded-xl border border-slate-200 hover:border-primary hover:bg-primary/5 transition-all flex items-center gap-3 group"
                >
                  <span className="text-2xl">{type.icon}</span>
                  <span className="font-medium text-slate-700 group-hover:text-primary">{type.label}</span>
                </button>
              ))}
            </div>
            
            <button 
              onClick={() => setShowClassificationModal(false)}
              className="mt-6 w-full py-3 text-slate-500 font-medium hover:text-slate-800"
            >
              Cancelar
            </button>
          </div>
        </div>
      )}

      {/* Modal Overtime */}
      {showOvertimeModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl shadow-2xl w-full max-w-md p-6 animate-in zoom-in-95">
            <div className="flex items-center gap-3 mb-4 text-purple-600">
              <Clock size={24} />
              <h3 className="text-xl font-bold">Horas Extras</h3>
            </div>
            
            <div className="bg-purple-50 p-4 rounded-xl mb-6">
              <p className="text-sm text-purple-800">
                Para registrar horas extras es necesaria la aprobación de un administrador.
              </p>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">PIN de Administrador</label>
                <input
                  type="password"
                  value={overtimePin}
                  onChange={(e) => setOvertimePin(e.target.value)}
                  className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-purple-500/20 focus:border-purple-500 text-center text-2xl tracking-widest font-mono"
                  placeholder="••••••"
                  maxLength={6}
                  autoFocus
                />
              </div>

              <button
                onClick={() => handleClockAction('entry', 'horas_extra', overtimePin)}
                disabled={overtimePin.length < 4 || loading}
                className="w-full bg-purple-600 hover:bg-purple-700 disabled:opacity-50 text-white py-3.5 rounded-xl font-bold shadow-lg shadow-purple-600/30 transition-all"
              >
                {loading ? 'Verificando...' : 'Aprobar y Fichar'}
              </button>
            </div>
            
            <button 
              onClick={() => {
                setShowOvertimeModal(false);
                setOvertimePin('');
              }}
              className="mt-6 w-full py-3 text-slate-500 font-medium hover:text-slate-800"
            >
              Cancelar
            </button>
          </div>
        </div>
      )}

      {/* Modal Vacaciones */}
      {showVacationModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl shadow-2xl w-full max-w-2xl p-6 animate-in zoom-in-95 h-[80vh] flex flex-col">
            <h3 className="text-xl font-bold text-slate-800 mb-4 flex items-center gap-2">
              <Calendar className="text-blue-600" /> Mis Vacaciones
            </h3>
            
            <div className="grid grid-cols-3 gap-4 mb-6">
              <div className="bg-blue-50 p-3 rounded-xl text-center">
                <p className="text-xs text-blue-600 font-bold uppercase">Total</p>
                <p className="text-2xl font-bold text-slate-700">{vacationBalance.total}</p>
              </div>
              <div className="bg-orange-50 p-3 rounded-xl text-center">
                <p className="text-xs text-orange-600 font-bold uppercase">Consumido</p>
                <p className="text-2xl font-bold text-slate-700">{vacationBalance.consumido}</p>
              </div>
              <div className="bg-emerald-50 p-3 rounded-xl text-center">
                <p className="text-xs text-emerald-600 font-bold uppercase">Disponible</p>
                <p className="text-2xl font-bold text-slate-700">{vacationBalance.pendiente}</p>
              </div>
            </div>

            <div className="mb-6">
              <h4 className="font-bold text-slate-700 mb-3 text-sm uppercase">Historial</h4>
              <button 
                onClick={() => {
                    setHistoryType('vacation');
                    setShowHistoryModal(true);
                }}
                className="w-full py-4 border border-slate-200 rounded-xl text-slate-600 font-medium hover:bg-slate-50 transition-colors flex items-center justify-center gap-2"
              >
                <Calendar size={20} />
                Ver Historial Completo ({vacationHistory.length})
              </button>
            </div>

            <form onSubmit={submitVacation} className="border-t border-slate-100 pt-4">
              <h4 className="font-bold text-slate-700 mb-3 text-sm uppercase">Nueva Solicitud</h4>
              <div className="grid grid-cols-2 gap-3 mb-3">
                <div>
                  <label className="text-xs font-bold text-slate-500">Desde</label>
                  <input 
                    type="date" 
                    required 
                    className="w-full p-2 border border-slate-200 rounded-lg text-sm"
                    value={vacationForm.start}
                    onChange={e => setVacationForm({...vacationForm, start: e.target.value})}
                  />
                </div>
                <div>
                  <label className="text-xs font-bold text-slate-500">Hasta</label>
                  <input 
                    type="date" 
                    required 
                    className="w-full p-2 border border-slate-200 rounded-lg text-sm"
                    value={vacationForm.end}
                    onChange={e => setVacationForm({...vacationForm, end: e.target.value})}
                  />
                </div>
              </div>
              <div className="mb-3">
                <label className="text-xs font-bold text-slate-500">Motivo</label>
                <input 
                  type="text" 
                  className="w-full p-2 border border-slate-200 rounded-lg text-sm"
                  placeholder="Opcional"
                  value={vacationForm.reason}
                  onChange={e => setVacationForm({...vacationForm, reason: e.target.value})}
                />
              </div>
              <div className="flex gap-3">
                <button 
                  type="button" 
                  onClick={() => setShowVacationModal(false)}
                  className="flex-1 py-2 text-slate-500 text-sm font-bold hover:bg-slate-50 rounded-lg"
                >
                  Cancelar
                </button>
                <button 
                  type="submit" 
                  disabled={loading}
                  className="flex-1 py-2 bg-blue-600 text-white text-sm font-bold rounded-lg hover:bg-blue-700"
                >
                  Enviar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal Ausencias */}
      {showAbsenceModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl shadow-2xl w-full max-w-2xl p-6 animate-in zoom-in-95 h-[80vh] flex flex-col">
            <h3 className="text-xl font-bold text-slate-800 mb-4 flex items-center gap-2">
              <Briefcase className="text-purple-600" /> Mis Ausencias
            </h3>

            <div className="mb-6">
              <h4 className="font-bold text-slate-700 mb-3 text-sm uppercase">Historial</h4>
              <button 
                onClick={() => {
                    setHistoryType('absence');
                    setShowHistoryModal(true);
                }}
                className="w-full py-4 border border-slate-200 rounded-xl text-slate-600 font-medium hover:bg-slate-50 transition-colors flex items-center justify-center gap-2"
              >
                <Briefcase size={20} />
                Ver Historial Completo ({absenceHistory.length})
              </button>
            </div>

            <form onSubmit={submitAbsence} className="border-t border-slate-100 pt-4">
              <h4 className="font-bold text-slate-700 mb-3 text-sm uppercase">Notificar Ausencia Futura</h4>
              <div className="grid grid-cols-2 gap-3 mb-3">
                <div>
                  <label className="text-xs font-bold text-slate-500">Desde</label>
                  <input 
                    type="date" 
                    required 
                    className="w-full p-2 border border-slate-200 rounded-lg text-sm"
                    value={absenceForm.start}
                    onChange={e => setAbsenceForm({...absenceForm, start: e.target.value})}
                  />
                </div>
                <div>
                  <label className="text-xs font-bold text-slate-500">Hasta</label>
                  <input 
                    type="date" 
                    required 
                    className="w-full p-2 border border-slate-200 rounded-lg text-sm"
                    value={absenceForm.end}
                    onChange={e => setAbsenceForm({...absenceForm, end: e.target.value})}
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3 mb-3">
                <div>
                  <label className="text-xs font-bold text-slate-500">Tipo</label>
                  <select 
                    className="w-full p-2 border border-slate-200 rounded-lg text-sm"
                    value={absenceForm.type}
                    onChange={e => setAbsenceForm({...absenceForm, type: e.target.value})}
                  >
                    <option value="baja_medica">Baja Médica</option>
                    <option value="permiso_retribuido">Permiso Retribuido</option>
                    <option value="permiso_no_retribuido">Permiso Sin Sueldo</option>
                  </select>
                </div>
                <div>
                  <label className="text-xs font-bold text-slate-500">Impacto</label>
                  <select 
                    className="w-full p-2 border border-slate-200 rounded-lg text-sm"
                    value={absenceForm.impact}
                    onChange={e => setAbsenceForm({...absenceForm, impact: e.target.value})}
                  >
                    <option value="it">IT (Incapacidad)</option>
                    <option value="remunerado">Remunerado</option>
                    <option value="no_remunerado">No Remunerado</option>
                  </select>
                </div>
              </div>
              <div className="mb-3">
                <label className="text-xs font-bold text-slate-500">Motivo</label>
                <input 
                  type="text" 
                  required
                  className="w-full p-2 border border-slate-200 rounded-lg text-sm"
                  placeholder="Justificación"
                  value={absenceForm.reason}
                  onChange={e => setAbsenceForm({...absenceForm, reason: e.target.value})}
                />
              </div>
              <div className="flex gap-3">
                <button 
                  type="button" 
                  onClick={() => setShowAbsenceModal(false)}
                  className="flex-1 py-2 text-slate-500 text-sm font-bold hover:bg-slate-50 rounded-lg"
                >
                  Cancelar
                </button>
                <button 
                  type="submit" 
                  disabled={loading}
                  className="flex-1 py-2 bg-purple-600 text-white text-sm font-bold rounded-lg hover:bg-purple-700"
                >
                  Enviar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

       {/* Modal Justificación Forzada */}
       {showForcedJustificationModal && pendingAbsenceData && (
          <div className="fixed inset-0 bg-red-900/50 backdrop-blur-md z-[60] flex items-center justify-center p-4">
              <div className="bg-white rounded-3xl shadow-2xl w-full max-w-md p-8 animate-in zoom-in-95 border-2 border-red-500">
                  <div className="flex flex-col items-center mb-6">
                      <div className="bg-red-100 p-4 rounded-full text-red-600 mb-4">
                          <AlertTriangle size={48} strokeWidth={2} />
                      </div>
                      <h3 className="text-2xl font-bold text-slate-900 text-center">Fichaje Bloqueado</h3>
                      <p className="text-slate-600 text-center mt-2">
                          No has registrado actividad desde el <span className="font-bold text-slate-800">{pendingAbsenceData.start_date}</span> hasta el <span className="font-bold text-slate-800">{pendingAbsenceData.end_date}</span>.
                      </p>
                      <p className="text-sm text-red-600 font-medium mt-2">
                          Debes justificar estas {pendingAbsenceData.count} faltas para continuar.
                      </p>
                  </div>

                  <form onSubmit={submitForcedJustification} className="space-y-4">
                      <div>
                          <label className="block text-sm font-bold text-slate-700 mb-1">Tipo de Justificación</label>
                          <select 
                              className="w-full p-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500"
                              value={forcedJustificationForm.type}
                              onChange={e => setForcedJustificationForm({...forcedJustificationForm, type: e.target.value})}
                          >
                              <option value="ausencia_injustificada">Ausencia Injustificada</option>
                              <option value="llegada_tarde">Llegada Tarde</option>
                              <option value="baja_medica">Baja Médica</option>
                              <option value="permiso_retribuido">Permiso Retribuido</option>
                              <option value="permiso_no_retribuido">Permiso No Retribuido</option>
                              <option value="olvido_fichaje">Olvidé Fichar</option>
                          </select>
                      </div>

                      <div>
                          <label className="block text-sm font-bold text-slate-700 mb-1">Motivo / Explicación</label>
                          <textarea 
                              required
                              rows="3"
                              className="w-full p-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500 resize-none"
                              placeholder="Describe la razón de tu ausencia..."
                              value={forcedJustificationForm.reason}
                              onChange={e => setForcedJustificationForm({...forcedJustificationForm, reason: e.target.value})}
                          ></textarea>
                      </div>

                      <div className="pt-4">
                          <button 
                              type="submit" 
                              disabled={loading}
                              className="w-full bg-red-600 hover:bg-red-700 text-white py-4 rounded-xl font-bold shadow-lg shadow-red-600/30 transition-all flex items-center justify-center gap-2"
                          >
                              {loading ? 'Procesando...' : (
                                  <><span>Enviar y Fichar Entrada</span> <ArrowRight size={20} /></>
                              )}
                          </button>
                      </div>
                  </form>
              </div>
          </div>
      )}

      {/* Modal Historial Completo */}
      {showHistoryModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl shadow-2xl w-full max-w-3xl p-6 animate-in zoom-in-95 h-[80vh] flex flex-col">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-bold text-slate-800 flex items-center gap-2">
                {historyType === 'vacation' ? <Calendar className="text-blue-600" /> : <Briefcase className="text-purple-600" />}
                Historial de {historyType === 'vacation' ? 'Vacaciones' : 'Ausencias'}
              </h3>
              <button 
                onClick={() => setShowHistoryModal(false)}
                className="p-2 hover:bg-slate-100 rounded-full transition-colors"
              >
                <X size={24} className="text-slate-400" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto pr-2">
              {(historyType === 'vacation' ? vacationHistory : absenceHistory).length === 0 ? (
                <div className="text-center py-20 text-slate-400">
                  <p>No hay registros en el historial</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {(historyType === 'vacation' ? vacationHistory : absenceHistory).map((req) => (
                    <div key={req.id} className="border border-slate-100 p-4 rounded-xl hover:shadow-md transition-all">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <p className="font-bold text-slate-700 text-lg">
                            {req.fecha_inicio} - {req.fecha_fin}
                          </p>
                          <p className="text-sm text-slate-500 capitalize flex items-center gap-2">
                            {req.tipo?.replace(/_/g, ' ')}
                            {req.dias && <span className="bg-slate-100 px-2 py-0.5 rounded text-xs font-bold">{req.dias} días</span>}
                          </p>
                        </div>
                        <span className={`px-3 py-1 rounded-lg text-xs font-bold capitalize ${
                          req.estado === 'pendiente' || req.estado === 'pendiente_justificar' ? 'bg-orange-100 text-orange-700' :
                          req.estado === 'aprobada' || req.estado === 'justificada' || req.estado === 'notificada' ? 'bg-emerald-100 text-emerald-700' :
                          'bg-red-100 text-red-700'
                        }`}>
                          {req.estado?.replace(/_/g, ' ')}
                        </span>
                      </div>
                      
                      {req.motivo_empleado && (
                        <div className="mt-2 text-sm text-slate-600 bg-slate-50 p-2 rounded-lg">
                          <span className="font-bold text-slate-400 text-xs block uppercase mb-1">Motivo Solicitud</span>
                          {req.motivo_empleado}
                        </div>
                      )}

                      {req.estado === 'rechazada' && req.motivo_rechazo && (
                        <div className="mt-2 text-sm text-red-600 bg-red-50 p-2 rounded-lg border border-red-100">
                          <span className="font-bold text-red-400 text-xs block uppercase mb-1">Motivo Rechazo</span>
                          {req.motivo_rechazo}
                        </div>
                      )}
                      
                      {req.observaciones_admin && req.estado !== 'rechazada' && (
                         <div className="mt-2 text-sm text-blue-600 bg-blue-50 p-2 rounded-lg border border-blue-100">
                          <span className="font-bold text-blue-400 text-xs block uppercase mb-1">Observaciones Admin</span>
                          {req.observaciones_admin}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
            
            <div className="pt-4 border-t border-slate-100 mt-4">
                <button 
                  onClick={() => setShowHistoryModal(false)}
                  className="w-full py-3 bg-slate-100 hover:bg-slate-200 text-slate-600 font-bold rounded-xl transition-colors"
                >
                  Cerrar
                </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}

export default EmployeeDashboard;
