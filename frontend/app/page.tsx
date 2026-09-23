"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { toast, Toaster } from "sonner";
import { UploadTemplate } from "@/components/UploadTemplate";
import { UploadContent } from "@/components/UploadContent";
import { BriefInput } from "@/components/BriefInput";
import { GenerateButton } from "@/components/GenerateButton";
import { uploadTemplate, uploadContent, startGeneration } from "@/api/client";

export default function Home() {
  const router = useRouter();
  const [templateId, setTemplateId] = useState<string | null>(null);
  const [contentId, setContentId] = useState<string | null>(null);
  const [brief, setBrief] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleTemplate(file: File) {
    try {
      const res = await uploadTemplate(file);
      setTemplateId(res.template_id);
      toast.success(`Шаблон загружен: ${res.patterns_count} паттернов`);
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
      toast.error("Заполни все поля");
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
    <main className="min-h-screen p-8 max-w-4xl mx-auto">
      <Toaster position="top-right" />
      <h1 className="text-3xl font-bold mb-8">
        Цифровой дизайнер презентаций
      </h1>
      <div className="space-y-6">
        <UploadTemplate onUpload={handleTemplate} />
        <UploadContent onUpload={handleContent} />
        <BriefInput value={brief} onChange={setBrief} />
        <GenerateButton
          onClick={handleGenerate}
          disabled={!templateId || !contentId || !brief}
          loading={loading}
        />
      </div>
    </main>
  );
}
