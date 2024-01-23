import unittest
import ast
from py_helpers import ASTExplorer


class TestConstructor(unittest.TestCase):
    def test_constructor(self):
        chainable = ASTExplorer()

        self.assertIsNone(chainable.tree)

    def test_constructor_with_tree(self):
        tree = ast.parse("def foo():\n  pass")
        chainable = ASTExplorer(tree)

        self.assertEqual(chainable.tree, tree)

    def test_constructor_with_string(self):
        with_string = ASTExplorer("def foo():\n  pass")
        with_tree = ASTExplorer(ast.parse("def foo():\n  pass"))

        self.assertEqual(with_string, with_tree)

    def test_constructor_with_anything_else(self):
        self.assertRaises(TypeError, lambda: ASTExplorer(1))


class TestVariableHelpers(unittest.TestCase):
    def test_find_variable_can_handle_all_asts(self):
        chainable = ASTExplorer().parse("x = 1")

        # First find_variable, so know that the AST has no body and we can be
        # sure find_class handles this.
        self.assertEqual(chainable.find_variable("x").find_variable("x"), ASTExplorer())

    def test_has_local_variable_in_function(self):
        func_str = """def foo():
  a = 1
  print(a)
  x = 2
"""

        chainable = ASTExplorer().parse(func_str)

        self.assertTrue(chainable.find_function("foo").has_variable("x"))

    def test_has_global_variable(self):
        globals_str = """a = 1
x = 2
"""

        chainable = ASTExplorer().parse(globals_str)

        self.assertTrue(chainable.has_variable("x"))

    def test_does_not_see_local_variables_out_of_scope(self):
        scopes_str = """def foo():
  a = 1
b = 2
"""

        chainable = ASTExplorer().parse(scopes_str)
        self.assertFalse(chainable.has_variable("a"))

    def test_is_integer(self):
        two_locals = """
def foo():
  a = 1
  print(a)
  x = 2
y = 3
"""
        chainable = ASTExplorer().parse(two_locals)
        self.assertTrue(chainable.find_function("foo").find_variable("x").is_integer())
        self.assertFalse(chainable.find_function("foo").find_variable("y").is_integer())

    def test_none_assignment(self):
        none_str = """
x = None
"""
        chainable = ASTExplorer().parse(none_str)

        self.assertTrue(chainable.has_variable("x"))
        self.assertTrue(chainable.find_variable("x").is_equivalent("x = None"))

    def test_local_variable_is_integer_with_string(self):
        chainable = ASTExplorer().parse('def foo():\n  x = "1"')

        self.assertFalse(chainable.find_function("foo").find_variable("x").is_integer())

    def test_variable_has_constant_value(self):
        chainable = ASTExplorer().parse('def foo():\n  x = "1"')

        self.assertEqual(chainable.find_function("foo").get_variable("x"), "1")

    def test_find_variable(self):
        chainable = ASTExplorer().parse('def foo():\n  x = "1"')

        self.assertTrue(
            chainable.find_function("foo").find_variable("x").is_equivalent('x = "1"'),
        )

    def test_find_variable_not_found(self):
        chainable = ASTExplorer().parse('def foo():\n  x = "1"')

        self.assertEqual(chainable.find_variable("y").tree, None)

    def test_function_call_assigned_to_variable(self):
        chainable = ASTExplorer().parse("def foo():\n  x = bar()")

        self.assertTrue(
            chainable.find_function("foo").find_variable("x").value_is_call("bar")
        )

    def test_function_call_not_assigned_to_variable(self):
        chainable = ASTExplorer().parse("def foo():\n  bar()")

        self.assertFalse(chainable.find_function("foo").value_is_call("bar"))


