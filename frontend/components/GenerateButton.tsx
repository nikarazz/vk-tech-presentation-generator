"use client";

import { motion } from "framer-motion";
import { Sparkles, Loader2 } from "lucide-react";

interface Props {
  onClick: () => void;
  disabled: boolean;
  loading: boolean;
}

export function GenerateButton({ onClick, disabled, loading }: Props) {
  return (
    <motion.button
      whileHover={!disabled && !loading ? { scale: 1.01, y: -2 } : {}}
      whileTap={!disabled && !loading ? { scale: 0.99 } : {}}
      onClick={onClick}
      disabled={disabled || loading}
      className="btn-primary w-full text-base py-4 relative overflow-hidden"
    >
      {loading ? (
        <>
          <Loader2 size={20} className="animate-spin" />
          Генерация...
        </>
      ) : (
        <>
          <motion.span
            animate={{ rotate: [0, 10, -10, 0] }}
            transition={{ duration: 2, repeat: Infinity, repeatDelay: 3 }}
          >
            <Sparkles size={20} />
          </motion.span>
          Сгенерировать презентацию
        </>
      )}
    </motion.button>
  );
}
