"""PRD-027: CPE Readiness Benchmark v1 Test Suite & Readiness Gate.

This module loads the authoritative 200-case corpus from
`tests/fixtures/benchmarks/cpe_readiness_v1.json`, executes the real CPE
pipeline, validates exact PerformanceGraph schema and values, checks deterministic
repeatability, and validates readiness for the CPE -> CAM contract freeze.

Corpus Breakdown:
- 10 Canonical PRD-026 cases (CANONICAL-001 .. CANONICAL-010)
- 40 Adversarial/Edge cases (ADV-001 .. ADV-040)
- 150 General Authored Regression cases (GEN-001 .. GEN-150)
Total: exactly 200 cases.
"""
import json
import pytest
from pathlib import Path
from typing import Any, Dict, List

from cse.performance.context import PerformanceContext
from cse.performance.graph import PerformanceGraph
from cse.performance.integration import generate_performance_graph
from cse.performance.passes.explicit_tag_parser import ExplicitTagError

# Authoritative path to the benchmark corpus
CORPUS_PATH = Path(__file__).resolve().parent / "fixtures" / "benchmarks" / "cpe_readiness_v1.json"

# Canonical PerformanceGraph fields — frozen contract
EXPECTED_GRAPH_FIELDS = frozenset({
    "text",
    "character_state",
    "semantics",
    "intent",
    "plan",
})


def load_benchmark_corpus() -> List[Dict[str, Any]]:
    """Load the benchmark corpus from disk in read-only mode."""
    if not CORPUS_PATH.exists():
        raise FileNotFoundError(f"Benchmark corpus not found at {CORPUS_PATH}")

    with open(CORPUS_PATH, "r", encoding="utf-8") as f:
        cases = json.load(f)

    if not isinstance(cases, list):
        raise ValueError(f"Corpus must be a JSON array, got {type(cases).__name__}")

    return cases


# Pre-load cases for pytest parametrization
_CORPUS_CASES = load_benchmark_corpus()


# ==============================================================================
# Corpus Integrity & Schema Checks
# ==============================================================================

class TestBenchmarkCorpusIntegrity:
    """Validate that the benchmark corpus meets all PRD-027 requirements."""

    def test_corpus_exists_and_readable(self):
        """Corpus file must exist at tests/fixtures/benchmarks/cpe_readiness_v1.json."""
        assert CORPUS_PATH.exists()
        assert CORPUS_PATH.is_file()
        assert CORPUS_PATH.stat().st_size > 0

    def test_exact_case_count_200(self):
        """Corpus must contain exactly 200 authored cases."""
        assert len(_CORPUS_CASES) == 200, f"Expected 200 cases, found {len(_CORPUS_CASES)}"

    def test_case_ids_unique(self):
        """Every case ID must be unique."""
        ids = [c["id"] for c in _CORPUS_CASES]
        assert len(ids) == len(set(ids)), f"Duplicate case IDs found: {[x for x in ids if ids.count(x) > 1]}"

    def test_case_breakdown_categories(self):
        """Corpus must contain exactly 10 canonical, 40 adversarial, and 150 general cases."""
        canonical = [c for c in _CORPUS_CASES if c["id"].startswith("CANONICAL-")]
        adversarial = [c for c in _CORPUS_CASES if c["id"].startswith("ADV-")]
        general = [c for c in _CORPUS_CASES if c["id"].startswith("GEN-")]

        assert len(canonical) == 10, f"Expected 10 canonical cases, got {len(canonical)}"
        assert len(adversarial) == 40, f"Expected 40 adversarial cases, got {len(adversarial)}"
        assert len(general) == 150, f"Expected 150 general cases, got {len(general)}"
        assert len(canonical) + len(adversarial) + len(general) == 200

    def test_case_structure_valid(self):
        """Every case must conform to either normal case schema or error case schema."""
        for case in _CORPUS_CASES:
            cid = case["id"]
            assert "input" in case, f"Case {cid} missing 'input'"
            assert isinstance(case["input"], str), f"Case {cid} 'input' must be string"

            if "expected_error" in case:
                assert isinstance(case["expected_error"], str)
                assert "expected" not in case, f"Error case {cid} must not have 'expected' graph"
            else:
                assert "expected" in case, f"Normal case {cid} missing 'expected'"
                exp = case["expected"]
                assert set(exp.keys()) == EXPECTED_GRAPH_FIELDS, (
                    f"Case {cid} expected fields {set(exp.keys())} != {EXPECTED_GRAPH_FIELDS}"
                )
                assert isinstance(exp["text"], str)
                assert isinstance(exp["semantics"], dict)
                assert isinstance(exp["intent"], dict)
                assert isinstance(exp["plan"], dict)


