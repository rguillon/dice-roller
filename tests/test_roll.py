# Copyright (c) 2025 Renaud. Licensed under the MIT License.

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from dice_roller import Roll

if TYPE_CHECKING:
    from matplotlib.figure import Figure


@pytest.mark.parametrize(
    ("expression", "expected_distribution"),
    [
        ("1", {1: 1}),
        ("-4", {-4: 1}),
        ("d4", {1: 1, 2: 1, 3: 1, 4: 1}),
        ("d4+2", {3: 1, 4: 1, 5: 1, 6: 1}),
        ("1d6", {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1}),
        ("1d10", {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 9: 1, 10: 1}),
        ("2d4", {2: 1, 3: 2, 4: 3, 5: 4, 6: 3, 7: 2, 8: 1}),
        ("1d4 - 1d4", {0: 4.0, -1: 3.0, -2: 2.0, -3: 1.0, 1: 3.0, 2: 2.0, 3: 1.0}),
    ],
)
def test_dice_constructor(expression: str, expected_distribution: dict[float, float]) -> None:
    assert Roll(expression).distribution == expected_distribution


@pytest.mark.parametrize(
    ("expression", "expected_space_size"),
    [
        ("1", 1),
        ("-4", 1),
        ("d4", 4),
        ("d4+2", 4),
        ("1d6", 6),
        ("5d10", 100000),
        ("2d4", 16),
        ("1d6 - 1d4", 24),
    ],
)
def test_dice_space_size(expression: str, expected_space_size: float) -> None:
    assert Roll(expression).space_size == expected_space_size


@pytest.mark.parametrize(
    ("expression", "expected_value"),
    [
        ("6", 6),
        ("-2", -2),
        ("d4", 2.5),
        ("d4+2", 4.5),
        ("2d6", 7),
        ("5d10", 27.5),
        ("2d4", 5),
        ("1d6 - 1d4", 1.0),
        ("200D6", 700.0),
    ],
)
def test_dice_expected_value(expression: str, expected_value: float) -> None:
    assert Roll(expression).expected_value == expected_value


@pytest.mark.parametrize(
    ("expression", "expected_distribution"),
    [
        ("1", {1: 1}),
        ("-4", {-4: 1}),
        ("d4", {1: 1 / 4, 2: 1 / 4, 3: 1 / 4, 4: 1 / 4}),
        ("d4+2", {3: 1 / 4, 4: 1 / 4, 5: 1 / 4, 6: 1 / 4}),
        ("2d4", {2: 1 / 16, 3: 2 / 16, 4: 3 / 16, 5: 4 / 16, 6: 3 / 16, 7: 2 / 16, 8: 1 / 16}),
    ],
)
def test_dice_normalize(expression: str, expected_distribution: dict[float, float]) -> None:
    dice = Roll(expression)
    normalized = dice.normalized()
    assert normalized.distribution == expected_distribution
    assert normalized.space_size == 1.0
    assert normalized.expected_value == dice.expected_value


@pytest.mark.parametrize(
    ("left", "right", "expected_distribution"),
    [
        ("1", "1", {0: 1}),
        ("D6", "1", {0: 6}),
        ("D6", "2", {0: 5, 1: 1}),
        ("D6", "6", {0: 1, 1: 5}),
        ("D6", "7", {1: 6}),
        ("D6", "D6", {0: 21, 1: 15}),
        ("1d10", "1d3", {0: 27, 1: 3}),
    ],
)
def test_lt_operator(left: str, right: str, expected_distribution: dict[float, float]) -> None:
    assert (Roll(left) < Roll(right)).distribution == expected_distribution


