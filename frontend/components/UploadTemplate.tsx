"use client";

import { useDropzone } from "react-dropzone";

interface Props {
  onUpload: (file: File) => void;
}

export function UploadTemplate({ onUpload }: Props) {
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      "application/vnd.openxmlformats-officedocument.presentationml.presentation": [".pptx"],
    },
    multiple: false,
    onDrop: (files) => files[0] && onUpload(files[0]),
  });

  return (
    <div
      {...getRootProps()}
      className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition ${
        isDragActive ? "border-blue-500 bg-blue-50" : "border-gray-300"
      }`}
    >
      <input {...getInputProps()} />
      <p className="text-lg">
        {isDragActive
          ? "Отпусти файл здесь"
          : "Перетащи .pptx шаблон сюда или кликни"}
      </p>
    </div>
  );
}
