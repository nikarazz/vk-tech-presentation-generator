"use client";

import { useState } from "react";

interface Props {
  onUpload: (pack: object) => void;
}

export function UploadContent({ onUpload }: Props) {
  const [text, setText] = useState("");
  const [error, setError] = useState<string | null>(null);

  function handleSubmit() {
    try {
      const parsed = JSON.parse(text);
      setError(null);
      onUpload(parsed);
    } catch (e) {
      setError("Некорректный JSON");
    }
  }

  return (
    <div>
      <label className="block mb-2 font-medium">Контент-пакет (JSON)</label>
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        rows={6}
        className="w-full border rounded-lg p-3 font-mono text-sm"
        placeholder='{"product": "...", "benefits": [...]}'
      />
      {error && <p className="text-red-500 text-sm mt-1">{error}</p>}
      <button
        onClick={handleSubmit}
        disabled={!text.trim()}
        className="mt-2 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
      >
        Загрузить контент
      </button>
    </div>
  );
}
