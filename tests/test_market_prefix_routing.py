"""Market-prefix routing for 6-digit A-share codes.

Regression cover for issue #85: the Beijing Stock Exchange started issuing
920xxx codes for new listings in October 2024.  A bare ``startswith("9")``
routed them to Shanghai, where the Tencent quote endpoint answers with an
empty payload instead of an error — so the failure was silent.
"""

import unittest

import pytest

from tradingagents.dataflows.a_stock import _eastmoney_secid, _get_prefix


@pytest.mark.unit
class MarketPrefixRoutingTests(unittest.TestCase):

    def test_shanghai_main_board_and_star(self):
        self.assertEqual(_get_prefix("600519"), "sh")
        self.assertEqual(_get_prefix("601398"), "sh")
        self.assertEqual(_get_prefix("688017"), "sh")

    def test_shenzhen_main_board_and_chinext(self):
        self.assertEqual(_get_prefix("000001"), "sz")
        self.assertEqual(_get_prefix("002463"), "sz")
        self.assertEqual(_get_prefix("300476"), "sz")

    def test_beijing_legacy_8_prefix(self):
        self.assertEqual(_get_prefix("830799"), "bj")
        self.assertEqual(_get_prefix("871981"), "bj")

    def test_beijing_920_series_routes_to_bj_not_sh(self):
        """920xxx is the Beijing Stock Exchange's new-listing range, not Shanghai."""
        for code in ("920002", "920008", "920098", "920111"):
            self.assertEqual(_get_prefix(code), "bj", f"{code} must route to bj")

    def test_shanghai_b_shares_still_route_to_sh(self):
        """900xxx (Shanghai B shares) is the only leading-9 range that really is Shanghai."""
        self.assertEqual(_get_prefix("900901"), "sh")
        self.assertEqual(_get_prefix("900932"), "sh")

    def test_eastmoney_secid_routes_shanghai_etf_to_market_1(self):
        """5xxxxx is a Shanghai ETF range; Eastmoney market 0 returns data=null."""
        self.assertEqual(_eastmoney_secid("510300"), "1.510300")
        self.assertEqual(_eastmoney_secid("513180"), "1.513180")
        self.assertEqual(_eastmoney_secid("588000"), "1.588000")
        self.assertEqual(_eastmoney_secid("159530"), "0.159530")


if __name__ == "__main__":
    unittest.main()