@pytest.mark.parametrize(
    ("left", "right", "expected_distribution"),
    [
        ("1", "1", {1: 1}),
        ("D6", "1", {0: 5, 1: 1}),
        ("D6", "2", {0: 4, 1: 2}),
        ("D6", "6", {1: 6}),
        ("D6", "7", {1: 6}),
        ("D6", "D6", {0: 15, 1: 21}),
        ("1d10", "1d3", {0: 24, 1: 6}),
    ],
)
def test_le_operator(left: str, right: str, expected_distribution: dict[float, float]) -> None:
    assert (Roll(left) <= Roll(right)).distribution == expected_distribution


@pytest.mark.parametrize(
    ("left", "right", "expected_distribution"),
    [
        ("1", "1", {0: 1}),
        ("D6", "1", {0: 1, 1: 5}),
        ("D6", "2", {0: 2, 1: 4}),
        ("D6", "6", {0: 6}),
        ("D6", "7", {0: 6}),
        ("D6", "D6", {0: 21, 1: 15}),
        ("1d10", "1d3", {0: 6, 1: 24}),
    ],
)
def test_gt_operator(left: str, right: str, expected_distribution: dict[float, float]) -> None:
    assert (Roll(left) > Roll(right)).distribution == expected_distribution


@pytest.mark.parametrize(
    ("left", "right", "expected_distribution"),
    [
        ("1", "1", {1: 1}),
        ("D6", "1", {1: 6}),
        ("D6", "2", {0: 1, 1: 5}),
        ("D6", "6", {0: 5, 1: 1}),
        ("D6", "7", {0: 6}),
        ("D6", "D6", {0: 15, 1: 21}),
        ("1d10", "1d3", {0: 3, 1: 27}),
    ],
)
def test_ge_operator(left: str, right: str, expected_distribution: dict[float, float]) -> None:
    assert (Roll(left) >= Roll(right)).distribution == expected_distribution


@pytest.mark.parametrize(
    ("left", "right", "expected_equal"),
    [
        (Roll("1"), Roll("1"), True),
        (Roll("D6"), Roll("D6"), True),
        (Roll("2D6"), Roll("1D6+1D6"), True),
        (Roll("2D6+1"), Roll("1D6+1+1D6"), True),
        (Roll("D4"), Roll("D5"), False),
        (Roll("D4"), "test", False),
        (Roll("D4"), 4, False),
        (Roll("D4"), False, False),
    ],
)
def test_eq_ne_operator(left: Roll, right: Roll | object, expected_equal: bool) -> None:
    assert (left == right) == expected_equal
    assert (left != right) == (not expected_equal)


def test_roll_returns_possible_value() -> None:
    # Test for a standard die
    dice = Roll("1d6")
    results: set[float] = set()
    for _ in range(100):
        val = dice.roll()
        assert 1 <= val <= 6
        results.add(val)
    # Should have seen all possible values after enough rolls
    assert results == {1, 2, 3, 4, 5, 6}


def test_roll_distribution_matches_distribution_keys() -> None:
    # For a custom distribution
    dist = {2.0: 0.2, 4.0: 0.3, 7.0: 0.5}
    dice = Roll(values=dist)
    for _ in range(20):
        assert dice.roll() in dist


def test_roll_with_negative_and_zero() -> None:
    dice = Roll("-2")
    for _ in range(5):
        assert dice.roll() == -2

    dice = Roll("0")
    for _ in range(5):
        assert dice.roll() == 0


def test_roll_with_complex_expression() -> None:
    dice = Roll("1d4+2")
    results: set[float] = set()
    for _ in range(100):
        val = dice.roll()
        assert 3 <= val <= 6
        results.add(val)
    assert results == {3, 4, 5, 6}


def test_hash() -> None:
    # dumb test for coverage
    dice1: Roll = Roll(desc="1d4+2")
    dice2: Roll = Roll(desc="1d4") + Roll(desc="2")
    assert hash(dice1) == hash(dice2)


@pytest.mark.mpl_image_compare
def test_to_image() -> Figure:
    return Roll(desc="6d6").to_figure(title="6d6 Distribution", xlabel="Sum of 6d6", ylabel="Probability (%)")
