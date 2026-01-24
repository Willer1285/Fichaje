import React, { useState, useEffect, useRef } from 'react';
import { LayoutDashboard, Users, Clock, Settings, LogOut, Bell, Search, Plus, Calendar as CalendarIcon, X, Filter, Download, AlertTriangle, ChevronLeft, Menu } from 'lucide-react';
import axios from 'axios';
import Login from './pages/Login';
import EmployeeDashboard from './pages/EmployeeDashboard';
import Employees from './pages/Employees';
import Attendance from './pages/Attendance';
import Requests from './pages/Requests';
import Reports from './pages/Reports';
import Config from './pages/Config';
import CalendarPage from './pages/Calendar';
import { TypeSelectionModal, EmployeeFormModal } from './components/EmployeeModals';
import { AlertDialog } from './components/AlertDialog';
import ErrorBoundary from './components/ErrorBoundary';

const API_URL = "/api";

function App() {
  const [user, setUser] = useState(null);
  const [avatarTimestamp, setAvatarTimestamp] = useState(Date.now());
  const [activeTab, setActiveTab] = useState('dashboard');
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [showNewModal, setShowNewModal] = useState(false);
  const [showFormModal, setShowFormModal] = useState(false);
  const [newType, setNewType] = useState('employee');

  // Alert Dialog State
  const [alertDialog, setAlertDialog] = useState({ isOpen: false, message: '', variant: 'error' });
  
  // Dashboard State
  const [period, setPeriod] = useState('day');
  const [stats, setStats] = useState({
    activeEmployees: 0,
    activeEmployeesPercentage: 100,
    checkinsToday: 0,
    checkinsTrend: '0%',
    checkinsPercentage: 0,
    late: 0,
    lateTrend: '0%',
    latePercentage: 0,
    absent: 0,
    absentTrend: '0%',
    absentPercentage: 0
  });
  const [recentCheckins, setRecentCheckins] = useState([]);
  const [dashboardAlerts, setDashboardAlerts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [showNotifications, setShowNotifications] = useState(false);
  const notificationRef = useRef(null);
  const [showAlertsModal, setShowAlertsModal] = useState(false);
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [alertDetails, setAlertDetails] = useState(null);
  const [config, setConfig] = useState(null);

  // Cerrar notificaciones al hacer clic fuera
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (notificationRef.current && !notificationRef.current.contains(event.target)) {
        setShowNotifications(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // Cargar configuración global al inicio
  useEffect(() => {
    const loadConfig = async () => {
        try {
            const res = await axios.get(`${API_URL}/config`);
            setConfig(res.data);
            
            if (res.data.nombre_aplicacion) {
                document.title = res.data.nombre_aplicacion;
            }
            if (res.data.icono_path) {
                let link = document.querySelector("link[rel~='icon']");
                if (!link) {
                    link = document.createElement('link');
                    link.rel = 'icon';
                    document.getElementsByTagName('head')[0].appendChild(link);
                }
                const iconUrl = res.data.icono_path.startsWith('http') 
                    ? res.data.icono_path 
                    : `${API_URL.replace('/api', '')}${res.data.icono_path}`;
                link.href = iconUrl;
            }
        } catch (e) {
            console.error("Error loading config", e);
        }
    };
    loadConfig();
  }, []);

  // Verificar sesión y escuchar cambios en usuario
  useEffect(() => {
    const loadUser = () => {
      console.log('👤 [App] loadUser called');
      const storedUser = localStorage.getItem('user');
      if (storedUser) {
        const parsedUser = JSON.parse(storedUser);
        console.log('   Usuario cargado:', parsedUser);
        console.log('   foto_path:', parsedUser.foto_path);
        setUser(parsedUser);
        const newTimestamp = Date.now();
        console.log('   Nuevo avatarTimestamp:', newTimestamp);
        setAvatarTimestamp(newTimestamp); // Actualizar timestamp para forzar recarga de imagen
      }
    };

    console.log('🔧 [App] Setting up user listener');
    loadUser();

    // Escuchar cambios en localStorage (cuando se actualiza el perfil)
    // Usamos evento personalizado 'userUpdated' porque 'storage' solo funciona entre tabs
    window.addEventListener('userUpdated', loadUser);
    return () => window.removeEventListener('userUpdated', loadUser);
  }, []);

  // Cargar datos del dashboard
  useEffect(() => {
    if (user && activeTab === 'dashboard') {
      fetchDashboardData();
    }
  }, [user, activeTab, period]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const statsRes = await axios.get(`${API_URL}/attendance/stats`, { params: { period } });
      setStats(statsRes.data);

      const checkinsRes = await axios.get(`${API_URL}/attendance/today`);
      setRecentCheckins(Array.isArray(checkinsRes.data) ? checkinsRes.data : []);

      const notifsRes = await axios.get(`${API_URL}/notifications/admin`);
      setNotifications(Array.isArray(notifsRes.data) ? notifsRes.data : []);

      const alertsRes = await axios.get(`${API_URL}/notifications/alerts`);
      // Filtrar alertas que el usuario ya eliminó
      const deletedAlerts = JSON.parse(localStorage.getItem('deletedAlerts') || '[]');
      const deletedIds = deletedAlerts.map(item => item.id);
      const filteredAlerts = Array.isArray(alertsRes.data)
        ? alertsRes.data.filter(alert => !deletedIds.includes(alert.id))
        : [];
      setDashboardAlerts(filteredAlerts);
      
    } catch (error) {
      console.error("Error cargando datos:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('user');
    setUser(null);
  };

  const handleAlertClick = async (alert) => {
    try {
      setSelectedAlert(alert);
      const response = await axios.get(`${API_URL}/notifications/alert/${alert.id}`);
      setAlertDetails(response.data);
    } catch (error) {
      console.error('Error cargando detalles de alerta:', error);
      // Mostrar detalles básicos si hay error
      setAlertDetails(alert.details || alert);
    }
  };

  const handleDeleteAlert = (alertId) => {
    // Guardar la alerta eliminada en localStorage
    const deletedAlerts = JSON.parse(localStorage.getItem('deletedAlerts') || '[]');
    const today = new Date().toISOString().split('T')[0];
    deletedAlerts.push({ id: alertId, date: today });
    // Mantener solo alertas eliminadas de los últimos 7 días
    const recentDeleted = deletedAlerts.filter(item => {
      const itemDate = new Date(item.date);
      const diffDays = (new Date() - itemDate) / (1000 * 60 * 60 * 24);
      return diffDays <= 7;
    });
    localStorage.setItem('deletedAlerts', JSON.stringify(recentDeleted));

    // Eliminar la alerta del estado local
    setDashboardAlerts(prev => prev.filter(alert => alert.id !== alertId));
  };

  const exportRecentCheckins = async (format) => {
    try {
      const today = new Date().toISOString().split('T')[0];
      const response = await axios.post(
        `${API_URL}/reports/generate`,
        {
          type: 'todos',
          start_date: today,
          end_date: today,
          format: format
        },
        {
          responseType: 'blob'
        }
      );

      // Crear link de descarga
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `fichajes_${today}.${format === 'pdf' ? 'pdf' : 'xlsx'}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      setAlertDialog({ isOpen: true, message: `Fichajes ${format.toUpperCase()} exportados exitosamente.`, variant: 'success' });

    } catch (error) {
      console.error('Error exportando fichajes:', error);
      
      let errorMessage = 'Error al exportar fichajes.';
      
      if (error.response && error.response.data instanceof Blob) {
           try {
               const text = await error.response.data.text();
               const json = JSON.parse(text);
               errorMessage += " " + (json.detail || json.message || "");
           } catch (e) { }
      } else if (error.response?.data?.detail) {
           errorMessage += " " + error.response.data.detail;
      }

      setAlertDialog({ isOpen: true, message: errorMessage, variant: 'error' });
    }
  };

  if (!user) {
    return <Login onLogin={setUser} />;
  }

  if (!user.es_admin && !user.es_superadmin) {
    return <EmployeeDashboard user={user} onLogout={handleLogout} />;
  }

  // Barra de título personalizada para escritorio
  const TitleBar = () => {
    const handleMinimize = () => window.pywebview?.api?.minimize();
    const handleMaximize = () => window.pywebview?.api?.maximize();
    const handleClose = () => window.pywebview?.api?.close();

    return (
      <div className="h-9 bg-[#F5F5DC] flex justify-between items-center px-3 select-none border-b border-stone-200 shadow-sm z-50">
        {/* Drag Region - Ocupa todo el espacio disponible */}
        <div className="flex-1 h-full flex items-center pywebview-drag-region cursor-default">
           {config?.icono_path && (
             <img 
               src={`${API_URL.replace('/api', '')}${config.icono_path}`} 
               alt="" 
               className="w-4 h-4 mr-2 opacity-70"
               onError={(e) => e.target.style.display = 'none'} 
             />
           )}
           <span className="text-xs font-semibold text-stone-600 tracking-wide">Fichaje Zaragonjg v1.0</span>
        </div>
        
        {/* Window Controls */}
        <div className="flex items-center gap-1 no-drag">
           <button onClick={handleMinimize} className="p-1.5 hover:bg-black/5 rounded-md text-stone-500 transition-colors focus:outline-none" title="Minimizar">
             <svg width="10" height="10" viewBox="0 0 10 10" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M1 5H9" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/></svg>
           </button>
           <button onClick={handleMaximize} className="p-1.5 hover:bg-black/5 rounded-md text-stone-500 transition-colors focus:outline-none" title="Maximizar">
             <svg width="10" height="10" viewBox="0 0 10 10" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="1.5" y="1.5" width="7" height="7" rx="1" stroke="currentColor" strokeWidth="1.2"/></svg>
           </button>
           <button onClick={handleClose} className="p-1.5 hover:bg-red-500 hover:text-white rounded-md text-stone-500 transition-colors focus:outline-none" title="Cerrar">
             <svg width="10" height="10" viewBox="0 0 10 10" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M2.5 2.5L7.5 7.5M7.5 2.5L2.5 7.5" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/></svg>
           </button>
        </div>
      </div>
    );
  };

  return (
    <div className="flex flex-col h-screen bg-background font-sans text-slate-900 overflow-hidden">
      <TitleBar />
      <div className="flex flex-1 overflow-hidden relative w-full">
      {/* Sidebar */}
      <aside className={`bg-sidebar text-white flex flex-col transition-all duration-300 shadow-xl z-20 h-full ${isSidebarCollapsed ? 'w-20' : 'w-64'}`}>
        <div className={`p-6 flex items-center gap-3 ${isSidebarCollapsed ? 'justify-center px-2' : ''}`}>
          {config?.logo_path ? (
             <img 
               src={`${API_URL.replace('/api', '')}${config.logo_path}`} 
               alt="Logo" 
               className="w-10 h-10 object-contain bg-white/10 rounded-lg p-1 shrink-0"
             />
          ) : (
            <div className="bg-primary p-2 rounded-lg shadow-lg shadow-primary/30 shrink-0">
              <Clock className="w-6 h-6 text-white" />
            </div>
          )}
          <div className={`transition-all duration-300 overflow-hidden whitespace-nowrap ${isSidebarCollapsed ? 'w-0 opacity-0' : 'w-auto opacity-100'}`}>
            <h1 className="font-bold text-xl leading-none tracking-tight">{config?.nombre_aplicacion || 'TimeTrack'}</h1>
            <span className="text-xs text-slate-400 font-medium tracking-widest">{config?.slogan || 'Pro'}</span>
          </div>
        </div>

        <nav className="flex-1 px-3 space-y-2 mt-4">
          <SidebarItem 
            icon={<LayoutDashboard size={20} />} 
            text="Dashboard" 
            active={activeTab === 'dashboard'} 
            onClick={() => setActiveTab('dashboard')} 
            collapsed={isSidebarCollapsed}
          />
          <SidebarItem 
            icon={<CalendarIcon size={20} />} 
            text="Calendario" 
            active={activeTab === 'calendar'} 
            onClick={() => setActiveTab('calendar')} 
            collapsed={isSidebarCollapsed}
          />
          <SidebarItem 
            icon={<Users size={20} />} 
            text="Personal" 
            active={activeTab === 'personal'} 
            onClick={() => setActiveTab('personal')} 
            collapsed={isSidebarCollapsed}
          />
          <SidebarItem 
            icon={<Clock size={20} />} 
            text="Fichajes" 
            active={activeTab === 'fichajes'} 
            onClick={() => setActiveTab('fichajes')} 
            collapsed={isSidebarCollapsed}
          />
          <SidebarItem 
            icon={<CalendarIcon size={20} />} 
            text="Solicitudes" 
            active={activeTab === 'requests'} 
            onClick={() => setActiveTab('requests')} 
            collapsed={isSidebarCollapsed}
          />
          <SidebarItem 
            icon={<div className="rotate-90"><LayoutDashboard size={20} /></div>} 
            text="Informes" 
            active={activeTab === 'reports'} 
            onClick={() => setActiveTab('reports')} 
            collapsed={isSidebarCollapsed}
          />
          <SidebarItem 
            icon={<Settings size={20} />} 
            text="Configuración" 
            active={activeTab === 'config'} 
            onClick={() => setActiveTab('config')} 
            collapsed={isSidebarCollapsed}
          />
        </nav>

        <div className="p-4 border-t border-slate-700/50">
          <div className={`flex items-center gap-3 p-2 rounded-xl hover:bg-white/5 cursor-pointer transition-colors group relative ${isSidebarCollapsed ? 'justify-center' : ''}`}>
            {user.foto_path ? (
              <img
                src={`${API_URL.replace('/api', '')}${user.foto_path}?t=${avatarTimestamp}`}
                alt={`${user.nombre} ${user.apellidos}`}
                className="w-10 h-10 rounded-full object-cover border-2 border-white/20 shadow-lg shrink-0"
              />
            ) : (
              <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-primary to-secondary flex items-center justify-center font-bold shadow-lg text-white text-sm shrink-0">
                {user.nombre?.charAt(0)}{user.apellidos?.charAt(0)}
              </div>
            )}
            
            <div className={`flex-1 min-w-0 transition-all duration-300 overflow-hidden ${isSidebarCollapsed ? 'w-0 opacity-0 hidden' : 'w-auto opacity-100'}`}>
              <p className="text-sm font-medium truncate group-hover:text-white transition-colors">{user.nombre}</p>
              <p className="text-xs text-slate-400 truncate">{user.es_superadmin ? 'Super Admin' : 'Admin'}</p>
            </div>
            
            {/* Botón Logout: En expandido es normal, en colapsado cubre la foto al hover */}
            <button 
              onClick={(e) => {
                e.stopPropagation();
                handleLogout();
              }} 
              className={`transition-colors ${
                  isSidebarCollapsed 
                  ? 'absolute inset-0 flex items-center justify-center bg-black/60 rounded-xl opacity-0 group-hover:opacity-100 text-white z-10' 
                  : 'p-1 hover:bg-white/10 rounded-lg text-slate-400 hover:text-error'
              }`}
              title="Cerrar sesión"
            >
              <LogOut size={isSidebarCollapsed ? 20 : 18} />
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden bg-background relative">
        {/* Header */}
        <header className="h-20 bg-white/80 backdrop-blur-md border-b border-slate-200/60 flex items-center justify-between px-8 sticky top-0 z-10">
          <div className="flex items-center gap-4">
            <button 
              onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
              className="p-2 bg-white border border-blue-200/60 text-blue-600 rounded-xl shadow-sm shadow-blue-100 hover:shadow-md hover:bg-slate-50 hover:animate-none animate-pulse transition-all"
              title={isSidebarCollapsed ? "Expandir menú" : "Contraer menú"}
            >
              {isSidebarCollapsed ? <Menu size={20} /> : <ChevronLeft size={20} />}
            </button>
            <div>
              <h2 className="text-2xl font-bold text-slate-800 tracking-tight">
                {activeTab === 'dashboard' ? 'Panel de Control' : 
               activeTab === 'calendar' ? 'Calendario General' :
               activeTab === 'personal' ? 'Gestión de Personal' :
               activeTab === 'fichajes' ? 'Historial de Fichajes' :
               activeTab === 'requests' ? 'Solicitudes' : 'Configuración'}
              </h2>
              <p className="text-sm text-slate-500 font-medium">Gestión de fichajes y personal</p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="relative group">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 w-4 h-4 group-focus-within:text-primary transition-colors" />
              <input 
                type="text" 
                placeholder="Buscar..." 
                className="pl-11 pr-4 py-2.5 bg-slate-100 rounded-full text-sm focus:outline-none focus:ring-2 focus:ring-primary/20 focus:bg-white w-64 transition-all border border-transparent focus:border-primary/10"
              />
            </div>
            <div className="relative" ref={notificationRef}>
                <button 
                    onClick={() => setShowNotifications(!showNotifications)}
                    className={`p-2.5 hover:bg-slate-100 rounded-full relative transition-colors ${showNotifications ? 'bg-slate-100 text-primary' : 'text-slate-600'}`}
                >
                    <Bell className="w-5 h-5" />
                    {notifications.length > 0 && (
                        <span className="absolute top-2 right-2 w-2 h-2 bg-error rounded-full ring-2 ring-white"></span>
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
                                        <div 
                                            key={notif.id} 
                                            className="p-4 hover:bg-slate-50 transition-colors cursor-pointer flex gap-3"
                                            onClick={() => {
                                                setShowNotifications(false);
                                                setActiveTab(notif.link);
                                            }}
                                        >
                                            <div className={`mt-1 w-2 h-2 rounded-full flex-shrink-0 ${notif.type === 'info' ? 'bg-blue-500' : 'bg-amber-500'}`}></div>
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
            <button onClick={() => setShowNewModal(true)} className="bg-primary hover:bg-blue-700 text-white px-5 py-2.5 rounded-full text-sm font-bold flex items-center gap-2 transition-all shadow-lg shadow-primary/30 hover:shadow-primary/50 hover:-translate-y-0.5 active:translate-y-0">
              <Plus size={18} strokeWidth={3} />
              <span>Nuevo</span>
            </button>
          </div>
        </header>

        {/* Global Modals */}
        {showNewModal && (
            <TypeSelectionModal 
                onClose={() => setShowNewModal(false)}
                onSelect={(type) => {
                    setNewType(type);
                    setShowNewModal(false);
                    setShowFormModal(true);
                }}
            />
        )}

        {showFormModal && (
            <EmployeeFormModal
                isOpen={showFormModal}
                onClose={() => setShowFormModal(false)}
                type={newType}
                onSuccess={() => {
                    setShowFormModal(false);
                    fetchDashboardData();
                    if (activeTab === 'personal') {
                        const event = new Event('employee-created');
                        window.dispatchEvent(event);
                    }
                }}
            />
        )}

        {/* Modal Alertas Detalladas */}
        {showAlertsModal && (
            <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                <div className="bg-white rounded-3xl shadow-2xl w-full max-w-3xl p-5 animate-in zoom-in-95 max-h-[85vh] flex flex-col" style={{ fontSize: '12px' }}>
                    <div className="flex justify-between items-center mb-4 border-b border-slate-100 pb-3">
                        <div className="flex items-center gap-2">
                            <div className="p-1.5 bg-amber-50 rounded-lg text-amber-600">
                                <AlertTriangle size={20} />
                            </div>
                            <h3 className="text-lg font-bold text-slate-800">Alertas del Día</h3>
                        </div>
                        <button onClick={() => setShowAlertsModal(false)} className="p-1.5 hover:bg-slate-100 rounded-full">
                            <X size={18} className="text-slate-400" />
                        </button>
                    </div>

                    <div className="flex-1 overflow-y-auto pr-2 space-y-2.5">
                        {dashboardAlerts.length === 0 ? (
                            <div className="text-center py-12 text-slate-400 text-xs">
                                <p>No hay alertas activas hoy</p>
                            </div>
                        ) : (
                            dashboardAlerts.map(alert => {
                                const alertStyles = {
                                    success: 'bg-green-50 border-green-500 hover:bg-green-100',
                                    error: 'bg-red-50 border-red-500 hover:bg-red-100',
                                    warning: 'bg-amber-50 border-amber-500 hover:bg-amber-100',
                                    info: 'bg-blue-50 border-blue-500 hover:bg-blue-100'
                                };
                                const alertTitleStyles = {
                                    success: 'text-green-800',
                                    error: 'text-red-800',
                                    warning: 'text-amber-800',
                                    info: 'text-blue-800'
                                };

                                return (
                                <div
                                    key={alert.id}
                                    onClick={() => handleAlertClick(alert)}
                                    className={`p-3 rounded-lg border-l-4 shadow-sm cursor-pointer hover:shadow-md transition-all ${alertStyles[alert.type] || alertStyles.info}`}
                                >
                                    <div className="flex justify-between items-start mb-1.5">
                                        <h4 className={`font-bold text-xs ${alertTitleStyles[alert.type] || 'text-slate-800'}`}>
                                            {alert.title}
                                        </h4>
                                        <span className="text-[10px] font-bold bg-white/50 px-1.5 py-0.5 rounded text-slate-600">{alert.time}</span>
                                    </div>
                                    <p className="text-xs text-slate-700 mb-1.5">{alert.message}</p>

                                    {alert.details && (
                                        <div className="bg-white/50 p-2 rounded-lg text-[10px] space-y-0.5">
                                            <div className="flex justify-between">
                                                <span className="text-slate-500">Empleado:</span>
                                                <span className="font-bold">{alert.details.empleado}</span>
                                            </div>
                                            {alert.details.hora_llegada && (
                                                <div className="flex justify-between">
                                                    <span className="text-slate-500">Hora Llegada:</span>
                                                    <span className="font-bold">{alert.details.hora_llegada} (Esp: {alert.details.hora_esperada})</span>
                                                </div>
                                            )}
                                        </div>
                                    )}
                                    <p className="text-[10px] text-slate-400 mt-1.5 font-medium">Click para ver detalles</p>
                                </div>
                                );
                            })
                        )}
                    </div>
                </div>
            </div>
        )}

        {/* Modal Detalles de Alerta */}
        {selectedAlert && alertDetails && (
            <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-[60] flex items-center justify-center p-4">
                <div className="bg-white rounded-3xl shadow-2xl w-full max-w-2xl p-8 animate-in zoom-in-95 max-h-[90vh] overflow-y-auto">
                    <div className="flex justify-between items-start mb-6 pb-4 border-b border-slate-100">
                        <div className="flex items-center gap-3">
                            <div className={`p-3 rounded-xl ${selectedAlert.type === 'error' ? 'bg-red-100 text-red-600' : 'bg-amber-100 text-amber-600'}`}>
                                <AlertTriangle size={28} />
                            </div>
                            <div>
                                <h3 className="text-2xl font-bold text-slate-800">{alertDetails.title || selectedAlert.title}</h3>
                                <p className="text-sm text-slate-500 mt-1">{selectedAlert.time}</p>
                            </div>
                        </div>
                        <button
                            onClick={() => {
                                setSelectedAlert(null);
                                setAlertDetails(null);
                            }}
                            className="p-2 hover:bg-slate-100 rounded-full transition-colors"
                        >
                            <X size={24} className="text-slate-400" />
                        </button>
                    </div>

                    <div className="space-y-6">
                        {/* Información del Empleado */}
                        <div className="bg-slate-50 p-6 rounded-2xl">
                            <h4 className="text-sm font-bold text-slate-600 uppercase mb-4">Información del Empleado</h4>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <p className="text-xs text-slate-500">Nombre Completo</p>
                                    <p className="text-sm font-bold text-slate-800">{alertDetails.empleado?.nombre || 'N/A'}</p>
                                </div>
                                <div>
                                    <p className="text-xs text-slate-500">DNI</p>
                                    <p className="text-sm font-bold text-slate-800">{alertDetails.empleado?.dni || 'N/A'}</p>
                                </div>
                                <div>
                                    <p className="text-xs text-slate-500">Número de Empleado</p>
                                    <p className="text-sm font-bold text-slate-800">{alertDetails.empleado?.numero_empleado || 'N/A'}</p>
                                </div>
                                <div>
                                    <p className="text-xs text-slate-500">Departamento</p>
                                    <p className="text-sm font-bold text-slate-800">{alertDetails.empleado?.departamento || 'N/A'}</p>
                                </div>
                                <div>
                                    <p className="text-xs text-slate-500">Email</p>
                                    <p className="text-sm font-bold text-slate-800">{alertDetails.empleado?.email || 'N/A'}</p>
                                </div>
                                <div>
                                    <p className="text-xs text-slate-500">Teléfono</p>
                                    <p className="text-sm font-bold text-slate-800">{alertDetails.empleado?.telefono || 'N/A'}</p>
                                </div>
                            </div>
                        </div>

                        {/* Detalles del Fichaje (si es llegada tarde) */}
                        {alertDetails.fichaje && (
                            <div className="bg-amber-50 p-6 rounded-2xl">
                                <h4 className="text-sm font-bold text-amber-800 uppercase mb-4">Detalles del Fichaje</h4>
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <p className="text-xs text-amber-600">Fecha</p>
                                        <p className="text-sm font-bold text-slate-800">{alertDetails.fichaje.fecha}</p>
                                    </div>
                                    <div>
                                        <p className="text-xs text-amber-600">Tipo</p>
                                        <p className="text-sm font-bold text-slate-800 capitalize">{alertDetails.fichaje.tipo.replace(/_/g, ' ')}</p>
                                    </div>
                                    <div>
                                        <p className="text-xs text-amber-600">Hora Entrada</p>
                                        <p className="text-sm font-bold text-slate-800">{alertDetails.fichaje.hora_entrada}</p>
                                    </div>
                                    <div>
                                        <p className="text-xs text-amber-600">Hora Salida</p>
                                        <p className="text-sm font-bold text-slate-800">{alertDetails.fichaje.hora_salida}</p>
                                    </div>
                                </div>
                                {alertDetails.fichaje.observaciones && (
                                    <div className="mt-4 pt-4 border-t border-amber-100">
                                        <p className="text-xs text-amber-600 mb-1">Observaciones</p>
                                        <p className="text-sm text-slate-700">{alertDetails.fichaje.observaciones}</p>
                                    </div>
                                )}
                            </div>
                        )}

                        {/* Detalles del Retraso */}
                        {alertDetails.retraso && (
                            <div className="bg-red-50 p-6 rounded-2xl">
                                <h4 className="text-sm font-bold text-red-800 uppercase mb-4">Análisis del Retraso</h4>
                                <div className="grid grid-cols-3 gap-4">
                                    <div>
                                        <p className="text-xs text-red-600">Hora Esperada</p>
                                        <p className="text-lg font-bold text-slate-800">{alertDetails.retraso.hora_esperada}</p>
                                    </div>
                                    <div>
                                        <p className="text-xs text-red-600">Hora Llegada</p>
                                        <p className="text-lg font-bold text-slate-800">{alertDetails.retraso.hora_llegada}</p>
                                    </div>
                                    <div>
                                        <p className="text-xs text-red-600">Minutos Tarde</p>
                                        <p className="text-2xl font-bold text-red-600">{alertDetails.retraso.minutos_tarde}</p>
                                    </div>
                                </div>
                                <div className="mt-4 pt-4 border-t border-red-100">
                                    <p className="text-xs text-red-600">Tolerancia Configurada</p>
                                    <p className="text-sm font-bold text-slate-800">{alertDetails.retraso.tolerancia} minutos</p>
                                </div>
                            </div>
                        )}

                        {/* Detalles de Ausencia */}
                        {alertDetails.ausencia && (
                            <div className="bg-red-50 p-6 rounded-2xl">
                                <h4 className="text-sm font-bold text-red-800 uppercase mb-4">Detalles de la Ausencia</h4>
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <p className="text-xs text-red-600">Fecha</p>
                                        <p className="text-sm font-bold text-slate-800">{alertDetails.ausencia.fecha}</p>
                                    </div>
                                    <div>
                                        <p className="text-xs text-red-600">Turno Esperado</p>
                                        <p className="text-sm font-bold text-slate-800">{alertDetails.ausencia.turno_esperado}</p>
                                    </div>
                                    <div>
                                        <p className="text-xs text-red-600">Hora Inicio</p>
                                        <p className="text-sm font-bold text-slate-800">{alertDetails.ausencia.hora_inicio_esperada}</p>
                                    </div>
                                    <div>
                                        <p className="text-xs text-red-600">Días Pendientes</p>
                                        <p className="text-lg font-bold text-red-600">{alertDetails.ausencia.dias_pendientes}</p>
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Detalles de Solicitud */}
                        {alertDetails.solicitud && (
                            <div className="bg-blue-50 p-6 rounded-2xl">
                                <h4 className="text-sm font-bold text-blue-800 uppercase mb-4">Detalles de la Solicitud</h4>
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <p className="text-xs text-blue-600">Tipo</p>
                                        <p className="text-sm font-bold text-slate-800">{alertDetails.solicitud.tipo}</p>
                                    </div>
                                    <div>
                                        <p className="text-xs text-blue-600">Estado</p>
                                        <p className="text-sm font-bold text-slate-800 capitalize">{alertDetails.solicitud.estado}</p>
                                    </div>
                                    <div>
                                        <p className="text-xs text-blue-600">Fecha Inicio</p>
                                        <p className="text-sm font-bold text-slate-800">{alertDetails.solicitud.fecha_inicio}</p>
                                    </div>
                                    <div>
                                        <p className="text-xs text-blue-600">Fecha Fin</p>
                                        <p className="text-sm font-bold text-slate-800">{alertDetails.solicitud.fecha_fin}</p>
                                    </div>
                                    <div>
                                        <p className="text-xs text-blue-600">Días Solicitados</p>
                                        <p className="text-lg font-bold text-blue-600">{alertDetails.solicitud.dias_solicitados}</p>
                                    </div>
                                    <div>
                                        <p className="text-xs text-blue-600">Fecha Solicitud</p>
                                        <p className="text-sm font-bold text-slate-800">{alertDetails.solicitud.fecha_solicitud}</p>
                                    </div>
                                </div>
                                {alertDetails.solicitud.motivo && (
                                    <div className="mt-4 pt-4 border-t border-blue-100">
                                        <p className="text-xs text-blue-600 mb-1">Motivo</p>
                                        <p className="text-sm text-slate-700">{alertDetails.solicitud.motivo}</p>
                                    </div>
                                )}
                            </div>
                        )}

                        {/* Información del Turno */}
                        {alertDetails.turno && (
                            <div className="bg-blue-50 p-6 rounded-2xl">
                                <h4 className="text-sm font-bold text-blue-800 uppercase mb-4">Información del Turno</h4>
                                <div className="grid grid-cols-3 gap-4">
                                    <div>
                                        <p className="text-xs text-blue-600">Turno</p>
                                        <p className="text-sm font-bold text-slate-800">{alertDetails.turno.nombre}</p>
                                    </div>
                                    <div>
                                        <p className="text-xs text-blue-600">Hora Inicio</p>
                                        <p className="text-sm font-bold text-slate-800">{alertDetails.turno.hora_inicio}</p>
                                    </div>
                                    <div>
                                        <p className="text-xs text-blue-600">Hora Fin</p>
                                        <p className="text-sm font-bold text-slate-800">{alertDetails.turno.hora_fin}</p>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>

                    <button
                        onClick={() => {
                            setSelectedAlert(null);
                            setAlertDetails(null);
                        }}
                        className="w-full mt-6 py-3 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold rounded-xl transition-colors"
                    >
                        Cerrar
                    </button>
                </div>
            </div>
        )}

        {/* Dynamic Content */}
        <div className="flex-1 overflow-auto p-8 custom-scrollbar">
          <ErrorBoundary>
          {activeTab === 'dashboard' && (
            <>
              {/* Filter Tabs */}
              <div className="flex justify-end mb-6">
                  <div className="bg-white p-1 rounded-xl shadow-sm border border-slate-200 inline-flex">
                      {['day', 'week', 'month', 'year'].map(p => (
                          <button 
                              key={p}
                              onClick={() => setPeriod(p)}
                              className={`px-4 py-2 rounded-lg text-sm font-bold transition-all ${
                                  period === p ? 'bg-primary text-white shadow-md' : 'text-slate-500 hover:bg-slate-50'
                              }`}
                          >
                              {p === 'day' ? 'Día' : p === 'week' ? 'Semana' : p === 'month' ? 'Mes' : 'Año'}
                          </button>
                      ))}
                  </div>
              </div>

              {/* Stats Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                <StatCard
                  title="Personal Activo"
                  value={stats.activeEmployees}
                  icon={<Users />}
                  color="text-emerald-600 bg-emerald-100"
                  trend="Total"
                  trendColor="bg-emerald-100 text-emerald-700"
                />
                <StatCard
                  title="Fichajes Hoy"
                  value={stats.checkinsToday}
                  icon={<Clock />}
                  color="text-primary bg-blue-100"
                  trend={stats.checkinsTrend}
                  trendColor="bg-blue-100 text-blue-700"
                />
                <StatCard
                  title="Retrasos"
                  value={stats.late}
                  icon={<Clock />}
                  color="text-amber-600 bg-amber-100"
                  trend={stats.lateTrend}
                  trendColor="bg-amber-100 text-amber-700"
                />
                <StatCard
                  title="Ausencias"
                  value={stats.absent}
                  icon={<Users />}
                  color="text-red-600 bg-red-100"
                  trend={stats.absentTrend}
                  trendColor="bg-red-100 text-red-700"
                />
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Recent Activity Table */}
                <div className="lg:col-span-2 bg-white rounded-[2rem] shadow-sm border border-slate-100 p-8">
                  <div className="flex items-center justify-between mb-8">
                    <h3 className="text-xl font-bold text-slate-800">Fichajes de Hoy</h3>
                    <div className="flex gap-2">
                      <button
                        onClick={() => fetchDashboardData()}
                        className="p-2 hover:bg-slate-50 rounded-lg border border-slate-200 text-slate-500"
                        title="Actualizar"
                      >
                          <Filter size={16} />
                      </button>
                      <div className="flex gap-1 bg-slate-50 p-1 rounded-xl border border-slate-200">
                        <button
                          onClick={() => exportRecentCheckins('excel')}
                          className="px-3 py-1.5 text-xs font-semibold hover:bg-white rounded-lg transition-colors text-slate-600 flex items-center gap-1.5"
                          title="Exportar a Excel"
                        >
                            <Download size={13} /> Excel
                        </button>
                        <button
                          onClick={() => exportRecentCheckins('pdf')}
                          className="px-3 py-1.5 text-xs font-semibold hover:bg-white rounded-lg transition-colors text-slate-600 flex items-center gap-1.5"
                          title="Exportar a PDF"
                        >
                            <Download size={13} /> PDF
                        </button>
                      </div>
                    </div>
                  </div>
                  
                  <div className="overflow-x-auto">
                    {loading ? (
                      <div className="text-center py-10 text-slate-400">Cargando datos...</div>
                    ) : recentCheckins.length === 0 ? (
                      <div className="text-center py-10 text-slate-400">No hay fichajes hoy</div>
                    ) : (
                      <table className="w-full">
                        <thead>
                          <tr className="text-left text-xs font-bold text-slate-400 uppercase tracking-wider border-b border-slate-100">
                            <th className="pb-4 pl-4">Empleado</th>
                            <th className="pb-4">Departamento</th>
                            <th className="pb-4">Entrada</th>
                            <th className="pb-4">Salida</th>
                            <th className="pb-4 text-right pr-4">Estado</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-50">
                          {recentCheckins.map((checkin) => {
                            // Extraer solo primer nombre y primer apellido
                            const nombreCompleto = checkin.empleado_nombre || '';
                            const partes = nombreCompleto.split(' ');
                            const primerNombre = partes[0] || '';
                            const primerApellido = partes[partes.length > 1 ? Math.floor(partes.length / 2) : 0] || '';
                            const nombreCorto = `${primerNombre} ${primerApellido}`.trim();

                            return (
                              <TableRow
                                key={checkin.id}
                                name={nombreCorto || nombreCompleto}
                                employeeNumber={checkin.numero_empleado || checkin.empleado_id}
                                photoPath={checkin.foto_path}
                                dept={checkin.departamento}
                                inTime={checkin.hora_entrada || "--:--"}
                                outTime={checkin.hora_salida || "--:--"}
                                status={checkin.estado}
                              />
                            );
                          })}
                        </tbody>
                      </table>
                    )}
                  </div>
                </div>

                {/* Alerts Panel */}
                <div className="bg-white rounded-[2rem] shadow-sm border border-slate-100 p-6 h-fit sticky top-8">
                  <h3 className="text-base font-bold text-slate-800 mb-4 flex items-center gap-2">
                      <AlertTriangle size={18} className="text-amber-500" />
                      Alertas del Día
                  </h3>
                  <div className="space-y-2">
                    {dashboardAlerts.length === 0 ? (
                        <div className="p-3 bg-slate-50 rounded-xl text-center text-xs text-slate-400">Todo en orden hoy</div>
                    ) : (
                        dashboardAlerts.map(alert => (
                            <NotificationItem
                                key={alert.id}
                                alertId={alert.id}
                                title={alert.title}
                                desc={alert.message}
                                time={alert.time}
                                type={alert.type}
                                onClick={() => handleAlertClick(alert)}
                                onDelete={handleDeleteAlert}
                            />
                        ))
                    )}
                  </div>

                  <button
                    onClick={() => setShowAlertsModal(true)}
                    className="w-full mt-4 py-2 text-xs font-semibold text-primary bg-primary/5 hover:bg-primary/10 rounded-xl transition-colors"
                  >
                    Ver todas las alertas
                  </button>
                </div>
              </div>
            </>
          )}
          
          {activeTab === 'calendar' && <CalendarPage />}
          {activeTab === 'personal' && <Employees />}
          {activeTab === 'fichajes' && <Attendance />}
          {activeTab === 'requests' && <Requests />}
          {activeTab === 'reports' && <Reports />}
          {activeTab === 'config' && <Config />}
          </ErrorBoundary>
        </div>
      </main>

      </div>
      {/* Alert Dialog */}
      <AlertDialog
        isOpen={alertDialog.isOpen}
        onClose={() => setAlertDialog({ isOpen: false, message: '', variant: 'error' })}
        message={alertDialog.message}
        variant={alertDialog.variant}
      />
    </div>
  );
}

function SidebarItem({ icon, text, active, onClick, collapsed }) {
  return (
    <button 
      onClick={onClick}
      className={`w-full flex items-center gap-3 px-3 py-3 rounded-xl text-sm font-medium transition-all duration-200 group relative overflow-hidden ${
        active 
          ? 'bg-primary text-white shadow-lg shadow-primary/30' 
          : 'text-slate-400 hover:bg-white/5 hover:text-white'
      } ${collapsed ? 'justify-center' : ''}`}
      title={collapsed ? text : ''}
    >
      <div className={`relative z-10 transition-transform duration-200 ${active ? 'scale-110' : 'group-hover:scale-110'}`}>
        {icon}
      </div>
      
      {!collapsed && (
        <span className="relative z-10 animate-in fade-in duration-200 whitespace-nowrap">{text}</span>
      )}
      
      {active && !collapsed && <div className="absolute right-0 top-1/2 -translate-y-1/2 w-1 h-6 bg-white/30 rounded-l-full"></div>}
    </button>
  );
}

function StatCard({ title, value, icon, color, trend, trendColor }) {
  return (
    <div className="bg-white p-6 rounded-[2rem] shadow-sm border border-slate-100 hover:shadow-lg hover:-translate-y-1 transition-all duration-300">
      <div className="flex justify-between items-start mb-6">
        <div className={`p-4 rounded-2xl ${color}`}>
          {React.cloneElement(icon, { className: "w-6 h-6" })}
        </div>
        <span className={`text-xs font-bold px-3 py-1.5 rounded-full ${trendColor}`}>
          {trend}
        </span>
      </div>
      <h3 className="text-slate-500 text-sm font-medium mb-1 pl-1">{title}</h3>
      <p className="text-4xl font-bold text-slate-800 pl-1">{value}</p>
    </div>
  );
}

function TableRow({ name, employeeNumber, photoPath, dept, inTime, outTime, status }) {
  const getStatusColor = (s) => {
      switch(s) {
          case 'A Tiempo': return 'bg-emerald-100 text-emerald-700';
          case 'Tarde': return 'bg-amber-100 text-amber-700';
          case 'Completo': return 'bg-blue-100 text-blue-700';
          case 'Ausente': return 'bg-red-100 text-red-700';
          default: return 'bg-slate-100 text-slate-700';
      }
  };

  return (
    <tr className="hover:bg-slate-50 transition-colors group cursor-default">
      <td className="py-5 pl-4">
        <div className="flex items-center gap-4">
          {photoPath ? (
            <img
              src={`${API_URL.replace('/api', '')}${photoPath}`}
              alt={name}
              className="w-12 h-12 rounded-full object-cover border-2 border-slate-100 group-hover:border-primary group-hover:scale-110 transition-all shadow-sm"
            />
          ) : (
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white font-bold text-lg group-hover:shadow-md transition-all group-hover:scale-110 border-2 border-transparent group-hover:border-slate-100">
              {name.split(' ').map(n => n.charAt(0)).join('').slice(0, 2)}
            </div>
          )}
          <div>
            <p className="font-bold text-slate-800 text-sm">{name}</p>
            <p className="text-xs text-slate-400 font-medium">N°: {employeeNumber}</p>
          </div>
        </div>
      </td>
      <td className="py-5 text-sm text-slate-600 font-medium">{dept}</td>
      <td className="py-5 text-sm font-bold text-slate-800">{inTime}</td>
      <td className="py-5 text-sm text-slate-400 font-medium">{outTime}</td>
      <td className="py-5 pr-4 text-right">
        <span className={`px-4 py-1.5 rounded-full text-xs font-bold shadow-sm ${getStatusColor(status)}`}>
          {status}
        </span>
      </td>
    </tr>
  );
}

function NotificationItem({ title, desc, time, type, onClick, onDelete, alertId }) {
  const styles = {
    success: 'bg-green-50 text-green-900 border-green-100 hover:border-green-200 hover:shadow-sm',
    error: 'bg-red-50 text-red-900 border-red-100 hover:border-red-200 hover:shadow-sm',
    warning: 'bg-amber-50 text-amber-900 border-amber-100 hover:border-amber-200 hover:shadow-sm',
    info: 'bg-blue-50 text-blue-900 border-blue-100 hover:border-blue-200 hover:shadow-sm'
  };

  const icons = {
    success: (
      <div className="w-6 h-6 rounded-full bg-green-500 flex items-center justify-center text-white">
        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="20 6 9 17 4 12"></polyline>
        </svg>
      </div>
    ),
    error: (
      <div className="w-6 h-6 rounded-full bg-red-500 flex items-center justify-center text-white">
        <span className="text-sm font-bold">!</span>
      </div>
    ),
    warning: (
      <div className="w-6 h-6 rounded-full bg-amber-500 flex items-center justify-center text-white">
        <Clock className="w-3.5 h-3.5" />
      </div>
    ),
    info: (
      <div className="w-6 h-6 rounded-full bg-blue-500 flex items-center justify-center text-white">
        <span className="text-xs font-bold">i</span>
      </div>
    )
  };

  const handleDelete = (e) => {
    e.stopPropagation();
    if (onDelete) {
      onDelete(alertId);
    }
  };

  return (
    <div
      className={`p-2.5 rounded-lg border transition-all cursor-pointer relative group ${styles[type]}`}
      style={{ fontSize: '12px' }}
    >
      <div onClick={onClick} className="flex gap-2 items-start">
        <div className="mt-0.5">{icons[type]}</div>
        <div className="flex-1 min-w-0">
          <h4 className="font-bold mb-0.5 truncate">{title}</h4>
          <p className="opacity-80 mb-1 font-medium leading-snug line-clamp-2">{desc}</p>
          <span className="text-[10px] opacity-60 font-bold uppercase tracking-wider">{time}</span>
        </div>
      </div>
      {onDelete && (
        <button
          onClick={handleDelete}
          className="absolute top-2 right-2 p-1 bg-white rounded-full shadow-sm hover:bg-red-50 hover:text-red-600 transition-colors opacity-0 group-hover:opacity-100"
          title="Eliminar alerta"
        >
          <X size={12} />
        </button>
      )}
    </div>
  );
}

export default App;
