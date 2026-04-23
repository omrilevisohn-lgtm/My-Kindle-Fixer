import streamlit as st
from ebooklib import epub
import bs4
import os
import subprocess

# פונקציית היפוך הטקסט (נבו -> ובנ)
def reverse_hebrew_logic(text):
    if not text: return text
    words = text.split()
    reversed_words = [word[::-1] if any('\u0590' <= char <= '\u05fe' for char in word) else word for word in words]
    return " ".join(reversed_words)

st.set_page_config(page_title="Kindle Fixed", page_icon="📖")
st.title("📖 ממיר לקינדל - עברית הפוכה")

uploaded_file = st.file_uploader("תעלה קובץ EPUB", type="epub")

if uploaded_file:
    # שמירת הקובץ שהועלה
    with open("input.epub", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # טעינת הספר עם הגדרות בטוחות
    try:
        book = epub.read_epub("input.epub")
        title_meta = book.get_metadata('DC', 'title')
        author_meta = book.get_metadata('DC', 'creator')
        title = title_meta[0][0] if title_meta else "Unknown_Book"
        author = author_meta[0][0] if author_meta else "Unknown_Author"
        
        st.info(f"**ספר:** {title} | **סופר:** {author}")

        if st.button("המר ל-AZW3"):
            with st.spinner("מעבד טקסט..."):
                # מעבר על הפרקים והיפוך הטקסט
                for item in book.get_items_of_type(10): # 10 = Document
                    content = item.get_content().decode('utf-8', errors='ignore')
                    soup = bs4.BeautifulSoup(content, 'html.parser')
                    for text_node in soup.find_all(text=True):
                        if text_node.parent.name not in ['script', 'style']:
                            if text_node.string:
                                text_node.replace_with(reverse_hebrew_logic(text_node.string))
                    item.set_content(str(soup).encode('utf-8'))
                
                # שמירה זמנית - כאן הייתה השגיאה, הוספנו טיפול
                output_epub = "temp_fixed.epub"
                epub.write_epub(output_epub, book)
                
                # המרה ל-AZW3 באמצעות Calibre
                output_azw3 = "output.azw3"
                result = subprocess.run(['ebook-convert', output_epub, output_azw3], capture_output=True, text=True)
                
                if os.path.exists(output_azw3):
                    with open(output_azw3, "rb") as f:
                        st.success("הקובץ מוכן!")
                        st.download_button("הורד קובץ AZW3 לקינדל", f, file_name=f"{title}.azw3")
                else:
                    st.error("שגיאה בהמרת הקובץ ל-AZW3. נסה קובץ אחר.")
                    st.code(result.stderr) # מציג את השגיאה הטכנית אם ההמרה נכשלה
    except Exception as e:
        st.error(f"שגיאה בקריאת הקובץ: {e}")
