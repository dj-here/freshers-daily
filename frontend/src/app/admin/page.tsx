"use client";

import React, { useState, useEffect } from "react";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { Lock, ShieldAlert, CheckCircle, XCircle, Activity, PlusCircle, RefreshCw, Key } from "lucide-react";

export default function AdminPage() {
  const [adminKey, setAdminKey] = useState<string>("adminkey-dev-supersecret-freshersdaily-2026");
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(true);
  const [activeTab, setActiveTab] = useState<"review" | "manual" | "health">("review");

  // Review Queue state
  const [reviewJobs, setReviewJobs] = useState<any[]>([]);
  const [loadingReview, setLoadingReview] = useState<boolean>(false);

  // Health state
  const [sourcesHealth, setSourcesHealth] = useState<any[]>([]);
  const [loadingHealth, setLoadingHealth] = useState<boolean>(false);

  // Manual submission state
  const [submitUrl, setSubmitUrl] = useState<string>("");
  const [submitCompany, setSubmitCompany] = useState<string>("");
  const [submitCohort, setSubmitCohort] = useState<string>("2027");
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [submitResult, setSubmitResult] = useState<any | null>(null);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "/api";

  const fetchReviewQueue = async () => {
    setLoadingReview(true);
    try {
      const res = await fetch(`${apiUrl}/admin/review-queue`, {
        headers: { "X-Admin-Key": adminKey },
      });
      if (res.ok) {
        const json = await res.json();
        setReviewJobs(json);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingReview(false);
    }
  };

  const fetchHealth = async () => {
    setLoadingHealth(true);
    try {
      const res = await fetch(`${apiUrl}/admin/sources/health`, {
        headers: { "X-Admin-Key": adminKey },
      });
      if (res.ok) {
        const json = await res.json();
        setSourcesHealth(json);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingHealth(false);
    }
  };

  useEffect(() => {
    if (activeTab === "review") fetchReviewQueue();
    if (activeTab === "health") fetchHealth();
  }, [activeTab]);

  const handleAction = async (jobId: number, action: "approve" | "reject") => {
    try {
      const res = await fetch(`${apiUrl}/admin/jobs/${jobId}/action`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Admin-Key": adminKey,
        },
        body: JSON.stringify({ action }),
      });
      if (res.ok) {
        setReviewJobs((prev) => prev.filter((j) => j.id !== jobId));
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleManualSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setSubmitResult(null);
    try {
      const res = await fetch(`${apiUrl}/admin/jobs/submit`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Admin-Key": adminKey,
        },
        body: JSON.stringify({
          url: submitUrl,
          company_name: submitCompany || undefined,
          expected_cohort: submitCohort,
        }),
      });
      const data = await res.json();
      setSubmitResult(data);
      if (res.ok) {
        setSubmitUrl("");
        setSubmitCompany("");
      }
    } catch (e: any) {
      console.error(e);
      setSubmitResult({ error: e.message });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col justify-between bg-slate-50">
      <Header onOpenSubscribe={() => {}} />

      <main className="flex-1 max-w-6xl w-full mx-auto px-4 sm:px-6 py-10">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="p-1 rounded bg-slate-900 text-white font-mono text-xs">ADMIN</span>
              <h1 className="text-2xl font-bold text-slate-900">Platform Management Dashboard</h1>
            </div>
            <p className="text-xs text-slate-500">
              Manage the verification review queue, inspect connector health, and submit job URLs manually.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <Key className="w-4 h-4 text-slate-400" />
            <input
              type="password"
              value={adminKey}
              onChange={(e) => setAdminKey(e.target.value)}
              placeholder="Admin API Key"
              className="text-xs px-3 py-1.5 border border-slate-300 rounded-lg w-52 focus:outline-none focus:ring-2 focus:ring-slate-900"
            />
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex border-b border-slate-200 mb-6 gap-2">
          <button
            onClick={() => setActiveTab("review")}
            className={`pb-3 px-4 text-xs font-bold flex items-center gap-2 border-b-2 transition ${
              activeTab === "review"
                ? "border-slate-900 text-slate-900"
                : "border-transparent text-slate-500 hover:text-slate-800"
            }`}
          >
            <ShieldAlert className="w-4 h-4" />
            <span>Review Queue ({reviewJobs.length})</span>
          </button>

          <button
            onClick={() => setActiveTab("manual")}
            className={`pb-3 px-4 text-xs font-bold flex items-center gap-2 border-b-2 transition ${
              activeTab === "manual"
                ? "border-slate-900 text-slate-900"
                : "border-transparent text-slate-500 hover:text-slate-800"
            }`}
          >
            <PlusCircle className="w-4 h-4" />
            <span>Manual Ingest URL</span>
          </button>

          <button
            onClick={() => setActiveTab("health")}
            className={`pb-3 px-4 text-xs font-bold flex items-center gap-2 border-b-2 transition ${
              activeTab === "health"
                ? "border-slate-900 text-slate-900"
                : "border-transparent text-slate-500 hover:text-slate-800"
            }`}
          >
            <Activity className="w-4 h-4" />
            <span>Connector Health</span>
          </button>
        </div>

        {/* Tab 1: Review Queue */}
        {activeTab === "review" && (
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-sm font-bold text-slate-900">
                Jobs Requiring Human Alignment (Trust Score 60-79 or Ambiguous Eligibility)
              </h2>
              <button
                onClick={fetchReviewQueue}
                className="text-xs text-slate-600 hover:text-slate-900 flex items-center gap-1 font-semibold"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                Refresh
              </button>
            </div>

            {loadingReview ? (
              <div className="p-12 text-center text-xs text-slate-500">Loading review queue...</div>
            ) : reviewJobs.length > 0 ? (
              <div className="space-y-4">
                {reviewJobs.map((job) => (
                  <div key={job.id} className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-bold text-slate-900">{job.title}</span>
                        <span className="text-xs bg-slate-100 text-slate-700 px-2 py-0.5 rounded">
                          {job.company_name}
                        </span>
                        <span className="text-xs bg-amber-100 text-amber-800 font-bold px-2 py-0.5 rounded">
                          Score: {Math.round(job.trust_score)}%
                        </span>
                      </div>
                      <div className="text-xs text-slate-500">
                        {job.normalized_city} • {job.role_category} • {job.apply_url}
                      </div>
                      {job.rejection_reason && (
                        <div className="mt-2 text-xs text-amber-700 bg-amber-50 p-2 rounded border border-amber-200 font-mono">
                          Flag: {job.rejection_reason}
                        </div>
                      )}
                    </div>

                    <div className="flex items-center gap-2 shrink-0">
                      <button
                        onClick={() => handleAction(job.id, "approve")}
                        className="bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs px-3 py-1.5 rounded-lg flex items-center gap-1 shadow-sm transition"
                      >
                        <CheckCircle className="w-3.5 h-3.5" />
                        Approve
                      </button>
                      <button
                        onClick={() => handleAction(job.id, "reject")}
                        className="bg-red-600 hover:bg-red-700 text-white font-semibold text-xs px-3 py-1.5 rounded-lg flex items-center gap-1 shadow-sm transition"
                      >
                        <XCircle className="w-3.5 h-3.5" />
                        Reject
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-12 text-center bg-white rounded-xl border border-slate-200 text-xs text-slate-500">
                🎉 Zero items in the review queue. All listings are either cleanly verified or rejected.
              </div>
            )}
          </div>
        )}

        {/* Tab 2: Manual Submit */}
        {activeTab === "manual" && (
          <div className="max-w-2xl bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
            <h2 className="text-base font-bold text-slate-900 mb-1">
              Submit Job URL to Verification Pipeline
            </h2>
            <p className="text-xs text-slate-500 mb-6">
              Manually ingest a job URL. The platform will run all 8 stages: Liveness, Domain Trust, Scam Filter, Fresher Exp, Location, and Anti-Hallucination Extraction.
            </p>

            <form onSubmit={handleManualSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Official ATS or Career Apply URL
                </label>
                <input
                  type="url"
                  required
                  value={submitUrl}
                  onChange={(e) => setSubmitUrl(e.target.value)}
                  placeholder="https://boards.greenhouse.io/... or https://company.myworkdayjobs.com/..."
                  className="w-full px-3.5 py-2 text-xs border border-slate-300 rounded-lg focus:ring-2 focus:ring-slate-900 focus:outline-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Company Name (Optional)
                  </label>
                  <input
                    type="text"
                    value={submitCompany}
                    onChange={(e) => setSubmitCompany(e.target.value)}
                    placeholder="e.g. Razorpay, Postman"
                    className="w-full px-3.5 py-2 text-xs border border-slate-300 rounded-lg focus:ring-2 focus:ring-slate-900 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Target Cohort
                  </label>
                  <select
                    value={submitCohort}
                    onChange={(e) => setSubmitCohort(e.target.value)}
                    className="w-full px-3.5 py-2 text-xs border border-slate-300 rounded-lg focus:ring-2 focus:ring-slate-900 focus:outline-none bg-white"
                  >
                    <option value="2026">Cohort 2026</option>
                    <option value="2027">Cohort 2027</option>
                    <option value="2028">Cohort 2028</option>
                  </select>
                </div>
              </div>

              <button
                type="submit"
                disabled={submitting}
                className="py-2.5 px-4 bg-slate-900 hover:bg-slate-800 disabled:opacity-50 text-white font-semibold text-xs rounded-lg transition"
              >
                {submitting ? "Running 8-Stage Verification..." : "Run Pipeline Verification"}
              </button>
            </form>

            {submitResult && (
              <div className="mt-6 p-4 rounded-xl bg-slate-50 border border-slate-200 text-xs">
                <div className="font-bold text-slate-900 mb-2">Verification Outcome:</div>
                <pre className="p-3 bg-white border border-slate-200 rounded font-mono text-[11px] overflow-x-auto">
                  {JSON.stringify(submitResult, null, 2)}
                </pre>
              </div>
            )}
          </div>
        )}

        {/* Tab 3: Connector Health */}
        {activeTab === "health" && (
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-sm font-bold text-slate-900">
                ATS Connectors & Company Endpoints Monitor
              </h2>
              <button
                onClick={fetchHealth}
                className="text-xs text-slate-600 hover:text-slate-900 flex items-center gap-1 font-semibold"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                Refresh
              </button>
            </div>

            {loadingHealth ? (
              <div className="p-12 text-center text-xs text-slate-500">Loading connectors health...</div>
            ) : (
              <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-semibold">
                    <tr>
                      <th className="p-3">Company</th>
                      <th className="p-3">Connector ATS</th>
                      <th className="p-3">Status</th>
                      <th className="p-3">Last Polled</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {sourcesHealth.slice(0, 30).map((s) => (
                      <tr key={s.source_id} className="hover:bg-slate-50">
                        <td className="p-3 font-semibold text-slate-900">{s.company_name}</td>
                        <td className="p-3 uppercase font-mono text-[10px] text-slate-600">{s.source_type}</td>
                        <td className="p-3">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            s.status === "healthy"
                              ? "bg-emerald-100 text-emerald-800"
                              : "bg-red-100 text-red-800"
                          }`}>
                            {s.status}
                          </span>
                        </td>
                        <td className="p-3 text-slate-500">{s.last_polled_at || "Scheduled 02:00 IST"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
      </main>

      <Footer />
    </div>
  );
}
