"use client";

interface Props {
  progress: number;
  message?: string;
}

export function ProgressBar({ progress, message }: Props) {
  return (
    <div>
      <div className="w-full bg-gray-200 rounded-full h-4">
        <div
          className="bg-blue-500 h-4 rounded-full transition-all"
          style={{ width: `${progress}%` }}
        />
      </div>
      {message && <p className="mt-2 text-sm text-gray-600">{message}</p>}
    </div>
  );
}
