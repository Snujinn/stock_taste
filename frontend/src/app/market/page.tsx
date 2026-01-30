'use client';
import { useEffect, useState } from 'react';
import api from '@/lib/api';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

interface Ticker {
    symbol: string;
    name: string;
}

interface PriceData {
    price: number;
    change: number;
    percent_change: number;
    timestamp: string;
}

export default function MarketPage() {
    const [tickers, setTickers] = useState<Ticker[]>([]);
    const [prices, setPrices] = useState<Record<string, PriceData>>({});
    const [loading, setLoading] = useState(true);
    const router = useRouter();

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [tickersRes, pricesRes] = await Promise.all([
                    api.get('/market/tickers'), // Returns [{symbol, name}, ...]
                    api.get('/market/prices'),
                ]);
                setTickers(tickersRes.data);
                setPrices(pricesRes.data);
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
        const interval = setInterval(fetchData, 30000); // Poll every 30s
        return () => clearInterval(interval);
    }, []);

    if (loading) return <div className="min-h-screen bg-black text-white flex items-center justify-center">Loading Market...</div>;

    return (
        <div className="min-h-screen bg-black text-white p-8">
            <div className="max-w-4xl mx-auto">
                <div className="flex justify-between items-center mb-8">
                    <h1 className="text-3xl font-bold text-blue-400">Market</h1>
                    <div className="space-x-4">
                        <Link href="/portfolio" className="bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded">Portfolio</Link>
                        <Link href="/leaderboard" className="bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded">Leaderboard</Link>
                    </div>
                </div>

                <div className="bg-zinc-900 rounded-lg overflow-hidden shadow-lg border border-zinc-800">
                    <table className="w-full text-left">
                        <thead className="bg-zinc-800 text-gray-300">
                            <tr>
                                <th className="p-4">Symbol</th>
                                <th className="p-4">Price (USD)</th>
                                <th className="p-4">Change</th>
                                <th className="p-4">Updated</th>
                            </tr>
                        </thead>
                        <tbody>
                            {tickers.map((ticker) => {
                                const symbol = ticker.symbol;
                                const data = prices[symbol];
                                const price = data ? parseFloat(data.price.toString()).toFixed(2) : '-';
                                const change = data ? parseFloat(data.change.toString()) : 0;
                                const pct = data ? parseFloat(data.percent_change.toString()) : 0;
                                const color = change >= 0 ? 'text-green-400' : 'text-red-400';

                                return (
                                    <tr key={symbol} className="border-b border-zinc-800 hover:bg-zinc-800 cursor-pointer transition-colors" onClick={() => router.push(`/stock/${symbol}`)}>
                                        <td className="p-4">
                                            <div className="font-bold text-lg">{ticker.name}</div>
                                            <div className="text-sm text-gray-400">{symbol}</div>
                                        </td>
                                        <td className="p-4">${price}</td>
                                        <td className={`p-4 ${color}`}>
                                            {change > 0 ? '+' : ''}{change.toFixed(2)} ({pct.toFixed(2)}%)
                                        </td>
                                        <td className="p-4 text-sm text-gray-400">
                                            {data ? new Date(parseInt(data.timestamp) * 1000).toLocaleTimeString() : '-'}
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
