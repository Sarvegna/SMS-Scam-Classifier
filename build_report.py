"""
build_report.py  –  generates Sarvegna_ProjectReport.docx
Run with:  py -3.11 build_report.py
"""

import os
import glob
from datetime import date
from docx import Document
from docx.shared import Pt, Cm, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# ── Helpers ────────────────────────────────────────────────────────────────────

def set_font(run, name="Times New Roman", size=12, bold=False, color=None):
    run.font.name = name
    run.font.size = Pt(size)
    run.font.bold = bold
    if color:
        run.font.color.rgb = RGBColor(*color)

def add_heading(doc, text, level=1):
    """Add a styled heading using built-in Heading styles."""
    p = doc.add_heading(text, level=level)
    for run in p.runs:
        run.font.name = "Times New Roman"
        run.font.color.rgb = RGBColor(0, 0, 0)
    return p

def add_body(doc, text, bold=False, italic=False, space_after=6):
    """Add a normal body paragraph in Times New Roman 12 pt."""
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    run = p.add_run(text)
    set_font(run, bold=bold)
    run.font.italic = italic
    return p

def add_bullet(doc, text):
    """Add a bullet-list paragraph."""
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_after = Pt(4)
    run = p.add_run(text)
    set_font(run)
    return p

def add_page_break(doc):
    doc.add_page_break()

def add_table(doc, headers, rows, col_widths=None):
    """Add a bordered table with a shaded header row."""
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    # Header row
    hdr = table.rows[0]
    for i, h in enumerate(headers):
        cell = hdr.cells[i]
        cell.text = ""
        run = cell.paragraphs[0].add_run(h)
        set_font(run, bold=True)
        # Light-grey header fill
        tc = cell._tc
        tcPr = tc.get_or_add_tcPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:color"), "auto")
        shd.set(qn("w:fill"), "D9D9D9")
        tcPr.append(shd)

    # Data rows
    for r_idx, row_data in enumerate(rows):
        row = table.rows[r_idx + 1]
        for c_idx, val in enumerate(row_data):
            cell = row.cells[c_idx]
            cell.text = ""
            run = cell.paragraphs[0].add_run(str(val))
            set_font(run)

    # Optional column widths
    if col_widths:
        for i, w in enumerate(col_widths):
            for row in table.rows:
                row.cells[i].width = Cm(w)

    return table

