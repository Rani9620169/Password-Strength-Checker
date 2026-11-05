# AI/ML Password Strength Checker & Security Analyzer

This is an educational machine-learning project using a Random Forest Classifier.

## Run on Windows (VS Code)
1. Extract the ZIP.
2. Open the extracted folder in VS Code.
3. Open Terminal > New Terminal.
4. Run these commands one at a time:

```bash
python -m pip install -r requirements.txt
python train_model.py
python -m streamlit run app.py
```

The training command creates `password_strength_model.pkl`. The app can also attempt to train the model automatically on first launch.

## How to explain to your teacher
"My project is an AI/ML-based Password Strength Checker and Security Analyzer. I used Python, Streamlit, and the Random Forest machine-learning algorithm. The model takes features like password length, uppercase and lowercase letters, digits, symbols, repeated characters, and common patterns. It predicts the password class as Weak, Moderate, or Strong and gives suggestions to improve it."

## Important limitation
The model is trained on synthetic examples whose labels are generated using simple rules. It demonstrates an ML workflow, but it is not a validated security product and does not check breached-password databases. The accuracy printed during training measures performance on synthetic held-out data only, not real-world password security. Use only sample passwords for testing.
