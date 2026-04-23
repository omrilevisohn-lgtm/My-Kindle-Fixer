import streamlit as st
import zipfile
import os
import re
import io
import subprocess

# פונקציית היפוך: הופכת אותיות במילה ואת סדר המילים
def reverse_hebrew_logic(text):
    if not text: return text
    words = text.split()
    # הופך אותיות רק במילים עם עברית
    reversed_words = [word[::-1] if any('\u0590' <= char <= '\u05fe' for char in word) else word for word in words]
    # הופך את סדר המילים (כדי ש"משחק האומנת" יוצג נכון בקינדל)
    return " ".join(reversed_words[::-1])

def get_meta_simple(input_bytes):
    """חילוץ שם וסופר ללא ספריות חיצוניות"""
    try:
        content = input_bytes.decode('utf-8', errors='ignore')
        title = re.search(r'<dc:title>(.*?)</dc:title>', content)
        author = re.search(r'<dc:creator.*?>(.*?)</dc:creator>', content)
        t = title.group(1) if title else "Book"
        a = author.group(1) if author else "Author"
        return t, a
    except:
        return "Fixed_Book", "Unknown"

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
                        # הופך טקסט מחוץ לתגי HTML
                        fixed_text = re.sub(r'([^<]+)(?=[^>]*<|$)', lambda m: reverse_hebrew_logic(m.group(1)), text_content)
                        outzip.writestr(item.filename, fixed_text.encode('utf-8'))
                    except:
                        outzip.writestr(item.filename, content)
                else:
                    outzip.writestr(item.filename, content)
    return out_io.getvalue()

st.set_page_config(page_title="Kindle Hebrew Fixer", page_icon="📖")
st.title("📖 ממיר לקינדל - גרסה יציבה")

uploaded_file = st.file_uploader("תעלה קובץ EPUB", type="epub")

if uploaded_file:
    file_bytes = uploaded_file.read()
    book_title, book_author = get_meta_simple(file_bytes)
    st.info(f"**מזוהה:** {book_title} - {book_author}")

    if st.button("המר ל-AZW3"):
        with st.spinner("מעבד..."):
            try:
                # 1. תיקון העברית
                fixed_epub_bytes = fix_epub_in_memory(file_bytes)
                
                # 2. שמירה זמנית להמרה
                with open("temp_fixed.epub", "wb") as f:
                    f.write(fixed_epub_bytes)
                
                # 3. המרה ל-AZW3
                output_azw3 = "output.azw3"
                # הפעלה בסיסית של Calibre
                proc = subprocess.run([
                    'ebook-convert', "temp_fixed.epub", output_azw3
                ], capture_output=True, text=True)
                
                if os.path.exists(output_azw3):
                    with open(output_azw3, "rb") as f:
                        st.balloons()
                        st.download_button(
                            label="הורד קובץ AZW3",
                            data=f,
                            file_name=f"{book_title} - {book_author}.azw3",
                            mime="application/octet-stream"
                        )
                else:
                    st.error("ההמרה נכשלה במערכת.")
                    st.code(proc.stderr) # מציג את השגיאה הטכנית
            except Exception as e:
                st.error(f"שגיאה: {e}")
