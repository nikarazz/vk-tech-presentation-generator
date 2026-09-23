"use client";

import { getFileUrl } from "@/api/client";
import type { PresentationVariant } from "@/types/api";

interface Props {
  variants: PresentationVariant[];
}

export function VariantViewer({ variants }: Props) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
      {variants.map((v) => (
        <div key={v.variant_id} className="border rounded-lg p-4">
          <h3 className="font-bold mb-2">{v.variant_name}</h3>
          <div className="space-y-2">
            <a href={getFileUrl(v.pptx_url)} download className="block text-blue-600 hover:underline">
              Скачать .pptx
            </a>
            {v.pdf_url && (
              <a href={getFileUrl(v.pdf_url)} download className="block text-blue-600 hover:underline">
                Скачать .pdf
              </a>
            )}
            {v.html_url && (
              <a href={getFileUrl(v.html_url)} target="_blank" className="block text-blue-600 hover:underline">
                Открыть .html
              </a>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
