import streamlit as st
from ebooklib import epub
import bs4
import re

# פונקציית היפוך חזקה
def reverse_hebrew_logic(text):
    if not text or not isinstance(text, str):
        return text
    # מוצא רצפים של עברית והופך אותם
    return re.sub(r'[\u0590-\u05FF]+', lambda m: m.group(0)[::-1], text)

st.set_page_config(page_title="Kindle Hebrew Fixer", page_icon="📖")
st.title("📖 מתקן עברית לקינדל (EPUB)")

uploaded_file = st.file_uploader("תעלה קובץ EPUB", type="epub")

if uploaded_file:
    # שמירת הקובץ בזיכרון
    input_data = uploaded_file.read()
    with open("temp_in.epub", "wb") as f:
        f.write(input_data)
    
    try:
        book = epub.read_epub("temp_in.epub")
        title = "book"
        title_meta = book.get_metadata('DC', 'title')
        if title_meta: title = title_meta[0][0]
        
        st.info(f"ספר מזוהה: {title}")

        if st.button("תקן עברית (EPUB)"):
            with st.spinner("מתקן עברית..."):
                for item in book.get_items_of_type(10): # HTML items
                    content = item.get_content().decode('utf-8', errors='ignore')
                    soup = bs4.BeautifulSoup(content, 'html.parser')
                    
                    for text_node in soup.find_all(text=True):
                        if text_node.parent.name not in ['script', 'style']:
                            if text_node.string:
                                text_node.replace_with(reverse_hebrew_logic(text_node.string))
                    
                    item.set_content(str(soup).encode('utf-8'))
                
                output_name = "fixed_hebrew.epub"
                epub.write_epub(output_name, book)
                
                with open(output_name, "rb") as f:
                    st.success("הקובץ מוכן!")
                    st.download_button(
                        label="הורד EPUB מתוקן",
                        data=f,
                        file_name=f"{title}_fixed.epub",
                        mime="application/epub+zip"
                    )
    except Exception as e:
        st.error(f"שגיאה: {e}")
