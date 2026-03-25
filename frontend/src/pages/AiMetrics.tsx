import { useEffect, useMemo, useState } from "react";

import {
  fetchAiMetrics,
  type AiMetricsResponse,
  type InterviewMetricsPack,
  type PackHistoryPoint,
} from "@/lib/api";

const statCard =
  "rounded-3xl border border-slate-200 bg-white/90 p-5 shadow-[0_16px_40px_rgba(15,23,42,0.08)]";
const softCard = "rounded-2xl border border-slate-200 bg-slate-50/80 p-4";

const pct = (value?: number) => (typeof value === "number" ? `${value.toFixed(2)}%` : "n/a");
const seconds = (value?: number) => (typeof value === "number" ? `${value.toFixed(2)}s` : "n/a");
const currency = (value?: number | null) => (typeof value === "number" ? `$${value.toFixed(2)}` : "n/a");
const signed = (value?: number) => (typeof value === "number" ? `${value > 0 ? "+" : ""}${value.toFixed(2)}` : "n/a");

const statusTone = (ok?: boolean) =>
  ok ? "bg-emerald-50 text-emerald-700 border-emerald-200" : "bg-amber-50 text-amber-700 border-amber-200";

const packTitle = (name: string) => {
  if (name === "benchmarks.local") return "Tuned Regression Pack";
  if (name === "benchmarks.holdout") return "Holdout Pack";
  if (name === "benchmarks.adversarial") return "Adversarial Pack";
  if (name === "benchmarks.blind") return "Blind Pack";
  return name;
};

const MetricTile = ({ label, value, hint }: { label: string; value: string; hint?: string }) => (
  <div className={softCard}>
    <div className="text-xs uppercase tracking-wide text-slate-500">{label}</div>
    <div className="mt-1 text-xl font-semibold text-slate-800">{value}</div>
    {hint && <div className="mt-1 text-xs text-slate-500">{hint}</div>}
  </div>
);

