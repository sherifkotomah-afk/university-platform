"""
Grading engine.

Ghana's universities are not uniform here: UG/UCC/UEW commonly use a
GPA/letter-grade system, while KNUST uses Cumulative Weighted Average (CWA)
— a straight weighted average of raw scores, not grade points. Since this
platform is white-labeled across institutions, the grading system is a
per-institution setting (institution_settings.grading_system), and this
module branches on it rather than assuming one scheme.

The letter-grade/grade-point scale below is a common standard shape used
across Ghanaian universities. Real deployments should let an admin adjust
the cutoffs per institution if theirs differs — that's a config table, not
something to hardcode blindly in production.
"""
from typing import List, Tuple, Optional

# (min_score_inclusive, letter, grade_point)
GRADE_SCALE = [
    (80, "A", 4.0),
    (75, "B+", 3.5),
    (70, "B", 3.0),
    (65, "C+", 2.5),
    (60, "C", 2.0),
    (55, "D+", 1.5),
    (50, "D", 1.0),
    (0, "F", 0.0),
]


def score_to_letter_and_point(total_score: float) -> Tuple[str, float]:
    for min_score, letter, point in GRADE_SCALE:
        if total_score >= min_score:
            return letter, point
    return "F", 0.0


def compute_cumulative(
    grading_system: str,
    course_results: List[dict],  # each: {"score": float, "grade_point": float, "credit_hours": int}
) -> Tuple[Optional[float], int]:
    """
    Returns (cumulative_value, total_credit_hours).
    - GPA system: weighted average of grade points by credit hours.
    - CWA system: weighted average of raw scores by credit hours.
    Only counts results that have a total_score set (i.e. finalized).
    """
    graded = [r for r in course_results if r.get("score") is not None]
    if not graded:
        return None, 0

    total_credits = sum(r["credit_hours"] for r in graded)
    if total_credits == 0:
        return None, 0

    if grading_system == "CWA":
        weighted_sum = sum(r["score"] * r["credit_hours"] for r in graded)
    else:  # GPA
        weighted_sum = sum(r["grade_point"] * r["credit_hours"] for r in graded)

    return round(weighted_sum / total_credits, 2), total_credits
