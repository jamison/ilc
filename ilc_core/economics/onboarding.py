import logging

logger = logging.getLogger(__name__)


class OnboardingVault:
    def __init__(self):
        self.vault_balance = 1000.0  # Seeded by Genesis/Fees
        self.credits_issued = {}     # agent_id -> amount_owed

    def request_starter_credit(self, agent_id: str) -> float:
        # Strict limit per agent
        STARTER_AMOUNT = 0.02
        
        if agent_id in self.credits_issued:
            return 0.0 
        
        if self.vault_balance >= STARTER_AMOUNT:
            self.vault_balance -= STARTER_AMOUNT
            self.credits_issued[agent_id] = STARTER_AMOUNT
            logger.info("[Vault] Issued starter credit %s to %s", STARTER_AMOUNT, agent_id)
            return STARTER_AMOUNT
        return 0.0

    def process_repayment(self, agent_id: str, earnings: float) -> tuple[float, float]:
        """
        Intercepts earnings to repay debt. 
        Returns (repayment_amount, net_earnings_for_agent)
        """
        debt = self.credits_issued.get(agent_id, 0.0)
        if debt <= 0:
            return 0.0, earnings
            
        # 50% Garnishment Rule
        repayment = min(debt, earnings * 0.5)
        self.credits_issued[agent_id] -= repayment
        self.vault_balance += repayment
        
        if self.credits_issued[agent_id] == 0:
            logger.info("[Vault] Agent %s has fully repaid their debt!", agent_id)
            
        return repayment, earnings - repayment
