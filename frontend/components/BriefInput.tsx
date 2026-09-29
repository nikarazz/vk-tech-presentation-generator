"use client";

import { motion } from "framer-motion";
import { MessageSquare } from "lucide-react";

interface Props {
  value: string;
  onChange: (v: string) => void;
}

export function BriefInput({ value, onChange }: Props) {
  return (
    <div className="card">
      <div className="flex items-center justify-between mb-3">
        <div className="text-sm text-[var(--color-text-muted)] flex items-center gap-2">
          <MessageSquare size={14} className="text-[var(--color-vk-primary)]" />
          Опишите, о чём презентация
        </div>
        <motion.span
          key={value.length}
          initial={{ scale: 1.2, color: "var(--color-vk-primary)" }}
          animate={{ scale: 1, color: "var(--color-text-muted)" }}
          transition={{ duration: 0.2 }}
          className="text-xs"
        >
          {value.length} символов
        </motion.span>
      </div>

      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        rows={5}
        className="input resize-y"
        placeholder="Фича: тёмная тема. Плюс: снижает нагрузку. Метрика: 40%."
      />

      <div className="text-xs text-[var(--color-text-muted)] mt-2">
        Опишите фичу, продукт, метрику или инициативу.
      </div>
    </div>
  );
}
