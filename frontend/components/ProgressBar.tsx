"use client";

import { motion } from "framer-motion";
import { Check } from "lucide-react";

interface Props {
  progress: number;
  message?: string;
  stage?: string;
}

const STAGES = [
  { id: "parse", label: "Парсинг" },
  { id: "plan", label: "Структура" },
  { id: "layout", label: "Раскладка" },
  { id: "improve", label: "Improve" },
  { id: "export", label: "Экспорт" },
];

export function ProgressBar({ progress, message, stage }: Props) {
  const currentStageIdx = stage ? STAGES.findIndex((s) => s.id === stage) : -1;

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-3">
        <div className="font-medium">
          {stage
            ? STAGES.find((s) => s.id === stage)?.label || stage
            : "Генерация"}
        </div>
        <motion.div
          key={Math.round(progress)}
          initial={{ scale: 1.2 }}
          animate={{ scale: 1 }}
          className="text-sm text-[var(--color-text-muted)] font-mono"
        >
          {Math.round(progress)}%
        </motion.div>
      </div>

      <div className="w-full bg-[var(--color-bg-subtle)] rounded-full h-2 overflow-hidden">
        <motion.div
          className="h-full bg-gradient-to-r from-[var(--color-vk-primary)] to-[var(--color-vk-accent)] rounded-full"
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.5, ease: "easeOut" }}
        />
      </div>

      {message && (
        <motion.p
          key={message}
          initial={{ opacity: 0, y: 4 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-3 text-sm text-[var(--color-text-muted)]"
        >
          {message}
        </motion.p>
      )}

      <div className="mt-6 grid grid-cols-5 gap-2">
        {STAGES.map((s, i) => {
          const isDone = i < currentStageIdx;
          const isActive = i === currentStageIdx;

          return (
            <div key={s.id} className="text-center">
              <motion.div
                initial={false}
                animate={{
                  scale: isActive ? [1, 1.1, 1] : 1,
                  backgroundColor: isDone
                    ? "var(--color-vk-success)"
                    : isActive
                    ? "var(--color-vk-primary)"
                    : "var(--color-bg-subtle)",
                }}
                transition={{
                  scale: { repeat: isActive ? Infinity : 0, duration: 1.5 },
                  duration: 0.3,
                }}
                className="w-8 h-8 mx-auto rounded-full flex items-center justify-center text-xs font-bold mb-2"
                style={{
                  color: isDone || isActive ? "white" : "var(--color-text-muted)",
                }}
              >
                {isDone ? <Check size={14} /> : i + 1}
              </motion.div>
              <div
                className={`text-[10px] leading-tight transition-colors ${
                  isActive
                    ? "text-[var(--color-vk-primary)] font-medium"
                    : "text-[var(--color-text-muted)]"
                }`}
              >
                {s.label}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
