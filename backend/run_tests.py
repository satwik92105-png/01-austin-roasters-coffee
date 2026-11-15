import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from test_security import (
    setup_function,
    test_health_check,
    test_public_can_read_menu,
    test_unauthenticated_cannot_mutate_menu,
    test_admin_login_and_authenticated_mutation,
    test_brute_force_lockout_429,
    test_mass_assignment_and_server_side_total_recalculation,
    test_xss_input_sanitization,
    test_idempotency_key_duplicate_prevention,
    test_kds_role_authorization,
    test_audit_logging_and_pagination,
    test_menu_upsert_and_id_normalization
)

tests = [
    ("test_health_check", test_health_check),
    ("test_public_can_read_menu", test_public_can_read_menu),
    ("test_unauthenticated_cannot_mutate_menu", test_unauthenticated_cannot_mutate_menu),
    ("test_admin_login_and_authenticated_mutation", test_admin_login_and_authenticated_mutation),
    ("test_brute_force_lockout_429", test_brute_force_lockout_429),
    ("test_mass_assignment_and_server_side_total_recalculation", test_mass_assignment_and_server_side_total_recalculation),
    ("test_xss_input_sanitization", test_xss_input_sanitization),
    ("test_idempotency_key_duplicate_prevention", test_idempotency_key_duplicate_prevention),
    ("test_kds_role_authorization", test_kds_role_authorization),
    ("test_audit_logging_and_pagination", test_audit_logging_and_pagination),
    ("test_menu_upsert_and_id_normalization", test_menu_upsert_and_id_normalization)
]

print("=== RUNNING FASTAPI SECURITY & ROLE VERIFICATION TESTS ===")
passed = 0
failed = 0

for name, test_fn in tests:
    setup_function()
    try:
        test_fn()
        print(f"[PASS]: {name}")
        passed += 1
    except AssertionError as e:
        print(f"[FAIL]: {name} (AssertionError: {e})")
        failed += 1
    except Exception as e:
        print(f"[ERROR]: {name} ({type(e).__name__}: {e})")
        failed += 1

print(f"\nSummary: {passed} PASSED, {failed} FAILED out of {len(tests)} tests.")
if failed > 0:
    sys.exit(1)
