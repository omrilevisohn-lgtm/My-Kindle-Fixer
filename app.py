import streamlit as st
import zipfile
import os
import re
import io
import subprocess

# פונקציה שהופכת רק את האותיות בתוך המילה
def reverse_letters_only(text):
    if not text: return text
    # מחפש רצפים של עברית והופך את סדר האותיות שלהם
    return re.sub(r'[\u0590-\u05FF]+', lambda m: m.group(0)[::-1], text)

def get_meta_simple(input_path):
    try:
        result = subprocess.run(['ebook-meta', input_path], capture_output=True, text=True)
        meta_text = result.stdout
        title = re.search(r'Title\s*:\s*(.*)', meta_text)
        author = re.search(r'Author\(s\)\s*:\s*(.*)', meta_text)
        t = title.group(1).strip() if title else "Book"
        a = author.group(1).strip() if author else "Author"
        return t, a
    except:
        return "Fixed_Book", "Unknown"

st.set_page_config(page_title="Kindle Hebrew Fixer", page_icon="📖")
st.title("📖 ממיר לקינדל - גרסה סופית")

uploaded_file = st.file_uploader("תעלה קובץ EPUB", type="epub")

if uploaded_file:
    input_path = "input.epub"
    output_path = "output.azw3"
    temp_epub = "temp_fixed.epub"
    
    file_bytes = uploaded_file.read()
    with open(input_path, "wb") as f:
        f.write(file_bytes)
    
    book_title, book_author = get_meta_simple(input_path)
    st.info(f"**מזוהה:** {book_title} - {book_author}")

    if st.button("המר ל-AZW3"):
        with st.spinner("מבצע תיקון סופי..."):
            try:
                # שלב 1: היפוך אותיות בלבד בתוך ה-ZIP
                in_io = io.BytesIO(file_bytes)
                out_io = io.BytesIO()
                with zipfile.ZipFile(in_io) as inzip:
                    with zipfile.ZipFile(out_io, "w") as outzip:
                        for item in inzip.infolist():
                            content = inzip.read(item.filename)
                            if item.filename.endswith(('.html', '.xhtml', '.htm', '.ncx', '.opf')):
                                try:
                                    text_content = content.decode('utf-8', errors='ignore')
                                    # תיקון: הופך אותיות רק בטקסט (לא בתגים)
                                    fixed = re.sub(r'([^<]+)(?=[^>]*<|$)', lambda m: reverse_letters_only(m.group(1)), text_content)
                                    outzip.writestr(item.filename, fixed.encode('utf-8'))
                                except:
                                    outzip.writestr(item.filename, content)
                            else:
                                outzip.writestr(item.filename, content)
                
                with open(temp_epub, "wb") as f:
                    f.write(out_io.getvalue())

                # שלב 2: המרה נקייה ל-AZW3
                subprocess.run(['ebook-convert', temp_epub, output_path], capture_output=True)
                
                if os.path.exists(output_path):
                    with open(output_path, "rb") as f:
                        st.balloons()
                        st.success(f"הספר '{book_title}' מוכן!")
                        st.download_button(
                            label="הורד קובץ AZW3",
                            data=f,
                            file_name=f"{book_title} - {book_author}.azw3",
                            mime="application/octet-stream"
                        )
            except Exception as e:
                st.error(f"שגיאה: {e}")
