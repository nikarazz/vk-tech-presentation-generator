"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { ArrowLeft, RefreshCw } from "lucide-react";

import { getJobStatus } from "@/api/client";
import type { JobStatusResponse } from "@/types/api";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { ProgressBar } from "@/components/ProgressBar";
import { VariantViewer } from "@/components/VariantViewer";
import { AuditReport } from "@/components/AuditReport";

export default function ResultPage() {
  const params = useParams();
  const router = useRouter();
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

  return (
    <>
      <Header />

      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-8">
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between mb-6"
        >
          <motion.button
            whileHover={{ x: -4 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => router.push("/")}
            className="btn-secondary text-sm"
          >
            <ArrowLeft size={16} />
            Назад
          </motion.button>

          <div className="flex items-center gap-3">
            <span className="text-sm text-[var(--color-text-muted)] font-mono">
              job: {jobId.slice(0, 8)}
            </span>
            {job && (
              <span
                className={`badge ${
                  job.status === "done"
                    ? "badge-success"
                    : job.status === "error"
                    ? "badge-error"
                    : "badge-info animate-pulse-soft"
                }`}
              >
                {job.status}
              </span>
            )}
          </div>
        </motion.div>

        {!job && (
          <div className="card text-center py-12">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ repeat: Infinity, duration: 1.5, ease: "linear" }}
              className="w-12 h-12 mx-auto mb-4 rounded-full border-3 border-[var(--color-border)] border-t-[var(--color-vk-primary)]"
            />
            <p className="text-[var(--color-text-muted)]">Загрузка...</p>
          </div>
        )}

        {job?.status === "processing" && (
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <ProgressBar
              progress={job.progress}
              message={job.message}
              stage={job.stage}
            />
          </motion.div>
        )}

        {job?.status === "error" && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="card border-[var(--color-vk-error)]"
          >
            <h2 className="text-xl font-bold text-[var(--color-vk-error)] mb-2">
              Ошибка
            </h2>
            <p className="text-[var(--color-text-muted)]">{job.error}</p>
          </motion.div>
        )}

        {job?.status === "done" && job.result && (
          <div className="space-y-6">
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center justify-between"
            >
              <h1 className="text-2xl font-bold">Готово! 🎉</h1>
              <motion.button
                whileHover={{ scale: 1.03, rotate: 180 }}
                whileTap={{ scale: 0.97 }}
                onClick={() => router.push("/")}
                className="btn-secondary text-sm"
              >
                <RefreshCw size={14} />
                Сгенерировать ещё
              </motion.button>
            </motion.div>

            <VariantViewer variants={job.result.presentations} />

            {job.result.audit_report && (
              <AuditReport report={job.result.audit_report} />
            )}
          </div>
        )}
      </main>

      <Footer />
    </>
  );
}
