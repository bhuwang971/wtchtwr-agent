import { useEffect, useMemo, useState } from "react";

import { fetchAiMetrics, type AiMetricsResponse, type InterviewMetricsPack } from "@/lib/api";

const statCard =
  "rounded-3xl border border-slate-200 bg-white/90 p-5 shadow-[0_16px_40px_rgba(15,23,42,0.08)]";

const softCard = "rounded-2xl border border-slate-200 bg-slate-50/80 p-4";

const pct = (value?: number) => (typeof value === "number" ? `${value.toFixed(2)}%` : "n/a");
const seconds = (value?: number) => (typeof value === "number" ? `${value.toFixed(2)}s` : "n/a");
const signed = (value?: number) =>
  typeof value === "number" ? `${value > 0 ? "+" : ""}${value.toFixed(2)}` : "n/a";

const statusTone = (ok?: boolean) =>
  ok ? "bg-emerald-50 text-emerald-700 border-emerald-200" : "bg-amber-50 text-amber-700 border-amber-200";

const rankTone = (index: number) => {
  if (index === 0) return "bg-emerald-50 text-emerald-700 border-emerald-200";
  if (index === 1) return "bg-sky-50 text-sky-700 border-sky-200";
  return "bg-slate-50 text-slate-700 border-slate-200";
};

const packTitle = (name: string) => {
  if (name === "benchmarks.local") return "Tuned Regression Pack";
  if (name === "benchmarks.holdout") return "Holdout Pack";
  if (name === "benchmarks.adversarial") return "Adversarial Pack";
  return name;
};

const MetricTile = ({ label, value, hint }: { label: string; value: string; hint?: string }) => (
  <div className={softCard}>
    <div className="text-xs uppercase tracking-wide text-slate-500">{label}</div>
    <div className="mt-1 text-xl font-semibold text-slate-800">{value}</div>
    {hint && <div className="mt-1 text-xs text-slate-500">{hint}</div>}
  </div>
);

const BreakdownList = ({
  title,
  items,
}: {
  title: string;
  items: Array<{ name: string; pass_rate: number; passed: number; total: number }>;
}) => (
  <div className={softCard}>
    <div className="text-sm font-semibold text-slate-800">{title}</div>
    <div className="mt-3 space-y-2">
      {items.length === 0 && <div className="rounded-xl bg-white px-3 py-2 text-sm text-slate-500">No data yet.</div>}
      {items.map((item) => (
        <div key={`${title}-${item.name}`} className="flex items-center justify-between rounded-xl bg-white px-3 py-2">
          <span className="text-sm text-slate-700">{item.name}</span>
          <span className="text-xs font-semibold text-slate-600">
            {pct(item.pass_rate)} ({item.passed}/{item.total})
          </span>
        </div>
      ))}
    </div>
  </div>
);

