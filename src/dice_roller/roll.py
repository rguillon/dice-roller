# Copyright (c) 2025 Renaud. Licensed under the MIT License.

"""Module for manipulating dices."""

from __future__ import annotations

import logging
import operator
import random
import re
from re import Pattern
from typing import TYPE_CHECKING

import matplotlib.pyplot as plt

if TYPE_CHECKING:
    from collections.abc import Callable

    from matplotlib.figure import Figure


class Roll:
    """Class representing a dice or a combination of dices."""

    def __init__(
        self,
        desc: str | None = None,
        values: dict[float, float] | None = None,
        *,
        value: float | None = None,
    ) -> None:
        """Initialize a Roll object.

        Args:
            desc (str | None): A string description of the roll expression (e.g., "2d6+3").
            values (dict[float, float] | None): A dictionary mapping outcomes to their probabilities.
            value (float | None): A fixed numeric value representing a certain outcome.

        """
        self.__distribution: dict[float, float]
        if values is not None:
            self.__distribution = values
        elif value is not None:
            self.__distribution = {value: 1.0}
        elif desc is not None:
            self.__distribution = Roll.parse_dice_expression(expression=desc).distribution
        else:
            self.__distribution = {}

    @staticmethod
    def parse_dice_expression(expression: str) -> Roll:
        """Parse a dice expression string and returns a Roll object representing the distribution.

        Args:
            expression (str): The dice expression string (e.g., "1d6-3").

        Returns:
            Roll: A Roll object representing the parsed expression.

        """
        term_pattern: Pattern[str] = re.compile(r"([+-]?\d*[dD]?\d*)")
        expression = expression.replace(" ", "")
        terms: list[str] = term_pattern.findall(expression)

        dice: Roll = Roll(value=0)

        for term in terms:
            if not term:
                continue
            if "d" in term.lower():
                sign = -1 if term.startswith("-") else 1
                clean_term: str = term.lstrip("+-")
                num, sides = clean_term.lower().split(sep="d")
                nb: int = int(num) if num else 1
                new_dice: Roll = Roll()
                for side in range(1, int(sides) + 1):
                    new_dice.add_event(event=float(side), probability=1.0)

                if sign == -1:
                    for _ in range(nb):
                        dice -= new_dice
                else:
                    for _ in range(nb):
                        dice += new_dice

            else:
                dice += Roll(value=float(term))
        return dice

    def add_event(self, event: float, probability: float) -> None:
        """Add an event to the dice distribution.

        Args:
            event (float): The outcome to add.
            probability (float): The probability of the outcome.

        """
        if event in self.__distribution:
            self.__distribution[event] += probability
        else:
            self.__distribution[event] = probability

    @property
    def distribution(self) -> dict[float, float]:
        """Return the probability distribution of the dice.

        Returns:
            dict[float, float]: A dictionary mapping outcomes to their probabilities.

        """
        return self.__distribution

    def _combine(self, other: Roll, op: Callable[[float, float], float]) -> Roll:
        """Combine two Roll objects using a specified binary operation.

        Args:
            other (Roll): The other Roll object to combine with.
            op (Callable[[float, float], float]): A binary operation function (e.g., addition, subtraction).

        Returns:
            Roll: A new Roll object representing the combined distribution.

        """
        result = Roll()
        for event1, prob1 in self.distribution.items():
            for event2, prob2 in other.distribution.items():
                result.add_event(float(op(event1, event2)), prob1 * prob2)
        return result

    def __add__(self, other: Roll) -> Roll:
        """Add two Roll objects together, combining their distributions.

        Args:
            other (Roll): The other Roll object to add.

        Returns:
            Roll: A new Roll object representing the combined distribution.

        """
        return self._combine(other, operator.add)

    def __sub__(self, other: Roll) -> Roll:
        """Subtract one Roll object from another, combining their distributions.

        Args:
            other (Roll): The other Roll object to subsctract.

        Returns:
            Roll: A new Roll object representing the combined distribution.

        """
        return self._combine(other, operator.sub)

    def __lt__(self, other: Roll) -> Roll:
        """Compare two Roll objects using the less-than operator, combining their distributions.

        Args:
            other (Roll): The other Roll object to compare.

        Returns:
            Roll: A new Roll object representing the combined distribution.

        """
        return self._combine(other, operator.lt)

    def __le__(self, other: Roll) -> Roll:
        """Compare two Roll objects using the less-than-or-equal-to operator, combining their distributions.

        Args:
            other (Roll): The other Roll object to compare.

        Returns:
            Roll: A new Roll object representing the combined distribution.

        """
        return self._combine(other, operator.le)

    def __gt__(self, other: Roll) -> Roll:
        """Compare two Roll objects using the greater-than operator, combining their distributions.

        Args:
            other (Roll): The other Roll object to compare.

        Returns:
            Roll: A new Roll object representing the combined distribution.

        """
        return self._combine(other, operator.gt)

    def __ge__(self, other: Roll) -> Roll:
        """Compare two Roll objects using the greater-than-or-equal-to operator, combining their distributions.

        Args:
            other (Roll): The other Roll object to compare.

        Returns:
            Roll: A new Roll object representing the combined distribution.

        """
        return self._combine(other, operator.ge)

    def __eq__(self, other: object) -> bool:
        """Override the equality operator to compare two Roll objects based on their distributions.

        Args:
            other (Roll): The other Roll object to compare.

        Returns:
            Roll: A new Roll object representing the combined distribution.

        """
        if not isinstance(other, Roll):
            return False
        return self.distribution == other.distribution

    def __hash__(self) -> int:
        """Override the hash function to allow Roll objects to be used in sets and as dictionary keys.

        Returns:
            int: The hash value of the Roll object.

        """
        return hash(frozenset(self.distribution.items()))

    def __ne__(self, other: object) -> bool:
        """Override the inequality operator to compare two Roll objects based on their distributions.

        Args:
            other (Roll): The other Roll object to compare.

        Returns:
            Roll: A new Roll object representing the combined distribution.

        """
        if not isinstance(other, Roll):
            return True
        return self.distribution != other.distribution

    @property
    def space_size(self) -> float:
        """Calculate the total number of possible outcomes (the size of the sample space) for the dice roll.

        Returns:
            float: The total number of possible outcomes.

        """
        return sum(self.__distribution.values())

    @property
    def expected_value(self) -> float:
        """Calculate the expected value of the dice roll based on its probability distribution.

        Returns:
            float: The expected value of the dice roll.

        """
        return sum(value * prob for value, prob in self.__distribution.items()) / self.space_size

    def normalized(self, value: float = 1.0) -> Roll:
        """Return a new Roll instance with its probability distribution normalized.

        Returns:
            Roll: A new Roll object with a normalized probability distribution.

        """
        total = self.space_size
        return Roll(values={outcome: prob * value / total for outcome, prob in self.__distribution.items()})

    def roll(self) -> float:
        """Simulate a roll of the dice based on its probability distribution.

        Returns:
            float: The result of the dice roll.
         calculated 2

        """
        values: list[float] = list[float](self.distribution.keys())
        weights: list[float] = list[float](self.distribution.values())
        return float(sum(random.choices(population=values, weights=weights, k=1)))

    def to_figure(
        self, title: str = "Roll Distribution", xlabel: str = "Outcome", ylabel: str = "Probability (%)"
    ) -> Figure:
        """Return a Matplotlib Figure object representing the dice distribution as a bar graph.

        Args:
            title (str): The title of the graph.
            xlabel (str): The label for the x-axis.
            ylabel (str): The label for the y-axis.

        Returns:
            Figure: A Matplotlib Figure object representing the bar graph.

        """
        normalized_dice: Roll = self.normalized(value=100.0)
        outcomes: list[float] = list[float](normalized_dice.distribution.keys())
        probabilities: list[float] = [normalized_dice.distribution[o] for o in outcomes]

        plt.set_loglevel(level="warning")
        logging.getLogger(name="PIL.PngImagePlugin").setLevel(level=logging.CRITICAL + 1)
        figure: Figure = plt.figure(figsize=(8, 4))
        plt.bar(x=outcomes, height=probabilities, color="skyblue", edgecolor="black")
        plt.xlabel(xlabel=xlabel)
        plt.ylabel(ylabel)
        plt.title(label=title)
        plt.tight_layout()
        return figure
