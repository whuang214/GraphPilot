"""Every registered error code has a producer, and every producer is registered.

A registry of error codes drifts in silence, because an entry nothing emits breaks
nothing. `a5.f5` found the drift by hand and got it wrong in both directions: it reported
14 dead codes when four were dead, because it did not search `api/views.py`, and acting on
it would have deleted ten live codes from a public contract.

So the check is compiled rather than grepped, and it runs in both directions. A code an
integrator is told to handle must be reachable; a code a caller can receive must be
documented in the registry with its retryability.
"""

import ast
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from services.shared.operation_problem import _RETRYABILITY

BACKEND = Path(settings.BASE_DIR)
#: The functions that turn a code into something a caller receives.
_PRODUCERS = {
    "operation_problem", "_error", "_problem",
    # A draft refusal reaches the host as an operation error too -- the transport maps
    # the leading finding's code onto one. Omitting this reported every refusal code as
    # unreachable, which is how the first version of this guard failed.
    "DraftFinding",
    # The edit round trip raises rather than returning, and the transport maps the
    # exception onto an operation error. Same contract, different control flow.
    "EditRefused", "UpdateRefused",
}


def _emitted_codes():
    """Every string literal passed as the code argument of a producer, in product code."""
    found = {}
    for path in BACKEND.rglob("*.py"):
        if any(part in {".venv", "__pycache__", "tests"} for part in path.parts):
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            callee = getattr(node.func, "id", getattr(node.func, "attr", ""))
            if callee not in _PRODUCERS or not node.args:
                continue
            first = node.args[0]
            if isinstance(first, ast.Constant) and isinstance(first.value, str):
                found.setdefault(first.value, []).append(f"{path.name}:{node.lineno}")
        # A third producer form: an exception class carrying its own code, which the
        # transport reads off the instance. Two registered codes looked unemitted until
        # this was included, and deleting them would have removed the only signal a host
        # gets when the layout engine is missing.
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            for statement in node.body:
                if (
                    isinstance(statement, ast.Assign)
                    and any(getattr(t, "id", "") == "code" for t in statement.targets)
                    and isinstance(statement.value, ast.Constant)
                ):
                    found.setdefault(statement.value.value, []).append(
                        f"{path.name}:{statement.lineno}"
                    )
    return found


class ErrorCodeRegistryTests(SimpleTestCase):
    def test_every_registered_code_can_actually_be_emitted(self):
        """An entry nothing produces is a promise to an integrator that never arrives."""
        unreachable = sorted(set(_RETRYABILITY) - set(_emitted_codes()))

        self.assertEqual(
            unreachable, [],
            "registered but never emitted; delete it or emit it",
        )

    def test_every_emitted_code_is_registered(self):
        """The other direction. An unregistered code reaches a caller with no documented
        retryability, so a client cannot decide whether trying again is sensible."""
        unregistered = sorted(set(_emitted_codes()) - set(_RETRYABILITY))

        self.assertEqual(unregistered, [], "emitted but not in _RETRYABILITY")

    def test_one_condition_does_not_have_two_codes(self):
        """`diagram_name_conflict` and `diagram_exists` both meant "that name is taken".
        Only one was ever emitted, so an integrator handling the other waited forever."""
        self.assertNotIn("diagram_name_conflict", _RETRYABILITY)
        self.assertIn("diagram_exists", _RETRYABILITY)
