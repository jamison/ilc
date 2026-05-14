import sys
import os
from decimal import Decimal
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ilc_core.economics.epoch_ledger import SimpleEpochLedger


def test_epoch_ledger_basic_aggregation():
    ledger = SimpleEpochLedger()

    # Epoch 0: 2 tasks, 1.0 ECU total, 2.0 ILC rewards
    ledger.record_task(epoch=0, ecu_spent=Decimal("0.4"), reward=Decimal("0.8"))
    ledger.record_task(epoch=0, ecu_spent=Decimal("0.6"), reward=Decimal("1.2"))

    # Epoch 1: 1 task, 0.5 ECU, 0.25 ILC
    ledger.record_task(epoch=1, ecu_spent=Decimal("0.5"), reward=Decimal("0.25"))

    # Per-epoch stats
    stats0 = ledger.get_epoch_stats(0)
    assert stats0.tasks == 2
    assert stats0.ecu_spent == Decimal("1.0")
    assert stats0.rewards_paid == Decimal("2.0")

    stats1 = ledger.get_epoch_stats(1)
    assert stats1.tasks == 1
    assert stats1.ecu_spent == Decimal("0.5")
    assert stats1.rewards_paid == Decimal("0.25")

    # Aggregate stats
    agg = ledger.total_aggregate()
    assert agg.tasks == 3
    assert agg.ecu_spent == Decimal("1.5")
    assert agg.rewards_paid == Decimal("2.25")

    # Clearing price (aggregate)
    price = ledger.clearing_price()
    # 2.25 ILC / 1.5 ECU = 1.5
    assert price == Decimal("1.5")
    assert isinstance(price, Decimal)
