import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { addUpdateAPI } from '../auth/ApiService';
import Swal from 'sweetalert2';

const Login = () => {
  const { register, handleSubmit, formState: { errors } } = useForm();
  const [showPassword, setShowPassword] = useState(false);

  const onSubmit = (data) => {
    console.log(data);
    const fm= new FormData();
    fm.append('username', data.username);
    fm.append('password', data.password);
    addUpdateAPI('POST', '/user/login', fm, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
      .then((response) => {
        console.log('Login successful:', response.data);
        // Handle successful login (e.g., redirect to dashboard)
      })
      .catch((error) => {
        console.error('Login error:', error);
        // Handle login error (e.g., show error message)
      });
  };

  return (
    <div className="d-flex justify-content-center align-items-center vh-100"
      style={{
        backgroundImage: "url('https://source.unsplash.com/1600x900/?technology')",
        backgroundSize: 'cover',
        backgroundPosition: 'center',
      }}
    >
      <div className="card shadow-lg" style={{ width: '800px', borderRadius: '20px' }}>
        <div className="row g-0">
          <div className="col-md-6 bg-primary text-white d-flex flex-column justify-content-center p-4">
            <h2>Welcome!</h2>
            <p>Please log in to continue.</p>
          </div>

          <div className="col-md-6 bg-white p-4">
            <h4 className="mb-4 text-center">Login</h4>
            <form onSubmit={handleSubmit(onSubmit)} noValidate>
              {/* Username Field */}
              <div className="mb-3">
                <label className="form-label">Username</label>
                <input
                  type="text"
                  className={`form-control ${errors.username ? 'is-invalid' : ''}`}
                  {...register('username', { required: 'Username is required' })}
                />
                {errors.username && <div className="invalid-feedback">{errors.username.message}</div>}
              </div>

              {/* Password Field with Toggle */}
              <div className="mb-3">
                <label className="form-label">Password</label>
                <div className="input-group">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    className={`form-control ${errors.password ? 'is-invalid' : ''}`}
                    {...register('password', { required: 'Password is required' })}
                  />
                  <span className="input-group-text" style={{ cursor: 'pointer' }} onClick={() => setShowPassword(!showPassword)}>
                    <i className={`fa ${showPassword ? 'fa-eye-slash' : 'fa-eye'}`}></i>
                  </span>
                </div>
                {errors.password && <div className="invalid-feedback d-block">{errors.password.message}</div>}
              </div>

              <div className="d-grid">
                <button type="submit" className="btn btn-primary">Login</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