# ==============================================================================
# PerformanceGraph Contract & Schema Isolation
# ==============================================================================

class TestPerformanceGraphContract:
    """Verify that PerformanceGraph schema contains strictly the 5 canonical fields."""

    def test_performance_graph_dataclass_fields(self):
        """PerformanceGraph must define exactly: text, character_state, semantics, intent, plan."""
        fields = set(PerformanceGraph.__dataclass_fields__.keys())
        assert fields == EXPECTED_GRAPH_FIELDS, f"PerformanceGraph schema mismatch: {fields} != {EXPECTED_GRAPH_FIELDS}"

    def test_no_disallowed_fields_in_graph(self):
        """Disallowed fields (explicit_intent_overrides, model, onnx, backend, cam) must NOT exist."""
        disallowed = [
            "explicit_intent_overrides",
            "model",
            "onnx",
            "backend",
            "cam",
            "embeddings",
            "weights",
        ]
        graph_fields = set(PerformanceGraph.__dataclass_fields__.keys())
        for d in disallowed:
            assert d not in graph_fields, f"Disallowed field '{d}' found in PerformanceGraph schema!"


# ==============================================================================
# Individual Benchmark Case Execution (200 / 200 Cases)
# ==============================================================================

@pytest.mark.parametrize("case", _CORPUS_CASES, ids=[c["id"] for c in _CORPUS_CASES])
def test_cpe_benchmark_case(case: Dict[str, Any]):
    """Execute a single benchmark case through the real CPE pipeline and assert exact results."""
    cid = case["id"]
    inp = case["input"]
    character_state = case.get("character_state")

    # Build input context
    if character_state is not None:
        input_data = PerformanceContext(text=inp, character_state=character_state)
    else:
        input_data = inp

    # Case 1: Expected validation error
    if "expected_error" in case:
        expected_err = case["expected_error"]
        try:
            graph = generate_performance_graph(input_data)
            pytest.fail(
                f"Case {cid} [{inp}]: Expected error {expected_err}, but unexpectedly produced PerformanceGraph: {graph}"
            )
        except Exception as exc:
            actual_err_type = type(exc).__name__
            assert actual_err_type == expected_err, (
                f"Case {cid} [{inp}]: Expected error {expected_err}, but got {actual_err_type}: {exc}"
            )
        return

    # Case 2: Normal case with expected PerformanceGraph
    expected = case["expected"]
    actual_graph = generate_performance_graph(input_data)

    # Validate output type
    assert isinstance(actual_graph, PerformanceGraph), (
        f"Case {cid} [{inp}]: Expected PerformanceGraph, got {type(actual_graph).__name__}"
    )

    # Validate schema strictly has 5 canonical fields
    actual_fields = set(actual_graph.__dataclass_fields__.keys())
    assert actual_fields == EXPECTED_GRAPH_FIELDS, (
        f"Case {cid} [{inp}]: PerformanceGraph schema mismatch: {actual_fields} != {EXPECTED_GRAPH_FIELDS}"
    )

    # Detailed field-by-field assertions with clear diagnostic diffs
    errors = []

    if actual_graph.text != expected["text"]:
        errors.append(f"  text mismatch:\n    expected: {expected['text']!r}\n    actual:   {actual_graph.text!r}")

    if actual_graph.character_state != expected["character_state"]:
        errors.append(
            f"  character_state mismatch:\n"
            f"    expected: {expected['character_state']!r}\n"
            f"    actual:   {actual_graph.character_state!r}"
        )

    if actual_graph.semantics != expected["semantics"]:
        errors.append(
            f"  semantics mismatch:\n"
            f"    expected: {expected['semantics']}\n"
            f"    actual:   {actual_graph.semantics}"
        )

    if actual_graph.intent != expected["intent"]:
        errors.append(
            f"  intent mismatch:\n"
            f"    expected: {expected['intent']}\n"
            f"    actual:   {actual_graph.intent}"
        )

    if actual_graph.plan != expected["plan"]:
        errors.append(
            f"  plan mismatch:\n"
            f"    expected: {expected['plan']}\n"
            f"    actual:   {actual_graph.plan}"
        )

    if errors:
        error_msg = f"Benchmark Case Failure in {cid} (Input: {inp!r}):\n" + "\n".join(errors)
        pytest.fail(error_msg)