const BreakdownTable = ({
  title,
  data,
}: {
  title: string;
  data?: Record<string, { pass_rate: number; passed: number; total: number; failed?: number }>;
}) => {
  const rows = Object.entries(data || {}).sort((a, b) => b[1].pass_rate - a[1].pass_rate);
  return (
    <div className={softCard}>
      <div className="text-sm font-semibold text-slate-800">{title}</div>
      <div className="mt-3 overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead className="text-left text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th className="px-3 py-2">Name</th>
              <th className="px-3 py-2">Pass rate</th>
              <th className="px-3 py-2">Passed</th>
              <th className="px-3 py-2">Total</th>
            </tr>
          </thead>
          <tbody>
            {rows.length === 0 && (
              <tr>
                <td className="px-3 py-3 text-slate-500" colSpan={4}>
                  No data yet.
                </td>
              </tr>
            )}
            {rows.map(([name, bucket]) => (
              <tr key={`${title}-${name}`} className="border-t border-slate-200">
                <td className="px-3 py-2 text-slate-700">{name}</td>
                <td className="px-3 py-2 font-semibold text-slate-800">{pct(bucket.pass_rate)}</td>
                <td className="px-3 py-2 text-slate-600">{bucket.passed}</td>
                <td className="px-3 py-2 text-slate-600">{bucket.total}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

const PackRanking = ({ packs }: { packs: InterviewMetricsPack[] }) => (
  <section className={statCard}>
    <div className="flex flex-wrap items-start justify-between gap-3">
      <div>
        <div className="text-xs font-semibold uppercase tracking-[0.22em] text-primary-500">Pack Ranking</div>
        <h2 className="mt-1 text-2xl font-semibold text-slate-800">Benchmark leaderboard</h2>
        <p className="mt-2 max-w-3xl text-sm leading-relaxed text-slate-600">
          Compare tuned, holdout, and adversarial performance from one place instead of opening report files manually.
        </p>
      </div>
    </div>
    <div className="mt-5 grid gap-3">
      {packs.map((pack, index) => (
        <div key={`${pack.pack}-${pack.generated_at}`} className="rounded-2xl border border-slate-200 bg-white px-4 py-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <span className={`rounded-full border px-3 py-1 text-xs font-semibold ${rankTone(index)}`}>Rank #{index + 1}</span>
              <div>
                <div className="text-sm font-semibold text-slate-800">{packTitle(pack.pack)}</div>
                <div className="text-xs text-slate-500">{pack.benchmark_report}</div>
              </div>
            </div>
            <div className="flex flex-wrap gap-2 text-xs">
              <span className="rounded-full bg-slate-100 px-3 py-1 font-semibold text-slate-700">
                Overall {pct(pack.pipeline_metrics.overall_pass_rate)}
              </span>
              <span className="rounded-full bg-slate-100 px-3 py-1 font-semibold text-slate-700">
                SQL {pct(pack.pipeline_metrics.sql_pass_rate)}
              </span>
              <span className="rounded-full bg-slate-100 px-3 py-1 font-semibold text-slate-700">
                RAG {pct(pack.pipeline_metrics.rag_pass_rate)}
              </span>
              <span className="rounded-full bg-slate-100 px-3 py-1 font-semibold text-slate-700">
                P50 {seconds(pack.performance_metrics.p50_latency_s)}
              </span>
            </div>
          </div>
        </div>
      ))}
    </div>
  </section>
);

const LatestRunBoard = ({ latest }: { latest: InterviewMetricsPack }) => (
  <section className={statCard}>
    <div className="flex flex-wrap items-start justify-between gap-3">
      <div>
        <div className="text-xs font-semibold uppercase tracking-[0.22em] text-primary-500">Latest Run</div>
        <h2 className="mt-1 text-2xl font-semibold text-slate-800">{packTitle(latest.pack)}</h2>
        <p className="mt-2 max-w-3xl text-sm leading-relaxed text-slate-600">
          This is the most recent benchmark summary. It is the fastest place to quote current accuracy, latency, weak spots, and regressions.
        </p>
      </div>
      <div className="rounded-full bg-primary-50 px-3 py-1 text-xs font-semibold text-primary-600">
        {latest.benchmark_report}
      </div>
    </div>

    <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-5">
      <MetricTile
        label="Overall accuracy"
        value={pct(latest.pipeline_metrics.overall_pass_rate)}
        hint={`${latest.pipeline_metrics.overall_cases_passed}/${latest.pipeline_metrics.overall_cases_total} cases`}
      />
      <MetricTile label="SQL accuracy" value={pct(latest.pipeline_metrics.sql_pass_rate)} />
      <MetricTile label="RAG accuracy" value={pct(latest.pipeline_metrics.rag_pass_rate)} />
      <MetricTile label="Hybrid accuracy" value={pct(latest.pipeline_metrics.hybrid_pass_rate)} />
      <MetricTile label="Assertion accuracy" value={pct(latest.headline_metrics.assertion_pass_rate)} />
    </div>

    <div className="mt-4 grid gap-3 md:grid-cols-4">
      <MetricTile label="Average latency" value={seconds(latest.performance_metrics.avg_latency_s)} />
      <MetricTile label="P50 latency" value={seconds(latest.performance_metrics.p50_latency_s)} />
      <MetricTile label="P95 latency" value={seconds(latest.performance_metrics.p95_latency_s)} />
      <MetricTile label="Max latency" value={seconds(latest.performance_metrics.max_latency_s)} />
    </div>

    {latest.delta_vs_previous && (
      <div className="mt-4 grid gap-3 md:grid-cols-4">
        <MetricTile label="Pass rate delta" value={`${signed(latest.delta_vs_previous.pass_rate_delta)} pts`} />
        <MetricTile
          label="Assertion delta"
          value={`${signed(latest.delta_vs_previous.assertion_pass_rate_delta)} pts`}
        />
        <MetricTile label="P50 delta" value={`${signed(latest.delta_vs_previous.p50_latency_delta_s)}s`} />
        <MetricTile label="P95 delta" value={`${signed(latest.delta_vs_previous.p95_latency_delta_s)}s`} />
      </div>
    )}

    <div className="mt-5 grid gap-4 lg:grid-cols-2">
      <BreakdownList title="Strongest categories" items={latest.strongest_categories} />
      <BreakdownList title="Weakest categories" items={latest.weakest_categories} />
    </div>
  </section>
);

const SlowestCasesCard = ({ latest }: { latest: InterviewMetricsPack }) => (
  <section className={statCard}>
    <div className="text-xs font-semibold uppercase tracking-[0.22em] text-primary-500">Latency Tail</div>
    <h2 className="mt-1 text-2xl font-semibold text-slate-800">Slowest workflows</h2>
    <p className="mt-2 max-w-3xl text-sm leading-relaxed text-slate-600">
      This makes it easy to talk about performance tradeoffs, long-tail latency, and where the system still needs optimization.
    </p>
    <div className="mt-5 space-y-3">
      {(latest.slowest_cases || []).length === 0 && (
        <div className="rounded-2xl border border-slate-200 bg-slate-50/80 px-4 py-3 text-sm text-slate-500">No slow-case data yet.</div>
      )}
      {(latest.slowest_cases || []).map((item, index) => (
        <div key={`${item.case_id}-${index}`} className="rounded-2xl border border-slate-200 bg-white px-4 py-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <div className="text-sm font-semibold text-slate-800">{item.case_id}</div>
              <div className="mt-1 text-xs text-slate-500">
                {item.category} {item.policy ? `• ${item.policy}` : ""}
              </div>
            </div>
            <div className="rounded-full bg-rose-50 px-3 py-1 text-xs font-semibold text-rose-700">
              {seconds(item.latency_s)}
            </div>
          </div>
        </div>
      ))}
    </div>
  </section>
);

const FailedCasesCard = ({ latest }: { latest: InterviewMetricsPack }) => (
  <section className={statCard}>
    <div className="text-xs font-semibold uppercase tracking-[0.22em] text-primary-500">Regression View</div>
    <h2 className="mt-1 text-2xl font-semibold text-slate-800">Failed cases</h2>
    <p className="mt-2 max-w-3xl text-sm leading-relaxed text-slate-600">
      Use this section when you want to explain what is still failing and how you would prioritize the roadmap.
    </p>
    <div className="mt-5 grid gap-3">
      {latest.failed_case_ids.length === 0 && (
        <div className="rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
          No failed cases in this run.
        </div>
      )}
      {latest.failed_case_ids.map((caseId) => (
        <div key={caseId} className="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-700">
          {caseId}
        </div>
      ))}
    </div>
  </section>
);

const TalkingPointsCard = ({ latest }: { latest: InterviewMetricsPack }) => (
  <section className={statCard}>
    <div className="text-xs font-semibold uppercase tracking-[0.22em] text-primary-500">Interview Script</div>
    <h2 className="mt-1 text-2xl font-semibold text-slate-800">Talking points</h2>
    <div className="mt-5 space-y-3">
      {(latest.interview_talking_points || []).map((point) => (
        <div key={point} className="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm leading-relaxed text-slate-700">
          {point}
        </div>
      ))}
      {(!latest.interview_talking_points || latest.interview_talking_points.length === 0) && (
        <div className="rounded-2xl border border-slate-200 bg-slate-50/80 px-4 py-3 text-sm text-slate-500">
          No talking points generated yet.
        </div>
      )}
    </div>
  </section>
);

const PackDrilldown = ({ pack }: { pack: InterviewMetricsPack }) => (
  <section className={statCard}>
    <div className="flex flex-wrap items-start justify-between gap-3">
      <div>
        <div className="text-xs font-semibold uppercase tracking-[0.22em] text-primary-500">{packTitle(pack.pack)}</div>
        <h3 className="mt-1 text-xl font-semibold text-slate-800">Detailed breakdown</h3>
        <p className="mt-1 text-sm text-slate-500">Generated {new Date(pack.generated_at).toLocaleString()}</p>
      </div>
      <div className="rounded-full bg-primary-50 px-3 py-1 text-xs font-semibold text-primary-600">
        {pct(pack.headline_metrics.case_pass_rate)} case pass rate
      </div>
    </div>

    <div className="mt-5 grid gap-3 md:grid-cols-4">
      <MetricTile label="Overall" value={pct(pack.pipeline_metrics.overall_pass_rate)} />
      <MetricTile label="SQL" value={pct(pack.pipeline_metrics.sql_pass_rate)} />
      <MetricTile label="RAG" value={pct(pack.pipeline_metrics.rag_pass_rate)} />
      <MetricTile label="Hybrid" value={pct(pack.pipeline_metrics.hybrid_pass_rate)} />
    </div>

    <div className="mt-5 grid gap-4 lg:grid-cols-2">
      <BreakdownTable title="Policy ranking" data={pack.policy_breakdown} />
      <BreakdownTable title="Intent ranking" data={pack.intent_breakdown} />
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
    return Object.values(data.packs).sort((a, b) => {
      if (b.pipeline_metrics.overall_pass_rate !== a.pipeline_metrics.overall_pass_rate) {
        return b.pipeline_metrics.overall_pass_rate - a.pipeline_metrics.overall_pass_rate;
      }
      return a.performance_metrics.p50_latency_s - b.performance_metrics.p50_latency_s;
    });
  }, [data]);

  const latest = data?.latest_interview_metrics;

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
            <div className="text-xs font-semibold uppercase tracking-[0.22em] text-primary-500">AI Command Center</div>
            <h1 className="mt-1 text-3xl font-semibold text-slate-800">Benchmark dashboard, rankings, and interview metrics</h1>
            <p className="mt-2 max-w-4xl text-sm leading-relaxed text-slate-600">
              This page is your one-stop reference for health, accuracy, ranking, regressions, slowest flows, and benchmark talking points.
              You should not need to open raw report files unless you want the full artifact history.
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

      {packs.length > 0 && <PackRanking packs={packs} />}
      {latest && <LatestRunBoard latest={latest} />}

      {latest && (
        <div className="grid gap-6 xl:grid-cols-2">
          <SlowestCasesCard latest={latest} />
          <FailedCasesCard latest={latest} />
        </div>
      )}

      {latest && (
        <div className="grid gap-6 xl:grid-cols-2">
          <TalkingPointsCard latest={latest} />
          <div className={statCard}>
            <div className="text-xs font-semibold uppercase tracking-[0.22em] text-primary-500">Current Run Metadata</div>
            <h2 className="mt-1 text-2xl font-semibold text-slate-800">Run context</h2>
            <div className="mt-5 grid gap-3">
              <MetricTile label="Benchmark file" value={latest.benchmark_file} />
              <MetricTile label="Model label" value={latest.model_label || "default"} />
              <MetricTile label="Generated at" value={new Date(latest.generated_at).toLocaleString()} />
              <MetricTile label="Failed cases" value={String(latest.failed_case_count ?? latest.failed_case_ids.length)} />
            </div>
          </div>
        </div>
      )}

      {packs.map((pack) => (
        <PackDrilldown key={`${pack.pack}-${pack.generated_at}`} pack={pack} />
      ))}

      {packs.length === 0 && (
        <div className="rounded-3xl border border-slate-200 bg-white/90 p-6 text-sm text-slate-600">
          No benchmark reports were found yet. Run the benchmark scripts and refresh this page.
        </div>
      )}
    </div>
  );
};