class TestFunctionAndClassHelpers(unittest.TestCase):
    def test_find_function_returns_chainable(self):
        func_str = """def foo():
  pass
"""
        chainable = ASTExplorer().parse(func_str)

        self.assertIsInstance(chainable.find_function("foo"), ASTExplorer)
        self.assertIsInstance(chainable.find_function("bar"), ASTExplorer)

    def test_find_function_can_handle_all_asts(self):
        chainable = ASTExplorer().parse("x = 1")

        # First find_variable, so know that the AST has no body and we can be
        # sure find_function handles this.
        self.assertEqual(chainable.find_variable("x").find_function("foo"), ASTExplorer())

    def test_parse_creates_chainable(self):
        chainable = ASTExplorer().parse("def foo():\n  pass")

        self.assertIsInstance(chainable.tree, ast.Module)
        self.assertEqual(
            ast.dump(chainable.tree), ast.dump(ast.parse("def foo():\n  pass"))
        )

    def test_find_function_returns_function_ast(self):
        chainable = ASTExplorer().parse("def foo():\n  pass")

        func = chainable.find_function("foo")

        self.assertIsInstance(func.tree, ast.FunctionDef)
        self.assertEqual(func.tree.name, "foo")

    def test_find_function_returns_chainable_none(self):
        chainable = ASTExplorer().parse("def foo():\n  pass")

        func = chainable.find_function("bar")

        self.assertIsInstance(func, ASTExplorer)
        self.assertEqual(func.tree, None)

    def test_nested_function(self):
        nested_str = """def foo():
  def bar():
    x = 1
  y = 2
"""

        chainable = ASTExplorer().parse(nested_str)

        self.assertTrue(chainable.find_function("foo").has_variable("y"))
        self.assertFalse(chainable.find_function("foo").has_variable("x"))
        self.assertTrue(
            chainable.find_function("foo").find_function("bar").has_variable("x")
        )

    def test_find_class(self):
        class_str = """
class Foo:
  def __init__(self):
    pass
"""

        chainable = ASTExplorer().parse(class_str)

        self.assertIsNotNone(chainable.find_class("Foo"))
        self.assertIsInstance(chainable.find_class("Foo"), ASTExplorer)

        self.assertIsInstance(chainable.find_class("Bar"), ASTExplorer)
        self.assertEqual(chainable.find_class("Bar"), ASTExplorer())

    def test_find_class_can_handle_all_asts(self):
        chainable = ASTExplorer().parse("x = 1")

        # First find_variable, so know that the AST has no body and we can be
        # sure find_class handles this.
        self.assertEqual(chainable.find_variable("x").find_class("Foo"), ASTExplorer())

    def test_method_exists(self):
        class_str = """
class Foo:
  def __init__(self):
    self.x = 1
  def bar(self):
    pass
"""
        chainable = ASTExplorer().parse(class_str)

        self.assertTrue(chainable.find_class("Foo").has_function("bar"))

    def test_not_has_function(self):
        chainable = ASTExplorer().parse("def foo():\n  pass")

        self.assertFalse(chainable.has_function("bar"))


class TestEquivalenceHelpers(unittest.TestCase):
    def test_is_equivalent(self):
        full_str = """def foo():
  a = 1
  print(a)
def bar():
  x = "1"
  print(x)
"""

        chainable = ASTExplorer().parse(full_str)

        expected = """def bar():
  x = "1"
  print(x)
"""

        self.assertTrue(chainable.find_function("bar").is_equivalent(expected))
        # Obviously, it should be equivalent to itself
        self.assertTrue(
            chainable.find_function("bar").is_equivalent(
                ast.unparse(chainable.find_function("bar").tree)
            )
        )

    def test_is_not_equivalent(self):
        full_str = """def foo():
  a = 1
  print(a)
def bar():
  x = "1"
  print(x)
"""
        chainable = ASTExplorer().parse(full_str)
        # this should not be equivalent because it contains an extra function

        expected = """def bar():
  x = "1"
  print(x)

def foo():
  a = 1
"""

        self.assertFalse(chainable.find_function("bar").is_equivalent(expected))

    def test_is_equivalent_with_conditional(self):
        cond_str = """
if True:
  pass
"""

        chainable = ASTExplorer().parse(cond_str)
        self.assertTrue(chainable[0].find_conditions()[0].is_equivalent("True"))

    def test_none_equivalence(self):
        none_str = """
x = None
"""

        chainable = ASTExplorer().parse(none_str)
        self.assertIsNone(chainable.get_variable("x"))
        self.assertFalse(chainable.find_variable("y").is_equivalent("None"))


