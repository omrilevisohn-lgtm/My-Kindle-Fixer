import streamlit as st
import os
import subprocess
import re

# פונקציה פשוטה וחזקה להיפוך עברית בתוך טקסט HTML
def reverse_hebrew_in_html(html_content):
    if not html_content:
        return ""
    
    # פונקציה פנימית להיפוך מילים בעברית בלבד
    def reverse_match(match):
        word = match.group(0)
        return word[::-1]

    # רגקס שמוצא רצפים של אותיות בעברית (כולל סופיות)
    hebrew_regex = r'[\u0590-\u05FF]+'
    return re.sub(hebrew_regex, reverse_match, html_content)

st.set_page_config(page_title="Kindle Fixed", page_icon="📖")
st.title("📖 ממיר לקינדל - גרסה יציבה")

uploaded_file = st.file_uploader("תעלה קובץ EPUB", type="epub")

if uploaded_file:
    # שמירת הקובץ המקורי
    with open("original.epub", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.success("הקובץ הועלה בהצלחה!")

    if st.button("המר ל-AZW3"):
        with st.spinner("מבצע המרה חכמה..."):
            # שלב 1: פתיחת ה-EPUB לתיקייה זמנית בעזרת Calibre
            subprocess.run(['ebook-convert', 'original.epub', 'temp_folder/'], capture_output=True)
            
            # שלב 2: מעבר על כל קבצי ה-HTML בתיקייה והיפוך העברית
            for root, dirs, files in os.walk('temp_folder/'):
                for file in files:
                    if file.endswith(('.html', '.xhtml', '.htm')):
                        path = os.path.join(root, file)
                        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        fixed_content = reverse_hebrew_in_html(content)
                        
                        with open(path, 'w', encoding='utf-8') as f:
                            f.write(fixed_content)
            
            # שלב 3: אריזה מחדש ל-AZW3
            output_file = "fixed_book.azw3"
            result = subprocess.run(['ebook-convert', 'temp_folder/', output_file], capture_output=True, text=True)
            
            if os.path.exists(output_file):
                with open(output_file, "rb") as f:
                    st.success("הספר מוכן להורדה!")
                    st.download_button(
                        label="הורד קובץ AZW3",
                        data=f,
                        file_name="fixed_book.azw3",
                        mime="application/octet-stream"
                    )
            else:
                st.error("ההמרה נכשלה. נסה קובץ אחר.")
                st.code(result.stderr)
