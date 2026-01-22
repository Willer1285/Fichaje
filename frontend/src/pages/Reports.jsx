import React, { useState, useEffect } from 'react';
import { FileText, Download, Filter, Calendar } from 'lucide-react';
import axios from 'axios';

const API_URL = "/api";

function Reports() {
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Form State
  const [reportType, setReportType] = useState('individual');
  const [selectedEmployee, setSelectedEmployee] = useState('');
  const [periodType, setPeriodType] = useState('month');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [format, setFormat] = useState('pdf');

  useEffect(() => {
    fetchEmployees();
    calculateDates('month');
  }, []);

  const fetchEmployees = async () => {
    try {
      const res = await axios.get(`${API_URL}/employees`);
      setEmployees(res.data);
      if (res.data.length > 0) setSelectedEmployee(res.data[0].id);
    } catch (err) {
      console.error("Error loading employees", err);
    }
  };

  const calculateDates = (period) => {
    const end = new Date();
    let start = new Date();

    if (period === 'week') {
      start.setDate(end.getDate() - 7);
    } else if (period === 'month') {
      start.setMonth(end.getMonth() - 1);
    } else if (period === 'trimester') {
      start.setMonth(end.getMonth() - 3);
    }
    
    // Format YYYY-MM-DD
    setEndDate(end.toISOString().split('T')[0]);
    if (period !== 'custom') {
      setStartDate(start.toISOString().split('T')[0]);
    }
  };

  const handlePeriodChange = (e) => {
    const period = e.target.value;
    setPeriodType(period);
    if (period !== 'custom') {
      calculateDates(period);
    }
  };

  const generateReport = async (e) => {
    e.preventDefault();
    setGenerating(true);
    setError('');
    setSuccess('');

    try {
      const payload = {
        type: reportType,
        employee_id: reportType === 'individual' ? parseInt(selectedEmployee) : null,
        start_date: startDate,
        end_date: endDate,
        format: format
      };

      const response = await axios.post(`${API_URL}/reports/generate`, payload, {
        responseType: 'blob' // Important for file download
      });

      const ext = format === 'pdf' ? 'pdf' : 'xlsx';
      const filename = `reporte_${startDate}_${endDate}.${ext}`;
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
                    setSuccess(`Informe generado y guardado exitosamente en: ${res.path}`);
                } else {
                    setError("Error guardando archivo: " + res.error);
                }
            } catch (e) {
                setError("Error comunicando con la aplicación de escritorio: " + e);
            }
        } else {
            // Fallback web browser
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', filename);
            document.body.appendChild(link);
            link.click();
            link.remove();
            window.URL.revokeObjectURL(url);
            
            setSuccess("Informe generado y descargado correctamente");
        }
        setGenerating(false);
      };

    } catch (err) {
      console.error(err);
      setError("Error al generar el informe. Verifique los datos.");
      setGenerating(false);
    } 
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="flex items-center gap-3 mb-8">
        <div className="bg-blue-100 p-3 rounded-xl text-blue-600">
          <FileText size={24} />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Generar Informes</h1>
          <p className="text-slate-500 text-sm">Exportación de datos para inspección</p>
        </div>
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-8">
        <form onSubmit={generateReport} className="space-y-6">
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Tipo de Informe */}
            <div className="space-y-2">
              <label className="text-sm font-bold text-slate-700">Tipo de Informe</label>
              <div className="grid grid-cols-2 gap-2 bg-slate-50 p-1 rounded-lg border border-slate-200">
                <button
                  type="button"
                  onClick={() => setReportType('individual')}
                  className={`py-2 px-4 rounded-md text-sm font-medium transition-all ${
                    reportType === 'individual' ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-500 hover:text-slate-700'
                  }`}
                >
                  Individual
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setReportType('todos');
                    setFormat('excel'); // Force excel for bulk
                  }}
                  className={`py-2 px-4 rounded-md text-sm font-medium transition-all ${
                    reportType === 'todos' ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-500 hover:text-slate-700'
                  }`}
                >
                  Todos (Excel)
                </button>
              </div>
            </div>

            {/* Empleado (si es individual) */}
            <div className="space-y-2">
              <label className="text-sm font-bold text-slate-700">Empleado</label>
              <select
                disabled={reportType === 'todos'}
                value={selectedEmployee}
                onChange={(e) => setSelectedEmployee(e.target.value)}
                className="w-full p-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 disabled:opacity-50"
              >
                {Array.isArray(employees) && employees.map(emp => (
                  <option key={emp.id} value={emp.id}>
                    {emp.apellidos}, {emp.nombre} - {emp.dni}
                  </option>
                ))}
              </select>
            </div>

            {/* Periodo */}
            <div className="space-y-2">
              <label className="text-sm font-bold text-slate-700">Periodo</label>
              <select
                value={periodType}
                onChange={handlePeriodChange}
                className="w-full p-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
              >
                <option value="week">Última Semana</option>
                <option value="month">Último Mes</option>
                <option value="trimester">Último Trimestre</option>
                <option value="custom">Personalizado</option>
              </select>
            </div>

            {/* Formato */}
            <div className="space-y-2">
              <label className="text-sm font-bold text-slate-700">Formato</label>
              <select
                value={format}
                onChange={(e) => setFormat(e.target.value)}
                disabled={reportType === 'todos'} // Todos solo Excel
                className="w-full p-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 disabled:opacity-50"
              >
                <option value="pdf">PDF (Oficial)</option>
                <option value="excel">Excel (Datos)</option>
              </select>
            </div>

            {/* Fechas Personalizadas */}
            <div className="md:col-span-2 grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-bold text-slate-700">Desde</label>
                <div className="relative">
                  <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 w-4 h-4" />
                  <input
                    type="date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    disabled={periodType !== 'custom'}
                    className="w-full pl-10 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 disabled:opacity-70"
                  />
                </div>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-bold text-slate-700">Hasta</label>
                <div className="relative">
                  <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 w-4 h-4" />
                  <input
                    type="date"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    disabled={periodType !== 'custom'}
                    className="w-full pl-10 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 disabled:opacity-70"
                  />
                </div>
              </div>
            </div>
          </div>

          {error && (
            <div className="p-4 bg-red-50 text-red-700 rounded-xl text-sm font-medium">
              {error}
            </div>
          )}

          {success && (
            <div className="p-4 bg-emerald-50 text-emerald-700 rounded-xl text-sm font-medium">
              {success}
            </div>
          )}

          <div className="pt-4 border-t border-slate-100 flex justify-end">
            <button
              type="submit"
              disabled={generating}
              className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-xl font-bold shadow-lg shadow-blue-600/30 transition-all disabled:opacity-70"
            >
              {generating ? 'Generando...' : 'Generar Informe'}
              {!generating && <Download size={20} />}
            </button>
          </div>

        </form>
      </div>

      <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-blue-50 p-6 rounded-2xl border border-blue-100">
          <h3 className="font-bold text-blue-800 mb-2">Información Legal</h3>
          <p className="text-sm text-blue-600">
            Los informes generados cumplen con el Real Decreto-ley 8/2019. 
            Deben ser conservados durante 4 años y estar a disposición de los trabajadores, sus representantes y la Inspección de Trabajo.
          </p>
        </div>
        <div className="bg-slate-50 p-6 rounded-2xl border border-slate-200">
          <h3 className="font-bold text-slate-800 mb-2">Ayuda</h3>
          <p className="text-sm text-slate-600">
            Utilice el formato PDF para presentar documentos oficiales firmados. 
            El formato Excel es útil para realizar cálculos adicionales o integraciones con otros sistemas.
          </p>
        </div>
      </div>
    </div>
  );
}

export default Reports;
