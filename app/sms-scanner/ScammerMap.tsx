'use client';

import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { phantomFetch } from '../lib/fetch';

export default function ScammerMap() {
    const [points, setPoints] = useState<any[]>([]);

    useEffect(() => {
        phantomFetch('/api/analytics/admin/geospatial-map', { ttl: 120000 })
            .then(res => res.json())
            .then(data => setPoints(data))
            .catch(err => console.error("Map fetch error:", err));
    }, []);

    return (
        <MapContainer
            center={[20.5937, 78.9629]} // Center of India
            zoom={4}
            style={{ height: '100%', width: '100%' }}
        >
            <TileLayer
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            />
            {points.map((p, idx) => (
                <CircleMarker
                    key={idx}
                    center={[p.lat, p.lng]}
                    radius={5 + (p.threat_count * 2)}
                    fillColor="#dc2626"
                    color="#991b1b"
                    weight={1}
                    fillOpacity={0.6}
                >
                    <Popup>
                        <div className="font-sans">
                            <p className="font-bold">Caller: {p.caller_id}</p>
                            <p className="text-sm">Threats: {p.threat_count}</p>
                            <p className="text-xs text-slate-500">Location: {p.city}</p>
                        </div>
                    </Popup>
                </CircleMarker>
            ))}
        </MapContainer>
    );
}