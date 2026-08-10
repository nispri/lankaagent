"""Unit tests for the custom tour pricing engine."""

from app.integrations.tour_pricing import quote_custom_tour, quote_table


def test_14day_2pax_matches_catalog_rate():
    """The 14-day quote for 2 pax must match the published $2,490/pp rate."""
    q = quote_custom_tour(14, 2)
    assert q["price_per_person_usd"] == 2490, q["price_per_person_usd"]
    assert q["total_usd"] == 2490 * 2


def test_7day_cheaper_than_14day():
    q7 = quote_custom_tour(7, 2)
    q14 = quote_custom_tour(14, 2)
    assert q7["price_per_person_usd"] < q14["price_per_person_usd"]
    assert q7["nights"] < q14["nights"]


def test_more_pax_lower_per_person():
    q2 = quote_custom_tour(7, 2)
    q4 = quote_custom_tour(7, 4)
    assert q4["price_per_person_usd"] < q2["price_per_person_usd"]
    assert q4["rooms"] == 2


def test_clamps_extreme_durations():
    assert quote_custom_tour(1, 2)["days"] == 2
    assert quote_custom_tour(50, 2)["days"] == 21


def test_quote_table_contains_expected_durations():
    table = quote_table()
    for days in ("5 days", "7 days", "10 days", "14 days"):
        assert days in table
