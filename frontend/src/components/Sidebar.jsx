import React, { useContext, useEffect, useState } from 'react'
import { Link, useLocation } from 'react-router-dom';
import userProfile from '../assets/images/logo.jpg';

function Sidebar({ menu, openSideBar }) {
    const location = useLocation();
    const [openMenu, setOpenMenu] = useState([]);
    const [navState, setNavState] = useState({ module_name: location.pathname.split('/')[1] });
    //   const [sideMenus, setSideMenus] = useState([]);
    const [showProfile, setShowProfile] = useState(false);
    const currUser = {};


    const sideMenus = [
        { name: 'Dashboard', path: '/dashboard', icon: <i className="fa-solid fa-gauge fs-5" />, key: "dashboard" },
        { name: 'Service', path: '/service', icon: <i className="fa-solid fa-briefcase fs-5" />, key: "services" },
        { name: 'Event', path: '/event', icon: <i className="fa-solid fa-calendar fs-5" />, key: "events" },
        { name: 'Help', path: '/help', icon: <i className="fa-solid fa-circle-question fs-5" />, key: "helps" },
        { name: 'Users', path: '/users', icon: <i className="fa-solid fa-users fs-5" />, key: "users" },
    ];

    useEffect(() => {
        setNavState({ module_name: location.pathname.split('/')[1] });
    }, [location]);

    return (
        <>
            <aside className={`sidebar ${menu ? "open" : ""} pt-2 `} id="sidebar">
                <div className="d-flex justify-content-end">
                    <button className='btn ' onClick={openSideBar}>
                        {/* <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" className="bi bi-x-circle" viewBox="0 0 16 16">
            <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14m0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16" />
            <path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708" />
          </svg> */}
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" className="bi bi-x-lg" viewBox="0 0 16 16">
                            <path d="M2.146 2.854a.5.5 0 1 1 .708-.708L8 7.293l5.146-5.147a.5.5 0 0 1 .708.708L8.707 8l5.147 5.146a.5.5 0 0 1-.708.708L8 8.707l-5.146 5.147a.5.5 0 0 1-.708-.708L7.293 8z" />
                        </svg>
                    </button>
                </div>
                <div >
                    <div className='d-flex justify-content-center position-relative'>
                        <img src={userProfile} className="avatar_profile" alt="User" />
                        <span className="position-absolute adminEdit-icon" title='Edit Profile' data-bs-toggle="modal" data-bs-target="#profileModal" onClick={() => setShowProfile(pre => !pre)}>
                            <svg xmlns="http://www.w3.org/2000/svg" width={18} fill="white" className="bi bi-person-gear" viewBox="0 0 16 16">
                                <path d="M11 5a3 3 0 1 1-6 0 3 3 0 0 1 6 0M8 7a2 2 0 1 0 0-4 2 2 0 0 0 0 4m.256 7a4.5 4.5 0 0 1-.229-1.004H3c.001-.246.154-.986.832-1.664C4.484 10.68 5.711 10 8 10q.39 0 .74.025c.226-.341.496-.65.804-.918Q8.844 9.002 8 9c-5 0-6 3-6 4s1 1 1 1zm3.63-4.54c.18-.613 1.048-.613 1.229 0l.043.148a.64.64 0 0 0 .921.382l.136-.074c.561-.306 1.175.308.87.869l-.075.136a.64.64 0 0 0 .382.92l.149.045c.612.18.612 1.048 0 1.229l-.15.043a.64.64 0 0 0-.38.921l.074.136c.305.561-.309 1.175-.87.87l-.136-.075a.64.64 0 0 0-.92.382l-.045.149c-.18.612-1.048.612-1.229 0l-.043-.15a.64.64 0 0 0-.921-.38l-.136.074c-.561.305-1.175-.309-.87-.87l.075-.136a.64.64 0 0 0-.382-.92l-.148-.045c-.613-.18-.613-1.048 0-1.229l.148-.043a.64.64 0 0 0 .382-.921l-.074-.136c-.306-.561.308-1.175.869-.87l.136.075a.64.64 0 0 0 .92-.382zM14 12.5a1.5 1.5 0 1 0-3 0 1.5 1.5 0 0 0 3 0" />
                            </svg>
                        </span>
                    </div>

                    <div className='text-center mt-2 p-2'>
                        <p className='ms-2 fw-bold m-0' style={{ overflowWrap: 'anywhere', fontSize: 'larger' }}>{currUser?.name}</p>
                        <p className='ms-2 text-muted fw-bold m-0' style={{ overflowWrap: 'anywhere', fontSize: 'small' }}>{currUser?.role?.name}</p>
                    </div>

                </div>
                <nav className="sidebar-menu-content mt-2 p-2">
                    <ul className="nav flex-column">
                        {sideMenus?.map((item, index) => (
                            <li key={index} className={`nav-item nav-item-main my-1 ${[location.pathname.split('/')[1]?.toLowerCase(), navState?.module_name?.toLowerCase()].includes(item.path.split('/')[1]?.toLowerCase()) ? 'active' : ''}`}>
                                <Link to={item.path} className={`nav-link px-3 py-2 11 ${[location.pathname.split('/')[1]?.toLowerCase(), navState?.module_name?.toLowerCase()].includes(item.path.split('/')[1]?.toLowerCase()) ? "active nav-main-only" : ""}`}>
                                    <span className='me-3'>{item.icon}</span>{item.name}
                                </Link>
                            </li>
                        ))}
                    </ul>
                </nav>
            </aside>

            {/* profile modal */}
            <div className="modal fade " id="profileModal" backdrop="static" keyboard="false" tabIndex="-1" aria-labelledby="addModelLabel">
                <div className="modal-dialog modal-lg" role="document">
                    <div className="modal-content rounded-1">
                        <div className="modal-header">
                            <h6 className="modal-title fw-bold">User Profile</h6>
                            <button type="button" className="btn-close" data-bs-dismiss="modal" ></button>
                        </div>
                        <div className="modal-body">
                            {/* <UserProfile user={user} isOpen={showProfile} /> */}
                        </div>
                    </div>
                </div>
            </div>
        </>
    );

}

export default Sidebar