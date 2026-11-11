
import streamlit as st
import pandas as pd
from decimal import Decimal
from datetime import date

from common.models import ExpenseLine
from module_a_validation.claim_processor import process_claim


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="FinLogic | Expense Intelligence",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==================================================
# CUSTOM CSS
# ==================================================

st.markdown("""
<style>

/* ==========================================
   FINLOGIC - COMPLETE SOFT PASTEL THEME
   ========================================== */

/* App background and default text */
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    background: #F6F2FA !important;
    color: #393247 !important;
}

.main .block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

[data-testid="stHeader"] {
    background: #F6F2FA !important;
}

/* Main page typography */
.stApp h1, .stApp h2, .stApp h3, .stApp h4,
.stApp h5, .stApp h6,
.stApp p, .stApp li,
.stMarkdown, .stMarkdown p, .stMarkdown span,
[data-testid="stCaptionContainer"] {
    color: #393247 !important;
}

.stApp h1, .stApp h2, .stApp h3 {
    font-weight: 700 !important;
}

/* Sidebar - soft lavender */
section[data-testid="stSidebar"] {
    background: #E9E0F2 !important;
    border-right: 1px solid #DCCFE9 !important;
}

section[data-testid="stSidebar"] * {
    color: #493D5C !important;
    -webkit-text-fill-color: #493D5C !important;
}

section[data-testid="stSidebar"] [role="radiogroup"] label {
    background: transparent;
    border-radius: 9px;
}

section[data-testid="stSidebar"] [role="radiogroup"] label:hover {
    background: #DCD0EA !important;
}

/* Pastel page headers */
.finlogic-header {
    background: linear-gradient(120deg, #E8DFF4 0%, #DDEDEB 55%, #F9E7E2 100%);
    padding: 30px;
    border: 1px solid #DED3E9;
    border-radius: 18px;
    margin-bottom: 25px;
    box-shadow: 0 4px 16px rgba(75, 57, 100, 0.06);
}

.finlogic-header,
.finlogic-header h1,
.finlogic-header h2,
.finlogic-header h3,
.finlogic-header p,
.finlogic-header span,
.finlogic-header div {
    color: #403650 !important;
    -webkit-text-fill-color: #403650 !important;
}

.finlogic-header h1 {
    margin-bottom: 8px;
}

/* Metric cards */
div[data-testid="stMetric"] {
    background: #FFFFFF !important;
    border: 1px solid #E6DDED !important;
    padding: 19px !important;
    border-radius: 15px !important;
    box-shadow: 0 3px 12px rgba(75, 57, 100, 0.05);
}

div[data-testid="stMetric"] label,
[data-testid="stMetricLabel"],
[data-testid="stMetricLabel"] * {
    color: #746A80 !important;
    -webkit-text-fill-color: #746A80 !important;
}

div[data-testid="stMetricValue"],
div[data-testid="stMetricValue"] * {
    color: #403650 !important;
    -webkit-text-fill-color: #403650 !important;
    font-weight: 700 !important;
}

[data-testid="stMetricDelta"] {
    color: #397E70 !important;
}

/* Text, number, date and multiline inputs */
.stTextInput input,
.stNumberInput input,
.stDateInput input,
.stTextArea textarea {
    color: #393247 !important;
    background: #FFFFFF !important;
    -webkit-text-fill-color: #393247 !important;
    border: 1px solid #D9CDE6 !important;
    border-radius: 10px !important;
}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: #91879D !important;
    -webkit-text-fill-color: #91879D !important;
}

/* Select boxes and dropdowns */
.stSelectbox div[data-baseweb="select"],
[data-baseweb="select"] > div {
    background: #FFFFFF !important;
    border-color: #D9CDE6 !important;
}

.stSelectbox div[data-baseweb="select"] *,
[data-baseweb="select"] * {
    color: #393247 !important;
    -webkit-text-fill-color: #393247 !important;
}

[data-baseweb="popover"],
[data-baseweb="menu"] {
    background: #FFFFFF !important;
}

[data-baseweb="menu"] * {
    color: #393247 !important;
}

/* Buttons */
.stButton button,
.stDownloadButton button {
    background: #A58BC7 !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    border: 1px solid #A58BC7 !important;
    border-radius: 10px !important;
    padding: 10px 20px !important;
    font-weight: 600 !important;
}

.stButton button *,
.stDownloadButton button * {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}

.stButton button:hover,
.stDownloadButton button:hover {
    background: #8E73B5 !important;
    border-color: #8E73B5 !important;
}

/* Data tables and editable tables */
div[data-testid="stDataFrame"],
div[data-testid="stDataEditor"],
div[data-testid="stTable"] {
    background: #FFFFFF !important;
    color: #393247 !important;
    border: 1px solid #E5DCEC !important;
    border-radius: 12px !important;
}

/* Chart panels - white background for clear chart labels */
[data-testid="stVegaLiteChart"],
[data-testid="stArrowVegaLiteChart"],
[data-testid="stPlotlyChart"] {
    background: #FFFFFF !important;
    border: 1px solid #E5DCEC !important;
    border-radius: 14px !important;
    padding: 12px !important;
}

/* Expanders */
[data-testid="stExpander"] {
    background: #FFFFFF !important;
    border: 1px solid #E5DCEC !important;
    border-radius: 12px !important;
}

[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary * {
    color: #493D5C !important;
    -webkit-text-fill-color: #493D5C !important;
}

/* Tabs */
.stTabs [data-baseweb="tab"],
.stTabs [data-baseweb="tab"] * {
    color: #625672 !important;
}

.stTabs [aria-selected="true"],
.stTabs [aria-selected="true"] * {
    color: #8066AD !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background: #FFFFFF !important;
    border: 1px dashed #BBA9D8 !important;
    border-radius: 14px !important;
    padding: 14px !important;
}

[data-testid="stFileUploader"] *,
[data-testid="stFileUploader"] section {
    color: #493D5C !important;
    -webkit-text-fill-color: #493D5C !important;
}

/* Alerts and status messages - pastel boxes instead of dark boxes */
div[data-testid="stAlert"] {
    background-color: #E8F3EF !important;
    border: 1px solid #C9E3D9 !important;
    border-left: 5px solid #8DBEAD !important;
    border-radius: 12px !important;
    color: #393247 !important;
}

/* Keep alert message text clearly readable */
div[data-testid="stAlert"] *,
div[data-testid="stAlert"] p,
div[data-testid="stAlert"] span {
    color: #393247 !important;
    -webkit-text-fill-color: #393247 !important;
}

/* Info messages use a soft powder-blue pastel */
div[data-testid="stAlert"][kind="info"] {
    background-color: #EAF1FB !important;
    border-color: #D2DFF2 !important;
    border-left-color: #91AEDA !important;
}

/* Warning messages use a soft peach pastel */
div[data-testid="stAlert"][kind="warning"] {
    background-color: #FCEDE7 !important;
    border-color: #F2D8CC !important;
    border-left-color: #E6A58E !important;
}

/* Checkbox and radio labels */
.stCheckbox label,
.stRadio label,
.stCheckbox label *,
.stRadio label * {
    color: #493D5C !important;
}

/* Dividers */
hr {
    border-color: #DED3EA !important;
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: #F6F2FA;
}

::-webkit-scrollbar-thumb {
    background: #C5B5DC;
    border-radius: 10px;
}

/* FORCE ALL STREAMLIT MESSAGE BOXES TO PASTEL */

div[data-testid="stAlert"],
div[data-testid="stAlert"] > div,
div[data-testid="stAlert"] [role="alert"],
div[data-testid="stAlert"] [data-testid="stMarkdownContainer"] {
    background: #EAF1FB !important;
    background-color: #EAF1FB !important;
    color: #393247 !important;
    border-radius: 12px !important;
}

/* Make every message readable */
div[data-testid="stAlert"] *,
div[data-testid="stAlert"] p,
div[data-testid="stAlert"] span {
    color: #393247 !important;
    -webkit-text-fill-color: #393247 !important;
}

/* Remove dark inner backgrounds */
div[data-testid="stAlert"] div {
    background-color: transparent !important;
}

/* Soft pastel border */
div[data-testid="stAlert"] {
    border: 1px solid #D2DFF2 !important;
    border-left: 5px solid #91AEDA !important;
}

</style>
""", unsafe_allow_html=True)


