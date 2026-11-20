"""De petits fichiers de chaque format, pour les tests des documents (US-012)."""

import io
import zipfile


def pdf() -> bytes:
    return b"%PDF-1.4\n% cours\n1 0 obj\n<<>>\nendobj\n%%EOF\n"


def ole2() -> bytes:
    return bytes.fromhex("D0CF11E0A1B11AE1") + b"\x00" * 512


def ooxml(folder: str) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("[Content_Types].xml", "<Types/>")
        archive.writestr(f"{folder}document.xml", "<doc/>")
    return buffer.getvalue()


def docx() -> bytes:
    return ooxml("word/")


def pptx() -> bytes:
    return ooxml("ppt/")
