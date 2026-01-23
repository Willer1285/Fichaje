import React, { useState, useEffect } from 'react';
import { Settings, Save, Building, Lock, Clock, MapPin, Briefcase, Plus, Trash2, Edit2, X, Upload } from 'lucide-react';
import axios from 'axios';
import { Toast, ConfirmDialog } from '../components/Toast';

const API_URL = "/api";

function Config() {
  const [activeTab, setActiveTab] = useState('company');

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="flex items-center gap-3 mb-8">
        <div className="bg-slate-100 p-3 rounded-xl text-slate-600">
          <Settings size={24} />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Configuración</h1>
          <p className="text-slate-500 text-sm">Gestiona los parámetros globales del sistema</p>
        </div>
      </div>

      {/* Tabs Navigation */}
      <div className="flex gap-2 overflow-x-auto pb-2 mb-6 custom-scrollbar">
        <TabButton active={activeTab === 'company'} onClick={() => setActiveTab('company')} icon={<Building size={18} />} label="Datos Empresa" />
        <TabButton active={activeTab === 'security'} onClick={() => setActiveTab('security')} icon={<Lock size={18} />} label="Horas Extras y Llegadas Tarde" />
        <TabButton active={activeTab === 'schedules'} onClick={() => setActiveTab('schedules')} icon={<Clock size={18} />} label="Horarios" />
        <TabButton active={activeTab === 'departments'} onClick={() => setActiveTab('departments')} icon={<Briefcase size={18} />} label="Departamentos" />
        <TabButton active={activeTab === 'locations'} onClick={() => setActiveTab('locations')} icon={<MapPin size={18} />} label="Ubicaciones" />
      </div>

      {/* Content Area */}
      <div className="bg-white rounded-2xl shadow-sm border border-slate-100 min-h-[500px]">
        {activeTab === 'company' && <CompanySettings />}
        {activeTab === 'security' && <SecuritySettings />}
        {activeTab === 'schedules' && <SchedulesManager />}
        {activeTab === 'departments' && <GenericCatalogManager title="Departamentos" endpoint="departments" itemName="Departamento" icon={<Briefcase />} />}
        {activeTab === 'locations' && <GenericCatalogManager title="Ubicaciones" endpoint="locations" itemName="Ubicación" icon={<MapPin />} />}
      </div>
    </div>
  );
}

