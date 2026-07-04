'use client'
import { phantomFetch } from "@/app/lib/fetch";;

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

const navItems = [
    { name: 'SMS Scanner', href: '/scanner', icon: '📱' },
    { name: 'Call Analyzer', href: '/call-analyzer', icon: '📞' },
    { name: 'Admin Dashboard', href: '/dashboard', icon: '📊' },
    { name: 'FIR Management', href: '/firs', icon: '📝' },
    { name: 'Evidence Ledger', href: '/evidence', icon: '⛓️' },
    { name: 'Honeypot Ops', href: '/honeypot', icon: '🍯' },
];

export default function Sidebar() {
    const pathname = usePathname();
    const [safetyData, setSafetyData] = useState<any>(null);
    const [showAlert, setShowAlert] = useState(false);
    const [protectionTimeLeft, setProtectionTimeLeft] = useState<string | null>(null);
    const [isExpiringSoon, setIsExpiringSoon] = useState(false);

    useEffect(() => {
        phantomFetch('/api/analytics/safety-score')
            .then(res => res.json())
            .then(data => {
                setSafetyData(data);
                if (data?.safety_score !== undefined && data.safety_score < 50) {
                    setShowAlert(true);
                }
            })
            .catch(err => console.error("Failed to fetch safety metrics", err));
    }, []);

    useEffect(() => {
        if (!safetyData?.protection_expiry) return;

        const interval = setInterval(() => {
            const expiry = new Date(safetyData.protection_expiry).getTime();
            const now = new Date().getTime();
            const diff = expiry - now;

            if (diff <= 0) {
                setProtectionTimeLeft(null);
                clearInterval(interval);
            } else {
                const hours = Math.floor(diff / (1000 * 60 * 60));
                const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
                setIsExpiringSoon(hours < 6);
                setProtectionTimeLeft(`${hours}h ${minutes}m`);
            }
        }, 60000);
        return () => clearInterval(interval);
    }, [safetyData]);

    return (
        <aside className="w-64 bg-slate-900 text-white flex flex-col h-screen sticky top-0 border-r border-slate-800">
            {/* Platform Branding */}
            <div className="p-6 border-b border-slate-800">
                <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-blue-600 rounded flex items-center justify-center font-bold text-lg">
                        V
                    </div>
                    <div>
                        <h1 className="font-bold text-sm tracking-tight">VSDP PLATFORM</h1>
                        <p className="text-[10px] text-slate-400 uppercase tracking-widest">National Defense</p>
                    </div>
                </div>
            </div>

            {/* Citizen Safety Stats */}
            <div className="mx-4 mt-6 p-4 bg-slate-800/50 rounded-xl border border-slate-700 group relative">
                <div className="flex items-center justify-between mb-2">
                    <p className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">Your Safety Status</p>
                    <span className="cursor-help text-[10px] text-slate-600 transition-colors group-hover:text-blue-400">ⓘ</span>
                </div>

                {/* Calculation Tooltip */}
                <div className="absolute bottom-full left-0 mb-3 w-56 p-3 bg-slate-900 border border-slate-700 rounded-lg shadow-2xl opacity-0 group-hover:opacity-100 transition-all duration-200 pointer-events-none z-50 text-[10px] text-slate-300 leading-relaxed transform translate-y-2 group-hover:translate-y-0">
                    <p className="font-bold text-blue-400 mb-1">Score Calculation</p>
                    Your score starts at 100. Deductions occur for detected threats (Critical: -15, High: -10). Points are restored over time through safe usage and successful threat interceptions.
                </div>

                {protectionTimeLeft && (
                    <div className={`mb-3 flex items-center justify-between px-2 py-1 rounded border ${isExpiringSoon ? 'bg-amber-500/10 border-amber-500/20' : 'bg-blue-500/10 border-blue-500/20'}`}>
                        <p className={`text-[8px] font-bold uppercase tracking-tight ${isExpiringSoon ? 'text-amber-400' : 'text-blue-400'}`}>Protection Active</p>
                        <p className="text-[8px] font-mono text-slate-300">{protectionTimeLeft}</p>
                    </div>
                )}

                {safetyData?.is_high_risk_trend && (
                    <div className="mb-3 flex items-center gap-2 px-2 py-1 bg-red-500/10 border border-red-500/20 rounded">
                        <span className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse" />
                        <p className="text-[9px] font-bold text-red-400 uppercase tracking-tight">High Risk Trend Detected</p>
                    </div>
                )}

                <div className="flex items-end justify-between">
                    <div>
                        <p className="text-2xl font-bold text-white">{safetyData?.safety_score ?? '--'}</p>
                        <p className="text-[10px] text-green-400 font-medium">Safety Score</p>
                    </div>
                    <div className="text-right">
                        <p className="text-sm font-bold text-blue-400">{safetyData?.scams_avoided ?? '0'}</p>
                        <p className="text-[10px] text-slate-500">Threats Blocked</p>
                    </div>
                </div>
                <div className="mt-3 w-full bg-slate-700 h-1.5 rounded-full overflow-hidden relative">
                    {/* Protection Shield Glow */}
                    {protectionTimeLeft && (
                        <div className="absolute inset-0 bg-blue-400/20 animate-pulse z-10" />
                    )}
                    <div
                        className={`h-full transition-all duration-1000 relative z-20 ${protectionTimeLeft ? 'bg-cyan-400 shadow-[0_0_10px_#22d3ee]' : 'bg-blue-500'}`}
                        style={{ width: `${safetyData?.safety_score ?? 0}%` }} />
                </div>

                {/* Severity Breakdown */}
                <div className="mt-4 pt-3 border-t border-slate-700/50">
                    <div className="grid grid-cols-2 gap-y-2">
                        {['critical', 'high', 'medium', 'low'].map((sev) => {
                            const count = safetyData?.severity_breakdown?.[sev] || 0;
                            return (
                                <div key={sev} className="flex items-center justify-between pr-2">
                                    <span className="text-[9px] text-slate-500 capitalize">{sev}</span>
                                    <span className={`text-[9px] font-bold ${count > 0 ? (sev === 'critical' || sev === 'high' ? 'text-red-400' : 'text-slate-300') : 'text-slate-600'}`}>{count}</span>
                                </div>
                            );
                        })}
                    </div>
                </div>
            </div>

            {/* Navigation Links */}
            <nav className="flex-1 overflow-y-auto py-4">
                <ul className="space-y-1 px-3">
                    {navItems.map((item) => {
                        const isActive = pathname === item.href;
                        return (
                            <li key={item.name}>
                                <Link
                                    href={item.href}
                                    className={`
                    flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors
                    ${isActive
                                            ? 'bg-blue-600/10 text-blue-400 border border-blue-600/20'
                                            : 'text-slate-400 hover:text-white hover:bg-slate-800'
                                        }
                  `}
                                >
                                    <span className="text-lg">{item.icon}</span>
                                    {item.name}
                                </Link>
                            </li>
                        );
                    })}
                </ul>
            </nav>

            {/* User Status / Footer */}
            <div className="p-4 bg-slate-950 border-t border-slate-800">
                <div className="flex items-center gap-3 mb-4">
                    <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                    <div className="text-xs">
                        <p className="text-slate-300 font-medium">Cyber Officer Session</p>
                        <p className="text-slate-500">ID: 4029-X</p>
                    </div>
                </div>
                <button
                    onClick={() => window.location.href = '/logout'}
                    className="w-full py-2 bg-slate-800 hover:bg-red-900/20 hover:text-red-400 text-slate-400 text-xs font-semibold rounded transition-all border border-slate-700"
                >
                    Secure Logout
                </button>
            </div>

            {/* Critical Safety Alert Modal */}
            {showAlert && (
                <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
                    <div className="bg-slate-900 border border-red-500/50 p-8 rounded-2xl max-w-md w-full shadow-2xl text-center">
                        <div className="w-16 h-16 bg-red-500/10 rounded-full flex items-center justify-center mx-auto mb-6">
                            <span className="text-3xl">⚠️</span>
                        </div>
                        <h2 className="text-xl font-bold text-white mb-2">Critical Safety Warning</h2>
                        <p className="text-slate-400 text-sm mb-6 leading-relaxed">
                            Your safety score has dropped to <span className="text-red-500 font-bold">{safetyData?.safety_score}</span>.
                            The platform has detected multiple high-risk threats targeting your device. Immediate caution is advised.
                        </p>
                        <button
                            onClick={() => setShowAlert(false)}
                            className="w-full py-3 bg-red-600 hover:bg-red-700 text-white font-bold rounded-lg transition-colors"
                        >
                            Acknowledge Risk
                        </button>
                    </div>
                </div>
            )}
        </aside>
    );
}