"""
app.py
------
Streamlit UI for Lecture-to-Quiz generator.
Design based on Lumina Study UI.

Run with:
    cd /home/modabbir/Agents/lecture-to-quiz
    streamlit run app.py
"""

import os
import json
import tempfile
import streamlit as st
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.parser import process_text, save_to_json
from utils.pdf import extract_text_from_pdf

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="Lumina Study",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Global CSS ───────────────────────────────────────────────
st.markdown("""
<style>
  /* ── Google Fonts ── */
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
  @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap');

  /* ── Reset & base ── */
  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
  #MainMenu, footer, header { visibility: hidden; }

  /* ── Colour tokens (matches the HTML design) ── */
  :root {
    --primary:          #3c5e91;
    --primary-container:#5677ac;
    --surface:          #f8f9ff;
    --surface-container:#e5eeff;
    --surface-container-low: #eff4ff;
    --surface-container-high:#dce9ff;
    --on-surface:       #0b1c30;
    --secondary:        #595f66;
    --outline-variant:  #c3c6d0;
    --outline:          #737780;
    --white:            #ffffff;
  }

  /* ── Top nav bar ── */
  .top-nav {
    position: fixed;
    top: 0; left: 0; right: 0;
    height: 64px;
    background: var(--white);
    border-bottom: 1px solid var(--outline-variant);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 32px;
    z-index: 999;
  }
  .nav-brand {
    font-size: 20px;
    font-weight: 700;
    color: var(--on-surface);
    letter-spacing: -0.02em;
  }
  .nav-right {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .nav-icon-btn {
    width: 36px; height: 36px;
    border-radius: 8px;
    border: none;
    background: transparent;
    color: var(--secondary);
    display: flex; align-items: center; justify-content: center;
    cursor: pointer;
    font-size: 22px;
  }
  .nav-icon-btn:hover { background: var(--surface-container-low); }
  .avatar {
    width: 32px; height: 32px;
    border-radius: 50%;
    background: var(--surface-container);
    overflow: hidden;
    margin-left: 8px;
  }

  /* ── Side nav ── */
  .side-nav {
    position: fixed;
    top: 64px; left: 0;
    width: 240px;
    height: calc(100vh - 64px);
    background: var(--white);
    border-right: 1px solid var(--outline-variant);
    display: flex;
    flex-direction: column;
    padding: 24px 16px;
    z-index: 998;
  }
  .side-nav-user { padding: 0 16px; margin-bottom: 32px; }
  .side-nav-name { font-size: 20px; font-weight: 500; color: var(--on-surface); }
  .side-nav-sub  { font-size: 12px; color: var(--secondary); letter-spacing: 0.05em; }
  .nav-item {
    display: flex; align-items: center; gap: 12px;
    padding: 8px 16px;
    border-radius: 6px;
    font-size: 12px; font-weight: 500;
    color: var(--secondary);
    text-decoration: none;
    cursor: pointer;
    margin-bottom: 2px;
  }
  .nav-item.active {
    background: #eff4ff;
    color: var(--primary);
    border-right: 2px solid var(--primary);
  }
  .nav-item:hover { background: var(--surface-container-low); }
  .nav-bottom { margin-top: auto; padding-top: 24px; border-top: 1px solid #f1f5f9; }

  /* ── Main canvas ── */
  .main-canvas {
    margin-left: 240px;
    padding-top: 64px;
    min-height: 100vh;
    background: var(--surface);
  }
  .canvas-inner { max-width: 1200px; margin: 0 auto; padding: 32px; }

  /* ── Welcome ── */
  .welcome-title {
    font-size: 32px; font-weight: 600;
    color: var(--on-surface);
    letter-spacing: -0.02em;
    margin-bottom: 4px;
  }
  .welcome-sub {
    font-size: 18px; color: var(--secondary);
  }

  /* ── Cards ── */
  .card {
    background: var(--white);
    border: 1px solid var(--outline-variant);
    border-radius: 12px;
    padding: 32px;
  }
  .card-header {
    display: flex; align-items: center; gap: 12px;
    margin-bottom: 24px;
  }
  .card-icon {
    width: 40px; height: 40px;
    border-radius: 8px;
    background: var(--surface-container-high);
    display: flex; align-items: center; justify-content: center;
    color: var(--primary);
    font-size: 20px;
  }
  .card-title { font-size: 24px; font-weight: 600; color: var(--on-surface); letter-spacing: -0.01em; }

  /* ── Stat mini cards ── */
  .stat-card {
    background: var(--surface-container-low);
    border: 1px solid #f1f5f9;
    border-radius: 12px;
    padding: 16px;
    display: flex; align-items: center; gap: 16px;
  }
  .stat-icon { font-size: 28px; color: var(--primary); }
  .stat-label { font-size: 12px; color: var(--secondary); letter-spacing: 0.05em; }
  .stat-value { font-size: 20px; font-weight: 500; color: var(--on-surface); }

  /* ── Recent lectures panel ── */
  .recent-panel {
    background: var(--white);
    border: 1px solid var(--outline-variant);
    border-radius: 12px;
    overflow: hidden;
  }
  .recent-header {
    padding: 12px 16px;
    border-bottom: 1px solid var(--outline-variant);
    background: var(--surface-container-low);
    display: flex; justify-content: space-between; align-items: center;
  }
  .recent-header-title { font-size: 20px; font-weight: 500; }
  .recent-item {
    padding: 16px;
    border-bottom: 1px solid #f1f5f9;
    display: flex; align-items: flex-start; gap: 12px;
    cursor: pointer;
  }
  .recent-item:hover { background: #f8fafc; }
  .recent-item-title { font-size: 16px; font-weight: 500; color: var(--on-surface); margin-bottom: 4px; }
  .recent-item-time  { font-size: 12px; color: var(--secondary); }

  /* ── Buttons ── */
  .btn-outline {
    display: inline-flex; align-items: center; gap: 8px;
    padding: 10px 20px;
    border: 1px solid var(--outline-variant);
    border-radius: 8px;
    background: transparent;
    color: var(--primary);
    font-size: 14px; font-weight: 500;
    cursor: pointer;
  }
  .btn-outline:hover { background: var(--surface-container-low); }
  .btn-primary {
    display: inline-flex; align-items: center; gap: 8px;
    padding: 10px 32px;
    border: none;
    border-radius: 8px;
    background: var(--primary-container);
    color: var(--white);
    font-size: 14px; font-weight: 600;
    cursor: pointer;
  }
  .btn-primary:hover { opacity: 0.9; }

  /* ── Difficulty badges ── */
  .badge {
    display: inline-block;
    padding: 2px 10px; border-radius: 20px;
    font-size: 11px; font-weight: 600;
  }
  .badge-easy   { background:#dcfce7; color:#166534; border:1px solid #bbf7d0; }
  .badge-medium { background:#fef9c3; color:#854d0e; border:1px solid #fde68a; }
  .badge-hard   { background:#fee2e2; color:#991b1b; border:1px solid #fecaca; }

  /* ── Result tabs styling ── */
  .stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    border-bottom: 1px solid var(--outline-variant);
  }
  .stTabs [data-baseweb="tab"] {
    background: transparent;
    border-radius: 6px 6px 0 0;
    color: var(--secondary);
    font-weight: 500;
    padding: 8px 16px;
  }
  .stTabs [aria-selected="true"] {
    background: var(--surface-container-low) !important;
    color: var(--primary) !important;
    border-bottom: 2px solid var(--primary);
  }

  /* ── Metric cards ── */
  [data-testid="metric-container"] {
    background: var(--surface-container-low);
    border: 1px solid var(--outline-variant);
    border-radius: 10px;
    padding: 16px;
  }

  /* push main content below fixed nav */
  .block-container { padding-top: 80px !important; padding-left: 260px !important; }
</style>

<!-- Material Icons -->
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@400,0&display=swap" rel="stylesheet"/>

<!-- Top Nav -->
<div class="top-nav">
  <span class="nav-brand">Lumina Study</span>
  <div class="nav-right">
    <button class="nav-icon-btn"><span class="material-symbols-outlined">notifications</span></button>
    <button class="nav-icon-btn"><span class="material-symbols-outlined">settings</span></button>
    <div class="avatar"></div>
  </div>
</div>

<!-- Side Nav -->
<div class="side-nav">
  <div class="side-nav-user">
    <div class="side-nav-name">Study AI</div>
    <div class="side-nav-sub">Lecture Assistant</div>
  </div>
  <div class="nav-item active">
    <span class="material-symbols-outlined" style="font-size:20px">dashboard</span>
    Dashboard
  </div>
  <div class="nav-item">
    <span class="material-symbols-outlined" style="font-size:20px">description</span>
    My Notes
  </div>
  <div class="nav-item">
    <span class="material-symbols-outlined" style="font-size:20px">quiz</span>
    Practice
  </div>
  <div class="nav-bottom">
    <div class="nav-item">
      <span class="material-symbols-outlined" style="font-size:20px">help</span>
      Help
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Sidebar (settings only) ──────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    api_key = st.text_input(
        "Gemini API Key",
        type="password",
        value=os.environ.get("GEMINI_API_KEY", ""),
        help="Get yours free at aistudio.google.com",
    )
    if api_key:
        os.environ["GEMINI_API_KEY"] = api_key
    st.caption("Key is stored only for this session.")

    st.divider()
    st.markdown("**🎙️ Audio Engine**")
    audio_engine = st.radio(
        "Transcription engine",
        ["google", "whisper"],
        captions=["Free, no key needed", "Better accuracy, needs OPENAI_API_KEY"],
        label_visibility="collapsed",
    )
    if audio_engine == "whisper":
        openai_key = st.text_input(
            "OpenAI API Key",
            type="password",
            value=os.environ.get("OPENAI_API_KEY", ""),
            help="Get yours at platform.openai.com",
        )
        if openai_key:
            os.environ["OPENAI_API_KEY"] = openai_key
    else:
        audio_engine = "google"

# ── Welcome section ──────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:32px">
  <div class="welcome-title">Good morning, Student. 👋</div>
  <div class="welcome-sub">Ready to turn your lecture into study material?</div>
</div>
""", unsafe_allow_html=True)

