"use client";

import React, { useState } from "react";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { SubscribeModal } from "@/components/SubscribeModal";
import { ShieldCheck, CheckCircle2, AlertTriangle, Lock, Eye, Filter, Zap, Scale } from "lucide-react";

export default function HowWeVerifyPage() {
  const [isSubscribeOpen, setIsSubscribeOpen] = useState(false);

  const stages = [
    {
      num: 1,
      title: "Active Liveness & Closure Inspection",
      desc: "Every link must return HTTP 200 following redirects. More importantly, our parser inspects the page DOM and body content for subtle closure messages like 'requisition closed', 'no longer accepting applications', or login-wall hurdles.",
      icon: <Zap className="w-5 h-5 text-emerald-600" />
    },
    {
      num: 2,
      title: "Domain Trust & ATS Verification",
      desc: "Every apply URL must terminate on the employer's official domain or an authoritative enterprise ATS (e.g. greenhouse.io, lever.co, myworkdayjobs.com, ashbyhq.com, smartrecruiters.com). URL shorteners, Google Forms, and Telegram channels are strictly rejected.",
      icon: <Lock className="w-5 h-5 text-emerald-600" />
    },
    {
      num: 3,
      title: "Scam & Training-Placement Filter",
      desc: "Zero tolerance for predatory postings. Any job mentioning 'security deposit', 'registration fee', 'training charges', 'pay to join', or 'earn per day' is rejected with an instant score of 0.",
      icon: <AlertTriangle className="w-5 h-5 text-amber-500" />
    },
    {
      num: 4,
      title: "Fresher Eligibility & Hidden Experience Trap Filter",
      desc: "Two-phase verification: Regex pre-screening + LLM structured JSON extraction. Postings requiring 2+ years of experience in seemingly junior titles are caught and rejected. Verbatim proof of batch or fresher eligibility is extracted and stored.",
      icon: <Eye className="w-5 h-5 text-emerald-600" />
    },
    {
      num: 5,
      title: "India Location Normalizer",
      desc: "Ensures roles are strictly based in Indian cities (Bengaluru, Hyderabad, Pune, Gurgaon, Noida, Mumbai, Chennai, etc.) or explicitly 'Remote - India'. Roles in foreign countries or ambiguous global locations are discarded.",
      icon: <Filter className="w-5 h-5 text-emerald-600" />
    },
    {
      num: 6,
      title: "Freshness & Deduplication Engine",
      desc: "Postings must have been first seen within the last 14 days, and deadlines must be in the future. Deduplication prevents showing repeated postings across different aggregators.",
      icon: <CheckCircle2 className="w-5 h-5 text-emerald-600" />
    },
    {
      num: 7,
      title: "Software Role Category Allow-List",
      desc: "High-confidence classification ensuring roles belong to core engineering (SDE, Backend, Frontend, Fullstack, Mobile, QA/SDET, DevOps/Cloud, ML/AI, GET/ASE). Non-software roles (sales, support, HR) are excluded.",
      icon: <Scale className="w-5 h-5 text-emerald-600" />
    },
    {
      num: 8,
      title: "Final Multi-Objective Trust Scoring (0-100)",
      desc: "Only opportunities with a trust score >= 80% are eligible for automated daily publishing. Listings scoring 60-79% are routed to the human Admin Review Queue.",
      icon: <ShieldCheck className="w-5 h-5 text-emerald-600" />
    }
  ];

  return (
    <div className="min-h-screen flex flex-col justify-between bg-slate-50">
      <Header onOpenSubscribe={() => setIsSubscribeOpen(true)} />

      <main className="flex-1 max-w-4xl mx-auto px-4 sm:px-6 py-12">
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-100 text-emerald-800 text-xs font-semibold mb-3">
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
            <span>Anti-Hallucination Standard</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
            How We Strictly Verify Every Opening
          </h1>
          <p className="text-sm sm:text-base text-slate-600 mt-2 max-w-2xl mx-auto leading-relaxed">
            FreshersDaily solves the widespread epidemic of ghost jobs, expired links, hidden 3-year experience traps, and scam placements for engineering students in India.
          </p>
        </div>

        {/* Core Invariants */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 mb-12 shadow-sm">
          <h2 className="text-lg font-bold text-slate-900 mb-4">Our Non-Negotiable Rules</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs text-slate-700">
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
              <strong className="block text-slate-900 text-sm mb-1">1. Verbatim Proof Only</strong>
              The AI is never allowed to guess or infer eligibility. Every critical field stores verbatim source quotes.
            </div>
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
              <strong className="block text-slate-900 text-sm mb-1">2. Zero Fabrication Policy</strong>
              If only 3 verified openings pass today for a cohort, we publish 3 and explain why. We never pad or invent fake roles.
            </div>
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
              <strong className="block text-slate-900 text-sm mb-1">3. Direct Official Portals</strong>
              Every link directs students straight to the company&apos;s own Workday, Greenhouse, Lever, Ashby, or career portal.
            </div>
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
              <strong className="block text-slate-900 text-sm mb-1">4. Pre-Publish Re-verification</strong>
              At 05:45 AM IST, 15 minutes before daily publication, selected listings are re-tested to ensure links have not closed overnight.
            </div>
          </div>
        </div>

        {/* 8 Stages Detailed */}
        <div className="space-y-4">
          <h2 className="text-xl font-bold text-slate-900 mb-6">The 8-Stage Verification Pipeline</h2>
          {stages.map((st) => (
            <div key={st.num} className="bg-white rounded-xl border border-slate-200 p-5 flex items-start gap-4 shadow-sm">
              <div className="w-10 h-10 rounded-xl bg-emerald-50 border border-emerald-200 flex items-center justify-center shrink-0">
                {st.icon}
              </div>
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded">
                    Stage {st.num}
                  </span>
                  <h3 className="font-bold text-slate-900 text-base">{st.title}</h3>
                </div>
                <p className="text-xs text-slate-600 leading-relaxed">{st.desc}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Creator & Mission Section */}
        <div className="mt-12 bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-sm">
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-5">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-emerald-600 to-teal-500 flex items-center justify-center text-white font-extrabold text-2xl shadow-md shrink-0">
              DJ
            </div>
            <div className="flex-1">
              <div className="flex flex-wrap items-center gap-2 mb-1">
                <h3 className="text-xl font-extrabold text-slate-900">Deepak Joshi</h3>
                <span className="px-3 py-0.5 rounded-full bg-emerald-100 text-emerald-800 text-xs font-bold">
                  Placement Trainer & Creator
                </span>
              </div>
              <p className="text-sm text-slate-600 leading-relaxed">
                As a Placement Trainer, Deepak Joshi created FreshersDaily to solve the biggest challenges faced by engineering freshers and Tier-3 college students in India: fake job listings, expired application links, hidden experience requirements, and college-pedigree bias. Every opening on this platform is verified to ensure equal opportunity and direct access to genuine software careers.
              </p>
            </div>
          </div>
        </div>
      </main>

      <Footer />

      <SubscribeModal
        isOpen={isSubscribeOpen}
        onClose={() => setIsSubscribeOpen(false)}
      />
    </div>
  );
}
