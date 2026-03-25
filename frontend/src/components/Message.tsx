import { useMemo } from "react";
import { motion } from "framer-motion";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { Components } from "react-markdown";

import type { Message, TablePayload, ThinkingStep } from "@/store/useChat";
import { ThinkingTrace } from "@/components/ThinkingTrace";

const DEBUG = import.meta.env.VITE_DEBUG === "true";

const resolveAssistantText = (msg: Message | undefined): string => {
  if (!msg) return "";
  if (msg.role !== "assistant") {
    return msg.content ?? msg.nl_summary ?? "";
  }
  return (
    msg.content ||
    msg.nl_summary ||
    msg.payload?.summary ||
    msg.payload?.answer_text ||
    msg.payload?.markdown_table ||
    ""
  );
};

const markdownComponents: Components = {
  p: ({ node, ...props }) => <p className="whitespace-pre-wrap leading-relaxed" {...props} />,
  ul: ({ node, ...props }) => <ul className="my-2 ml-4 list-disc space-y-1" {...props} />,
  ol: ({ node, ...props }) => <ol className="my-2 ml-4 list-decimal space-y-1" {...props} />,
  li: ({ node, ...props }) => <li className="leading-relaxed" {...props} />,
  table: ({ node, ...props }) => (
    <div className="overflow-x-auto inline-block">
      <table className="border-collapse text-sm my-3 table-auto" {...props} />
    </div>
  ),
  thead: ({ node, ...props }) => <thead className="bg-slate-100/70" {...props} />,
  tbody: ({ node, ...props }) => <tbody {...props} />,
  th: ({ node, ...props }) => (
    <th className="border border-slate-300 px-3 py-2 text-left font-medium" {...props} />
  ),
  td: ({ node, ...props }) => (
    <td className="border border-slate-200 px-3 py-2 align-top whitespace-pre-wrap" {...props} />
  ),
  pre: ({ node, ...props }) => (
    <pre className="rounded-xl bg-slate-950 text-slate-100 p-4 text-xs overflow-auto" {...props} />
  ),
  code: ({ node, className, ...props }) => {
    const isInline = !className?.includes("language-");
    const resolvedClassName = [isInline ? "rounded bg-slate-100 px-1 py-0.5 text-xs" : "block", className]
      .filter(Boolean)
      .join(" ");
    return <code className={resolvedClassName} {...props} />;
  },
};

const assistantMarkdownClass =
  "prose prose-slate max-w-none leading-relaxed text-[15px] space-y-4";

const userMarkdownClass =
  "prose prose-invert max-w-none leading-relaxed text-[15px]";

const isRagTable = (table?: TablePayload | null): boolean => {
  if (!table) return false;
  const source = typeof table.source === "string" ? table.source.toLowerCase() : "";
  if (source === "rag") {
    return true;
  }
  if (!Array.isArray(table.columns) || table.columns.length === 0) {
    return false;
  }
  const columnSet = new Set(table.columns.map((col) => col.toLowerCase()));
  const looksLikeRagSchema = columnSet.has("snippet") && columnSet.has("comment_id");
  if (!looksLikeRagSchema) {
    return false;
  }
  const label = typeof table.name === "string" ? table.name.toLowerCase() : "";
  return label.includes("rag");
};

interface SnippetMeta {
  snippet: string;
  month?: string;
  year?: string;
  neighbourhood?: string;
  borough?: string;
  neighbourhood_group?: string;
  listing_name?: string;
  listing_id?: string;
  comment_id?: string;
  commentId?: string;
  commentID?: string;
  review_id?: string;
  reviewId?: string;
  citation?: string;
  sentiment_label?: string;
  compound?: number;
  positive?: number;
  neutral?: number;
  negative?: number;
  is_highbury?: string;
}

interface ExpansionSource {
  url?: string;
  title?: string;
  text?: string;
  score?: number | string;
}

const formatCellValue = (value: unknown): string => {
  if (value === null || value === undefined) return "";
  if (typeof value === "string") return value;
  return String(value);
};

const getTrimmedString = (value: unknown): string | undefined => {
  if (typeof value !== "string") return undefined;
  const trimmed = value.trim();
  return trimmed.length > 0 ? trimmed : undefined;
};

