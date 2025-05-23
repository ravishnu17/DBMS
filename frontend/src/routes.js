import React, { lazy } from 'react';

const DashBoard = lazy(() => import('./pages/DashBoard'));
const Service = lazy(() => import('./pages/Service'));
const Event = lazy(() => import('./pages/Event'));
const Help = lazy(() => import('./pages/Help'));
const Users = lazy(() => import('./pages/Users'));

export const routes = [
    { path: '/dashboard', element: DashBoard, label: 'Dashboard' },
    { path: '/service', element: Service, label: 'Service' },
    { path: '/event', element: Event, label: 'Event' },
    { path: '/help', element: Help, label: 'Help' },
    { path: '/users', element: Users, label: 'Users' },
];