import os
import platform
import subprocess
from pathlib import Path


def _find_soffice() -> str:
    """Ищет LibreOffice soffice в стандартных путях."""
    system = platform.system()
    
    if system == "Windows":
        paths = [
            r"C:\Program Files\LibreOffice\program\soffice.exe",
            r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
        ]
    elif system == "Darwin":
        paths = ["/Applications/LibreOffice.app/Contents/MacOS/soffice"]
    else:
        paths = ["/usr/bin/soffice", "/usr/bin/libreoffice"]
    
    for p in paths:
        if os.path.exists(p):
            return p
    
    return "soffice"


def export_pdf(pptx_path: str, output_path: str) -> None:
    """
    Конвертирует .pptx → .pdf через LibreOffice headless.
    """
    soffice = _find_soffice()
    output_dir = str(Path(output_path).parent.resolve())
    
    cmd = [
        soffice,
        "--headless",
        "--convert-to", "pdf",
        "--outdir", output_dir,
        pptx_path,
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        raise RuntimeError(f"LibreOffice failed: {result.stderr}")
    
    # LibreOffice сохраняет с именем исходного файла
    src_name = Path(pptx_path).stem
    generated = Path(output_dir) / f"{src_name}.pdf"
    
    if generated.exists() and str(generated) != str(Path(output_path).resolve()):
        os.replace(generated, output_path)
    
    print(f"[B] Exported PDF: {output_path}")