const parseNumeric = (value: unknown): number | undefined => {
  if (typeof value === "number" && Number.isFinite(value)) return value;
  if (typeof value === "string") {
    const trimmed = value.trim();
    if (!trimmed) return undefined;
    const parsed = Number(trimmed);
    return Number.isFinite(parsed) ? parsed : undefined;
  }
  return undefined;
};

const SENTIMENT_BADGE_STYLES: Record<string, string> = {
  positive: "bg-emerald-100 text-emerald-700 border border-emerald-200",
  neutral: "bg-amber-50 text-amber-700 border border-amber-200",
  negative: "bg-rose-50 text-rose-700 border border-rose-200",
};

const formatPercent = (value?: number): string | undefined => {
  if (typeof value !== "number" || !Number.isFinite(value)) return undefined;
  const pct = Math.round(value * 100);
  return `${pct}%`;
};

const formatStrengthValue = (value?: number): string => {
  if (typeof value !== "number" || !Number.isFinite(value)) return "n/a";
  return value.toFixed(2);
};

const confidenceTone = (band?: string): string => {
  if (band === "high") return "bg-emerald-50 text-emerald-700 border-emerald-200";
  if (band === "medium") return "bg-amber-50 text-amber-700 border-amber-200";
  return "bg-rose-50 text-rose-700 border-rose-200";
};

const prettyJson = (value: unknown): string => {
  try {
    return JSON.stringify(value ?? {}, null, 2);
  } catch {
    return String(value ?? "");
  }
};

const isRenderableMarkdownTable = (value: string | undefined): boolean => {
  if (!value) return false;
  const lower = value.toLowerCase();
  const hasMarkdownTableSyntax = value.includes("|") && value.includes("\n");
  const hasHtmlTableSyntax = lower.includes("<table") && lower.includes("</table>");
  return hasMarkdownTableSyntax || hasHtmlTableSyntax;
};

const getRowCount = (message: Message): number | undefined => {
  const payload = message.payload;
  if (!payload) return undefined;
  if (typeof payload.row_count === "number") {
    return payload.row_count;
  }
  if (Array.isArray(payload.tables) && payload.tables.length > 0) {
    const rows = payload.tables.reduce((total, table) => {
      if (isRagTable(table)) return total;
      if (typeof table?.row_count === "number") return total + table.row_count;
      if (Array.isArray(table?.data)) return total + table.data.length;
      return total;
    }, 0);
    return rows || undefined;
  }
  return undefined;
};

const getPipelineLabel = (message: Message): string | undefined => {
  const payload = message.payload;
  if (!payload) return undefined;
  if (typeof payload.pipeline === "string" && payload.pipeline.trim()) {
    return payload.pipeline;
  }
  if (typeof payload.policy === "string" && payload.policy.trim()) {
    return payload.policy;
  }
  if (typeof payload.response_type === "string" && payload.response_type.trim()) {
    return payload.response_type;
  }
  return undefined;
};

interface EmailShareOptions {
  csvOnly?: boolean;
}

interface MessageProps {
  message: Message;
  highlighted?: boolean;
  exportLoading?: { messageId: string; tableIndex: number } | null;
  exportError?: { messageId: string; tableIndex: number; message: string } | null;
  onExport?: (tableIndex: number) => void;
  onEmailExport?: (tableIndex: number, label: string, options?: EmailShareOptions) => void;
}

