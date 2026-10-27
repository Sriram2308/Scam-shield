"""Scam classifier: TF-IDF char n-grams + logistic regression, blended with
transparent rule signals. Works offline with Tamil, Hindi, English and
transliterated (Hinglish/Tanglish) text. Swap in a BERT model via docs/ARCHITECTURE.md."""
import csv
import re
from functools import lru_cache
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "sample_messages.csv"

URL_RE = re.compile(r"(https?://\S+|www\.\S+)", re.I)
BAD_TLD_RE = re.compile(r"\.(xyz|top|club|info|link|click|apk)\b", re.I)

# name -> (regex, weight)
SIGNALS = {
    "urgency": (
        r"\b(urgent|immediately|today|tonight|last chance|expires?|turant|udane)\b|உடனே|तुरंत|आज ही",
        0.15,
    ),
    "credential_request": (
        r"\b(share|send|enter|tell|verify|bhejein)\b.{0,25}\b(otp|pin|cvv|password)\b|\botp\b.{0,15}\b(share|send)\b|OTP भेजें",
        0.35,
    ),
    "fee_demand": (
        r"(registration|processing|training|delivery|claim)\s+fee|शुल्क|கட்டணம்|फीस",
        0.25,
    ),
    "threat": (
        r"(blocked|suspended|disconnected|band ho|block aaga)|खाता बंद|முடக்க",
        0.2,
    ),
}

# scam type -> regex (first match wins, order matters)
TYPE_PATTERNS = [
    ("upi_refund", r"collect request|refund|cashback|upi pin"),
    ("loan_app", r"loan.*(approved|instant)|pre-approved|\.apk|\bapk\b"),
    ("parcel", r"parcel|courier|customs|delivery (failed|fee)"),
    ("job_offer", r"work from home|part.?time|earn .*(per day|daily)|hiring|घर बैठे|வீட்டிலிருந்தே"),
    ("lottery_prize", r"lottery|lucky draw|winner|won |prize|इनाम|பரிசு"),
    ("kyc_bank", r"kyc|pan |account.*(block|suspend)|bank|खाता|केवाईसी|வங்கி"),
]


@lru_cache(maxsize=1)
def _model():
    texts, labels = [], []
    with open(DATA_PATH, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            texts.append(row["text"])
            labels.append(int(row["label"]))
    pipe = make_pipeline(
        TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), lowercase=True, sublinear_tf=True),
        LogisticRegression(C=5.0, max_iter=1000, class_weight="balanced"),
    )
    pipe.fit(texts, labels)
    return pipe


def detect_signals(text: str) -> dict:
    found = {}
    for name, (pattern, weight) in SIGNALS.items():
        if re.search(pattern, text, re.I | re.S):
            found[name] = weight
    if URL_RE.search(text):
        found["link"] = 0.2
        if BAD_TLD_RE.search(text):
            found["suspicious_domain"] = 0.2
    return found


def detect_type(text: str) -> str:
    for scam_type, pattern in TYPE_PATTERNS:
        if re.search(pattern, text, re.I):
            return scam_type
    return "generic"


def classify(text: str) -> dict:
    text = (text or "").strip()
    ml_prob = float(_model().predict_proba([text])[0][1])
    signals = detect_signals(text)
    rule_score = min(1.0, sum(signals.values()))
    score = 0.5 * ml_prob + 0.5 * rule_score
    if rule_score >= 0.6:
        score = max(score, rule_score)
    score = round(min(1.0, score), 3)
    level = "high" if score >= 0.7 else "suspicious" if score >= 0.4 else "likely_safe"
    return {
        "score": score,
        "level": level,
        "scam_type": detect_type(text) if level != "likely_safe" else None,
        "signals": sorted(signals),
        "ml_probability": round(ml_prob, 3),
    }
