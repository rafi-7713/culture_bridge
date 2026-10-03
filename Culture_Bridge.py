import streamlit as st
import pandas as pd
import json
import random

# ============================================================
# PAGE SETUP
# ============================================================

st.set_page_config(
    page_title="HIT-CultureBridge",
    page_icon="🎓",
    layout="centered"
)

# ============================================================
# TITLE
# ============================================================

st.title("🎓 HIT-CultureBridge")
st.caption("Interactive Chinese Language & Campus Culture Learning Platform")

# ============================================================
# TABS
# ============================================================

tab_cards, tab_quiz, tab_about = st.tabs(
    ["📇 Flashcards", "🧠 Culture Quiz", "ℹ️ About the Project"]
)

# ============================================================
# TAB 1: FLASHCARDS
# ============================================================

with tab_cards:
    st.subheader("Interactive HSK & Campus Vocabulary")

    @st.cache_data
    def load_vocab():
        return pd.read_csv("data/hsk_words.csv")

    try:
        df_vocab = load_vocab()

        if df_vocab.empty:
            st.warning("The vocabulary file is empty.")

        else:
            # ----------------------------------------------------
            # CATEGORY / LEVEL FILTER
            # ----------------------------------------------------

            levels = ["All"] + list(
                df_vocab["level"].dropna().unique()
            )

            selected_level = st.selectbox(
                "Filter by Category/Level:",
                levels
            )

            if selected_level == "All":
                filtered_df = df_vocab
            else:
                filtered_df = df_vocab[
                    df_vocab["level"] == selected_level
                ]

            # ----------------------------------------------------
            # SESSION STATE
            # ----------------------------------------------------

            if "card_index" not in st.session_state:
                st.session_state.card_index = 0

            if "revealed" not in st.session_state:
                st.session_state.revealed = False

            # Reset index if filter changes and index becomes invalid
            if st.session_state.card_index >= len(filtered_df):
                st.session_state.card_index = 0

            # ----------------------------------------------------
            # CURRENT CARD
            # ----------------------------------------------------

            current_card = filtered_df.iloc[
                st.session_state.card_index
            ]

            # ----------------------------------------------------
            # FLASHCARD DISPLAY
            # ----------------------------------------------------

            with st.container(border=True):

                st.markdown(
                    f"""
                    <div style="
                        text-align: center;
                        padding: 30px 10px;
                    ">
                        <h1>{current_card['hanzi']}</h1>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                if st.session_state.revealed:

                    st.markdown(
                        f"""
                        <div style="
                            text-align: center;
                            padding: 10px;
                        ">
                            <h3>{current_card['pinyin']}</h3>
                            <h4>{current_card['english']}</h4>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                else:

                    st.markdown(
                        """
                        <div style="
                            text-align: center;
                            padding: 10px;
                        ">
                            <h3>••••••</h3>
                            <p>Click "Reveal Answer" below</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            # ----------------------------------------------------
            # BUTTONS
            # ----------------------------------------------------

            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button(
                    "👁️ Reveal Answer",
                    use_container_width=True
                ):
                    st.session_state.revealed = True
                    st.rerun()

            with col2:
                if st.button(
                    "➡️ Next Word",
                    use_container_width=True
                ):
                    st.session_state.card_index = (
                        st.session_state.card_index + 1
                    ) % len(filtered_df)

                    st.session_state.revealed = False
                    st.rerun()

            with col3:
                if st.button(
                    "🔀 Randomize",
                    use_container_width=True
                ):
                    st.session_state.card_index = random.randint(
                        0,
                        len(filtered_df) - 1
                    )

                    st.session_state.revealed = False
                    st.rerun()

            # ----------------------------------------------------
            # CARD COUNTER
            # ----------------------------------------------------

            st.caption(
                f"Card {st.session_state.card_index + 1} "
                f"of {len(filtered_df)}"
            )

    except FileNotFoundError:
        st.error(
            "❌ Could not find data/hsk_words.csv. "
            "Please ensure the file exists."
        )

    except Exception as e:
        st.error(f"❌ Error loading vocabulary: {e}")


# ============================================================
# TAB 2: CULTURE QUIZ
# ============================================================

with tab_quiz:

    st.subheader("China & HIT Campus Trivia Quiz")

    def load_quiz():
        import os

        file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data",
            "quiz.json"
        )

        if not os.path.exists(file_path):
            raise FileNotFoundError(
                f"quiz.json not found at: {file_path}"
            )

        with open(
            file_path,
            "r",
            encoding="utf-8-sig"
        ) as f:
            content = f.read()

        return json.loads(content)

    try:

        questions = load_quiz()

        if not questions:

            st.warning("The quiz file is empty.")

        else:

            total_q = len(questions)

            with st.form("quiz_form"):

                user_answers = []

                for i, q in enumerate(questions):

                    st.markdown(
                        f"**Q{i + 1}: {q['question']}**"
                    )

                    choice = st.radio(
                        f"Select your answer for Q{i + 1}:",
                        q["options"],
                        key=f"q_{i}",
                        label_visibility="collapsed"
                    )

                    user_answers.append(choice)

                    st.write("---")

                submitted = st.form_submit_button(
                    "Submit Quiz",
                    use_container_width=True
                )

            if submitted:

                user_score = 0

                for i, q in enumerate(questions):

                    if user_answers[i] == q["answer"]:

                        user_score += 1

                        st.success(
                            f"✅ Q{i + 1}: Correct! "
                            f"{q['explanation']}"
                        )

                    else:

                        st.error(
                            f"❌ Q{i + 1}: Incorrect. "
                            f"Correct answer: **{q['answer']}**. "
                            f"{q['explanation']}"
                        )

                st.metric(
                    label="Your Final Score",
                    value=f"{user_score} / {total_q}"
                )

                if user_score == total_q:

                    st.balloons()

                    st.success(
                        "🎉 Perfect score! Excellent work!"
                    )

                elif user_score >= total_q * 0.7:

                    st.success(
                        "👏 Great job! You have a good understanding "
                        "of Chinese culture and HIT!"
                    )

                else:

                    st.info(
                        "📚 Keep practicing! Review the answers "
                        "and try the quiz again."
                    )

    except FileNotFoundError as e:

        st.error(f"❌ {e}")

    except json.JSONDecodeError as e:

        st.error(
            f"❌ JSON Error: Line {e.lineno}, "
            f"Column {e.colno}: {e.msg}"
        )

    except Exception as e:

        st.error(f"❌ Error loading quiz: {e}")


# ============================================================
# TAB 3: ABOUT
# ============================================================

with tab_about:

    st.subheader("Project Purpose & Overview")

    st.markdown(
        """
        ### 🎯 Objective

        Developed to support international students at
        **Harbin Institute of Technology (HIT)** in mastering
        core daily Chinese and accelerating cultural adaptation.

        ### ✨ Key Highlights

        - 📇 Interactive flashcards with multi-category filters
          (HSK levels and campus vocabulary).
        - 🧠 Culture and campus knowledge check module.
        - 📱 Lightweight, responsive, and accessible on both
          desktop and mobile browsers.
        - 🎓 Tailored for international students at HIT.

        ### 👤 Author

        International Undergraduate Student, Harbin Institute
        of Technology.
        """
    )