# ==============================================================================
# Deterministic Repeatability Suite (All 200 Cases: Normal + Error)
# ==============================================================================

class TestBenchmarkDeterminism:
    """Verify that EVERY benchmark case (normal and error) produces identical behavior across repetitions."""

    def test_normal_cases_deterministic_repeatability(self):
        """Execute all normal cases repeatedly (5 runs) and assert identical PerformanceGraphs."""
        normal_cases = [c for c in _CORPUS_CASES if "expected" in c]
        repetitions = 5

        for case in normal_cases:
            cid = case["id"]
            inp = case["input"]
            character_state = case.get("character_state")

            if character_state is not None:
                input_data = PerformanceContext(text=inp, character_state=character_state)
            else:
                input_data = inp

            first_run = generate_performance_graph(input_data)

            for rep in range(1, repetitions):
                repeated_run = generate_performance_graph(input_data)

                assert repeated_run.text == first_run.text, (
                    f"Determinism failure in normal case {cid} at repetition {rep}: text differed"
                )
                assert repeated_run.character_state == first_run.character_state, (
                    f"Determinism failure in normal case {cid} at repetition {rep}: character_state differed"
                )
                assert repeated_run.semantics == first_run.semantics, (
                    f"Determinism failure in normal case {cid} at repetition {rep}: semantics differed"
                )
                assert repeated_run.intent == first_run.intent, (
                    f"Determinism failure in normal case {cid} at repetition {rep}: intent differed"
                )
                assert repeated_run.plan == first_run.plan, (
                    f"Determinism failure in normal case {cid} at repetition {rep}: plan differed"
                )
                assert repeated_run == first_run, (
                    f"Determinism failure in normal case {cid} at repetition {rep}: dataclass equality failed"
                )

    def test_error_cases_deterministic_repeatability(self):
        """Execute all error cases repeatedly (5 runs) and assert identical exception behavior."""
        error_cases = [c for c in _CORPUS_CASES if "expected_error" in c]
        repetitions = 5

        assert len(error_cases) > 0, "Corpus must contain error cases for determinism testing"

        for case in error_cases:
            cid = case["id"]
            inp = case["input"]
            character_state = case.get("character_state")
            expected_err = case["expected_error"]

            if character_state is not None:
                input_data = PerformanceContext(text=inp, character_state=character_state)
            else:
                input_data = inp

            for rep in range(repetitions):
                try:
                    graph = generate_performance_graph(input_data)
                    pytest.fail(
                        f"Determinism failure in error case {cid} at repetition {rep}: "
                        f"Expected {expected_err}, but unexpectedly produced a PerformanceGraph: {graph}"
                    )
                except Exception as exc:
                    actual_err = type(exc).__name__
                    assert actual_err == expected_err, (
                        f"Determinism failure in error case {cid} at repetition {rep}: "
                        f"Expected {expected_err}, got {actual_err}: {exc}"
                    )

    def test_all_200_cases_deterministic_repeatability(self):
        """Verify that all 200 cases (100% of corpus) are covered by determinism checks."""
        normal_cases = [c for c in _CORPUS_CASES if "expected" in c]
        error_cases = [c for c in _CORPUS_CASES if "expected_error" in c]
        total_cases = len(normal_cases) + len(error_cases)

        assert len(_CORPUS_CASES) == 200
        assert total_cases == 200, f"Expected 200 total cases, got {total_cases}"


# ==============================================================================
# Standalone Runner & Summary Report
# ==============================================================================