# ==================================================
# SESSION STATE
# ==================================================

if "results" not in st.session_state:
    st.session_state.results = []


# ==================================================
# HELPER FUNCTIONS
# ==================================================

def to_bool(value):

    if isinstance(value, bool):
        return value

    return str(value).strip().lower() in [
        "true", "1", "yes", "y"
    ]


def money(value):

    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


def analyze_expenses(data):

    results = []

    for _, row in data.iterrows():

        try:

            expense = ExpenseLine(
                line_id=str(row["line_id"]),
                category=str(row["category"]).strip().lower(),
                expense_date=str(row["expense_date"]),
                amount=Decimal(str(row["amount"])),
                currency=str(row["currency"]).strip().upper(),
                receipt=to_bool(row["receipt"])
            )

            result = process_claim(expense)

            claimed = money(row["amount"])
            eligible = money(result.get("eligible_amount", 0))

            results.append({
                "Expense ID": str(row["line_id"]),
                "Category": str(row["category"]),
                "Date": str(row["expense_date"]),
                "Claimed Amount": claimed,
                "Eligible Amount": eligible,
                "Rejected Amount": max(0, claimed - eligible),
                "Currency": str(row["currency"]).upper(),
                "Status": str(result.get("status", "UNKNOWN")),
                "Findings": "; ".join(
                    str(error)
                    for error in result.get("errors", [])
                )
            })

        except Exception as error:

            results.append({
                "Expense ID": str(row.get("line_id", "Unknown")),
                "Category": str(row.get("category", "")),
                "Date": str(row.get("expense_date", "")),
                "Claimed Amount": money(row.get("amount", 0)),
                "Eligible Amount": 0,
                "Rejected Amount": money(row.get("amount", 0)),
                "Currency": str(row.get("currency", "INR")),
                "Status": "ERROR",
                "Findings": str(error)
            })

    return results


