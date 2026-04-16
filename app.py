"""
=============================================================
  Streamlit Web App – Legal Document Simplification System
  Run: streamlit run app.py
=============================================================
"""

import streamlit as st
from legal_simplifier import load_models, simplify_legal_document

# ── Page config ────────────────────────────────────────────
st.set_page_config(
    page_title = "LegalSimplify AI",
    page_icon  = "⚖️",
    layout     = "wide",
)

# ── Custom CSS ─────────────────────────────────────────────
st.markdown("""
<style>
    /* ── global ── */
    html, body, [class*="css"] { font-family: 'Segoe UI', sans-serif; }

    /* ── header banner ── */
    .hero {
        background: linear-gradient(135deg, #1a3a5c 0%, #0d7377 100%);
        border-radius: 14px;
        padding: 2rem 2.5rem;
        margin-bottom: 1.5rem;
        color: white;
    }
    .hero h1 { font-size: 2rem; margin: 0; }
    .hero p  { font-size: 1rem; margin: 0.4rem 0 0; opacity: 0.85; }

    /* ── metric cards ── */
    .metric-card {
        background: #f7f9fc;
        border: 1px solid #e0e7ef;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        text-align: center;
    }
    .metric-value { font-size: 2rem; font-weight: 700; color: #1a3a5c; }
    .metric-label { font-size: 0.8rem; color: #666; margin-top: 0.2rem; }

    /* ── entity badge ── */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 600;
        margin: 0.2rem;
        color: white;
    }
    .badge-PERSON  { background: #5b6af7; }
    .badge-ORG     { background: #e87a2a; }
    .badge-GPE     { background: #2aa65e; }
    .badge-LAW     { background: #b0363a; }
    .badge-DATE    { background: #1c8fa8; }
    .badge-MONEY   { background: #7c3aed; }
    .badge-other   { background: #64748b; }

    /* ── result box ── */
    .result-box {
        background: #eef9f2;
        border-left: 4px solid #0d7377;
        border-radius: 0 8px 8px 0;
        padding: 1.1rem 1.4rem;
        font-size: 1rem;
        line-height: 1.7;
    }

    /* ── readability bar ── */
    .bar-wrap { background: #e5e7eb; border-radius: 999px; height: 12px; overflow: hidden; }
    .bar-fill  { height: 100%; border-radius: 999px; transition: width .5s; }

    /* ── section heading ── */
    .sec-heading {
        font-size: 1.05rem; font-weight: 700;
        color: #1a3a5c; margin: 0.5rem 0 0.8rem;
        border-bottom: 2px solid #e0e7ef;
        padding-bottom: 0.3rem;
    }
</style>
""", unsafe_allow_html=True)


# ── Model caching ──────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def get_models():
    return load_models()


# ── Helpers ────────────────────────────────────────────────
BADGE_COLORS = {
    "PERSON": "badge-PERSON", "ORG": "badge-ORG",
    "GPE": "badge-GPE",       "LAW": "badge-LAW",
    "DATE": "badge-DATE",     "MONEY": "badge-MONEY",
}

def badge_html(entity: dict) -> str:
    cls = BADGE_COLORS.get(entity["label"], "badge-other")
    return (f'<span class="badge {cls}" title="{entity["description"]}">'
            f'{entity["entity"]}</span>')

def readability_bar(score: float, color: str) -> str:
    pct = min(max(score, 0), 100)
    return (f'<div class="bar-wrap"><div class="bar-fill" '
            f'style="width:{pct}%;background:{color};"></div></div>')

SAMPLE_TEXTS = {
    "Software Licence Agreement": """
WHEREAS, the Party of the First Part (hereinafter referred to as the "Licensor") is the
owner of certain intellectual property rights, including but not limited to patents,
trademarks, and copyrights, pertaining to the Software, and WHEREAS, the Party of the
Second Part (hereinafter referred to as the "Licensee") desires to obtain a
non-exclusive, non-transferable, limited license to use the Software solely for internal
business purposes, subject to the terms and conditions set forth herein; NOW, THEREFORE,
in consideration of the mutual covenants and agreements contained herein, and for other
good and valuable consideration, the receipt and sufficiency of which are hereby
acknowledged, the parties agree that Licensee shall not sublicense, modify, reverse
engineer, decompile, or create derivative works based upon the Software.
""",
    "Government Circular – RTI Act": """
In exercise of the powers conferred by sub-section (1) of Section 19 of the Right to
Information Act, 2005, the Central Government, being satisfied that it is necessary and
expedient so to do in the public interest, hereby directs that any citizen who does not
receive a decision within the time specified in sub-section (1) of Section 7 shall have
the right to appeal to the First Appellate Authority designated under sub-section (1) of
Section 19 within a period of thirty days from the expiry of such period or from the
receipt of such a decision, as the case may be. No fee shall be charged for the first
appeal.
""",
    "Tenancy Agreement Clause": """
The Lessee covenants with the Lessor that the Lessee will not, without the prior written
consent of the Lessor (such consent not to be unreasonably withheld or delayed), assign,
sublet, or part with or share possession of the demised premises or any part thereof, nor
carry out or permit to be carried out any alterations, additions, or improvements to the
structure of the demised premises. In the event of any breach of the covenants contained
herein, the Lessor shall be entitled to forfeit the deposit and re-enter the demised
premises forthwith.
""",
}


