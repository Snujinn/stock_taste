import Link from "next/link";

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-zinc-950 text-white">
      <main className="flex flex-col items-center gap-8 text-center px-4">
        <div className="space-y-4">
          <h1 className="text-5xl font-extrabold tracking-tight sm:text-7xl bg-gradient-to-r from-green-400 to-blue-500 bg-clip-text text-transparent">
            Mock Stock Game
          </h1>
          <p className="text-xl text-zinc-400 max-w-lg mx-auto">
            Experience the thrill of the market without the risk.
            Trade top US stocks with real-time data and compete on the global leaderboard.
          </p>
        </div>

        <div className="flex gap-4">
          <Link
            href="/login"
            className="rounded-full bg-white px-8 py-3 text-zinc-950 font-semibold transition hover:bg-zinc-200"
          >
            Login
          </Link>
          <Link
            href="/register"
            className="rounded-full border border-zinc-700 px-8 py-3 font-semibold transition hover:bg-zinc-800 hover:border-zinc-600"
          >
            Get Started
          </Link>
        </div>
      </main>

      <footer className="absolute bottom-8 text-zinc-600 text-sm">
        &copy; 2026 Mock Stock Game. All rights reserved.
      </footer>
    </div>
  );
}
