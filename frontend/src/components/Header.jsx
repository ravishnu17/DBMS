import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Swal from 'sweetalert2';
import defaultAvatar from '../assets/images/avatar.png'; // fallback avatar image
import { logo } from '../constant/utils';

function Header({ openSideBar, menu }) {
    const [currUser, setCurrUser] = useState({ name: 'John Doe', avatar: defaultAvatar });
    const navigate = useNavigate();

    const logout = () => {
        Swal.fire({
            title: "Are you sure you want to logout?",
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
                <div className="d-flex align-items-center justify-content-between w-100 flex-nowrap mt-1">
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
                        <h4 className='fw-bold text-light mt-0'>Don Bosco Migrant Service</h4>
                    </div>

                    <div className='d-flex align-items-center gap-2'>
                        {/* Logout Button */}
                        <div className='p-1 px-2 bg-danger rounded' title='Logout' role='button' style={{ cursor: 'pointer' }} onClick={logout}>
                            <i className="fa-solid fa-right-from-bracket text-light" />
                        </div>
                        {/* <div className=' border-start border-1 border-light' style={{ height: '30px' }}></div> */}
                        {/* User Profile Avatar */}
                        <img
                            src={currUser.avatar}
                            alt="User Avatar"
                            className="rounded-circle border"
                            width="35"
                            height="35"
                        />
                        <small className="text-light fw-bold">{currUser.name}</small>
                    </div>
                </div>
            </nav>
        </div>
    );
}

export default Header;