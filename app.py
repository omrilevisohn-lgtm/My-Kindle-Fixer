import streamlit as st
import zipfile
import os
import re
import io
import subprocess
from ebooklib import epub

# פונקציית היפוך חכמה: הופכת אותיות בתוך מילה וגם את סדר המילים
def reverse_hebrew_logic(text):
    if not text: return text
    # היפוך האותיות בכל מילה שיש בה עברית
    words = text.split()
    reversed_words = [word[::-1] if any('\u0590' <= char <= '\u05fe' for char in word) else word for word in words]
    # היפוך סדר המילים במשפט כדי ש"משחק האומנת" יהיה "האומנת משחק" בקוד (ויוצג נכון בקינדל)
    return " ".join(reversed_words[::-1])

def fix_epub_in_memory(input_bytes):
    in_io = io.BytesIO(input_bytes)
    out_io = io.BytesIO()
    with zipfile.ZipFile(in_io) as inzip:
        with zipfile.ZipFile(out_io, "w") as outzip:
            for item in inzip.infolist():
                content = inzip.read(item.filename)
                if item.filename.endswith(('.html', '.xhtml', '.htm', '.ncx', '.opf')):
                    try:
                        text_content = content.decode('utf-8', errors='ignore')
                        # שימוש ברגקס כדי למצוא טקסט בין תגים ולטפל רק בו
                        def replace_func(match):
                            return reverse_hebrew_logic(match.group(0))
                        
                        # הופך טקסט שלא נמצא בתוך תגי <>
                        fixed_text = re.sub(r'([^<]+)(?=[^>]*<|$)', lambda m: reverse_hebrew_logic(m.group(1)), text_content)
                        outzip.writestr(item.filename, fixed_text.encode('utf-8'))
                    except:
                        outzip.writestr(item.filename, content)
                else:
                    outzip.writestr(item.filename, content)
    return out_io.getvalue()

st.set_page_config(page_title="Kindle Hebrew Fixer", page_icon="📖")
st.title("📖 ממיר לקינדל - תיקון סדר מילים")

uploaded_file = st.file_uploader("תעלה קובץ EPUB", type="epub")

if uploaded_file:
    # שמירה זמנית כדי לחלץ שם וסופר
    input_bytes = uploaded_file.read()
    with open("temp_meta.epub", "wb") as f:
        f.write(input_bytes)
    
    book_title = "Unknown_Book"
    book_author = "Unknown_Author"
    
    try:
        book = epub.read_epub("temp_meta.epub")
        title_meta = book.get_metadata('DC', 'title')
        if title_meta: book_title = title_meta[0][0]
        author_meta = book.get_metadata('DC', 'creator')
        if author_meta: book_author = author_meta[0][0]
        st.info(f"**מזוהה:** {book_title} - {book_author}")
    except:
        st.warning("לא הצלחתי לקרוא מטה-דאטה, שם הקובץ יהיה גנרי.")

    if st.button("המר ל-AZW3"):
        with st.spinner("מתקן סדר מילים וממיר..."):
            try:
                # שלב 1: תיקון העברית
                fixed_epub_bytes = fix_epub_in_memory(input_bytes)
                
                with open("temp_fixed.epub", "wb") as f:
                    f.write(fixed_epub_bytes)
                
                # שלב 2: המרה ל-AZW3
                output_azw3 = "output.azw3"
                subprocess.run([
                    'ebook-convert', "temp_fixed.epub", output_azw3,
                    '--language', 'he',
                    '--extra-css', 'body { direction: rtl !important; }'
                ], capture_output=True)
                
                if os.path.exists(output_azw3):
                    with open(output_azw3, "rb") as f:
                        st.balloons()
                        # יצירת שם קובץ מותאם
                        final_filename = f"{book_title} - {book_author}.azw3"
                        st.success(f"הספר '{book_title}' מוכן!")
                        st.download_button(
                            label="הורד קובץ AZW3",
                            data=f,
                            file_name=final_filename,
                            mime="application/octet-stream"
                        )
                else:
                    st.error("ההמרה נכשלה.")
            except Exception as e:
                st.error(f"שגיאה: {e}")
