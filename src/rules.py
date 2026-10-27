
from dataclasses import dataclass
import re
import unicodedata


@dataclass(frozen=True)
class Rule:
    name: str
    weight: int
    phrases: tuple[str, ...]


# Each rule represents one type of risk signal.
# The weights are experimental scores, not probabilities.
RULES = (
    Rule(
        "credential_request",
        4,
        (
            "رمز التحقق",
            "رمز تحقق",
            "كود التحقق",
            "كود التفعيل",
            "كلمة المرور",
            "الرمز السري",
            "الرقم السري",
            "otp",
        ),
    ),
    Rule(
        "financial_data_request",
        3,
        (
            "بياناتك المالية",
            "بيانات مالية",
            "معلومات مالية",
            "بياناتك المصرفية",
            "رقم بطاقتك",
            "بيانات البطاقة",
            "معلومات البطاقة",
        ),
    ),
    Rule(
        "advance_payment_request",
        3,
        (
            "عربون",
            "دفعة مقدمة",
            "دفعة مسبقة",
            "ادفع مقدما",
        ),
    ),
    Rule(
        "currency_exchange_request",
        2,
        (
            "الدولار السياحي",
            "حجز الدولار",
            "حجز حصتك",
        ),
    ),
    Rule(
        "unverified_benefit",
        2,
        (
            "ضمن المستفيدين",
            "منحة",
            "جائزة",
            "ربحت",
            "مكافأة",
        ),
    ),
    Rule(
        "impersonation",
        1,
        (
            "دعم المحفظة",
            "الدعم الفني",
            "الدعم الرسمي",
            "إدارة المحفظة",
        ),
    ),
    Rule(
        "urgency_pressure",
        1,
        (
            "خلال عشر دقايق",
            "خلال 10 دقايق",
            "عشر دقايق",
            "خلال عشر دقائق",
            "عشر دقائق",
            "الفرصة تنتهي",
            "تنتهي اليوم",
            "راح يتوقف",
            "راح يتوقف حسابك",
            "إيقاف الحساب",
            "خلال دقائق",
            "فورا",
            "فوراً",
            "حالاً",
        ),
    ),
    Rule(
        "mild_urgency",
        1,
        (
            "بسرعة",
            "بأسرع وقت",
        ),
    ),
    Rule(
        "suspicious_link",
        1,
        (
            "افتح الرابط",
            "اضغط الرابط",
            "افتح الرابط وسجل",
        ),
    ),
    Rule(
        "vague_account_claim",
        1,
        (
            "حسابك بيه مشكلة",
            "حسابك فيه مشكلة",
            "مشكلة بحسابك",
            "مشكلة في حسابك",
            "حسابك بيه خلل",
        ),
    ),
)


MIXED_INPUT_CUES = (
    "وصلتني هاي الرسالة",
    "وصلتني هذه الرسالة",
    "الرسالة اللي وصلتني",
    "هذا نص الرسالة",
    "نص الرسالة هو",
    "شنو رأيك",
    "شنو رايك",
    "بس للتوضيح",
    "للتوضيح",
    "السياق هو",
    "أعتقد أن",
    "اعتقد ان",
)


def _normalize(text: str) -> str:
    """Normalize Arabic letter variants, diacritics, and whitespace."""
    text = text.casefold()

    text = text.translate(
        str.maketrans({
            "أ": "ا",
            "إ": "ا",
            "آ": "ا",
            "ٱ": "ا",
            "ى": "ي",
            "ـ": "",
        })
    )

    text = "".join(
        char
        for char in text
        if unicodedata.category(char) != "Mn"
    )

    return re.sub(r"\s+", " ", text).strip()


def _first_match(
    normalized_text: str,
    phrases: tuple[str, ...],
) -> str | None:
    """Return the first phrase matched as a complete phrase."""
    for phrase in phrases:
        normalized_phrase = _normalize(phrase)

        if not normalized_phrase:
            continue

        # Allow flexible whitespace between words.
        parts = normalized_phrase.split()
        phrase_pattern = r"\s+".join(
            re.escape(part) for part in parts
        )

        # Avoid matching a phrase inside a longer word.
        pattern = rf"(?<!\w){phrase_pattern}(?!\w)"

        if re.search(pattern, normalized_text):
            return phrase

    return None


def analyze_message(message_text: str) -> dict:
    """
    Analyze only the original message text.

    User context and transfer context must be processed separately.
    The score is an experimental rule-based score, not a probability.
    """
    if not isinstance(message_text, str):
        raise TypeError("message_text must be a string")

    normalized_text = _normalize(message_text)

    if not normalized_text:
        raise ValueError("message_text must not be empty")

    signals = []

    for rule in RULES:
        matched_phrase = _first_match(
            normalized_text,
            rule.phrases,
        )

        if matched_phrase is not None:
            signals.append({
                "name": rule.name,
                "weight": rule.weight,
                "matched_phrase": matched_phrase,
            })

    score = sum(signal["weight"] for signal in signals)

    if score >= 4:
        response = "warn"
        explanation = (
            "ظهرت مؤشرات تستدعي الحذر والتحقق قبل اتخاذ أي إجراء."
        )
    elif score > 0:
        response = "clarify"
        explanation = (
            "ظهرت مؤشرات محدودة؛ نحتاج إلى التحقق من السياق."
        )
    else:
        response = "no_clear_indicators"
        explanation = (
            "لم تكشف القواعد الحالية عن مؤشرات واضحة. "
            "هذا لا يثبت أن الرسالة آمنة."
        )

    possible_mixed_input = any(
        _first_match(normalized_text, (cue,)) is not None
        for cue in MIXED_INPUT_CUES
    )

    return {
        "response": response,
        "score": score,
        "signals": signals,
        "possible_mixed_input": possible_mixed_input,
        "message_only": True,
        "explanation": explanation,
    }