# ══════════════════════════════════════════════════════════
#  PAGE LAYOUT
# ══════════════════════════════════════════════════════════

# Hero banner
st.markdown("""
<div class="hero">
  <h1>⚖️ LegalSimplify AI</h1>
  <p>Paste any legal or government document and get a plain-English explanation instantly.</p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    show_summary  = st.checkbox("Show raw summary",     value=False)
    show_entities = st.checkbox("Show named entities",  value=True)
    show_scores   = st.checkbox("Show readability",     value=True)

    st.markdown("---")
    st.markdown("### 📂 Sample Documents")
    sample_choice = st.selectbox("Load a sample:", ["(none)"] + list(SAMPLE_TEXTS.keys()))

    st.markdown("---")
    st.markdown("### 📌 About")
    st.info("Uses BART for summarisation, T5 for paraphrasing, "
            "spaCy for entity recognition, and textstat for readability scoring.")

# ── Main columns ───────────────────────────────────────────
col_in, col_out = st.columns([1, 1], gap="large")

with col_in:
    st.markdown('<div class="sec-heading">📝 Input Document</div>', unsafe_allow_html=True)

    default_text = SAMPLE_TEXTS.get(sample_choice, "") if sample_choice != "(none)" else ""
    user_text = st.text_area(
        label       = "Paste legal text here:",
        value       = default_text,
        height      = 320,
        placeholder = "e.g. WHEREAS, the Party of the First Part …",
        label_visibility = "collapsed",
    )

    word_count = len(user_text.split()) if user_text.strip() else 0
    st.caption(f"Word count: **{word_count}**")

    run = st.button("⚡ Simplify Document", type="primary", use_container_width=True)

with col_out:
    st.markdown('<div class="sec-heading">✅ Simplified Explanation</div>',
                unsafe_allow_html=True)

    if not run:
        st.info("👈  Paste your document and press **Simplify Document**.")

    elif not user_text.strip():
        st.warning("Please enter some text first.")

    else:
        with st.spinner("🔄 Loading models and processing …"):
            models = get_models()
            result = simplify_legal_document(user_text, models)

        # ── Simplified text ───────────────────────────────
        st.markdown(
            f'<div class="result-box">{result["simplified_text"]}</div>',
            unsafe_allow_html=True,
        )
        st.markdown("")

        # ── Optional: raw summary ─────────────────────────
        if show_summary:
            with st.expander("📃 Intermediate Summary (BART output)"):
                st.write(result["summary"])

        # ── Entities ──────────────────────────────────────
        if show_entities:
            st.markdown('<div class="sec-heading">🏷️ Extracted Named Entities</div>',
                        unsafe_allow_html=True)
            if result["entities"]:
                badges = " ".join(badge_html(e) for e in result["entities"])
                st.markdown(badges, unsafe_allow_html=True)

                with st.expander("Entity details"):
                    for ent in result["entities"]:
                        st.markdown(f"- **{ent['entity']}** → {ent['description']}")
            else:
                st.caption("No named entities detected.")

        # ── Readability ───────────────────────────────────
        if show_scores:
            rd = result["readability"]
            st.markdown('<div class="sec-heading">📊 Readability Analysis</div>',
                        unsafe_allow_html=True)

            m1, m2, m3 = st.columns(3)
            with m1:
                st.markdown(f"""
                <div class="metric-card">
                  <div class="metric-value">{rd['original']['flesch_reading_ease']}</div>
                  <div class="metric-label">Before (Flesch)</div>
                </div>""", unsafe_allow_html=True)
            with m2:
                st.markdown(f"""
                <div class="metric-card">
                  <div class="metric-value" style="color:#0d7377">
                    {rd['simplified']['flesch_reading_ease']}
                  </div>
                  <div class="metric-label">After (Flesch)</div>
                </div>""", unsafe_allow_html=True)
            with m3:
                imp = rd["improvement"]
                colour = "#0d7377" if imp >= 0 else "#b0363a"
                st.markdown(f"""
                <div class="metric-card">
                  <div class="metric-value" style="color:{colour}">
                    {"+" if imp >= 0 else ""}{imp}
                  </div>
                  <div class="metric-label">Improvement</div>
                </div>""", unsafe_allow_html=True)

            st.markdown("")
            st.markdown("**Before**")
            st.markdown(readability_bar(rd["original"]["flesch_reading_ease"],  "#b0363a"),
                        unsafe_allow_html=True)
            st.caption(rd["original"]["label"])

            st.markdown("**After**")
            st.markdown(readability_bar(rd["simplified"]["flesch_reading_ease"], "#0d7377"),
                        unsafe_allow_html=True)
            st.caption(rd["simplified"]["label"])

            st.markdown("")
            st.markdown(
                f"Grade Level:  **{rd['original']['flesch_kincaid_grade']}**"
                f" → **{rd['simplified']['flesch_kincaid_grade']}**"
            )

        # ── Success toast ─────────────────────────────────
        st.success("✅ Simplification complete!", icon="🎉")

# ── Footer ─────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<center style='color:#999;font-size:0.8rem;'>"
    "AI-Powered Legal Document Simplification System &nbsp;|&nbsp; "
    "NLP Mini-Project &nbsp;|&nbsp; Powered by BART · T5 · spaCy"
    "</center>",
    unsafe_allow_html=True,
)
