import os
import re
import math
import pickle
import subprocess
import sys
from collections import Counter

import streamlit as st

MODEL_PATH = "password_strength_model.pkl"

def features(password):
    length = len(password)
    counts = Counter(password)
    entropy_est = 0.0
    if length:
        for n in counts.values():
            p = n / length
            entropy_est -= p * math.log2(p)
    return [
        length,
        int(bool(re.search(r"[a-z]", password))),
        int(bool(re.search(r"[A-Z]", password))),
        int(bool(re.search(r"\d", password))),
        int(bool(re.search(r"[^A-Za-z0-9]", password))),
        int(bool(re.search(r"(.)\1{2,}", password))),
        int(bool(re.search(r"1234|abcd|qwerty|password|admin", password.lower()))),
        int(len(set(password)) / max(1, length) * 100),
        round(entropy_est, 3),
        int(any(ch.isspace() for ch in password)),
    ]

def load_model():
    if not os.path.exists(MODEL_PATH):
        with st.spinner("First-time setup: training the ML model..."):
            result = subprocess.run(
                [sys.executable, "train_model.py"],
                capture_output=True, text=True
            )
            if result.returncode != 0:
                st.error("Model training failed. Open the terminal and check the error.")
                st.code(result.stderr or result.stdout)
                st.stop()
    with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)

st.set_page_config(page_title="AI/ML Password Analyzer", page_icon="🔐")
st.title("🔐 AI/ML Password Strength Checker")
st.write("A machine-learning model predicts whether a password is Weak, Moderate, or Strong.")
st.info("For a class project, test with sample passwords only. Do not enter a password you currently use. This demo does not save the password.")
model = load_model()

password = st.text_input("Enter a sample password", type="password")
if password:
    x = [features(password)]
    prediction = model.predict(x)[0]
    probabilities = model.predict_proba(x)[0]
    classes = list(model.classes_)
    confidence = max(probabilities) * 100

    if prediction == "Weak":
        st.error(f"ML prediction: {prediction}")
    elif prediction == "Moderate":
        st.warning(f"ML prediction: {prediction}")
    else:
        st.success(f"ML prediction: {prediction}")

    st.metric("Model confidence (estimated)", f"{confidence:.1f}%")
    st.caption("Confidence is the model's estimate, not a guarantee of real-world security.")

    st.subheader("Feature analysis")
    checks = {
        "At least 12 characters": len(password) >= 12,
        "Lowercase letters": bool(re.search(r"[a-z]", password)),
        "Uppercase letters": bool(re.search(r"[A-Z]", password)),
        "Numbers": bool(re.search(r"\d", password)),
        "Special symbols": bool(re.search(r"[^A-Za-z0-9]", password)),
        "No repeated-character run (e.g. aaa)": not bool(re.search(r"(.)\1{2,}", password)),
        "No common predictable pattern": not bool(re.search(r"1234|abcd|qwerty|password|admin", password.lower())),
    }
    for label, passed in checks.items():
        st.write(("✅ " if passed else "❌ ") + label)

    st.subheader("Suggestions")
    tips = []
    if len(password) < 12: tips.append("Use a longer password or passphrase (12–16+ characters).")
    if not re.search(r"[a-z]", password): tips.append("Include lowercase letters.")
    if not re.search(r"[A-Z]", password): tips.append("Include uppercase letters.")
    if not re.search(r"\d", password): tips.append("Include numbers.")
    if not re.search(r"[^A-Za-z0-9]", password): tips.append("Consider adding symbols.")
    if re.search(r"(.)\1{2,}|1234|abcd|qwerty|password|admin", password.lower()): tips.append("Avoid repeated characters, common words, and predictable sequences.")
    if not tips: tips.append("Use a unique password for every account and store it in a trusted password manager.")
    for tip in tips: st.write("• " + tip)

with st.expander("About the machine-learning model"):
    st.write("Algorithm: Random Forest Classifier.")
    st.write("Input features: length, character groups, repeated characters, common patterns, character diversity, and estimated character diversity entropy.")
    st.write("Training data: generated synthetic examples with rule-based labels. This is a demonstration model, not a production-grade password security service.")
