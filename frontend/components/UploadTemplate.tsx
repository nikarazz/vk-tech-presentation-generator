"use client";

import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { motion, AnimatePresence } from "framer-motion";
import { Upload, FileCheck, X } from "lucide-react";

interface Props {
  onUpload: (file: File) => void;
}

export function UploadTemplate({ onUpload }: Props) {
  const [file, setFile] = useState<File | null>(null);

  const onDrop = useCallback(
    (accepted: File[]) => {
      if (accepted[0]) {
        setFile(accepted[0]);
        onUpload(accepted[0]);
      }
    },
    [onUpload]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      "application/vnd.openxmlformats-officedocument.presentationml.presentation":
        [".pptx"],
    },
    multiple: false,
    onDrop,
  });

  return (
    <AnimatePresence mode="wait">
      {file ? (
        <motion.div
          key="file"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
          transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
          className="card"
        >
          <div className="flex items-start justify-between mb-3">
            <motion.span
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.1, type: "spring", stiffness: 400 }}
              className="badge badge-success"
            >
              <FileCheck size={12} />
              Загружен
            </motion.span>
            <motion.button
              whileHover={{ scale: 1.1, rotate: 90 }}
              whileTap={{ scale: 0.9 }}
              onClick={(e) => {
                e.stopPropagation();
                setFile(null);
              }}
              className="text-[var(--color-text-muted)] hover:text-[var(--color-vk-error)] transition-colors"
            >
              <X size={18} />
            </motion.button>
          </div>
          <div className="flex items-center gap-3">
            <motion.div
              initial={{ rotate: -10, scale: 0.8 }}
              animate={{ rotate: 0, scale: 1 }}
              transition={{ delay: 0.1, type: "spring" }}
              className="w-12 h-12 rounded-lg bg-[var(--color-vk-primary-light)] flex items-center justify-center text-[var(--color-vk-primary)]"
            >
              <FileCheck size={24} />
            </motion.div>
            <div>
              <div className="font-medium">{file.name}</div>
              <div className="text-sm text-[var(--color-text-muted)]">
                {(file.size / 1024).toFixed(1)} KB
              </div>
            </div>
          </div>
        </motion.div>
      ) : (
        <motion.div
          key="dropzone"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          {...(getRootProps() as any)}
          className={`card card-interactive ${
            isDragActive
              ? "border-[var(--color-vk-primary)] bg-[var(--color-vk-primary-light)]"
              : ""
          }`}
          whileHover={{ scale: 1.01 }}
          whileTap={{ scale: 0.99 }}
        >
          <input {...getInputProps()} />
          <div className="text-center py-2">
            <motion.div
              animate={isDragActive ? { y: [-4, 4, -4] } : {}}
              transition={{ repeat: Infinity, duration: 1 }}
              className="w-14 h-14 rounded-full bg-[var(--color-vk-primary-light)] flex items-center justify-center text-[var(--color-vk-primary)] mx-auto mb-3"
            >
              <Upload size={24} />
            </motion.div>
            <div className="font-medium mb-1">
              {isDragActive ? "Отпустите файл" : "Перетащите .pptx сюда"}
            </div>
            <div className="text-sm text-[var(--color-text-muted)]">
              или кликните для выбора файла
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
