"""GL-P00-002/003/005: configuration and cloud writes fail closed."""

import json

import pytest

from scripts.dev.cloud_preflight import (
    APPROVED_PROJECT_REF,
    APPROVED_URL,
    CloudTargetError,
    assert_cloud_run,
    configuration_report,
    eligible_cloud_job,
)


def configuration(**changes):
    return {
        "SUPABASE_URL": APPROVED_URL,
        "SUPABASE_ANON_KEY": "sb_publishable_synthetic",
        "SUPABASE_SECRET_KEY": "sb_secret_synthetic",
        "GLYCOLENS_CLOUD_PROJECT_REF": APPROVED_PROJECT_REF,
        **changes,
    }


@pytest.mark.parametrize(
    "url",
    [
        "http://127.0.0.1:54321",
        "https://production.supabase.co",
        APPROVED_URL + ".evil.example",
        APPROVED_URL + "/rest/v1",
        APPROVED_URL + "?key=secret",
        APPROVED_URL.replace("https://", "http://"),
        APPROVED_URL.replace("https://", "https://user@"),
    ],
)
def test_unapproved_target_is_rejected_without_disclosing_value(url):
    with pytest.raises(CloudTargetError) as caught:
        assert_cloud_run(configuration(SUPABASE_URL=url), allow_cloud=True, run_id="gl_" + "a" * 24)
    assert url not in str(caught.value)


@pytest.mark.parametrize(
    "opt_in,run_id", [(False, "gl_" + "a" * 24), (True, ""), (True, "arbitrary")]
)
def test_mutations_need_explicit_intent_and_scoped_run_id(opt_in, run_id):
    with pytest.raises(CloudTargetError):
        assert_cloud_run(configuration(), allow_cloud=opt_in, run_id=run_id)


def test_modern_secret_is_sufficient_and_run_has_no_credentials():
    run = assert_cloud_run(configuration(), allow_cloud=True, run_id="gl_" + "a" * 24)
    assert run.project_ref == APPROVED_PROJECT_REF
    assert "secret" not in repr(run)
    assert run.run_id.startswith("gl_")


def test_mismatched_project_ref_and_missing_server_key_fail():
    for changes in [{"GLYCOLENS_CLOUD_PROJECT_REF": "other"}, {"SUPABASE_SECRET_KEY": ""}]:
        with pytest.raises(CloudTargetError):
            assert_cloud_run(configuration(**changes), allow_cloud=True, run_id="gl_" + "a" * 24)


def test_report_never_contains_secret_values_and_distinguishes_optional_providers():
    values = configuration(LLM_API_KEY="private-llm-canary", USDA_FDC_API_KEY="private-usda-canary")
    report = configuration_report(values)
    serialized = json.dumps(report)
    assert all(value not in serialized for name, value in values.items() if name.endswith("KEY"))
    assert report["cloud_configuration_ready"]
    assert not report["configuration_present"]["SUPABASE_SERVICE_ROLE_KEY"]
    assert report["configuration_present"]["SUPABASE_SECRET_KEY"]
    assert "GLYCOLENS_T1D_UOM_ROOT" not in report["configuration_present"]


@pytest.mark.parametrize(
    "event,ref,protected,enabled,expected",
    [
        ("pull_request", "refs/heads/main", True, True, False),
        ("pull_request_target", "refs/heads/main", True, True, False),
        ("workflow_dispatch", "refs/heads/untrusted", False, True, False),
        ("workflow_dispatch", "refs/heads/main", True, False, False),
        ("workflow_dispatch", "refs/heads/main", True, True, True),
    ],
)
def test_cloud_ci_is_manual_protected_and_opt_in(event, ref, protected, enabled, expected):
    assert eligible_cloud_job(event, ref, protected=protected, enabled=enabled) is expected
