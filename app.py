import streamlit as st
import streamlit.components.v1 as components
import os
import base64

# --- 1. 頁面設定 ---
st.set_page_config(
    page_title="南島玉路：完美對齊版",
    page_icon="🗺️",
    layout="wide"
)

# --- 2. CSS：定義高度與樣式 ---
st.markdown("""
    <style>
    /* === 關鍵修改：字體改為適中 (20px) === */
    .stMarkdown p, .stMarkdown li, .stMarkdown h3 { 
        font-size: 20px !important;  /* 從 24px 改為 20px */
        line-height: 1.5 !important; /* 行距稍微收緊 */
    }
    
    h1 { 
        padding-top: 0px !important; 
        padding-bottom: 20px !important; 
    }
    
    /* 右側文字框的樣式 */
    .text-box {
        background-color: #f9f9f9;  /* 淺灰背景 */
        padding: 25px; 
        border: 2px solid #ddd;     /* 邊框 */
        border-radius: 10px;        /* 圓角 */
        height: 600px;              /* 固定高度，跟圖片一樣高 */
        overflow-y: auto;           /* 文字太長時出現捲軸 */
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    /* 調整欄位間距 */
    [data-testid="column"] {
        padding: 0 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. 核心技術：互動地圖 (Google Maps Style) ---
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def show_interactive_map_style(img_path, height=600):
    """
    建立一個互動視窗：左鍵拖曳、滾輪縮放
    高度設定為 600px
    """
    if not os.path.exists(img_path):
        st.error(f"找不到圖片：{img_path}")
        return

    img_base64 = get_base64_image(img_path)
    img_ext = img_path.split('.')[-1]

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{ margin: 0; padding: 0; overflow: hidden; background-color: #ffffff; }}
        #container {{
            width: 100%;
            height: {height}px;
            overflow: hidden;
            cursor: grab;
            display: flex;
            justify_content: center;
            align-items: center;
            border: 2px solid #eee;
            border-radius: 10px;
            background-color: #f0f2f6;
            position: relative;
        }}
        #container:active {{ cursor: grabbing; }}
        img {{
            max-width: 98%;
            max-height: 98%;
            transition: transform 0.1s;
            transform-origin: center center;
        }}
        #controls {{
            position: absolute;
            bottom: 15px;
            right: 15px;
            z-index: 10;
        }}
        button {{
            font-size: 14px;
            cursor: pointer;
            padding: 8px 12px;
            border: 1px solid #ccc;
            background: white;
            border-radius: 4px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        button:hover {{ background: #f0f0f0; }}
    </style>
    </head>
    <body>
    
    <div id="container">
        <img id="zoom-img" src="data:image/{img_ext};base64,{img_base64}">
        <div id="controls">
            <button onclick="resetZoom()">🔄 重置視角</button>
        </div>
    </div>

    <script>
        const img = document.getElementById('zoom-img');
        const container = document.getElementById('container');
        
        let scale = 1;
        let panning = false;
        let pointX = 0;
        let pointY = 0;
        let startX = 0;
        let startY = 0;

        container.addEventListener('wheel', (e) => {{
            e.preventDefault();
            const delta = -Math.sign(e.deltaY);
            if (delta > 0) scale += 0.15; else scale -= 0.15;
            scale = Math.min(Math.max(0.5, scale), 6);
            updateTransform();
        }});

        container.addEventListener('mousedown', (e) => {{
            e.preventDefault();
            startX = e.clientX - pointX;
            startY = e.clientY - pointY;
            panning = true;
        }});

        container.addEventListener('mouseup', () => {{ panning = false; }});
        container.addEventListener('mouseleave', () => {{ panning = false; }});

        container.addEventListener('mousemove', (e) => {{
            e.preventDefault();
            if (!panning) return;
            pointX = (e.clientX - startX);
            pointY = (e.clientY - startY);
            updateTransform();
        }});
        
        function updateTransform() {{
            img.style.transform = `translate(${{pointX}}px, ${{pointY}}px) scale(${{scale}})`;
        }}
        
        function resetZoom() {{
            scale = 1; pointX = 0; pointY = 0;
            updateTransform();
        }}
    </script>
    </body>
    </html>
    """
    components.html(html_code, height=height+10)

# --- 4. 資料夾管理 ---
FOLDERS = {
    "intro": "1_開場",
    "industry": "2_產業",
    "artifact": "3_文物",
    "trade": "4_貿易",
    "summary": "5_結語"
}

def setup_folders():
    if not os.path.exists("images"): os.makedirs("images")
    for f in FOLDERS.values():
        path = os.path.join("images", f)
        if not os.path.exists(path): os.makedirs(path)

setup_folders()

def get_images_from_folder(key):
    path = os.path.join("images", FOLDERS[key])
    if not os.path.exists(path): return [], path
    files = [f for f in os.listdir(path) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
    files.sort()
    return files, path

def visual_selector(key, label):
    files, path = get_images_from_folder(key)
    if not files:
        st.warning(f"⚠️ `{path}` 是空的，請放入圖片。")
        return None
    
    session_key = f"sel_{key}"
    if session_key not in st.session_state: st.session_state[session_key] = None
    
    with st.expander(f"📂 更換圖片 ({len(files)} 張可用)", expanded=False):
        cols = st.columns(6)
        for i, f in enumerate(files):
            with cols[i%6]:
                st.image(os.path.join(path, f), use_container_width=True)
                if st.button("選用", key=f"btn_{key}_{i}"):
                    st.session_state[session_key] = os.path.join(path, f)
    return st.session_state[session_key]

# --- 5. 側邊欄 ---
with st.sidebar:
    st.title("🗿 南島玉路導航")
    menu = st.radio("章節", ["1. 開場", "2. 產業", "3. 文物", "4. 貿易", "5. 結語"])
    st.markdown("---")
    if st.button("⏱️ 30秒計時"):
        import time
        b = st.progress(100)
        for i in range(30):
            time.sleep(1)
            b.progress(100 - int((i+1)/30*100))

# --- 6. 主畫面邏輯 (左圖右文，高度固定) ---

def render_aligned_section(title, folder_key, desc_html, quiz=None):
    st.title(title)
    
    # 1. 選圖片
    img_path = visual_selector(folder_key, title)
    st.markdown("---")
    
    if img_path:
        # 2. 分割畫面：左 3.5 : 右 2
        col_img, col_text = st.columns([3.5, 2])
        
        # --- 左邊：圖片區 (高度 600px) ---
        with col_img:
            show_interactive_map_style(img_path, height=600)
            
        # --- 右邊：文字區 (高度 600px) ---
        with col_text:
            quiz_html = ""
            if quiz:
                quiz_html = f"<hr><strong>🧠 隨堂小考：{quiz['q']}</strong><br><br>✅ 答案：{quiz['a']}"
            
            # 使用 .text-box 樣式 (字體已改為適中)
            st.markdown(f"""
            <div class="text-box">
                {desc_html}
                {quiz_html}
            </div>
            """, unsafe_allow_html=True)
            
            st.caption("👈 左側圖片可縮放 | 右側文字可捲動")

    else:
        st.info("👈 請點擊上方的「📂」按鈕選擇一張圖片開始講解。")
        st.markdown(desc_html)

# === 章節內容定義 ===

if menu == "1. 開場":
    render_aligned_section(
        "🌊 南島玉路：3000年前的貿易網", "intro",
        """
        ### 📖 核心概念
        
        這是一條由「玉石」鋪成的海上絲路，比西方的絲路更早、更海洋。
        
        * **主角**：台灣花蓮豐田玉 (Nephrite)。
        * **範圍**：跨越 3000 公里，連結台灣、菲律賓、越南、泰國。
        * **意義**：這證明了台灣原住民（南島語族）在 3000 年前就是海洋貿易的霸主。
        
        > **講者提示**：
        > 可以請觀眾看地圖，指出台灣的位置，強調我們是整個網絡的起點。
        """
    )

elif menu == "2. 產業":
    render_aligned_section(
        "⚒️ 巨石與製玉工業", "industry",
        """
        ### 🏭 史前工業園區
        
        我們在花蓮看到的不是簡單的家庭代工，而是「重工業」。
        
        **1. 獨特的原料 (DNA)**
        * 豐田玉擁有世界罕見的 **高鋅 (Zn)** 成分。
        * 這成為科學家追蹤它的化學指紋。
        
        **2. 巨石機具**
        * 圖片中的 **月眉石槽** 或 **石棺**，表面有長期研磨的痕跡。
        * 考古學家證實，這些是大型的「磨玉工作檯」，用來量產玉器。
        """
    )

elif menu == "3. 文物":
    render_aligned_section(
        "💎 玉器密碼：造型解析", "artifact",
        """
        ### 1. 人獸形玉玦 (國寶)
        * **造型**：雙人叉腰，頭頂雲豹。
        * **巧思**：獸腳即人頭，人獸合一。
        * **意義**：象徵狩獵榮耀或祖靈守護。
        
        ### 2. Lingling-O (四突起)
        * **造型**：像是有四個角的圓環。
        * **功能**：跨國貿易的「通行證」。
        * **證據**：在台灣、菲律賓、越南出土的款式一模一樣，代表我們屬於同一個文化圈。
        """
    )

elif menu == "4. 貿易":
    render_aligned_section(
        "⛵ 季節性航海物流", "trade",
        """
        ### 🌊 靠天吃飯的航海術
        
        請操作左圖放大，觀察洋流箭頭：
        
        **❄️ 冬天 (去程：南下)**
        * 利用 **東北季風** 加上 **中國沿岸流**。
        * 船隻順風順水，快速衝向菲律賓。
        
        **☀️ 夏天 (回程：北返)**
        * 利用 **西南季風** 加上 **黑潮 (Kuroshio)**。
        * 黑潮是強勁的海上高速公路，把商船帶回台灣。
        """
    )

elif menu == "5. 結語":
    render_aligned_section(
        "📝 結語：我們是海洋的子民", "summary",
        """
        ### 🌟 演講總結
        
        透過這塊石頭，我們找回了失落的歷史：
        
        1.  **技術自信**：我們擁有世界級的玉石加工技術。
        2.  **海洋視野**：台灣從不是孤島，而是連結世界的樞紐。
        3.  **文化連結**：玉器見證了千年前跨越海洋的友誼。
        
        這條南島玉路，就是台灣迎向世界的證明。
        """,
        quiz={'q': "科學家靠哪種元素確認玉石來自台灣？", 'a': "鋅 (Zn)"}
    )