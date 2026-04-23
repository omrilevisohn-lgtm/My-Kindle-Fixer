import streamlit as st
import zipfile
import os
import re
import io

# פונקציית היפוך חזקה שעובדת על טקסט נקי
def reverse_hebrew_text(text):
    if not text: return text
    # מוצא רצפים של עברית והופך אותם
    return re.sub(r'[\u0590-\u05FF]+', lambda m: m.group(0)[::-1], text)

def fix_epub_hebrew(input_bytes):
    # פותחים את ה-EPUB כקובץ ZIP (כי זה מה שהוא באמת)
    with zipfile.ZipFile(io.BytesIO(input_bytes)) as inzip:
        out_io = io.BytesIO()
        with zipfile.ZipFile(out_io, "w") as outzip:
            for item in inzip.infolist():
                content = inzip.read(item.filename)
                # מטפלים רק בקבצי טקסט (HTML/XML)
                if item.filename.endswith(('.html', '.xhtml', '.htm', '.ncx', '.opf')):
                    try:
                        text_content = content.decode('utf-8')
                        # הופכים את העברית בתוך הטקסט
                        fixed_text = reverse_hebrew_text(text_content)
                        outzip.writestr(item.filename, fixed_text.encode('utf-8'))
                    except:
                        outzip.writestr(item, content)
                else:
                    # קבצים אחרים (תמונות, פונטים) פשוט מעתיקים
                    outzip.writestr(item, content)
        return out_io.getvalue()

st.set_page_config(page_title="Kindle Hebrew Fixer", page_icon="📖")
st.title("📖 מתקן עברית לקינדל - גרסה ללא קריסות")

uploaded_file = st.file_uploader("תעלה קובץ EPUB", type="epub")

if uploaded_file:
    st.success("הקובץ נקלט בהצלחה!")
    
    if st.button("תקן עברית"):
        with st.spinner("מתקן..."):
            try:
                fixed_epub = fix_epub_hebrew(uploaded_file.read())
                
                st.balloons()
                st.download_button(
                    label="הורד EPUB מתוקן",
                    data=fixed_epub,
                    file_name="fixed_book.epub",
                    mime="application/epub+zip"
                )
                st.info("טיפ: את הקובץ הזה כדאי לשלוח לקינדל דרך האתר Send to Kindle של אמזון.")
            except Exception as e:
                st.error(f"שגיאה בתהליך: {e}")
