"""Calculated mining expectations, never pool-confirmed payouts."""
from math import isfinite


def estimate(hashrate_hps, difficulty, btc_usd, power_w=0, electricity_usd_kwh=0.12,
             pool_fee_percent=2, subsidy_btc=3.125):
    args = [hashrate_hps, difficulty, btc_usd, power_w, electricity_usd_kwh, pool_fee_percent, subsidy_btc]
    if any(not isinstance(n, (int,float)) or not isfinite(n) for n in args):
        raise ValueError('finite numerical inputs required')
    if min(hashrate_hps, btc_usd, power_w, electricity_usd_kwh, subsidy_btc) < 0 or difficulty <= 0 or not 0 <= pool_fee_percent <= 100:
        raise ValueError('negative or out of range mining assumptions')
    blocks_per_day = hashrate_hps * 86400 / (difficulty * (2**32))
    btc_per_day = blocks_per_day * subsidy_btc * (1 - pool_fee_percent/100)
    gross_usd_day = btc_per_day * btc_usd
    electric_usd_day = (power_w / 1000) * 24 * electricity_usd_kwh
    return {'btc_per_day_expected': btc_per_day, 'gross_usd_day_expected': gross_usd_day,
            'electric_usd_day_calculated': electric_usd_day,
            'net_usd_day_expected': gross_usd_day - electric_usd_day,
            'inputs': {'hashrate_hps': hashrate_hps, 'difficulty': difficulty, 'btc_usd': btc_usd,
                       'power_w': power_w, 'electricity_usd_kwh': electricity_usd_kwh,
                       'pool_fee_percent': pool_fee_percent, 'subsidy_btc': subsidy_btc},
            'classification': 'calculated expectation from operator assumptions; not earnings',
            'pool_confirmed_paid_btc': None}
