"use client";

import React, { useEffect, useState } from "react";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { JobCard } from "@/components/JobCard";
import { EvidenceModal } from "@/components/EvidenceModal";
import { SubscribeModal } from "@/components/SubscribeModal";
import { ShieldCheck, Sparkles, AlertCircle, Filter, RefreshCw, Calendar } from "lucide-react";

export default function HomePage() {
  const [cohort, setCohort] = useState<string>("2027");
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedJobForEvidence, setSelectedJobForEvidence] = useState<any | null>(null);
  const [isSubscribeOpen, setIsSubscribeOpen] = useState<boolean>(false);

  // Filters
  const [cityFilter, setCityFilter] = useState<string>("ALL");
  const [roleFilter, setRoleFilter] = useState<string>("ALL");

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "/api";

  const fetchDailyFeed = async (targetCohort: string) => {
    setLoading(true);
    try {
      const res = await fetch(`${apiUrl}/cohorts/${targetCohort}/daily`);
      if (res.ok) {
        const json = await res.json();
        setData(json);
      } else {
        setData(null);
      }
    } catch (e) {
      console.error("Failed to fetch daily feed:", e);
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDailyFeed(cohort);
  }, [cohort]);

  // Filter listings
  const filterListings = (list: any[]) => {
    if (!list) return [];
    return list.filter((item) => {
      const job = item.job;
      const matchCity = cityFilter === "ALL" || job.normalized_city.toLowerCase().includes(cityFilter.toLowerCase());
      const matchRole = roleFilter === "ALL" || job.role_category === roleFilter;
      return matchCity && matchRole;
    });
  };

  const filteredToday = filterListings(data?.today_openings || []);
  const filteredFallback = filterListings(data?.still_open_fallback || []);

  return (
    <div className="min-h-screen flex flex-col justify-between bg-slate-50">
      <Header onOpenSubscribe={() => setIsSubscribeOpen(true)} />

      <main className="flex-1 max-w-6xl w-full mx-auto px-4 sm:px-6 py-8">
        {/* Hero Section */}
        <div className="mb-8 text-center sm:text-left sm:flex items-center justify-between">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-100 text-emerald-800 text-xs font-semibold mb-3">
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
              <span>Anti-Hallucination Standard • Published Daily at 06:00 IST</span>
            </div>
            <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
              Today&apos;s Verified Software Openings
            </h1>
            <p className="text-sm text-slate-600 mt-1">
              Exactly 5 high-quality, verified opportunities for your graduating batch in India. Zero spam.
            </p>
          </div>

          <div className="mt-4 sm:mt-0 flex items-center justify-center gap-2 text-xs text-slate-500 bg-white px-3.5 py-2 rounded-xl border border-slate-200 shadow-sm">
            <Calendar className="w-4 h-4 text-slate-400" />
            <span>Edition Date: <strong className="text-slate-800">{data?.date || new Date().toISOString().split("T")[0]}</strong></span>
          </div>
        </div>

        {/* Cohort Selector Tabs */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-6">
          <button
            onClick={() => setCohort("2026")}
            className={`p-4 rounded-xl text-left border transition-all ${
              cohort === "2026"
                ? "bg-slate-900 text-white border-slate-900 shadow-md ring-2 ring-slate-900/10"
                : "bg-white text-slate-700 border-slate-200 hover:border-slate-300"
            }`}
          >
            <div className="text-xs font-bold uppercase tracking-wider text-emerald-400 mb-1">
              Cohort 2026
            </div>
            <div className="font-extrabold text-base">2026 Passouts</div>
            <div className={`text-xs mt-1 ${cohort === "2026" ? "text-slate-300" : "text-slate-500"}`}>
              Full-time fresher & entry-level roles (0-1 yrs exp)
            </div>
          </button>

          <button
            onClick={() => setCohort("2027")}
            className={`p-4 rounded-xl text-left border transition-all ${
              cohort === "2027"
                ? "bg-slate-900 text-white border-slate-900 shadow-md ring-2 ring-slate-900/10"
                : "bg-white text-slate-700 border-slate-200 hover:border-slate-300"
            }`}
          >
            <div className="text-xs font-bold uppercase tracking-wider text-emerald-400 mb-1">
              Cohort 2027 • Recommended
            </div>
            <div className="font-extrabold text-base">2027 Graduates</div>
            <div className={`text-xs mt-1 ${cohort === "2027" ? "text-slate-300" : "text-slate-500"}`}>
              Final year full-time + 6-mo internships with PPO
            </div>
          </button>

          <button
            onClick={() => setCohort("2028")}
            className={`p-4 rounded-xl text-left border transition-all ${
              cohort === "2028"
                ? "bg-slate-900 text-white border-slate-900 shadow-md ring-2 ring-slate-900/10"
                : "bg-white text-slate-700 border-slate-200 hover:border-slate-300"
            }`}
          >
            <div className="text-xs font-bold uppercase tracking-wider text-emerald-400 mb-1">
              Cohort 2028
            </div>
            <div className="font-extrabold text-base">2028 Pre-Final</div>
            <div className={`text-xs mt-1 ${cohort === "2028" ? "text-slate-300" : "text-slate-500"}`}>
              Summer internships & explore/engage programs
            </div>
          </button>
        </div>

        {/* Filter Toolbar */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 mb-6 flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-2 text-xs font-semibold text-slate-600">
            <Filter className="w-4 h-4 text-slate-400" />
            <span>Filter Today&apos;s Feed:</span>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <div>
              <select
                value={cityFilter}
                onChange={(e) => setCityFilter(e.target.value)}
                className="text-xs bg-slate-50 border border-slate-200 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-emerald-500"
              >
                <option value="ALL">All Indian Cities</option>
                <option value="Bengaluru">Bengaluru</option>
                <option value="Hyderabad">Hyderabad</option>
                <option value="Pune">Pune</option>
                <option value="Mumbai">Mumbai</option>
                <option value="Noida">Noida / NCR</option>
                <option value="Remote">Remote - India</option>
              </select>
            </div>

            <div>
              <select
                value={roleFilter}
                onChange={(e) => setRoleFilter(e.target.value)}
                className="text-xs bg-slate-50 border border-slate-200 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-emerald-500"
              >
                <option value="ALL">All Software Roles</option>
                <option value="SDE">SDE / Software Engineer</option>
                <option value="Backend">Backend</option>
                <option value="Frontend">Frontend</option>
                <option value="Fullstack">Fullstack</option>
                <option value="QA/SDET">QA / SDET</option>
                <option value="DevOps/Cloud">DevOps / Cloud</option>
                <option value="GET/ASE">GET / ASE</option>
                <option value="ML/AI">ML / AI</option>
              </select>
            </div>
          </div>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="py-20 flex flex-col items-center justify-center text-slate-500">
            <RefreshCw className="w-8 h-8 animate-spin text-emerald-600 mb-3" />
            <p className="text-sm font-medium">Fetching verified listings for Cohort {cohort}...</p>
          </div>
        )}

        {/* Not-Complete Notice (if fewer than 5 pass) */}
        {!loading && data && !data.is_complete && data.message && (
          <div className="mb-6 p-4 rounded-xl bg-amber-50 border border-amber-200 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
            <div>
              <h4 className="text-sm font-bold text-amber-900">Notice on Today&apos;s Verified Count</h4>
              <p className="text-xs text-amber-800 mt-0.5 leading-relaxed">{data.message}</p>
            </div>
          </div>
        )}

        {/* Today's 5 Verified Openings Grid */}
        {!loading && (
          <div className="space-y-8">
            <div>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                  <span>Today&apos;s Verified Selection</span>
                  <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800">
                    {filteredToday.length} openings
                  </span>
                </h2>
              </div>

              {filteredToday.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {filteredToday.map((item: any) => (
                    <JobCard
                      key={item.id}
                      selection={item}
                      onInspectEvidence={(job) => setSelectedJobForEvidence(job)}
                    />
                  ))}
                </div>
              ) : (
                <div className="p-8 text-center bg-white rounded-xl border border-slate-200 text-slate-500 text-xs">
                  No verified openings matching selected filters today.
                </div>
              )}
            </div>

            {/* Fallback Still-Open Section */}
            {filteredFallback.length > 0 && (
              <div className="pt-6 border-t border-slate-200">
                <div className="mb-4">
                  <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
                    <span>Still Open From Previous Days (Re-verified Today)</span>
                    <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-slate-100 text-slate-600">
                      Fallback
                    </span>
                  </h3>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Re-verified for active apply status and valid future deadlines today.
                  </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {filteredFallback.map((item: any) => (
                    <JobCard
                      key={item.id}
                      selection={item}
                      onInspectEvidence={(job) => setSelectedJobForEvidence(job)}
                    />
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </main>

      <Footer />

      {/* Modals */}
      <EvidenceModal
        job={selectedJobForEvidence}
        onClose={() => setSelectedJobForEvidence(null)}
      />

      <SubscribeModal
        isOpen={isSubscribeOpen}
        onClose={() => setIsSubscribeOpen(false)}
      />
    </div>
  );
}
