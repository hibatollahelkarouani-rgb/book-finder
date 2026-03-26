import requests  # bach nsiftou demandes l internet
import gradio as gr   # bach nbaniwi l interface
from urllib.parse import quote   # bach nencodi les caractères spéciaux
import re  #Regex bhalha filtre dyal texte o  patterns 

API_KEY = "AIzaSyDXYPdl0vFYKAG1srde9QMEBKAVuaYFkNo"

def search_book(title):
    encoded_title = quote(title)
    
    # Google Books - cover + info
    gb_url = f"https://www.googleapis.com/books/v1/volumes?q=intitle:{encoded_title}&key={API_KEY}"
    gb_data = requests.get(gb_url).json()
    
    if not gb_data.get("items"):
        return "<div style='text-align:center;padding:40px;color:#e57373;font-family:Nunito;font-size:1.1rem;'>❌ Book not found</div>"
    
    book = None
    for item in gb_data["items"]:
        if item["volumeInfo"].get("imageLinks"):
            book = item["volumeInfo"]
            break
    if not book:
        book = gb_data["items"][0]["volumeInfo"]
    
    title_result = book.get("title", "Unknown")
    author = ", ".join(book.get("authors", ["Unknown"]))
    categories = book.get("categories", [])
    subject = categories[0] if categories else "Literature"
    image_url = book.get("imageLinks", {}).get("extraLarge") or \
                book.get("imageLinks", {}).get("large") or \
                book.get("imageLinks", {}).get("medium") or \
                book.get("imageLinks", {}).get("thumbnail", None)

    # Open Library - description + first_publish_year
    ol_url = f"https://openlibrary.org/search.json?title={encoded_title}&limit=10"
    ol_data = requests.get(ol_url).json()
    description = "No description available."
    published = book.get("publishedDate", "Unknown")[:4]
    
    if ol_data.get("docs"):
        for doc in ol_data["docs"]:
            doc_title = doc.get("title", "").lower()
            if title.lower() not in doc_title:
                continue
            
            # first_publish_year mn Open Library
            if doc.get("first_publish_year"):
                published = str(doc["first_publish_year"])
            
            work_key = doc.get("key", "")
            if work_key:
                work_data = requests.get(f"https://openlibrary.org{work_key}.json").json()
                desc = work_data.get("description", "")
                if isinstance(desc, dict):
                    desc = desc.get("value", "")
                if desc:
                    desc = re.sub(r'\[.*?\]\(.*?\)', '', desc)
                    desc = re.sub(r'\[\d+\]', '', desc)
                    desc = re.sub(r'----------.*', '', desc, flags=re.DOTALL)
                    description = desc.strip()
                    break

    if not image_url and ol_data.get("docs"):
        cover_id = ol_data["docs"][0].get("cover_i")
        if cover_id:
            image_url = f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"

    cover_html = f'''
        <img src="{image_url}" style="
            width: 130px;
            border-radius: 16px;
            box-shadow: 4px 4px 0px #f0b8c8, 8px 8px 0px #ffd6e0;
            transition: transform 0.3s ease;
        " onmouseover="this.style.transform='rotate(-3deg) scale(1.05)'"
           onmouseout="this.style.transform='rotate(0deg) scale(1)'">
    ''' if image_url else "📚"

    short_desc = description[:350] + "..." if len(description) > 350 else description

    result_html = f"""
    <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap" rel="stylesheet">
    <div style="
        font-family: 'Nunito', sans-serif;
        background: linear-gradient(135deg, #fff0f5 0%, #f0f4ff 100%);
        border-radius: 24px;
        padding: 24px;
        border: 2px solid #ffd6e0;
        box-shadow: 0 8px 32px rgba(255,182,193,0.2);
    ">
        <div style="display:flex; gap:24px; align-items:flex-start;">
            <div style="flex-shrink:0; text-align:center;">
                {cover_html}
            </div>
            <div style="flex:1;">
                <div style="font-size:1.4rem;font-weight:800;color:#5c3d6e;margin-bottom:4px;line-height:1.3;">
                    {title_result}
                </div>
                <div style="color:#e591b0;font-weight:600;font-size:0.95rem;margin-bottom:14px;">
                    ✍️ {author}
                </div>
                <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px;">
                    <span style="background:#ffe0ec;color:#c4607a;padding:4px 14px;border-radius:20px;font-size:0.78rem;font-weight:700;border:1.5px solid #ffb6cb;">📅 {published}</span>
                    <span style="background:#e8e0ff;color:#7c5cbf;padding:4px 14px;border-radius:20px;font-size:0.78rem;font-weight:700;border:1.5px solid #c9b8ff;">🎭 {subject}</span>
                </div>
                <div style="background:rgba(255,255,255,0.7);border-radius:16px;padding:14px 16px;color:#6b5b7b;font-size:0.88rem;line-height:1.7;border:1.5px solid #ffd6e0;">
                    📝 {short_desc}
                </div>
            </div>
        </div>
    </div>
    """
    return result_html