const SectionTitle = ({ eyebrow, title, detail }: { eyebrow: string; title: string; detail: string }) => (
  <div>
    <div className="text-xs font-semibold uppercase tracking-[0.22em] text-primary-500">{eyebrow}</div>
    <h2 className="mt-1 text-2xl font-semibold text-slate-800">{title}</h2>
    <p className="mt-2 max-w-4xl text-sm leading-relaxed text-slate-600">{detail}</p>
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
    <SectionTitle
      eyebrow="Pack Ranking"
      title="Benchmark leaderboard"
      detail="Compare tuned, holdout, blind, and adversarial performance without opening raw report files."
    />
    <div className="mt-5 grid gap-3">
      {packs.map((pack, index) => (
        <div key={`${pack.pack}-${pack.generated_at}`} className="rounded-2xl border border-slate-200 bg-white px-4 py-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <div className="text-sm font-semibold text-slate-800">
                #{index + 1} {packTitle(pack.pack)}
              </div>
              <div className="mt-1 text-xs text-slate-500">{pack.benchmark_report}</div>
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

const TrendHistory = ({ pack, history }: { pack: string; history: PackHistoryPoint[] }) => (
  <section className={statCard}>
    <SectionTitle
      eyebrow="Trend History"
      title={`${packTitle(pack)} trend line`}
      detail="Use this to show that benchmark quality is moving over time, not just on the latest run."
    />
    <div className="mt-5 overflow-x-auto">
      <table className="min-w-full text-sm">
        <thead className="text-left text-xs uppercase tracking-wide text-slate-500">
          <tr>
            <th className="px-3 py-2">Run</th>
            <th className="px-3 py-2">Overall</th>
            <th className="px-3 py-2">SQL</th>
            <th className="px-3 py-2">RAG</th>
            <th className="px-3 py-2">Hybrid</th>
            <th className="px-3 py-2">P50</th>
            <th className="px-3 py-2">P95</th>
          </tr>
        </thead>
        <tbody>
          {history.map((point) => (
            <tr key={`${pack}-${point.generated_at}`} className="border-t border-slate-200">
              <td className="px-3 py-2 text-slate-700">{new Date(point.generated_at).toLocaleString()}</td>
              <td className="px-3 py-2 font-semibold text-slate-800">{pct(point.overall_pass_rate)}</td>
              <td className="px-3 py-2 text-slate-600">{pct(point.sql_pass_rate)}</td>
              <td className="px-3 py-2 text-slate-600">{pct(point.rag_pass_rate)}</td>
              <td className="px-3 py-2 text-slate-600">{pct(point.hybrid_pass_rate)}</td>
              <td className="px-3 py-2 text-slate-600">{seconds(point.p50_latency_s)}</td>
              <td className="px-3 py-2 text-slate-600">{seconds(point.p95_latency_s)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  </section>
);

const DataQualityPanel = ({ data }: { data?: AiMetricsResponse["data_quality"] }) => (
  <section className={statCard}>
    <SectionTitle
      eyebrow="Data Trust"
      title="Data quality and contracts"
      detail="This section makes the data layer defensible in interviews: schema contracts, row counts, and basic quality checks."
    />
    <div className="mt-5 grid gap-3 md:grid-cols-4">
      <MetricTile label="Status" value={data?.status || "unknown"} />
      <MetricTile label="Highbury listings" value={String(data?.summary?.highbury_listing_count ?? "n/a")} />
      <MetricTile label="Market listings" value={String(data?.summary?.market_listing_count ?? "n/a")} />
      <MetricTile label="Review rows" value={String(data?.summary?.review_row_count ?? "n/a")} />
    </div>
    <div className="mt-5 grid gap-4 lg:grid-cols-2">
      <div className={softCard}>
        <div className="text-sm font-semibold text-slate-800">Open issues</div>
        <div className="mt-3 space-y-2">
          {(data?.issues || []).length === 0 && <div className="rounded-xl bg-white px-3 py-2 text-sm text-slate-600">No open issues in the latest snapshot.</div>}
          {(data?.issues || []).map((issue) => (
            <div key={issue} className="rounded-xl bg-white px-3 py-2 text-sm text-slate-700">
              {issue}
            </div>
          ))}
        </div>
      </div>
      <div className={softCard}>
        <div className="text-sm font-semibold text-slate-800">Quality checks</div>
        <pre className="mt-3 overflow-auto rounded-2xl bg-slate-950 p-4 text-xs text-slate-100">
          <code>{JSON.stringify(data?.checks || {}, null, 2)}</code>
        </pre>
      </div>
    </div>
  </section>
);

const BusinessKpiPanel = ({ data }: { data?: AiMetricsResponse["business_kpis"] }) => (
  <section className={statCard}>
    <SectionTitle
      eyebrow="Business Value"
      title="Decision-support KPIs"
      detail="This is the business-facing layer: where the assistant creates value for operators, revenue managers, and expansion leads."
    />
    <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
      <MetricTile label="Portfolio listings" value={String(data?.headline?.portfolio_listings ?? "n/a")} />
      <MetricTile label="Pricing opportunities" value={String(data?.headline?.pricing_opportunities_found ?? "n/a")} />
      <MetricTile label="Underperformers flagged" value={String(data?.headline?.underperforming_listings_flagged ?? "n/a")} />
      <MetricTile label="Median occupancy 90" value={pct(data?.headline?.portfolio_median_occupancy_90)} />
      <MetricTile label="Average price" value={currency(data?.headline?.portfolio_avg_price)} />
      <MetricTile label="Average revenue 30" value={currency(data?.headline?.portfolio_avg_revenue_30)} />
      <MetricTile label="Average rating" value={String(data?.headline?.portfolio_avg_rating ?? "n/a")} />
    </div>
    <div className="mt-5 grid gap-4 xl:grid-cols-2">
      <div className={softCard}>
        <div className="text-sm font-semibold text-slate-800">Complaint themes by borough</div>
        <div className="mt-3 space-y-3">
          {(data?.complaint_themes_by_borough || []).map((borough) => (
            <div key={borough.borough} className="rounded-xl bg-white px-3 py-3">
              <div className="text-sm font-semibold text-slate-800">{borough.borough}</div>
              <div className="mt-2 flex flex-wrap gap-2">
                {borough.themes.map((theme) => (
                  <span key={`${borough.borough}-${theme.theme}`} className="rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs text-slate-700">
                    {theme.theme}: {theme.count}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
      <div className={softCard}>
        <div className="text-sm font-semibold text-slate-800">Expansion candidates</div>
        <div className="mt-3 space-y-3">
          {(data?.expansion_candidates || []).map((candidate) => (
            <div key={`${candidate.neighbourhood}-${candidate.borough}`} className="rounded-xl bg-white px-3 py-3">
              <div className="text-sm font-semibold text-slate-800">
                {candidate.neighbourhood}, {candidate.borough}
              </div>
              <div className="mt-2 text-xs text-slate-600">
                listings {candidate.listings} • occ90 {pct(candidate.avg_occupancy_90)} • rev30 {currency(candidate.avg_revenue_30)}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
    <div className="mt-5 grid gap-3">
      {(data?.decision_support_examples || []).map((example) => (
        <div key={example.persona} className="rounded-2xl border border-slate-200 bg-white px-4 py-4">
          <div className="text-sm font-semibold text-slate-800">{example.persona}</div>
          <div className="mt-2 text-sm text-slate-600">Before: {example.before}</div>
          <div className="mt-1 text-sm text-slate-700">After: {example.after}</div>
        </div>
      ))}
    </div>
  </section>
);

const LatestRunBoard = ({ latest }: { latest: InterviewMetricsPack }) => (
  <section className={statCard}>
    <SectionTitle
      eyebrow="Latest Run"
      title={packTitle(latest.pack)}
      detail="This is the quickest place to quote current accuracy, latency, cost/token usage, and regressions."
    />
    <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-5">
      <MetricTile label="Overall" value={pct(latest.pipeline_metrics.overall_pass_rate)} />
      <MetricTile label="SQL" value={pct(latest.pipeline_metrics.sql_pass_rate)} />
      <MetricTile label="RAG" value={pct(latest.pipeline_metrics.rag_pass_rate)} />
      <MetricTile label="Hybrid" value={pct(latest.pipeline_metrics.hybrid_pass_rate)} />
      <MetricTile label="Assertion" value={pct(latest.headline_metrics.assertion_pass_rate)} />
    </div>
    <div className="mt-4 grid gap-3 md:grid-cols-4">
      <MetricTile label="Average latency" value={seconds(latest.performance_metrics.avg_latency_s)} />
      <MetricTile label="P50" value={seconds(latest.performance_metrics.p50_latency_s)} />
      <MetricTile label="P95" value={seconds(latest.performance_metrics.p95_latency_s)} />
      <MetricTile label="Max" value={seconds(latest.performance_metrics.max_latency_s)} />
    </div>
    <div className="mt-4 grid gap-3 md:grid-cols-4">
      <MetricTile label="Prompt tokens" value={String(latest.cost_metrics?.prompt_tokens ?? 0)} />
      <MetricTile label="Completion tokens" value={String(latest.cost_metrics?.completion_tokens ?? 0)} />
      <MetricTile label="Total tokens" value={String(latest.cost_metrics?.total_tokens ?? 0)} />
      <MetricTile label="Estimated cost" value={currency(latest.cost_metrics?.estimated_cost_usd)} />
    </div>
    {latest.delta_vs_previous && (
      <div className="mt-4 grid gap-3 md:grid-cols-4">
        <MetricTile label="Pass rate delta" value={`${signed(latest.delta_vs_previous.pass_rate_delta)} pts`} />
        <MetricTile label="Assertion delta" value={`${signed(latest.delta_vs_previous.assertion_pass_rate_delta)} pts`} />
        <MetricTile label="P50 delta" value={`${signed(latest.delta_vs_previous.p50_latency_delta_s)}s`} />
        <MetricTile label="P95 delta" value={`${signed(latest.delta_vs_previous.p95_latency_delta_s)}s`} />
      </div>
    )}
  </section>
);

export const AiMetricsPage = (): JSX.Element => {
  const [data, setData] = useState<AiMetricsResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedPack, setSelectedPack] = useState<string>("all");

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const payload = await fetchAiMetrics();
      setData(payload);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load AI metrics.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void load();
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

  const visiblePacks = selectedPack === "all" ? packs : packs.filter((pack) => pack.pack === selectedPack);
  const latest = data?.latest_interview_metrics;
  const selectedHistory = selectedPack === "all" ? undefined : data?.pack_history?.[selectedPack];

  if (loading) {
    return <div className="rounded-3xl border border-slate-200 bg-white/90 p-6 text-sm text-slate-600">Loading AI metrics…</div>;
  }

  if (error) {
    return <div className="rounded-3xl border border-rose-200 bg-rose-50 p-6 text-sm text-rose-700">{error}</div>;
  }

  return (
    <div className="h-full overflow-y-auto pr-2 space-y-6">
      <section className={statCard}>
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.22em] text-primary-500">AI Command Center</div>
            <h1 className="mt-1 text-3xl font-semibold text-slate-800">Metrics, trust, business value, and interview readiness</h1>
            <p className="mt-2 max-w-4xl text-sm leading-relaxed text-slate-600">
              This page brings together benchmark rankings, trend history, data quality, business KPIs, and the latest interview talking points so you can demo the whole system from one place.
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <select
              value={selectedPack}
              onChange={(event) => setSelectedPack(event.target.value)}
              className="rounded-full border border-slate-200 bg-white px-4 py-2 text-sm text-slate-700 shadow-sm"
            >
              <option value="all">All benchmark packs</option>
              {packs.map((pack) => (
                <option key={pack.pack} value={pack.pack}>
                  {packTitle(pack.pack)}
                </option>
              ))}
            </select>
            <button
              onClick={() => void load()}
              className="rounded-full border border-primary-200 bg-white px-4 py-2 text-sm font-semibold text-primary-600 hover:bg-primary-50"
            >
              Refresh metrics
            </button>
            <div className={`rounded-full border px-4 py-2 text-sm font-semibold ${statusTone(data?.health?.status === "ready")}`}>
              Backend status: {data?.health?.status || "unknown"}
            </div>
          </div>
        </div>
        <div className="mt-4 text-xs text-slate-500">
          Last metric refresh: {data?.generated_at ? new Date(data.generated_at).toLocaleString() : "n/a"}
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
      {selectedHistory && <TrendHistory pack={selectedPack} history={selectedHistory} />}
      <DataQualityPanel data={data?.data_quality} />
      <BusinessKpiPanel data={data?.business_kpis} />

      {visiblePacks.map((pack) => (
        <section key={`${pack.pack}-${pack.generated_at}`} className={statCard}>
          <SectionTitle
            eyebrow={packTitle(pack.pack)}
            title="Detailed breakdown"
            detail={`Generated ${new Date(pack.generated_at).toLocaleString()} • model ${pack.model_label || "default"}`}
          />
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
          <div className="mt-5 grid gap-4 lg:grid-cols-2">
            <div className={softCard}>
              <div className="text-sm font-semibold text-slate-800">Failed cases</div>
              <div className="mt-3 space-y-2">
                {pack.failed_case_ids.length === 0 && <div className="rounded-xl bg-white px-3 py-2 text-sm text-slate-600">No failed cases in this run.</div>}
                {pack.failed_case_ids.map((caseId) => (
                  <div key={`${pack.pack}-${caseId}`} className="rounded-xl bg-white px-3 py-2 text-sm text-slate-700">
                    {caseId}
                  </div>
                ))}
              </div>
            </div>
            <div className={softCard}>
              <div className="text-sm font-semibold text-slate-800">Interview talking points</div>
              <div className="mt-3 space-y-2">
                {(pack.interview_talking_points || []).map((point) => (
                  <div key={`${pack.pack}-${point}`} className="rounded-xl bg-white px-3 py-2 text-sm text-slate-700">
                    {point}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>
      ))}

      {packs.length === 0 && (
        <div className="rounded-3xl border border-slate-200 bg-white/90 p-6 text-sm text-slate-600">
          No benchmark reports were found yet. Run the benchmark scripts and refresh this page.
        </div>
      )}
    </div>
  );
};
