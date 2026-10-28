
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
            "معلومات بطاقتك",
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
        "relative_impersonation",
        2,
        (
            "اني ابن عمك",
            "انا ابن عمك",
            "اني اخوك",
            "انا اخوك",
            "اني اختك",
            "انا اختك",
        ),
    ),
    Rule(
        "transfer_request",
        2,
        (
            "حوللي فلوس",
            "حول لي فلوس",
            "حول فلوسك",
            "حول فلوس",
            "دزلي فلوس",
            "دز لي فلوس",
            "دزلي المبلغ",
            "دز لي المبلغ",
        ),
    ),
    Rule(
        "verification_avoidance",
        2,
        (
            "لا تتصل بي",
            "لا تتصل",
            "لا تدق علي",
            "لا تحجي وياه",
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
            "بنهاية اليوم",
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
            "لا تتأخر",
            "هسه",
            "استعجل",
        ),
    ),
    Rule(
        "safe_account_transfer",
        3,
        (
            "الحساب الآمن",
            "حساب آمن",
            "حول فلوسك لهذا الحساب",
            "انقل فلوسك لهذا الحساب",
            "حتى نحمي رصيدك",
            "نحمي رصيدك من الاختراق",
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
    Rule(
        "extortion_threat",
        4,
        (
            "عندي صورك ومعلوماتك اذا ما وصل المبلغ",
            "عندي صورك اذا ما وصل المبلغ",
            "عندي معلوماتك اذا ما وصل المبلغ",
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

PROTECTIVE_CREDENTIAL_WARNINGS = (
    "لا تشارك رمز التحقق",
    "لا تشارك كود التحقق",
    "لا تعطي رمز التحقق",
    "لا ترسل رمز التحقق",
    "لا تفصح عن رمز التحقق",
    "لا تشارك كلمة المرور",
)

EXPLICIT_CREDENTIAL_REQUESTS = (
    "ارسل رمز التحقق",
    "ارسل لي رمز التحقق",
    "اعطني رمز التحقق",
    "زودني برمز التحقق",
    "شارك رمز التحقق",
    "ارسل كود التحقق",
    "اعطني كود التحقق",
)

EXTORTION_THREATS = (
    "عندي صورك",
    "عندي معلوماتك",
    "راح انشر صورك",
    "راح انشر صور",
    "انشر صورك",
    "انشر صور",
    "راح انشر معلوماتك",
    "انشر معلوماتك",
    "راح افضحك",
    "افضحك",
    "انا املك صورك",
)

EXTORTION_MONEY_DEMANDS = (
    "اذا ما وصل المبلغ",
    "اذا ما تدفع",
    "اذا ما دفعت",
    "اذا ما تحول المبلغ",
    "اذا ما ترسل المبلغ",
    "اذا ما وصلني المبلغ",
    "ارسل الاموال اليوم",
)


def _normalize(text: str) -> str:
    """Normalize Arabic letters, diacritics, punctuation, and whitespace."""
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

    # Treat punctuation as word separators.
    text = "".join(
        " " if unicodedata.category(char).startswith("P") else char
        for char in text
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

    protective_warning = (
        _first_match(
            normalized_text,
            PROTECTIVE_CREDENTIAL_WARNINGS,
        )
        is not None
    )

    explicit_credential_request = (
        _first_match(
            normalized_text,
            EXPLICIT_CREDENTIAL_REQUESTS,
        )
        is not None
    )

    for rule in RULES:
        if (
            rule.name == "credential_request"
            and protective_warning
            and not explicit_credential_request
        ):
            continue

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

    extortion_threat = _first_match(
        normalized_text,
        EXTORTION_THREATS,
    )

    extortion_demand = _first_match(
        normalized_text,
        EXTORTION_MONEY_DEMANDS,
    )

    if extortion_threat and extortion_demand:
        existing_extortion = next(
            (
                signal
                for signal in signals
                if signal["name"] == "extortion_threat"
            ),
            None,
        )

        if existing_extortion is None:
            signals.append({
                "name": "extortion_threat",
                "weight": 4,
                "matched_phrase": (
                    f"{extortion_threat} + {extortion_demand}"
                ),
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
