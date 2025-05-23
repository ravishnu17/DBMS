import logoicon from '../assets/images/logo.jpg';

export const baseUrl = "http://localhost:8000";
// export const baseUrl = "http://172.105.54.28:8004";

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