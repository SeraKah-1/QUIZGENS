import fitz  # PyMuPDF

def extract_text_from_pdf(file_content: bytes, max_pages: int = 20) -> str:
    """
    Ekstrak teks dari bytes PDF.
    max_pages: Batasi halaman biar token Gemini nggak jebol (Hemat biaya).
    """
    try:
        doc = fitz.open(stream=file_content, filetype="pdf")
        text_content = []
        
        # Loop setiap halaman (dibatasi max_pages)
        for i, page in enumerate(doc):
            if i >= max_pages:
                break
                
            text = page.get_text()
            
            # Basic Cleaning: Hapus whitespace berlebih
            # Mengubah "Hello    World" jadi "Hello World"
            clean_text = " ".join(text.split())
            
            if len(clean_text) > 50: # Abaikan halaman kosong/sedikit teks
                text_content.append(f"--- Page {i+1} ---\n{clean_text}")
        
        full_text = "\n\n".join(text_content)
        
        if not full_text:
            raise ValueError("Tidak ada teks terbaca. PDF mungkin berupa scan gambar.")
            
        return full_text

    except Exception as e:
        print(f"Error reading PDF: {e}")
        raise ValueError("File korup atau bukan PDF valid.")