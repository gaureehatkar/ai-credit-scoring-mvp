"""
Evidence Quality Engine
-----------------------
Computes a confidence score E ∈ [0, 1] that measures how much data we have
to trust the PD estimate — NOT creditworthiness itself.

Formula (designed assumption, not an industry standard):
    E = 0.5 * (history_months / 12) + 0.25 * aa_completeness + 0.25 * uli_completeness

Threshold τ_E = 0.5
    E >= 0.5 → SUFFICIENT   (can auto-approve in D3/D4)
    E <  0.5 → INSUFFICIENT (routes to REVIEW in D3/D4)
"""

from dataclasses import dataclass

# Evidence sufficiency threshold (τ_E)
TAU_E = 0.5

# Weight configuration (kept here as the single source of truth)
WEIGHT_HISTORY = 0.50
WEIGHT_AA      = 0.25
WEIGHT_ULI     = 0.25


@dataclass
class EvidenceResult:
    score: float               # E ∈ [0, 1]
    status: str                # "SUFFICIENT" | "INSUFFICIENT"
    history_months: int        # visible history length (1–12)
    aa_completeness: float     # Account Aggregator completeness ∈ [0, 1]
    uli_completeness: float    # ULI completeness ∈ [0, 1]
    threshold: float           # τ_E used for the decision

    def to_dict(self) -> dict:
        return {
            "score": round(self.score, 4),
            "status": self.status,
            "history_months": self.history_months,
            "aa_completeness": round(self.aa_completeness, 4),
            "uli_completeness": round(self.uli_completeness, 4),
            "threshold": self.threshold,
        }


def compute_evidence(
    history_months: int,
    aa_completeness: float,
    uli_completeness: float,
    tau_e: float = TAU_E,
) -> EvidenceResult:
    """
    Compute evidence quality score for an applicant.

    Parameters
    ----------
    history_months   : int   — months of visible financial history (1–12)
    aa_completeness  : float — Account Aggregator data completeness (0–1)
    uli_completeness : float — ULI data completeness (0–1)
    tau_e            : float — sufficiency threshold (default 0.5)

    Returns
    -------
    EvidenceResult
    """
    # Clamp inputs to valid ranges
    h  = max(0, min(int(history_months), 12))
    aa = max(0.0, min(float(aa_completeness), 1.0))
    ul = max(0.0, min(float(uli_completeness), 1.0))

    score = WEIGHT_HISTORY * (h / 12.0) + WEIGHT_AA * aa + WEIGHT_ULI * ul
    score = round(max(0.0, min(score, 1.0)), 6)

    status = "SUFFICIENT" if score >= tau_e else "INSUFFICIENT"

    return EvidenceResult(
        score=score,
        status=status,
        history_months=h,
        aa_completeness=aa,
        uli_completeness=ul,
        threshold=tau_e,
    )


def derive_evidence_inputs(alternative_data: dict, applicant_type: str) -> dict:
    """
    Derive evidence inputs from the existing alternative_data fields
    collected in the credit application form.

    Returns a dict with keys: history_months, aa_completeness, uli_completeness
    """
    # --- History months ---
    # Proxy: employment stability years → months of verifiable income history
    stability_years = float(alternative_data.get("employment_stability_years") or 1.0)
    # Cap at 12 months (our observation window)
    history_months = min(int(stability_years * 12), 12)
    # Minimum 1 month if the applicant submitted anything
    history_months = max(history_months, 1)

    # --- AA completeness ---
    # Proxy: for underbanked applicants, UPI frequency + savings indicate
    # how complete their Account Aggregator data trail would be.
    if applicant_type == "underbanked":
        upi_freq = float(alternative_data.get("upi_transaction_frequency") or 0)
        savings  = float(alternative_data.get("savings_account_balance") or 0)
        # Normalise: 30 UPI tx/month ≈ complete; savings > 0 adds confidence
        aa_completeness = min((upi_freq / 30.0) * 0.7 + (1.0 if savings > 0 else 0.0) * 0.3, 1.0)
    else:
        # Unbanked: proxy from remittance frequency
        remittance = float(alternative_data.get("remittance_frequency") or 0)
        aa_completeness = min(remittance / 10.0, 1.0)

    # --- ULI completeness ---
    # Proxy: loan repayment history score (0–10) → normalise to [0, 1]
    repayment_score  = float(alternative_data.get("loan_repayment_history_score") or 5.0)
    utility_score    = float(alternative_data.get("utility_bill_payment_score") or 5.0)
    uli_completeness = min((repayment_score + utility_score) / 20.0, 1.0)

    return {
        "history_months": history_months,
        "aa_completeness": round(aa_completeness, 4),
        "uli_completeness": round(uli_completeness, 4),
    }
