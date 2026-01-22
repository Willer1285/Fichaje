import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Calendar as CalendarIcon, Download, Filter } from 'lucide-react';
import { SuccessModal } from '../components/SuccessModal';

const API_URL = "/api";

function Attendance() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [startDate, setStartDate] = useState(new Date().toISOString().split('T')[0]);
  const [endDate, setEndDate] = useState(new Date().toISOString().split('T')[0]);
  const [employees, setEmployees] = useState([]);
  const [selectedEmployee, setSelectedEmployee] = useState('');
  
  // Modal state
  const [showSuccessModal, setShowSuccessModal] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  useEffect(() => {
    fetchEmployees();
    fetchHistory();
  }, []);

  const fetchEmployees = async () => {
    try {
      const res = await axios.get(`${API_URL}/employees`);
      // Validar que sea un array antes de asignar
      if (Array.isArray(res.data)) {
        setEmployees(res.data);
      } else {
        console.error("Error: La respuesta de empleados no es un array", res.data);
        setEmployees([]);
      }
    } catch (error) {
      console.error("Error cargando empleados:", error);
      setEmployees([]);
    }
  };

  const fetchHistory = async () => {
    try {
      setLoading(true);
      let url = `${API_URL}/attendance/history?start_date=${startDate}&end_date=${endDate}`;
      if (selectedEmployee) {
        url += `&employee_id=${selectedEmployee}`;
      }
      const res = await axios.get(url);
      // Validar que sea un array antes de asignar
      if (Array.isArray(res.data)) {
        setHistory(res.data);
      } else {
        console.error("Error: La respuesta del historial no es un array", res.data);
        setHistory([]);
      }
    } catch (error) {
      console.error("Error fetching history:", error);
      setHistory([]);
    } finally {
      setLoading(false);
    }
  };

  const exportData = async (format) => {
    try {
        setLoading(true);
        // Construir filtros
        const payload = {
            type: selectedEmployee ? 'individual' : 'todos',
            start_date: startDate,
            end_date: endDate,
            format: format
        };
        if (selectedEmployee) payload.employee_id = parseInt(selectedEmployee);

        const response = await axios.post(`${API_URL}/reports/generate`, payload, {
            responseType: 'blob'
        });

        const filename = `reporte_asistencia_${startDate}_${endDate}.${format === 'excel' ? 'xlsx' : 'pdf'}`;
        const blob = new Blob([response.data]);

        // Convertir blob a base64 para enviar a pywebview si existe
        const reader = new FileReader();
        reader.readAsDataURL(blob);
        reader.onloadend = async () => {
            const base64data = reader.result;
            
            // Verificar si existe API pywebview (Desktop App)
            if (window.pywebview && window.pywebview.api) {
                try {
                    const res = await window.pywebview.api.save_file(filename, base64data);
                    if (res.success) {
                        setSuccessMessage(`Archivo guardado exitosamente en:\n${res.path}`);
                        setShowSuccessModal(true);
                    } else {
                        alert("Error guardando archivo: " + res.error);
                    }
                } catch (e) {
                    alert("Error comunicando con la aplicación de escritorio: " + e);
                }
            } else {
                // Fallback web browser standard
                const url = window.URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = url;
                link.setAttribute('download', filename);
                document.body.appendChild(link);
                link.click();
                link.remove();
                window.URL.revokeObjectURL(url);

                setSuccessMessage(`Reporte ${format.toUpperCase()} exportado exitosamente.`);
                setShowSuccessModal(true);
            }
            setLoading(false);
        };

    } catch (error) {
        console.error("Error exportando:", error);
        setLoading(false);
        
        let errorMessage = "Error al exportar datos.";
        
        if (error.response && error.response.data instanceof Blob) {
             try {
                 const text = await error.response.data.text();
                 const json = JSON.parse(text);
                 errorMessage += " " + (json.detail || json.message || "");
             } catch (e) {}
        } else if (error.response?.data?.detail) {
             errorMessage += " " + error.response.data.detail;
        }
        
        alert(errorMessage);
    }
  };

  return (
    <div className="p-8">
      <h2 className="text-2xl font-bold text-slate-800 mb-8">Historial de Fichajes</h2>

      {/* Filters */}
      <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 mb-8 flex flex-wrap gap-4 items-end">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Desde</label>
          <input 
            type="date" 
            className="input-field" 
            value={startDate} 
            onChange={(e) => setStartDate(e.target.value)} 
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Hasta</label>
          <input 
            type="date" 
            className="input-field" 
            value={endDate} 
            onChange={(e) => setEndDate(e.target.value)} 
          />
        </div>
        <div className="flex-1 min-w-[200px]">
          <label className="block text-sm font-medium text-slate-700 mb-1">Empleado</label>
          <select 
            className="input-field" 
            value={selectedEmployee} 
            onChange={(e) => setSelectedEmployee(e.target.value)}
          >
            <option value="">Todos los empleados</option>
            {Array.isArray(employees) && employees.map(emp => (
              <option key={emp.id} value={emp.id}>{emp.nombre} {emp.apellidos}</option>
            ))}
          </select>
        </div>
        <button 
          onClick={fetchHistory}
          className="bg-primary hover:bg-blue-700 text-white px-6 py-2.5 rounded-xl font-bold shadow-lg shadow-primary/30 transition-all flex items-center gap-2"
        >
          <Filter size={18} /> Filtrar
        </button>
        <div className="flex gap-2">
            <button 
              onClick={() => exportData('excel')}
              disabled={loading}
              className="bg-white border border-slate-200 text-slate-600 hover:bg-slate-50 px-4 py-2.5 rounded-xl font-bold transition-all flex items-center gap-2 disabled:opacity-50"
            >
              <Download size={18} /> Excel
            </button>
            <button 
              onClick={() => exportData('pdf')}
              disabled={loading}
              className="bg-white border border-slate-200 text-slate-600 hover:bg-slate-50 px-4 py-2.5 rounded-xl font-bold transition-all flex items-center gap-2 disabled:opacity-50"
            >
              <Download size={18} /> PDF
            </button>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
        <table className="w-full">
          <thead className="bg-slate-50 border-b border-slate-100">
            <tr className="text-left text-xs font-bold text-slate-500 uppercase">
              <th className="px-6 py-4">Fecha</th>
              <th className="px-6 py-4">Empleado</th>
              <th className="px-6 py-4">DNI</th>
              <th className="px-6 py-4">Entrada</th>
              <th className="px-6 py-4">Salida</th>
              <th className="px-6 py-4">Horas</th>
              <th className="px-6 py-4 text-right">Estado</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-50">
            {(!history || history.length === 0) ? (
              <tr>
                <td colSpan="7" className="px-6 py-8 text-center text-slate-400">
                  No se encontraron registros para los filtros seleccionados.
                </td>
              </tr>
            ) : (
              Array.isArray(history) && history.map((record) => (
                <tr key={record.id} className="hover:bg-slate-50/50 transition-colors">
                  <td className="px-6 py-4 text-sm font-medium text-slate-800">{record.fecha}</td>
                  <td className="px-6 py-4 font-bold text-slate-800">{record.empleado_nombre}</td>
                  <td className="px-6 py-4 text-sm text-slate-500">{record.dni}</td>
                  <td className="px-6 py-4 text-sm font-medium text-emerald-600">{record.hora_entrada}</td>
                  <td className="px-6 py-4 text-sm font-medium text-red-500">{record.hora_salida}</td>
                  <td className="px-6 py-4 text-sm font-bold text-slate-800">{record.horas_trabajadas}h</td>
                  <td className="px-6 py-4 text-right">
                    <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                      record.estado === 'A Tiempo' ? 'bg-emerald-100 text-emerald-700' :
                      record.estado === 'Tarde' ? 'bg-amber-100 text-amber-700' :
                      record.estado === 'Completo' ? 'bg-blue-100 text-blue-700' :
                      'bg-slate-100 text-slate-700'
                    }`}>
                      {record.estado}
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <SuccessModal 
        isOpen={showSuccessModal} 
        onClose={() => setShowSuccessModal(false)} 
        message={successMessage}
        title="Exportación Exitosa"
      />

      <style>{`
        .input-field {
          width: 100%;
          padding: 0.6rem 1rem;
          background-color: #f8fafc;
          border: 1px solid #e2e8f0;
          border-radius: 0.75rem;
          outline: none;
          transition: all 0.2s;
        }
        .input-field:focus {
          border-color: #4318FF;
          box-shadow: 0 0 0 3px rgba(67, 24, 255, 0.1);
          background-color: white;
        }
      `}</style>
    </div>
  );
}

export default Attendance;
