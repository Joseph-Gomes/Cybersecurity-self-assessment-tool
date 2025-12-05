import os
import tempfile
import smtplib

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from dotenv import load_dotenv

from logic import load_questions, calculate_scores, generate_recommendations

# Load variables from .env (if present)
load_dotenv()


# ---------- Helper functions ----------

def get_answers_from_session(questions):
    """Convert radio button values into 'yes'/'no' answers."""
    answers = {}
    for q in questions:
        raw = st.session_state.get(q["id"])
        if raw is None:
            continue

        raw_lower = raw.strip().lower()
        if raw_lower.startswith("y"):
            answers[q["id"]] = "yes"
        elif raw_lower.startswith("n"):
            answers[q["id"]] = "no"

    return answers


def build_radar_chart(pillar_scores: dict):
    """
    Build a radar / spider chart from pillar scores using Matplotlib.
    Returns a Matplotlib Figure.
    """
    if not pillar_scores:
        return None

    pillars = list(pillar_scores.keys())
    scores = [pillar_scores[p] for p in pillars]

    # Shorter label so it doesn't get cut off
    display_labels = []
    for p in pillars:
        if p == "Governance & People":
            display_labels.append("Gov & People")
        elif p == "Detect & Respond":
            display_labels.append("Detect &\nRespond")
        else:
            display_labels.append(p)    
  

    num_vars = len(display_labels)

    # Angles for each axis
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    # Close the loop
    scores_cycle = scores + scores[:1]
    angles_cycle = angles + angles[:1]

    # Slightly larger figure for breathing room
    fig, ax = plt.subplots(subplot_kw=dict(polar=True), figsize=(6, 6))

    # Plot and fill
    ax.plot(angles_cycle, scores_cycle, linewidth=2, color="#1f77b4")
    ax.fill(angles_cycle, scores_cycle, alpha=0.25, color="#1f77b4")

    # Labels and limits
    ax.set_xticks(angles)
    ax.set_xticklabels(display_labels, fontsize=10)
    ax.set_yticks([0, 20, 40, 60, 80, 100])
    ax.set_ylim(0, 100)

    # Make the concentric circles and numbers darker & clearer
    ax.grid(color="#999999", linewidth=0.8)
    ax.tick_params(axis="y", colors="black", labelsize=9)
    ax.tick_params(axis="x", pad=12)  # push titles away from border

    ax.set_facecolor("white")
    fig.patch.set_facecolor("white")

    fig.tight_layout()
    return fig


def build_bar_chart(pillar_scores: dict):
    """
    Build a bar chart of pillar scores using Matplotlib.
    Returns a Matplotlib Figure.
    """
    if not pillar_scores:
        return None

    pillars = list(pillar_scores.keys())
    scores = [pillar_scores[p] for p in pillars]

    # Friendlier labels, break long ones into 2 lines
    display_labels = []
    for p in pillars:
        if p == "Governance & People":
            display_labels.append("Gov &\nPeople")
        elif p == "Detect & Respond":
            display_labels.append("Detect &\nRespond")
        else:
            display_labels.append(p)

    # Similar visual scale to radar chart
    fig, ax = plt.subplots(figsize=(7.5, 5.2))

    ax.bar(display_labels, scores, color="#1f77b4")
    ax.set_ylim(0, 100)
    ax.set_ylabel("Score (0-100)", fontweight="bold", fontstyle="italic")
    ax.set_xlabel("Security area", fontweight="bold", fontstyle="italic",labelpad=20)


    
    ax.set_xticklabels(display_labels, rotation=0, ha="center")

    ax.grid(axis="y", color="#dddddd")
    ax.set_facecolor("white")
    fig.patch.set_facecolor("white")

    fig.tight_layout()
    return fig


def clean_text(text: str) -> str:
    """
    Replace characters that Latin-1 / FPDF can't handle with safe ASCII equivalents.
    """
    if not isinstance(text, str):
        return text

    replacements = {
        "–": "-",   # en dash
        "—": "-",   # em dash
        "’": "'",   # curly apostrophe
        "“": '"',   # left double quote
        "”": '"',   # right double quote
        "•": "-",   # bullet
        "\u00a0": " ",  # non-breaking space
        "🛡": "[Shield]",   # shield emoji fallback
        "🛡️": "[Shield]",
    }

    for bad, good in replacements.items():
        text = text.replace(bad, good)
    return text


