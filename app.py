import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, ConfusionMatrixDisplay

# ── Page config (must be first Streamlit call) ─────────────────────────────────
st.set_page_config(
    page_title="SMS Scam Classifier",
    page_icon="🛡️",
    layout="centered",
)

# ── Custom CSS — tighten card styling and color result boxes ───────────────────
st.markdown("""
<style>
/* Center the main title */
h1 { text-align: center; }

/* Metric card border */
[data-testid="metric-container"] {
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 12px;
    background-color: #161b22;
}

/* SPAM result box */
.result-spam {
    background-color: #3d0000;
    border: 1px solid #ff4444;
    border-radius: 8px;
    padding: 18px 20px;
    color: #ff6b6b;
    font-size: 1.2rem;
    font-weight: 600;
}

/* SAFE result box */
.result-safe {
    background-color: #002200;
    border: 1px solid #00ff88;
    border-radius: 8px;
    padding: 18px 20px;
    color: #00ff88;
    font-size: 1.2rem;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# ── Load data & train model (cached — runs only once per session) ──────────────
@st.cache_resource
def load_and_train():
    df = pd.read_csv(
        "data/sms_spam.csv",
        sep="\t", header=None,
        names=["label", "text"],
        encoding="latin-1",
    )
    df["label_num"] = df["label"].map({"spam": 1, "ham": 0})

    X, y = df["text"], df["label_num"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    model = Pipeline([
        ("tfidf", TfidfVectorizer(lowercase=True, stop_words="english", max_features=5000)),
        ("clf",   MultinomialNB()),
    ])
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    cm  = confusion_matrix(y_test, y_pred)

    spam_count = int(df["label_num"].sum())
    return model, acc, len(df), spam_count, cm

model, accuracy, total_msgs, spam_msgs, cm = load_and_train()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🛡️ SMS Scam Classifier")
    st.markdown("---")
    st.markdown("**Project**")
    st.markdown("Classifies SMS messages as **SPAM** or **SAFE** using TF-IDF + Naive Bayes.")
    st.markdown("---")
    st.markdown("**Dataset**")
    st.markdown(
        "📂 UCI SMS Spam Collection  \n"
        f"📨 {total_msgs:,} messages  \n"
        f"🚨 {spam_msgs:,} spam  \n"
        f"✅ {total_msgs - spam_msgs:,} safe (ham)"
    )
    st.markdown("---")
    st.markdown("**Model**")
    st.markdown(
        "🔬 TF-IDF Vectoriser (5,000 features)  \n"
        "🤖 Multinomial Naive Bayes  \n"
        f"🎯 Test accuracy: **{accuracy*100:.2f}%**"
    )
    st.markdown("---")
    st.caption("Python 3.11 · scikit-learn · Streamlit")

# ── Title ──────────────────────────────────────────────────────────────────────
st.title("🛡️ SMS Scam Classifier")
st.markdown(
    "<p style='text-align:center; color:#8b949e;'>"
    "Paste any SMS message below to instantly detect spam or scam attempts."
    "</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

# ── Metric cards ───────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
col1.metric("🎯 Model Accuracy",   f"{accuracy*100:.2f}%")
col2.metric("📨 Total Messages",   f"{total_msgs:,}")
col3.metric("🚨 Spam Messages",    f"{spam_msgs:,}")

st.markdown("---")

# ── Example message buttons ────────────────────────────────────────────────────
st.markdown("**Try an example:**")
ex_col1, ex_col2, ex_col3 = st.columns(3)

# Each button stores an example message in session state so it pre-fills the text box
if ex_col1.button("🚨 Scam example"):
    st.session_state["sms_input"] = "URGENT: Your bank account has been locked. Verify now at http://secure-login.biz or lose access."
if ex_col2.button("✅ Safe example"):
    st.session_state["sms_input"] = "Hey, are you coming to dinner tonight? Let me know by 6."
if ex_col3.button("🤔 Tricky example"):
    st.session_state["sms_input"] = "Your delivery is waiting. Please confirm your address to reschedule."

# ── Message input ──────────────────────────────────────────────────────────────
user_input = st.text_area(
    label="SMS Message",
    value=st.session_state.get("sms_input", ""),
    placeholder='Type or paste an SMS message here…',
    height=130,
    key="sms_input",
)

check_btn = st.button("🔍 Check Message", type="primary", use_container_width=True)

# ── Result ─────────────────────────────────────────────────────────────────────
if check_btn:
    if not user_input.strip():
        st.warning("⚠️ Please enter a message before checking.")
    else:
        # Get prediction and class probabilities
        pred  = model.predict([user_input])[0]          # 0 = safe, 1 = spam
        proba = model.predict_proba([user_input])[0]    # [p_safe, p_spam]
        p_spam = proba[1]
        p_safe = proba[0]

        st.markdown("### Result")

        if pred == 1:
            st.markdown(
                f'<div class="result-spam">🚨 SPAM &nbsp;·&nbsp; {p_spam*100:.1f}% confidence</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="result-safe">✅ SAFE &nbsp;·&nbsp; {p_safe*100:.1f}% confidence</div>',
                unsafe_allow_html=True,
            )

        st.markdown("")  # spacer

        # Progress bar — always shows spam probability (red end = spam)
        st.markdown("**Spam probability**")
        st.progress(float(p_spam))
        st.caption(f"P(safe) = {p_safe*100:.1f}%   ·   P(spam) = {p_spam*100:.1f}%")

# ── Confusion matrix (in an expander so it doesn't clutter the page) ──────────
st.markdown("---")
with st.expander("📊 Confusion Matrix (test set)"):
    st.markdown(
        "The confusion matrix shows how well the model performed on the **20% test set** it never saw during training."
    )

    # Build the chart with matplotlib dark styling to match the theme
    matplotlib.rcParams.update({
        "figure.facecolor":  "#161b22",
        "axes.facecolor":    "#161b22",
        "axes.edgecolor":    "#30363d",
        "text.color":        "#e6edf3",
        "xtick.color":       "#e6edf3",
        "ytick.color":       "#e6edf3",
    })

    fig, ax = plt.subplots(figsize=(4, 3.5))
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["Safe", "Spam"])
    disp.plot(ax=ax, colorbar=False, cmap="Blues")
    ax.set_title("Confusion Matrix", color="#e6edf3", pad=10)
    # Style the text inside the matrix cells
    for text in disp.text_.ravel():
        text.set_color("#e6edf3")
    plt.tight_layout()

    st.pyplot(fig, use_container_width=False)

    # Show raw numbers below the chart
    tn, fp, fn, tp = cm.ravel()
    st.caption(
        f"True Safe: {tn}  ·  False Spam: {fp}  ·  "
        f"Missed Spam: {fn}  ·  True Spam: {tp}"
    )
