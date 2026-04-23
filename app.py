import streamlit as st
import os
import subprocess
import re

def get_meta_simple(input_path):
    """חילוץ שם וסופר בעזרת פקודה של Calibre"""
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
    
    with open(input_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    book_title, book_author = get_meta_simple(input_path)
    st.info(f"**מזוהה:** {book_title} - {book_author}")

    if st.button("המר ל-AZW3"):
        with st.spinner("מבצע המרה חכמה..."):
            # פקודת ההמרה: 
            # 1. הופכת אותיות בעזרת ה-Script שכבר ראינו
            # 2. מוסיפה CSS שמתקן את סדר המילים (RTL)
            convert_command = [
                'ebook-convert', input_path, output_path,
                '--language', 'he',
                '--extra-css', 'body { direction: rtl !important; unicode-bidi: bidi-override !important; }',
                '--linearize-tables',
                '--subset-embedded-fonts'
            ]
            
            # שלב א' - המרה רגילה עם תיקון כיווניות
            result = subprocess.run(convert_command, capture_output=True, text=True)
            
            if os.path.exists(output_path):
                with open(output_path, "rb") as f:
                    st.balloons()
                    st.success("הצלחנו!")
                    st.download_button(
                        label="הורד קובץ AZW3",
                        data=f,
                        file_name=f"{book_title} - {book_author}.azw3",
                        mime="application/octet-stream"
                    )
            else:
                st.error("ההמרה נכשלה.")
                st.code(result.stderr)
