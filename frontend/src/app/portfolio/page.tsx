'use client';
import { useEffect, useState } from 'react';
import api from '@/lib/api';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

export default function PortfolioPage() {
    const [data, setData] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const router = useRouter();

    useEffect(() => {
        const fetchData = async () => {
            try {
                const res = await api.get('/portfolio/');
                setData(res.data);
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    if (loading) return <div className="min-h-screen bg-black text-white p-8 flex justify-center items-center">Loading Portfolio...</div>;
    if (!data) return <div className="min-h-screen bg-black text-white p-8 flex justify-center items-center">Failed to load portfolio.</div>;

    return (
        <div className="min-h-screen bg-black text-white p-8">
            <div className="max-w-4xl mx-auto">
                <div className="flex justify-between items-center mb-8">
                    <h1 className="text-3xl font-bold text-blue-400">My Portfolio</h1>
                    <Link href="/market" className="bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded">Back to Market</Link>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
                    <div className="bg-gray-800 p-6 rounded-lg shadow-lg">
                        <h2 className="text-gray-400 mb-2">Total Equity (KRW)</h2>
                        <p className="text-4xl font-bold font-mono text-green-400">₩{data.total_equity_krw.toLocaleString()}</p>
                    </div>
                    <div className="bg-gray-800 p-6 rounded-lg shadow-lg">
                        <h2 className="text-gray-400 mb-2">Cash Available (KRW)</h2>
                        <p className="text-4xl font-bold font-mono">₩{data.cash_krw.toLocaleString()}</p>
                    </div>
                </div>

                <div className="bg-gray-800 rounded-lg overflow-hidden shadow-lg">
                    <h2 className="text-xl font-bold p-4 bg-gray-750 border-b border-gray-700">Holdings</h2>
                    {data.holdings.length === 0 ? (
                        <div className="p-8 text-center text-gray-400">No holdings. Go buy some stocks!</div>
                    ) : (
                        <div className="overflow-x-auto">
                            <table className="w-full text-left">
                                <thead className="bg-gray-700 text-gray-300">
                                    <tr>
                                        <th className="p-4">Symbol</th>
                                        <th className="p-4">Qty</th>
                                        <th className="p-4">Avg Cost (USD)</th>
                                        <th className="p-4">Current Price</th>
                                        <th className="p-4">Market Value (KRW)</th>
                                        <th className="p-4">Return %</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {data.holdings.map((h: any) => (
                                        <tr key={h.symbol} className="border-b border-gray-700 hover:bg-gray-750 cursor-pointer" onClick={() => router.push(`/stock/${h.symbol}`)}>
                                            <td className="p-4 font-bold">{h.symbol}</td>
                                            <td className="p-4">{h.qty}</td>
                                            <td className="p-4 text-gray-400">${h.avg_cost_usd.toFixed(2)}</td>
                                            <td className="p-4">${h.current_price_usd.toFixed(2)}</td>
                                            <td className="p-4 font-mono">₩{h.market_value_krw.toLocaleString()}</td>
                                            <td className={`p-4 font-bold ${h.return_pct >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                                {h.return_pct > 0 ? '+' : ''}{h.return_pct.toFixed(2)}%
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
