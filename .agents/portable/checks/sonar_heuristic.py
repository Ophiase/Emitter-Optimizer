"""SonarQube findings no linter of the repository reports, read from the AST."""

import ast
import re
import sys
from collections import Counter
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Final

COGNITIVE_COMPLEXITY_LIMIT: Final = 15
PARAMETER_LIMIT: Final = 13
_COLLECTION_CALLS: Final = frozenset({"tuple", "list", "set", "dict"})
_DUPLICATED_LITERAL_COUNT: Final = 3
_DUPLICATED_LITERAL_LENGTH: Final = 5
_WORD: Final = re.compile(r"\w+")
_BRANCHES: Final = (ast.If, ast.IfExp, ast.While, ast.Match, ast.Try)
_COMPREHENSIONS: Final = (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)
_LITERAL_ARGUMENTS: Final = (ast.List, ast.ListComp, ast.Set, ast.SetComp, ast.Dict, ast.DictComp)
_FUNCTIONS: Final = (ast.FunctionDef, ast.AsyncFunctionDef)
_SCOPES: Final = (*_FUNCTIONS, ast.Lambda)
_NESTING: Final = (ast.If, ast.For, ast.AsyncFor, ast.While, ast.IfExp, ast.ExceptHandler)
_LOOPS: Final = (ast.For, ast.AsyncFor, ast.comprehension)
_DICT_FACTORIES: Final = frozenset({"dict", "defaultdict", "OrderedDict", "Counter"})
_REGEX_CALLS: Final = frozenset({"compile", "match", "fullmatch", "search", "findall", "finditer", "sub", "split"})
_SPACES_AROUND_NEGATED_CLASS: Final = re.compile(r"\\s[*+]\(?\[\^[^\]]*\](?:[*+]|\{\d*,\d*\})|\[\^[^\]]*\](?:[*+]|\{\d*,\d*\})\??\)?\\s[*+]")


@dataclass(frozen=True, slots=True)
class Finding:
    line: int
    rule: str
    message: str
    end: int = 0

    def touches(self, lines: frozenset[int]) -> bool:
        return any(number in lines for number in range(self.line, max(self.line, self.end) + 1))


class CognitiveComplexity:
    """Sonar's cognitive complexity, close enough to warn before the scan:
    each branch costs one plus its nesting, an `elif` or `else` costs one,
    and each boolean operator sequence costs one."""

    @classmethod
    def of(cls, function: ast.AST) -> int:
        return sum(cls._cost(child, 0) for child in ast.iter_child_nodes(function))

    @classmethod
    def _cost(cls, node: ast.AST, nesting: int) -> int:
        if isinstance(node, _SCOPES):
            return cls._children(node, nesting + 1)
        if isinstance(node, ast.If):
            return 1 + nesting + cls._if_chain(node, nesting)
        own = (1 + nesting) if isinstance(node, _NESTING) else 0
        own += 1 if isinstance(node, ast.BoolOp) else 0
        if isinstance(node, ast.For | ast.AsyncFor | ast.While) and node.orelse:
            own += 1
        inner = nesting + 1 if isinstance(node, _NESTING) else nesting
        return own + cls._children(node, inner)

    @classmethod
    def _if_chain(cls, node: ast.If, nesting: int) -> int:
        cost = cls._cost(node.test, nesting) + cls._block(node.body, nesting + 1)
        if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
            elif_ = node.orelse[0]
            return cost + 1 + cls._if_chain(elif_, nesting)
        if node.orelse:
            return cost + 1 + cls._block(node.orelse, nesting + 1)
        return cost

    @classmethod
    def _block(cls, statements: list[ast.stmt], nesting: int) -> int:
        return sum(cls._cost(statement, nesting) for statement in statements)

    @classmethod
    def _children(cls, node: ast.AST, nesting: int) -> int:
        return sum(cls._cost(child, nesting) for child in ast.iter_child_nodes(node))


def _own_nodes(function: ast.AST) -> Iterator[ast.AST]:
    """The nodes of a function, its nested functions excluded."""
    for child in ast.iter_child_nodes(function):
        if isinstance(child, _SCOPES):
            continue
        yield child
        yield from _own_nodes(child)


def _function_findings(
    function: ast.FunctionDef | ast.AsyncFunctionDef,
    source: list[str],
    implements: bool,
    is_method: bool,
) -> Iterator[Finding]:
    complexity = CognitiveComplexity.of(function)
    if complexity > COGNITIVE_COMPLEXITY_LIMIT:
        yield Finding(function.lineno, "S3776", f"cognitive complexity {complexity} > {COGNITIVE_COMPLEXITY_LIMIT}: split {function.name}", _end(function))
    if isinstance(function, ast.AsyncFunctionDef) and not _may_await_nothing(function, implements):
        yield Finding(function.lineno, "S7503", f"{function.name} is async but awaits nothing", _end(function))
    parameters = _parameter_count(function, is_method)
    if parameters > PARAMETER_LIMIT:
        yield Finding(function.lineno, "S107", f"{function.name} takes {parameters} parameters > {PARAMETER_LIMIT}: group them", function.body[0].lineno - 1)
    if _is_empty(function, source):
        yield Finding(function.lineno, "S1186", f"{function.name} is empty: add a comment saying why")
    if not is_method and _recurses_unconditionally(function):
        yield Finding(function.lineno, "S2190", f"{function.name} calls itself on every path: add a base case", _end(function))


