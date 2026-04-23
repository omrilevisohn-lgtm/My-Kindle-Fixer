import streamlit as st
import zipfile
import os
import re
import io
import subprocess

# פונקציית היפוך חזקה
def reverse_hebrew_text(text):
    if not text: return text
    return re.sub(r'[\u0590-\u05FF]+', lambda m: m.group(0)[::-1], text)

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
                        fixed_text = reverse_hebrew_text(text_content)
                        outzip.writestr(item.filename, fixed_text.encode('utf-8'))
                    except:
                        outzip.writestr(item, content)
                else:
                    outzip.writestr(item, content)
    return out_io.getvalue()

st.set_page_config(page_title="Kindle Hebrew Fixer", page_icon="📖")
st.title("📖 ממיר לקינדל - AZW3 עברית ישרה")

uploaded_file = st.file_uploader("תעלה קובץ EPUB", type="epub")

if uploaded_file:
    st.success("הקובץ נקלט!")
    
    if st.button("המר ל-AZW3"):
        with st.spinner("מתקן עברית וממיר לפורמט קינדל..."):
            try:
                # שלב 1: תיקון העברית בזיכרון (השיטה היציבה)
                fixed_epub_bytes = fix_epub_in_memory(uploaded_file.read())
                
                # שלב 2: שמירה זמנית לדיסק לצורך המרה
                with open("temp_fixed.epub", "wb") as f:
                    f.write(fixed_epub_bytes)
                
                # שלב 3: המרה ל-AZW3 בעזרת Calibre
                output_azw3 = "output_book.azw3"
                # הוספנו דגל שמבטיח כיוון טקסט מימין לשמאל
                subprocess.run([
                    'ebook-convert', "temp_fixed.epub", output_azw3,
                    '--language', 'he',
                    '--extra-css', 'body { direction: rtl !important; }'
                ], capture_output=True)
                
                if os.path.exists(output_azw3):
                    with open(output_azw3, "rb") as f:
                        st.balloons()
                        st.success("הקובץ מוכן בפורמט AZW3!")
                        st.download_button(
                            label="הורד AZW3 לקינדל",
                            data=f,
                            file_name="fixed_book.azw3",
                            mime="application/octet-stream"
                        )
                else:
                    st.error("ההמרה ל-AZW3 נכשלה בשרת. נסה להוריד כ-EPUB.")
                    st.download_button("הורד כ-EPUB מתוקן", fixed_epub_bytes, file_name="fixed.epub")
                    
            except Exception as e:
                st.error(f"שגיאה: {e}")