css = """
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');
* { box-sizing: border-box; }
body {
    background: linear-gradient(160deg, #fff0f8 0%, #f0f0ff 100%) !important;
    font-family: 'Nunito', sans-serif !important;
    min-height: 100vh !important;
}
.gradio-container {
    max-width: 780px !important;
    margin: 0 auto !important;
    padding: 40px 24px !important;
    background: transparent !important;
}
.gradio-container h1 {
    font-family: 'Nunito', sans-serif !important;
    font-size: 2.6rem !important;
    font-weight: 800 !important;
    color: #5c3d6e !important;
    text-align: center !important;
    margin-bottom: 4px !important;
}
.gradio-container > div > div > p {
    color: #c48aaa !important;
    text-align: center !important;
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    margin-bottom: 30px !important;
    letter-spacing: 1px !important;
}
input[type="text"], textarea {
    background: #ffffff !important;
    border: 2px solid #ffd6e0 !important;
    border-radius: 16px !important;
    color: #5c3d6e !important;
    font-family: 'Nunito', sans-serif !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    padding: 14px 18px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 16px rgba(255,182,193,0.15) !important;
}
input[type="text"]:focus, textarea:focus {
    border-color: #e591b0 !important;
    box-shadow: 0 4px 20px rgba(229,145,176,0.25) !important;
    outline: none !important;
}
label span {
    color: #c48aaa !important;
    font-family: 'Nunito', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 700 !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
}
#search-btn {
    background: linear-gradient(135deg, #f48fb1, #ce93d8) !important;
    color: #fff !important;
    font-family: 'Nunito', sans-serif !important;
    font-size: 1rem !important;
    font-weight: 800 !important;
    letter-spacing: 1px !important;
    border: none !important;
    border-radius: 16px !important;
    padding: 13px 36px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 20px rgba(244,143,177,0.4) !important;
    width: 100% !important;
}
#search-btn:hover {
    transform: translateY(-3px) scale(1.02) !important;
    box-shadow: 0 8px 30px rgba(244,143,177,0.5) !important;
}
.block {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
}
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #fff0f8; }
::-webkit-scrollbar-thumb { background: #ffd6e0; border-radius: 10px; }

#clear-btn {
    background: #fff0f5 !important;
    color: #e591b0 !important;
    font-family: 'Nunito', sans-serif !important;
    font-size: 1rem !important;
    font-weight: 800 !important;
    letter-spacing: 1px !important;
    border: 2px solid #ffd6e0 !important;
    border-radius: 16px !important;
    padding: 13px 36px !important;
    transition: all 0.3s ease !important;
    width: 100% !important;
}
#clear-btn:hover {
    background: #ffe0ec !important;
    transform: translateY(-3px) scale(1.02) !important;
}
"""

with gr.Blocks(theme=gr.themes.Base(), css=css) as interface:
    gr.Markdown("# 🌸 Book Finder")
    gr.Markdown("✨ search · discover · explore ✨")
    inp = gr.Textbox(label="Book Title", placeholder="ex: Harry Potter, Les Misérables...")
    
    with gr.Row():
        btn = gr.Button(" Search", elem_id="search-btn")
        clear_btn = gr.Button(" Clear", elem_id="clear-btn")
    
    out = gr.HTML()
    
    btn.click(fn=search_book, inputs=inp, outputs=out)
    clear_btn.click(fn=lambda: ("", ""), outputs=[inp, out])

interface.launch(share=True)