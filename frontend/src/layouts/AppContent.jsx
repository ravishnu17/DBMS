import React, { Suspense, useEffect, useContext } from 'react';
import { routes } from '../routes';
import { Navigate, Route, Routes, useLocation } from 'react-router-dom';

function AppContent() {
    const location = useLocation();
    // const [transitionClass, setTransitionClass] = useState('page-content');
    // const context = useContext(playlistData)

    return (
        <Suspense>
            <Routes>
                {routes.map((route, index) => (
                    route.element &&
                    <Route
                        key={index}
                        path={route.path}
                        element={<route.element />}
                    />
                ))}
                <Route path='*' element={<Navigate to='/dashboard' />} />
            </Routes>
        </Suspense>
    )
}

export default AppContent