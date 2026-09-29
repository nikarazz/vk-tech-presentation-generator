"""Экспорт .pptx → .pdf через LibreOffice."""
import os
import shutil
import subprocess
from pathlib import Path


SOFFICE_PATHS = [
    "soffice",
    "soffice.exe",
    "/usr/bin/soffice",
    "/Applications/LibreOffice.app/Contents/MacOS/soffice",
    r"C:\Program Files\LibreOffice\program\soffice.exe",
    r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
]


def _find_soffice() -> str | None:
    """Ищет soffice в PATH и стандартных местах."""
    found = shutil.which("soffice")
    if found:
        return found

    for path in SOFFICE_PATHS:
        if os.path.exists(path):
            return path

    return None


def export_pdf(pptx_path: str, output_path: str) -> None:
    """Конвертирует .pptx в .pdf через LibreOffice headless."""
    soffice = _find_soffice()
    if not soffice:
        raise RuntimeError(
            "LibreOffice (soffice) не найден. "
            "Установите: https://www.libreoffice.org/download/download/"
        )

    output_dir = str(Path(output_path).resolve().parent)
    pptx_abs = str(Path(pptx_path).resolve())

    cmd = [
        soffice,
        "--headless",
        "--convert-to", "pdf",
        "--outdir", output_dir,
        pptx_abs,
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=120,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"LibreOffice failed (code={result.returncode}): {result.stderr}"
        )

    # LibreOffice сохраняет по имени pptx — переименуем
    pptx_name = Path(pptx_path).stem
    generated = Path(output_dir) / f"{pptx_name}.pdf"
    output_abs = str(Path(output_path).resolve())

    if generated.exists() and str(generated) != output_abs:
        if os.path.exists(output_abs):
            os.remove(output_abs)
        os.rename(str(generated), output_abs)

    print(f"[B] Exported PDF: {output_path}")