def run_readiness_benchmark() -> Dict[str, Any]:
    """Execute the full readiness benchmark programmatically and return a summary report."""
    cases = load_benchmark_corpus()
    passed_cases = 0
    failed_cases = []

    normal_cases = [c for c in cases if "expected" in c]
    error_cases = [c for c in cases if "expected_error" in c]

    # 1. Benchmark Execution Pass
    for case in cases:
        cid = case["id"]
        inp = case["input"]
        character_state = case.get("character_state")

        if character_state is not None:
            input_data = PerformanceContext(text=inp, character_state=character_state)
        else:
            input_data = inp

        try:
            if "expected_error" in case:
                expected_err = case["expected_error"]
                try:
                    graph = generate_performance_graph(input_data)
                    failed_cases.append((cid, inp, f"Expected {expected_err} but unexpectedly produced PerformanceGraph: {graph}"))
                except Exception as e:
                    actual_err_type = type(e).__name__
                    if actual_err_type == expected_err:
                        passed_cases += 1
                    else:
                        failed_cases.append((cid, inp, f"Expected {expected_err} but got {actual_err_type}: {e}"))
            else:
                expected = case["expected"]
                graph = generate_performance_graph(input_data)

                # Schema check
                fields = set(graph.__dataclass_fields__.keys())
                if fields != EXPECTED_GRAPH_FIELDS:
                    failed_cases.append((cid, inp, f"Schema mismatch: {fields}"))
                    continue

                # Content check
                if (graph.text == expected["text"] and
                        graph.character_state == expected["character_state"] and
                        graph.semantics == expected["semantics"] and
                        graph.intent == expected["intent"] and
                        graph.plan == expected["plan"]):
                    passed_cases += 1
                else:
                    failed_cases.append((cid, inp, "Field value mismatch"))
        except Exception as e:
            failed_cases.append((cid, inp, f"Unexpected exception: {e}"))

    # 2. Determinism Execution Pass across ALL 200 cases (Normal + Error)
    normal_det_passed = 0
    error_det_passed = 0
    det_failures = []
    repetitions = 5

    # Normal cases determinism
    for case in normal_cases:
        cid = case["id"]
        inp = case["input"]
        character_state = case.get("character_state")
        input_data = PerformanceContext(text=inp, character_state=character_state) if character_state is not None else inp

        try:
            first_run = generate_performance_graph(input_data)
            all_match = True
            for rep in range(1, repetitions):
                rep_run = generate_performance_graph(input_data)
                if rep_run != first_run:
                    all_match = False
                    det_failures.append((cid, f"Normal run {rep} differed from first run"))
                    break
            if all_match:
                normal_det_passed += 1
        except Exception as e:
            det_failures.append((cid, f"Unexpected error during normal determinism check: {e}"))

    # Error cases determinism
    for case in error_cases:
        cid = case["id"]
        inp = case["input"]
        character_state = case.get("character_state")
        input_data = PerformanceContext(text=inp, character_state=character_state) if character_state is not None else inp
        expected_err = case["expected_error"]

        try:
            all_errored = True
            for rep in range(repetitions):
                try:
                    graph = generate_performance_graph(input_data)
                    all_errored = False
                    det_failures.append((cid, f"Error run {rep} unexpectedly produced PerformanceGraph: {graph}"))
                    break
                except Exception as exc:
                    actual_err_type = type(exc).__name__
                    if actual_err_type != expected_err:
                        all_errored = False
                        det_failures.append((cid, f"Error run {rep} raised {actual_err_type} != {expected_err}: {exc}"))
                        break
            if all_errored:
                error_det_passed += 1
        except Exception as e:
            det_failures.append((cid, f"Unexpected error during error determinism check: {e}"))


    total_det_passed = normal_det_passed + error_det_passed

    is_ready = (
        passed_cases == len(cases) and
        len(cases) == 200 and
        total_det_passed == len(cases) and
        len(failed_cases) == 0 and
        len(det_failures) == 0
    )

    return {
        "total": len(cases),
        "passed": passed_cases,
        "failed": len(failed_cases),
        "failed_details": failed_cases,
        "normal_cases_count": len(normal_cases),
        "error_cases_count": len(error_cases),
        "normal_determinism_verified": normal_det_passed,
        "error_determinism_verified": error_det_passed,
        "total_determinism_verified": total_det_passed,
        "determinism_failures": det_failures,
        "is_ready": is_ready,
    }


if __name__ == "__main__":
    print("=" * 60)
    print("PRD-027: CPE READINESS BENCHMARK V1 RUNNER")
    print("=" * 60)
    summary = run_readiness_benchmark()
    print(f"Total Benchmark Cases: {summary['total']}")
    print(f"Passed Cases:          {summary['passed']}")
    print(f"Failed Cases:          {summary['failed']}")
    print("\n--- Determinism Repeatability ---")
    print(f"Normal cases:          {summary['normal_determinism_verified']} / {summary['normal_cases_count']} verified")
    print(f"Error cases:           {summary['error_determinism_verified']} / {summary['error_cases_count']} verified")
    print(f"Total:                 {summary['total_determinism_verified']} / {summary['total']} determinism cases verified")

    if summary["is_ready"]:
        print("\n>>> CPE READY FOR CONTRACT FREEZE <<<")
    else:
        print("\n>>> READINESS GATE FAILED <<<")
        for cid, inp, reason in summary["failed_details"]:
            print(f"  FAILED {cid} ({inp!r}): {reason}")
        for cid, reason in summary["determinism_failures"]:
            print(f"  DETERMINISM FAILED {cid}: {reason}")