export const MessageBubble: React.FC<MessageProps> = ({
  message,
  highlighted,
  exportLoading,
  exportError,
  onExport,
  onEmailExport,
}) => {
  const isUser = message.role === "user";
  const bubbleClass = isUser
    ? "bg-gradient-to-r from-primary-500 to-primary-600 text-white border-transparent shadow-xl"
    : "bg-white border border-slate-200 text-slate-700 shadow-md";
  const labelClass = isUser ? "text-white/80" : "text-primary-500";
  const highlightClass = highlighted ? "ring-2 ring-primary-300/60 bubble-highlight" : "";

  if (DEBUG && !isUser) {
    console.info(
      `[HYDRATE_FIX] ${message.role}: payload keys=${message.payload ? Object.keys(message.payload).join(", ") : ""}`,
    );
  }

  const rowCount = getRowCount(message);
  const durationMs = typeof message.payload?.duration_ms === "number" ? message.payload.duration_ms : undefined;
  const pipeline = getPipelineLabel(message);
  const suppressMarkdownTable =
    !isUser && typeof pipeline === "string" && pipeline.toUpperCase() === "PORTFOLIO_TRIAGE";
  const ragSnippets = useMemo<SnippetMeta[]>(() => {
    const raw = message.payload?.rag_snippets;
    if (!Array.isArray(raw)) return [];
    return raw
      .map((entry) => {
        if (!entry) return null;
        if (typeof entry === "string") {
          const text = entry.trim();
          return text ? { snippet: text } : null;
        }
        if (typeof entry === "object") {
          const snippetText =
            typeof entry.snippet === "string" && entry.snippet.trim().length
              ? entry.snippet.trim()
              : typeof entry.text === "string" && entry.text.trim().length
                ? entry.text.trim()
                : null;
          if (!snippetText) {
            return null;
          }
          const sentimentLabel =
            typeof entry.sentiment_label === "string" && entry.sentiment_label.trim().length
              ? entry.sentiment_label.trim().toLowerCase()
              : undefined;
          const isHighbury =
            typeof entry.is_highbury === "string"
              ? entry.is_highbury.trim()
              : typeof entry.is_highbury === "boolean"
                ? entry.is_highbury
                  ? "true"
                  : "false"
                : undefined;
          return {
            snippet: snippetText,
            month: typeof entry.month === "string" ? entry.month.trim() : undefined,
            year:
              typeof entry.year === "number"
                ? String(entry.year)
                : typeof entry.year === "string" && entry.year.trim().length
                  ? entry.year.trim()
                  : undefined,
            neighbourhood:
              typeof entry.neighbourhood === "string" && entry.neighbourhood.trim().length
                ? entry.neighbourhood.trim()
                : undefined,
            borough:
              typeof entry.borough === "string" && entry.borough.trim().length
                ? entry.borough.trim()
                : undefined,
            neighbourhood_group:
              typeof entry.neighbourhood_group === "string" && entry.neighbourhood_group.trim().length
                ? entry.neighbourhood_group.trim()
                : undefined,
            listing_name:
              typeof entry.listing_name === "string" && entry.listing_name.trim().length
                ? entry.listing_name.trim()
                : undefined,
            listing_id:
              typeof entry.listing_id === "string"
                ? entry.listing_id.trim()
                : typeof entry.listing_id === "number"
                  ? String(entry.listing_id)
                  : undefined,
            sentiment_label: sentimentLabel,
            compound: parseNumeric(entry.compound),
            positive: parseNumeric(entry.positive),
            neutral: parseNumeric(entry.neutral),
            negative: parseNumeric(entry.negative),
            is_highbury: isHighbury,
          };
        }
        return null;
      })
      .filter((item): item is NonNullable<typeof item> => Boolean(item));
  }, [message.payload?.rag_snippets]);
  const sentimentAnalytics = !isUser && message.payload?.sentiment_analytics ? message.payload.sentiment_analytics : undefined;

  const markdownTable = getTrimmedString(message.payload?.markdown_table);
  const thinkingTrace: ThinkingStep[] =
    !isUser && Array.isArray(message.payload?.thinking_trace)
      ? (message.payload?.thinking_trace as ThinkingStep[])
      : [];
  const tables: TablePayload[] =
    !isUser && Array.isArray(message.payload?.tables) ? (message.payload?.tables as TablePayload[]) : [];
  const sqlTableIndex = tables.findIndex((table) => !isRagTable(table));
  const ragTableIndex = tables.findIndex((table) => isRagTable(table));
  const hasSqlTable = sqlTableIndex !== -1;
  const hasSqlExport = hasSqlTable;
  const primaryTableName = hasSqlTable ? tables[sqlTableIndex]?.name || "Result 1" : "Result 1";
  const ragTableName = ragTableIndex !== -1 ? tables[ragTableIndex]?.name || "RAG Sources" : "RAG Sources";
  const ragExportAvailable = ragSnippets.length > 0 && ragTableIndex !== -1;
  const isExportBusy = (index: number): boolean =>
    index >= 0 && Boolean(exportLoading?.messageId === message.id && exportLoading?.tableIndex === index);
  const getExportError = (index: number): string | null =>
    index >= 0 && exportError?.messageId === message.id && exportError?.tableIndex === index
      ? exportError.message
      : null;
  const sqlExportBusy = hasSqlExport && isExportBusy(sqlTableIndex);
  const sqlExportError = hasSqlExport ? getExportError(sqlTableIndex) : null;
  const ragExportBusy = ragExportAvailable && isExportBusy(ragTableIndex);
  const ragExportError = ragExportAvailable ? getExportError(ragTableIndex) : null;
  const rawSqlText =
    typeof message.payload?.sql === "string" && message.payload.sql.trim().length
      ? message.payload.sql.trim()
      : undefined;
  const fallbackSqlFromTable =
    hasSqlTable &&
    typeof tables[sqlTableIndex]?.sql === "string" &&
    tables[sqlTableIndex]?.sql?.trim().length
      ? tables[sqlTableIndex]?.sql?.trim()
      : undefined;
  const sqlText = rawSqlText || fallbackSqlFromTable;
  const hasSqlQuery = Boolean(sqlText);
  const expansionSources: ExpansionSource[] =
    !isUser && Array.isArray(message.payload?.expansion_sources)
      ? (message.payload?.expansion_sources as ExpansionSource[])
      : [];
  const expansionCount = expansionSources.length;
  const expansionIntent =
    !isUser &&
    ((typeof message.payload?.intent === "string" &&
      message.payload.intent.toUpperCase() === "EXPANSION_SCOUT") ||
      (typeof message.payload?.policy === "string" &&
        message.payload.policy.toUpperCase() === "EXPANSION_SCOUT") ||
      message.payload?.response_type === "expansion");
  const isLoadingPlaceholder = !isUser && message.payload?.response_type === "loading";
  const confidence = !isUser ? message.payload?.confidence : undefined;
  const trace = !isUser ? message.payload?.trace : undefined;
  const totalTokens = typeof trace?.performance?.tokens?.total_tokens === "number" ? trace.performance.tokens.total_tokens : undefined;

  let displayContent = "";
  let usedMarkdownAsText = false;
  if (isUser) {
    displayContent = message.content ?? message.nl_summary ?? "";
  } else {
    displayContent = isLoadingPlaceholder ? "" : resolveAssistantText(message);
    if (!displayContent && markdownTable) {
      displayContent = markdownTable;
      usedMarkdownAsText = true;
    }
  }

  if (!displayContent && !isUser && !isLoadingPlaceholder) {
    displayContent = "No insight available from the model. Please rephrase your question or try again.";
  }

  const shouldRenderContent = displayContent.trim().length > 0;
  const shouldRenderMarkdownTable =
    !suppressMarkdownTable && !isUser && isRenderableMarkdownTable(markdownTable) && !usedMarkdownAsText;

  return (
    <motion.div
      id={`msg-${message.id}`}
      initial={{ opacity: 0, y: 4 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className={`rounded-2xl transition-all duration-300 ${highlightClass}`}
    >
      <div className={`rounded-2xl shadow-sm px-5 py-4 ${bubbleClass}`}>
        <div className="flex items-center justify-between gap-3">
          {isUser ? (
            <div className={`text-xs uppercase tracking-[0.25em] font-semibold ${labelClass}`}>You</div>
          ) : (
            <div className="flex items-center gap-2 mb-1">
              <span className="font-semibold text-indigo-600"> 💡 wtchtwr</span>
              <span className="text-gray-400 text-sm">Your property insights companion</span>
            </div>
          )}
        </div>

        {isLoadingPlaceholder && (
          <div className="mt-2">
            <div className="flex items-center gap-2 text-sm text-slate-500 font-semibold">
              <span>Thinking longer for a better answer</span>
              <span className="loading-dots flex items-center gap-1">
                <span className="dot" />
                <span className="dot" />
                <span className="dot" />
              </span>
            </div>
          </div>
        )}

        {shouldRenderContent && (
          <div className={`mt-3 ${isUser ? "text-white/95" : "text-slate-700"}`}>
            <ReactMarkdown
              className={isUser ? userMarkdownClass : assistantMarkdownClass}
              components={markdownComponents}
              remarkPlugins={[remarkGfm]}
            >
              {displayContent}
            </ReactMarkdown>
          </div>
        )}

        {shouldRenderMarkdownTable && markdownTable && (
          <div className="mt-4 border border-slate-200 rounded-2xl bg-white/90 p-4">
            <ReactMarkdown className={assistantMarkdownClass} components={markdownComponents} remarkPlugins={[remarkGfm]}>
              {markdownTable}
            </ReactMarkdown>
          </div>
        )}

        {!isUser && expansionIntent && expansionSources.length > 0 && (
          <details className="mt-4 expansion-sources group">
            <summary className="flex flex-wrap items-center justify-between gap-3 cursor-pointer text-sm font-semibold text-primary-600 transition group-open:text-primary-700">
              <span className="flex items-center gap-1">
                <span className="text-2xl leading-none transition-transform group-open:rotate-90">▸</span>
                Web Sources Used{expansionCount ? ` (${expansionCount})` : ""}
              </span>
            </summary>
            <div className="mt-3 space-y-2">
              {expansionSources.map((src, idx) => (
                <div
                  key={`expansion-source-${idx}-${src.url || src.title || "source"}`}
                  className="relative overflow-hidden rounded-3xl border border-slate-200/70 bg-gradient-to-br from-white via-sky-50/80 to-sky-100/70 p-5 shadow-[0_12px_25px_rgba(15,23,42,0.08)]"
                >
                  <div className="absolute inset-y-4 left-4 w-px bg-gradient-to-b from-primary-200 via-primary-300 to-transparent" aria-hidden="true" />
                  <div className="pl-4 sm:pl-6 space-y-2">
                    <div className="text-sm font-semibold text-slate-800">
                      {src.title || src.url || `Source ${idx + 1}`}
                    </div>
                    {src.url && (
                      <a
                        href={src.url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-xs text-primary-600 hover:text-primary-700 break-words"
                      >
                        {src.url}
                      </a>
                    )}
                    {src.text && (
                      <p className="text-xs text-slate-600 leading-relaxed">
                        {src.text.slice(0, 320)}
                        {src.text.length > 320 ? "..." : ""}
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </details>
        )}

        {!isUser && hasSqlQuery && (
          <details className="mt-4 group">
            <summary className="flex flex-wrap items-center justify-between gap-3 cursor-pointer text-sm font-semibold text-primary-600 transition group-open:text-primary-700">
              <span className="flex items-center gap-1">
                <span className="text-2xl leading-none transition-transform group-open:rotate-90">▸</span>
                View Generated SQL
              </span>
              {hasSqlExport && (
                <div className="flex flex-wrap items-center gap-2">
                  <button
                    onClick={(event) => {
                      event.stopPropagation();
                      event.preventDefault();
                      onExport?.(sqlTableIndex);
                    }}
                    disabled={sqlExportBusy}
                    className="rounded-full bg-primary-500 text-white px-3 py-1.5 text-xs font-semibold shadow hover:bg-primary-600 disabled:opacity-60"
                  >
                    {sqlExportBusy ? "Preparing…" : "Download CSV"}
                  </button>
                  <button
                    onClick={(event) => {
                      event.stopPropagation();
                      event.preventDefault();
                      onEmailExport?.(sqlTableIndex, primaryTableName);
                    }}
                    disabled={sqlExportBusy}
                    className="rounded-full border border-primary-200 px-3 py-1.5 text-xs font-semibold text-primary-600 hover:bg-primary-50 disabled:opacity-60"
                  >
                    Email SQL / CSV
                  </button>
                </div>
              )}
            </summary>
            {hasSqlExport && sqlExportError && (
              <p className="mt-2 text-xs text-red-500 text-right">{sqlExportError}</p>
            )}
            <div className="mt-3 relative overflow-hidden rounded-3xl border border-slate-200/70 bg-white p-4 shadow-[0_12px_25px_rgba(15,23,42,0.08)]">
              <div className="absolute inset-y-4 left-4 w-[3px] rounded-full bg-gradient-to-b from-sky-200 via-blue-300 to-transparent" aria-hidden="true" />
              <pre className="max-h-80 overflow-auto rounded-2xl bg-gradient-to-br from-white via-sky-50/70 to-blue-50/60 text-slate-800 p-4 text-xs leading-relaxed shadow-inner border border-blue-50">
                <code>{sqlText}</code>
              </pre>
            </div>
          </details>
        )}

        {/* sentiment summary now showcased inline with each snippet */}

        {!isUser && ragSnippets.length > 0 && (
          <details className="mt-4 group">
            <summary className="flex flex-wrap items-center justify-between gap-3 cursor-pointer text-sm font-semibold text-primary-600 transition group-open:text-primary-700">
              <span className="flex items-center gap-1">
                <span className="text-2xl leading-none transition-transform group-open:rotate-90">▸</span>
                View RAG Sources ({ragSnippets.length})
              </span>
              {ragExportAvailable && (
                <div className="flex flex-wrap items-center gap-2">
                  <button
                    onClick={(event) => {
                      event.stopPropagation();
                      event.preventDefault();
                      onExport?.(ragTableIndex);
                    }}
                    disabled={ragExportBusy}
                    className="rounded-full bg-primary-500 text-white px-3 py-1.5 text-xs font-semibold shadow hover:bg-primary-600 disabled:opacity-60"
                  >
                    {ragExportBusy ? "Preparing…" : "Download reviews"}
                  </button>
                  <button
                    onClick={(event) => {
                      event.stopPropagation();
                      event.preventDefault();
                      onEmailExport?.(ragTableIndex, ragTableName, { csvOnly: true });
                    }}
                    disabled={ragExportBusy}
                    className="rounded-full border border-primary-200 px-3 py-1.5 text-xs font-semibold text-primary-600 hover:bg-primary-50 disabled:opacity-60"
                  >
                    Email reviews
                  </button>
                </div>
              )}
            </summary>
            {ragExportAvailable && ragExportError && (
              <p className="mt-2 text-xs text-red-500 text-right">{ragExportError}</p>
            )}
            <div className="mt-3 space-y-2">
              {ragSnippets.slice(0, 10).map((snip, idx) => {
                const metaParts: string[] = [];
                const listingId = snip.listing_id ? String(snip.listing_id).trim() : "";
                const neighbourhood = snip.neighbourhood?.trim();
                if (neighbourhood) {
                  metaParts.push(neighbourhood);
                }
                const neighbourhoodGroup = snip.neighbourhood_group?.trim();
                if (neighbourhoodGroup && neighbourhoodGroup !== neighbourhood) {
                  metaParts.push(neighbourhoodGroup);
                }
                if (snip.is_highbury && snip.is_highbury !== "false") {
                  metaParts.push("Highbury");
                }
                const monthYearParts = [snip.month, snip.year]
                  .map((value) => (value ? String(value).trim() : ""))
                  .filter(Boolean);
                if (monthYearParts.length) {
                  const monthYear = [monthYearParts.slice(0, -1).join(" "), monthYearParts.slice(-1)[0]]
                    .filter(Boolean)
                    .join(" ")
                    .trim();
                  if (monthYear) {
                    metaParts.push(monthYear);
                  }
                }
                const metaDisplay = metaParts.join(" • ");
                const hasSentimentBreakdown = Boolean(snip.positive || snip.neutral || snip.negative);
                return (
                  <div key={`rag-source-${idx}`}>
                    {idx > 0 && <hr className="my-2 border-slate-100" />}
                    <div className="relative overflow-hidden rounded-3xl border border-slate-200/70 bg-gradient-to-br from-white via-sky-50/80 to-sky-100/70 p-5 shadow-[0_12px_25px_rgba(15,23,42,0.08)]">
                      <div className="absolute inset-y-4 left-4 w-px bg-gradient-to-b from-primary-200 via-primary-300 to-transparent" aria-hidden="true" />
                      <div className="pl-4 sm:pl-6">
                        <div className="text-sm text-slate-800 leading-relaxed font-semibold">{snip.snippet}</div>
                        <div className="mt-4 flex flex-wrap items-center justify-between gap-3 text-xs text-slate-600">
                          <div className="flex flex-wrap items-center gap-2">
                            <span className="inline-flex items-center gap-1 rounded-full bg-white px-2 py-0.5 font-semibold text-slate-700 border border-slate-200">
                              Listing ID: {listingId || "n/a"}
                            </span>
                            {metaDisplay && (
                              <span className="inline-flex items-center gap-2 text-slate-500">
                                {metaDisplay}
                              </span>
                            )}
                          </div>
                          <div className="flex flex-wrap gap-3 text-[11px] text-slate-500">
                            {snip.sentiment_label && (
                              <span
                                className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 font-semibold ${SENTIMENT_BADGE_STYLES[snip.sentiment_label] || "bg-slate-100 text-slate-600"}`}
                              >
                                {snip.sentiment_label.charAt(0).toUpperCase() + snip.sentiment_label.slice(1)}
                              </span>
                            )}
                            {typeof snip.compound === "number" && (
                              <span className="inline-flex items-center gap-1 rounded-full bg-white px-2 py-0.5 text-slate-600 border border-slate-200">
                                Avg strength: {snip.compound.toFixed(2)}
                              </span>
                            )}
                            {formatPercent(snip.positive) && <span>Positive {formatPercent(snip.positive)}</span>}
                            {formatPercent(snip.neutral) && <span>Neutral {formatPercent(snip.neutral)}</span>}
                            {formatPercent(snip.negative) && <span>Negative {formatPercent(snip.negative)}</span>}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </details>
        )}

        {!isUser && confidence?.overall && (
          <div className="mt-4 rounded-2xl border border-slate-200 bg-slate-50/80 p-4">
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-sm font-semibold text-slate-800">Answer confidence</span>
              <span className={`rounded-full border px-2.5 py-1 text-xs font-semibold ${confidenceTone(confidence.overall.band)}`}>
                {confidence.overall.band.toUpperCase()}
              </span>
              <span className="rounded-full bg-white px-2.5 py-1 text-xs font-medium text-slate-600">
                Score {Math.round((confidence.overall.score || 0) * 100)} / 100
              </span>
              {confidence.degraded && (
                <span className="rounded-full border border-amber-200 bg-amber-50 px-2.5 py-1 text-xs font-semibold text-amber-700">
                  Degraded mode
                </span>
              )}
            </div>
            <div className="mt-3 flex flex-wrap gap-2 text-xs">
              {confidence.sql && (
                <span className={`rounded-full border px-2.5 py-1 font-semibold ${confidenceTone(confidence.sql.band)}`}>
                  SQL: {confidence.sql.band}
                </span>
              )}
              {confidence.rag && (
                <span className={`rounded-full border px-2.5 py-1 font-semibold ${confidenceTone(confidence.rag.band)}`}>
                  Retrieval: {confidence.rag.band}
                </span>
              )}
            </div>
            {(confidence.overall.reasons?.length || confidence.degraded_reasons?.length) && (
              <div className="mt-3 space-y-1 text-xs leading-relaxed text-slate-600">
                {(confidence.overall.reasons || []).slice(0, 2).map((reason) => (
                  <div key={`confidence-reason-${reason}`}>• {reason}</div>
                ))}
                {(confidence.degraded_reasons || []).map((reason) => (
                  <div key={`degraded-reason-${reason}`} className="text-amber-700">• {reason}</div>
                ))}
              </div>
            )}
          </div>
        )}

        {!isUser && (rowCount !== undefined || durationMs !== undefined || pipeline) && (
          <div className="mt-3 flex flex-wrap items-center gap-2 text-xs text-slate-500">
            {rowCount !== undefined && (
              <span className="inline-flex items-center gap-1 rounded-full bg-slate-100 px-2.5 py-1 font-medium">
                Rows: {rowCount}
              </span>
            )}
            {durationMs !== undefined && (
              <span className="inline-flex items-center gap-1 rounded-full bg-slate-100 px-2.5 py-1 font-medium">
                Latency: {Math.round(durationMs)} ms
              </span>
            )}
            {totalTokens !== undefined && (
              <span className="inline-flex items-center gap-1 rounded-full bg-slate-100 px-2.5 py-1 font-medium">
                Tokens: {totalTokens}
              </span>
            )}
            {pipeline && (
              <span className="inline-flex items-center gap-1 rounded-full bg-slate-100 px-2.5 py-1 text-primary-500 font-semibold">
                Pipeline: {pipeline}
              </span>
            )}
          </div>
        )}

        {!isUser && trace && (
          <details className="mt-4 group">
            <summary className="flex flex-wrap items-center justify-between gap-3 cursor-pointer text-sm font-semibold text-primary-600 transition group-open:text-primary-700">
              <span className="flex items-center gap-1">
                <span className="text-2xl leading-none transition-transform group-open:rotate-90">▸</span>
                AI Trace
              </span>
              <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-600">
                intent {trace.intent || "n/a"} • policy {trace.policy || "n/a"}
              </span>
            </summary>
            <div className="mt-3 grid gap-3 lg:grid-cols-2">
              <div className="rounded-2xl border border-slate-200 bg-white p-4">
                <div className="text-xs uppercase tracking-wide text-slate-500">Routing</div>
                <div className="mt-2 space-y-2 text-sm text-slate-700">
                  <div><strong>Intent:</strong> {trace.intent || "n/a"}</div>
                  <div><strong>Scope:</strong> {trace.scope || "n/a"}</div>
                  <div><strong>Policy:</strong> {trace.policy || "n/a"}</div>
                  <div><strong>Degraded:</strong> {trace.degraded ? "yes" : "no"}</div>
                </div>
              </div>
              <div className="rounded-2xl border border-slate-200 bg-white p-4">
                <div className="text-xs uppercase tracking-wide text-slate-500">Performance</div>
                <div className="mt-2 space-y-2 text-sm text-slate-700">
                  <div><strong>Total latency:</strong> {typeof trace.performance?.total_latency_s === "number" ? `${trace.performance.total_latency_s.toFixed(2)}s` : "n/a"}</div>
                  <div><strong>Compose latency:</strong> {typeof trace.performance?.compose_latency_s === "number" ? `${trace.performance.compose_latency_s.toFixed(2)}s` : "n/a"}</div>
                  <div><strong>Tokens:</strong> {trace.performance?.tokens?.total_tokens ?? "n/a"}</div>
                </div>
              </div>
              <div className="rounded-2xl border border-slate-200 bg-white p-4">
                <div className="text-xs uppercase tracking-wide text-slate-500">SQL Path</div>
                <div className="mt-2 space-y-2 text-sm text-slate-700">
                  <div><strong>Present:</strong> {trace.sql?.present ? "yes" : "no"}</div>
                  <div><strong>Rows:</strong> {trace.sql?.row_count ?? 0}</div>
                  <div><strong>Table:</strong> {trace.sql?.table || "n/a"}</div>
                </div>
              </div>
              <div className="rounded-2xl border border-slate-200 bg-white p-4">
                <div className="text-xs uppercase tracking-wide text-slate-500">Retrieval Path</div>
                <div className="mt-2 space-y-2 text-sm text-slate-700">
                  <div><strong>Hits:</strong> {trace.retrieval?.hit_count ?? 0}</div>
                  <div><strong>Confidence:</strong> {trace.retrieval?.confidence || "n/a"}</div>
                  <div><strong>Weak evidence:</strong> {trace.retrieval?.weak_evidence ? "yes" : "no"}</div>
                  <div><strong>Error:</strong> {trace.retrieval?.error || "none"}</div>
                </div>
              </div>
              <div className="rounded-2xl border border-slate-200 bg-white p-4 lg:col-span-2">
                <div className="text-xs uppercase tracking-wide text-slate-500">Filters</div>
                <pre className="mt-2 overflow-auto rounded-xl bg-slate-950 p-3 text-xs text-slate-100">
                  <code>{prettyJson(trace.filters)}</code>
                </pre>
              </div>
            </div>
          </details>
        )}

        {!isUser && thinkingTrace.length > 0 && <ThinkingTrace steps={thinkingTrace} />}
      </div>
    </motion.div>
  );
};
