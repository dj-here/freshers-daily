"use client";

import React from "react";
import Link from "next/link";
import { ShieldCheck, Mail, Calendar, Info, Lock } from "lucide-react";

interface HeaderProps {
  onOpenSubscribe: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onOpenSubscribe }) => {
  return (
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur border-b border-slate-200">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-emerald-600 flex items-center justify-center text-white font-bold text-lg shadow-sm">
            FD
          </div>
          <div>
            <span className="font-extrabold text-slate-900 tracking-tight text-lg">
              Freshers<span className="text-emerald-600">Daily</span>
            </span>
            <span className="hidden sm:inline-block ml-2 text-xs bg-emerald-100 text-emerald-800 font-semibold px-2 py-0.5 rounded-full">
              India • 5 Daily Verified
            </span>
          </div>
        </Link>

        <nav className="flex items-center gap-1 sm:gap-4 text-sm font-medium text-slate-600">
          <Link
            href="/"
            className="px-2.5 py-1.5 rounded-md hover:text-slate-900 hover:bg-slate-100 transition flex items-center gap-1"
          >
            Today
          </Link>
          <Link
            href="/archive"
            className="px-2.5 py-1.5 rounded-md hover:text-slate-900 hover:bg-slate-100 transition flex items-center gap-1"
          >
            <Calendar className="w-4 h-4 text-slate-400" />
            <span className="hidden sm:inline">Archives</span>
          </Link>
          <Link
            href="/how-we-verify"
            className="px-2.5 py-1.5 rounded-md hover:text-slate-900 hover:bg-slate-100 transition flex items-center gap-1"
          >
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
            <span className="hidden sm:inline">How We Verify</span>
          </Link>
          <Link
            href="/admin"
            className="px-2.5 py-1.5 rounded-md hover:text-slate-900 hover:bg-slate-100 transition flex items-center gap-1"
          >
            <Lock className="w-4 h-4 text-slate-400" />
            <span className="hidden sm:inline">Admin</span>
          </Link>

          <button
            onClick={onOpenSubscribe}
            className="ml-2 bg-slate-900 hover:bg-slate-800 text-white px-3.5 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 shadow-sm transition"
          >
            <Mail className="w-3.5 h-3.5" />
            <span>Get Daily 6 AM Digest</span>
          </button>
        </nav>
      </div>
    </header>
  );
};