def build_pdf_report(summary, pillar_scores, recs, participant, radar_fig=None, bar_fig=None) -> bytes:
    """
    Build a PDF report and return it as bytes.
    Optionally embeds radar/bar charts if Matplotlib figures are provided.
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.set_margins(20, 20, 20)
    pdf.add_page()

    # Title
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, clean_text("Cybersecurity Self-Assessment Report"), ln=True)

    # Participant details
    pdf.ln(4)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 7, clean_text("Assessment details"), ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 6, clean_text(f"Participant name: {participant['name']}"), ln=True)
    pdf.cell(0, 6, clean_text(f"Business name: {participant['business']}"), ln=True)
    pdf.cell(0, 6, clean_text(f"Email address: {participant['email']}"), ln=True)

    # Intro text
    pdf.ln(4)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(
        0,
        6,
        clean_text(
            "This report summarises the results of your cybersecurity self-assessment "
            "and provides simple recommendations to help reduce risk."
        ),
    )

    # Overall results
    pdf.ln(6)
    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 8, clean_text("Overall results"), ln=True)

    pdf.set_font("Arial", "", 11)
    pdf.cell(
        0,
        6,
        clean_text(
            f"Overall security score: {summary['security_score']:.1f} / 100"
        ),
        ln=True,
    )
    pdf.cell(
        0,
        6,
        clean_text(f"Overall risk level: {summary['risk_level']}"),
        ln=True,
    )
    pdf.cell(
        0,
        6,
        clean_text(
            f"Internal risk points: {summary['risk_points']} out of {summary['max_risk']}"
        ),
        ln=True,
    )

    # Explanation of internal risk points
    pdf.ln(4)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 7, clean_text("How to interpret these scores"), ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(
        0,
        6,
        clean_text(
            "The overall security score is a simple 0-100 rating based on your answers. "
            "Internal risk points show how many important cybersecurity controls are currently missing or weak. "
            "The higher this number (relative to the maximum), the more exposed your business is to cyber incidents."
        ),
    )

    # Security by area
    pdf.ln(4)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 7, clean_text("Security by area"), ln=True)

    explanations = {
        "Identify": "This area is about knowing what devices, systems and information your business uses. If you don't know what you have, you can't protect it.",
        "Protect": "This area covers the basic protections that keep attackers out, like strong passwords, multi-factor authentication, firewalls, updates and device security.",
        "Detect & Respond": "This area is about noticing when something suspicious is happening and knowing what to do next.",
        "Recover": "This area focuses on backups and recovery so you can restore important data and keep operating after an incident.",
        "Governance & People": "This area looks at staff training, joiner/leaver processes and how you manage third-party providers.",
    }

    pdf.set_font("Arial", "", 11)
    for pillar, score in pillar_scores.items():
        pdf.ln(2)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(
            0,
            6,
            clean_text(f"{pillar}: {score:.1f} / 100"),
            ln=True,
        )
        pdf.set_font("Arial", "", 11)
        pdf.multi_cell(
            0,
            6,
            clean_text(explanations.get(pillar, "")),
        )

    # Visual overview with charts (if possible)
    pdf.ln(4)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 7, clean_text("Visual overview"), ln=True)

    has_radar = radar_fig is not None
    has_bar = bar_fig is not None

    if has_radar or has_bar:
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                content_width = pdf.w - 2 * pdf.l_margin  # usable width
                img_width = min(150, content_width)       # leave some side margin
                x_center = (pdf.w - img_width) / 2        # centre horizontally

                if has_radar:
                    radar_path = os.path.join(tmpdir, "radar.jpg")
                    radar_fig.savefig(radar_path, bbox_inches="tight", format="jpg")
                    pdf.ln(2)
                    pdf.image(radar_path, x=x_center, w=img_width)
                    plt.close(radar_fig)

                if has_bar:
                    bar_path = os.path.join(tmpdir, "bars.jpg")
                    bar_fig.savefig(bar_path, bbox_inches="tight", format="jpg")
                    pdf.ln(8)
                    pdf.image(bar_path, x=x_center, w=img_width)
                    plt.close(bar_fig)
        except Exception:
            pdf.ln(2)
            pdf.set_font("Arial", "", 11)
            pdf.multi_cell(
                0,
                6,
                clean_text(
                    "Charts could not be embedded in this PDF. You can still see "
                    "the visual overview in the web report."
                ),
            )
    else:
        pdf.ln(2)
        pdf.set_font("Arial", "", 11)
        pdf.multi_cell(
            0,
            6,
            clean_text("No chart data was available for this assessment."),
        )

    # Recommendations
    pdf.ln(4)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 7, clean_text("Recommended actions"), ln=True)
    pdf.set_font("Arial", "", 11)

    if recs:
        for i, rec in enumerate(recs, start=1):
            pdf.multi_cell(0, 6, clean_text(f"{i}. {rec}"))
            pdf.ln(1)
    else:
        pdf.multi_cell(
            0,
            6,
            clean_text(
                "Based on your answers, no urgent recommendations were identified. "
                "Continue to review and maintain your current cybersecurity practices."
            ),
        )

    # Return as bytes for Streamlit download / email attachment
    pdf_bytes = pdf.output(dest="S").encode("latin-1")
    return pdf_bytes


def build_email_html(participant, summary) -> str:
    """Build HTML body for the email."""
    return f"""
