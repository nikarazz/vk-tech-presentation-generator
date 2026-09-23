"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { getJobStatus } from "@/api/client";
import type { JobStatusResponse } from "@/types/api";
import { ProgressBar } from "@/components/ProgressBar";
import { VariantViewer } from "@/components/VariantViewer";
import { AuditReport } from "@/components/AuditReport";

export default function ResultPage() {
  const params = useParams();
  const jobId = params.jobId as string;
  const [job, setJob] = useState<JobStatusResponse | null>(null);

  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const status = await getJobStatus(jobId);
        setJob(status);
        if (status.status === "done" || status.status === "error") {
          clearInterval(interval);
        }
      } catch (e) {}
    }, 2000);
    return () => clearInterval(interval);
  }, [jobId]);

  if (!job) return <div className="p-8">Загрузка...</div>;

  if (job.status === "processing") {
    return (
      <div className="p-8 max-w-2xl mx-auto">
        <h1 className="text-2xl font-bold mb-4">Генерация...</h1>
        <ProgressBar progress={job.progress} message={job.message} />
      </div>
    );
  }

  if (job.status === "error") {
    return (
      <div className="p-8 max-w-2xl mx-auto">
        <h1 className="text-2xl font-bold text-red-600 mb-4">Ошибка</h1>
        <p>{job.error}</p>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Готово!</h1>
      <VariantViewer variants={job.result!.presentations} />
      <AuditReport report={job.result!.audit_report} />
    </div>
  );
}
