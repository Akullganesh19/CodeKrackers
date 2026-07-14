'use client';

import React, { useEffect, useState } from 'react';
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line
} from 'recharts';
import dynamic from 'next/dynamic';
import { phantomFetch } from '@/app/lib/fetch'

// Dynamically import Map to avoid SSR issues with Leaflet
const ScammerMap = dynamic(() => import('./ScammerMap'), { ssr: false });

export default function AdminDashboard() {
    const [stats, setStats] = useState<any>(null);
    const [trend, setTrend] = useState<any[]>([]);
    const [leaderboard, setLeaderboard] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchDashboardData = async () => {
            try {
                const response = await phantomFetch('/api/analytics/admin/dashboard', { ttl: 60000 });
                const data = await response.json();
                setStats(data.stats);
                setTrend(data.visualization.threat_trend_7d);
                setLeaderboard(data.leaderboard || []);
            } catch (error) {
                console.error("Failed to load dashboard statistics", error);
            } finally {
                setLoading(false);
            }
        };

        fetchDashboardData();
    }, []);

    const handleReward = async (userId: string) => {
        const points = prompt("Enter reward points for high-quality evidence (e.g., 5.0):", "5.0");
        if (!points || isNaN(parseFloat(points))) return;

        try {
            const response = await phantomFetch('/api/analytics/admin/reward-user', {
          ttl: 60000, // 1 min cache
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: userId, points: parseFloat(points) })
            });
            if (response.ok) {
                alert("Citizen rewarded successfully.");
                window.location.reload();
            }
        } catch (error) {
            console.error("Reward failed", error);
        }
    };

    if (loading) return <div className="p-8 text-center">Loading National Intelligence Data...</div>;

    return (
        <div className="p-6 bg-slate-50 min-h-screen">
            <header className="mb-8 flex justify-between items-center">
                <h1 className="text-3xl font-bold text-slate-900">VSDP Command Center</h1>
                <div className="bg-white px-4 py-2 rounded shadow-sm text-sm text-slate-500">
                    System Status: <span className="text-green-500 font-medium">Operational</span>
                </div>
            </header>

            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                    <p className="text-sm font-medium text-slate-500">Total Interceptions</p>
                    <h3 className="text-2xl font-bold text-slate-900">{stats.total_threats}</h3>
                </div>
                <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                    <p className="text-sm font-medium text-slate-500">FIRs Filed</p>
                    <h3 className="text-2xl font-bold text-blue-600">{stats.total_firs_filed}</h3>
                </div>
                <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                    <p className="text-sm font-medium text-slate-500">Critical Threats</p>
                    <h3 className="text-2xl font-bold text-red-600">{stats.threats_by_severity.critical || 0}</h3>
                </div>
                <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                    <p className="text-sm font-medium text-slate-500">Active Honeypots</p>
                    <h3 className="text-2xl font-bold text-amber-600">12</h3>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* 7-Day Trend Chart */}
                <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                    <h2 className="text-lg font-semibold mb-6">7-Day Threat Vector Trend</h2>
                    <div className="h-80">
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={trend}>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                                <XAxis dataKey="date" />
                                <YAxis />
                                <Tooltip />
                                <Line type="monotone" dataKey="count" stroke="#2563eb" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 8 }} />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Geospatial Map */}
                <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                    <h2 className="text-lg font-semibold mb-4">Geographic Threat Distribution</h2>
                    <div className="h-80 rounded-lg overflow-hidden border border-slate-200">
                        <ScammerMap />
                    </div>
                </div>

                {/* Citizen Leaderboard */}
                <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100 lg:col-span-2">
                    <div className="flex justify-between items-center mb-6">
                        <h2 className="text-lg font-semibold text-slate-900">Top Performing Citizens</h2>
                        <span className="text-xs text-slate-400 font-medium uppercase tracking-wider">National Defense Rankings</span>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="w-full text-left">
                            <thead>
                                <tr className="border-b border-slate-100">
                                    <th className="pb-3 font-semibold text-slate-600 text-xs uppercase">Citizen Name</th>
                                    <th className="pb-3 font-semibold text-slate-600 text-center text-xs uppercase">Scams Avoided</th>
                                    <th className="pb-3 font-semibold text-slate-600 text-right text-xs uppercase">Safety Score</th>
                                    <th className="pb-3 font-semibold text-slate-600 text-right text-xs uppercase">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {leaderboard.map((user, idx) => (
                                    <tr key={idx} className="border-b border-slate-50 last:border-0 hover:bg-slate-50/50 transition-colors">
                                        <td className="py-4 text-slate-900 font-medium flex items-center gap-3">
                                            <span className="text-slate-300 font-bold w-4">#{idx + 1}</span>
                                            {user.name}
                                        </td>
                                        <td className="py-4 text-slate-600 text-center font-mono">{user.scams_avoided}</td>
                                        <td className="py-4 text-right">
                                            <span className={`px-2.5 py-1 rounded-full text-xs font-bold ${user.safety_score > 90 ? 'bg-green-100 text-green-700' : 'bg-blue-100 text-blue-700'}`}>
                                                {user.safety_score.toFixed(1)}%
                                            </span>
                                        </td>
                                        <td className="py-4 text-right">
                                            <button
                                                onClick={() => handleReward(user.id)}
                                                className="text-[10px] font-bold text-blue-600 hover:text-blue-800 uppercase"
                                            >
                                                Reward
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    );
}