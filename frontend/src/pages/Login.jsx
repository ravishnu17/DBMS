import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import { addUpdateAPI } from '../auth/ApiService';
import logo from "../assets/images/logo.jpg";
import login_bg from "../assets/images/login_bg.jpg"
import { Loader, toast } from '../constant/utils';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';

// ✅ Define Yup validation schema
const schema = yup.object().shape({
  username: yup.string().email('Enter a valid email').required('Email is required'),
  password: yup.string().required('Password is required'),
});

const Login = () => {
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: yupResolver(schema),
  });

  const onSubmit = (data) => {
    setLoading(true);
    const fm = new FormData();
    fm.append('username', data.username);
    fm.append('password', data.password);

    addUpdateAPI('POST', '/user/login', fm, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
      .then((response) => {
        if (response.data?.status) {
          toast('Success', 'Login successful');
          sessionStorage.setItem('token', response.data.access_token);
          sessionStorage.setItem('userId', response.data.user_id);
          navigate('/dashboard');
        } else {
          toast('Error', 'Invalid credentials', 'error');
        }
      })
      .catch((error) => {
        toast('Error', 'Invalid credentials', 'error');
        console.error('Login error:', error);
      })
      .finally(() => {
        setLoading(false);
      });
  };

  return (
    <div className="d-flex justify-content-center align-items-center vh-100"
      style={{
        backgroundImage: `url(${login_bg})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
      }}
    >
      <div className="shadow-lg border overflow-hidden rounded w-50">
        <div className="row g-0" style={{ minHeight: "55vh" }}>
          <div className="col-md-6 text-white d-flex flex-column justify-content-center align-items-center p-4 login-content">
            <img src={logo} width={150} height={150} className="rounded" alt="Logo" />
            <h2>Welcome to DBMS!</h2>
            <p>Please log in to continue.</p>
          </div>

          <div className="col-md-6 bg-white p-4">
            <h4 className="mb-3 text-center fw-bold mt-4">Login</h4>
            <form onSubmit={handleSubmit(onSubmit)} noValidate>
              {/* Email Field */}
              <div className="mb-4">
                <label className="form-label fw-bold">Email</label>
                <input
                  type="email"
                  placeholder="Enter your email"
                  className={`form-control ${errors.username ? 'is-invalid' : ''}`}
                  {...register('username')}
                />
                {errors.username && (
                  <div className="invalid-feedback">{errors.username.message}</div>
                )}
              </div>

              {/* Password Field */}
              <div className="mb-5">
                <label className="form-label fw-bold">Password</label>
                <div className="input-group">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    placeholder="Enter your password"
                    autoComplete="off"
                    className={`form-control ${errors.password ? 'is-invalid' : ''} rounded`}
                    {...register('password')}
                  />
                  <span
                    className="input-group-text bg-transparent eye-icon"
                    onClick={() => setShowPassword(!showPassword)}
                    style={{ cursor: 'pointer' }}
                  >
                    <i className={`fa ${showPassword ? 'fa-eye-slash' : 'fa-eye'}`}></i>
                  </span>
                </div>
                {errors.password && (
                  <div className="invalid-feedback d-block">{errors.password.message}</div>
                )}
              </div>

              <div className="d-grid">
                <button type="submit" className="btn adminBtn fw-bold d-flex justify-content-center align-items-center gap-2">Login <Loader status={loading} color="#7c0b98ff" /></button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
