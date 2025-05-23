import React, { Suspense } from 'react';
import { HashRouter, Navigate, Route, Routes } from 'react-router-dom';

import Login from './pages/Login';
import DefaultLayout from './layouts/DefaultLayout';
import './App.css';
// import DefaultLayout from './layouts/DefaultLayout';

function App() {
  return (
    <div className="App">
      <Suspense fallback={<div>Loading...</div>}>
       <HashRouter>
        <Routes>
          <Route path='/' element={<Navigate to='/login' />} />
          <Route path='/login' element={<Login />} />
          <Route path='*' element={<DefaultLayout />} />
        </Routes>
      </HashRouter>
      </Suspense>
      
    </div>
  );
}

export default App;