def _parameter_count(function: ast.FunctionDef | ast.AsyncFunctionDef, is_method: bool) -> int:
    """Every named parameter, the receiver of a method left out as Sonar does."""
    arguments = function.args
    named = [*arguments.posonlyargs, *arguments.args, *arguments.kwonlyargs]
    has_receiver = is_method and named and named[0].arg in {"self", "cls"}
    return len(named) - (1 if has_receiver else 0)


def _recurses_unconditionally(function: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """A self-call no branch guards: no if, loop or try in the body, and the
    call is not inside a comprehension filtered by an `if`."""
    nodes = list(_own_nodes(function))
    if any(isinstance(node, _BRANCHES) for node in nodes):
        return False
    guarded = {
        id(call)
        for node in nodes
        if isinstance(node, _COMPREHENSIONS) and any(generator.ifs for generator in node.generators)
        for call in ast.walk(node)
    }
    return any(_calls(node, function.name) and id(node) not in guarded for node in nodes)


def _calls(node: ast.AST, name: str) -> bool:
    if not isinstance(node, ast.Call):
        return False
    if isinstance(node.func, ast.Name):
        return node.func.id == name
    return (
        isinstance(node.func, ast.Attribute)
        and node.func.attr == name
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id in {"self", "cls"}
    )


def _end(node: ast.AST) -> int:
    return getattr(node, "end_lineno", None) or getattr(node, "lineno", 0)


def _uses_async(function: ast.AsyncFunctionDef) -> bool:
    asynchronous = (ast.Await, ast.AsyncFor, ast.AsyncWith, ast.Yield, ast.YieldFrom)
    return any(isinstance(node, asynchronous) for node in _own_nodes(function))


def _may_await_nothing(function: ast.AsyncFunctionDef, implements: bool) -> bool:
    """An async signature someone else imposes: a method of a class that
    implements an interface, a decorated handler, or a stub."""
    return implements or bool(function.decorator_list) or _is_stub(function) or _uses_async(function)


def _methods(tree: ast.Module, implementing_only: bool) -> frozenset[ast.AST]:
    return frozenset(
        method
        for owner in ast.walk(tree)
        if isinstance(owner, ast.ClassDef) and (owner.bases or not implementing_only)
        for method in owner.body
        if isinstance(method, _FUNCTIONS)
    )


def _is_stub(function: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """A body that only declares: a docstring, `...`, `pass` or a `raise`, as
    a Protocol or abstract method has; Sonar leaves those alone."""
    return all(
        isinstance(statement, ast.Pass | ast.Raise)
        or (isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Constant))
        for statement in function.body
    )


def _is_empty(function: ast.FunctionDef | ast.AsyncFunctionDef, source: list[str]) -> bool:
    body = function.body
    if not (len(body) == 1 and isinstance(body[0], ast.Pass)) or function.decorator_list:
        return False
    span = source[function.lineno - 1 : (function.end_lineno or function.lineno)]
    return not any("#" in line for line in span)


def _node_findings(node: ast.AST) -> Iterator[Finding]:
    if isinstance(node, ast.IfExp) and any(isinstance(part, ast.IfExp) for part in (node.body, node.orelse)):
        yield Finding(node.lineno, "S3358", "nested conditional expression: use an if statement")
    if isinstance(node, ast.ExceptHandler) and _catches_cancellation(node) and not _reraises(node):
        yield Finding(node.lineno, "S7497", "CancelledError caught and not re-raised")
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id in _COLLECTION_CALLS
        and len(node.args) == 1
        and isinstance(node.args[0], _LITERAL_ARGUMENTS)
    ):
        yield Finding(node.lineno, "S7496", f"{node.func.id}() wraps a literal or comprehension")


def _dict_names(tree: ast.Module) -> frozenset[str]:
    """Names the file binds to a dict: annotated as one, or assigned a dict
    literal, comprehension or factory call."""
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and ast.unparse(node.annotation).split("[")[0] in {"dict", "Mapping", "MutableMapping"}:
            names.add(node.target.id)
        if isinstance(node, ast.Assign | ast.AnnAssign) and _builds_a_dict(node.value):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            names.update(target.id for target in targets if isinstance(target, ast.Name))
    return frozenset(names)


