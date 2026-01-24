import React, { useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight, Calendar as CalendarIcon, Clock, User, X } from 'lucide-react';
import axios from 'axios';

const API_URL = "/api";

function CalendarPage() {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedDay, setSelectedDay] = useState(null);
  const [dayEvents, setDayEvents] = useState([]);

  useEffect(() => {
    fetchEvents();
  }, [currentDate]);

  const fetchEvents = async () => {
    setLoading(true);
    try {
      // Calcular primer y último día del mes visible (incluyendo días de relleno)
      const year = currentDate.getFullYear();
      const month = currentDate.getMonth();

      const firstDayOfMonth = new Date(year, month, 1);
      const lastDayOfMonth = new Date(year, month + 1, 0);

      // Ajustar al lunes anterior si es necesario para llenar la grilla
      const start = new Date(firstDayOfMonth);
      start.setDate(start.getDate() - (start.getDay() === 0 ? 6 : start.getDay() - 1));

      // Ajustar al domingo posterior
      const end = new Date(lastDayOfMonth);
      end.setDate(end.getDate() + (7 - end.getDay()));

      const startStr = start.toISOString().split('T')[0];
      const endStr = end.toISOString().split('T')[0];

      console.log(`📅 [Calendar] Solicitando eventos: ${startStr} a ${endStr}`);

      const res = await axios.get(`${API_URL}/calendar/events`, {
        params: {
          start: startStr,
          end: endStr
        }
      });

      console.log(`✅ [Calendar] Respuesta recibida:`, res.data);
      console.log(`   Total eventos: ${res.data ? res.data.length : 0}`);
      if (res.data && res.data.length > 0) {
        console.log(`   Primer evento:`, res.data[0]);
      }

      setEvents(Array.isArray(res.data) ? res.data : []);
    } catch (err) {
      console.error("❌ [Calendar] Error fetching events:", err);
    } finally {
      setLoading(false);
    }
  };

  const getDaysInMonth = () => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const days = [];

    // Relleno previo
    const startPadding = firstDay.getDay() === 0 ? 6 : firstDay.getDay() - 1;
    for (let i = startPadding; i > 0; i--) {
      const d = new Date(year, month, 1 - i);
      days.push({ date: d, isCurrentMonth: false });
    }

    // Días del mes
    for (let i = 1; i <= lastDay.getDate(); i++) {
      days.push({ date: new Date(year, month, i), isCurrentMonth: true });
    }

    // Relleno posterior (para completar 42 celdas = 6 filas * 7 días)
    const remainingCells = 42 - days.length;
    for (let i = 1; i <= remainingCells; i++) {
      const d = new Date(year, month + 1, i);
      days.push({ date: d, isCurrentMonth: false });
    }

    return days;
  };

  const nextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1));
  };

  const prevMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1));
  };

  const handleDayClick = (day) => {
    const dayStr = day.date.toISOString().split('T')[0];
    const eventsForDay = Array.isArray(events)
      ? events.filter(e => e.start.startsWith(dayStr))
      : [];
    setSelectedDay(day.date);
    setDayEvents(eventsForDay);
  };

  // Helper para obtener eventos de un día específico para renderizar los dots
  const getEventsForRender = (date) => {
      const dateStr = date.toISOString().split('T')[0];
      return Array.isArray(events)
        ? events.filter(e => e.start.startsWith(dateStr))
        : [];
  };

  const getShortName = (fullName) => {
      if (!fullName) return '';
      const parts = fullName.split(' ');
      return parts[0]; 
  };

  const getStatusText = (evt) => {
      const props = evt.extendedProps || {};
      if (props.type === 'attendance') return props.late ? 'Tarde' : 'OK';
      
      if (props.type === 'vacation' || props.type === 'absence') {
          const estado = props.estado || '';
          if (estado === 'aprobada' || estado === 'justificada') return 'Aprobado';
          if (estado === 'rechazada') return 'Rechazado';
          if (estado === 'pendiente' || estado === 'pendiente_justificar' || estado === 'notificada') return 'Pendiente';
          return estado.replace(/_/g, ' ').substring(0, 8); // Fallback truncado
      }
      return '';
  };

  return (
    <div className="p-8 flex flex-col min-h-full">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div className="flex items-center gap-4">
          <div className="bg-white p-3 rounded-xl shadow-sm border border-slate-100 text-primary">
            <CalendarIcon size={24} />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-800 capitalize">
              {currentDate.toLocaleDateString('es-ES', { month: 'long', year: 'numeric' })}
            </h1>
            <p className="text-slate-500 text-sm">Vista general de actividad</p>
          </div>
        </div>
        <div className="flex gap-2 bg-white p-1 rounded-xl border border-slate-200 shadow-sm">
          <button onClick={prevMonth} className="p-2 hover:bg-slate-50 rounded-lg text-slate-600 transition-colors">
            <ChevronLeft size={20} />
          </button>
          <button onClick={() => setCurrentDate(new Date())} className="px-4 py-2 text-sm font-bold text-slate-600 hover:bg-slate-50 rounded-lg transition-colors">
            Hoy
          </button>
          <button onClick={nextMonth} className="p-2 hover:bg-slate-50 rounded-lg text-slate-600 transition-colors">
            <ChevronRight size={20} />
          </button>
        </div>
      </div>

      {/* Calendar Grid */}
      <div className="bg-white rounded-[2rem] shadow-sm border border-slate-100 flex flex-col">
        {/* Days Header */}
        <div className="grid grid-cols-7 border-b border-slate-100 bg-slate-50/50 rounded-t-[2rem]">
          {['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'].map(day => (
            <div key={day} className="py-4 text-center text-sm font-bold text-slate-400 uppercase tracking-wider">
              {day}
            </div>
          ))}
        </div>

        {/* Days Grid */}
        <div className="grid grid-cols-7 auto-rows-fr">
          {getDaysInMonth().map((day, idx) => {
            const dayEventsList = getEventsForRender(day.date);
            const isToday = day.date.toDateString() === new Date().toDateString();
            
            return (
              <div 
                key={idx} 
                onClick={() => handleDayClick(day)}
                className={`border-b border-r border-slate-100 p-2 min-h-[140px] relative hover:bg-slate-50 transition-colors cursor-pointer group flex flex-col items-center justify-start gap-1 ${
                  !day.isCurrentMonth ? 'bg-slate-50/30 text-slate-300' : 'text-slate-700'
                } ${idx >= 35 ? 'border-b-0' : ''} ${idx % 7 === 6 ? 'border-r-0' : ''} ${idx >= 35 && idx % 7 === 0 ? 'rounded-bl-[2rem]' : ''} ${idx >= 35 && idx % 7 === 6 ? 'rounded-br-[2rem]' : ''}`}
              >
                <span className={`w-8 h-8 flex items-center justify-center rounded-full text-sm font-bold mb-1 ${
                  isToday ? 'bg-primary text-white shadow-md shadow-primary/30' : ''
                }`}>
                  {day.date.getDate()}
                </span>
                
                {/* Event List */}
                <div className="flex flex-col gap-1 w-full px-1 mt-1 overflow-hidden">
                    {dayEventsList.slice(0, 3).map((evt, i) => (
                        <div 
                            key={i} 
                            className="text-[10px] px-1.5 py-0.5 rounded truncate font-bold flex justify-between items-center gap-1 shadow-sm"
                            style={{ 
                                backgroundColor: evt.backgroundColor ? `${evt.backgroundColor}15` : '#f1f5f9', // Muy suave
                                color: evt.backgroundColor || '#64748b',
                                borderLeft: `3px solid ${evt.backgroundColor || '#cbd5e1'}`
                            }}
                            title={`${evt.title} - ${getStatusText(evt)}`}
                        >
                            <span className="truncate font-semibold">{getShortName(evt.extendedProps?.employee)}</span>
                            <span className="text-[9px] opacity-90 shrink-0">{getStatusText(evt)}</span>
                        </div>
                    ))}
                    {dayEventsList.length > 3 && (
                        <div className="text-[10px] text-slate-400 font-bold px-1 text-center">
                            +{dayEventsList.length - 3} más
                        </div>
                    )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Modal Detalles Día */}
      {selectedDay && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl shadow-2xl w-full max-w-md p-6 animate-in zoom-in-95 flex flex-col max-h-[80vh]">
            <div className="flex justify-between items-center mb-6 pb-4 border-b border-slate-100">
              <h3 className="text-xl font-bold text-slate-800 capitalize">
                {selectedDay.toLocaleDateString('es-ES', { weekday: 'long', day: 'numeric', month: 'long' })}
              </h3>
              <button onClick={() => setSelectedDay(null)} className="p-2 hover:bg-slate-100 rounded-full text-slate-400">
                <X size={20} />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto pr-2 space-y-3">
              {dayEvents.length === 0 ? (
                <div className="text-center py-10 text-slate-400">
                  <p>No hay actividad registrada</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {/* Agrupar eventos por tipo */}
                  {(() => {
                    const safeEvents = Array.isArray(dayEvents) ? dayEvents : [];
                    const attendances = safeEvents.filter(e => e.extendedProps?.type === 'attendance');
                    const vacations = safeEvents.filter(e => e.extendedProps?.type === 'vacation');
                    const absences = safeEvents.filter(e => e.extendedProps?.type === 'absence');

                    return (
                      <>
                        {/* Fichajes/Asistencias */}
                        {attendances.length > 0 && (
                          <div className="space-y-2">
                            <h5 className="text-xs font-bold text-slate-500 uppercase tracking-wider px-2">
                              Fichajes del Día ({attendances.length})
                            </h5>
                            {attendances.map(evt => (
                              <div
                                key={evt.id}
                                className="p-4 rounded-xl border-l-4 bg-slate-50 hover:bg-white hover:shadow-md transition-all"
                                style={{ borderLeftColor: evt.backgroundColor }}
                              >
                                <div className="flex justify-between items-start mb-2">
                                  <h4 className="font-bold text-slate-800 text-sm">{evt.extendedProps.employee}</h4>
                                  {evt.extendedProps.late && (
                                    <span className="bg-amber-100 text-amber-700 px-2 py-0.5 rounded text-xs font-bold">
                                      Tarde
                                    </span>
                                  )}
                                </div>
                                <div className="space-y-1 text-xs text-slate-600">
                                  <div className="flex items-center gap-2">
                                    <Clock size={12} className="text-slate-400" />
                                    <span className="font-medium">Entrada:</span>
                                    <span className="font-bold">{evt.extendedProps.checkIn}</span>
                                  </div>
                                  <div className="flex items-center gap-2">
                                    <User size={12} className="text-slate-400" />
                                    <span className="font-medium">Estado:</span>
                                    <span className={`font-bold ${evt.extendedProps.late ? 'text-amber-600' : 'text-emerald-600'}`}>
                                      {evt.extendedProps.late ? 'Llegó tarde' : 'A tiempo'}
                                    </span>
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                        )}

                        {/* Vacaciones */}
                        {vacations.length > 0 && (
                          <div className="space-y-2">
                            <h5 className="text-xs font-bold text-slate-500 uppercase tracking-wider px-2">
                              Vacaciones ({vacations.length})
                            </h5>
                            {vacations.map(evt => (
                              <div
                                key={evt.id}
                                className="p-4 rounded-xl border-l-4 bg-blue-50 hover:bg-blue-100 hover:shadow-md transition-all border-blue-500"
                              >
                                <div className="flex justify-between items-start mb-1">
                                    <h4 className="font-bold text-slate-800 text-sm">
                                    {evt.extendedProps.employee}
                                    </h4>
                                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider border ${
                                        evt.extendedProps.estado === 'aprobada' ? 'bg-green-100 text-green-700 border-green-200' :
                                        evt.extendedProps.estado === 'rechazada' ? 'bg-red-100 text-red-700 border-red-200' :
                                        'bg-amber-100 text-amber-700 border-amber-200'
                                    }`}>
                                        {evt.extendedProps.estado?.replace(/_/g, ' ')}
                                    </span>
                                </div>
                                <div className="flex items-center gap-2 text-xs">
                                  <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded font-bold">
                                    De Vacaciones
                                  </span>
                                </div>
                              </div>
                            ))}
                          </div>
                        )}

                        {/* Ausencias */}
                        {absences.length > 0 && (
                          <div className="space-y-2">
                            <h5 className="text-xs font-bold text-slate-500 uppercase tracking-wider px-2">
                              Ausencias ({absences.length})
                            </h5>
                            {absences.map(evt => (
                              <div
                                key={evt.id}
                                className="p-4 rounded-xl border-l-4 bg-red-50 hover:bg-red-100 hover:shadow-md transition-all border-red-500"
                              >
                                <div className="flex justify-between items-start mb-2">
                                    <h4 className="font-bold text-slate-800 text-sm">
                                    {evt.extendedProps.employee}
                                    </h4>
                                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider border ${
                                        ['aprobada', 'justificada'].includes(evt.extendedProps.estado) ? 'bg-green-100 text-green-700 border-green-200' :
                                        evt.extendedProps.estado === 'rechazada' ? 'bg-red-100 text-red-700 border-red-200' :
                                        'bg-amber-100 text-amber-700 border-amber-200'
                                    }`}>
                                        {evt.extendedProps.estado?.replace(/_/g, ' ')}
                                    </span>
                                </div>
                                <div className="space-y-1 text-xs">
                                  <div className="flex items-center gap-2">
                                    <span className="font-medium text-slate-600">Tipo:</span>
                                    <span className="bg-red-100 text-red-700 px-2 py-0.5 rounded font-bold capitalize">
                                      {evt.extendedProps.reason?.replace(/_/g, ' ')}
                                    </span>
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                        )}

                        {/* Resumen */}
                        <div className="mt-4 pt-4 border-t border-slate-200">
                          <div className="grid grid-cols-3 gap-4 text-center">
                            <div className="bg-emerald-50 p-3 rounded-xl">
                              <p className="text-2xl font-bold text-emerald-600">{attendances.length}</p>
                              <p className="text-xs text-slate-500 font-medium">Fichajes</p>
                            </div>
                            <div className="bg-blue-50 p-3 rounded-xl">
                              <p className="text-2xl font-bold text-blue-600">{vacations.length}</p>
                              <p className="text-xs text-slate-500 font-medium">Vacaciones</p>
                            </div>
                            <div className="bg-red-50 p-3 rounded-xl">
                              <p className="text-2xl font-bold text-red-600">{absences.length}</p>
                              <p className="text-xs text-slate-500 font-medium">Ausencias</p>
                            </div>
                          </div>
                          <div className="mt-3 text-center">
                            <p className="text-xs text-slate-400">
                              {attendances.filter(e => e.extendedProps.late).length > 0 && (
                                <span className="text-amber-600 font-bold">
                                  {attendances.filter(e => e.extendedProps.late).length} llegada(s) tarde
                                </span>
                              )}
                            </p>
                          </div>
                        </div>
                      </>
                    );
                  })()}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default CalendarPage;
