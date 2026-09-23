import axios from "axios";
import type {
  TemplateResponse,
  ContentResponse,
  GenerateRequest,
  GenerateResponse,
  JobStatusResponse,
} from "@/types/api";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: API_URL,
});

export async function uploadTemplate(file: File): Promise<TemplateResponse> {
  const form = new FormData();
  form.append("file", file);
  const { data } = await api.post<TemplateResponse>("/api/templates", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function uploadContent(contentPack: object): Promise<ContentResponse> {
  const { data } = await api.post<ContentResponse>("/api/content", {
    content_pack: contentPack,
  });
  return data;
}

export async function startGeneration(
  req: GenerateRequest
): Promise<GenerateResponse> {
  const { data } = await api.post<GenerateResponse>("/api/generate", req);
  return data;
}

export async function getJobStatus(jobId: string): Promise<JobStatusResponse> {
  const { data } = await api.get<JobStatusResponse>(`/api/jobs/${jobId}`);
  return data;
}

export function getFileUrl(path: string): string {
  return `${API_URL}${path}`;
}
