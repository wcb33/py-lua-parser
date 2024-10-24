from ast import Name
import textwrap

from luaparser import ast
from luaparser.astnodes import *
from luaparser.utils import tests


class LuaOutputTestCase(tests.TestCase):
    def test_assign(self):
        source = textwrap.dedent(
            '''\
            a = 42
            local b = "42"'''
        )
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))

    def test_while(self):
        source = textwrap.dedent(
            """\
            while a[i] do
                print(a[i])
                i = i + 1
            end"""
        )
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))

    def test_repeat(self):
        source = textwrap.dedent(
            """\
            repeat
                print("value of a:", a)
            until a > 15"""
        )
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))

    def test_if(self):
        source = textwrap.dedent(
            """\
            if op == "+" then
                r = a + b
            elseif op == "-" then
                r = a - b
            elseif op == "*" then
                r = a * b
            elseif op == "/" then
                r = a / b
            else
                error("invalid operation")
            end"""
        )
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))

    def test_goto(self):
        source = textwrap.dedent(
            """\
            ::label::
            goto label"""
        )
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))

    def test_func(self):
        source = textwrap.dedent(
            """\
            function nop(arg, ...)
                break
                return 1, 2, 3
            end"""
        )
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))

    def test_for_num(self):
        source = textwrap.dedent(
            """\
            for i = 1, 10 do
                print(i)
            end"""
        )
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))

    def test_for_in(self):
        source = textwrap.dedent(
            """\
            for key, value in pairs(t) do
                print(key, value)
            end"""
        )
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))

    def test_call_invoke(self):
        source = textwrap.dedent(
            """\
            call("foo")
            invoke:me("ok")"""
        )
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))

    def test_method(self):
        source = textwrap.dedent(
            """\
            function my:method(arg1, ...)
                nop()
            end"""
        )
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))

    def test_anonymous_func(self):
        source = textwrap.dedent(
            """\
            local ano = function()
                nop()
            end"""
        )
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))

    def test_table(self):
        source = textwrap.dedent(
            """\
            local table = {
                ['ok'] = true,
                foo = bar,
            }"""
        )
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))

    def test_int_24(self):
        source = textwrap.dedent(
            """\
            local a = 0
            if a == 0 then
                if a == 1 then
                    if a == 2 then
                        if a == 3 then
                        
                        end
                    end
                end
            end"""
        )
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))

    def test_parenthesis(self):
        source = "a = (1 * 2) + 3"
        self.assertEqual(source, ast.to_lua_source(ast.parse(source)))

    def test_parenthesis_2(self):
        source = """
-- test func
a = (1 * 2) + 3
"""
        res = "a = (1 * 2) + 3"
        self.assertEqual(res, ast.to_lua_source(ast.parse(source), ignore_types=[Comment]))

    def test_parenthesis_3(self):
        source = """
-- test func
a = (1 * 2) + 3;
"""
        res = """\
a = (1 * 2) + 3
"""
        self.assertEqual(res, ast.to_lua_source(ast.parse(source), ignore_types=[Comment, SemiColon]))

    def test_parenthesis_4(self):
        source = """
        test_table = {
        ["zqdm"] = {
                def = "",
                field = "stock_code",
            },
            }
        """
        res = """\
test_table = {
    ["zqdm"] = { def = "", field = "stock_code" },
}"""

        def custom_should_indent(node:Table):
            for item in node.fields:
                if isinstance(item.key,Name):
                    if item.key.id == "def" or item.key.id == "field":
                        return True

            return False
        self.maxDiff=None
        str1 = ast.to_lua_source(ast.parse(source), ignore_types=[Comment, SemiColon], should_indent_callback=custom_should_indent) 
        self.assertEqual(res, str1)


    def test_parenthesis_5(self):
        source = """\
        a = CreateReturnHDFile({
                    'index',
                    {
                        'cj_rq', '发生日期', DTE_STRING + WT_CJ_RQ,
                        DD_RIGHT, 8, 3
                    }, 'wt_rq', 'cj_sj', 'zqdm',
                    {'zqmc', '', DTE_STRING + WT_ZQMC, DD_LEFT, 16, 3},
                    {
                        'czlb', '业务名称', DTE_STRING + WT_CZLB, DD_RIGHT,
                        16, 3
                    }
                })
        """
        res = """\
a = CreateReturnHDFile({
    'index',
    { 'cj_rq', '发生日期', DTE_STRING + WT_CJ_RQ, DD_RIGHT, 8, 3 },
    'wt_rq',
    'cj_sj',
    'zqdm',
    { 'zqmc', '', DTE_STRING + WT_ZQMC, DD_LEFT, 16, 3 },
    { 'czlb', '业务名称', DTE_STRING + WT_CZLB, DD_RIGHT, 16, 3 },
})"""

        def custom_should_indent(node:Table):
            if len(node.fields) == 0:
                return True  # 如果 fields 为空，直接返回 True

            first_item = node.fields[0]  # 获取第一个 item

            if isinstance(first_item.key, Name):
                return first_item.key.id in {"def", "field", "change"}
            elif isinstance(first_item.key, Number):
                # 检查所有 fields 是否为 Number 或 String
                return all(isinstance(item.value, (Number, String, Name, Index, AddOp)) for item in node.fields)
            else:
                return False  # 其他类型的 key 返回 False
        self.maxDiff=None
        str1 = ast.to_lua_source(ast.parse(source), ignore_types=[Comment, SemiColon], should_indent_callback=custom_should_indent) 
        self.assertEqual(res, str1)