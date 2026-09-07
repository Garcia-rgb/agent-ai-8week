import pytest

from support_agent.services.tools import ToolError, query_order, safe_calculate


def test_safe_calculator() -> None:
    assert safe_calculate("(12 + 8) / 4") == 5


@pytest.mark.parametrize("expression", ["__import__('os')", "2 ** 100", "1 / 0"])
def test_calculator_rejects_unsafe_or_invalid_input(expression: str) -> None:
    with pytest.raises(ToolError):
        safe_calculate(expression)


def test_query_order() -> None:
    assert query_order("a1001").status == "已发货"
    with pytest.raises(ToolError, match="未找到"):
        query_order("A9999")