function TabButton({ active, onClick, icon, label }) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-2 px-5 py-3 rounded-xl font-medium text-sm transition-all whitespace-nowrap ${
        active 
          ? 'bg-blue-50 text-blue-700 shadow-sm ring-1 ring-blue-200' 
          : 'text-slate-500 hover:bg-slate-50 hover:text-slate-700'
      }`}
    >
      {icon}
      {label}
    </button>
  );
}

// --- Componentes de Secciones ---

function CompanySettings() {
  const [config, setConfig] = useState({
    nombre_empresa: '',
    nombre_aplicacion: 'Fichaje',
    slogan: 'Pro',
    representante_legal: '',
    dni_cif: '',
    direccion: '',
    ciudad: '',
    codigo_postal: '',
    pais: 'España',
    telefono_empresa: '',
    email_empresa: '',
    logo_path: '',
    icono_path: '',
    zona_horaria: 'Europe/Madrid',
    moneda: 'EUR'
  });
  const [loading, setLoading] = useState(false);
  const [logoFile, setLogoFile] = useState(null);
  const [iconFile, setIconFile] = useState(null);
  const [toast, setToast] = useState(null);

  useEffect(() => {
    fetchConfig();
  }, []);

  const fetchConfig = async () => {
    try {
      const res = await axios.get(`${API_URL}/config`);
      console.log('Config recibido del servidor:', res.data);
      setConfig(res.data);
    } catch (err) {
      console.error("Error loading config", err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setToast(null);

    const formData = new FormData();
    Object.keys(config).forEach(key => {
        if (key !== 'logo_path' && key !== 'icono_path') {
            const val = config[key];
            formData.append(key, (val === null || val === undefined) ? "" : val);
        }
    });

    if (logoFile) formData.append('logo', logoFile);
    if (iconFile) formData.append('icono', iconFile);

    // Debug: Ver qué se está enviando
    console.log('Config antes de enviar:', config);
    console.log('FormData entries:');
    for (let [key, value] of formData.entries()) {
      console.log(`  ${key}: ${value}`);
    }

    try {
      const response = await axios.put(`${API_URL}/config`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      console.log('Respuesta del servidor:', response.data);
      setToast({ message: 'Configuración guardada correctamente', type: 'success' });
      setLogoFile(null);
      setIconFile(null);

      // Recargar configuración y verificar
      await fetchConfig();
    } catch (err) {
      console.error('Error al guardar configuración:', err);
      setToast({ message: 'Error al guardar la configuración', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8">
      <form onSubmit={handleSubmit} className="space-y-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          
          {/* Identidad Visual */}
          <div className="space-y-6">
            <h3 className="text-lg font-bold text-slate-800 border-b pb-2">Identidad Visual</h3>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="block text-sm font-medium text-slate-700">Nombre de la Aplicación</label>
                <input type="text" value={config.nombre_aplicacion} onChange={e => setConfig({...config, nombre_aplicacion: e.target.value})} className="input-field" />
              </div>

              <div className="space-y-2">
                <label className="block text-sm font-medium text-slate-700">Slogan / Tagline</label>
                <input type="text" value={config.slogan || ''} onChange={e => setConfig({...config, slogan: e.target.value})} className="input-field" placeholder="Pro" />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="block text-sm font-medium text-slate-700">Logo</label>
                <div className="border-2 border-dashed border-slate-200 rounded-xl p-4 text-center hover:bg-slate-50 transition-colors cursor-pointer relative group">
                  <input type="file" accept="image/*" onChange={e => setLogoFile(e.target.files[0])} className="absolute inset-0 opacity-0 cursor-pointer" />
                  {logoFile ? (
                    <div className="text-sm text-blue-600 font-medium truncate">{logoFile.name}</div>
                  ) : config.logo_path ? (
                    <img src={`${API_URL.replace('/api', '')}${config.logo_path}`} alt="Logo" className="h-16 mx-auto object-contain" />
                  ) : (
                    <div className="flex flex-col items-center text-slate-400">
                      <Upload size={24} className="mb-2" />
                      <span className="text-xs">Subir Logo</span>
                    </div>
                  )}
                </div>
              </div>

              <div className="space-y-2">
                <label className="block text-sm font-medium text-slate-700">Icono</label>
                <div className="border-2 border-dashed border-slate-200 rounded-xl p-4 text-center hover:bg-slate-50 transition-colors cursor-pointer relative group">
                  <input type="file" accept="image/*" onChange={e => setIconFile(e.target.files[0])} className="absolute inset-0 opacity-0 cursor-pointer" />
                  {iconFile ? (
                    <div className="text-sm text-blue-600 font-medium truncate">{iconFile.name}</div>
                  ) : config.icono_path ? (
                    <img src={`${API_URL.replace('/api', '')}${config.icono_path}`} alt="Icono" className="h-16 mx-auto object-contain" />
                  ) : (
                    <div className="flex flex-col items-center text-slate-400">
                      <Upload size={24} className="mb-2" />
                      <span className="text-xs">Subir Icono</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Configuración Regional */}
          <div className="space-y-6">
            <h3 className="text-lg font-bold text-slate-800 border-b pb-2">Configuración Regional</h3>
            <div className="grid grid-cols-1 gap-4">
               <div className="space-y-2">
                  <label className="block text-sm font-medium text-slate-700">Moneda</label>
                  <select value={config.moneda || 'EUR'} onChange={e => setConfig({...config, moneda: e.target.value})} className="input-field">
                      <option value="EUR">Euro (€)</option>
                      <option value="USD">Dólar ($)</option>
                      <option value="COP">Peso Colombiano</option>
                      <option value="MXN">Peso Mexicano</option>
                      <option value="ARS">Peso Argentino</option>
                      <option value="CLP">Peso Chileno</option>
                      <option value="PEN">Sol Peruano</option>
                      <option value="VES">Bolívar</option>
                  </select>
               </div>
            </div>
          </div>

          {/* Datos Legales */}
          <div className="space-y-6">
            <h3 className="text-lg font-bold text-slate-800 border-b pb-2">Información Legal</h3>
            <div className="space-y-4">
                <InputGroup label="Nombre Empresa / Razón Social" value={config.nombre_empresa} onChange={v => setConfig({...config, nombre_empresa: v})} />
                <div className="grid grid-cols-2 gap-4">
                    <InputGroup label="CIF / NIF" value={config.dni_cif} onChange={v => setConfig({...config, dni_cif: v})} />
                    <InputGroup label="Representante Legal" value={config.representante_legal} onChange={v => setConfig({...config, representante_legal: v})} />
                </div>
            </div>
          </div>
        </div>

        {/* Contacto y Ubicación */}
        <div className="space-y-6">
            <h3 className="text-lg font-bold text-slate-800 border-b pb-2">Contacto y Ubicación</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <InputGroup label="Dirección" value={config.direccion} onChange={v => setConfig({...config, direccion: v})} />
                <div className="grid grid-cols-3 gap-4">
                    <InputGroup label="Ciudad" value={config.ciudad} onChange={v => setConfig({...config, ciudad: v})} />
                    <InputGroup label="C. Postal" value={config.codigo_postal} onChange={v => setConfig({...config, codigo_postal: v})} />
                    <InputGroup label="País" value={config.pais} onChange={v => setConfig({...config, pais: v})} />
                </div>
                <InputGroup label="Teléfono" value={config.telefono_empresa} onChange={v => setConfig({...config, telefono_empresa: v})} />
                <InputGroup label="Correo Electrónico" value={config.email_empresa} type="email" onChange={v => setConfig({...config, email_empresa: v})} />
            </div>
        </div>


        <div className="flex justify-end pt-4">
          <button type="submit" disabled={loading} className="btn-primary">
            {loading ? 'Guardando...' : 'Guardar Cambios'}
          </button>
        </div>
      </form>

      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}
    </div>
  );
}

function SecuritySettings() {
    const [config, setConfig] = useState({
        clave_aprobacion_horas_extras: '',
        tiempo_tolerancia_minutos: 15,
        permitir_llegadas_tarde: true
    });
    const [loading, setLoading] = useState(false);
    const [toast, setToast] = useState(null);

    useEffect(() => {
        axios.get(`${API_URL}/config`).then(res => setConfig(res.data));
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setToast(null);
        try {
            const formData = new FormData();
            formData.append('clave_aprobacion_horas_extras', config.clave_aprobacion_horas_extras);
            formData.append('tiempo_tolerancia_minutos', config.tiempo_tolerancia_minutos);
            formData.append('permitir_llegadas_tarde', config.permitir_llegadas_tarde);

            await axios.put(`${API_URL}/config`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });

            setToast({ message: 'Configuración actualizada', type: 'success' });
        } catch (err) {
            console.error(err);
            setToast({ message: 'Error al guardar', type: 'error' });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="p-8 max-w-2xl">
            <h3 className="text-lg font-bold text-slate-800 mb-6">Horas Extras y Llegadas Tarde</h3>
            <form onSubmit={handleSubmit} className="space-y-6">
                <div className="space-y-2">
                    <label className="block text-sm font-medium text-slate-700">PIN Maestro para Horas Extras</label>
                    <input 
                        type="text" 
                        maxLength={6}
                        value={config.clave_aprobacion_horas_extras}
                        onChange={e => setConfig({...config, clave_aprobacion_horas_extras: e.target.value})}
                        className="input-field font-mono tracking-widest w-48"
                        placeholder="123456"
                    />
                    <p className="text-xs text-slate-500">Código de 6 dígitos requerido para autorizar horas extras.</p>
                </div>

                <div className="space-y-2">
                    <label className="block text-sm font-medium text-slate-700">Tolerancia de Llegada Tarde (minutos)</label>
                    <input 
                        type="number" 
                        value={config.tiempo_tolerancia_minutos}
                        onChange={e => setConfig({...config, tiempo_tolerancia_minutos: parseInt(e.target.value)})}
                        className="input-field w-32"
                    />
                    <p className="text-xs text-slate-500">Margen de tiempo antes de marcar un fichaje como "Retraso".</p>
                </div>

                <div className="flex items-center gap-3 pt-2">
                    <input 
                        type="checkbox" 
                        checked={config.permitir_llegadas_tarde}
                        onChange={e => setConfig({...config, permitir_llegadas_tarde: e.target.checked})}
                        className="w-5 h-5 text-blue-600 rounded focus:ring-blue-500"
                    />
                    <span className="text-sm font-medium text-slate-700">Permitir fichar con retraso (si no, bloquea)</span>
                </div>

                <button type="submit" disabled={loading} className="btn-primary mt-4">
                  {loading ? 'Guardando...' : 'Guardar Cambios'}
                </button>
            </form>

            {toast && (
                <Toast
                    message={toast.message}
                    type={toast.type}
                    onClose={() => setToast(null)}
                />
            )}
        </div>
    )
}

function GenericCatalogManager({ title, endpoint, itemName, icon }) {
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(false);
    const [newItem, setNewItem] = useState('');
    const [editingId, setEditingId] = useState(null);
    const [editValue, setEditValue] = useState('');
    const [toast, setToast] = useState(null);
    const [confirmDialog, setConfirmDialog] = useState(null);

    useEffect(() => {
        loadItems();
    }, []);

    const loadItems = async () => {
        setLoading(true);
        try {
            const res = await axios.get(`${API_URL}/${endpoint}`);
            setItems(Array.isArray(res.data) ? res.data : []);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleAdd = async (e) => {
        e.preventDefault();
        if (!newItem.trim()) return;
        try {
            await axios.post(`${API_URL}/${endpoint}`, { nombre: newItem, activo: true });
            setNewItem('');
            loadItems();
            setToast({ message: `${itemName} creado correctamente`, type: 'success' });
        } catch (err) {
            setToast({ message: `Error al crear ${itemName}`, type: 'error' });
        }
    };

    const handleDelete = async (id) => {
        setConfirmDialog({
            title: 'Confirmar eliminación',
            message: `¿Estás seguro de que deseas eliminar este ${itemName}?`,
            onConfirm: async () => {
                try {
                    await axios.delete(`${API_URL}/${endpoint}/${id}`);
                    loadItems();
                    setToast({ message: `${itemName} eliminado correctamente`, type: 'success' });
                } catch (err) {
                    setToast({ message: `Error al eliminar ${itemName}`, type: 'error' });
                }
                setConfirmDialog(null);
            },
            onCancel: () => setConfirmDialog(null)
        });
    };

    const startEdit = (item) => {
        setEditingId(item.id);
        setEditValue(item.nombre);
    };

    const saveEdit = async () => {
        try {
            await axios.put(`${API_URL}/${endpoint}/${editingId}`, { nombre: editValue, activo: true });
            setEditingId(null);
            loadItems();
            setToast({ message: `${itemName} actualizado correctamente`, type: 'success' });
        } catch (err) {
            setToast({ message: `Error al actualizar ${itemName}`, type: 'error' });
        }
    };

    return (
        <div className="p-8">
            <div className="flex items-center gap-3 mb-6">
                <div className="p-2 bg-blue-50 text-blue-600 rounded-lg">{icon}</div>
                <h3 className="text-xl font-bold text-slate-800">Gestión de {title}</h3>
            </div>

            <form onSubmit={handleAdd} className="flex gap-4 mb-8">
                <input 
                    type="text" 
                    value={newItem}
                    onChange={e => setNewItem(e.target.value)}
                    placeholder={`Nombre del nuevo ${itemName}...`}
                    className="input-field flex-1"
                />
                <button type="submit" className="btn-primary flex items-center gap-2">
                    <Plus size={18} /> Añadir
                </button>
            </form>

            <div className="bg-slate-50 rounded-xl border border-slate-200 overflow-hidden">
                {loading ? (
                    <div className="p-8 text-center text-slate-400">Cargando...</div>
                ) : items.length === 0 ? (
                    <div className="p-8 text-center text-slate-400">No hay elementos registrados</div>
                ) : (
                    <div className="divide-y divide-slate-200">
                        {items.map(item => (
                            <div key={item.id} className="p-4 flex items-center justify-between hover:bg-white transition-colors">
                                {editingId === item.id ? (
                                    <div className="flex gap-2 flex-1 mr-4">
                                        <input 
                                            type="text" 
                                            value={editValue} 
                                            onChange={e => setEditValue(e.target.value)}
                                            className="input-field py-1"
                                            autoFocus
                                        />
                                        <button onClick={saveEdit} className="text-emerald-600 hover:bg-emerald-50 p-2 rounded"><Save size={18} /></button>
                                        <button onClick={() => setEditingId(null)} className="text-slate-400 hover:bg-slate-100 p-2 rounded"><X size={18} /></button>
                                    </div>
                                ) : (
                                    <span className="font-medium text-slate-700">{item.nombre}</span>
                                )}
                                
                                {editingId !== item.id && (
                                    <div className="flex gap-2">
                                        <button onClick={() => startEdit(item)} className="p-2 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors">
                                            <Edit2 size={18} />
                                        </button>
                                        <button onClick={() => handleDelete(item.id)} className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors">
                                            <Trash2 size={18} />
                                        </button>
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {toast && (
                <Toast
                    message={toast.message}
                    type={toast.type}
                    onClose={() => setToast(null)}
                />
            )}

            {confirmDialog && (
                <ConfirmDialog
                    title={confirmDialog.title}
                    message={confirmDialog.message}
                    onConfirm={confirmDialog.onConfirm}
                    onCancel={confirmDialog.onCancel}
                    type="danger"
                    confirmText="Eliminar"
                    cancelText="Cancelar"
                />
            )}
        </div>
    );
}

function SchedulesManager() {
    const [schedules, setSchedules] = useState([]);
    const [loading, setLoading] = useState(false);
    const [isEditing, setIsEditing] = useState(false);
    const [currentSchedule, setCurrentSchedule] = useState({ nombre: '', dias_semana: [], hora_inicio: '09:00', hora_fin: '17:00' });
    const [toast, setToast] = useState(null);
    const [confirmDialog, setConfirmDialog] = useState(null);

    const DAYS = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];

    useEffect(() => { loadSchedules(); }, []);

    const loadSchedules = async () => {
        setLoading(true);
        try {
            const res = await axios.get(`${API_URL}/schedules`);
            setSchedules(Array.isArray(res.data) ? res.data : []);
        } catch(err) { console.error(err); } finally { setLoading(false); }
    };

    const handleSave = async (e) => {
        e.preventDefault();
        const data = {
            ...currentSchedule,
            dias_semana: Array.isArray(currentSchedule.dias_semana) ? currentSchedule.dias_semana.join(',') : currentSchedule.dias_semana,
            activo: true
        };

        try {
            if (currentSchedule.id) {
                await axios.put(`${API_URL}/schedules/${currentSchedule.id}`, data);
                setToast({ message: 'Horario actualizado correctamente', type: 'success' });
            } else {
                await axios.post(`${API_URL}/schedules`, data);
                setToast({ message: 'Horario creado correctamente', type: 'success' });
            }
            setIsEditing(false);
            loadSchedules();
            setCurrentSchedule({ nombre: '', dias_semana: [], hora_inicio: '09:00', hora_fin: '17:00' });
        } catch (err) {
            setToast({ message: 'Error al guardar horario', type: 'error' });
        }
    };

    const toggleDay = (day) => {
        const currentDays = Array.isArray(currentSchedule.dias_semana) ? currentSchedule.dias_semana : [];
        if (currentDays.includes(day)) {
            setCurrentSchedule({...currentSchedule, dias_semana: currentDays.filter(d => d !== day)});
        } else {
            setCurrentSchedule({...currentSchedule, dias_semana: [...currentDays, day]});
        }
    };

    const handleEdit = (schedule) => {
        setCurrentSchedule({
            ...schedule,
            dias_semana: Array.isArray(schedule.dias_semana)
                ? schedule.dias_semana
                : (schedule.dias_semana ? schedule.dias_semana.split(',') : [])
        });
        setIsEditing(true);
    };

    const handleDelete = async (id) => {
        setConfirmDialog({
            title: 'Confirmar eliminación',
            message: '¿Estás seguro de que deseas eliminar este horario?',
            onConfirm: async () => {
                try {
                    await axios.delete(`${API_URL}/schedules/${id}`);
                    loadSchedules();
                    setToast({ message: 'Horario eliminado correctamente', type: 'success' });
                } catch (err) {
                    setToast({ message: 'Error al eliminar horario', type: 'error' });
                }
                setConfirmDialog(null);
            },
            onCancel: () => setConfirmDialog(null)
        });
    };

    return (
        <div className="p-8">
            <div className="flex justify-between items-center mb-6">
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-blue-50 text-blue-600 rounded-lg"><Clock /></div>
                    <h3 className="text-xl font-bold text-slate-800">Gestión de Horarios</h3>
                </div>
                {!isEditing && (
                    <button onClick={() => setIsEditing(true)} className="btn-primary flex items-center gap-2">
                        <Plus size={18} /> Nuevo Horario
                    </button>
                )}
            </div>

            {isEditing && (
                <div className="bg-slate-50 p-6 rounded-2xl border border-slate-200 mb-8 animate-in fade-in slide-in-from-top-4">
                    <h4 className="font-bold text-slate-700 mb-4">{currentSchedule.id ? 'Editar Horario' : 'Nuevo Horario'}</h4>
                    <form onSubmit={handleSave} className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div className="space-y-1">
                                <label className="text-xs font-bold uppercase text-slate-500">Nombre</label>
                                <input type="text" value={currentSchedule.nombre} onChange={e => setCurrentSchedule({...currentSchedule, nombre: e.target.value})} className="input-field" placeholder="Ej: Jornada Completa" required />
                            </div>
                            <div className="space-y-1">
                                <label className="text-xs font-bold uppercase text-slate-500">Entrada</label>
                                <input type="time" value={currentSchedule.hora_inicio} onChange={e => setCurrentSchedule({...currentSchedule, hora_inicio: e.target.value})} className="input-field" required />
                            </div>
                            <div className="space-y-1">
                                <label className="text-xs font-bold uppercase text-slate-500">Salida</label>
                                <input type="time" value={currentSchedule.hora_fin} onChange={e => setCurrentSchedule({...currentSchedule, hora_fin: e.target.value})} className="input-field" required />
                            </div>
                        </div>
                        
                        <div className="space-y-2">
                            <label className="text-xs font-bold uppercase text-slate-500">Días Laborables</label>
                            <div className="flex flex-wrap gap-2">
                                {DAYS.map(day => (
                                    <button
                                        key={day}
                                        type="button"
                                        onClick={() => toggleDay(day)}
                                        className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
                                            (Array.isArray(currentSchedule.dias_semana) ? currentSchedule.dias_semana : []).includes(day)
                                                ? 'bg-blue-600 text-white shadow-md shadow-blue-500/30'
                                                : 'bg-white border border-slate-200 text-slate-500 hover:border-blue-300'
                                        }`}
                                    >
                                        {day.slice(0, 3)}
                                    </button>
                                ))}
                            </div>
                        </div>

                        <div className="flex justify-end gap-3 pt-2">
                            <button type="button" onClick={() => setIsEditing(false)} className="px-4 py-2 text-slate-500 hover:bg-slate-200 rounded-lg text-sm font-medium">Cancelar</button>
                            <button type="submit" className="btn-primary">Guardar</button>
                        </div>
                    </form>
                </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {schedules.map(sch => (
                    <div key={sch.id} className="border border-slate-200 rounded-xl p-5 hover:shadow-md transition-all bg-white group">
                        <div className="flex justify-between items-start mb-3">
                            <h4 className="font-bold text-slate-800">{sch.nombre}</h4>
                            <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                <button onClick={() => handleEdit(sch)} className="p-1.5 text-slate-400 hover:text-blue-600 bg-slate-50 rounded"><Edit2 size={14} /></button>
                                <button onClick={() => handleDelete(sch.id)} className="p-1.5 text-slate-400 hover:text-red-600 bg-slate-50 rounded"><Trash2 size={14} /></button>
                            </div>
                        </div>
                        <div className="flex items-center gap-2 text-slate-600 text-sm mb-3">
                            <Clock size={14} />
                            <span>{sch.hora_inicio} - {sch.hora_fin}</span>
                        </div>
                        <div className="flex flex-wrap gap-1">
                            {sch.dias_semana.split(',').map(d => (
                                <span key={d} className="text-[10px] px-2 py-0.5 bg-slate-100 text-slate-500 rounded-full">{d.slice(0,3)}</span>
                            ))}
                        </div>
                    </div>
                ))}
            </div>

            {toast && (
                <Toast
                    message={toast.message}
                    type={toast.type}
                    onClose={() => setToast(null)}
                />
            )}

            {confirmDialog && (
                <ConfirmDialog
                    title={confirmDialog.title}
                    message={confirmDialog.message}
                    onConfirm={confirmDialog.onConfirm}
                    onCancel={confirmDialog.onCancel}
                    type="danger"
                    confirmText="Eliminar"
                    cancelText="Cancelar"
                />
            )}
        </div>
    )
}

function InputGroup({ label, value, onChange, type = "text" }) {
    return (
        <div className="space-y-1">
            <label className="block text-sm font-medium text-slate-700">{label}</label>
            <input 
                type={type} 
                value={value} 
                onChange={e => onChange(e.target.value)} 
                className="input-field" 
            />
        </div>
    );
}

// Add global styles for inputs
const style = document.createElement('style');
style.textContent = `
  .input-field {
    width: 100%;
    padding: 0.75rem 1rem;
    background-color: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 0.75rem;
    outline: none;
    transition: all 0.2s;
  }
  .input-field:focus {
    background-color: #fff;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }
  .btn-primary {
    background-color: #2563eb;
    color: white;
    padding: 0.75rem 1.5rem;
    border-radius: 0.75rem;
    font-weight: 600;
    transition: all 0.2s;
    box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2);
  }
  .btn-primary:hover {
    background-color: #1d4ed8;
    transform: translateY(-1px);
    box-shadow: 0 6px 8px -1px rgba(37, 99, 235, 0.3);
  }
  .btn-primary:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }
`;
document.head.appendChild(style);

export default Config;
