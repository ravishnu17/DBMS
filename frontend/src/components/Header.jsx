import React, { useContext, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Swal from 'sweetalert2';
import { logo } from '../constant/utils';
// import { addUpdateAPI, getAPI } from '../constant/apiServices';


function Header({ openSideBar, menu }) {
    const currUser  = {};
    const navigate = useNavigate();


    const logout = () => {
        Swal.fire({
            title: "Are you sure want to logout?",
            icon: "warning",
            toast: true,
            showCancelButton: true,
            confirmButtonColor: "#d33",
            cancelButtonColor: "#3085d6",
            confirmButtonText: "Yes",
            cancelButtonText: "No",
        }).then((result) => {
            if (result.isConfirmed) {
                sessionStorage.clear();
                navigate('/login');
            }
        });
    };

    return (
        <div className='main-header'>
            <nav className="navbar px-2">
                <div className="d-flex align-items-center justify-content-between w-100 flex-nowrap">
                    {!menu ? (
                        <div onClick={openSideBar}>
                            <svg
                                className=''
                                xmlns="http://www.w3.org/2000/svg"
                                fill="white"
                                viewBox="0 0 448 512"
                                width={13}
                                role='button'
                            >
                                <path d="M0 96C0 78.3 14.3 64 32 64H416c17.7 0 32 14.3 32 32s-14.3 32-32 32H32C14.3 128 0 113.7 0 96zM0 256c0-17.7 14.3-32 32-32H416c17.7 0 32 14.3 32 32s-14.3 32-32 32H32c-17.7 0-32-14.3-32-32zM448 416c0 17.7-14.3 32-32 32H32c-17.7 0-32-14.3-32-32s14.3-32 32-32H416c17.7 0 32-14.3 32 32z" />
                            </svg>
                        </div>
                    ) : <div></div>}
                    <div className='gap-2'>
                        {logo(
                            "white",
                            currUser?.role_id === 1
                                ? "Data Management System"
                                : currUser?.province?.name || ""
                        )}
                    </div>
                    <div className='d-flex align-items-center gap-3'>
                        {/* Logout Button */}
                        <div className='p-1 px-2 bg-danger rounded' title='Logout' role='button' style={{ cursor: 'pointer' }} onClick={logout}>
                            <i className="fa-solid fa-right-from-bracket text-light" />
                            {/* <svg
                                title='Logout'
                                onClick={logout}
                                xmlns="http://www.w3.org/2000/svg"
                                viewBox="0 0 512 512"
                                width={25}
                                fill='white'
                                className='p-1'
                            >
                                <path d="M502.6 278.6c12.5-12.5 12.5-32.8 0-45.3l-128-128c-12.5-12.5-32.8-12.5 0 45.3L402.7 224 192 224c-17.7 0-32 14.3-32 32s14.3 32 32 32l210.7 0-73.4 73.4c-12.5 12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0l128-128zM160 96c17.7 0 32-14.3 32-32s-14.3-32-32-32L96 32C43 32 0 75 0 128L0 384c0 53 43 96 96 96l64 0c17.7 0 32-14.3 32-32s-14.3-32-32-32l-64 0c-17.7 0-32-14.3-32-32l0-256c0-17.7 14.3-32 32-32l64 0z" />
                            </svg> */}
                        </div>
                    </div>
                </div>
            </nav>
        </div>
    );
}

export default Header;