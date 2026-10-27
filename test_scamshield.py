import pytest
from fastapi.testclient import TestClient

from app.classifier import classify, detect_type
from app.main import app

client = TestClient(app)

SCAMS = [
    "Your SBI account will be blocked today. Update KYC now at http://sbi-kyc.xyz and share OTP",
    "Congratulations! You won Rs 25 lakh in lucky draw. Pay Rs 5000 processing fee to claim prize",
    "Work from home part time job. Earn Rs 4000 per day. Pay registration fee to join",
    "உங்கள் வங்கி கணக்கு முடக்கப்படும். உடனே KYC புதுப்பிக்க இந்த லிங்கை கிளிக் செய்யவும்",
]
SAFE = [
    "Hi are we still meeting for lunch at 1 pm tomorrow",
    "Your OTP is 731942. Do not share it with anyone.",
    "நாளை மாலை 5 மணிக்கு சந்திக்கலாம்",
]


@pytest.mark.parametrize("msg", SCAMS)
def test_scams_flagged(msg):
    assert classify(msg)["level"] in ("high", "suspicious")


@pytest.mark.parametrize("msg", SAFE)
def test_safe_not_flagged(msg):
    assert classify(msg)["level"] == "likely_safe"


def test_scam_type_detection():
    assert detect_type("You won the lottery, claim your prize") == "lottery_prize"
    assert detect_type("Update your KYC or account blocked") == "kyc_bank"


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


@pytest.mark.parametrize("lang", ["en", "ta", "hi"])
def test_api_languages(lang):
    r = client.post("/api/check", json={"message": SCAMS[0], "lang": lang})
    assert r.status_code == 200
    body = r.json()
    assert body["level"] == "high" and len(body["steps"]) == 3 and body["explanation"]


def test_tamil_explanation_is_tamil():
    r = client.post("/api/check", json={"message": SCAMS[0], "lang": "ta"}).json()
    assert any("\u0b80" <= ch <= "\u0bff" for ch in r["explanation"])


def test_validation():
    assert client.post("/api/check", json={"message": "", "lang": "en"}).status_code == 422
