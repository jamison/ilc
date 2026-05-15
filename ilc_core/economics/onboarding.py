import logging
from decimal import Decimal, InvalidOperation

from ilc_core.identity.log_redaction_runtime import redact_agent_id_for_log

logger = logging.getLogger(__name__)


class OnboardingVault:
    def __init__(self):
        self.vault_balance = Decimal("1000")  # Seeded by Genesis/Fees
        self.credits_issued = {}     # agent_id -> amount_owed

    def request_starter_credit(self, agent_id: str) -> Decimal:
        # Strict limit per agent
        STARTER_AMOUNT = Decimal("0.02")
        
        if agent_id in self.credits_issued:
            return Decimal("0")
        
        if self.vault_balance >= STARTER_AMOUNT:
            self.vault_balance -= STARTER_AMOUNT
            self.credits_issued[agent_id] = STARTER_AMOUNT
            logger.info(
                "[Vault] Issued starter credit %s to %s",
                STARTER_AMOUNT,
                redact_agent_id_for_log(agent_id),
            )
            return STARTER_AMOUNT
        return Decimal("0")

    def process_repayment(self, agent_id: str, earnings: Decimal) -> tuple[Decimal, Decimal]:
        """
        Intercepts earnings to repay debt. 
        Returns (repayment_amount, net_earnings_for_agent)
        """
        earnings_amount = _onboarding_decimal(earnings, "onboarding_earnings_invalid")
        debt = self.credits_issued.get(agent_id, Decimal("0"))
        if debt <= Decimal("0"):
            return Decimal("0"), earnings_amount
            
        # 50% Garnishment Rule
        repayment = min(debt, earnings_amount * Decimal("0.5"))
        self.credits_issued[agent_id] -= repayment
        self.vault_balance += repayment
        
        if self.credits_issued[agent_id] == Decimal("0"):
            logger.info(
                "[Vault] Agent %s has fully repaid their debt!",
                redact_agent_id_for_log(agent_id),
            )
            
        return repayment, earnings_amount - repayment


def _onboarding_decimal(value: object, token: str) -> Decimal:
    if isinstance(value, bool):
        raise ValueError(token)
    if not isinstance(value, (Decimal, int, float, str)):
        raise ValueError(token)
    try:
        amount = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(token) from exc
    if not amount.is_finite():
        raise ValueError(f"{token}_non_finite")
    return amount
