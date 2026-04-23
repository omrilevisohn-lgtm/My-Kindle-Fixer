import streamlit as st
from ebooklib import epub
import os
import subprocess
import re
import shutil

# פונקציית היפוך חזקה
def reverse_hebrew_in_html(html_content):
    if not html_content: return ""
    hebrew_regex = r'[\u0590-\u05FF]+'
    return re.sub(hebrew_regex, lambda m: m.group(0)[::-1], html_content)

st.set_page_config(page_title="Kindle Fixed", page_icon="📖")
st.title("📖 ממיר לקינדל - גרסה סופית")

uploaded_file = st.file_uploader("תעלה קובץ EPUB", type="epub")

if uploaded_file:
    # ניקוי שאריות מהרצה קודמת
    if os.path.exists('temp_folder'): shutil.rmtree('temp_folder')
    
    # שמירת הקובץ עם סיומת ברורה
    input_path = "input_book.epub"
    with open(input_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # ניסיון לשלוף מטה-דאטה (שם וסופר)
    try:
        book = epub.read_epub(input_path)
        title = book.get_metadata('DC', 'title')[0][0] if book.get_metadata('DC', 'title') else "Unknown"
        author = book.get_metadata('DC', 'creator')[0][0] if book.get_metadata('DC', 'creator') else "Unknown"
        st.info(f"**ספר:** {title} | **סופר:** {author}")
    except:
        title = "Fixed_Book"
        st.warning("לא הצלחתי לקרוא את פרטי הספר, אבל נמשיך בהמרה.")

    if st.button("המר ל-AZW3"):
        with st.spinner("מבצע המרה... זה לוקח דקה"):
            # שלב 1: פירוק ה-EPUB לתיקייה
            os.makedirs('temp_folder', exist_ok=True)
            subprocess.run(['ebook-convert', input_path, 'temp_folder'], capture_output=True)
            
            # שלב 2: היפוך עברית בקבצי התוכן
            for root, dirs, files in os.walk('temp_folder'):
                for file in files:
                    if file.endswith(('.html', '.xhtml', '.htm')):
                        path = os.path.join(root, file)
                        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        with open(path, 'w', encoding='utf-8') as f:
                            f.write(reverse_hebrew_in_html(content))
            
            # שלב 3: אריזה מחדש ל-AZW3
            # הוספת הסיומת .epub לתיקייה כדי ש-Calibre יבין שזה מקור של ספר
            output_azw3 = "output.azw3"
            # פקודה שיוצרת את הקובץ מתוך תוכן התיקייה
            result = subprocess.run(['ebook-convert', 'temp_folder/metadata.opf', output_azw3], capture_output=True, text=True)
            
            if os.path.exists(output_azw3):
                with open(output_azw3, "rb") as f:
                    st.success("הצלחנו!")
                    st.download_button(
                        label="הורד קובץ לקינדל",
                        data=f,
                        file_name=f"{title}.azw3",
                        mime="application/octet-stream"
                    )
            else:
                st.error("ההמרה נכשלה.")
                st.code(result.stderr)
