"use client";

import React from "react";
import { ExternalLink, ShieldCheck, MapPin, Building2, Calendar, FileText, CheckCircle2 } from "lucide-react";

interface JobCardProps {
  selection: any;
  onInspectEvidence: (job: any) => void;
}

export const JobCard: React.FC<JobCardProps> = ({ selection, onInspectEvidence }) => {
  const job = selection.job;
  const elig = job.cohort_eligibilities?.[0];

  const getTierBadge = (tier: string) => {
    switch (tier) {
      case "TIER_1":
        return <span className="bg-purple-100 text-purple-800 text-[10px] font-bold px-2 py-0.5 rounded-full">Tier 1 • Top Tech</span>;
      case "TIER_2":
        return <span className="bg-blue-100 text-blue-800 text-[10px] font-bold px-2 py-0.5 rounded-full">Tier 2 • Scaleup</span>;
      case "TIER_3":
        return <span className="bg-slate-100 text-slate-700 text-[10px] font-bold px-2 py-0.5 rounded-full">Tier 3 • Enterprise</span>;
      default:
        return <span className="bg-slate-100 text-slate-600 text-[10px] font-medium px-2 py-0.5 rounded-full">Verified</span>;
    }
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 hover:border-slate-300 shadow-sm hover:shadow-md transition-all duration-200 overflow-hidden flex flex-col justify-between">
      <div className="p-5 sm:p-6">
        {/* Top Meta Header */}
        <div className="flex items-center justify-between gap-2 mb-3">
          <div className="flex items-center gap-2">
            <span className="w-6 h-6 rounded-full bg-slate-900 text-white font-bold text-xs flex items-center justify-center">
              #{selection.rank}
            </span>
            <span className="text-sm font-semibold text-slate-700">{job.company_name}</span>
            {getTierBadge(job.company_tier)}
          </div>
          <div className="flex items-center gap-1 text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-200">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
            <span>{Math.round(job.trust_score)}% Verified</span>
          </div>
        </div>

        {/* Job Title */}
        <h3 className="font-bold text-slate-900 text-lg leading-snug mb-2 hover:text-emerald-700 transition">
          {job.title}
        </h3>

        {/* Badges Bar */}
        <div className="flex flex-wrap items-center gap-2 mb-4 text-xs">
          <span className="flex items-center gap-1 font-medium text-slate-600 bg-slate-100 px-2 py-1 rounded-md">
            <MapPin className="w-3 h-3 text-slate-400" />
            {job.normalized_city}
            {job.is_remote ? " (Remote)" : job.is_hybrid ? " (Hybrid)" : ""}
          </span>
          <span className="bg-slate-100 text-slate-700 font-medium px-2 py-1 rounded-md">
            {job.role_category}
          </span>
          {job.stipend_ctc && (
            <span className="bg-emerald-50 text-emerald-800 font-bold px-2 py-1 rounded-md border border-emerald-200">
              {job.stipend_ctc}
            </span>
          )}
        </div>

        {/* Verbatim Batch Evidence Box */}
        {elig && elig.evidence_snippet && (
          <div className="p-3 rounded-lg bg-slate-50 border border-slate-200/80 mb-4 text-xs">
            <div className="flex items-center gap-1 text-slate-500 font-semibold mb-1 text-[11px]">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
              <span>Target Batch Evidence:</span>
            </div>
            <p className="text-slate-700 italic font-mono text-[11px] leading-relaxed line-clamp-2">
              &ldquo;{elig.evidence_snippet}&rdquo;
            </p>
          </div>
        )}
      </div>

      {/* Card Action Footer */}
      <div className="px-5 py-3.5 bg-slate-50/70 border-t border-slate-100 flex items-center justify-between gap-3">
        <button
          onClick={() => onInspectEvidence(job)}
          className="text-xs font-semibold text-slate-600 hover:text-slate-900 flex items-center gap-1 px-2.5 py-1.5 rounded-lg hover:bg-slate-200/60 transition"
        >
          <FileText className="w-3.5 h-3.5 text-slate-400" />
          <span>Inspect Evidence & Audit</span>
        </button>

        <a
          href={job.final_apply_url || job.apply_url}
          target="_blank"
          rel="noopener noreferrer"
          className="bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs px-4 py-2 rounded-lg flex items-center gap-1.5 shadow-sm transition"
        >
          <span>Direct Apply</span>
          <ExternalLink className="w-3.5 h-3.5" />
        </a>
      </div>
    </div>
  );
};
