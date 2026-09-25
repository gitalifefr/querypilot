import streamlit as st

from text_to_sql import question_to_sql
from database import execute_query


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="QueryPilot",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
<style>

html, body, [class*="css"] {
    font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 80% 0%, rgba(99,102,241,0.12), transparent 30%),
        radial-gradient(circle at 10% 20%, rgba(59,130,246,0.06), transparent 28%),
        #080b12;
    color: #f8fafc;
}

.main .block-container {
    max-width: 1050px;
    padding-top: 42px;
    padding-bottom: 60px;
}

/* Hide Streamlit branding */
#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    background: transparent !important;
}


/* =========================================================
   SIDEBAR
   ========================================================= */

section[data-testid="stSidebar"] {
    background: #0b0f17;
    border-right: 1px solid rgba(148,163,184,0.10);
}

section[data-testid="stSidebar"] > div {
    padding: 30px 22px;
}

.brand-icon {
    width: 52px;
    height: 52px;
    border-radius: 15px;

    background: linear-gradient(
        135deg,
        #6366f1,
        #8b5cf6
    );

    display: flex;
    align-items: center;
    justify-content: center;

    color: white;
    font-size: 24px;
    font-weight: 700;

    margin-bottom: 17px;

    box-shadow:
        0 10px 30px rgba(99,102,241,0.25);
}

.brand-name {
    font-size: 1.42rem;
    font-weight: 750;
    color: #f8fafc;
    letter-spacing: -0.5px;
}

.brand-description {
    margin-top: 8px;
    color: #7f8ba3;
    font-size: 0.84rem;
    line-height: 1.55;
}

.side-heading {
    margin-top: 30px;
    margin-bottom: 11px;

    color: #59657a;
    font-size: 0.66rem;
    font-weight: 750;

    letter-spacing: 1.4px;
    text-transform: uppercase;
}

.side-item {
    color: #aab4c5;
    font-size: 0.86rem;
    padding: 7px 0;
}

.side-item span {
    color: #818cf8;
    margin-right: 9px;
}

.side-footer {
    margin-top: 42px;
    padding-top: 18px;

    border-top: 1px solid rgba(148,163,184,0.08);

    color: #4f5b70;
    font-size: 0.70rem;
    line-height: 1.5;
}


/* =========================================================
   HERO
   ========================================================= */

.hero {
    text-align: center;
    margin-bottom: 28px;
}

.hero-badge {
    display: inline-block;

    padding: 6px 12px;
    margin-bottom: 15px;

    border-radius: 30px;

    background: rgba(99,102,241,0.09);
    border: 1px solid rgba(129,140,248,0.18);

    color: #a5b4fc;

    font-size: 0.68rem;
    font-weight: 700;

    letter-spacing: 1px;
}

.hero-title {
    margin: 0;

    color: #f8fafc;

    font-size: 3.25rem;
    line-height: 1.05;

    font-weight: 800;
    letter-spacing: -2.3px;
}

