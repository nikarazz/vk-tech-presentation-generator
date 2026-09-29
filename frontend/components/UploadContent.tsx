"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { CheckCircle2, Loader2, Code2 } from "lucide-react";

interface Props {
  onUpload: (pack: object) => void;
}

const EXAMPLE = `{
  "product": "Тёмная тема в мобильном приложении",
  "benefits": [
    "Снижает нагрузку на глаза",
    "Экономит заряд батареи"
  ],
  "metrics": {
    "adoption": "40%",
    "satisfaction": "4.6/5"
  }
}`;

export function UploadContent({ onUpload }: Props) {
  const [text, setText] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loaded, setLoaded] = useState(false);
  const [loading, setLoading] = useState(false);

  function handleSubmit() {
    try {
      const parsed = JSON.parse(text);
      setError(null);
      setLoading(true);
      onUpload(parsed);
      setLoaded(true);
      setTimeout(() => setLoading(false), 500);
    } catch (e) {
      setError("Некорректный JSON");
      setLoaded(false);
    }
  }

  function handleExample() {
    setText(EXAMPLE);
    setError(null);
    setLoaded(false);
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-3">
        <div className="text-sm text-[var(--color-text-muted)]">
          JSON с данными продукта
        </div>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={handleExample}
          className="text-xs text-[var(--color-vk-primary)] hover:underline flex items-center gap-1"
        >
          <Code2 size={12} />
          Вставить пример
        </motion.button>
      </div>

      <textarea
        value={text}
        onChange={(e) => {
          setText(e.target.value);
          setLoaded(false);
        }}
        rows={6}
        className="input font-mono text-sm resize-y"
        placeholder='{"product": "...", "benefits": [...]}'
      />

      <AnimatePresence>
        {error && (
          <motion.p
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="text-[var(--color-vk-error)] text-sm mt-2"
          >
            {error}
          </motion.p>
        )}
      </AnimatePresence>

      <div className="flex items-center gap-3 mt-3">
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={handleSubmit}
          disabled={!text.trim() || loading}
          className="btn-primary text-sm"
        >
          {loading && <Loader2 size={16} className="animate-spin" />}
          Загрузить контент
        </motion.button>

        <AnimatePresence>
          {loaded && (
            <motion.span
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -10 }}
              className="badge badge-success"
            >
              <CheckCircle2 size={12} />
              Загружен
            </motion.span>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
