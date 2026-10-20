import os
def parse_resume(path):
    ext=os.path.splitext(path)[1].lower()
    if ext==".pdf":
        try:
            from pypdf import PdfReader
            return "\n".join(page.extract_text() or "" for page in PdfReader(path).pages)
        except Exception as e:
            return f"PDF parsing error: {e}"
    if ext==".docx":
        try:
            from docx import Document
            doc=Document(path)
            return "\n".join(p.text for p in doc.paragraphs)
        except Exception as e:
            return f"DOCX parsing error: {e}"
    return ""
