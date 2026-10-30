import React from "react";
import Link from "next/link";
import { Rss, ShieldCheck } from "lucide-react";

export const Footer: React.FC = () => {
  return (
    <footer className="bg-slate-900 text-slate-400 py-12 border-t border-slate-800 mt-20">
      <div className="max-w-6xl mx-auto px-4 sm:px-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <div className="w-6 h-6 rounded bg-emerald-600 flex items-center justify-center text-white font-bold text-xs">
                FD
              </div>
              <span className="font-bold text-white text-base">FreshersDaily</span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed mb-4">
              Anti-hallucination engineering job research platform. Every day at 06:00 AM IST,
              we publish exactly 5 rigorously verified software opportunities for 2026 passouts,
              2027 graduates, and 2028 pre-final students in India.
            </p>
            <div className="flex items-center gap-2 text-xs text-emerald-400">
              <ShieldCheck className="w-4 h-4" />
              <span>Verbatim evidence stored for 100% of published roles</span>
            </div>
          </div>

          <div>
            <h4 className="text-sm font-semibold text-white mb-3">Cohorts & Programs</h4>
            <ul className="space-y-2 text-xs">
              <li>
                <Link href="/?cohort=2026" className="hover:text-emerald-400 transition">
                  Cohort 2026: Full-Time Fresher / Entry Level
                </Link>
              </li>
              <li>
                <Link href="/?cohort=2027" className="hover:text-emerald-400 transition">
                  Cohort 2027: Final Year Jobs + 6-Mo Internships with PPO
                </Link>
              </li>
              <li>
                <Link href="/?cohort=2028" className="hover:text-emerald-400 transition">
                  Cohort 2028: Pre-Final Summer Internships / Engage
                </Link>
              </li>
              <li>
                <Link href="/how-we-verify" className="hover:text-emerald-400 transition">
                  Our 8-Stage Strict Verification Standard
                </Link>
              </li>
            </ul>
          </div>

          <div>
            <h4 className="text-sm font-semibold text-white mb-3">Direct RSS Feeds</h4>
            <p className="text-xs text-slate-400 mb-3">
              Subscribe directly in your favorite RSS reader or Slackbot without tracking.
            </p>
            <div className="flex flex-col gap-2 text-xs">
              <a
                href="/feed/2026.xml"
                target="_blank"
                className="flex items-center gap-1.5 text-slate-300 hover:text-emerald-400 transition"
              >
                <Rss className="w-3.5 h-3.5 text-amber-500" />
                <span>RSS: Cohort 2026 Feed (/feed/2026.xml)</span>
              </a>
              <a
                href="/feed/2027.xml"
                target="_blank"
                className="flex items-center gap-1.5 text-slate-300 hover:text-emerald-400 transition"
              >
                <Rss className="w-3.5 h-3.5 text-amber-500" />
                <span>RSS: Cohort 2027 Feed (/feed/2027.xml)</span>
              </a>
              <a
                href="/feed/2028.xml"
                target="_blank"
                className="flex items-center gap-1.5 text-slate-300 hover:text-emerald-400 transition"
              >
                <Rss className="w-3.5 h-3.5 text-amber-500" />
                <span>RSS: Cohort 2028 Feed (/feed/2028.xml)</span>
              </a>
            </div>
          </div>
        </div>

        {/* Creator & Placement Trainer Credit Section */}
        <div className="bg-slate-800/80 rounded-2xl p-6 border border-slate-700/60 mb-8 flex flex-col md:flex-row items-center justify-between gap-5">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-400 flex items-center justify-center text-white font-black text-lg shadow-md ring-2 ring-emerald-500/30 shrink-0">
              DJ
            </div>
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <h4 className="text-white font-bold text-base tracking-tight">Deepak Joshi</h4>
                <span className="px-2.5 py-0.5 rounded-full bg-emerald-500/15 text-emerald-400 text-xs font-bold border border-emerald-500/30">
                  Placement Trainer
                </span>
                <span className="text-[11px] text-slate-400 font-medium">Platform Creator & Mentor</span>
              </div>
              <p className="text-xs text-slate-300 mt-1 leading-relaxed">
                Dedicated to empowering engineering students & Tier-3 college graduates across India with 100% verified, active, pedigree-bias-free software job opportunities.
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3 shrink-0 self-stretch md:self-auto justify-end border-t md:border-t-0 pt-3 md:pt-0 border-slate-700/50">
            <div className="text-right">
              <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-400 block">Student First Initiative</span>
              <span className="text-xs text-slate-400">Zero Pedigree Bias • Zero Fake Roles</span>
            </div>
          </div>
        </div>

        <div className="border-t border-slate-800 pt-6 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500">
          <p>© {new Date().getFullYear()} FreshersDaily • Created & Curated by <strong className="text-slate-200 font-semibold">Deepak Joshi (Placement Trainer)</strong>.</p>
          <p className="mt-2 sm:mt-0">Strictly no staffing agencies • Direct official careers portal links only</p>
        </div>
      </div>
    </footer>
  );
};
