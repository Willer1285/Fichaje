import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { X, User, Shield, Camera, Phone, Trash2, DollarSign, LogOut, Plus, Briefcase, Mail } from 'lucide-react';

const API_URL = "/api";

const getCurrencySymbol = (currency) => {
    if (!currency) return '€';
    switch(currency) {
        case 'EUR': return '€';
        case 'USD': return '$';
        case 'GBP': return '£';
        case 'JPY': return '¥';
        case 'COP': return '$';
        case 'MXN': return '$';
        case 'ARS': return '$';
        case 'CLP': return '$';
        case 'PEN': return 'S/';
        case 'VES': return 'Bs';
        default: return '$';
    }
};

export function TypeSelectionModal({ onClose, onSelect }) {
  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4 animate-in fade-in duration-200">
      <div className="bg-white rounded-3xl w-full max-w-md shadow-2xl p-8 text-center relative overflow-hidden">
        <button onClick={onClose} className="absolute top-4 right-4 text-slate-400 hover:text-slate-600"><X /></button>
        <h3 className="text-2xl font-bold text-slate-800 mb-2">Nuevo Registro</h3>
        <p className="text-slate-500 mb-8">Selecciona el tipo de usuario que deseas registrar</p>
        
        <div className="grid grid-cols-2 gap-4">
            <button onClick={() => onSelect('employee')} className="p-6 rounded-2xl border-2 border-slate-100 hover:border-blue-500 hover:bg-blue-50 transition-all group flex flex-col items-center gap-3">
                <div className="p-3 bg-blue-100 text-blue-600 rounded-full group-hover:scale-110 transition-transform"><User size={28} /></div>
                <span className="font-bold text-slate-700 group-hover:text-blue-700">Empleado</span>
            </button>
            <button onClick={() => onSelect('admin')} className="p-6 rounded-2xl border-2 border-slate-100 hover:border-purple-500 hover:bg-purple-50 transition-all group flex flex-col items-center gap-3">
                <div className="p-3 bg-purple-100 text-purple-600 rounded-full group-hover:scale-110 transition-transform"><Shield size={28} /></div>
                <span className="font-bold text-slate-700 group-hover:text-purple-700">Administrador</span>
            </button>
        </div>
      </div>
    </div>
  );
}

