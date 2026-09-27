"""Exercise the status predicate embedded in the reusable workflow."""
import ast
from pathlib import Path
import textwrap
import unittest

workflow = Path(__file__).resolve().parents[1] / '.github/workflows/review-reusable.yml'
source = workflow.read_text().split("python3 - <<'PY'\n", 1)[1].rsplit('\n          PY', 1)[0]
tree = ast.parse(textwrap.dedent(source))
predicate = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'completed_status')
namespace = {}
exec(compile(ast.Module(body=[predicate], type_ignores=[]), str(workflow), 'exec'), namespace)
completed_status = namespace['completed_status']


def status(identifier=1, state='success', description='Review completed', login='coderabbitai[bot]'):
    return {'id': identifier, 'context': 'CodeRabbit', 'state': state,
            'description': description, 'creator': {'login': login, 'type': 'Bot'}}


class ReviewGateTests(unittest.TestCase):
    def test_accepts_completed_clean_review(self):
        self.assertTrue(completed_status([status()]))

    def test_rejects_skipped_pending_and_other_authors(self):
        for item in [status(description='Review skipped'), status(state='pending'), status(login='other[bot]')]:
            with self.subTest(item=item):
                self.assertFalse(completed_status([item]))
        self.assertFalse(completed_status([]))

    def test_new_pending_status_overrides_old_success(self):
        self.assertFalse(completed_status([status(), status(2, state='pending')]))


if __name__ == '__main__':
    unittest.main()
