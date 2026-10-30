"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { SubscribeModal } from "@/components/SubscribeModal";
import { Calendar, ArrowRight, ShieldCheck } from "lucide-react";

export default function ArchivePage() {
  const [cohort, setCohort] = useState<string>("2027");
  const [archiveDates, setArchiveDates] = useState<string[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [isSubscribeOpen, setIsSubscribeOpen] = useState(false);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "/api";

  useEffect(() => {
    async function loadArchives() {
      setLoading(true);
      try {
        const res = await fetch(`${apiUrl}/cohorts/${cohort}/archive`);
        if (res.ok) {
          const json = await res.json();
          setArchiveDates(json.archive_dates || []);
        }
      } catch (err) {
        console.error("Failed to load archive dates:", err);
      } finally {
        setLoading(false);
      }
    }
    loadArchives();
  }, [cohort]);

  return (
    <div className="min-h-screen flex flex-col justify-between bg-slate-50">
      <Header onOpenSubscribe={() => setIsSubscribeOpen(true)} />

      <main className="flex-1 max-w-4xl w-full mx-auto px-4 sm:px-6 py-12">
        <div className="mb-8">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-200 text-slate-800 text-xs font-semibold mb-3">
            <Calendar className="w-4 h-4 text-slate-600" />
            <span>Daily Verified Archives</span>
          </div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">
            Historical Daily Selections
          </h1>
          <p className="text-sm text-slate-600 mt-1">
            Browse through past verified daily editions by date.
          </p>
        </div>

        {/* Cohort Tabs */}
        <div className="flex gap-2 mb-6">
          {["2026", "2027", "2028"].map((c) => (
            <button
              key={c}
              onClick={() => setCohort(c)}
              className={`px-4 py-2 rounded-lg text-xs font-bold transition ${
                cohort === c
                  ? "bg-slate-900 text-white shadow-sm"
                  : "bg-white text-slate-700 border border-slate-200 hover:bg-slate-100"
              }`}
            >
              Cohort {c}
            </button>
          ))}
        </div>

        {loading ? (
          <div className="p-12 text-center text-xs text-slate-500">Loading historical dates...</div>
        ) : archiveDates.length > 0 ? (
          <div className="bg-white rounded-xl border border-slate-200 divide-y divide-slate-100 overflow-hidden shadow-sm">
            {archiveDates.map((d) => (
              <Link
                key={d}
                href={`/?cohort=${cohort}&date=${d}`}
                className="p-4 flex items-center justify-between hover:bg-slate-50 transition"
              >
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-700 flex items-center justify-center font-bold text-xs">
                    <ShieldCheck className="w-4 h-4" />
                  </div>
                  <div>
                    <div className="text-sm font-bold text-slate-900">Edition of {d}</div>
                    <div className="text-xs text-slate-500">5 Verified Opportunities for Cohort {cohort}</div>
                  </div>
                </div>
                <ArrowRight className="w-4 h-4 text-slate-400" />
              </Link>
            ))}
          </div>
        ) : (
          <div className="p-12 text-center bg-white rounded-xl border border-slate-200 text-xs text-slate-500">
            No past editions found for Cohort {cohort} yet.
          </div>
        )}
      </main>

      <Footer />

      <SubscribeModal
        isOpen={isSubscribeOpen}
        onClose={() => setIsSubscribeOpen(false)}
      />
    </div>
  );
}
