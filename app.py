import streamlit as st
from ebooklib import epub
import bs4
import os
import subprocess

# פונקציית היפוך חזקה יותר
def reverse_hebrew_logic(text):
    if text is None or not isinstance(text, str): 
        return ""
    words = text.split()
    reversed_words = [word[::-1] if any('\u0590' <= char <= '\u05fe' for char in word) else word for word in words]
    return " ".join(reversed_words)

st.set_page_config(page_title="Kindle Fixed", page_icon="📖")
st.title("📖 ממיר לקינדל - עברית הפוכה")

uploaded_file = st.file_uploader("תעלה קובץ EPUB", type="epub")

if uploaded_file:
    with open("input.epub", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    try:
        # פתיחת הספר במצב "סלחני"
        book = epub.read_epub("input.epub")
        
        # שליפת מטה-דאטה בזהירות
        title = "Unknown_Book"
        author = "Unknown_Author"
        try:
            title_meta = book.get_metadata('DC', 'title')
            if title_meta: title = title_meta[0][0]
            author_meta = book.get_metadata('DC', 'creator')
            if author_meta: author = author_meta[0][0]
        except: pass
        
        st.info(f"**ספר:** {title} | **סופר:** {author}")

        if st.button("המר ל-AZW3"):
            with st.spinner("מעבד טקסט..."):
                for item in book.get_items_of_type(10):
                    try:
                        content = item.get_content().decode('utf-8', errors='ignore')
                        soup = bs4.BeautifulSoup(content, 'html.parser')
                        
                        # טיפול בטקסט בזהירות רבה
                        for text_node in soup.find_all(text=True):
                            if text_node and text_node.string:
                                if text_node.parent.name not in ['script', 'style']:
                                    new_text = reverse_hebrew_logic(text_node.string)
                                    text_node.replace_with(new_text)
                        
                        item.set_content(str(soup).encode('utf-8'))
                    except:
                        continue # מדלג על פרקים בעייתיים במקום לקרוס
                
                output_epub = "temp_fixed.epub"
                epub.write_epub(output_epub, book)
                
                output_azw3 = "output.azw3"
                # הפעלת Calibre עם הגדרות לקידוד עברית
                result = subprocess.run([
                    'ebook-convert', output_epub, output_azw3,
                    '--input-encoding', 'utf-8',
                    '--output-encoding', 'utf-8'
                ], capture_output=True, text=True)
                
                if os.path.exists(output_azw3):
                    with open(output_azw3, "rb") as f:
                        st.success("הקובץ מוכן!")
                        st.download_button("הורד קובץ AZW3 לקינדל", f, file_name=f"{title}.azw3")
                else:
                    st.error("ההמרה ל-AZW3 נכשלה.")
                    st.code(result.stderr)
    except Exception as e:
        st.error(f"שגיאה כללית: {e}")
