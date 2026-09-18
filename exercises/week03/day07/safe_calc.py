"""Day 7 闭卷练习：重写 safe_calculate 的受限 AST 求值。

背景
    这是整个项目里最容易被面试官抓着问的一段代码。它要回答的问题是：
    「你凭什么敢把模型或用户给出的字符串拿去计算？」

目标
    实现 `safe_calculate(expression) -> float`：算出算术表达式的值，
    同时保证表达式里的任何内容都不会被当作**代码**执行。

硬性要求
    1. 只准解析，不准执行：用 `ast.parse(expression, mode="eval")` 拿到语法树，
       自己递归求值。**禁止出现 `eval` / `exec` / `compile`。**
    2. 只放行以下节点，其余一律拒绝：
       - `ast.Expression` —— 表达式根节点
       - 数字常量（int / float）
       - `ast.BinOp` 二元运算，运算符只允许 `+ - * / // % **`
       - `ast.UnaryOp` 一元运算，运算符只允许 `+x` / `-x`
       被拒绝的例子（这些都必须失败，不能算出结果）：
       名字 `x`、函数调用 `open(...)`、属性访问 `os.getcwd()`、下标 `a[0]`、
       比较 `1 == 1`、字符串 `'a' * 3`、列表/字典/条件表达式……
    3. 幂运算的指数绝对值不得超过 10（挡住 `2 ** 100` 这类算力炸弹）。
    4. 表达式长度超过 100 个字符直接拒绝。
    5. 计算结果绝对值超过 1e100 直接拒绝。
    6. 语法错误、除以零、数值溢出，统一转成 ToolError（不要漏出 SyntaxError / ZeroDivisionError）。
    7. `bool` 不是数字：`True` / `False` 也要拒绝。
       （坑：在 Python 里 `isinstance(True, int)` 是 True，不显式判断就会漏过去。）

错误类型
    出错时抛 `ToolError`（它继承自 ValueError，从项目里 import）。
    错误文案你自己定，验收脚本只校验类型，不校验文字。

验收（在仓库根目录执行）
    python exercises/day07/check_safe_calc.py     # 逐条打印通过/失败，末尾给总结
    python -m pytest tests/test_tools.py -q       # 项目原有的断言

    两处都绿 = Day 7 完成。写完后可以和 `src/support_agent/services/tools.py`
    里的参考实现 diff 一下，看看自己漏了哪一层防护——**别提前打开那个文件。**

排查工具（不是答案）
    print(ast.dump(ast.parse("2 ** 3", mode="eval"), indent=2))
    先看清楚表达式被解析成什么形状，再决定怎么递归。
"""

from __future__ import annotations

from support_agent.services.tools import ToolError  # noqa: F401  实现时要用它抛错

MAX_LENGTH = 100
MAX_EXPONENT = 10
MAX_RESULT = 1e100


def safe_calculate(expression: str) -> float:
    """计算一个算术表达式；不允许表达式里出现任何"代码"。"""
    # TODO(Day 7)：由你自己实现。
    #
    # 建议的推进顺序（每一步都跑一次验收脚本，看红点少没少）：
    #   1. 长度检查 + ast.parse
    #   2. 递归函数处理 Expression / Constant / BinOp / UnaryOp 四类节点
    #   3. 其余节点落到"兜底拒绝"分支
    #   4. 加上幂指数上限、结果上限、异常转换
    raise NotImplementedError("Day 7：请自己实现 safe_calculate")
