import { BrowserRouter, Route, Routes, Navigate } from "react-router-dom";
import { AuthProvider } from "@/contexts/AuthContext";
import { ToastProvider } from "@/components/ToastNotify";
import ProtectedRoute from "@/components/ProtectedRoute";
import Login from "@/pages/Login";
import Register from "@/pages/Register";
import DriverLogin from "@/pages/DriverLogin";
import Home from "@/pages/Home";
import DriverDetail from "@/pages/DriverDetail";
import Profile from "@/pages/Profile";
import Admin from "@/pages/Admin";
import DriverDashboard from "@/pages/DriverDashboard";
import DriverRegister from "@/pages/DriverRegister";
import NotFound from "@/pages/NotFound";

const App = () => (
  <BrowserRouter>
    <AuthProvider>
      <ToastProvider>
        <Routes>
          <Route path="/" element={<Navigate to="/login" replace />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/register-driver" element={<DriverRegister />} />
          <Route path="/driver/login" element={<DriverLogin />} />
          <Route path="/home" element={<ProtectedRoute allowedRoles={['student']}><Home /></ProtectedRoute>} />
          <Route path="/drivers/:id" element={<ProtectedRoute allowedRoles={['student']}><DriverDetail /></ProtectedRoute>} />
          <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
          <Route path="/admin" element={<ProtectedRoute allowedRoles={['admin']}><Admin /></ProtectedRoute>} />
          <Route path="/driver/dashboard" element={<ProtectedRoute allowedRoles={['driver']}><DriverDashboard /></ProtectedRoute>} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </ToastProvider>
    </AuthProvider>
  </BrowserRouter>
);

export default App;
