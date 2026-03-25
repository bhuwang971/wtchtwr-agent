import { useEffect, useMemo, useState } from "react";

import { fetchAiMetrics, type AiMetricsResponse, type InterviewMetricsPack } from "@/lib/api";

const statCard =
  "rounded-3xl border border-slate-200 bg-white/90 p-5 shadow-[0_16px_40px_rgba(15,23,42,0.08)]";

const pct = (value?: number) => (typeof value === "number" ? `${value.toFixed(2)}%` : "n/a");
const seconds = (value?: number) => (typeof value === "number" ? `${value.toFixed(2)}s` : "n/a");

const statusTone = (ok?: boolean) =>
  ok ? "bg-emerald-50 text-emerald-700 border-emerald-200" : "bg-amber-50 text-amber-700 border-amber-200";

const packTitle = (name: string) => {
  if (name === "benchmarks.local") return "Tuned Regression Pack";
  if (name === "benchmarks.holdout") return "Holdout Pack";
  if (name === "benchmarks.adversarial") return "Adversarial Pack";
  return name;
};

const PackCard = ({ pack }: { pack: InterviewMetricsPack }) => (
  <section className={statCard}>
    <div className="flex flex-wrap items-start justify-between gap-3">
      <div>
        <div className="text-xs font-semibold uppercase tracking-[0.22em] text-primary-500">{packTitle(pack.pack)}</div>
        <h3 className="mt-1 text-xl font-semibold text-slate-800">{pack.benchmark_report}</h3>
        <p className="mt-1 text-sm text-slate-500">Generated {new Date(pack.generated_at).toLocaleString()}</p>
      </div>
      <div className="rounded-full bg-primary-50 px-3 py-1 text-xs font-semibold text-primary-600">
        {pct(pack.headline_metrics.case_pass_rate)} case pass rate
      </div>
    </div>

    <div className="mt-5 grid gap-3 md:grid-cols-4">
      <div className="rounded-2xl bg-slate-50 px-4 py-3">
        <div className="text-xs uppercase tracking-wide text-slate-500">Overall</div>
        <div className="mt-1 text-lg font-semibold text-slate-800">{pct(pack.pipeline_metrics.overall_pass_rate)}</div>
      </div>
      <div className="rounded-2xl bg-slate-50 px-4 py-3">
        <div className="text-xs uppercase tracking-wide text-slate-500">SQL</div>
        <div className="mt-1 text-lg font-semibold text-slate-800">{pct(pack.pipeline_metrics.sql_pass_rate)}</div>
      </div>
      <div className="rounded-2xl bg-slate-50 px-4 py-3">
        <div className="text-xs uppercase tracking-wide text-slate-500">RAG</div>
        <div className="mt-1 text-lg font-semibold text-slate-800">{pct(pack.pipeline_metrics.rag_pass_rate)}</div>
      </div>
      <div className="rounded-2xl bg-slate-50 px-4 py-3">
        <div className="text-xs uppercase tracking-wide text-slate-500">Hybrid</div>
        <div className="mt-1 text-lg font-semibold text-slate-800">{pct(pack.pipeline_metrics.hybrid_pass_rate)}</div>
      </div>
    </div>

    <div className="mt-5 grid gap-3 md:grid-cols-3">
      <div className="rounded-2xl border border-slate-200 px-4 py-3">
        <div className="text-xs uppercase tracking-wide text-slate-500">Assertion Accuracy</div>
        <div className="mt-1 text-base font-semibold text-slate-800">
          {pct(pack.headline_metrics.assertion_pass_rate)}
        </div>
      </div>
      <div className="rounded-2xl border border-slate-200 px-4 py-3">
        <div className="text-xs uppercase tracking-wide text-slate-500">P50 Latency</div>
        <div className="mt-1 text-base font-semibold text-slate-800">{seconds(pack.performance_metrics.p50_latency_s)}</div>
      </div>
      <div className="rounded-2xl border border-slate-200 px-4 py-3">
        <div className="text-xs uppercase tracking-wide text-slate-500">P95 Latency</div>
        <div className="mt-1 text-base font-semibold text-slate-800">{seconds(pack.performance_metrics.p95_latency_s)}</div>
      </div>
    </div>

    <div className="mt-5 grid gap-4 lg:grid-cols-2">
      <div className="rounded-2xl bg-slate-50/80 p-4">
        <div className="text-sm font-semibold text-slate-800">Strongest Categories</div>
        <div className="mt-3 space-y-2">
          {pack.strongest_categories.map((item) => (
            <div key={`${pack.pack}-strong-${item.name}`} className="flex items-center justify-between rounded-xl bg-white px-3 py-2">
              <span className="text-sm text-slate-700">{item.name}</span>
              <span className="text-xs font-semibold text-emerald-700">{pct(item.pass_rate)}</span>
            </div>
          ))}
        </div>
      </div>
      <div className="rounded-2xl bg-slate-50/80 p-4">
        <div className="text-sm font-semibold text-slate-800">Recent Regressions / Failed Cases</div>
        <div className="mt-3 space-y-2">
          {pack.failed_case_ids.length === 0 && (
            <div className="rounded-xl bg-white px-3 py-2 text-sm text-slate-600">No failed cases in this run.</div>
          )}
          {pack.failed_case_ids.slice(0, 6).map((caseId) => (
            <div key={`${pack.pack}-fail-${caseId}`} className="rounded-xl bg-white px-3 py-2 text-sm text-slate-700">
              {caseId}
            </div>
          ))}
        </div>
      </div>
    </div>
  </section>
);

