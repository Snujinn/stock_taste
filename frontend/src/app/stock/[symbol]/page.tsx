'use client';
import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import api from '@/lib/api';
import Link from 'next/link';

import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

export default function StockDetail() {
    const params = useParams();
    const symbol = (params.symbol as string).toUpperCase();
    const [data, setData] = useState<any>(null);
    const [history, setHistory] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    // Trade state
    const [qty, setQty] = useState(1);
    const [side, setSide] = useState<'BUY' | 'SELL'>('BUY');
    const [message, setMessage] = useState('');
    const [processing, setProcessing] = useState(false);

    const [userCash, setUserCash] = useState<number | null>(null);
    const FX_RATE = 1300; // Fixed for MVP

    const [error, setError] = useState('');

    useEffect(() => {
        const fetchData = async () => {
            try {
                // Fetch Price
                const priceRes = await api.get(`/market/prices/${symbol}`);
                setData(priceRes.data);

                // Fetch History
                try {
                    const historyRes = await api.get(`/market/history/${symbol}?resolution=D`);
                    // Convert timestamp to readable date for chart
                    const formattedHistory = historyRes.data.map((item: any) => ({
                        date: new Date(item.time * 1000).toLocaleDateString(),
                        price: item.close
                    }));
                    setHistory(formattedHistory);
                } catch (hErr) {
                    console.warn("Failed to fetch history:", hErr);
                }

                // Fetch Portfolio (Auth required)
                try {
                    const portfolioRes = await api.get('/portfolio');
                    setUserCash(portfolioRes.data.cash_krw);
                } catch (pErr) {
                    console.warn("Failed to fetch portfolio (may need login):", pErr);
                    // Treat as not logged in or auth error - userCash remains null
                }

            } catch (err: any) {
                console.error(err);
                setError(err.response?.status === 404 ? 'Symbol not found' : 'Failed to load data');
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, [symbol]);

    const handleOrder = async (e: React.FormEvent) => {
        e.preventDefault();
        setProcessing(true);
        setMessage('');
        try {
            await api.post('/trade/orders', {
                symbol: symbol,
                qty: parseInt(qty.toString()),
                side: side,
                order_type: 'MARKET'
            });
            setMessage('Order Executed!');
            // Refresh cash after trade
            const res = await api.get('/portfolio');
            setUserCash(res.data.cash_krw);
        } catch (err: any) {
            setMessage(err.response?.data?.detail || 'Order failed');
        } finally {
            setProcessing(false);
        }
    };

    if (loading) return <div className="min-h-screen bg-black text-white flex items-center justify-center">Loading...</div>;

    // Handle case where data might be empty object if not found
    if (error || !data || !data.price) return <div className="min-h-screen bg-black text-white flex items-center justify-center flex-col">
        <h1 className="text-2xl mb-4 text-red-500">{error || `Symbol ${symbol} not found or no data.`}</h1>
        <Link href="/market" className="text-blue-400 underline">Back to Market</Link>
    </div>;

    const price = parseFloat(data.price);
    const change = parseFloat(data.change);
    const pct = parseFloat(data.percent_change);

    const estTotalUSD = price * qty;
    const estTotalKRW = estTotalUSD * FX_RATE;

    let remainingCash = null;
    if (userCash !== null) {
        if (side === 'BUY') {
            remainingCash = userCash - estTotalKRW;
        } else {
            remainingCash = userCash + estTotalKRW;
        }
    }

    return (
        <div className="min-h-screen bg-black text-white p-8">
            <div className="max-w-4xl mx-auto">
                <Link href="/market" className="text-gray-400 hover:text-white mb-4 block">&larr; Back to Market</Link>
                <div className="bg-zinc-900 rounded-lg p-6 shadow-lg mb-6 border border-zinc-800">
                    <div className="flex justify-between items-start mb-6">
                        <div>
                            <h1 className="text-4xl font-bold mb-2">{symbol}</h1>
                            <p className="text-3xl font-mono">${price.toFixed(2)} <span className="text-lg text-gray-500">({(price * FX_RATE).toLocaleString()} KRW)</span></p>
                            <p className={change >= 0 ? "text-green-400" : "text-red-400"}>
                                {change > 0 ? '+' : ''}{change.toFixed(2)} ({pct.toFixed(2)}%)
                            </p>
                            <p className="text-sm text-gray-500 mt-2">Last Updated: {new Date(parseInt(data.timestamp) * 1000).toLocaleString()}</p>
                        </div>
                    </div>

                    {/* Chart Area */}
                    <div className="h-[300px] w-full mt-4">
                        {history.length > 0 ? (
                            <ResponsiveContainer width="100%" height="100%">
                                <LineChart data={history}>
                                    <XAxis dataKey="date" stroke="#666" tick={{ fill: '#666' }} minTickGap={30} />
                                    <YAxis domain={['auto', 'auto']} stroke="#666" tick={{ fill: '#666' }} />
                                    <Tooltip
                                        contentStyle={{ backgroundColor: '#18181b', borderColor: '#27272a', color: '#fff' }}
                                        itemStyle={{ color: '#fff' }}
                                    />
                                    <Line type="monotone" dataKey="price" stroke="#3b82f6" strokeWidth={2} dot={false} />
                                </LineChart>
                            </ResponsiveContainer>
                        ) : (
                            <div className="h-full flex items-center justify-center text-gray-500">
                                Loading Chart...
                            </div>
                        )}
                    </div>
                </div>

                <div className="bg-zinc-900 rounded-lg p-6 shadow-lg border border-zinc-800">
                    <h2 className="text-2xl font-bold mb-4 border-b border-zinc-800 pb-2">Trade</h2>

                    {userCash !== null && (
                        <div className="mb-4 bg-black p-3 rounded border border-zinc-800">
                            <p className="text-gray-400 text-sm">Current Cash</p>
                            <p className="text-xl font-mono">{userCash.toLocaleString()} KRW</p>
                        </div>
                    )}

                    <form onSubmit={handleOrder} className="space-y-4">
                        <div className="flex space-x-4 mb-4">
                            <button type="button" onClick={() => setSide('BUY')} className={`flex-1 py-2 rounded font-bold transition ${side === 'BUY' ? 'bg-green-600' : 'bg-zinc-800 hover:bg-zinc-700'}`}>Buy</button>
                            <button type="button" onClick={() => setSide('SELL')} className={`flex-1 py-2 rounded font-bold transition ${side === 'SELL' ? 'bg-red-600' : 'bg-zinc-800 hover:bg-zinc-700'}`}>Sell</button>
                        </div>

                        <div>
                            <label className="block mb-1 text-gray-300">Quantity</label>
                            <input
                                type="number"
                                min="1"
                                value={qty}
                                onChange={(e) => setQty(parseInt(e.target.value))}
                                className="w-full p-2 rounded bg-black border border-zinc-700 font-mono text-lg focus:border-blue-500 outline-none transition"
                            />
                        </div>

                        <div className="border-t border-zinc-800 pt-4 space-y-2">
                            <div className="flex justify-between text-lg">
                                <span className="text-gray-400">Estimated Total:</span>
                                <div className="text-right">
                                    <div className="font-mono">${estTotalUSD.toFixed(2)}</div>
                                    <div className="text-sm text-gray-500">{estTotalKRW.toLocaleString()} KRW</div>
                                </div>
                            </div>

                            {remainingCash !== null && (
                                <div className="flex justify-between text-lg border-t border-zinc-800 pt-2">
                                    <span className={remainingCash < 0 ? "text-red-400" : "text-gray-300"}>
                                        {side === 'BUY' ? 'Remaining Cash:' : 'Proj. Cash:'}
                                    </span>
                                    <span className={`font-mono ${remainingCash < 0 ? "text-red-400 font-bold" : "text-white"}`}>
                                        {remainingCash.toLocaleString()} KRW
                                    </span>
                                </div>
                            )}
                        </div>

                        <button
                            type="submit"
                            disabled={processing || (side === 'BUY' && remainingCash !== null && remainingCash < 0)}
                            className={`w-full py-3 rounded font-bold text-lg mt-4 transition ${side === 'BUY'
                                ? 'bg-green-600 hover:bg-green-700 shadow-[0_0_15px_rgba(22,163,74,0.5)]'
                                : 'bg-red-600 hover:bg-red-700 shadow-[0_0_15px_rgba(220,38,38,0.5)]'
                                } disabled:opacity-50 disabled:shadow-none disabled:cursor-not-allowed`}
                        >
                            {processing ? 'Processing...' : (side === 'BUY' && remainingCash !== null && remainingCash < 0 ? 'Insufficient Funds' : `Submit ${side} Order`)}
                        </button>
                        {message && <p className="text-center mt-2 font-bold text-yellow-400">{message}</p>}
                    </form>
                </div>
            </div>
        </div>
    );
}
