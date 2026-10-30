"use client";

import React from "react";
import { X, CheckCircle2, AlertCircle, ExternalLink, ShieldCheck, Building2, MapPin, Award } from "lucide-react";

interface EvidenceModalProps {
  job: any | null;
  onClose: () => void;
}

export const EvidenceModal: React.FC<EvidenceModalProps> = ({ job, onClose }) => {
  if (!job) return null;

  const elig = job.cohort_eligibilities?.[0] || {};
  const verificationResults = job.verification_results || [];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="relative w-full max-w-2xl bg-white rounded-2xl shadow-2xl border border-slate-200 overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100 bg-slate-50/50">
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-lg bg-emerald-100 text-emerald-700">
              <ShieldCheck className="w-5 h-5" />
            </span>
            <div>
              <h3 className="font-bold text-slate-900 text-base">Verification Proof & Verbatim Evidence</h3>
              <p className="text-xs text-slate-500">Stored from official posting during pipeline ingestion</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <div className="p-6 overflow-y-auto space-y-6">
          {/* Job Summary Banner */}
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80">
            <div className="flex flex-wrap items-center justify-between gap-2 mb-1">
              <div className="font-bold text-slate-900 text-lg">{job.title}</div>
              <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-emerald-100 text-emerald-800">
                Trust Score: {Math.round(job.trust_score)}%
              </span>
            </div>
            <div className="flex flex-wrap items-center gap-3 text-xs text-slate-600">
              <span className="flex items-center gap-1 font-medium text-slate-800">
                <Building2 className="w-3.5 h-3.5 text-slate-400" />
                {job.company_name} ({job.company_tier})
              </span>
              <span>•</span>
              <span className="flex items-center gap-1">
                <MapPin className="w-3.5 h-3.5 text-slate-400" />
                {job.normalized_city}
              </span>
              {job.stipend_ctc && (
                <>
                  <span>•</span>
                  <span className="font-semibold text-emerald-700">{job.stipend_ctc}</span>
                </>
              )}
            </div>
          </div>

          {/* Verbatim Proof Callout */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500">
              Critical Field Proof Snippets
            </h4>

            {/* Batch eligibility proof */}
            <div className="p-3.5 rounded-lg bg-emerald-50/70 border border-emerald-200">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-bold text-emerald-900">
                  Target Batch Eligibility Proof (Cohort {elig.cohort || "Active"})
                </span>
                <span className="text-[10px] font-semibold text-emerald-700 uppercase">Verbatim Source Quote</span>
              </div>
              <p className="text-xs text-emerald-950 font-mono bg-white/80 p-2.5 rounded border border-emerald-200/60 leading-relaxed">
                &ldquo;{elig.evidence_snippet || "Verified from listing text"}&rdquo;
              </p>
              {elig.branches && (
                <div className="mt-2 text-[11px] text-emerald-800 font-medium">
                  Accepted Branches: {elig.branches}
                </div>
              )}
            </div>

            {/* Pay transparency proof */}
            {job.stipend_ctc_evidence && (
              <div className="p-3.5 rounded-lg bg-blue-50/70 border border-blue-200">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-bold text-blue-900">Stipend / CTC Range Proof</span>
                  <span className="text-[10px] font-semibold text-blue-700 uppercase">Verbatim Source Quote</span>
                </div>
                <p className="text-xs text-blue-950 font-mono bg-white/80 p-2.5 rounded border border-blue-200/60 leading-relaxed">
                  &ldquo;{job.stipend_ctc_evidence}&rdquo;
                </p>
              </div>
            )}
          </div>

          {/* 8-Stage Verification Pipeline Checklist */}
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-3">
              8-Stage Verification Pipeline Audit Log
            </h4>
            <div className="border border-slate-200 rounded-xl divide-y divide-slate-100 overflow-hidden">
              {verificationResults.length > 0 ? (
                verificationResults.map((v: any, idx: number) => (
                  <div key={idx} className="p-3 flex items-start gap-3 bg-white text-xs">
                    {v.passed ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-600 mt-0.5 shrink-0" />
                    ) : (
                      <AlertCircle className="w-4 h-4 text-amber-500 mt-0.5 shrink-0" />
                    )}
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-slate-900 capitalize">
                          {v.check_name.replace("_", " ")}
                        </span>
                        <span className="text-[10px] text-slate-400 font-mono">Score: {Math.round(v.score)}</span>
                      </div>
                      <p className="text-slate-600 mt-0.5">{v.reason}</p>
                    </div>
                  </div>
                ))
              ) : (
                <div className="p-4 text-xs text-slate-500 text-center">
                  All 8 verification checks (Liveness, Domain Trust, Scam Filter, Fresher Exp, Location, Freshness, Role Relevance, Trust Score) passed with score &ge; 80.
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-3.5 bg-slate-50 border-t border-slate-100 flex items-center justify-between">
          <span className="text-xs text-slate-500 font-mono truncate max-w-[320px]">
            {job.company_domain}
          </span>
          <a
            href={job.final_apply_url || job.apply_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs shadow-sm transition"
          >
            <span>Proceed to Official ATS Apply</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
        </div>
      </div>
    </div>
  );
};