.hero-accent {
    background:
        linear-gradient(
            90deg,
            #60a5fa,
            #818cf8,
            #a78bfa
        );

    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-description {
    max-width: 650px;
    margin: 16px auto 0;

    color: #7f8ba3;

    font-size: 0.96rem;
    line-height: 1.65;
}


/* =========================================================
   QUERY CARD
   ========================================================= */

.query-card {
    background: rgba(15,23,42,0.70);

    border: 1px solid rgba(148,163,184,0.12);

    border-radius: 18px;

    padding: 21px 23px 18px;

    box-shadow:
        0 20px 60px rgba(0,0,0,0.18);

    margin-top: 5px;
}

.query-title {
    color: #e2e8f0;

    font-size: 0.96rem;
    font-weight: 650;

    margin-bottom: 4px;
}

.query-subtitle {
    color: #64748b;

    font-size: 0.76rem;

    margin-bottom: 14px;
}


/* =========================================================
   INPUT
   ========================================================= */

.stTextInput {
    margin-top: 0 !important;
    margin-bottom: 8px !important;
}

.stTextInput > div {
    margin-top: 0 !important;
}

.stTextInput > div > div > input {
    height: 48px !important;

    background: #090d15 !important;

    color: #f8fafc !important;

    border: 1px solid #263247 !important;

    border-radius: 11px !important;

    padding: 0 15px !important;

    font-size: 0.92rem !important;

    box-shadow: none !important;
}

.stTextInput > div > div > input:focus {
    border-color: #6366f1 !important;

    box-shadow:
        0 0 0 2px rgba(99,102,241,0.10) !important;
}

.stTextInput > div > div > input::placeholder {
    color: #566176 !important;
}


/* =========================================================
   BUTTON
   ========================================================= */

.stButton {
    margin-top: 0 !important;
}

.stButton > button {
    height: 47px;

    border: none !important;
    border-radius: 11px;

    background:
        linear-gradient(
            135deg,
            #4f46e5,
            #7c3aed
        ) !important;

    color: white !important;

    font-size: 0.84rem;
    font-weight: 650;

    box-shadow:
        0 8px 25px rgba(79,70,229,0.20);

    transition: all 0.2s ease;
}

.stButton > button:hover {
    transform: translateY(-1px);

    box-shadow:
        0 12px 30px rgba(79,70,229,0.30);
}


/* =========================================================
   EXAMPLES
   ========================================================= */

.examples-label {
    color: #59657a;

    font-size: 0.65rem;
    font-weight: 700;

    text-transform: uppercase;
    letter-spacing: 1px;

    margin-top: 14px;
    margin-bottom: 7px;
}

.examples {
    color: #68758a;
    font-size: 0.75rem;
}

.example-pill {
    display: inline-block;

    padding: 4px 9px;

    margin-right: 5px;
    margin-bottom: 4px;

    border-radius: 7px;

    background: #101624;

    border: 1px solid #1d283a;

    color: #8490a4;
}


/* =========================================================
   RESULTS
   ========================================================= */

.section-header {
    display: flex;
    align-items: center;

    gap: 9px;

    margin-top: 30px;
    margin-bottom: 6px;
}

.section-icon {
    width: 30px;
    height: 30px;

    border-radius: 8px;

    display: flex;
    align-items: center;
    justify-content: center;

    background: rgba(99,102,241,0.10);

    color: #818cf8;

    font-size: 13px;
}

.section-title {
    color: #e2e8f0;

    font-size: 1rem;
    font-weight: 650;
}

.section-description {
    color: #59657a;

    font-size: 0.74rem;

    margin-bottom: 9px;
}

.stCodeBlock {
    border-radius: 11px !important;
    border: 1px solid rgba(148,163,184,0.10) !important;
}

.stDataFrame {
    border-radius: 11px;
    overflow: hidden;
    border: 1px solid rgba(148,163,184,0.10);
}

.stAlert {
    border-radius: 10px;
}


/* =========================================================
   FOOTER
   ========================================================= */

.footer {
    text-align: center;

    margin-top: 50px;
    padding-top: 18px;

    border-top:
        1px solid rgba(148,163,184,0.07);

    color: #3f4a5d;

    font-size: 0.70rem;
}

</style>
""",
    unsafe_allow_html=True
)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.html("""
        <div class="brand-icon">✦</div>

        <div class="brand-name">
            QueryPilot
        </div>

        <div class="brand-description">
            Your AI-powered database copilot.
            Ask questions in natural language
            and turn them into SQL insights.
        </div>

        <div class="side-heading">
            Capabilities
        </div>

        <div class="side-item">
            <span>✦</span>
            Natural Language to SQL
        </div>

        <div class="side-item">
            <span>⌘</span>
            Intelligent Schema Search
        </div>

        <div class="side-item">
            <span>▣</span>
            MySQL Query Execution
        </div>

        <div class="side-item">
            <span>◈</span>
            Instant Data Insights
        </div>

        <div class="side-heading">
            Workflow
        </div>

        <div class="side-item">
            <span>01</span>
            Ask your question
        </div>

        <div class="side-item">
            <span>02</span>
            Understand the schema
        </div>

        <div class="side-item">
            <span>03</span>
            Generate SQL
        </div>

        <div class="side-item">
            <span>04</span>
            Execute & retrieve
        </div>

        <div class="side-footer">
            QueryPilot<br>
            Natural Language → SQL → Insights
        </div>
    """)


# =========================================================
# HERO
# =========================================================

st.html("""
    <div class="hero">

        <div class="hero-badge">
            ✦ AI DATABASE COPILOT
        </div>

        <h1 class="hero-title">
            Ask your data.<br>
            <span class="hero-accent">
                Get answers.
            </span>
        </h1>

        <p class="hero-description">
            QueryPilot turns natural-language questions into
            executable SQL and retrieves insights from your database.
        </p>

    </div>
""")


# =========================================================
# QUERY CARD
# =========================================================

st.html("""
    <div class="query-card">

        <div class="query-title">
            Ask QueryPilot
        </div>

        <div class="query-subtitle">
            Describe what you want to know about your data.
        </div>

    </div>
""")


# =========================================================
# INPUT
# =========================================================

def submit_query():
    st.session_state["submit"] = True


question = st.text_input(
    "Question",
    placeholder="e.g. How many customers are there?",
    label_visibility="collapsed",
    key="question_value",
    on_change=submit_query
)


# =========================================================
# GENERATE BUTTON
# =========================================================

col1, col2, col3 = st.columns([7, 1.5, 7])

with col2:
    button_pressed = st.button(
        "✦ Generate",
        use_container_width=True
    )

submit = (
    button_pressed
    or st.session_state.get("submit", False)
)


# =========================================================
# EXAMPLES
# =========================================================

st.html("""
    <div class="examples-label">
        Example queries
    </div>

    <div class="examples">

        <span class="example-pill">
            How many customers are there?
        </span>

        <span class="example-pill">
            Show total orders
        </span>

        <span class="example-pill">
            Top 5 products
        </span>

        <span class="example-pill">
            Most expensive product
        </span>

    </div>
""")


# =========================================================
# PROCESS QUERY
# =========================================================

if submit and st.session_state.get(
    "question_value", ""
).strip():

    user_question = (
        st.session_state["question_value"].strip()
    )

    greetings = [
        "hi",
        "hello",
        "hey"
    ]

    if user_question.lower() in greetings:

        st.success(
            "Hello! I'm QueryPilot. "
            "Ask me anything about your database."
        )

    else:

        with st.spinner(
            "QueryPilot is analyzing your question..."
        ):

            try:

                # -----------------------------------------
                # GENERATE SQL
                # -----------------------------------------

                sql_query = question_to_sql(
                    user_question
                )

                st.html("""
                    <div class="section-header">

                        <div class="section-icon">
                            ⌘
                        </div>

                        <div class="section-title">
                            Generated SQL
                        </div>

                    </div>

                    <div class="section-description">
                        SQL generated from your natural-language question.
                    </div>
                """)

                st.code(
                    sql_query,
                    language="sql"
                )

                # -----------------------------------------
                # EXECUTE SQL
                # -----------------------------------------

                results = execute_query(
                    sql_query
                )

                # -----------------------------------------
                # RESULTS
                # -----------------------------------------

                st.html("""
                    <div class="section-header">

                        <div class="section-icon">
                            ▣
                        </div>

                        <div class="section-title">
                            Results
                        </div>

                    </div>

                    <div class="section-description">
                        Data returned from your database.
                    </div>
                """)

                if hasattr(results, "empty"):

                    if not results.empty:

                        st.dataframe(
                            results,
                            use_container_width=True,
                            hide_index=True
                        )

                    else:

                        st.info(
                            "The query executed successfully, "
                            "but no records were found."
                        )

                elif results:

                    st.dataframe(
                        results,
                        use_container_width=True
                    )

                else:

                    st.info(
                        "The query executed successfully, "
                        "but no results were returned."
                    )

            except Exception as e:

                st.error(
                    f"QueryPilot couldn't complete the request: {e}"
                )

    st.session_state["submit"] = False


# =========================================================
# FOOTER
# =========================================================

st.html("""
    <div class="footer">
        QueryPilot · Natural Language → SQL → Insights
    </div>
""")