# ── Main grid: left (input) + right (recent) ─────────────────
col_left, col_right = st.columns([2, 1], gap="large")

with col_left:
    st.markdown("""
    <div class="card-header">
      <div class="card-icon">
        <span class="material-symbols-outlined">add_circle</span>
      </div>
      <span class="card-title">New Study Session</span>
    </div>
    """, unsafe_allow_html=True)

    # ── All input types visible at once ─────────────────────
    st.markdown('<p style="font-size:13px;color:#595f66;margin-bottom:8px">Choose your input type:</p>', unsafe_allow_html=True)

    inp1, inp2, inp3, inp4 = st.tabs(["📝 Paste Text", "📄 PDF", "🎙️ Audio", "🎬 Video"])

    uploaded_file  = None
    uploaded_audio = None
    uploaded_video = None
    text_input     = None

    with inp1:
        st.caption("Paste your lecture notes or transcript below")
        text_input = st.text_area(
            "Paste lecture text",
            height=180,
            placeholder="Enter study material...",
            label_visibility="collapsed",
        )

    with inp2:
        st.caption("Upload a PDF of your lecture slides or notes")
        uploaded_file = st.file_uploader(
            "Upload PDF",
            type=["pdf"],
            label_visibility="collapsed",
        )
        if uploaded_file:
            st.success(f"✅ **{uploaded_file.name}** — {uploaded_file.size/1024:.1f} KB")

    with inp3:
        st.caption("Upload lecture audio — WAV, MP3, M4A, OGG, FLAC")
        uploaded_audio = st.file_uploader(
            "Upload Audio",
            type=["wav", "mp3", "m4a", "ogg", "flac"],
            label_visibility="collapsed",
            key="audio_uploader",
        )
        if uploaded_audio:
            st.success(f"✅ **{uploaded_audio.name}** — {uploaded_audio.size/1024:.1f} KB")
        st.caption("✅ ffmpeg detected. Google SR (free) or Whisper — select engine in sidebar.")

    with inp4:
        st.caption("Upload a lecture video — MP4, MOV, WEBM")
        uploaded_video = st.file_uploader(
            "Upload Video",
            type=["mp4", "mov", "webm"],
            label_visibility="collapsed",
            key="video_uploader",
        )
        if uploaded_video:
            st.success(f"✅ **{uploaded_video.name}** — {uploaded_video.size/1024/1024:.1f} MB")
        st.caption("⚠️ Video support coming soon.")

    st.markdown("<br>", unsafe_allow_html=True)

    # action row — button on the right
    _, btn_col = st.columns([2, 1])
    with btn_col:
        generate = st.button("🚀 Start Session", type="primary", use_container_width=True)

    # stat mini cards
    st.markdown("<br>", unsafe_allow_html=True)
    s1, s2 = st.columns(2)
    with s1:
        st.markdown("""
        <div class="stat-card">
          <span class="material-symbols-outlined stat-icon">timer</span>
          <div>
            <div class="stat-label">TODAY'S FOCUS</div>
            <div class="stat-value">Ready</div>
          </div>
        </div>""", unsafe_allow_html=True)
    with s2:
        st.markdown("""
        <div class="stat-card">
          <span class="material-symbols-outlined stat-icon">bolt</span>
          <div>
            <div class="stat-label">STATUS</div>
            <div class="stat-value">Active</div>
          </div>
        </div>""", unsafe_allow_html=True)

