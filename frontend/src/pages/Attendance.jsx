import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Calendar as CalendarIcon, Download, Filter } from 'lucide-react';

const API_URL = "http://localhost:8000/api";

function Attendance() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [startDate, setStartDate] = useState(new Date().toISOString().split('T')[0]);
  const [endDate, setEndDate] = useState(new Date().toISOString().split('T')[0]);
  const [employees, setEmployees] = useState([]);
  const [selectedEmployee, setSelectedEmployee] = useState('');

  useEffect(() => {
    fetchEmployees();
    fetchHistory();
  }, []);

  const fetchEmployees = async () => {
    try {
      const res = await axios.get(`${API_URL}/employees`);
      setEmployees(res.data);
    } catch (error) {
      console.error(error);
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
      setHistory(res.data);
    } catch (error) {
      console.error("Error fetching history:", error);
    } finally {
      setLoading(false);
    }
  };

  const exportToCSV = () => {
      const csvContent = "data:text/csv;charset=utf-8," 
          + "Fecha,Empleado,DNI,Entrada,Salida,Horas,Estado\n"
          + history.map(row => `${row.fecha},${row.empleado_nombre},${row.dni},${row.hora_entrada},${row.hora_salida},${row.horas_trabajadas},${row.estado}`).join("\n");
      
      const encodedUri = encodeURI(csvContent);
      const link = document.createElement("a");
      link.setAttribute("href", encodedUri);
      link.setAttribute("download", `historial_fichajes_${startDate}_${endDate}.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
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
            {employees.map(emp => (
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
        <button 
          onClick={exportToCSV}
          className="bg-white border border-slate-200 text-slate-600 hover:bg-slate-50 px-4 py-2.5 rounded-xl font-bold transition-all flex items-center gap-2"
        >
          <Download size={18} /> Exportar
        </button>
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
            {history.length === 0 ? (
              <tr>
                <td colSpan="7" className="px-6 py-8 text-center text-slate-400">
                  No se encontraron registros para los filtros seleccionados.
                </td>
              </tr>
            ) : (
              history.map((record) => (
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
