"use client";

interface Props {
  value: string;
  onChange: (v: string) => void;
}

export function BriefInput({ value, onChange }: Props) {
  return (
    <div>
      <label className="block mb-2 font-medium">Бриф</label>
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        rows={4}
        className="w-full border rounded-lg p-3"
        placeholder="Фича: тёмная тема. Плюс: снижает нагрузку. Метрика: 40%."
      />
    </div>
  );
}
