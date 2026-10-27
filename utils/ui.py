from html import escape

import streamlit as st


def apply_app_style():
    st.markdown(
        """
        <style>
        :root {
            --canvas: #f5f5ef;
            --ink: #17251f;
            --muted: #64736a;
            --forest: #183b32;
            --lime: #d3f36b;
            --line: #e4e9df;
            --card: #ffffff;
        }
        html, body, [class*="css"] { font-family: 'Segoe UI', Arial, sans-serif; }
        .stApp { background: var(--canvas); color: var(--ink); }
        [data-testid="stHeader"] { background: rgba(245,245,239,.88); }
        [data-testid="stSidebar"] { background: var(--forest); }
        [data-testid="stSidebar"] * { color: #f4f7ed; }
        [data-testid="stSidebar"] span[role="button"],
        [data-testid="stSidebar"] span[role="button"] * {
            color: var(--forest) !important;
        }
        [data-testid="stSidebar"] [data-testid="stRadio"] label { color: #f4f7ed; }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: #d4e0d7; }
        [data-baseweb="popover"] [role="option"] { color: var(--ink); }
        [data-baseweb="popover"] [role="option"] * { color: inherit; }
        .block-container { max-width: 1180px; padding-top: 2.2rem; padding-bottom: 4rem; }
        h1, h2, h3 { font-family: 'Trebuchet MS', 'Segoe UI', sans-serif !important; color: var(--ink); letter-spacing: -.035em; }
        h1 { font-weight: 800 !important; }
        [data-testid="stMetric"] {
            background: var(--card); border: 1px solid var(--line); border-radius: 16px;
            padding: 18px 20px; box-shadow: 0 5px 18px rgba(23,37,31,.035);
        }
        [data-testid="stMetricLabel"] p { color: var(--muted); font-size: .83rem; }
        [data-testid="stMetricValue"] { color: var(--forest); font-family: 'Trebuchet MS', 'Segoe UI', sans-serif; }
        [data-testid="stForm"], [data-testid="stVerticalBlockBorderWrapper"] {
            border-color: var(--line) !important; border-radius: 18px !important;
            background: var(--card); box-shadow: 0 5px 18px rgba(23,37,31,.035);
        }
        [data-testid="stForm"] { padding: 1.4rem; }
        .hero {
            background: var(--forest); color: #f5f7f0; border-radius: 24px;
            padding: 30px 34px; margin: 0 0 25px; position: relative; overflow: hidden;
        }
        .hero:after { content: ''; position: absolute; width: 190px; height: 190px; right: 5%; top: -105px;
            border: 1px solid rgba(211,243,107,.35); border-radius: 50%;
            box-shadow: 0 0 0 24px rgba(211,243,107,.045), 0 0 0 50px rgba(211,243,107,.035); }
        .hero .eyebrow { color: var(--lime); font-size: .72rem; text-transform: uppercase;
            letter-spacing: .16em; font-weight: 700; margin-bottom: 8px; }
        .hero h1 { color: #fff; font-size: clamp(1.8rem, 4vw, 2.55rem); margin: 0 0 8px; }
        .hero p { color: #d5e0d9; margin: 0; max-width: 700px; line-height: 1.6; }
        .insight {
            background: #edf4df; border-left: 4px solid #8eaf36; border-radius: 0 12px 12px 0;
            padding: 15px 18px; color: #34432d; margin: 10px 0 20px; line-height: 1.6;
        }
        .note { color: var(--muted); font-size: .86rem; line-height: 1.55; }
        div.stButton > button[kind="primary"], div.stFormSubmitButton > button {
            background: var(--lime); color: var(--forest); border: 0; font-weight: 700;
            border-radius: 10px; min-height: 2.7rem;
        }
        div.stButton > button[kind="primary"]:hover, div.stFormSubmitButton > button:hover {
            background: #c3e45b; color: var(--forest); border: 0;
        }
        .stDownloadButton button { border-radius: 10px; }
        hr { border-color: var(--line); }
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(eyebrow, title, description):
    st.markdown(
        f"""
        <section class="hero">
          <div class="eyebrow">{escape(eyebrow)}</div>
          <h1>{escape(title)}</h1>
          <p>{escape(description)}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def insight(text):
    st.markdown(
        f'<div class="insight"><strong>What this means</strong><br>{escape(str(text))}</div>',
        unsafe_allow_html=True,
    )
