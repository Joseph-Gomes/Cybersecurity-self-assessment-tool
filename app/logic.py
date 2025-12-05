import json
from pathlib import Path
from typing import Dict, List, Tuple


# Path to questions.json (relative to this file)
DATA_FILE = Path(__file__).parent.parent / "data" / "questions.json"


def load_questions() -> List[Dict]:
    """Load questions from the JSON file and return them as a list of dicts."""
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            questions = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: Could not find questions file at: {DATA_FILE}")
        return []
    except json.JSONDecodeError as e:
        print(f"ERROR: questions.json is not valid JSON: {e}")
        return []

    return questions


def calculate_scores(
    questions: List[Dict], answers: Dict[str, str]
) -> Tuple[Dict, Dict[str, float]]:
    """
    Calculate:
      - overall risk & security score
      - per-pillar security scores

    Returns:
      summary: dict with risk_points, max_risk, risk_percentage, security_score, risk_level
      pillar_scores: dict { pillar_name: security_score_0_to_100 }
    """
    max_risk = sum(q["weight"] for q in questions)
    risk_points = 0

    pillar_max: Dict[str, int] = {}
    pillar_risk: Dict[str, int] = {}

    for q in questions:
        pillar = q["pillar"]
        weight = q["weight"]
        good_answer = q.get("good_answer", "yes")
        user_answer = answers.get(q["id"])

        pillar_max[pillar] = pillar_max.get(pillar, 0) + weight

        if user_answer is not None and user_answer != good_answer:
            risk_points += weight
            pillar_risk[pillar] = pillar_risk.get(pillar, 0) + weight
        else:
            pillar_risk.setdefault(pillar, 0)

    if max_risk == 0:
        risk_percentage = 0.0
    else:
        risk_percentage = (risk_points / max_risk) * 100

    security_score = 100 - risk_percentage

    if security_score >= 80:
        risk_level = "LOW"
    elif security_score >= 50:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"

    summary = {
        "risk_points": risk_points,
        "max_risk": max_risk,
        "risk_percentage": risk_percentage,
        "security_score": security_score,
        "risk_level": risk_level,
    }

    pillar_scores: Dict[str, float] = {}
    for pillar, max_w in pillar_max.items():
        risk_w = pillar_risk.get(pillar, 0)
        if max_w == 0:
            pillar_scores[pillar] = 100.0
        else:
            pillar_risk_pct = (risk_w / max_w) * 100
            pillar_security = 100 - pillar_risk_pct
            pillar_scores[pillar] = pillar_security

    return summary, pillar_scores


def generate_recommendations(questions: List[Dict], answers: Dict[str, str]) -> List[str]:
    """
    Generate simple, non-technical recommendations based on 'bad' answers.
    One recommendation per question answered in an unsafe way.
    """
    recs: List[str] = []

    # NOTE: IDs are Q1, Q2, ..., Q20 to match questions.json
    recommendation_map: Dict[str, str] = {
        "Q1": "Create and keep an up-to-date list of all company devices (laptops, phones, servers, tablets) and review it regularly.",
        "Q2": "Define an approved software list and uninstall or block software that is not needed or not approved.",
        "Q3": "Identify where sensitive data is stored, label it (e.g. confidential), and limit where it is copied or shared.",
        "Q4": "Enable multi-factor authentication (MFA) for all remote access, email accounts and key business systems.",
        "Q5": "Change all default passwords on devices, routers and systems, and require strong unique passwords.",
        "Q6": "Configure computers and mobile devices to automatically lock after a short period of inactivity (5–10 minutes).",
        "Q7": "Limit admin accounts to a small number of trusted users and use standard accounts for day-to-day work.",
        "Q8": "Ensure device firewalls are turned on and use a router or gateway with a firewall for your business network.",
        "Q9": "Turn on automatic updates for operating systems and key software, and apply critical patches promptly.",
        "Q10": "Install reputable antivirus or endpoint protection on all devices and make sure it is kept up to date.",
        "Q11": "Enable full-disk encryption on laptops and mobile devices (e.g. BitLocker, FileVault) to protect lost or stolen devices.",
        "Q12": "Create a separate guest Wi-Fi network that only provides internet access and cannot reach your business systems.",
        "Q13": "Write a simple incident response plan describing who to contact and what steps to follow if an incident occurs, and review it yearly.",
        "Q14": "Maintain an up-to-date list of emergency contacts (IT support, cloud providers, bank, legal/cyber support) and keep it easily accessible.",
        "Q15": "Set up automatic weekly (or more frequent) backups of important business data to a secure, offsite or cloud location.",
        "Q16": "Regularly test restoring files from your backups and document the steps so you know recovery will work in an emergency.",
        "Q17": "Provide basic cybersecurity awareness training for all staff at induction and at least once per year, and record attendance.",
        "Q18": "Create an offboarding checklist to immediately remove system, email and remote access when someone leaves the business.",
        "Q19": "Assess third-party vendors for basic security (e.g. encryption, access controls, incident handling) before sharing sensitive data.",
        "Q20": "Document how you will detect, assess and respond to privacy or data breaches in line with Australian privacy obligations.",
    }

    for q in questions:
        qid = q["id"]
        good_answer = q.get("good_answer", "yes")
        user_answer = answers.get(qid)

        if user_answer is not None and user_answer != good_answer:
            rec_text = recommendation_map.get(qid)
            if rec_text and rec_text not in recs:
                recs.append(rec_text)

    return recs
