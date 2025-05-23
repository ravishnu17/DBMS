import Swal from 'sweetalert2';
import logoicon from '../assets/images/logo.jpg';

// export const baseUrl = "http://localhost:8000";
export const baseUrl = "http://172.105.54.28:8004";

export const logo = (color) => {
    return (
        <div className="navbar-brand text-center d-flex align-items-center justify-content-center" style={{ fontFamily: 'auto', fontSize: 'medium' }} >
            <img src={logoicon} alt="Logo" width="34" height="35" className="align-text-center" />
            <h6 className="fw-bold mb-0 mt-2" style={{ color: color }}>&nbsp;&nbsp; DBMS</h6>
        </div>
    )
}

export const profileName = (name) => {
    let splits = name?.toUpperCase()?.split(' ');
    if (splits?.length > 1) {
        return splits[0][0] + splits[1][0];
    } else if (name?.length > 1) {
        return splits[0][0] + splits[0][1];
    }
}

export const toast = (title, msg, icon = "success", position = 'top-end') => {
    let background = icon === "success" ? "#28a745" : "#dc3545";
    Swal.fire({
        toast: true,
        position: position,
        icon: icon,
        title: title,
        text: msg,
        showConfirmButton: false,
        timer: 2000,
        timerProgressBar: true,
        background: background,
        color: ' #fff'
    })
}

export const Loader = ({status}) => {
    return (
        status ?
            <div className="position-fixed top-0 start-0 w-100 h-100 d-flex justify-content-center align-items-center" style={{ zIndex: 1, background: '#0000002e' }}>
                <div className="text-center" style={{zIndex:999}}>
                    <div className="spinner-border" style={{ width: '2.5rem', height: '2.5rem', color: '#1e9229' }} role="status">
                        <span className="visually-hidden">Loading...</span>
                    </div>
                    <div className="mt-3 fw-bold text-success">Please wait...</div>
                </div>
            </div>
            :
            <div></div>
    );
};