<html>
  <body style="font-family: Arial, sans-serif; color: #222;">
    <h2>Cybersecurity Self-Assessment Report</h2>
    <p>Hi {participant['name']},</p>
    <p>
      Thank you for using our cybersecurity self-assessment toolkit for
      <strong>{participant['business']}</strong>.
    </p>
    <p>Your overall results:</p>
    <ul>
      <li><strong>Security score:</strong> {summary['security_score']:.1f} / 100</li>
      <li><strong>Risk level:</strong> {summary['risk_level']}</li>
      <li><strong>Internal risk points:</strong> {summary['risk_points']} out of {summary['max_risk']}</li>
    </ul>
    <p>
      Your full report is attached as a PDF. It includes a breakdown by security area
      and practical recommendations you can share with your team or IT provider.
    </p>
    <p>
      This report is a general guide only and is not legal or financial advice.
      For complex environments or high-risk industries, consider engaging a cybersecurity
      professional for a detailed assessment.
    </p>
    <p>Kind regards,<br/>Cybersecurity Self-Assessment Toolkit</p>
  </body>
</html>
"""


def send_report_email(to_email: str, participant, summary, pdf_bytes: bytes):
    """
    Send the report as an email with attached PDF.
    Returns (success: bool, error_message: str | None).
    """
    smtp_user = os.getenv("CYBER_TOOLKIT_EMAIL")
    smtp_pass = os.getenv("CYBER_TOOLKIT_APP_PASSWORD")

    if not smtp_user or not smtp_pass:
        return False, (
            "Email settings are not configured. Please set CYBER_TOOLKIT_EMAIL "
            "and CYBER_TOOLKIT_APP_PASSWORD in your .env file or environment."
        )

    msg = MIMEMultipart()
    msg["Subject"] = "Your Cybersecurity Self-Assessment Report"
    msg["From"] = smtp_user
    msg["To"] = to_email

    # HTML body
    html_body = build_email_html(participant, summary)
    msg.attach(MIMEText(html_body, "html"))

    # PDF attachment
    part = MIMEApplication(pdf_bytes, _subtype="pdf")
    part.add_header(
        "Content-Disposition",
        "attachment",
        filename="cybersecurity_assessment_report.pdf",
    )
    msg.attach(part)

    try:
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=20) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        return True, None
    except Exception as e:
        return False, str(e)


# ---------- Streamlit app ----------

def main():
    st.set_page_config(
        page_title="Cybersecurity Self-Assessment Tool",
        page_icon="🛡️",
        layout="wide",
    )

    st.title("🛡️Cybersecurity Self-Assessment Tool")
    st.write(
        "This tool helps Australian small and medium businesses perform a quick cybersecurity self-check.\n\n"
        "Please enter your details below and then answer the following yes/no questions about your business "
        "to get a simple risk score and practical recommendations."
    )

    # --- Your details section ---
    st.subheader("Your details")

    col_left, col_right = st.columns(2)
    with col_left:
        participant_name = st.text_input(
            "Your name",
            placeholder="e.g. John Smith",
        )
    with col_right:
        business_name = st.text_input(
            "Business name",
            placeholder="e.g. ABC Cleaning Services",
        )

    participant_email = st.text_input(
        "Email address",
        placeholder="e.g. you@example.com",
    )

    questions = load_questions()
    if not questions:
        st.error("Could not load questions.json. Please check the file.")
        return

    # Step 1: Questions
    st.subheader("Step 1: Answer the assessment questions")

    with st.form("assessment_form"):
        for q in questions:
            st.markdown(f"**{q['id']} — {q['text']}**")
            st.radio(
                label="Your answer:",
                options=["Please select...", "Yes", "No"],
                key=q["id"],
                horizontal=True,
            )
            st.markdown("---")

        submitted = st.form_submit_button("Calculate my cyber risk")

    # If user just submitted the form, validate and compute, then store in session_state
    if submitted:
        # Validate personal details
        if not participant_name or not business_name or not participant_email:
            st.error("Please enter your name, business name and email address before calculating your score.")
            return
        if "@" not in participant_email:
            st.error("Please enter a valid email address (it should contain '@').")
            return

        participant = {
            "name": participant_name.strip(),
            "business": business_name.strip(),
            "email": participant_email.strip(),
        }

        # Collect and validate answers
        answers = get_answers_from_session(questions)
        missing = [q["id"] for q in questions if q["id"] not in answers]
        if missing:
            st.error("Please answer all questions before calculating your score.")
            return

        # Shared logic for scores and recommendations
        summary, pillar_scores = calculate_scores(questions, answers)
        recs = generate_recommendations(questions, answers)

        # Store everything in session_state so user can download/email without redoing assessment
        st.session_state["assessment_data"] = {
            "participant": participant,
            "summary": summary,
            "pillar_scores": pillar_scores,
            "recs": recs,
        }

    # If we don't have assessment data yet, stop here
    if "assessment_data" not in st.session_state:
        st.info("Please complete Step 1 and click 'Calculate my cyber risk' to see your results.")
        return

    # Retrieve stored results
    data = st.session_state["assessment_data"]
    participant = data["participant"]
    summary = data["summary"]
    pillar_scores = data["pillar_scores"]
    recs = data["recs"]

    # Step 2: Results
    st.subheader("Step 2: Your results")

    st.metric("Overall security score", f"{summary['security_score']:.1f} / 100")
    st.write(f"**Overall risk level:** {summary['risk_level']}")
    st.caption(
        f"Internal risk points: {summary['risk_points']} out of {summary['max_risk']}"
    )

    # Explanation box for scores
    with st.expander("What do these scores mean?"):
        st.markdown(
            """
