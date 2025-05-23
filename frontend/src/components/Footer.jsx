import React from 'react';

function Footer({menu}) {
  
  return (
    <div className={`p-1 d-flex justify-content-center align-items-center footer ${menu ? "open" : ""}`}>
      <p className='text-light mb-0 footer-text'>© {new Date().getFullYear()} All rights reserved. Developed by <a href="https://boscosofttech.com/" className='text-light fw-bold' target="_blank" rel="noopener noreferrer">Bocosoft Technologies</a></p>
    </div>
  )
}

export default Footer