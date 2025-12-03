// Web stub for react-native-maps
import React from 'react';

// Create mock components that don't crash
const MockView = (props) => React.createElement('div', { ...props, style: { display: 'none' } });

export const MapView = MockView;
export const Marker = MockView;
export const Circle = MockView;
export const Polyline = MockView;
export const Polygon = MockView;
export const PROVIDER_DEFAULT = 'default';
export const PROVIDER_GOOGLE = 'google';

export default MapView;