"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { motion } from "framer-motion";
import { Wand2, Zap } from "lucide-react";

import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { UploadTemplate } from "@/components/UploadTemplate";
import { UploadContent } from "@/components/UploadContent";
import { BriefInput } from "@/components/BriefInput";
import { GenerateButton } from "@/components/GenerateButton";

import {
  uploadTemplate,
  uploadContent,
  startGeneration,
} from "@/api/client";

export default function Home() {
  const router = useRouter();
  const [templateId, setTemplateId] = useState<string | null>(null);
  const [contentId, setContentId] = useState<string | null>(null);
  const [brief, setBrief] = useState("");
  const [loading, setLoading] = useState(false);

  const [variant, setVariant] = useState<"dense" | "airy" | "data">("dense");
  const [improve, setImprove] = useState(true);
  const [maxIterations, setMaxIterations] = useState(3);

  async function handleTemplate(file: File) {
    try {
      const res = await uploadTemplate(file);
      setTemplateId(res.template_id);
      toast.success(
        `Шаблон загружен: ${res.patterns_count} паттернов, confidence ${res.confidence.toFixed(2)}`
      );
    } catch (e) {
      toast.error("Ошибка загрузки шаблона");
    }
  }

  async function handleContent(pack: object) {
    try {
      const res = await uploadContent(pack);
      setContentId(res.content_id);
      toast.success("Контент загружен");
    } catch (e) {
      toast.error("Ошибка загрузки контента");
    }
  }

  async function handleGenerate() {
    if (!templateId || !contentId || !brief) {
      toast.error("Заполните все поля");
      return;
    }
    setLoading(true);
    try {
      const res = await startGeneration({
        template_id: templateId,
        content_id: contentId,
        brief,
        variants: 3,
      });
      router.push(`/result/${res.job_id}`);
    } catch (e) {
      toast.error("Ошибка запуска генерации");
      setLoading(false);
    }
  }

  return (
    <>
      <Header />

      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-8">
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-8"
        >
          <div className="flex items-center gap-2 mb-3">
            <span className="badge badge-info">
              <Zap size={12} />
              AI-пайплайн
            </span>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold mb-3">
            Создайте презентацию в{" "}
            <span className="gradient-text">фирменном стиле</span>
          </h1>
          <p className="text-[var(--color-text-muted)] text-lg max-w-2xl">
            Загрузите шаблон .pptx, введите бриф — получите 3 варианта вёрстки в
            стиле вашего шаблона.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-[280px_1fr] gap-8">
          {/* Sidebar */}
          <motion.aside
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="space-y-4"
          >
            <div className="card sticky top-24">
              <div className="font-medium mb-4 flex items-center gap-2">
                <Wand2 size={16} className="text-[var(--color-vk-primary)]" />
                Настройки
              </div>

              <div className="space-y-5">
                <div>
                  <label className="text-xs text-[var(--color-text-muted)] mb-2 block uppercase tracking-wider">
                    Вариант
                  </label>
                  <div className="flex gap-1">
                    {(["dense", "airy", "data"] as const).map((v) => (
                      <motion.button
                        key={v}
                        whileHover={{ scale: 1.03 }}
                        whileTap={{ scale: 0.97 }}
                        onClick={() => setVariant(v)}
                        className={`flex-1 text-xs py-2 rounded-md transition-colors font-medium ${
                          variant === v
                            ? "bg-[var(--color-vk-primary)] text-white shadow-[var(--shadow-vk)]"
                            : "bg-[var(--color-bg-subtle)] hover:bg-[var(--color-border)]"
                        }`}
                      >
                        {v}
                      </motion.button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="flex items-center gap-2 text-sm cursor-pointer">
                    <input
                      type="checkbox"
                      checked={improve}
                      onChange={(e) => setImprove(e.target.checked)}
                      className="w-4 h-4 rounded accent-[var(--color-vk-primary)]"
                    />
                    <span className="font-medium">Режим Improve</span>
                  </label>
                  <div className="text-xs text-[var(--color-text-muted)] mt-1 ml-6">
                    Аудит + автоисправление
                  </div>
                </div>

                {improve && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                  >
                    <label className="text-xs text-[var(--color-text-muted)] mb-2 block uppercase tracking-wider">
                      Итераций: {maxIterations}
                    </label>
                    <input
                      type="range"
                      min={1}
                      max={5}
                      value={maxIterations}
                      onChange={(e) => setMaxIterations(Number(e.target.value))}
                      className="w-full accent-[var(--color-vk-primary)]"
                    />
                  </motion.div>
                )}
              </div>
            </div>
          </motion.aside>

          {/* Main */}
          <div className="space-y-6">
            <StepCard number={1} title="Загрузите шаблон" delay={0.15}>
              <UploadTemplate onUpload={handleTemplate} />
            </StepCard>

            <StepCard number={2} title="Контент-пакет" delay={0.2}>
              <UploadContent onUpload={handleContent} />
            </StepCard>

            <StepCard number={3} title="Бриф" delay={0.25}>
              <BriefInput value={brief} onChange={setBrief} />
            </StepCard>

            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3, duration: 0.4 }}
            >
              <GenerateButton
                onClick={handleGenerate}
                disabled={!templateId || !contentId || !brief}
                loading={loading}
              />
            </motion.div>
          </div>
        </div>
      </main>

      <Footer />
    </>
  );
}

function StepCard({
  number,
  title,
  delay,
  children,
}: {
  number: number;
  title: string;
  delay: number;
  children: React.ReactNode;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.4 }}
    >
      <div className="flex items-center gap-3 mb-3">
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: delay + 0.1, type: "spring", stiffness: 400 }}
          className="w-7 h-7 rounded-full bg-gradient-to-br from-[var(--color-vk-primary)] to-[var(--color-vk-accent)] text-white text-xs font-bold flex items-center justify-center shadow-[var(--shadow-vk)]"
        >
          {number}
        </motion.div>
        <h2 className="font-bold text-lg">{title}</h2>
      </div>
      {children}
    </motion.div>
  );
}
