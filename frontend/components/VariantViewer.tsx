"use client";

import { motion } from "framer-motion";
import { Download, FileText, Globe, Presentation } from "lucide-react";
import { getFileUrl } from "@/api/client";
import type { PresentationVariant } from "@/types/api";

interface Props {
  variants: PresentationVariant[];
}

export function VariantViewer({ variants }: Props) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      {variants.map((v, i) => (
        <motion.div
          key={v.variant_id}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.1, duration: 0.4 }}
          whileHover={{ y: -4 }}
          className="card gradient-border"
        >
          <div className="flex items-center gap-3 mb-4">
            <motion.div
              whileHover={{ rotate: 8 }}
              className="w-10 h-10 rounded-lg bg-gradient-to-br from-[var(--color-vk-primary)] to-[var(--color-vk-accent)] flex items-center justify-center text-white shadow-[var(--shadow-vk)]"
            >
              <Presentation size={20} />
            </motion.div>
            <div>
              <div className="font-bold">{v.variant_name}</div>
              <div className="text-xs text-[var(--color-text-muted)]">
                Вариант {v.variant_id}
              </div>
            </div>
          </div>

          <div className="space-y-2">
            <motion.a
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              href={getFileUrl(v.pptx_url)}
              download
              className="btn-primary w-full text-sm"
            >
              <Download size={14} />
              Скачать .pptx
            </motion.a>
            {v.pdf_url && (
              <motion.a
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                href={getFileUrl(v.pdf_url)}
                download
                className="btn-secondary w-full text-sm"
              >
                <FileText size={14} />
                Скачать .pdf
              </motion.a>
            )}
            {v.html_url && (
              <motion.a
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                href={getFileUrl(v.html_url)}
                target="_blank"
                rel="noopener noreferrer"
                className="btn-secondary w-full text-sm"
              >
                <Globe size={14} />
                Открыть .html
              </motion.a>
            )}
          </div>
        </motion.div>
      ))}
    </div>
  );
}