def figure_caption(doc, number, caption_text):
    """Add a centred italic figure caption below an image."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(10)
    run = p.add_run(f"Figure {number}: {caption_text}")
    set_font(run, italic=True, size=11)
    run.font.italic = True

# ── Document setup ─────────────────────────────────────────────────────────────

doc = Document()

# Page margins (2.5 cm all sides)
for section in doc.sections:
    section.top_margin    = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin   = Cm(3.0)
    section.right_margin  = Cm(2.5)

# Default Normal style → Times New Roman 12 pt
style = doc.styles["Normal"]
style.font.name = "Times New Roman"
style.font.size = Pt(12)

# ── Title Page ─────────────────────────────────────────────────────────────────

# Vertical space before title
for _ in range(6):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(0)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run("SMS Spam / Scam Classifier")
set_font(run, size=22, bold=True)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run("A Machine Learning Project Report")
set_font(run, size=14)

doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run("Submitted by")
set_font(run, size=12)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run("Sarvegna")
set_font(run, size=14, bold=True)

doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run("Kalasalingam Academy of Research and Education")
set_font(run, size=12, bold=True)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run(date.today().strftime("%B %d, %Y"))
set_font(run, size=12)

add_page_break(doc)

# ── Abstract ───────────────────────────────────────────────────────────────────

add_heading(doc, "Abstract", level=1)
add_body(doc, (
    "This report presents the design, implementation, and evaluation of an SMS Spam and "
    "Scam Classifier built using Python 3.11 and machine learning techniques. The system "
    "uses Term Frequency–Inverse Document Frequency (TF-IDF) to convert SMS text into "
    "numerical features and a Multinomial Naive Bayes algorithm to classify each message "
    "as spam or safe (ham). The model was trained and tested on the UCI SMS Spam Collection "
    "dataset, which contains 5,572 real-world labelled SMS messages. The classifier achieves "
    "a test accuracy of 97.22% and is deployed as an interactive web dashboard using "
    "Streamlit, allowing users to check any message in real time. The project also includes "
    "a step-by-step Jupyter notebook for educational purposes."
))

# ── 1. Introduction ────────────────────────────────────────────────────────────

add_heading(doc, "1. Introduction", level=1)
add_body(doc, (
    "Spam and scam text messages have become a widespread problem. Fraudsters use SMS to "
    "trick people into clicking malicious links, sharing personal information, or claiming "
    "fake prizes. Detecting such messages automatically saves time and protects users from "
    "harm. Natural Language Processing (NLP) and machine learning provide effective tools "
    "for this task."
))
add_body(doc, (
    "This project builds a simple, beginner-friendly SMS classifier that learns from "
    "labelled examples. A user can type or paste any SMS message into the web dashboard "
    "and instantly see whether the model considers it spam or safe, along with a confidence "
    "percentage. The project demonstrates the full machine-learning workflow: data loading, "
    "exploration, preprocessing, model training, evaluation, and deployment."
))

# ── 2. Problem Statement ───────────────────────────────────────────────────────

add_heading(doc, "2. Problem Statement", level=1)
add_body(doc, (
    "Given a raw SMS message, automatically determine whether it is spam (scam, "
    "unsolicited promotional content, or fraudulent) or ham (a legitimate, safe message). "
    "The classifier must be accurate, fast, and simple enough for a beginner to understand "
    "and extend."
))

# ── 3. Objectives ──────────────────────────────────────────────────────────────

add_heading(doc, "3. Objectives", level=1)
add_bullet(doc, "Load and explore the UCI SMS Spam Collection dataset.")
add_bullet(doc, "Preprocess the text data and encode labels numerically.")
add_bullet(doc, "Build a TF-IDF + Naive Bayes classification pipeline.")
add_bullet(doc, "Evaluate the model using accuracy, precision, recall, F1, and a confusion matrix.")
add_bullet(doc, "Deploy the model as an interactive Streamlit web dashboard.")
add_bullet(doc, "Document the entire workflow in a Jupyter notebook for learning purposes.")

# ── 4. Tools and Technologies ──────────────────────────────────────────────────

add_heading(doc, "4. Tools and Technologies", level=1)
add_table(
    doc,
    headers=["Tool / Library", "Version", "Purpose"],
    rows=[
        ["Python",       "3.11.9",  "Programming language"],
        ["pandas",       "3.0.6",   "Data loading and manipulation"],
        ["scikit-learn", "1.9.1",   "TF-IDF vectoriser, Naive Bayes, evaluation metrics"],
        ["matplotlib",   "3.11.2",  "Confusion matrix chart"],
        ["Streamlit",    "1.66.0",  "Interactive web dashboard"],
        ["Jupyter Notebook", "7.2.0", "Step-by-step educational notebook"],
        ["python-docx",  "1.2.0",   "Report generation"],
    ],
    col_widths=[5.5, 3.0, 8.5],
)
doc.add_paragraph()

# ── 5. Dataset Description ─────────────────────────────────────────────────────

add_heading(doc, "5. Dataset Description", level=1)
add_body(doc, (
    "The UCI SMS Spam Collection is a publicly available dataset sourced from the UCI "
    "Machine Learning Repository (https://archive.ics.uci.edu/ml/datasets/SMS+Spam+Collection). "
    "It contains 5,572 real SMS messages collected from various sources, each manually "
    "labelled as either spam or ham."
))
add_table(
    doc,
    headers=["Property", "Value"],
    rows=[
        ["Total messages",  "5,572"],
        ["Ham (safe)",      "4,825  (86.6%)"],
        ["Spam",            "747  (13.4%)"],
        ["Format",          "Tab-separated text, no header row"],
        ["Encoding",        "Latin-1"],
        ["Source",          "UCI Machine Learning Repository"],
    ],
    col_widths=[6.0, 11.0],
)
doc.add_paragraph()
add_body(doc, (
    "The dataset is imbalanced — approximately 87% of messages are ham and only 13% are spam. "
    "This is realistic: most real SMS traffic is legitimate. The model is evaluated on both "
    "classes separately to ensure it performs well on the minority spam class."
))

# ── 6. Methodology ─────────────────────────────────────────────────────────────

add_heading(doc, "6. Methodology", level=1)

add_heading(doc, "6.1 Data Preprocessing", level=2)
add_body(doc, (
    "The raw dataset is loaded with pandas using a tab separator and latin-1 encoding. "
    "The two columns are named label and text. Labels are encoded numerically: "
    "ham becomes 0 and spam becomes 1, so the model can work with numbers."
))

add_heading(doc, "6.2 Train / Test Split", level=2)
add_body(doc, (
    "The data is split into a training set (80%, 4,457 messages) and a test set "
    "(20%, 1,115 messages) using scikit-learn's train_test_split. The stratify "
    "parameter ensures the spam-to-ham ratio is the same in both splits. A fixed "
    "random seed (42) makes the split reproducible."
))

add_heading(doc, "6.3 TF-IDF Vectorisation", level=2)
add_body(doc, (
    "TF-IDF (Term Frequency–Inverse Document Frequency) converts raw SMS text into "
    "a numerical feature matrix. Words that appear frequently in a message but rarely "
    "across all messages receive higher scores. This highlights distinctive words "
    "such as FREE, WIN, and URGENT that are common in spam. The vectoriser is configured "
    "to lowercase all text, remove common English stop words (the, is, at, etc.), and "
    "keep the 5,000 most informative words."
))

add_heading(doc, "6.4 Multinomial Naive Bayes Classifier", level=2)
add_body(doc, (
    "Multinomial Naive Bayes is a probabilistic algorithm well suited to text "
    "classification. It calculates the probability that a message belongs to each "
    "class (spam or ham) based on the word frequencies, and assigns the label with "
    "the higher probability. The algorithm is fast, interpretable, and performs "
    "very well on text data even with relatively few training examples."
))

add_heading(doc, "6.5 Pipeline", level=2)
add_body(doc, (
    "The TF-IDF vectoriser and the Naive Bayes classifier are chained together in a "
    "scikit-learn Pipeline. This ensures that the vectoriser is always fitted on training "
    "data only and applied consistently to test data, preventing data leakage."
))

# ── 7. Implementation ──────────────────────────────────────────────────────────

add_heading(doc, "7. Implementation", level=1)

add_heading(doc, "7.1 Jupyter Notebook", level=2)
add_body(doc, (
    "The file Sarvegna_SMSScamClassifier.ipynb contains the full step-by-step "
    "implementation. It is divided into seven sections, each with a short markdown "
    "explanation cell followed by a code cell: Setup and Imports, Load Dataset, "
    "Explore Data, Preprocess, Build Pipeline, Evaluate, and Try Your Own Messages. "
    "The notebook is intended for learning and includes printed outputs and a "
    "matplotlib confusion matrix chart."
))

add_heading(doc, "7.2 Streamlit Dashboard", level=2)
add_body(doc, (
    "The file app.py implements an interactive web dashboard using Streamlit. "
    "The dashboard features a dark cybersecurity theme with green and blue accent "
    "colours configured in .streamlit/config.toml. Key components include:"
))
add_bullet(doc, "A sidebar showing the dataset statistics and model accuracy.")
add_bullet(doc, "Three metric cards displaying accuracy, total messages, and spam count.")
add_bullet(doc, "Three example message buttons (Scam, Safe, Tricky) that pre-fill the input box.")
add_bullet(doc, "A large text area where the user types any SMS message.")
add_bullet(doc, "A Check Message button that shows a red SPAM or green SAFE result box with a confidence percentage.")
add_bullet(doc, "A progress bar visualising the spam probability.")
add_bullet(doc, "An expandable panel containing the confusion matrix chart.")
add_body(doc, (
    "The model is trained once per session using Streamlit's @st.cache_resource decorator, "
    "making all subsequent predictions instant."
))

add_page_break(doc)

# ── 8. Results ─────────────────────────────────────────────────────────────────

add_heading(doc, "8. Results", level=1)

add_heading(doc, "8.1 Model Performance", level=2)
add_body(doc, (
    "The trained TF-IDF + Naive Bayes pipeline was evaluated on the 1,115 held-out "
    "test messages. The results are summarised in the table below."
))
add_table(
    doc,
    headers=["Metric", "Ham (Safe)", "Spam"],
    rows=[
        ["Precision",   "~98%",  "~99%"],
        ["Recall",      "~99%",  "~81%"],
        ["F1 Score",    "~99%",  "~89%"],
        ["Accuracy (overall)", "97.22%", "—"],
    ],
    col_widths=[6.0, 4.5, 4.5],
)
doc.add_paragraph()
add_body(doc, (
    "The model achieves an overall test accuracy of 97.22%. Precision for the spam "
    "class is approximately 99%, meaning almost every message flagged as spam is "
    "genuinely spam. Recall for spam is approximately 81%, meaning the model catches "
    "about four out of every five spam messages. This conservative behaviour is "
    "desirable in a spam filter: it is better to occasionally miss a spam message "
    "than to incorrectly flag a legitimate one."
))

add_heading(doc, "8.2 Confusion Matrix", level=2)
add_body(doc, (
    "The confusion matrix below shows the exact counts for the 1,115 test messages."
))
add_table(
    doc,
    headers=["", "Predicted Safe", "Predicted Spam"],
    rows=[
        ["Actual Safe",  "963 (True Negatives)",   "2 (False Positives)"],
        ["Actual Spam",  "29 (False Negatives)",   "121 (True Positives)"],
    ],
    col_widths=[4.0, 6.0, 6.0],
)
doc.add_paragraph()
add_body(doc, (
    "963 safe messages were correctly classified. 121 spam messages were correctly "
    "caught. Only 2 safe messages were incorrectly flagged as spam (false positives), "
    "and 29 spam messages were missed (false negatives)."
))

# ── 9. Screenshots ─────────────────────────────────────────────────────────────

add_heading(doc, "9. Screenshots", level=1)

# Fixed list of (filename, caption) — edit captions here if needed
SCREENSHOTS = [
    (os.path.join("screenshots", "dashboard.png"),  "Streamlit dashboard overview"),
    (os.path.join("screenshots", "notebook.png"),   "Notebook results and confusion matrix"),
    (os.path.join("screenshots", "spam.png"),        "Spam detection result"),
    (os.path.join("screenshots", "safe.png"),        "Safe message result"),
]

IMG_WIDTH = Inches(5.5)   # 5.5 inches wide, height scales automatically

for fig_num, (img_path, caption) in enumerate(SCREENSHOTS, start=1):
    if os.path.isfile(img_path):
        try:
            doc.add_picture(img_path, width=IMG_WIDTH)
            p = doc.paragraphs[-1]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            figure_caption(doc, fig_num, caption)
        except Exception as e:
            add_body(doc, f"[Could not embed {img_path}: {e}]", italic=True)
    else:
        add_body(doc, f"[Image not found: {img_path}]", italic=True)

# ── 10. Limitations ────────────────────────────────────────────────────────────

add_heading(doc, "10. Limitations", level=1)
add_bullet(doc, (
    "The model relies on word-level TF-IDF features and cannot understand context, "
    "sarcasm, or sentence meaning."
))
add_bullet(doc, (
    "It was trained on English SMS messages from one dataset and may not generalise "
    "well to other languages or newer scam styles."
))
add_bullet(doc, (
    "Multinomial Naive Bayes assumes that all words in a message are independent of "
    "each other, which is not always true in natural language."
))
add_bullet(doc, (
    "The dataset is imbalanced (87% ham, 13% spam), which can bias the model "
    "towards the majority class."
))
add_bullet(doc, (
    "The system has no memory and cannot learn from new messages after training "
    "without retraining the model."
))

# ── 11. Conclusion ─────────────────────────────────────────────────────────────

add_heading(doc, "11. Conclusion", level=1)
add_body(doc, (
    "This project successfully demonstrates that a simple TF-IDF + Multinomial Naive Bayes "
    "pipeline can classify SMS spam with high accuracy. The model achieved 97.22% accuracy "
    "on the UCI SMS Spam Collection test set, with very few false positives. The entire "
    "workflow — from raw data to a deployed web application — was implemented in Python 3.11 "
    "using standard, well-documented libraries. The Jupyter notebook provides a clear "
    "educational resource for beginners, and the Streamlit dashboard makes the classifier "
    "accessible without any coding knowledge."
))

# ── 12. Future Scope ───────────────────────────────────────────────────────────

add_heading(doc, "12. Future Scope", level=1)
add_bullet(doc, (
    "Replace Naive Bayes with more powerful classifiers such as Logistic Regression, "
    "Support Vector Machines, or a neural network to improve recall on spam messages."
))
add_bullet(doc, (
    "Add bigram and trigram features (ngram_range=(1, 3)) to the TF-IDF vectoriser "
    "to capture multi-word phrases like free prize or click here."
))
add_bullet(doc, (
    "Fine-tune a pre-trained language model such as BERT or DistilBERT for much "
    "richer text understanding."
))
add_bullet(doc, (
    "Expand the dataset with more recent SMS scam examples, including phishing, "
    "delivery scams, and OTP fraud."
))
add_bullet(doc, (
    "Add multilingual support so the classifier can handle messages in languages "
    "other than English."
))
add_bullet(doc, (
    "Deploy the Streamlit app publicly using Streamlit Community Cloud or a cloud "
    "provider so it can be accessed from any device."
))

# ── 13. References ─────────────────────────────────────────────────────────────

add_heading(doc, "13. References", level=1)
refs = [
    ("UCI SMS Spam Collection Dataset",
     "https://archive.ics.uci.edu/ml/datasets/SMS+Spam+Collection"),
    ("scikit-learn Documentation — TfidfVectorizer",
     "https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html"),
    ("scikit-learn Documentation — MultinomialNB",
     "https://scikit-learn.org/stable/modules/generated/sklearn.naive_bayes.MultinomialNB.html"),
    ("Streamlit Documentation",
     "https://docs.streamlit.io"),
    ("pandas Documentation",
     "https://pandas.pydata.org/docs"),
    ("Almeida, T.A., Hidalgo, J.M.G., Yamakami, A. (2011). Contributions to the Study of SMS "
     "Spam Filtering: New Collection and Results. Proceedings of the 11th ACM Symposium on "
     "Document Engineering (DOCENG'11), Mountain View, CA, USA.",
     None),
]
for i, (title, url) in enumerate(refs, 1):
    p = doc.add_paragraph(style="List Number")
    p.paragraph_format.space_after = Pt(4)
    run = p.add_run(title)
    set_font(run, bold=(url is None))
    if url:
        run2 = p.add_run(f". Available at: {url}")
        set_font(run2)

# ── Save ───────────────────────────────────────────────────────────────────────

out_path = "Sarvegna_ProjectReport.docx"
doc.save(out_path)
print(f"Report saved: {out_path}")