class TestConditionalHelpers(unittest.TestCase):
    def test_find_if_statements(self):
        self.maxDiff = None
        if_str = """
x = 1
if x == 1:
  x = 2

if True:
  pass
"""

        chainable = ASTExplorer().parse(if_str)
        # it should return an array of Chainables, not a Chainable of an array
        for if_chainable in chainable.find_ifs():
            self.assertIsInstance(if_chainable, ASTExplorer)
        self.assertNotIsInstance(chainable.find_ifs(), ASTExplorer)
        self.assertEqual(len(chainable.find_ifs()), 2)

        self.assertTrue(chainable.find_ifs()[0].is_equivalent("if x == 1:\n  x = 2"))
        self.assertTrue(chainable.find_ifs()[1].is_equivalent("if True:\n  pass"))

    def test_find_conditions(self):
        if_str = """
if True:
  x = 1
else:
  x = 4
"""
        chainable = ASTExplorer().parse(if_str)

        # it should return an array of Chainables, not a Chainable of an array
        for if_cond in chainable.find_ifs()[0].find_conditions():
            self.assertIsInstance(if_cond, ASTExplorer)
        self.assertNotIsInstance(chainable.find_ifs()[0].find_conditions(), ASTExplorer)
        self.assertEqual(len(chainable.find_ifs()[0].find_conditions()), 2)

        self.assertIsNone(chainable.find_ifs()[0].find_conditions()[1].tree)

    def test_find_conditions_without_if(self):
        chainable = ASTExplorer().parse("x = 1")

        self.assertEqual(len(chainable.find_conditions()), 0)

    def test_find_conditions_only_if(self):
        if_str = """
if True:
  x = 1
"""
        chainable = ASTExplorer().parse(if_str)

        self.assertEqual(len(chainable.find_ifs()[0].find_conditions()), 1)

    def test_find_conditions_elif(self):
        if_str = """
if True:
  x = 1
elif y == 2:
  x = 2
elif not x < 3:
  x = 3
else:
  x = 4
"""
        chainable = ASTExplorer().parse(if_str)

        self.assertEqual(len(chainable.find_ifs()[0].find_conditions()), 4)
        self.assertTrue(
            chainable.find_ifs()[0].find_conditions()[0].is_equivalent("True")
        )
        self.assertTrue(
            chainable.find_ifs()[0].find_conditions()[1].is_equivalent("y == 2")
        )
        self.assertTrue(
            chainable.find_ifs()[0].find_conditions()[2].is_equivalent("not x < 3")
        )
        self.assertEqual(chainable.find_ifs()[0].find_conditions()[3].tree, None)
        self.assertFalse(
            chainable.find_ifs()[0]
            .find_conditions()[3]
            .is_equivalent("This can be anything")
        )

    def test_find_if_bodies(self):
        if_str = """
if True:
  x = 1
"""
        chainable = ASTExplorer().parse(if_str)

        self.assertEqual(len(chainable.find_ifs()[0].find_if_bodies()), 1)
        self.assertTrue(
            chainable.find_ifs()[0].find_if_bodies()[0].is_equivalent("x = 1")
        )

    def test_find_if_bodies_elif(self):
        if_str = """
if True:
  x = 1
elif y == 2:
  x = 2
elif True:
  x = 3
else:
  x = 4
"""
        chainable = ASTExplorer().parse(if_str)

        self.assertEqual(len(chainable.find_ifs()[0].find_if_bodies()), 4)
        self.assertTrue(
            chainable.find_ifs()[0].find_if_bodies()[0].is_equivalent("x = 1")
        )
        self.assertTrue(
            chainable.find_ifs()[0].find_if_bodies()[1].is_equivalent("x = 2")
        )
        self.assertTrue(
            chainable.find_ifs()[0].find_if_bodies()[2].is_equivalent("x = 3")
        )
        self.assertTrue(
            chainable.find_ifs()[0].find_if_bodies()[3].is_equivalent("x = 4")
        )
        self.assertRaises(
            IndexError, lambda: chainable.find_ifs()[0].find_if_bodies()[4]
        )


class TestGenericHelpers(unittest.TestCase):
    def test_equality(self):
        self.assertEqual(
            ASTExplorer().parse("def foo():\n  pass"),
            ASTExplorer().parse("def foo():\n  pass"),
        )
        self.assertNotEqual(
            ASTExplorer().parse("def foo():\n  pass"),
            ASTExplorer().parse("def bar():\n  pass"),
        )

    def test_strict_equality(self):
        self.assertNotEqual(
            ASTExplorer().parse("def foo():\n  pass"),
            ASTExplorer().parse("def foo():\n   pass"),
        )

    def test_not_equal_to_non_chainable(self):
        self.assertIsNotNone(ASTExplorer().parse("def foo():\n  pass"))
        self.assertNotEqual(ASTExplorer(), 1)

    def test_find_nth_statement(self):
        func_str = """
if True:
  pass

x = 1
"""
        chainable = ASTExplorer().parse(func_str)

        self.assertTrue(chainable[0].is_equivalent("if True:\n  pass"))
        self.assertTrue(chainable[1].is_equivalent("x = 1"))

    def test_raise_exception_if_out_of_bounds(self):
        one_stmt_str = """
if True:
  pass
"""

        chainable = ASTExplorer().parse(one_stmt_str)
        self.assertRaises(IndexError, lambda: chainable[1])

    def test_len_of_body(self):
        func_str = """
if True:
  pass
"""

        chainable = ASTExplorer().parse(func_str)

        self.assertEqual(len(chainable), 1)

    def test_len(self):
        ifs_str = """
if True:
  pass

if True:
  pass
"""

        chainable = ASTExplorer().parse(ifs_str)

        self.assertEqual(len(chainable.find_ifs()), 2)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestConstructor))
    suite.addTest(unittest.makeSuite(TestVariableHelpers))
    suite.addTest(unittest.makeSuite(TestFunctionAndClassHelpers))
    suite.addTest(unittest.makeSuite(TestEquivalenceHelpers))
    suite.addTest(unittest.makeSuite(TestConditionalHelpers))
    suite.addTest(unittest.makeSuite(TestGenericHelpers))
    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(suite())
