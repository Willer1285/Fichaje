import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Search, Plus, Edit2, Trash2, Shield, User, Phone, Mail, Eye, X } from 'lucide-react';
import { TypeSelectionModal, EmployeeFormModal, EmployeeCardModal } from '../components/EmployeeModals';

const API_URL = "/api";

function Employees() {
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  
  // Modales
  const [showTypeSelection, setShowTypeSelection] = useState(false);
  const [showFormModal, setShowFormModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  
  const [formType, setFormType] = useState('employee'); // 'employee' or 'admin'
  const [editingEmployee, setEditingEmployee] = useState(null);
  const [viewEmployee, setViewEmployee] = useState(null);

  // Catálogos
  const [departments, setDepartments] = useState([]);
  const [locations, setLocations] = useState([]);
  const [schedules, setSchedules] = useState([]);
  const [config, setConfig] = useState({ moneda: 'EUR' });

  useEffect(() => {
    console.log("Employees component mounted");
    fetchEmployees();
    fetchCatalogs();
  }, []);

  const fetchEmployees = async () => {
    try {
      console.log("Fetching employees...");
      const res = await axios.get(`${API_URL}/employees`);
      console.log("Employees loaded:", res.data);
      setEmployees(Array.isArray(res.data) ? res.data : []);
    } catch (error) {
      console.error("Error fetching employees:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchCatalogs = async () => {
    try {
      const [deptRes, locRes, schRes, confRes] = await Promise.all([
        axios.get(`${API_URL}/departments`),
        axios.get(`${API_URL}/locations`),
        axios.get(`${API_URL}/schedules`),
        axios.get(`${API_URL}/config`)
      ]);
      setDepartments(Array.isArray(deptRes.data) ? deptRes.data : []);
      setLocations(Array.isArray(locRes.data) ? locRes.data : []);
      setSchedules(Array.isArray(schRes.data) ? schRes.data : []);
      setConfig(confRes.data || { moneda: 'EUR' });
    } catch (err) {
      console.error("Error loading catalogs", err);
      // Asegurar que los estados siempre sean arrays incluso en caso de error
      setDepartments([]);
      setLocations([]);
      setSchedules([]);
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm("¿Estás seguro de eliminar este empleado?")) {
      try {
        await axios.delete(`${API_URL}/employees/${id}`);
        fetchEmployees();
      } catch (error) {
        alert("Error al eliminar: " + (error.response?.data?.detail || error.message));
      }
    }
  };

  const handleEdit = (emp) => {
    setEditingEmployee(emp);
    setFormType(emp.es_admin ? 'admin' : 'employee');
    setShowFormModal(true);
  };

  const handleView = (emp) => {
    setViewEmployee(emp);
    setShowViewModal(true);
  };

  const handleCreateNew = (type) => {
    setFormType(type);
    setEditingEmployee(null);
    setShowTypeSelection(false);
    setShowFormModal(true);
  };

  const filteredEmployees = employees.filter(emp =>
    emp.nombre?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    emp.apellidos?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    emp.dni?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <div>
            <h2 className="text-2xl font-bold text-slate-800">Gestión de Personal</h2>
            <p className="text-slate-500 text-sm">Administra empleados y administradores</p>
        </div>
        <button 
          onClick={() => setShowTypeSelection(true)}
          className="bg-primary hover:bg-blue-700 text-white px-5 py-2.5 rounded-xl flex items-center gap-2 font-bold shadow-lg shadow-primary/30 transition-all hover:-translate-y-0.5"
        >
          <Plus size={20} strokeWidth={2.5} /> Nuevo
        </button>
      </div>

      <div className="bg-white p-4 rounded-2xl shadow-sm border border-slate-100 mb-6 flex gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5" />
          <input 
            type="text" 
            placeholder="Buscar por nombre, DNI, teléfono..." 
            className="w-full pl-10 pr-4 py-2.5 bg-slate-50 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20 transition-all border border-transparent focus:border-primary/20"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
        <table className="w-full">
          <thead className="bg-slate-50/50 border-b border-slate-100">
            <tr className="text-left text-xs font-bold text-slate-500 uppercase tracking-wider">
              <th className="px-6 py-4">Empleado</th>
              <th className="px-6 py-4">Contacto</th>
              <th className="px-6 py-4">Cargo / Dept</th>
              <th className="px-6 py-4">Rol</th>
              <th className="px-6 py-4">Estado</th>
              <th className="px-6 py-4 text-right">Acciones</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-50">
            {Array.isArray(filteredEmployees) && filteredEmployees.map((emp) => (
              <tr key={emp.id} className="hover:bg-slate-50/80 transition-colors">
                <td className="px-6 py-4">
                  <div className="flex items-center gap-3">
                    {emp.foto_path ? (
                        <img src={`${API_URL.replace('/api', '')}${emp.foto_path}`} className="w-10 h-10 rounded-full object-cover shadow-sm border border-white flex-shrink-0" alt="" />
                    ) : (
                        <div className="w-10 h-10 min-w-[2.5rem] min-h-[2.5rem] rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 text-white flex items-center justify-center font-bold shadow-sm flex-shrink-0 text-sm">
                        {(emp.nombre?.charAt(0) || '')}{(emp.apellidos?.charAt(0) || '')}
                        </div>
                    )}
                    <div>
                      <p className="font-bold text-slate-800 text-sm">
                        {emp.primer_nombre || emp.nombre?.split(' ')[0] || emp.nombre} {emp.primer_apellido || emp.apellidos?.split(' ')[0] || emp.apellidos}
                      </p>
                      <p className="text-xs text-slate-400 font-mono">{emp.dni}</p>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <div className="flex flex-col gap-1">
                    <div className="flex items-center gap-1.5 text-slate-600">
                        <Phone size={12} />
                        <span className="text-xs">
                          {(() => {
                            if (!emp.telefono) return '-';
                            try {
                              return emp.telefono.startsWith('[') 
                                ? JSON.parse(emp.telefono)[0] || emp.telefono 
                                : emp.telefono;
                            } catch (e) {
                              return emp.telefono;
                            }
                          })()}
                        </span>
                    </div>
                    {emp.email && (
                        <div className="flex items-center gap-1.5 text-slate-600">
                            <Mail size={12} />
                            <span className="text-xs">{emp.email}</span>
                        </div>
                    )}
                  </div>
                </td>
                <td className="px-6 py-4">
                    <p className="text-sm font-medium text-slate-700">{emp.cargo || '-'}</p>
                    <p className="text-xs text-slate-400">
                        {Array.isArray(departments) && departments.find(d => d.id === emp.departamento_id)?.nombre || '-'}
                    </p>
                </td>
                <td className="px-6 py-4">
                    {emp.es_superadmin ? (
                        <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold bg-purple-100 text-purple-700">
                            <Shield size={12} /> Super Admin
                        </span>
                    ) : emp.es_admin ? (
                        <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold bg-blue-100 text-blue-700">
                            <Shield size={12} /> Admin
                        </span>
                    ) : (
                        <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold bg-slate-100 text-slate-600">
                            <User size={12} /> Empleado
                        </span>
                    )}
                </td>
                <td className="px-6 py-4">
                  <span className={`px-3 py-1 rounded-full text-xs font-bold ${emp.active ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-700'}`}>
                    {emp.active ? 'Activo' : 'Inactivo'}
                  </span>
                </td>
                <td className="px-6 py-4 text-right">
                  <div className="flex justify-end gap-2">
                    <button onClick={() => handleView(emp)} className="p-2 hover:bg-slate-100 text-slate-500 rounded-lg transition-colors" title="Ver Ficha">
                        <Eye size={18} />
                    </button>
                    <button onClick={() => handleEdit(emp)} className="p-2 hover:bg-blue-50 text-blue-600 rounded-lg transition-colors" title="Editar">
                      <Edit2 size={18} />
                    </button>
                    {!emp.es_superadmin && (
                        <button onClick={() => handleDelete(emp.id)} className="p-2 hover:bg-red-50 text-red-600 rounded-lg transition-colors" title="Eliminar">
                        <Trash2 size={18} />
                        </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Modal Selección Tipo */}
      {showTypeSelection && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4 animate-in fade-in duration-200">
          <div className="bg-white rounded-3xl w-full max-w-md shadow-2xl p-8 text-center relative overflow-hidden">
            <button onClick={() => setShowTypeSelection(false)} className="absolute top-4 right-4 text-slate-400 hover:text-slate-600"><X /></button>
            <h3 className="text-2xl font-bold text-slate-800 mb-2">Nuevo Registro</h3>
            <p className="text-slate-500 mb-8">Selecciona el tipo de usuario que deseas registrar</p>
            
            <div className="grid grid-cols-2 gap-4">
                <button onClick={() => handleCreateNew('employee')} className="p-6 rounded-2xl border-2 border-slate-100 hover:border-blue-500 hover:bg-blue-50 transition-all group flex flex-col items-center gap-3">
                    <div className="p-3 bg-blue-100 text-blue-600 rounded-full group-hover:scale-110 transition-transform"><User size={28} /></div>
                    <span className="font-bold text-slate-700 group-hover:text-blue-700">Empleado</span>
                </button>
                <button onClick={() => handleCreateNew('admin')} className="p-6 rounded-2xl border-2 border-slate-100 hover:border-purple-500 hover:bg-purple-50 transition-all group flex flex-col items-center gap-3">
                    <div className="p-3 bg-purple-100 text-purple-600 rounded-full group-hover:scale-110 transition-transform"><Shield size={28} /></div>
                    <span className="font-bold text-slate-700 group-hover:text-purple-700">Administrador</span>
                </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal Formulario */}
      {showFormModal && (
        <EmployeeFormModal
            isOpen={showFormModal}
            onClose={() => setShowFormModal(false)}
            type={formType}
            employee={editingEmployee}
            catalogs={{ departments, locations, schedules }}
            config={config}
            onSuccess={async () => {
              setShowFormModal(false);
              await fetchEmployees();

              // Si el empleado editado es el usuario actual, actualizar localStorage
              const currentUser = JSON.parse(localStorage.getItem('user') || '{}');
              if (editingEmployee && currentUser.id === editingEmployee.id) {
                try {
                  const res = await axios.get(`${API_URL}/employees/${editingEmployee.id}`);
                  const updatedUser = { ...currentUser, ...res.data };
                  localStorage.setItem('user', JSON.stringify(updatedUser));
                  window.dispatchEvent(new Event('storage')); // Trigger update
                } catch (err) {
                  console.error('Error actualizando usuario en localStorage:', err);
                }
              }
            }}
        />
      )}

      {/* Modal Ficha */}
      {showViewModal && viewEmployee && (
          <EmployeeCardModal
            isOpen={showViewModal}
            onClose={() => setShowViewModal(false)}
            employee={viewEmployee}
            catalogs={{ departments, locations, schedules }}
          />
      )}
    </div>
  );
}

// --- Componentes Internos eliminados, se importan desde components/EmployeeModals ---

export default Employees;
