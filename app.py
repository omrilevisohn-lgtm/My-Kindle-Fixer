import streamlit as st
from ebooklib import epub
import bs4
import os
import subprocess

def reverse_hebrew_logic(text):
    if not text: return text
    words = text.split()
    reversed_words = [word[::-1] if any('\u0590' <= char <= '\u05fe' for char in word) else word for word in words]
    return " ".join(reversed_words)

st.set_page_config(page_title="Kindle Fixed", page_icon="📖")
st.title("📖 ממיר לקינדל - עברית הפוכה")

uploaded_file = st.file_uploader("תעלה קובץ EPUB", type="epub")

if uploaded_file:
    with open("input.epub", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    book = epub.read_epub("input.epub")
    title_meta = book.get_metadata('DC', 'title')
    author_meta = book.get_metadata('DC', 'creator')
    title = title_meta[0][0] if title_meta else "Unknown Title"
    author = author_meta[0][0] if author_meta else "Unknown Author"
    
    st.info(f"**ספר:** {title} | **סופר:** {author}")

    if st.button("המר ל-AZW3"):
        with st.spinner("מעבד..."):
            for item in book.get_items_of_type(10):
                soup = bs4.BeautifulSoup(item.get_content(), 'html.parser')
                for text_node in soup.find_all(text=True):
                    if text_node.parent.name not in ['script', 'style']:
                        text_node.replace_with(reverse_hebrew_logic(text_node.string))
                item.set_content(str(soup).encode('utf-8'))
            
            epub.write_epub("temp.epub", book)
            subprocess.run(['ebook-convert', 'temp.epub', 'output.azw3'])
            
            if os.path.exists("output.azw3"):
                with open("output.azw3", "rb") as f:
                    st.success("מוכן!")
                    st.download_button("הורד קובץ AZW3", f, file_name=f"{title}.azw3")
