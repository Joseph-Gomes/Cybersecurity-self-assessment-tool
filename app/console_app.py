from typing import Dict, List

from logic import load_questions, calculate_scores, generate_recommendations


def ask_yes_no(prompt: str) -> str:
    """
    Ask the user a yes/no question in the console.
    Returns 'yes' or 'no'.
    """
    while True:
        answer = input(f"{prompt} (yes/no): ").strip().lower()
        if answer in ("yes", "y"):
            return "yes"
        elif answer in ("no", "n"):
            return "no"
        else:
            print("Please answer with 'yes' or 'no' (or y/n).")


def ask_questions(questions: List[Dict]) -> Dict[str, str]:
    """
    Ask all questions one by one and return a dict:
    { question_id: 'yes'/'no' }
    """
    print("\nPlease answer the following questions about your business.\n")
    answers: Dict[str, str] = {}

    for q in questions:
        print(f"\n[{q['id']}] {q['text']}")
        user_answer = ask_yes_no("Your answer")
        answers[q["id"]] = user_answer

    return answers


def print_summary(summary: Dict, pillar_scores: Dict[str, float], recs: List[str]) -> None:
    """Print a neat summary of the results."""
    print("\n=== Assessment Summary ===\n")

    print(f"Overall security score: {summary['security_score']:.1f} / 100")
    print(f"Overall risk level: {summary['risk_level']}")
    print(
        f"(Internal risk points: {summary['risk_points']} out of {summary['max_risk']})\n"
    )

    print("Security by area (higher is better):")
    for pillar, score in pillar_scores.items():
        print(f" - {pillar}: {score:.1f} / 100")
    print()

    if recs:
        print("Priority recommendations for your business:\n")
        for i, rec in enumerate(recs, start=1):
            print(f"{i}. {rec}")
    else:
        print("Great job! Based on your answers, no urgent recommendations were identified.")


def main():
    print("=== Cybersecurity Self-Assessment (Console Version) ===\n")
    print("This tool will ask you a series of yes/no questions about your business.\n")
    print("Please answer honestly to get useful recommendations.\n")

    questions = load_questions()

    if not questions:
        print("No questions loaded. Please check questions.json.")
        return

    # Ask questions and collect answers
    answers = ask_questions(questions)

    # Calculate scores using shared logic
    summary, pillar_scores = calculate_scores(questions, answers)

    # Generate recommendations using shared logic
    recs = generate_recommendations(questions, answers)

    # Print final summary
    print_summary(summary, pillar_scores, recs)

    print("\nThank you for completing the assessment.\n")


if __name__ == "__main__":
    main()