export const AiMetricsPage = (): JSX.Element => {
  const [data, setData] = useState<AiMetricsResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const payload = await fetchAiMetrics();
        if (!mounted) return;
        setData(payload);
      } catch (err) {
        if (!mounted) return;
        setError(err instanceof Error ? err.message : "Unable to load AI metrics.");
      } finally {
        if (mounted) setLoading(false);
      }
    })();
    return () => {
      mounted = false;
    };
  }, []);

  const packs = useMemo(() => {
    if (!data?.packs) return [];
    return Object.values(data.packs).sort((a, b) => b.generated_at.localeCompare(a.generated_at));
  }, [data]);

  if (loading) {
    return <div className="rounded-3xl border border-slate-200 bg-white/90 p-6 text-sm text-slate-600">Loading AI metrics…</div>;
  }

  if (error) {
    return <div className="rounded-3xl border border-rose-200 bg-rose-50 p-6 text-sm text-rose-700">{error}</div>;
  }

  return (
    <div className="h-full overflow-y-auto pr-2 space-y-6">
      <section className={statCard}>
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.22em] text-primary-500">AI Observability</div>
            <h1 className="mt-1 text-3xl font-semibold text-slate-800">System health, benchmark quality, and interview metrics</h1>
            <p className="mt-2 max-w-3xl text-sm leading-relaxed text-slate-600">
              This page makes the agent inspectable: component readiness, tuned vs holdout performance, SQL/RAG/hybrid accuracy,
              and latency tail behavior in one place.
            </p>
          </div>
          <div className={`rounded-full border px-4 py-2 text-sm font-semibold ${statusTone(data?.health?.status === "ready")}`}>
            Backend status: {data?.health?.status || "unknown"}
          </div>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
        {Object.entries(data?.health?.components || {}).map(([name, component]) => (
          <div key={name} className={statCard}>
            <div className="flex items-center justify-between gap-2">
              <div className="text-sm font-semibold capitalize text-slate-800">{name}</div>
              <div className={`rounded-full border px-2.5 py-1 text-xs font-semibold ${statusTone(component.ok)}`}>
                {component.ok ? "ready" : "degraded"}
              </div>
            </div>
            <p className="mt-3 text-sm leading-relaxed text-slate-600">{component.detail}</p>
          </div>
        ))}
      </section>

      {packs.map((pack) => (
        <PackCard key={`${pack.pack}-${pack.generated_at}`} pack={pack} />
      ))}

      {packs.length === 0 && (
        <div className="rounded-3xl border border-slate-200 bg-white/90 p-6 text-sm text-slate-600">
          No benchmark reports were found yet. Run the benchmark scripts and refresh this page.
        </div>
      )}
    </div>
  );
};