# ==================================================
# SIDEBAR NAVIGATION
# ==================================================

st.sidebar.markdown("# 💼 FinLogic")
st.sidebar.caption("Expense Intelligence Platform")

page = st.sidebar.radio(
    "NAVIGATION",
    [
        "Dashboard",
        "Submit Expenses",
        "Analysis Results",
        "About"
    ]
)

st.sidebar.markdown("---")
st.sidebar.caption("Corporate Expense Reimbursement Engine")
st.sidebar.caption("Team T041 | PS-029")


# ==================================================
# DASHBOARD
# ==================================================

if page == "Dashboard":

    st.markdown("""
    <div class="finlogic-header">
        <h1>Welcome to FinLogic</h1>
        <p>Intelligent corporate expense validation and reimbursement platform.</p>
    </div>
    """, unsafe_allow_html=True)

    results = st.session_state.results

    total_claimed = sum(
        item["Claimed Amount"] for item in results
    )

    total_eligible = sum(
        item["Eligible Amount"] for item in results
    )

    total_rejected = sum(
        item["Rejected Amount"] for item in results
    )

    total_expenses = len(results)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Expenses", total_expenses)
    col2.metric("Total Claimed", f"₹{total_claimed:,.2f}")
    col3.metric("Eligible Amount", f"₹{total_eligible:,.2f}")
    col4.metric("Rejected Amount", f"₹{total_rejected:,.2f}")

    st.markdown("---")

    st.subheader("Expense Overview")

    if results:

        chart_data = pd.DataFrame({
            "Amount Type": ["Eligible", "Rejected"],
            "Amount": [total_eligible, total_rejected]
        })

        st.bar_chart(
            chart_data.set_index("Amount Type")
        )

        st.subheader("Recent Expense Activity")

        st.dataframe(
            pd.DataFrame(results),
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No expenses analyzed yet. Go to Submit Expenses to begin."
        )


# ==================================================
# SUBMIT EXPENSES
# ==================================================

