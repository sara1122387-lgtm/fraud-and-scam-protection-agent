import streamlit as st
from pathlib import Path

from src.rules import analyze_message


# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="مساعد الحماية من الاحتيال المالي",
    page_icon="🛡️",
    layout="centered",
)


# --------------------------------------------------
# Load external stylesheet
# --------------------------------------------------

CSS_PATH = Path(__file__).parent / "styles.css"

if CSS_PATH.is_file():
    css_content = CSS_PATH.read_text(encoding="utf-8")
    st.markdown(
        f"<style>{css_content}</style>",
        unsafe_allow_html=True,
    )


# --------------------------------------------------
# Arabic text helper
# --------------------------------------------------

def rtl_text(text):
    """Render Arabic text in an explicitly right-to-left container."""
    st.markdown(
        f'<div class="arabic-text" dir="rtl">{text}</div>',
        unsafe_allow_html=True,
    )


# --------------------------------------------------
# Session state
# --------------------------------------------------

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

if "analyzed_message" not in st.session_state:
    st.session_state.analyzed_message = ""

if "simulation_decision" not in st.session_state:
    st.session_state.simulation_decision = None


# --------------------------------------------------
# Main interface
# --------------------------------------------------

st.title("مساعد الحماية من الاحتيال المالي")

rtl_text(
    "<strong>تنبيه:</strong> نموذج أولي تجريبي. لا تدخل كلمات "
    "المرور أو رموز التحقق أو بيانات البطاقة أو المحفظة "
    "أو أي معلومات شخصية حساسة."
)

rtl_text(
    "أدخل نص الرسالة الأصلية وحده دون إضافة شرحك الشخصي. "
    "احذف أي معلومات حساسة قبل الفحص."
)


# --------------------------------------------------
# Message analysis form
# --------------------------------------------------

with st.form("message_analysis_form"):
    message_text = st.text_area(
        "نص الرسالة المشبوهة",
        height=180,
        placeholder="الصق الرسالة هنا...",
    )

    submitted = st.form_submit_button(
        "فحص الرسالة",
        type="primary",
        use_container_width=True,
    )

if submitted:
    st.session_state.simulation_decision = None

    if not message_text.strip():
        st.session_state.analysis_result = None
        st.session_state.analyzed_message = ""
        st.error("أدخل نص الرسالة أولًا.")
    else:
        try:
            st.session_state.analysis_result = analyze_message(
                message_text
            )
            st.session_state.analyzed_message = message_text

        except (TypeError, ValueError):
            st.session_state.analysis_result = None
            st.session_state.analyzed_message = ""
            st.error("تعذر فحص الرسالة. تحقق من النص وحاول مجددًا.")


# --------------------------------------------------
# User-facing signal labels
# --------------------------------------------------

SIGNAL_LABELS = {
    "credential_request": "طلب رمز تحقق أو كلمة مرور",
    "financial_data_request": "طلب بيانات مالية أو بيانات بطاقة",
    "advance_payment_request": "طلب دفعة مقدمة",
    "currency_exchange_request": "عرض مالي يحتاج إلى تحقق",
    "unverified_benefit": "ادعاء بوجود جائزة أو منحة أو منفعة",
    "impersonation": "إشارة إلى جهة دعم أو إدارة محفظة",
    "relative_impersonation": "ادعاء صلة قرابة أو معرفة شخصية",
    "transfer_request": "طلب تحويل أموال",
    "verification_avoidance": "محاولة منع التحقق من هوية المرسل",
    "urgency_pressure": "ضغط لاتخاذ إجراء بسرعة",
    "mild_urgency": "استعجال في الطلب",
    "safe_account_transfer": "طلب نقل الأموال إلى حساب يُدّعى أنه آمن",
    "suspicious_link": "طلب فتح رابط",
    "vague_account_claim": "ادعاء وجود مشكلة في الحساب",
    "extortion_threat": "تهديد أو ابتزاز مرتبط بطلب مالي",
}


# --------------------------------------------------
# Analysis results
# --------------------------------------------------

result = st.session_state.analysis_result

