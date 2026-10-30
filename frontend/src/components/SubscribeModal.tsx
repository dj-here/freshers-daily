"use client";

import React, { useState } from "react";
import { X, Mail, CheckCircle2, AlertCircle } from "lucide-react";

interface SubscribeModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const SubscribeModal: React.FC<SubscribeModalProps> = ({ isOpen, onClose }) => {
  const [email, setEmail] = useState("");
  const [cohort, setCohort] = useState("2027");
  const [loading, setLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setSuccessMessage(null);
    setErrorMessage(null);

    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "/api";

    try {
      const resp = await fetch(`${apiUrl}/subscriptions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, cohort }),
      });
      const data = await resp.json();
      if (!resp.ok) {
        throw new Error(data.detail || "Subscription failed");
      }
      setSuccessMessage(data.message || "Subscribed successfully!");
      setEmail("");
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to subscribe. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="relative w-full max-w-md bg-white rounded-2xl shadow-2xl border border-slate-200 overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-lg bg-emerald-100 text-emerald-700">
              <Mail className="w-4 h-4" />
            </span>
            <h3 className="font-bold text-slate-900 text-base">Get Verified 6 AM Digest</h3>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          <p className="text-xs text-slate-600 mb-4 leading-relaxed">
            Receive exactly 5 verified, high-quality India software job openings for your graduating batch
            delivered directly to your inbox every morning at 06:00 AM IST. Zero spam, one-click unsubscribe.
          </p>

          {successMessage && (
            <div className="mb-4 p-3 rounded-lg bg-emerald-50 border border-emerald-200 flex items-center gap-2 text-xs text-emerald-800">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
              <span>{successMessage}</span>
            </div>
          )}

          {errorMessage && (
            <div className="mb-4 p-3 rounded-lg bg-red-50 border border-red-200 flex items-center gap-2 text-xs text-red-800">
              <AlertCircle className="w-4 h-4 text-red-600 shrink-0" />
              <span>{errorMessage}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Your Email Address
              </label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@university.edu or gmail.com"
                className="w-full px-3.5 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Select Your Cohort
              </label>
              <select
                value={cohort}
                onChange={(e) => setCohort(e.target.value)}
                className="w-full px-3.5 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:outline-none bg-white"
              >
                <option value="2026">Cohort 2026 (Passouts - Full-Time Fresher)</option>
                <option value="2027">Cohort 2027 (Final Year - Jobs + PPO Internships)</option>
                <option value="2028">Cohort 2028 (Pre-Final - Summer Internships)</option>
                <option value="all">All Cohorts (Aggregated)</option>
              </select>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 px-4 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white font-semibold text-xs rounded-lg shadow-sm transition"
            >
              {loading ? "Subscribing..." : "Confirm Daily Subscription"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};
