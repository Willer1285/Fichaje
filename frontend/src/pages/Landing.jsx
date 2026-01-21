import React from 'react';
import { useNavigate } from 'react-router-dom';
import { UserCog, Users } from 'lucide-react';

function Landing() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-sidebar flex items-center justify-center p-4">
      <div className="w-full max-w-4xl grid md:grid-cols-2 gap-8">
        {/* Admin Card */}
        <div 
          onClick={() => navigate('/login')}
          className="bg-white/10 backdrop-blur-lg border border-white/10 p-8 rounded-3xl cursor-pointer hover:bg-white/20 transition-all hover:-translate-y-2 group"
        >
          <div className="bg-primary p-4 rounded-2xl w-fit mb-6 group-hover:scale-110 transition-transform">
            <UserCog size={48} className="text-white" />
          </div>
          <h2 className="text-3xl font-bold text-white mb-2">Administrador</h2>
          <p className="text-slate-300">
            Acceso al panel de control para gestión de personal, reportes y configuración.
          </p>
        </div>

        {/* Employee Card */}
        <div 
          onClick={() => navigate('/scan')}
          className="bg-white/10 backdrop-blur-lg border border-white/10 p-8 rounded-3xl cursor-pointer hover:bg-white/20 transition-all hover:-translate-y-2 group"
        >
          <div className="bg-emerald-500 p-4 rounded-2xl w-fit mb-6 group-hover:scale-110 transition-transform">
            <Users size={48} className="text-white" />
          </div>
          <h2 className="text-3xl font-bold text-white mb-2">Empleado</h2>
          <p className="text-slate-300">
            Registrar entrada o salida escaneando el código QR.
          </p>
        </div>
      </div>
    </div>
  );
}

export default Landing;
