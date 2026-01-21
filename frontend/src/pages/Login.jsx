import React, { useState, useEffect } from 'react';
import { User, Lock, ArrowRight, QrCode, ArrowLeft, Shield, Clock, Eye, EyeOff } from 'lucide-react';
import axios from 'axios';

const API_URL = "http://localhost:8000/api";

function Login({ onLogin }) {
  const [view, setView] = useState('selection'); // 'selection', 'admin', 'employee'

  // Admin Login State
  const [dni, setDni] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [adminError, setAdminError] = useState('');
  const [adminLoading, setAdminLoading] = useState(false);

  // Employee Login State
  const [empDni, setEmpDni] = useState('');
  const [empCode, setEmpCode] = useState('');
  const [empError, setEmpError] = useState('');
  const [empLoading, setEmpLoading] = useState(false);
  const [qrImage, setQrImage] = useState('');
  const [timeLeft, setTimeLeft] = useState(0);
  const [empSuccess, setEmpSuccess] = useState('');

  // Fetch QR Code
  useEffect(() => {
    let interval;
    if (view === 'employee') {
      fetchQrCode();
      interval = setInterval(() => {
        setTimeLeft((prev) => {
          if (prev <= 1) {
            fetchQrCode();
            return 60;
          }
          return prev - 1;
        });
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [view]);

  const fetchQrCode = async () => {
    try {
      const response = await axios.get(`${API_URL}/auth/qr`);
      setQrImage(response.data.qr_image);
      setTimeLeft(response.data.seconds_left);
    } catch (error) {
      console.error("Error fetching QR:", error);
    }
  };

  const handleAdminLogin = async (e) => {
    e.preventDefault();
    setAdminError('');
    setAdminLoading(true);

    try {
      const response = await axios.post(`${API_URL}/auth/login`, {
        dni,
        password
      });
      localStorage.setItem('user', JSON.stringify(response.data));
      onLogin(response.data);
    } catch (err) {
      setAdminError(err.response?.data?.detail || 'Error al iniciar sesión');
    } finally {
      setAdminLoading(false);
    }
  };

  const handleEmployeeLogin = async (e) => {
    e.preventDefault();
    setEmpError('');
    setEmpSuccess('');
    setEmpLoading(true);

    try {
      const response = await axios.post(`${API_URL}/auth/login/employee`, {
        dni: empDni,
        code: empCode
      });
      
      if (response.data.access_token) {
        // Login exitoso, redirigir al dashboard
        localStorage.setItem('user', JSON.stringify(response.data.user));
        // TODO: Guardar token también si se implementa auth real
        onLogin(response.data.user);
      } else {
        // Fallback por si acaso
        setEmpSuccess(response.data.message || 'Fichaje realizado');
      }

    } catch (err) {
      setEmpError(err.response?.data?.detail || 'Error al iniciar sesión');
    } finally {
      setEmpLoading(false);
    }
  };

  const renderSelection = () => (
    <div className="flex flex-col items-center w-full max-w-2xl">
      <div className="text-center mb-10">
        <h1 className="text-3xl font-bold text-slate-800 mb-2">Fichaje Zaragonjg</h1>
        <p className="text-slate-500">Selecciona el tipo de acceso</p>
      </div>

      <div className="flex flex-col md:flex-row gap-6 w-full justify-center">
        <button
          onClick={() => setView('employee')}
          className="flex-1 bg-emerald-600 hover:bg-emerald-700 text-white p-8 rounded-2xl shadow-xl hover:-translate-y-1 transition-all duration-300 flex flex-col items-center gap-4 group"
        >
          <div className="bg-white/20 p-4 rounded-full group-hover:bg-white/30 transition-colors">
            <QrCode size={48} />
          </div>
          <div className="text-center">
            <h2 className="text-2xl font-bold mb-1">EMPLEADO</h2>
            <p className="text-emerald-100 text-sm">Fichar con código QR</p>
          </div>
        </button>

        <button
          onClick={() => setView('admin')}
          className="flex-1 bg-blue-600 hover:bg-blue-700 text-white p-8 rounded-2xl shadow-xl hover:-translate-y-1 transition-all duration-300 flex flex-col items-center gap-4 group"
        >
          <div className="bg-white/20 p-4 rounded-full group-hover:bg-white/30 transition-colors">
            <Shield size={48} />
          </div>
          <div className="text-center">
            <h2 className="text-2xl font-bold mb-1">ADMINISTRADOR</h2>
            <p className="text-blue-100 text-sm">Acceso con DNI y contraseña</p>
          </div>
        </button>
      </div>
      
      <p className="mt-12 text-xs text-slate-400 italic">Protección de datos según RGPD</p>
    </div>
  );

  const renderAdminLogin = () => (
    <div className="bg-white p-8 rounded-3xl shadow-xl w-full max-w-md border border-slate-100">
      <button 
        onClick={() => {
          setView('selection');
          setAdminError('');
          setDni('');
          setPassword('');
        }}
        className="flex items-center text-slate-400 hover:text-primary mb-6 transition-colors text-sm font-medium"
      >
        <ArrowLeft size={16} className="mr-1" /> Volver
      </button>

      <div className="text-center mb-8">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-blue-100 mb-4 text-blue-600">
          <Shield size={32} />
        </div>
        <h1 className="text-2xl font-bold text-slate-800">Administrador</h1>
        <p className="text-slate-500">Inicia sesión para gestionar</p>
      </div>

      <form onSubmit={handleAdminLogin} className="space-y-6">
        <div className="space-y-2">
          <label className="text-sm font-medium text-slate-700">DNI / NIE</label>
          <div className="relative">
            <User className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5" />
            <input
              type="text"
              value={dni}
              onChange={(e) => setDni(e.target.value.toUpperCase())}
              className="w-full pl-12 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all uppercase"
              placeholder="12345678A"
              required
            />
          </div>
        </div>

        <div className="space-y-2">
          <label className="text-sm font-medium text-slate-700">Contraseña</label>
          <div className="relative">
            <Lock className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5" />
            <input
              type={showPassword ? "text" : "password"}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full pl-12 pr-12 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
              placeholder="••••••••"
              required
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 hover:text-blue-600 transition-colors"
            >
              {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
            </button>
          </div>
        </div>

        {adminError && (
          <div className="p-3 bg-red-50 text-red-600 text-sm rounded-lg text-center font-medium animate-pulse">
            {adminError}
          </div>
        )}

        <button
          type="submit"
          disabled={adminLoading}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3.5 rounded-xl font-bold text-lg shadow-lg shadow-blue-600/30 hover:shadow-blue-600/50 transition-all flex items-center justify-center gap-2 disabled:opacity-70"
        >
          {adminLoading ? 'Entrando...' : 'Iniciar Sesión'}
          {!adminLoading && <ArrowRight size={20} />}
        </button>
      </form>
    </div>
  );

  const renderEmployeeLogin = () => (
    <div className="bg-white p-8 rounded-3xl shadow-xl w-full max-w-4xl border border-slate-100 flex flex-col md:flex-row gap-8">
      <div className="flex-1 border-r border-slate-100 pr-8 hidden md:block">
        <div className="text-center h-full flex flex-col justify-center items-center">
          <h3 className="text-lg font-bold text-slate-800 mb-4">Escanea con tu móvil</h3>
          
          <div className="p-4 bg-white border-2 border-slate-200 rounded-xl shadow-sm mb-4">
            {qrImage ? (
              <img src={qrImage} alt="QR Code" className="w-48 h-48 object-contain" />
            ) : (
              <div className="w-48 h-48 bg-slate-100 flex items-center justify-center text-slate-400 rounded-lg">
                Cargando...
              </div>
            )}
          </div>

          <div className="flex items-center gap-2 text-emerald-600 font-bold text-xl">
            <Clock size={24} />
            <span>{timeLeft} seg</span>
          </div>
        </div>
      </div>

      <div className="flex-1">
        <button 
          onClick={() => {
            setView('selection');
            setEmpError('');
            setEmpSuccess('');
            setEmpDni('');
            setEmpCode('');
          }}
          className="flex items-center text-slate-400 hover:text-emerald-600 mb-6 transition-colors text-sm font-medium"
        >
          <ArrowLeft size={16} className="mr-1" /> Volver
        </button>

        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-emerald-100 mb-4 text-emerald-600">
            <QrCode size={32} />
          </div>
          <h1 className="text-2xl font-bold text-slate-800">Fichaje</h1>
          <p className="text-slate-500">Introduce tus datos</p>
        </div>

        {/* Mobile QR (visible only on small screens) */}
        <div className="md:hidden text-center mb-6">
             <div className="p-4 bg-white border-2 border-slate-200 rounded-xl shadow-sm inline-block mb-2">
                {qrImage ? (
                  <img src={qrImage} alt="QR Code" className="w-32 h-32 object-contain" />
                ) : (
                  <div className="w-32 h-32 bg-slate-100 flex items-center justify-center text-slate-400 rounded-lg">
                    ...
                  </div>
                )}
              </div>
              <div className="flex items-center justify-center gap-2 text-emerald-600 font-bold">
                <Clock size={16} />
                <span>{timeLeft} seg</span>
              </div>
        </div>

        <form onSubmit={handleEmployeeLogin} className="space-y-6">
          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-700">DNI / NIE</label>
            <div className="relative">
              <User className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5" />
              <input
                type="text"
                value={empDni}
                onChange={(e) => setEmpDni(e.target.value.toUpperCase())}
                className="w-full pl-12 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 transition-all uppercase"
                placeholder="12345678A"
                required
              />
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-700">Código del QR</label>
            <div className="relative">
              <QrCode className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5" />
              <input
                type="text"
                value={empCode}
                onChange={(e) => setEmpCode(e.target.value.replace(/[^0-9]/g, '').slice(0, 6))}
                className="w-full pl-12 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 transition-all font-mono tracking-widest text-center text-lg"
                placeholder="000000"
                maxLength="6"
                required
              />
            </div>
          </div>

          {empError && (
            <div className="p-3 bg-red-50 text-red-600 text-sm rounded-lg text-center font-medium animate-pulse">
              {empError}
            </div>
          )}

          {empSuccess && (
            <div className="p-3 bg-emerald-50 text-emerald-600 text-sm rounded-lg text-center font-bold animate-bounce">
              {empSuccess}
            </div>
          )}

          <button
            type="submit"
            disabled={empLoading}
            className="w-full bg-emerald-600 hover:bg-emerald-700 text-white py-3.5 rounded-xl font-bold text-lg shadow-lg shadow-emerald-600/30 hover:shadow-emerald-600/50 transition-all flex items-center justify-center gap-2 disabled:opacity-70"
          >
            {empLoading ? 'Procesando...' : 'FICHAR'}
            {!empLoading && <ArrowRight size={20} />}
          </button>
        </form>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 p-4">
      {view === 'selection' && renderSelection()}
      {view === 'admin' && renderAdminLogin()}
      {view === 'employee' && renderEmployeeLogin()}
    </div>
  );
}

export default Login;