export function EmployeeFormModal({ isOpen, onClose, type, employee, onSuccess }) {
    if (!isOpen) return null;

    const isEdit = !!employee;
    const [activeTab, setActiveTab] = useState(0);
    const [loading, setLoading] = useState(false);
    const [photoPreview, setPhotoPreview] = useState(null);
    const [catalogs, setCatalogs] = useState({ departments: [], locations: [], schedules: [] });
    
    // Cargar catálogos
    useEffect(() => {
        const fetchCatalogs = async () => {
            try {
                const [deptRes, locRes, schRes] = await Promise.all([
                    axios.get(`${API_URL}/departments`),
                    axios.get(`${API_URL}/locations`),
                    axios.get(`${API_URL}/schedules`)
                ]);
                setCatalogs({
                    departments: deptRes.data,
                    locations: locRes.data,
                    schedules: schRes.data
                });
            } catch (err) {
                console.error("Error loading catalogs", err);
            }
        };
        fetchCatalogs();
    }, []);

    // Parsear telefonos si viene de BD
    const initialPhones = employee?.telefono ? (
        employee.telefono.startsWith('[') ? JSON.parse(employee.telefono) : [employee.telefono]
    ) : [''];

    const [formData, setFormData] = useState({
        nombre: employee?.nombre || '',
        apellidos: employee?.apellidos || '',
        dni: employee?.dni || '',
        telefonos: initialPhones,
        email: employee?.email || '',
        numero_empleado: employee?.numero_empleado || '',
        cargo: employee?.cargo || '',
        departamento_id: employee?.departamento_id || '',
        ubicacion_id: employee?.ubicacion_id || '',
        turno_id: employee?.turno_id || '',
        pago_por_hora: employee?.pago_por_hora || 0,
        pago_hora_especial: employee?.pago_hora_especial || 0,
        es_admin: type === 'admin',
        password: '',
        foto: null,
        // Campos de egreso
        es_egresado: employee ? !employee.active : false,
        fecha_egreso: employee?.fecha_egreso ? employee.fecha_egreso.split('T')[0] : '',
        motivo_egreso: employee?.motivo_egreso || ''
    });

    useEffect(() => {
        if (employee?.foto_path) {
            setPhotoPreview(`${API_URL.replace('/api', '')}${employee.foto_path}`);
        }
    }, [employee]);

    const handlePhoneChange = (index, value) => {
        const newPhones = [...formData.telefonos];
        newPhones[index] = value;
        setFormData({...formData, telefonos: newPhones});
    };

    const addPhone = () => {
        setFormData({...formData, telefonos: [...formData.telefonos, '']});
    };

    const removePhone = (index) => {
        if (formData.telefonos.length === 1) return;
        const newPhones = formData.telefonos.filter((_, i) => i !== index);
        setFormData({...formData, telefonos: newPhones});
    };

    const handlePhotoChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            setFormData({...formData, foto: file});
            setPhotoPreview(URL.createObjectURL(file));
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);

        const data = new FormData();
        // Campos básicos
        data.append('nombre', formData.nombre);
        data.append('apellidos', formData.apellidos);
        data.append('dni', formData.dni);
        data.append('telefono', JSON.stringify(formData.telefonos.filter(t => t.trim()))); // Enviar como JSON string
        data.append('email', formData.email);
        
        if (type === 'employee' || isEdit) {
            data.append('numero_empleado', formData.numero_empleado);
            data.append('cargo', formData.cargo);
            if(formData.departamento_id) data.append('departamento_id', formData.departamento_id);
            if(formData.ubicacion_id) data.append('ubicacion_id', formData.ubicacion_id);
            if(formData.turno_id) data.append('turno_id', formData.turno_id);
            data.append('pago_por_hora', formData.pago_por_hora);
            data.append('pago_hora_especial', formData.pago_hora_especial);
        }

        data.append('es_admin', formData.es_admin);
        if (formData.password) data.append('password', formData.password);
        if (formData.foto) data.append('foto', formData.foto);

        if (isEdit) {
            data.append('es_egresado', formData.es_egresado);
            if (formData.es_egresado) {
                data.append('fecha_egreso', formData.fecha_egreso);
                data.append('motivo_egreso', formData.motivo_egreso);
            }
        }

        try {
            if (isEdit) {
                await axios.put(`${API_URL}/employees/${employee.id}`, data, { headers: { 'Content-Type': 'multipart/form-data' } });
            } else {
                await axios.post(`${API_URL}/employees`, data, { headers: { 'Content-Type': 'multipart/form-data' } });
            }
            if(onSuccess) onSuccess();
            onClose();
        } catch (error) {
            alert("Error: " + (error.response?.data?.detail || error.message));
        } finally {
            setLoading(false);
        }
    };

    const tabs = type === 'admin' ? ['Datos Personales'] : ['Datos Personales', 'Información Laboral', 'Salarial'];

    return (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4 overflow-y-auto">
            <div className="bg-white rounded-3xl w-full max-w-3xl shadow-2xl flex flex-col max-h-[90vh]">
                {/* Header */}
                <div className="p-6 border-b border-slate-100 flex justify-between items-center bg-white rounded-t-3xl sticky top-0 z-10">
                    <div>
                        <h3 className="text-xl font-bold text-slate-800">
                            {isEdit ? 'Editar Registro' : type === 'admin' ? 'Nuevo Administrador' : 'Nuevo Empleado'}
                        </h3>
                        <p className="text-sm text-slate-500">{isEdit ? 'Modifica los datos del usuario' : 'Completa la información requerida'}</p>
                    </div>
                    <button onClick={onClose} className="p-2 hover:bg-slate-100 rounded-full"><X size={20} /></button>
                </div>

                {/* Tabs */}
                {type !== 'admin' && (
                    <div className="flex border-b border-slate-100 px-6">
                        {tabs.map((tab, idx) => (
                            <button 
                                key={idx}
                                onClick={() => setActiveTab(idx)}
                                className={`px-4 py-3 text-sm font-bold border-b-2 transition-colors ${activeTab === idx ? 'border-primary text-primary' : 'border-transparent text-slate-400 hover:text-slate-600'}`}
                            >
                                {tab}
                            </button>
                        ))}
                    </div>
                )}

                {/* Form Content */}
                <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto p-8 custom-scrollbar">
                    
                    {/* Tab 0: Personales (Admin & Empleado) */}
                    <div className={activeTab === 0 ? 'block space-y-6' : 'hidden'}>
                        <div className="flex gap-6">
                            {/* Foto Upload */}
                            <div className="w-1/3 flex flex-col items-center gap-4">
                                <div className="w-40 h-40 rounded-full bg-slate-100 border-4 border-white shadow-lg overflow-hidden relative group">
                                    {photoPreview ? (
                                        <img src={photoPreview} alt="Preview" className="w-full h-full object-cover" />
                                    ) : (
                                        <div className="w-full h-full flex flex-col items-center justify-center text-slate-300">
                                            <User size={48} />
                                        </div>
                                    )}
                                    <label className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer text-white font-medium">
                                        <Camera size={24} className="mr-2" /> Cambiar
                                        <input type="file" accept="image/*" className="hidden" onChange={handlePhotoChange} />
                                    </label>
                                </div>
                                <p className="text-xs text-center text-slate-400 w-40">Formato JPG/PNG. Máx 2MB.<br/>Se detectará y recortará el rostro automáticamente.</p>
                            </div>

                            {/* Datos Básicos */}
                            <div className="flex-1 space-y-4">
                                <div className="grid grid-cols-2 gap-4">
                                    <Input label="Nombres" value={formData.nombre} onChange={e => setFormData({...formData, nombre: e.target.value})} required />
                                    <Input label="Apellidos" value={formData.apellidos} onChange={e => setFormData({...formData, apellidos: e.target.value})} required />
                                </div>
                                <Input label="DNI / NIE" value={formData.dni} onChange={e => setFormData({...formData, dni: e.target.value})} required placeholder="12345678A" />
                                <Input label="Correo Electrónico" type="email" value={formData.email} onChange={e => setFormData({...formData, email: e.target.value})} placeholder="email@empresa.com" />
                                
                                {/* Teléfonos Dinámicos */}
                                <div>
                                    <label className="block text-sm font-bold text-slate-700 mb-2">Teléfonos</label>
                                    {formData.telefonos.map((tel, idx) => (
                                        <div key={idx} className="flex gap-2 mb-2">
                                            <input 
                                                type="tel" 
                                                className="input-field" 
                                                value={tel}
                                                onChange={e => handlePhoneChange(idx, e.target.value)}
                                                placeholder="+34 600 000 000"
                                            />
                                            {idx === formData.telefonos.length - 1 ? (
                                                <button type="button" onClick={addPhone} className="p-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100"><Plus size={18} /></button>
                                            ) : (
                                                <button type="button" onClick={() => removePhone(idx)} className="p-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100"><Trash2 size={18} /></button>
                                            )}
                                        </div>
                                    ))}
                                </div>

                                {type === 'admin' && (
                                    <div className="pt-4 border-t border-slate-100 mt-4">
                                        <Input 
                                            label="Contraseña de Acceso" 
                                            type="password" 
                                            value={formData.password} 
                                            onChange={e => setFormData({...formData, password: e.target.value})} 
                                            required={!isEdit} 
                                            placeholder={isEdit ? "•••••• (Dejar vacío para mantener)" : "••••••"}
                                        />
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>

                    {/* Tab 1: Laboral (Solo Empleados) */}
                    <div className={activeTab === 1 ? 'block space-y-6' : 'hidden'}>
                        <div className="grid grid-cols-2 gap-6">
                            <Input label="Nro de Empleado" value={formData.numero_empleado} onChange={e => setFormData({...formData, numero_empleado: e.target.value})} />
                            <Input label="Cargo" value={formData.cargo} onChange={e => setFormData({...formData, cargo: e.target.value})} />
                            
                            <Select label="Departamento" value={formData.departamento_id} onChange={e => setFormData({...formData, departamento_id: e.target.value})}>
                                <option value="">Seleccionar...</option>
                                {catalogs.departments.map(d => <option key={d.id} value={d.id}>{d.nombre}</option>)}
                            </Select>

                            <Select label="Ubicación / Sede" value={formData.ubicacion_id} onChange={e => setFormData({...formData, ubicacion_id: e.target.value})}>
                                <option value="">Seleccionar...</option>
                                {catalogs.locations.map(l => <option key={l.id} value={l.id}>{l.nombre}</option>)}
                            </Select>

                            <Select label="Horario" value={formData.turno_id} onChange={e => setFormData({...formData, turno_id: e.target.value})}>
                                <option value="">Seleccionar...</option>
                                {catalogs.schedules.map(s => <option key={s.id} value={s.id}>{s.nombre} ({s.hora_inicio}-{s.hora_fin})</option>)}
                            </Select>
                        </div>

                        {/* Estado Egresado (Solo Edición) */}
                        {isEdit && (
                            <div className="bg-slate-50 p-6 rounded-2xl border border-slate-200 mt-6">
                                <div className="flex items-center justify-between mb-4">
                                    <div className="flex items-center gap-2 text-slate-800 font-bold">
                                        <LogOut size={20} className="text-red-500" />
                                        <span>Estado del Empleado</span>
                                    </div>
                                    <label className="relative inline-flex items-center cursor-pointer">
                                        <input type="checkbox" className="sr-only peer" checked={formData.es_egresado} onChange={e => setFormData({...formData, es_egresado: e.target.checked})} />
                                        <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-red-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-red-600"></div>
                                        <span className="ml-3 text-sm font-medium text-slate-600">{formData.es_egresado ? 'Marcado como Egresado' : 'Empleado Activo'}</span>
                                    </label>
                                </div>
                                
                                {formData.es_egresado && (
                                    <div className="grid grid-cols-2 gap-4 animate-in fade-in slide-in-from-top-2">
                                        <Input type="date" label="Fecha de Egreso" value={formData.fecha_egreso} onChange={e => setFormData({...formData, fecha_egreso: e.target.value})} required={formData.es_egresado} />
                                        <Input label="Motivo" value={formData.motivo_egreso} onChange={e => setFormData({...formData, motivo_egreso: e.target.value})} placeholder="Renuncia, Despido..." required={formData.es_egresado} />
                                    </div>
                                )}
                            </div>
                        )}
                    </div>

                    {/* Tab 2: Salarial (Solo Empleados) */}
                    <div className={activeTab === 2 ? 'block space-y-6' : 'hidden'}>
                        <div className="grid grid-cols-2 gap-6">
                            <Input 
                                label={`Pago Hora Normal (${config?.moneda || 'EUR'})`} 
                                type="number" 
                                value={formData.pago_por_hora} 
                                onChange={e => setFormData({...formData, pago_por_hora: e.target.value})} 
                                icon={<span className="text-sm font-bold text-slate-400">{getCurrencySymbol(config?.moneda)}</span>} 
                            />
                            <Input 
                                label={`Pago Hora Especial (${config?.moneda || 'EUR'})`} 
                                type="number" 
                                value={formData.pago_hora_especial} 
                                onChange={e => setFormData({...formData, pago_hora_especial: e.target.value})} 
                                icon={<span className="text-sm font-bold text-slate-400">{getCurrencySymbol(config?.moneda)}</span>} 
                            />
                        </div>
                        <div className="p-4 bg-blue-50 text-blue-800 text-sm rounded-xl">
                            ℹ️ La hora especial aplica para horas extras, feriados y fines de semana según configuración global.
                        </div>
                    </div>

                </form>

                {/* Footer Buttons */}
                <div className="p-6 border-t border-slate-100 flex justify-end gap-3 bg-white rounded-b-3xl">
                    <button type="button" onClick={onClose} className="px-6 py-3 rounded-xl border border-slate-200 text-slate-600 font-bold hover:bg-slate-50 transition-colors">Cancelar</button>
                    <button onClick={handleSubmit} disabled={loading} className="px-8 py-3 rounded-xl bg-primary text-white font-bold hover:bg-blue-700 shadow-lg shadow-primary/30 transition-all disabled:opacity-70 flex items-center gap-2">
                        {loading ? 'Guardando...' : 'Guardar Registro'}
                    </button>
                </div>
            </div>
        </div>
    );
}

export function EmployeeCardModal({ isOpen, onClose, employee, catalogs }) {
    if (!isOpen || !employee) return null;

    const department = catalogs.departments.find(d => d.id === employee.departamento_id)?.nombre || '-';
    const location = catalogs.locations.find(l => l.id === employee.ubicacion_id)?.nombre || '-';
    const schedule = catalogs.schedules.find(s => s.id === employee.turno_id);
    const phones = employee.telefono.startsWith('[') ? JSON.parse(employee.telefono) : [employee.telefono];

    return (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-3xl w-full max-w-4xl shadow-2xl overflow-hidden flex">
                {/* Sidebar Visual */}
                <div className="w-1/3 bg-slate-50 p-8 flex flex-col items-center text-center border-r border-slate-100">
                    <div className="w-48 h-48 rounded-2xl bg-white shadow-lg overflow-hidden mb-6 border-4 border-white">
                        {employee.foto_path ? (
                            <img src={`${API_URL.replace('/api', '')}${employee.foto_path}`} className="w-full h-full object-cover" alt="" />
                        ) : (
                            <div className="w-full h-full flex items-center justify-center bg-slate-100 text-slate-300">
                                <User size={64} />
                            </div>
                        )}
                    </div>
                    <h2 className="text-2xl font-bold text-slate-800 mb-1">{employee.nombre}</h2>
                    <h3 className="text-xl text-primary font-medium mb-4">{employee.apellidos}</h3>
                    
                    <div className="w-full space-y-3">
                        <div className="bg-white p-3 rounded-xl border border-slate-200 shadow-sm">
                            <p className="text-xs text-slate-400 uppercase font-bold tracking-wider mb-1">Cargo</p>
                            <p className="font-semibold text-slate-700">{employee.cargo || '-'}</p>
                        </div>
                        <div className="bg-white p-3 rounded-xl border border-slate-200 shadow-sm">
                            <p className="text-xs text-slate-400 uppercase font-bold tracking-wider mb-1">Nº Empleado</p>
                            <p className="font-mono font-semibold text-slate-700">{employee.numero_empleado || '-'}</p>
                        </div>
                    </div>
                </div>

                {/* Info Content */}
                <div className="flex-1 p-8 relative">
                    <button onClick={onClose} className="absolute top-6 right-6 p-2 hover:bg-slate-100 rounded-full text-slate-400 hover:text-slate-600"><X size={24} /></button>
                    
                    <h3 className="text-lg font-bold text-slate-800 mb-6 flex items-center gap-2">
                        <Briefcase size={20} className="text-primary" /> Información Profesional
                    </h3>
                    
                    <div className="grid grid-cols-2 gap-6 mb-8">
                        <InfoItem label="Departamento" value={department} />
                        <InfoItem label="Ubicación" value={location} />
                        <InfoItem label="Horario" value={schedule ? `${schedule.nombre} (${schedule.hora_inicio}-${schedule.hora_fin})` : '-'} />
                        <InfoItem label="Fecha Ingreso" value={employee.fecha_ingreso ? employee.fecha_ingreso.split('T')[0] : '-'} />
                    </div>

                    <div className="border-t border-slate-100 my-6"></div>

                    <h3 className="text-lg font-bold text-slate-800 mb-6 flex items-center gap-2">
                        <Phone size={20} className="text-primary" /> Contacto
                    </h3>

                    <div className="grid grid-cols-2 gap-6">
                        <div className="col-span-2">
                            <p className="text-sm text-slate-400 mb-1 font-medium">Teléfonos</p>
                            <div className="flex flex-wrap gap-2">
                                {phones.map((p, i) => (
                                    <span key={i} className="px-3 py-1.5 bg-slate-100 rounded-lg text-sm font-mono text-slate-700">{p}</span>
                                ))}
                            </div>
                        </div>
                        <InfoItem label="Email" value={employee.email} />
                        <InfoItem label="DNI / NIE" value={employee.dni} />
                    </div>

                    {!employee.active && (
                        <div className="mt-8 p-4 bg-red-50 border border-red-100 rounded-xl">
                            <div className="flex items-center gap-2 text-red-800 font-bold mb-2">
                                <LogOut size={18} /> Empleado Egresado
                            </div>
                            <div className="grid grid-cols-2 gap-4 text-sm">
                                <div><span className="font-bold text-red-700">Fecha:</span> {employee.fecha_egreso ? employee.fecha_egreso.split('T')[0] : '-'}</div>
                                <div><span className="font-bold text-red-700">Motivo:</span> {employee.motivo_egreso}</div>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}

function InfoItem({ label, value }) {
    return (
        <div>
            <p className="text-sm text-slate-400 mb-1 font-medium">{label}</p>
            <p className="font-semibold text-slate-700">{value || '-'}</p>
        </div>
    )
}

function Input({ label, ...props }) {
    return (
        <div className="space-y-1 w-full">
            <label className="block text-sm font-bold text-slate-700">{label}</label>
            <div className="relative">
                {props.icon && <div className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">{props.icon}</div>}
                <input 
                    {...props} 
                    className={`w-full p-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all ${props.icon ? 'pl-10' : ''}`} 
                />
            </div>
        </div>
    )
}

function Select({ label, children, ...props }) {
    return (
        <div className="space-y-1 w-full">
            <label className="block text-sm font-bold text-slate-700">{label}</label>
            <select 
                {...props} 
                className="w-full p-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all appearance-none"
            >
                {children}
            </select>
        </div>
    )
}
