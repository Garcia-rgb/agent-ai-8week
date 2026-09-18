"""Day 7 验收脚本：逐条检查 safe_calculate 的行为。

用法（在仓库根目录执行）：

    python exercises/day07/check_safe_calc.py

必测项（能算的算对、该拒的拒掉）全绿才算通过；标 [加分] 的失败不影响退出码。
改完 `safe_calc.py` 随时重跑，直到全绿。
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from safe_calc import MAX_LENGTH, safe_calculate  # noqa: E402  练习文件就在同目录

from support_agent.services.tools import ToolError  # noqa: E402

LONG_EXPRESSION = (
    "(1 + 2) * (3 + 4) * 5 * 6 * 7 * 8 * 9 * 10 * 11 * 12 * 13 * 14 * 15 * 16 * 17 * 18 * "
    "19 * 20 * 21 * 22 * 23 * 24 * 25 * 26 * 27 * 28 * 29 * 30"
)

DEEP_EXPRESSION = " + ".join(str(number) for number in range(1, 21))
DEEP_EXPECTED = float(sum(range(1, 21)))  # 1..20 求和 = 210

# 一、能算的必须算对：(表达式, 期望结果)
NUMERIC_CASES: list[tuple[str, float]] = [
    ("1 + 1", 2.0),
    ("10 - 4 * 2", 2.0),
    ("(12 + 8) / 4", 5.0),
    ("2 ** 10", 1024.0),
    ("2 ** -3", 0.125),
    ("7 % 3", 1.0),
    ("7 // 2", 3.0),
    ("-3 + 1", -2.0),
    ("+5", 5.0),
    ("1.5 * 2", 3.0),
]

# 二、该拒的必须拒掉：(表达式, 这条测的攻击面)
REJECT_CASES: list[tuple[str, str]] = [
    ("__import__('os')", "函数调用：直接执行任意代码"),
    ("open('/etc/passwd')", "函数调用：读文件"),
    ("os.getcwd()", "未知名字 + 属性访问"),
    ("a[0]", "下标访问"),
    ("'a' * 3", "字符串乘法"),
    ("x + 1", "变量名"),
    ("1 == 1", "比较运算"),
    ("[1, 2]", "列表字面量"),
    ("{1: 2}", "字典字面量"),
    ("1 + 1 if True else 2", "条件表达式"),
    ("sum([1, 2])", "函数调用：内置函数"),
    ("2 ** 100", "指数炸弹：指数远超上限"),
    ("2 ** 11", "指数炸弹：刚过上限的边界"),
    ("1 / 0", "运行时错误：除以零"),
    ("1 +", "语法错误"),
    ("1e400", "溢出：常量本身就是无穷大"),
    (LONG_EXPRESSION, "超长表达式"),
]

# 三、加分项（不影响退出码）：(表达式, 期望结果, 这条考什么)
BONUS_NUMERIC: list[tuple[str, float, str]] = [
    ("--5", 5.0, "嵌套一元运算"),
    (DEEP_EXPRESSION, DEEP_EXPECTED, "深一点的表达式树，递归会不会写错"),
]

# 三、加分项（不影响退出码）：(表达式, 这条考什么)
BONUS_REJECT: list[tuple[str, str]] = [
    ("True", "bool 不是数字（isinstance(True, int) 是 True 的坑）"),
    ("False + 1", "bool 参与运算"),
    ("None", "None 不是数字"),
    ("2 ** 10.5", "指数是小数且超过上限"),
]


def attempt(expression: str) -> tuple[str, float | None, str]:
    """跑一次调用，返回 (结果类型, 返回值, 描述)。

    结果类型：
      ok       —— 正常返回了一个数
      rejected —— 抛出了 ToolError（我们期望的拒绝方式）
      crashed  —— 抛出了别的东西，说明异常没转换干净
    """
    try:
        return "ok", safe_calculate(expression), ""
    except ToolError as exc:
        return "rejected", None, f"ToolError：{exc}"
    except Exception as exc:  # noqa: BLE001 - 练习脚本要如实展示任何异常类型
        return "crashed", None, f"漏出了 {type(exc).__name__}：{exc}"


def report(label: str, expression: str, ok: bool, detail: str) -> int:
    """打印一行结果，返回失败计数（0 或 1），方便用 failed += report(...) 累加。"""
    shown = expression if len(expression) <= 44 else expression[:41] + "..."
    print(f"  [{'通过' if ok else '失败'}] {label:<4} {shown:<46} {detail}")
    return 0 if ok else 1


def check_numeric(cases: list[tuple[str, float] | tuple[str, float, str]]) -> int:
    """逐条验证「应该算出这个数」。第三个元素是可选的说明文字。"""
    failed = 0
    for case in cases:
        expression, expected = case[0], case[1]
        note = f"{case[2]}，" if len(case) > 2 else ""
        kind, actual, detail = attempt(expression)
        if kind != "ok":
            failed += report(
                "算值", expression, False, f"{note}期望 {expected}，但没算出数（{detail}）"
            )
        elif actual is None or abs(actual - expected) > 1e-9:
            failed += report("算值", expression, False, f"{note}期望 {expected}，实际 {actual}")
        else:
            report("算值", expression, True, f"{note}= {actual}")
    return failed


def check_reject(cases: list[tuple[str, str]]) -> int:
    """逐条验证「必须被拒绝」。"""
    failed = 0
    for expression, note in cases:
        kind, actual, detail = attempt(expression)
        if kind == "rejected":
            report("拦截", expression, True, note)
        elif kind == "ok":
            failed += report("拦截", expression, False, f"没拦住，返回了 {actual}（{note}）")
        else:
            failed += report("拦截", expression, False, f"拒绝方式不对，{detail}（{note}）")
    return failed


def sanity_check() -> None:
    """确认测试数据本身自洽，避免出题出错误导你。"""
    if len(LONG_EXPRESSION) <= MAX_LENGTH:
        print(f"注意：超长样例只有 {len(LONG_EXPRESSION)} 字符，没超过上限 {MAX_LENGTH}")


def main() -> int:
    print(f"safe_calculate 来自：{safe_calculate.__module__}")
    sanity_check()
    print()

    print("一、能不能算对")
    hard = check_numeric(NUMERIC_CASES)

    print("\n二、该拒的有没有拒掉")
    hard += check_reject(REJECT_CASES)

    print("\n三、[加分] 边界与细节")
    bonus = check_numeric(BONUS_NUMERIC) + check_reject(BONUS_REJECT)

    print()
    if hard == 0:
        print(f"必测全绿，加分项失败 {bonus} 条。")
        print("别忘了再跑一次：python -m pytest tests/test_tools.py -q")
        return 0
    print(f"必测还有 {hard} 条没过，加分项失败 {bonus} 条。改完 safe_calc.py 再跑一遍。")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
