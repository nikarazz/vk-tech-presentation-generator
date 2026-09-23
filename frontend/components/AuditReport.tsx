"use client";

import type { AuditReport as AuditReportType } from "@/types/api";

interface Props {
  report: AuditReportType;
}

export function AuditReport({ report }: Props) {
  const severityColor = {
    error: "text-red-600 bg-red-50",
    warning: "text-yellow-600 bg-yellow-50",
    info: "text-blue-600 bg-blue-50",
  };

  return (
    <div className="border rounded-lg p-4">
      <h2 className="text-xl font-bold mb-4">
        Аудит: {report.total_problems} проблем
      </h2>
      <div className="space-y-2">
        {report.problems.map((p, i) => (
          <div key={i} className={`p-3 rounded ${severityColor[p.severity]}`}>
            <span className="font-medium">Слайд {p.slide_id}</span>{" "}
            <span className="text-sm">[{p.rule_id}]</span> — {p.message}
          </div>
        ))}
      </div>
    </div>
  );
}
