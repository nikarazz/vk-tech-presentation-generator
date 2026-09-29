"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { AlertCircle, AlertTriangle, Info, Filter } from "lucide-react";
import type { AuditReport as AuditReportType } from "@/types/api";

interface Props {
  report: AuditReportType;
}

type Severity = "all" | "error" | "warning" | "info";

export function AuditReport({ report }: Props) {
  const [filter, setFilter] = useState<Severity>("all");

  const filtered =
    filter === "all"
      ? report.problems
      : report.problems.filter((p) => p.severity === filter);

  const severityIcon = {
    error: <AlertCircle size={14} />,
    warning: <AlertTriangle size={14} />,
    info: <Info size={14} />,
  };

  const severityClass = {
    error: "badge-error",
    warning: "badge-warning",
    info: "badge-info",
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="card"
    >
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-bold">Аудит</h2>
        <div className="flex items-center gap-2 text-sm">
          <Filter size={14} className="text-[var(--color-text-muted)]" />
          {(["all", "error", "warning", "info"] as const).map((s) => (
            <motion.button
              key={s}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setFilter(s)}
              className={`px-2.5 py-1 rounded text-xs font-medium transition-colors ${
                filter === s
                  ? "bg-[var(--color-vk-primary)] text-white"
                  : "hover:bg-[var(--color-bg-subtle)]"
              }`}
            >
              {s === "all" ? "Все" : s}
            </motion.button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-3 gap-3 mb-4">
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.05 }}
          className="bg-[var(--color-vk-error-light)] rounded-lg p-3"
        >
          <div className="text-2xl font-bold text-[#A32020]">
            {report.by_severity?.error || 0}
          </div>
          <div className="text-xs text-[#A32020]">Ошибок</div>
        </motion.div>
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="bg-[var(--color-vk-warning-light)] rounded-lg p-3"
        >
          <div className="text-2xl font-bold text-[#8A6100]">
            {report.by_severity?.warning || 0}
          </div>
          <div className="text-xs text-[#8A6100]">Предупреждений</div>
        </motion.div>
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.15 }}
          className="bg-[var(--color-vk-primary-light)] rounded-lg p-3"
        >
          <div className="text-2xl font-bold text-[var(--color-vk-primary)]">
            {report.by_severity?.info || 0}
          </div>
          <div className="text-xs text-[var(--color-vk-primary)]">Info</div>
        </motion.div>
      </div>

      {filtered.length === 0 ? (
        <div className="text-center py-8 text-[var(--color-text-muted)]">
          Проблем нет 🎉
        </div>
      ) : (
        <div className="space-y-2 max-h-96 overflow-y-auto pr-2">
          <AnimatePresence>
            {filtered.map((p, i) => (
              <motion.div
                key={`${p.slide_id}-${p.rule_id}-${i}`}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 10 }}
                transition={{ delay: i * 0.03 }}
                className="flex items-start gap-3 p-3 rounded-lg bg-[var(--color-bg-subtle)] hover:bg-[var(--color-vk-primary-light)]/30 transition-colors"
              >
                <span className={`badge ${severityClass[p.severity]} shrink-0`}>
                  {severityIcon[p.severity]}
                  {p.severity}
                </span>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium">
                    Слайд {p.slide_id}
                    <span className="text-[var(--color-text-muted)] font-normal ml-2 font-mono text-xs">
                      {p.rule_id}
                    </span>
                  </div>
                  <div className="text-sm text-[var(--color-text-muted)] mt-0.5">
                    {p.message}
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      )}
    </motion.div>
  );
}
