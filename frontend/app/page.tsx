"use client";

import { motion } from "framer-motion";
import {
  ArrowRight, Bot, BrainCircuit, CheckCircle2, Cpu, FileText, Globe,
  Layers3, Search, ShieldCheck, Sparkles, Stars, Workflow, AlertTriangle, RefreshCw
} from "lucide-react";
import { useMemo, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";

type Source = { id?: string; title: string; url?: string | null; source_type?: string; metadata?: { [key: string]: unknown } };
type Evidence = { id?: string; claim: string; evidence: string; confidence: number; source_title?: string; source_url?: string | null };
type Report = {
  title: string; executive_summary: string; key_findings: string[];
  analysis: string; limitations: string[]; sources: string[]; conclusion: string; confidence: number;
};
type ResearchResponse = {
  research_id: string; status: "completed" | "failed" | "in_progress";
  report?: Report | null; sources?: Source[]; error?: string | null;
  metadata?: Record<string, unknown>;
};

const initialStages = [
  { label: "Planning", detail: "Decomposes the research objective", progress: 0 },
  { label: "Research", detail: "Aggregates evidence and sources", progress: 0 },
  { label: "Synthesis", detail: "Validates evidence and contradictions", progress: 0 },
  { label: "Reporting", detail: "Builds the grounded final answer", progress: 0 },
];

export default function Home() {
  const [question, setQuestion] = useState("Compare between the latest AI models");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState<ResearchResponse | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  const isCompleted = result?.status === "completed" && !!result.report;
  const isFailed = result?.status === "failed";
  const sources = result?.sources ?? [];
  const evidence: Evidence[] = Array.isArray(result?.metadata?.evidence)
    ? result!.metadata!.evidence as Evidence[]
    : [];

  const stages = useMemo(() => {
    if (isCompleted) return initialStages.map((s) => ({ ...s, progress: 100 }));
    if (isFailed) return initialStages.map((s, i) => ({ ...s, progress: i < 2 ? 100 : 0 }));
    return initialStages;
  }, [isCompleted, isFailed]);

  const completion = useMemo(
    () => stages.reduce((total, stage) => total + stage.progress, 0) / stages.length,
    [stages],
  );

  const handleStartResearch = async () => {
    if (!question.trim()) {
      setStatusMessage("Please enter a research question.");
      return;
    }

    setIsSubmitting(true);
    setResult(null);
    setStatusMessage("Running planner, researcher, validation, and reporting agents...");

    try {
      const response = await fetch(`${apiBaseUrl}/api/v1/research`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, max_sources: 5, research_mode: "standard" }),
      });

      const data: ResearchResponse = await response.json();

      if (!response.ok) {
        throw new Error(data?.error || `Request failed with status ${response.status}`);
      }

      setResult(data);
      if (data.status === "failed") {
        setStatusMessage(data.error || "Research failed because the evidence quality gate was not satisfied.");
      } else {
        setStatusMessage("Research completed successfully.");
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unknown error";
      setStatusMessage(`Research request failed: ${message}`);
      setResult({ research_id: "", status: "failed", error: message, sources: [] });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className="min-h-screen bg-[#050816] text-slate-100">
      <div className="absolute inset-0 -z-10 bg-[radial-gradient(circle_at_top_left,_rgba(34,211,238,0.18),_transparent_20%),radial-gradient(circle_at_top_right,_rgba(168,85,247,0.16),_transparent_24%),linear-gradient(180deg,_#020817_0%,_#0a1020_50%,_#040816_100%)]" />
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <header className="mb-8 flex items-center justify-between rounded-full border border-white/10 bg-white/5 px-4 py-3 backdrop-blur-xl shadow-[0_20px_60px_rgba(15,23,42,0.4)]">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-cyan-400 via-indigo-500 to-violet-500">
              <Bot className="h-5 w-5" />
            </div>
            <div>
              <p className="text-xs uppercase tracking-[0.22em] text-cyan-300">Research OS</p>
              <h1 className="text-sm font-medium text-white">Multi-Agent Research Assistant</h1>
            </div>
          </div>
          <Button variant="secondary" size="sm" onClick={() => { setResult(null); setStatusMessage(null); }} className="bg-white/10 text-white">
            New research
          </Button>
        </header>

        <section className="grid gap-6 lg:grid-cols-[1.4fr_0.9fr]">
          <motion.div initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} className="rounded-[28px] border border-white/10 bg-white/[0.04] p-4 backdrop-blur-2xl sm:p-6">
            <div className="mb-5 flex items-center justify-between">
              <div className="flex items-center gap-2 text-sm text-cyan-300"><Sparkles className="h-4 w-4" />Research prompt</div>
              <div className="flex items-center gap-2 rounded-full border border-emerald-400/30 bg-emerald-500/10 px-2.5 py-1 text-[11px] text-emerald-300">
                <CheckCircle2 className="h-3.5 w-3.5" />Live
              </div>
            </div>

            <div className="rounded-2xl border border-white/10 bg-slate-950/70 p-3">
              <textarea value={question} onChange={(e) => setQuestion(e.target.value)} rows={5}
                className="w-full resize-none border-0 bg-transparent text-base leading-7 text-slate-100 outline-none placeholder:text-slate-500"
                placeholder="Ask a research question..." />
            </div>

            <div className="mt-5 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex flex-wrap items-center gap-2 text-xs text-slate-400">
                <span className="rounded-full border border-white/10 bg-white/5 px-2 py-1">Grounded</span>
                <span className="rounded-full border border-white/10 bg-white/5 px-2 py-1">Verified sources</span>
                <span className="rounded-full border border-white/10 bg-white/5 px-2 py-1">Multi-agent</span>
              </div>
              <Button size="lg" disabled={isSubmitting} onClick={handleStartResearch}
                className="bg-gradient-to-r from-cyan-400 via-indigo-500 to-violet-500 text-white">
                {isSubmitting ? <><RefreshCw className="h-4 w-4 animate-spin" />Running...</> : <>Start research<ArrowRight className="h-4 w-4" /></>}
              </Button>
            </div>

            {statusMessage && (
              <div className={`mt-4 rounded-2xl border px-3 py-3 text-sm ${isFailed ? "border-red-400/20 bg-red-500/10 text-red-100" : "border-cyan-400/20 bg-cyan-500/5 text-cyan-100"}`}>
                {statusMessage}
              </div>
            )}

            <div className="mt-6 grid gap-4 md:grid-cols-3">
              <div className="rounded-2xl border border-white/10 bg-[#0c1325]/80 p-4"><div className="mb-2 flex items-center gap-2 text-cyan-300"><BrainCircuit className="h-4 w-4" />Agents</div><p className="text-3xl font-semibold text-white">4</p><p className="mt-1 text-sm text-slate-400">Planner, researcher, summarizer, reporter</p></div>
              <div className="rounded-2xl border border-white/10 bg-[#0c1325]/80 p-4"><div className="mb-2 flex items-center gap-2 text-violet-300"><Layers3 className="h-4 w-4" />Evidence</div><p className="text-3xl font-semibold text-white">{sources.length}</p><p className="mt-1 text-sm text-slate-400">Retrieved sources</p></div>
              <div className="rounded-2xl border border-white/10 bg-[#0c1325]/80 p-4"><div className="mb-2 flex items-center gap-2 text-emerald-300"><ShieldCheck className="h-4 w-4" />Confidence</div><p className="text-3xl font-semibold text-white">{result?.report ? `${Math.round(result.report.confidence * 100)}%` : "—"}</p><p className="mt-1 text-sm text-slate-400">Grounded report confidence</p></div>
            </div>
          </motion.div>

          <motion.aside initial={{ opacity: 0, x: 18 }} animate={{ opacity: 1, x: 0 }} className="rounded-[28px] border border-white/10 bg-white/[0.04] p-4 backdrop-blur-2xl sm:p-5">
            <div className="mb-4 flex items-center justify-between"><div className="flex items-center gap-2 text-sm text-violet-300"><Workflow className="h-4 w-4" />Execution flow</div><div className="text-xs text-slate-400">{Math.round(completion)}%</div></div>
            <div className="space-y-4">
              {stages.map((stage, index) => (
                <div key={stage.label} className="rounded-2xl border border-white/10 bg-slate-950/60 p-3">
                  <div className="mb-2 flex items-center justify-between"><div className="flex items-center gap-2"><div className="flex h-7 w-7 items-center justify-center rounded-full bg-white/5 text-slate-300">{index + 1}</div><span className="font-medium text-white">{stage.label}</span></div><span className="text-[11px] text-slate-400">{stage.progress}%</span></div>
                  <p className="mb-2 text-xs text-slate-400">{stage.detail}</p><Progress value={stage.progress} />
                </div>
              ))}
            </div>
          </motion.aside>
        </section>

        {isFailed ? (
          <section className="mt-8">
            <Card className="border-red-400/20 bg-red-500/[0.05]">
              <CardContent className="p-6">
                <div className="flex items-start gap-3">
                  <AlertTriangle className="mt-1 h-5 w-5 text-red-300" />
                  <div>
                    <h2 className="text-xl font-semibold text-white">Research failed</h2>
                    <p className="mt-2 text-slate-300">{result?.error || "No usable evidence was retrieved."}</p>
                    <p className="mt-3 text-sm text-slate-500">The UI will not display a report when the backend reports failure.</p>
                    <Button className="mt-4" onClick={handleStartResearch} disabled={isSubmitting}>Retry research</Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </section>
        ) : isCompleted ? (
          <section className="mt-8 grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
            <Card className="overflow-hidden border-white/10 bg-white/[0.04]">
              <CardHeader className="flex flex-row items-center justify-between border-b border-white/10 pb-4">
                <div className="flex items-center gap-2"><FileText className="h-4 w-4 text-cyan-300" /><CardTitle>Research Report</CardTitle></div>
                <div className="rounded-full border border-emerald-400/30 bg-emerald-500/10 px-2.5 py-1 text-[11px] text-emerald-300">Grounded report</div>
              </CardHeader>
              <CardContent className="pt-5">
                <div className="mb-4 flex items-center gap-2 text-xs uppercase tracking-[0.20em] text-slate-400"><Cpu className="h-3.5 w-3.5" />Executive summary</div>
                <h2 className="text-2xl font-semibold text-white sm:text-3xl">{result!.report!.title}</h2>
                <p className="mt-5 text-[15px] leading-7 text-slate-300">{result!.report!.executive_summary}</p>
                <div className="mt-6 space-y-3">{result!.report!.key_findings.map((item) => <div key={item} className="rounded-xl border border-white/10 bg-slate-950/50 p-3 text-sm text-slate-200">{item}</div>)}</div>
                <p className="mt-5 text-[15px] leading-7 text-slate-300">{result!.report!.analysis}</p>
                <div className="mt-6 rounded-2xl border border-indigo-400/20 bg-indigo-500/10 p-4"><p className="text-xs uppercase tracking-[0.18em] text-slate-400">Conclusion</p><p className="mt-2 text-base text-slate-100">{result!.report!.conclusion}</p></div>
                {result!.report!.limitations.length > 0 && <div className="mt-5"><p className="text-xs uppercase tracking-[0.18em] text-slate-400">Limitations</p>{result!.report!.limitations.map((item) => <p key={item} className="mt-2 text-sm text-slate-400">• {item}</p>)}</div>}
              </CardContent>
            </Card>

            <div className="space-y-6">
              <Card className="border-white/10 bg-white/[0.04]">
                <CardHeader className="border-b border-white/10 pb-4"><div className="flex items-center justify-between"><div className="flex items-center gap-2"><Search className="h-4 w-4 text-violet-300" /><CardTitle>Sources</CardTitle></div><span className="text-xs text-slate-400">{sources.length} retrieved</span></div></CardHeader>
                <CardContent className="pt-4"><div className="space-y-3">{sources.map((source) => <div key={source.id || source.url || source.title} className="rounded-2xl border border-white/10 bg-slate-950/60 p-3"><p className="font-medium text-white">{source.title}</p><p className="mt-1 text-xs text-slate-400">{source.source_type || "web"}</p>{source.url && <a href={source.url} target="_blank" rel="noreferrer" className="mt-2 block truncate text-xs text-cyan-300 hover:underline">{source.url}</a>}</div>)}</div></CardContent>
              </Card>
            </div>
          </section>
        ) : (
          <section className="mt-8 rounded-2xl border border-white/10 bg-white/[0.04] p-8 text-center text-slate-400">Start a research run to see the grounded report.</section>
        )}

        <footer className="mt-8 flex items-center justify-between rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3 text-sm text-slate-400">
          <div className="flex items-center gap-2"><Globe className="h-4 w-4 text-cyan-300" />Grounded AI research system</div>
          <div className="flex items-center gap-2"><span className="h-2 w-2 rounded-full bg-emerald-400" />All systems online</div>
        </footer>
      </div>
    </main>
  );
}
