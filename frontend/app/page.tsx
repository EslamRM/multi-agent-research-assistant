"use client";

import { motion } from "framer-motion";
import {
  ArrowRight,
  Bot,
  BrainCircuit,
  CheckCircle2,
  Cpu,
  FileText,
  Globe,
  Layers3,
  Search,
  ShieldCheck,
  Sparkles,
  Stars,
  Workflow,
} from "lucide-react";
import { useMemo, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";

const workflowStages = [
  { label: "Planning", detail: "Decomposes the research objective", progress: 100 },
  { label: "Research", detail: "Aggregates evidence and sources", progress: 80 },
  { label: "Synthesis", detail: "Finds contradictions and gaps", progress: 62 },
  { label: "Reporting", detail: "Formats the final answer", progress: 48 },
];

const sources = [
  { title: "AI coding efficiency benchmarks", domain: "arxiv.org", type: "Paper" },
  { title: "Developer workflows in LLM-assisted teams", domain: "research.google", type: "Report" },
  { title: "Engineering productivity review", domain: "nature.com", type: "Journal" },
];

const evidence = [
  {
    claim: "AI tools improve repetitive development work most strongly.",
    confidence: 0.88,
    note: "Evidence is strongest for boilerplate generation and scaffold creation.",
  },
  {
    claim: "Complex reasoning still depends on human oversight.",
    confidence: 0.79,
    note: "Large productivity gains are not universal across architecture-heavy tasks.",
  },
  {
    claim: "Team maturity and workflow design modulate impact.",
    confidence: 0.74,
    note: "Experienced teams benefit more from structured prompting and validation loops.",
  },
];

const reportSections = [
  "AI coding assistants are most useful for repetitive, low-context tasks where they can reduce friction and speed iteration.",
  "The strongest observed gains appear in code generation, boilerplate creation, refactoring suggestions, and test scaffolding.",
  "For architecture, debugging, and ambiguous multi-step work, performance remains highly dependent on developer skill and review quality.",
  "The best outcomes come from structured prompting, retrieval-grounded workflows, and explicit verification steps.",
];

export default function Home() {
  const [question, setQuestion] = useState(
    "Compare the impact of AI coding assistants on software engineering productivity.",
  );
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  const completion = useMemo(() => {
    return workflowStages.reduce((total, stage) => total + stage.progress, 0) / workflowStages.length;
  }, []);

  const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

  const handleStartResearch = async () => {
    if (!question.trim()) {
      setStatusMessage("Please enter a research question.");
      return;
    }

    setIsSubmitting(true);
    setStatusMessage("Submitting research request...");

    try {
      const response = await fetch(`${apiBaseUrl}/api/v1/research`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question,
          max_sources: 5,
          research_mode: "standard",
        }),
      });

      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`);
      }

      const data = await response.json();
      setStatusMessage(
        data?.report?.executive_summary ?? `Research started successfully (id: ${data.research_id ?? "unknown"}).`,
      );
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unknown error";
      setStatusMessage(`Research request failed: ${message}`);
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
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-cyan-400 via-indigo-500 to-violet-500 shadow-[0_12px_40px_rgba(99,102,241,0.5)]">
              <Bot className="h-5 w-5" />
            </div>
            <div>
              <p className="text-xs uppercase tracking-[0.22em] text-cyan-300">Research OS</p>
              <h1 className="text-sm font-medium text-white">Multi-Agent Research Assistant</h1>
            </div>
          </div>

          <div className="hidden items-center gap-2 sm:flex">
            <Button variant="ghost" size="sm" className="text-slate-200">
              Workspace
            </Button>
            <Button variant="secondary" size="sm" className="bg-white/10 text-white">
              New research
            </Button>
          </div>
        </header>

        <section className="grid gap-6 lg:grid-cols-[1.4fr_0.9fr]">
          <motion.div
            initial={{ opacity: 0, y: 18 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.45 }}
            className="rounded-[28px] border border-white/10 bg-white/[0.04] p-4 shadow-[0_30px_80px_rgba(15,23,42,0.55)] backdrop-blur-2xl sm:p-6"
          >
            <div className="mb-5 flex items-center justify-between">
              <div className="flex items-center gap-2 text-sm text-cyan-300">
                <Sparkles className="h-4 w-4" />
                Research prompt
              </div>
              <div className="flex items-center gap-2 rounded-full border border-emerald-400/30 bg-emerald-500/10 px-2.5 py-1 text-[11px] font-medium text-emerald-300">
                <CheckCircle2 className="h-3.5 w-3.5" />
                Live
              </div>
            </div>

            <div className="rounded-2xl border border-white/10 bg-slate-950/70 p-3 shadow-inner shadow-cyan-500/5">
              <textarea
                value={question}
                onChange={(event) => setQuestion(event.target.value)}
                rows={5}
                className="w-full resize-none border-0 bg-transparent text-base leading-7 text-slate-100 outline-none placeholder:text-slate-500"
                placeholder="Ask a research question..."
              />
            </div>

            <div className="mt-5 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex flex-wrap items-center gap-2 text-xs text-slate-400">
                <span className="rounded-full border border-white/10 bg-white/5 px-2 py-1">Grounded</span>
                <span className="rounded-full border border-white/10 bg-white/5 px-2 py-1">Verified sources</span>
                <span className="rounded-full border border-white/10 bg-white/5 px-2 py-1">Multi-agent</span>
              </div>

              <Button
                size="lg"
                disabled={isSubmitting}
                onClick={handleStartResearch}
                className="bg-gradient-to-r from-cyan-400 via-indigo-500 to-violet-500 text-white shadow-[0_18px_45px_rgba(99,102,241,0.6)] hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-70"
              >
                {isSubmitting ? "Running..." : "Start research"}
                <ArrowRight className="h-4 w-4" />
              </Button>
            </div>

            {statusMessage ? (
              <div className="mt-4 rounded-2xl border border-cyan-400/20 bg-cyan-500/5 px-3 py-2 text-sm text-cyan-100">
                {statusMessage}
              </div>
            ) : null}

            <div className="mt-6 grid gap-4 md:grid-cols-3">
              <div className="rounded-2xl border border-white/10 bg-[#0c1325]/80 p-4">
                <div className="mb-2 flex items-center gap-2 text-cyan-300">
                  <BrainCircuit className="h-4 w-4" />
                  Agents
                </div>
                <p className="text-3xl font-semibold text-white">4</p>
                <p className="mt-1 text-sm text-slate-400">Planner, researcher, summarizer, reporter</p>
              </div>

              <div className="rounded-2xl border border-white/10 bg-[#0c1325]/80 p-4">
                <div className="mb-2 flex items-center gap-2 text-violet-300">
                  <Layers3 className="h-4 w-4" />
                  Evidence
                </div>
                <p className="text-3xl font-semibold text-white">27</p>
                <p className="mt-1 text-sm text-slate-400">Critical findings and supporting claims</p>
              </div>

              <div className="rounded-2xl border border-white/10 bg-[#0c1325]/80 p-4">
                <div className="mb-2 flex items-center gap-2 text-emerald-300">
                  <ShieldCheck className="h-4 w-4" />
                  Confidence
                </div>
                <p className="text-3xl font-semibold text-white">82%</p>
                <p className="mt-1 text-sm text-slate-400">Based on retrieval and validation score</p>
              </div>
            </div>
          </motion.div>

          <motion.aside
            initial={{ opacity: 0, x: 18 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.45, delay: 0.06 }}
            className="rounded-[28px] border border-white/10 bg-white/[0.04] p-4 backdrop-blur-2xl sm:p-5"
          >
            <div className="mb-4 flex items-center justify-between">
              <div className="flex items-center gap-2 text-sm text-violet-300">
                <Workflow className="h-4 w-4" />
                Execution flow
              </div>
              <div className="text-xs text-slate-400">{Math.round(completion)}%</div>
            </div>

            <div className="space-y-4">
              {workflowStages.map((stage, index) => (
                <div key={stage.label} className="rounded-2xl border border-white/10 bg-slate-950/60 p-3">
                  <div className="mb-2 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className={`flex h-7 w-7 items-center justify-center rounded-full ${index === 0 ? "bg-cyan-500/20 text-cyan-300" : "bg-white/5 text-slate-300"}`}>
                        {index + 1}
                      </div>
                      <span className="font-medium text-white">{stage.label}</span>
                    </div>
                    <span className="text-[11px] text-slate-400">{stage.progress}%</span>
                  </div>
                  <p className="mb-2 text-xs text-slate-400">{stage.detail}</p>
                  <Progress value={stage.progress} />
                </div>
              ))}
            </div>
          </motion.aside>
        </section>

        <section className="mt-8 grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
          <Card className="overflow-hidden border-white/10 bg-white/[0.04]">
            <CardHeader className="flex flex-row items-center justify-between border-b border-white/10 pb-4">
              <div className="flex items-center gap-2">
                <FileText className="h-4 w-4 text-cyan-300" />
                <CardTitle>Research Report</CardTitle>
              </div>
              <div className="rounded-full border border-cyan-400/30 bg-cyan-500/10 px-2.5 py-1 text-[11px] text-cyan-300">
                Final draft
              </div>
            </CardHeader>
            <CardContent className="pt-5">
              <div className="mb-4 flex items-center gap-2 text-xs uppercase tracking-[0.20em] text-slate-400">
                <Cpu className="h-3.5 w-3.5" />
                Executive summary
              </div>

              <h2 className="text-2xl font-semibold text-white sm:text-3xl">
                AI coding assistants increase productivity most when paired with structured human review.
              </h2>

              <div className="mt-5 space-y-4 text-[15px] leading-7 text-slate-300">
                {reportSections.map((paragraph) => (
                  <p key={paragraph}>{paragraph}</p>
                ))}
              </div>

              <div className="mt-6 rounded-2xl border border-indigo-400/20 bg-gradient-to-r from-indigo-500/10 via-sky-600/10 to-cyan-500/10 p-4">
                <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Key conclusion</p>
                <p className="mt-2 text-base text-slate-100">
                  The highest-value use case is not autonomous coding, but collaborative acceleration with verification loops.
                </p>
              </div>
            </CardContent>
          </Card>

          <div className="space-y-6">
            <Card className="border-white/10 bg-white/[0.04]">
              <CardHeader className="border-b border-white/10 pb-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Search className="h-4 w-4 text-violet-300" />
                    <CardTitle>Sources</CardTitle>
                  </div>
                  <span className="text-xs text-slate-400">{sources.length} cited</span>
                </div>
              </CardHeader>
              <CardContent className="pt-4">
                <div className="space-y-3">
                  {sources.map((source) => (
                    <div key={source.title} className="rounded-2xl border border-white/10 bg-slate-950/60 p-3">
                      <div className="flex items-start justify-between gap-4">
                        <div>
                          <p className="font-medium text-white">{source.title}</p>
                          <p className="mt-1 text-xs text-slate-400">{source.domain}</p>
                        </div>
                        <span className="rounded-full border border-white/10 bg-white/5 px-2 py-1 text-[10px] uppercase tracking-[0.18em] text-slate-300">
                          {source.type}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card className="border-white/10 bg-white/[0.04]">
              <CardHeader className="border-b border-white/10 pb-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Stars className="h-4 w-4 text-amber-300" />
                    <CardTitle>Evidence</CardTitle>
                  </div>
                  <span className="text-xs text-slate-400">Validated</span>
                </div>
              </CardHeader>
              <CardContent className="pt-4">
                <div className="space-y-4">
                  {evidence.map((item) => (
                    <div key={item.claim} className="rounded-2xl border border-white/10 bg-slate-950/60 p-3">
                      <div className="mb-2 flex items-center justify-between gap-3">
                        <p className="text-sm text-slate-100">{item.claim}</p>
                        <span className="rounded-full bg-emerald-500/10 px-2 py-1 text-[10px] font-medium text-emerald-300">
                          {(item.confidence * 100).toFixed(0)}%
                        </span>
                      </div>
                      <p className="text-xs leading-6 text-slate-400">{item.note}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </section>

        <footer className="mt-8 flex items-center justify-between rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3 text-sm text-slate-400">
          <div className="flex items-center gap-2">
            <Globe className="h-4 w-4 text-cyan-300" />
            Grounded AI research system
          </div>
          <div className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-emerald-400" />
            All systems online
          </div>
        </footer>
      </div>
    </main>
  );
}
