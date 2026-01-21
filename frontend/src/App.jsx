import React, { useState, useEffect } from 'react';
import { LayoutDashboard, Users, Clock, Settings, LogOut, Bell, Search, Plus, Calendar as CalendarIcon, X, Filter, Download, AlertTriangle } from 'lucide-react';
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

const API_URL = "http://localhost:8000/api";

function App() {
  const [user, setUser] = useState(null);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [showNewModal, setShowNewModal] = useState(false);
  const [showFormModal, setShowFormModal] = useState(false);
  const [newType, setNewType] = useState('employee');
  
  // Dashboard State
  const [period, setPeriod] = useState('day');
  const [stats, setStats] = useState({
    activeEmployees: 0,
    checkinsToday: 0,
    late: 0,
    absent: 0
  });
  const [recentCheckins, setRecentCheckins] = useState([]);
  const [dashboardAlerts, setDashboardAlerts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [showNotifications, setShowNotifications] = useState(false);
  const [showAlertsModal, setShowAlertsModal] = useState(false);
  const [config, setConfig] = useState(null);

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

  // Verificar sesión
  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
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
      setRecentCheckins(checkinsRes.data);

      const notifsRes = await axios.get(`${API_URL}/notifications/admin`);
      setNotifications(notifsRes.data);
      
      const alertsRes = await axios.get(`${API_URL}/notifications/alerts`);
      setDashboardAlerts(alertsRes.data);
      
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

  const exportRecentCheckins = () => {
      const csvContent = "data:text/csv;charset=utf-8," 
          + "Empleado,Departamento,Entrada,Salida,Estado\n"
          + recentCheckins.map(row => `${row.empleado_nombre},${row.departamento},${row.hora_entrada},${row.hora_salida},${row.estado}`).join("\n");
      
      const encodedUri = encodeURI(csvContent);
      const link = document.createElement("a");
      link.setAttribute("href", encodedUri);
      link.setAttribute("download", `fichajes_recientes_${new Date().toISOString().split('T')[0]}.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
  };

  if (!user) {
    return <Login onLogin={setUser} />;
  }

  if (!user.es_admin && !user.es_superadmin) {
    return <EmployeeDashboard user={user} onLogout={handleLogout} />;
  }

  return (
    <div className="flex h-screen bg-background font-sans text-slate-900">
      {/* Sidebar */}
      <aside className="w-64 bg-sidebar text-white flex flex-col transition-all duration-300 shadow-xl z-20">
        <div className="p-6 flex items-center gap-3">
          {config?.logo_path ? (
             <img 
               src={`${API_URL.replace('/api', '')}${config.logo_path}`} 
               alt="Logo" 
               className="w-10 h-10 object-contain bg-white/10 rounded-lg p-1"
             />
          ) : (
            <div className="bg-primary p-2 rounded-lg shadow-lg shadow-primary/30">
              <Clock className="w-6 h-6 text-white" />
            </div>
          )}
          <div>
            <h1 className="font-bold text-xl leading-none tracking-tight">{config?.nombre_aplicacion || 'TimeTrack'}</h1>
            <span className="text-xs text-slate-400 font-medium tracking-widest uppercase">Pro</span>
          </div>
        </div>

        <nav className="flex-1 px-4 space-y-2 mt-4">
          <SidebarItem icon={<LayoutDashboard size={20} />} text="Dashboard" active={activeTab === 'dashboard'} onClick={() => setActiveTab('dashboard')} />
          <SidebarItem icon={<CalendarIcon size={20} />} text="Calendario" active={activeTab === 'calendar'} onClick={() => setActiveTab('calendar')} />
          <SidebarItem icon={<Users size={20} />} text="Personal" active={activeTab === 'personal'} onClick={() => setActiveTab('personal')} />
          <SidebarItem icon={<Clock size={20} />} text="Fichajes" active={activeTab === 'fichajes'} onClick={() => setActiveTab('fichajes')} />
          <SidebarItem icon={<CalendarIcon size={20} />} text="Solicitudes" active={activeTab === 'requests'} onClick={() => setActiveTab('requests')} />
          <SidebarItem icon={<div className="rotate-90"><LayoutDashboard size={20} /></div>} text="Informes" active={activeTab === 'reports'} onClick={() => setActiveTab('reports')} />
          <SidebarItem icon={<Settings size={20} />} text="Configuración" active={activeTab === 'config'} onClick={() => setActiveTab('config')} />
        </nav>

        <div className="p-4 border-t border-slate-700/50">
          <div className="flex items-center gap-3 p-3 rounded-xl hover:bg-white/5 cursor-pointer transition-colors group">
            <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-primary to-secondary flex items-center justify-center font-bold shadow-lg text-white text-sm">
              {user.nombre?.charAt(0)}{user.apellidos?.charAt(0)}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate group-hover:text-white transition-colors">{user.nombre}</p>
              <p className="text-xs text-slate-400 truncate">{user.es_superadmin ? 'Super Admin' : 'Admin'}</p>
            </div>
            <button onClick={handleLogout} className="p-1 hover:bg-white/10 rounded-lg transition-colors">
              <LogOut size={18} className="text-slate-400 hover:text-error transition-colors" />
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden bg-background relative">
        {/* Header */}
        <header className="h-20 bg-white/80 backdrop-blur-md border-b border-slate-200/60 flex items-center justify-between px-8 sticky top-0 z-10">
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

          <div className="flex items-center gap-4">
            <div className="relative group">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 w-4 h-4 group-focus-within:text-primary transition-colors" />
              <input 
                type="text" 
                placeholder="Buscar..." 
                className="pl-11 pr-4 py-2.5 bg-slate-100 rounded-full text-sm focus:outline-none focus:ring-2 focus:ring-primary/20 focus:bg-white w-64 transition-all border border-transparent focus:border-primary/10"
              />
            </div>
            <div className="relative">
                <button 
                    onClick={() => setShowNotifications(!showNotifications)}
                    className="p-2.5 hover:bg-slate-100 rounded-full relative transition-colors"
                >
                    <Bell className="w-5 h-5 text-slate-600" />
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
                <div className="bg-white rounded-3xl shadow-2xl w-full max-w-3xl p-6 animate-in zoom-in-95 h-[80vh] flex flex-col">
                    <div className="flex justify-between items-center mb-6 border-b border-slate-100 pb-4">
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-amber-50 rounded-lg text-amber-600">
                                <AlertTriangle size={24} />
                            </div>
                            <h3 className="text-xl font-bold text-slate-800">Alertas del Día</h3>
                        </div>
                        <button onClick={() => setShowAlertsModal(false)} className="p-2 hover:bg-slate-100 rounded-full">
                            <X size={20} className="text-slate-400" />
                        </button>
                    </div>
                    
                    <div className="flex-1 overflow-y-auto pr-2 space-y-4">
                        {dashboardAlerts.length === 0 ? (
                            <div className="text-center py-20 text-slate-400">
                                <p>No hay alertas activas hoy</p>
                            </div>
                        ) : (
                            dashboardAlerts.map(alert => (
                                <div key={alert.id} className={`p-4 rounded-xl border-l-4 shadow-sm ${
                                    alert.type === 'error' ? 'bg-red-50 border-red-500' : 'bg-amber-50 border-amber-500'
                                }`}>
                                    <div className="flex justify-between items-start mb-2">
                                        <h4 className={`font-bold ${alert.type === 'error' ? 'text-red-800' : 'text-amber-800'}`}>
                                            {alert.title}
                                        </h4>
                                        <span className="text-xs font-bold bg-white/50 px-2 py-1 rounded text-slate-600">{alert.time}</span>
                                    </div>
                                    <p className="text-sm text-slate-700 mb-2">{alert.message}</p>
                                    
                                    {alert.details && (
                                        <div className="bg-white/50 p-3 rounded-lg text-xs space-y-1">
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
                                </div>
                            ))
                        )}
                    </div>
                </div>
            </div>
        )}

        {/* Dynamic Content */}
        <div className="flex-1 overflow-auto p-8 custom-scrollbar">
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
                <StatCard title="Personal Activo" value={stats.activeEmployees} icon={<Users />} color="text-emerald-600 bg-emerald-100" trend="Total" trendColor="bg-emerald-100 text-emerald-700" />
                <StatCard title="Fichajes" value={stats.checkinsToday} icon={<Clock />} color="text-primary bg-blue-100" trend={stats.checkinsTrend} trendColor="bg-blue-100 text-blue-700" />
                <StatCard title="Retrasos" value={stats.late} icon={<Clock />} color="text-amber-600 bg-amber-100" trend={stats.lateTrend} trendColor="bg-amber-100 text-amber-700" />
                <StatCard title="Ausencias" value={stats.absent} icon={<Users />} color="text-red-600 bg-red-100" trend={stats.absentTrend} trendColor="bg-red-100 text-red-700" />
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
                      <button 
                        onClick={exportRecentCheckins} 
                        className="px-4 py-2 text-xs font-semibold bg-slate-50 hover:bg-slate-100 rounded-xl border border-slate-200 transition-colors text-slate-600 flex items-center gap-2"
                      >
                          <Download size={14} /> Exportar
                      </button>
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
                          {recentCheckins.map((checkin) => (
                            <TableRow 
                              key={checkin.id}
                              name={checkin.empleado_nombre} 
                              id={`ID: ${checkin.empleado_id}`} 
                              dept={checkin.departamento} 
                              inTime={checkin.hora_entrada || "--:--"} 
                              outTime={checkin.hora_salida || "--:--"} 
                              status={checkin.estado} 
                            />
                          ))}
                        </tbody>
                      </table>
                    )}
                  </div>
                </div>

                {/* Alerts Panel */}
                <div className="bg-white rounded-[2rem] shadow-sm border border-slate-100 p-8 h-fit sticky top-8">
                  <h3 className="text-xl font-bold text-slate-800 mb-6 flex items-center gap-2">
                      <AlertTriangle size={20} className="text-amber-500" />
                      Alertas del Día
                  </h3>
                  <div className="space-y-4 max-h-[400px] overflow-y-auto pr-1 custom-scrollbar">
                    {dashboardAlerts.length === 0 ? (
                        <div className="p-4 bg-slate-50 rounded-xl text-center text-sm text-slate-400">Todo en orden hoy</div>
                    ) : (
                        dashboardAlerts.slice(0, 5).map(alert => (
                            <NotificationItem 
                                key={alert.id}
                                title={alert.title} 
                                desc={alert.message} 
                                time={alert.time} 
                                type={alert.type} 
                            />
                        ))
                    )}
                  </div>
                  
                  <button 
                    onClick={() => setShowAlertsModal(true)}
                    className="w-full mt-6 py-3 text-sm font-semibold text-primary bg-primary/5 hover:bg-primary/10 rounded-xl transition-colors"
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
          
        </div>
      </main>
    </div>
  );
}

function SidebarItem({ icon, text, active, onClick }) {
  return (
    <button 
      onClick={onClick}
      className={`w-full flex items-center gap-3 px-4 py-3.5 rounded-xl text-sm font-medium transition-all duration-200 group relative overflow-hidden ${
        active 
          ? 'bg-primary text-white shadow-lg shadow-primary/30' 
          : 'text-slate-400 hover:bg-white/5 hover:text-white'
      }`}
    >
      <div className={`relative z-10 transition-transform duration-200 ${active ? 'scale-110' : 'group-hover:scale-110'}`}>
        {icon}
      </div>
      <span className="relative z-10">{text}</span>
      {active && <div className="absolute right-0 top-1/2 -translate-y-1/2 w-1 h-6 bg-white/30 rounded-l-full"></div>}
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

function TableRow({ name, id, dept, inTime, outTime, status }) {
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
          <div className="w-12 h-12 rounded-full bg-slate-100 flex items-center justify-center text-slate-500 font-bold text-lg group-hover:bg-white group-hover:shadow-md transition-all group-hover:scale-110 group-hover:text-primary border-2 border-transparent group-hover:border-slate-100">
            {name.charAt(0)}
          </div>
          <div>
            <p className="font-bold text-slate-800 text-sm">{name}</p>
            <p className="text-xs text-slate-400 font-medium">{id}</p>
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

function NotificationItem({ title, desc, time, type }) {
  const styles = {
    error: 'bg-red-50 text-red-900 border-red-100 hover:border-red-200',
    warning: 'bg-amber-50 text-amber-900 border-amber-100 hover:border-amber-200',
    info: 'bg-blue-50 text-blue-900 border-blue-100 hover:border-blue-200'
  };

  const icons = {
    error: <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></div>,
    warning: <Clock className="w-4 h-4 text-amber-600" />,
    info: <div className="w-5 h-5 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-[10px] font-bold border border-blue-200">i</div>
  };

  return (
    <div className={`p-4 rounded-2xl border transition-all cursor-pointer ${styles[type]}`}>
      <div className="flex gap-4 items-start">
        <div className="mt-1">{icons[type]}</div>
        <div className="flex-1">
          <h4 className="text-sm font-bold mb-1">{title}</h4>
          <p className="text-xs opacity-80 mb-2 font-medium leading-relaxed">{desc}</p>
          <span className="text-[10px] opacity-60 font-bold uppercase tracking-wider">{time}</span>
        </div>
      </div>
    </div>
  );
}

export default App;