**Overall security score**  
This is a simple 0–100 rating based on your answers. Higher scores mean stronger cybersecurity controls.

**Internal risk points**  
Each question has a weight based on how important it is. When you answer "No" to a question, its weight is added to your risk points.  
The first number shows how much risk you currently have; the second number shows the maximum possible risk in this assessment.  
A higher value (compared to the maximum) means your business is missing more key protections and is more exposed to cyber incidents.
"""
        )

    st.write("### Security by area (higher is better)")

    explanations = {
        "Identify": "This area is about knowing what devices, systems and information your business uses. If you don't know what you have, you can't protect it.",
        "Protect": "This area covers the basic protections that keep attackers out, like strong passwords, multi-factor authentication, firewalls, updates and device security.",
        "Detect & Respond": "This area is about noticing when something suspicious is happening and knowing what to do next.",
        "Recover": "This area focuses on backups and recovery so you can restore important data and keep operating after an incident.",
        "Governance & People": "This area looks at staff training, joiner/leaver processes and how you manage third-party providers.",
    }

    for pillar, score in pillar_scores.items():
        st.markdown(
            f"**{pillar}: {score:.1f} / 100**  \n"
            f"{explanations[pillar]}\n"
        )

    # Step 3: Visual overview
    st.write("### Visual overview")

    space, col1, col2, space2 = st.columns([1, 3, 3, 1])

    radar_fig = build_radar_chart(pillar_scores)
    bar_fig = build_bar_chart(pillar_scores)

    with col1:
        if radar_fig is not None:
            st.pyplot(radar_fig)

    with col2:
        if bar_fig is not None:
            # add vertical space so the bar chart sits slightly lower than the radar chart
            st.markdown("<div style='margin-top: 70px;'></div>", unsafe_allow_html=True)  
            st.pyplot(bar_fig)

    # Step 3: Recommendations
    st.subheader("Step 3: Recommended actions")

    if recs:
        st.write("Based on your answers, we suggest focusing on the following areas first:")
        for i, rec in enumerate(recs, start=1):
            st.write(f"{i}. {rec}")
    else:
        if summary["risk_level"] == "LOW":
            st.success(
                "Great job! Based on your answers, no urgent recommendations were identified."
            )
        else:
            st.warning(
                "Your score indicates some cybersecurity risk, but no specific recommendations were generated. "
                "Please review your answers or consult a cybersecurity advisor."
            )

    # Step 4: Get report (download + email)
    st.subheader("Step 4: Get your report")

    pdf_bytes = build_pdf_report(summary, pillar_scores, recs, participant, radar_fig, bar_fig)

    st.download_button(
        label="Download full report (PDF)",
        data=pdf_bytes,
        file_name="cybersecurity_assessment_report.pdf",
        mime="application/pdf",
    )

    st.markdown("")

    if st.button("Email this report to me"):
        success, error_message = send_report_email(
            participant["email"], participant, summary, pdf_bytes
        )
        if success:
            st.success("Report emailed successfully.")
        else:
            st.error(f"Could not send email: {error_message}")

    st.markdown("---")
    if st.button("Start a new assessment"):
        # Completely clear all stored state and rerun the app
        st.session_state.clear()
        try:
            st.rerun()
        except AttributeError:
            # For older Streamlit versions
            st.experimental_rerun()


if __name__ == "__main__":
    main()
