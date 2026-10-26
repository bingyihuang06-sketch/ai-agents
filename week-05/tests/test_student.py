"""可修改的小测试示例：另选输入，保留自己的预期与解释。

测试通过参数接收课程 fixture，--impl 才能切换候选实现。
不要直接 from operations import pop_last 绕过这个开关。
"""


def test_my_pop_example(pop_last):
    items = [7, 4]

    result = pop_last(items)

    assert result == 4
    assert items == [7]


def test_my_pop_last_with_repeated_value(pop_last):
    """自选输入 [5, -2, 5]：只删除末尾那个 5，前一个 5 留在原位。"""
    items = [5, -2, 5]

    result = pop_last(items)

    assert result == 5
    assert items == [5, -2]
