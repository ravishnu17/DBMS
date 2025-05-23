import React, { useContext, useEffect, useState } from 'react'
import Swal from 'sweetalert2';

import Header from '../components/Header';
import Footer from '../components/Footer';
import Sidebar from '../components/Sidebar';
import AppContent from './AppContent';
// import AppContent from './AppContent';

function DefaultLayout() {

    // const { setCurrUser, setPermissions } = useContext(ContextProvider);
    const [menu, setMenu] = useState(true); // enable sidebar
    const userId = localStorage.getItem("userId");
    const user_id = sessionStorage.getItem("userId")



    // const getCurrentuser = () => {
    //     getAPI('/access/current-user').then((res) => {
    //         if (res?.data.status) {
    //             setPermissions(res?.data?.permissions);
    //             setCurrUser(res?.data?.data)
    //         } else {
    //             unknownUser();
    //         }
    //     }).catch((err) => {
    //         unknownUser();
    //         console.log(err);
    //     })
    // }

    // useEffect(() => {
    //     getCurrentuser();
    // }, []);

    return (
        <div className='min-vh-100'>
            <Sidebar menu={menu} openSideBar={() => { setMenu(!menu) }} />
            <div className={` admin-content ${menu ? "open" : ""}`}>
                <Header openSideBar={() => { setMenu(!menu) }} menu={menu} />
                <AppContent />
                <Footer menu={menu} />
            </div>
        </div>
    )
}

export default DefaultLayout