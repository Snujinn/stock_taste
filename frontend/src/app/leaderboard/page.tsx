'use client';
import { useEffect, useState } from 'react';
import api from '@/lib/api';
import Link from 'next/link';

interface Rank {
    rank: number;
    nickname: string;
    total_equity_krw: number;
}

export default function LeaderboardPage() {
    const [ranks, setRanks] = useState<Rank[]>([]);
    const [myRank, setMyRank] = useState<Rank | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [listRes, meRes] = await Promise.all([
                    api.get('/leaderboard/'),
                    api.get('/leaderboard/me')
                ]);
                setRanks(listRes.data);
                if (meRes.data.rank > 0) {
                    setMyRank({
                        rank: meRes.data.rank,
                        nickname: 'Me',
                        total_equity_krw: meRes.data.total_equity_krw
                    });
                }
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    if (loading) return <div className="min-h-screen bg-black text-white p-8 flex justify-center items-center">Loading Leaderboard...</div>;

    return (
        <div className="min-h-screen bg-black text-white p-8">
            <div className="max-w-2xl mx-auto">
                <div className="flex justify-between items-center mb-8">
                    <h1 className="text-3xl font-bold text-yellow-400">Leaderboard</h1>
                    <Link href="/market" className="bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded">Back to Market</Link>
                </div>

                {myRank && (
                    <div className="bg-gray-800 p-4 rounded-lg mb-6 border border-yellow-500/50 flex justify-between items-center">
                        <div>
                            <span className="text-gray-400 mr-2">My Rank:</span>
                            <span className="text-2xl font-bold">#{myRank.rank}</span>
                        </div>
                        <div className="font-mono text-xl">₩{myRank?.total_equity_krw.toLocaleString()}</div>
                    </div>
                )}

                <div className="bg-gray-800 rounded-lg overflow-hidden shadow-lg">
                    <table className="w-full text-left">
                        <thead className="bg-gray-700 text-gray-300">
                            <tr>
                                <th className="p-4 w-16">Rank</th>
                                <th className="p-4">Nickname</th>
                                <th className="p-4 text-right">Total Equity (KRW)</th>
                            </tr>
                        </thead>
                        <tbody>
                            {ranks.map((r) => (
                                <tr key={r.rank} className="border-b border-gray-700">
                                    <td className="p-4 font-bold text-gray-400">#{r.rank}</td>
                                    <td className="p-4">{r.nickname}</td>
                                    <td className="p-4 text-right font-mono">₩{r.total_equity_krw.toLocaleString()}</td>
                                </tr>
                            ))}
                            {ranks.length === 0 && (
                                <tr><td colSpan={3} className="p-8 text-center text-gray-400">No rankings yet.</td></tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