def _builds_a_dict(value: ast.expr | None) -> bool:
    if isinstance(value, ast.Dict | ast.DictComp):
        return True
    return isinstance(value, ast.Call) and isinstance(value.func, ast.Name) and value.func.id in _DICT_FACTORIES


def _dict_unpackings(tree: ast.Module) -> Iterator[Finding]:
    """A loop unpacking each element of a dict: it walks the keys, which reads
    as a forgotten .items()."""
    names = _dict_names(tree)
    for node in ast.walk(tree):
        if isinstance(node, _LOOPS) and isinstance(node.target, ast.Tuple) and isinstance(node.iter, ast.Name) and node.iter.id in names:
            yield Finding(node.iter.lineno, "S7517", f"unpacking the keys of {node.iter.id}: iterate a tuple of them, or .items()")


def _backtracking_regexes(tree: ast.Module) -> Iterator[Finding]:
    """A spacing quantifier beside a quantified negated class: both can match
    the same spaces, the polynomial backtracking Sonar asks to review."""
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "re"
            and node.func.attr in _REGEX_CALLS
            and node.args
            and isinstance(node.args[0], ast.Constant)
            and isinstance(node.args[0].value, str)
            and _SPACES_AROUND_NEGATED_CLASS.search(node.args[0].value)
        ):
            yield Finding(node.lineno, "S5852", "\\s quantifier beside a quantified negated class: polynomial backtracking", _end(node))


def _catches_cancellation(handler: ast.ExceptHandler) -> bool:
    caught = handler.type
    names = caught.elts if isinstance(caught, ast.Tuple) else [caught]
    return any(isinstance(name, ast.Name | ast.Attribute) and ast.unparse(name).endswith("CancelledError") for name in names)


def _reraises(handler: ast.ExceptHandler) -> bool:
    return any(isinstance(node, ast.Raise) for node in ast.walk(handler))


def _duplicated_literals(tree: ast.Module) -> Iterator[Finding]:
    """Sonar's exceptions: under five characters, or only letters, digits and
    underscores — keys and identifiers, never flagged."""
    skipped = _docstrings_and_fstring_parts(tree)
    literals = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and len(node.value) >= _DUPLICATED_LITERAL_LENGTH
        and not _WORD.fullmatch(node.value)
        and id(node) not in skipped
    ]
    counts = Counter(literal.value for literal in literals)
    keylike = _keylike_literals(tree)
    meaningful = {literal.value for literal in literals if id(literal) not in keylike}
    for literal in literals:
        if counts[literal.value] >= _DUPLICATED_LITERAL_COUNT and literal.value in meaningful:
            yield Finding(literal.lineno, "S1192", f"{literal.value!r} appears {counts[literal.value]} times: name it once")


def _keylike_literals(tree: ast.Module) -> frozenset[int]:
    """Dict keys and encode/decode arguments: Sonar leaves a literal alone
    when it only ever appears there."""
    keys = (key for node in ast.walk(tree) if isinstance(node, ast.Dict) for key in node.keys if key is not None)
    encodings = (
        argument
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr in {"encode", "decode"}
        for argument in node.args
    )
    return frozenset(id(node) for node in (*keys, *encodings))


def _docstrings_and_fstring_parts(tree: ast.Module) -> frozenset[int]:
    owners = (ast.Module, ast.ClassDef, *_FUNCTIONS)
    docstrings = (
        owner.body[0].value
        for owner in ast.walk(tree)
        if isinstance(owner, owners)
        and owner.body
        and isinstance(owner.body[0], ast.Expr)
        and isinstance(owner.body[0].value, ast.Constant)
    )
    fstring_parts = (
        part for node in ast.walk(tree) if isinstance(node, ast.JoinedStr) for part in node.values
    )
    return frozenset(id(node) for node in (*docstrings, *fstring_parts))


def findings(path: str) -> Iterator[Finding]:
    text = Path(path).read_text(encoding="utf-8")
    tree = ast.parse(text, filename=path)
    source = text.splitlines()
    implementing = _methods(tree, implementing_only=True)
    methods = _methods(tree, implementing_only=False)
    for node in ast.walk(tree):
        if isinstance(node, _FUNCTIONS):
            yield from _function_findings(node, source, node in implementing, node in methods)
        yield from _node_findings(node)
    yield from _duplicated_literals(tree)
    yield from _dict_unpackings(tree)
    yield from _backtracking_regexes(tree)


def _reported(path: str, added: str) -> Iterator[str]:
    lines = None if added == "ALL" else frozenset(int(number) for number in added.split(",") if number)
    for finding in sorted(set(findings(path)), key=lambda finding: finding.line):
        if lines is None or finding.touches(lines):
            yield f"{path}:{finding.line}: {finding.rule} {finding.message}"


if __name__ == "__main__":
    for line in _reported(sys.argv[1], sys.argv[2]):
        print(line)
