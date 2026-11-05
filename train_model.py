import math
import pickle
import random
import re
from collections import Counter

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer

random.seed(42)

COMMON = ["password", "qwerty", "admin", "welcome", "letmein", "abc123", "iloveyou", "dragon", "monkey"]
LOWER = "abcdefghijklmnopqrstuvwxyz"
UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
DIGITS = "0123456789"
SYMBOLS = "!@#$%&*?_+-"

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
        len(set(password)) / max(1, length) * 100,
        entropy_est,
        int(any(ch.isspace() for ch in password)),
    ]

def make_password():
    style = random.randrange(6)
    length = random.randint(3, 24)
    if style == 0:
        return random.choice(COMMON)
    if style == 1:
        return random.choice(COMMON) + str(random.randint(1, 9999))
    pool = LOWER
    if style >= 2: pool += UPPER
    if style >= 3: pool += DIGITS
    if style >= 4: pool += SYMBOLS
    p = ''.join(random.choice(pool) for _ in range(length))
    if style == 5 and len(p) >= 3 and random.random() < .3:
        p = p[:2] + p[1] * 3 + p[5:]
    return p

def label_password(p):
    lower = bool(re.search(r"[a-z]", p))
    upper = bool(re.search(r"[A-Z]", p))
    digit = bool(re.search(r"\d", p))
    symbol = bool(re.search(r"[^A-Za-z0-9]", p))
    predictable = bool(re.search(r"1234|abcd|qwerty|password|admin", p.lower()))
    repeated = bool(re.search(r"(.)\1{2,}", p))
    score = sum([len(p) >= 12, lower, upper, digit, symbol])
    if p.lower() in COMMON or predictable or len(p) < 8 or repeated:
        return "Weak"
    if len(p) >= 16 and score >= 4:
        return "Strong"
    if len(p) >= 12 and score >= 4:
        return "Strong"
    if len(p) >= 10 and score >= 3:
        return "Moderate"
    if len(p) >= 8 and score >= 3:
        return "Moderate"
    return "Weak"

if __name__ == "__main__":
    passwords = [make_password() for _ in range(6000)]
    X = [features(p) for p in passwords]
    y = [label_password(p) for p in passwords]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    model = RandomForestClassifier(
        n_estimators=180, max_depth=14, class_weight="balanced", random_state=42
    )
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    print("Validation accuracy on synthetic held-out examples:", round(accuracy_score(y_test, predictions), 3))
    print(classification_report(y_test, predictions, zero_division=0))
    with open("password_strength_model.pkl", "wb") as f:
        pickle.dump(model, f)
    print("Saved trained model: password_strength_model.pkl")