if result is not None:
    st.divider()
    st.subheader("نتيجة الفحص")

    signal_names = {
        signal["name"] for signal in result["signals"]
    }

    is_high_risk = result["response"] == "warn"
    is_uncertain = result["response"] == "clarify"

    if is_high_risk:
        rtl_text(
            "<strong>توقّف قبل اتخاذ أي إجراء مالي.</strong> "
            "اكتُشفت مؤشرات تستدعي الحذر والتحقق."
        )
    elif is_uncertain:
        rtl_text(
            "النتيجة غير حاسمة. تحقّق من هوية المرسل "
            "وسياق الطلب قبل اتخاذ أي إجراء."
        )
    else:
        rtl_text(
            "لم تكتشف القواعد الحالية مؤشرات واضحة. "
            "هذا لا يعني أن الرسالة آمنة."
        )

    if result["signals"]:
        st.subheader("ما الذي يستدعي الانتباه؟")

        shown_labels = []
        for signal in result["signals"]:
            label = SIGNAL_LABELS.get(
                signal["name"],
                "مؤشر يحتاج إلى التحقق",
            )
            if label not in shown_labels:
                shown_labels.append(label)

        for label in shown_labels:
            rtl_text(f"• {label}")
    else:
        rtl_text(
            "لم تتطابق الرسالة مع مؤشرات الخطر الموجودة حاليًا."
        )

    # Context-specific guidance
    st.subheader("خطوة التحقق التالية")

    if "extortion_threat" in signal_names:
        rtl_text("<strong>عند الاشتباه بالابتزاز الإلكتروني</strong>")

        rtl_text(
            "لا تستجب للتهديد بالدفع على عجل، ولا ترسل معلومات "
            "إضافية. احتفظ بالرسائل والمحادثات ذات الصلة، "
            "واطلب المساعدة عبر القنوات الحكومية المختصة "
            "بمكافحة الابتزاز الإلكتروني."
        )

        rtl_text(
            "عند وجود خطر فوري على السلامة، اتصل بالطوارئ "
            "على الرقم 911 في العراق."
        )

        rtl_text(
            "يمكنك أيضًا الاستعانة بمنصة أمين الحكومية "
            "المختصة بمكافحة الابتزاز الإلكتروني."
        )

    elif signal_names & {
        "credential_request",
        "financial_data_request",
        "safe_account_transfer",
        "suspicious_link",
    }:
        rtl_text(
            "لا تشارك رمز التحقق أو كلمة المرور أو بيانات البطاقة، "
            "ولا تفتح رابطًا مشبوهًا. تحقّق من الجهة عبر تطبيقها "
            "أو وسيلة اتصال رسمية مستقلة، لا عبر بيانات الرسالة."
        )

    elif (
        "relative_impersonation" in signal_names
        or "verification_avoidance" in signal_names
    ):
        rtl_text(
            "تواصل مع الشخص عبر رقم تعرفه مسبقًا، وتأكد من الطلب "
            "مباشرة قبل إرسال المال. لا تعتمد على الاسم أو صورة "
            "الحساب وحدهما."
        )

    elif signal_names & {
        "urgency_pressure",
        "mild_urgency",
        "transfer_request",
    }:
        rtl_text(
            "لا تدع الاستعجال يختصر التحقق. اسأل عن سبب الطلب، "
            "وتأكد من هوية المستلم والمبلغ عبر قناة مستقلة "
            "قبل اتخاذ القرار."
        )

    elif is_uncertain:
        rtl_text(
            "تحقّق من مصدر الرسالة، واطلب توضيحًا، ولا تشارك "
            "معلومات حساسة قبل التأكد."
        )

    else:
        rtl_text(
            "إذا كان هناك طلب مالي، فتحقّق من هوية المرسل "
            "والغرض من الطلب عبر وسيلة موثوقة مستقلة. "
            "عدم ظهور مؤشرات لا يثبت سلامة الرسالة."
        )

    if result["possible_mixed_input"]:
        rtl_text(
            "قد يحتوي النص على شرح إضافي بجانب الرسالة الأصلية. "
            "لنتيجة أدق، افحص نص الرسالة وحده بعد حذف المعلومات الحساسة."
        )

    rtl_text(
        "هذا نموذج أولي يعتمد على قواعد محددة، وقد لا يفهم كل "
        "السياقات أو اللهجات. الإشارات المكتشفة ليست إثباتًا "
        "للاحتيال، وغيابها ليس إثباتًا للأمان."
    )

    # Decision simulation
    st.divider()
    st.subheader("قرارك في المحاكاة")

    rtl_text(
        "اختر قرارك داخل النموذج فقط. لا يوجد اتصال بمحفظة "
        "ولا يُنفّذ أي تحويل مالي حقيقي."
    )

    if is_high_risk:
        rtl_text(
            "قبل محاكاة المتابعة، راجع التحذير وتحقق من الطلب "
            "عبر وسيلة مستقلة."
        )

    cancel_col, proceed_col = st.columns(2)

    with cancel_col:
        if st.button("إلغاء العملية", use_container_width=True):
            st.session_state.simulation_decision = "cancel"

    with proceed_col:
        proceed_label = (
            "محاكاة المتابعة رغم التحذير"
            if is_high_risk
            else "محاكاة المتابعة"
        )

        if st.button(
            proceed_label,
            use_container_width=True,
        ):
            st.session_state.simulation_decision = "proceed"

    if st.session_state.simulation_decision == "cancel":
        rtl_text(
            "تم تسجيل إلغاء المحاكاة. لم يحدث أي تحويل مالي."
        )

    elif st.session_state.simulation_decision == "proceed":
        rtl_text(
            "تم تسجيل اختيار المتابعة في المحاكاة فقط. "
            "لم يحدث أي تحويل مالي، ولم يتم الاتصال بأي محفظة."
        )