with col_right:
    st.markdown("""
    <div class="recent-panel">
      <div class="recent-header">
        <span class="recent-header-title">Recent Lectures</span>
        <span style="font-size:12px;color:#3c5e91;font-weight:500;cursor:pointer">View All</span>
      </div>
    """, unsafe_allow_html=True)

    # show saved outputs if any
    outputs_dir = "outputs"
    recent_files = []
    if os.path.exists(outputs_dir):
        recent_files = sorted(
            [f for f in os.listdir(outputs_dir) if f.endswith(".json")],
            reverse=True
        )[:4]

    if recent_files:
        for fname in recent_files:
            ts = fname.replace("lecture_output_", "").replace(".json", "")
            display_ts = f"{ts[6:8]}/{ts[4:6]}/{ts[:4]} {ts[9:11]}:{ts[11:13]}"

            col_info, col_btn = st.columns([3, 1])
            with col_info:
                st.markdown(f"""
                <div class="recent-item">
                  <span class="material-symbols-outlined" style="color:#595f66">article</span>
                  <div>
                    <div class="recent-item-title">Lecture Output</div>
                    <div class="recent-item-time">🕐 {display_ts}</div>
                  </div>
                </div>""", unsafe_allow_html=True)
            with col_btn:
                if st.button("Open", key=f"open_{fname}", use_container_width=True):
                    from core.parser import load_from_json
                    loaded = load_from_json(os.path.join(outputs_dir, fname))
                    st.session_state["results"]    = loaded
                    st.session_state["char_count"] = 0
                    st.session_state["loaded_file"] = fname
                    st.rerun()
    else:
        st.markdown("""
        <div style="padding:24px;text-align:center;color:#595f66;font-size:14px">
          No lectures yet.<br>Start your first session!
        </div>""", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ── Generate logic ───────────────────────────────────────────
if generate:
    if not os.environ.get("GEMINI_API_KEY"):
        st.error("⚠️ Enter your Gemini API key in the **sidebar** (top-left arrow).")
        st.stop()

    # figure out which input was provided
    has_text  = bool(text_input)
    has_pdf   = bool(uploaded_file)
    has_audio = bool(uploaded_audio)
    has_video = bool(uploaded_video)

    if not any([has_text, has_pdf, has_audio, has_video]):
        st.error("⚠️ Please provide at least one input — paste text, upload a PDF, audio, or video.")
        st.stop()
    if has_video:
        st.warning("🎬 Video support coming soon. Please use PDF, text, or audio for now.")
        st.stop()

    st.divider()

    with st.status("⚙️ Processing your lecture…", expanded=True) as status:
        if has_pdf:
            st.write("📄 Extracting text from PDF…")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name
            try:
                raw_text = extract_text_from_pdf(tmp_path)
            finally:
                os.unlink(tmp_path)

        elif has_audio:
            suffix = os.path.splitext(uploaded_audio.name)[1].lower()
            st.write(f"🎙️ Transcribing audio with **{audio_engine}** engine…")
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(uploaded_audio.getvalue())
                tmp_path = tmp.name
            try:
                from utils.audio import transcribe_audio
                chunk_status = st.empty()
                def audio_progress(current, total):
                    chunk_status.caption(f"  Chunk {current}/{total}…")
                raw_text = transcribe_audio(tmp_path, engine=audio_engine, progress_cb=audio_progress)
                chunk_status.empty()
            finally:
                os.unlink(tmp_path)

        else:
            raw_text = text_input

        st.write(f"✅ {len(raw_text):,} characters extracted")

        from core.llm import generate_notes, generate_flashcards, generate_mcqs

        st.write("📝 Generating notes…")
        notes = generate_notes(raw_text)

        st.write("🃏 Generating flashcards…")
        flashcards = generate_flashcards(raw_text)

        st.write("❓ Generating MCQs…")
        mcqs = generate_mcqs(raw_text)

        results = {"notes": notes, "flashcards": flashcards, "mcqs": mcqs}
        saved_path = save_to_json(results)
        st.write(f"💾 Saved → `{saved_path}`")

        status.update(label="✅ Session complete!", state="complete")
        st.session_state["results"]   = results
        st.session_state["char_count"] = len(raw_text)

# ── Results ──────────────────────────────────────────────────
if "results" in st.session_state:
    results = st.session_state["results"]

    st.divider()

    # header row — show filename if loaded from recent, close button
    res_title_col, res_close_col = st.columns([4, 1])
    with res_title_col:
        loaded_file = st.session_state.get("loaded_file")
        if loaded_file:
            ts = loaded_file.replace("lecture_output_", "").replace(".json", "")
            display_ts = f"{ts[6:8]}/{ts[4:6]}/{ts[:4]} {ts[9:11]}:{ts[11:13]}"
            st.markdown(f"### 📂 {display_ts}")
        else:
            st.markdown("### 📊 Results")
    with res_close_col:
        if st.button("✕ Close", use_container_width=True):
            del st.session_state["results"]
            st.session_state.pop("loaded_file", None)
            st.session_state.pop("char_count", None)
            st.rerun()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("📝 Notes",      len(results["notes"]))
    m2.metric("🃏 Flashcards", len(results["flashcards"]))
    m3.metric("❓ MCQs",       len(results["mcqs"]))
    m4.metric("📖 Characters", f'{st.session_state.get("char_count", 0):,}')

    st.markdown("<br>", unsafe_allow_html=True)

    tab_notes, tab_flash, tab_mcq, tab_dl = st.tabs(
        ["📝 Notes", "🃏 Flashcards", "❓ MCQs", "⬇️ Download"]
    )

    with tab_notes:
        st.markdown("#### Lecture Notes")
        for i, note in enumerate(results["notes"], 1):
            st.markdown(f"**{i}.** {note}")

    with tab_flash:
        st.markdown("#### Flashcards")
        for i, card in enumerate(results["flashcards"], 1):
            with st.expander(f"Card {i} — {card['q']}"):
                st.markdown(f"**Answer:** {card['a']}")

    with tab_mcq:
        st.markdown("#### Exam-Style Questions")
        diff = {"Easy": 0, "Medium": 0, "Hard": 0}
        for q in results["mcqs"]:
            diff[q.get("difficulty", "Medium")] += 1
        d1, d2, d3 = st.columns(3)
        d1.metric("🟢 Easy",   diff["Easy"])
        d2.metric("🟡 Medium", diff["Medium"])
        d3.metric("🔴 Hard",   diff["Hard"])

        st.markdown("<br>", unsafe_allow_html=True)
        show_answers = st.toggle("Show answers", value=False)

        for i, q in enumerate(results["mcqs"], 1):
            diff_label = q.get("difficulty", "Medium")
            badge = f'<span class="badge badge-{diff_label.lower()}">{diff_label}</span>'
            st.markdown(
                f"**Q{i}.** {q['question']} {badge}",
                unsafe_allow_html=True,
            )
            for opt in q["options"]:
                st.markdown(f"&nbsp;&nbsp;&nbsp;{opt}")
            if show_answers:
                st.success(f"✅ Answer: **{q['answer']}**")
            st.markdown("---")

    with tab_dl:
        st.markdown("#### Download Results")
        json_str = json.dumps(results, indent=2, ensure_ascii=False)
        st.download_button(
            "⬇️ Download JSON",
            data=json_str,
            file_name="lecture_output.json",
            mime="application/json",
            use_container_width=True,
        )
        st.code(json_str[:1500] + ("\n..." if len(json_str) > 1500 else ""), language="json")