elif page == "Submit Expenses":

    st.markdown("""
    <div class="finlogic-header">
        <h1>Submit Expenses</h1>
        <p>Enter expense details or upload a CSV file for validation.</p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Employee Information")

    col1, col2 = st.columns(2)

    with col1:
        employee_id = st.text_input("Employee ID", value="E100")

    with col2:
        employee_name = st.text_input(
            "Employee Name",
            value="Demo Employee"
        )

    st.markdown("---")

    st.subheader("Expense Details")

    sample_data = pd.DataFrame([
        {
            "line_id": "EXP001",
            "category": "meal",
            "expense_date": str(date.today()),
            "amount": 500.0,
            "currency": "INR",
            "receipt": True,
            "vendor": "Restaurant"
        },
        {
            "line_id": "EXP002",
            "category": "hotel",
            "expense_date": str(date.today()),
            "amount": 4500.0,
            "currency": "INR",
            "receipt": True,
            "vendor": "Hotel"
        },
        {
            "line_id": "EXP003",
            "category": "travel",
            "expense_date": str(date.today()),
            "amount": 2500.0,
            "currency": "INR",
            "receipt": True,
            "vendor": "Travel Agency"
        }
    ])

    uploaded_csv = st.file_uploader(
        "Upload expense CSV",
        type=["csv"]
    )

    if uploaded_csv is not None:

        try:
            expense_data = pd.read_csv(uploaded_csv)
            st.success("CSV uploaded successfully!")

        except Exception as error:
            st.error(f"Could not read CSV: {error}")
            expense_data = sample_data.copy()

    else:
        expense_data = sample_data.copy()

    required_columns = [
        "line_id",
        "category",
        "expense_date",
        "amount",
        "currency",
        "receipt"
    ]

    missing_columns = [
        column for column in required_columns
        if column not in expense_data.columns
    ]

    if missing_columns:

        st.error(
            "CSV is missing required columns: "
            + ", ".join(missing_columns)
        )

    else:

        edited_data = st.data_editor(
            expense_data,
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True,
            column_config={
                "line_id": st.column_config.TextColumn(
                    "Expense ID"
                ),
                "category": st.column_config.SelectboxColumn(
                    "Category",
                    options=[
                        "meal",
                        "hotel",
                        "travel",
                        "transport",
                        "other"
                    ]
                ),
                "amount": st.column_config.NumberColumn(
                    "Amount",
                    min_value=0.0,
                    format="%.2f"
                ),
                "receipt": st.column_config.CheckboxColumn(
                    "Receipt Available"
                )
            }
        )

        st.markdown("---")

        st.subheader("Attach Supporting Documents")

        receipt_files = st.file_uploader(
            "Upload receipts or invoices",
            type=["pdf", "png", "jpg", "jpeg"],
            accept_multiple_files=True
        )

        if receipt_files:
            st.success(
                f"{len(receipt_files)} document(s) attached. "
                "Automatic OCR extraction is not enabled."
            )

        st.markdown("---")

        if st.button(
            "🔍 ANALYZE EXPENSES",
            use_container_width=True
        ):

            if not employee_id.strip() or not employee_name.strip():

                st.error("Please enter employee information.")

            elif edited_data.empty:

                st.error("Please add at least one expense.")

            else:

                with st.spinner(
                    "Analyzing expenses against company policies..."
                ):

                    st.session_state.results = analyze_expenses(
                        edited_data
                    )

                    st.session_state.employee_id = employee_id
                    st.session_state.employee_name = employee_name

                st.success("Expense analysis completed!")

                st.info(
                    "Open Analysis Results in the sidebar to view "
                    "your validation report."
                )


# ==================================================
# ANALYSIS RESULTS
# ==================================================

elif page == "Analysis Results":

    st.markdown("""
    <div class="finlogic-header">
        <h1>Analysis Results</h1>
        <p>Expense validation report generated by FinLogic.</p>
    </div>
    """, unsafe_allow_html=True)

    results = st.session_state.results

    if not results:

        st.warning(
            "No analysis results available. Submit expenses first."
        )

    else:

        results_df = pd.DataFrame(results)

        total_claimed = results_df["Claimed Amount"].sum()
        total_eligible = results_df["Eligible Amount"].sum()
        total_rejected = results_df["Rejected Amount"].sum()

        col1, col2, col3 = st.columns(3)

        col1.metric("Claimed", f"₹{total_claimed:,.2f}")
        col2.metric("Eligible", f"₹{total_eligible:,.2f}")
        col3.metric("Rejected", f"₹{total_rejected:,.2f}")

        st.markdown("---")

        st.subheader("Detailed Validation Report")

        st.dataframe(
            results_df,
            use_container_width=True,
            hide_index=True
        )

        st.subheader("Individual Expense Findings")

        for item in results:

            with st.expander(
                f"{item['Expense ID']} — {item['Category'].title()}"
            ):

                col1, col2 = st.columns(2)

                col1.write(
                    f"**Claimed:** ₹{item['Claimed Amount']:,.2f}"
                )

                col2.write(
                    f"**Eligible:** ₹{item['Eligible Amount']:,.2f}"
                )

                st.write(f"**Status:** {item['Status']}")

                st.write(
                    f"**Findings:** "
                    f"{item['Findings'] or 'No validation errors reported.'}"
                )

        st.markdown("---")

        csv_data = results_df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            label="⬇ Download Analysis Report",
            data=csv_data,
            file_name="finlogic_analysis_report.csv",
            mime="text/csv"
        )


# ==================================================
# ABOUT
# ==================================================

elif page == "About":

    st.markdown("""
    <div class="finlogic-header">
        <h1>About FinLogic</h1>
        <p>Corporate Expense Reimbursement Policy Engine</p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Project Overview")

    st.write("""
    FinLogic is an intelligent corporate expense reimbursement
    policy engine designed to validate employee expense claims,
    identify policy violations and support transparent reimbursement.
    """)

    st.subheader("Core Modules")

    st.markdown("""
    **Module A — Expense Validation**

    - Expense policy validation
    - Receipt verification
    - Hotel limit validation
    - Meal limit validation
    - Travel validation
    - Per diem validation
    - Duplicate expense detection
    - Currency conversion

    **Module B — Approval and Settlement**

    - Approval chain generation
    - Manager and finance approvals
    - Claim rejection and return
    - Settlement calculation
    - Audit trail generation
    """)

    st.markdown("---")

    st.write("**Team:** T041")
    st.write("**Problem Statement:** PS-029")
    st.write("**Technology:** Python, Streamlit, Pandas")
