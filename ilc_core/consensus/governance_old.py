import math

class Governance:
    def __init__(self):
        self.base_fee_target = 0.01 # The 'Genesis' price (e.g. 1 ECU)
        self.genesis_potential = 0.1 # Baseline (Carbon Tier)
        self.current_median_potential = 0.1 # Dynamic

    def update_network_metrics(self, agent_potentials: list[float]):
        """
        Called at Epoch start with the results of Intelligence Tests.
        """
        if not agent_potentials: return
        
        # Calculate Median
        sorted_pots = sorted(agent_potentials)
        mid = len(sorted_pots) // 2
        self.current_median_potential = sorted_pots[mid]
        
        print(f"[Governance] Network Median Potential: {self.current_median_potential:.2f}")

    def get_dynamic_fee(self) -> float:
        """
        Scales fee based on Hardware Inflation.
        If network is 10x faster, fee is 10x higher to curb spam.
        """
        ratio = self.current_median_potential / self.genesis_potential
        # Clamp ratio to avoid wild swings (e.g. 0.5x to 100.0x)
        ratio = max(0.5, min(ratio, 100.0))
        
        fee = self.base_fee_target * ratio
        return round(fee, 6)
