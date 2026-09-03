"""ServiceNow API, CLI, credential, pagination, and synchronization contract tests."""

from __future__ import annotations

import json
from pathlib import Path
from zipfile import ZipFile

import pytest
import requests

from knowledge.cli import main
from knowledge.errors import KnowledgeError
from knowledge.okf import split_frontmatter
from knowledge.registry import create_source_adapter
from knowledge.sources import servicenow as sn
from knowledge.store import KnowledgeStore

BASE = "https://dev.example.test"
GROUP = "a" * 32
KB = "b" * 32


def record(index: int = 1, **fields) -> dict:
    return {
        "sys_id": f"{index:032x}", "number": f"INC{index:07d}",
        "short_description": "VPN access", "description": "Restore access.",
        "sys_updated_on": "2026-08-28 12:00:00",
        "state": {"value": "1", "display_value": "New"},
        "assignment_group": {"value": GROUP, "display_value": "Support"},
        **fields,
    }


def response(result=None, *, status=200, headers=None, payload=None) -> requests.Response:
    result_response = requests.Response()
    result_response.status_code = status
    result_response.headers.update(headers or {})
    result_response._content = json.dumps(payload if payload is not None else {"result": result}).encode()
    result_response._content_consumed = True
    return result_response


def api(monkeypatch, *responses):
    queue = iter(responses)
    calls = []

    def request(method, url, **kwargs):
        calls.append((method, url, kwargs))
        item = next(queue)
        if isinstance(item, Exception):
            raise item
        return item

    monkeypatch.setattr(sn.requests, "request", request)
    return calls


@pytest.fixture(autouse=True)
def isolated_environment(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("SERVICENOW_BASE_URL", BASE)
    monkeypatch.setenv("SERVICENOW_USERNAME", "integration-test")
    monkeypatch.setenv("SERVICENOW_PASSWORD", "private-password-value")
    monkeypatch.delenv("SERVICENOW_TOKEN", raising=False)
    monkeypatch.setattr("knowledge.store.TEMP_ROOT", tmp_path / "cache")

    def blocked(*args, **kwargs):
        raise AssertionError("Unexpected network request")

    monkeypatch.setattr(sn.requests, "request", blocked)


@pytest.fixture
def store(tmp_path) -> KnowledgeStore:
    result = KnowledgeStore(tmp_path / "store")
    result.initialize()
    result.create_collection_key("itsm")
    return result


def run(store, capsys, *args):
    capsys.readouterr()
    code = main(["--store", str(store.root), *args])
    output = capsys.readouterr()
    return code, output.out, output.err


def register(store, capsys, *args):
    code, out, err = run(store, capsys, "add", "servicenow", "--key", "itsm", *args)
    assert code == 0, err
    return json.loads(out)["source"]


def client(**credentials):
    return sn.ServiceNowClient(BASE, **(credentials or {"username": "u", "password": "p"}))


@pytest.mark.parametrize("value", [
    None, "", "http://dev.example.test", "https://u:private-secret@dev.example.test",
    "https://dev.example.test/path", "https://dev.example.test?token=private-secret",
    "https://dev.example.test#fragment", "https://dev.example.test:8443",
    "https://[invalid", "https://bad host", "https://dev.example.test\\other",
])
def test_instance_origin_validation_does_not_leak_secrets(value):
    with pytest.raises(KnowledgeError) as error:
        sn.instance_url(value)
    assert "private-secret" not in str(error.value)


def test_authentication_requires_one_mode_and_does_not_use_netrc(monkeypatch):
    assert sn.instance_url("https://DEV.example.test:443/") == BASE
    for credentials in ({}, {"username": "u"}, {"password": "p"}, {"token": "t", "username": "u"}, {"token": "t\nx"}):
        with pytest.raises(KnowledgeError):
            sn.ServiceNowClient(BASE, **credentials)
    calls = api(monkeypatch, response([]), response([]))
    client().list_records("incident")
    assert calls[0][2]["auth"].username == "u"
    assert calls[0][2]["auth"].password == "p"
    client(token="test-bearer").list_records("incident")
    prepared = requests.Request("GET", BASE).prepare()
    calls[1][2]["auth"](prepared)
    assert prepared.headers["Authorization"] == "Bearer test-bearer"
    assert calls[1][2]["allow_redirects"] is False
    assert calls[1][2]["timeout"] == 60


@pytest.mark.parametrize("query", ["active=true^NQactive=false", "active=true^EQ", "x=javascript:gs.getUserID()", "x=1\ny=2"])
def test_unsafe_query_structure_rejected(query):
    with pytest.raises(KnowledgeError):
        sn.encoded_query(query)


def test_scopes_and_field_projections():
    query, scope = sn.scope_query("kb_knowledge", "workflow_state=published", knowledge_base=KB.upper(), text="VPN")
    assert query == f"workflow_state=published^short_descriptionLIKEVPN^kb_knowledge_base={KB}"
    assert scope == {"kb_knowledge_base": KB}
    fields = sn.checked_fields("kb_knowledge", ["text"], scope)
    assert set(fields) >= {"sys_id", "number", "sys_updated_on", "text", "kb_knowledge_base"}
    assert sn.field_value({"x": {"value": "raw", "display_value": "Shown"}}, "x", display=True) == "Shown"
    assert sn.field_value({}, "x") == ""
    assert sn.validate_sys_id(GROUP.upper()) == GROUP
    assert sn.default_fields("kb_knowledge_base")[1] == "title"
    for table, kwargs in [
        ("sys_user", {}), ("incident", {"knowledge_base": KB}),
        ("kb_knowledge", {"assignment_group": GROUP}), ("incident", {"text": "VPN^ORactive=true"}),
        ("incident", {"assignment_group": "../escape"}),
    ]:
        with pytest.raises(KnowledgeError):
            sn.scope_query(table, **kwargs)
    with pytest.raises(KnowledgeError):
        sn.checked_fields("incident", ["number,sys_id"], {})
    with pytest.raises(KnowledgeError):
        client().record_url("sys_user", GROUP)


def test_pagination_advances_requested_window_through_acl_filtered_pages(monkeypatch):
    next_link = '<https://untrusted.example/table?offset=wrong>; rel="next"'
    calls = api(
        monkeypatch,
        response([], headers={"Link": next_link}),
        response([record(1)], headers={"Link": next_link}),
        response([record(2)]),
    )
    result = client().list_records("incident", query="active=true", limit=4, page_size=2)
    assert [item["number"] for item in result["records"]] == ["INC0000001", "INC0000002"]
    assert [call[2]["params"]["sysparm_offset"] for call in calls] == [0, 2, 4]
    assert all(call[1] == BASE + "/api/now/table/incident" for call in calls)
    assert result["truncated"] is False
    assert calls[0][2]["params"]["sysparm_query"] == "active=true^ORDERBYsys_id"


def test_pagination_reports_truncation_and_honors_total_count(monkeypatch):
    calls = api(monkeypatch, response([record()], headers={"X-Total-Count": "10"}))
    result = client().list_records("incident", limit=1, page_size=100, offset=2)
    assert result["truncated"] and result["next_offset"] == 3
    assert calls[0][2]["params"]["sysparm_limit"] == 1
    calls = api(monkeypatch, response([record()], headers={"Link": '<x>; rel="prev"'}))
    assert client().list_records("incident", limit=1)["next_offset"] is None
    api(monkeypatch, response([record()], headers={"X-Total-Count": "bad"}))
    with pytest.raises(KnowledgeError, match="pagination count"):
        client().list_records("incident")


def test_full_pages_without_headers_continue_and_duplicate_ids_fail(monkeypatch):
    calls = api(monkeypatch, response([record()]), response([]))
    assert len(client().list_records("incident", page_size=1)["records"]) == 1
    assert len(calls) == 2
    api(monkeypatch, response([record()]), response([record()]))
    with pytest.raises(KnowledgeError, match="repeated"):
        client().list_records("incident", page_size=1)
    monkeypatch.setattr(sn, "_MAX_PAGES", 1)
    api(monkeypatch, response([], headers={"Link": '<x>; rel="next"'}))
    with pytest.raises(KnowledgeError, match="safety limit"):
        client().list_records("incident")


@pytest.mark.parametrize("kwargs", [{"limit": 0}, {"page_size": 0}, {"page_size": 101}, {"offset": -1}])
def test_invalid_pagination_is_rejected_before_network(kwargs):
    with pytest.raises(KnowledgeError):
        client().list_records("incident", **kwargs)


@pytest.mark.parametrize("result", [{}, [None], [{"sys_id": "../escape"}], [{"number": "INC123"}]])
def test_malformed_result_pages_fail_closed(monkeypatch, result):
    api(monkeypatch, response(result))
    with pytest.raises(KnowledgeError):
        client().list_records("incident")


def test_oversized_and_out_of_scope_pages_fail_closed(monkeypatch):
    api(monkeypatch, response([record(1), record(2)]))
    with pytest.raises(KnowledgeError, match="oversized"):
        client().list_records("incident", limit=1)
    api(monkeypatch, response([record(assignment_group=KB)]))
    with pytest.raises(KnowledgeError, match="outside"):
        client().list_records("incident", scope={"assignment_group": GROUP})


@pytest.mark.parametrize("status", [302, 401, 403, 404, 400, 500])
def test_http_errors_are_redacted(monkeypatch, status):
    calls = api(monkeypatch, response(payload={"error": {"message": "private-password-value"}}, status=status))
    with pytest.raises(KnowledgeError) as error:
        client().list_records("incident")
    assert f"HTTP {status}" in str(error.value)
    assert "private-password-value" not in str(error.value)
    assert len(calls) == 1


def test_get_retries_are_bounded_but_post_is_not_replayed(monkeypatch):
    delays = []
    monkeypatch.setattr(sn.time, "sleep", delays.append)
    calls = api(
        monkeypatch, response(status=429, headers={"Retry-After": "999"}),
        response(status=503, headers={"Retry-After": "not-a-number"}), response([]),
    )
    assert client().list_records("incident")["records"] == []
    assert len(calls) == 3 and delays == [5, 2]
    calls = api(monkeypatch, response(status=503))
    with pytest.raises(KnowledgeError, match="Creation may have succeeded"):
        client().create_ticket({"short_description": "Test"})
    assert len(calls) == 1
    calls = api(monkeypatch, requests.Timeout("private-password-value"))
    with pytest.raises(KnowledgeError, match="outcome is unknown") as error:
        client().create_ticket({"short_description": "Test"})
    assert len(calls) == 1 and "private-password-value" not in str(error.value)


def test_invalid_json_and_missing_envelope(monkeypatch):
    invalid = response()
    invalid._content = b"<html>SSO login</html>"
    api(monkeypatch, invalid)
    with pytest.raises(KnowledgeError, match="invalid JSON"):
        client().list_records("incident")
    api(monkeypatch, response(payload={"unrelated": []}))
    with pytest.raises(KnowledgeError, match="missing result"):
        client().list_records("incident")


def test_successful_post_with_unusable_response_warns_against_duplicate_creation(monkeypatch):
    invalid = response(status=201)
    invalid._content = b"<html>created, but the response was truncated</html>"
    calls = api(monkeypatch, invalid)
    with pytest.raises(
        KnowledgeError,
        match="accepted the creation.*invalid JSON.*do not repeat creation",
    ):
        client().create_ticket({"short_description": "Test"})
    assert len(calls) == 1

    calls = api(monkeypatch, response(status=201, payload={"unrelated": {}}))
    with pytest.raises(
        KnowledgeError,
        match="accepted the creation.*no result envelope.*do not repeat creation",
    ):
        client().create_ticket({"short_description": "Test"})
    assert len(calls) == 1


def test_read_ticket_by_id_and_number(monkeypatch):
    expected = record()
    calls = api(monkeypatch, response(expected))
    assert client().read_record("incident", expected["sys_id"]) == expected
    assert calls[0][1].endswith("/incident/" + expected["sys_id"])
    calls = api(monkeypatch, response([expected]))
    assert client().read_record("incident", expected["number"]) == expected
    assert calls[0][2]["params"]["sysparm_query"] == "number=INC0000001^ORDERBYsys_id"
    api(monkeypatch, response(record(2)))
    with pytest.raises(KnowledgeError, match="different record"):
        client().read_record("incident", expected["sys_id"])
    for records in ([], [expected, record(2)], [record(2)]):
        api(monkeypatch, response(records))
        with pytest.raises(KnowledgeError, match="not found or was not unique"):
            client().read_record("incident", expected["number"])
    with pytest.raises(KnowledgeError):
        client().read_record("incident", "INC1^ORactive=true")


def test_create_ticket_performs_one_post_and_verifies_by_get(monkeypatch):
    calls = api(monkeypatch, response(record(), status=201), response(record()))
    result = client().create_ticket({"short_description": "VPN access", "description": "Restore access.", "caller_id": KB, "impact": "2"})
    assert result["created"] and result["verified"]
    assert result["number"] == "INC0000001"
    assert result["url"] == BASE + "/incident.do?sys_id=" + record()["sys_id"]
    assert [call[0] for call in calls] == ["POST", "GET"]
    assert calls[0][2]["json"]["impact"] == "2"


def test_create_ticket_reports_partial_success_without_replaying(monkeypatch):
    calls = api(monkeypatch, response(record(), status=201), response(status=403))
    with pytest.raises(KnowledgeError, match="created incident.*read-back failed.*Do not repeat"):
        client().create_ticket({"short_description": "VPN access"})
    assert len(calls) == 2
    api(monkeypatch, response({}, status=201))
    with pytest.raises(KnowledgeError, match="accepted the creation"):
        client().create_ticket({"short_description": "Test"})


@pytest.mark.parametrize("fields", [
    {}, {"short_description": ""}, {"short_description": "Test", "sys_id": GROUP},
    {"short_description": "Test", "description": 4},
    {"short_description": "Test", "urgency": "4"},
    {"short_description": "Test", "caller_id": "name"},
])
def test_create_ticket_rejects_bad_fields_before_network(fields):
    with pytest.raises(KnowledgeError):
        client().create_ticket(fields)


def test_registration_has_stable_scope_identity_and_secret_references(store, capsys):
    first = register(store, capsys, "--query", "active=true")
    second = register(store, capsys, "--query", "active=false")
    assert first["id"] != second["id"]
    assert first["config"]["username"] == "$env:SERVICENOW_USERNAME"
    assert first["config"]["password"] == "$env:SERVICENOW_PASSWORD"
    assert first["update_command"].endswith("--source-id " + first["id"])
    code, _, err = run(store, capsys, "add", "servicenow", "--key", "itsm", "--query", "active=true")
    assert code == 1 and "already exists" in err
    serialized = (store.root / "itsm" / "metadata.yaml").read_text()
    assert "private-password-value" not in serialized
    assert isinstance(create_source_adapter(first, store), sn.ServiceNowSource)


@pytest.mark.parametrize("args", [
    ("--password", "literal-secret"), ("--token", "literal-secret"),
    ("--token", "$sn", "--username", "user"),
    ("--limit", "0"), ("--page-size", "101"), ("--knowledge-base", KB),
    ("--field", "../bad"), ("--query", "active=true^NQactive=false"),
])
def test_registration_rejects_invalid_configuration(store, capsys, args):
    code, out, err = run(store, capsys, "add", "servicenow", "--key", "itsm", *args)
    assert code == 1 and out == ""
    assert "literal-secret" not in err
    assert store.list_collection_sources(key_name="itsm") == []


def test_bearer_credentials_and_custom_projection(store, capsys, monkeypatch):
    monkeypatch.setenv("SERVICENOW_TOKEN", "bearer-secret")
    source = register(store, capsys, "--table", "kb_knowledge", "--knowledge-base", KB, "--field", "text")
    assert source["config"]["token"] == "$env:SERVICENOW_TOKEN"
    assert "password" not in source["config"]
    assert "kb_knowledge_base" in source["config"]["fields"]
    calls = api(monkeypatch, response([record(number="KB00001", kb_knowledge_base=KB, text="<p>Article</p>")]))
    sn.ServiceNowSource(source, store).sync()
    assert calls[0][2]["auth"].token == "bearer-secret"
    assert "bearer-secret" not in (store.source_dir(source) / "source-metadata.yaml").read_text()


def test_sync_upserts_stable_ids_retains_unreturned_records_and_exports(store, capsys, monkeypatch):
    source = register(store, capsys, "--assignment-group", GROUP, "--limit", "2", "--page-size", "2")
    api(monkeypatch, response([record(), record(2)], headers={"X-Total-Count": "2"}))
    code, out, err = run(store, capsys, "sync", "servicenow", "--key", "itsm", "--source-id", source["id"])
    assert code == 0, err
    assert json.loads(out)["synced"][0]["changed"] == 2
    folder = store.source_dir(source)
    file = folder / "records" / (record()["sys_id"] + ".md")
    frontmatter, body, _ = split_frontmatter(file.read_text())
    assert frontmatter["type"] == "ServiceNow Ticket"
    assert frontmatter["generated"]["at"] == "2026-08-28T12:00:00+00:00"
    assert frontmatter["resource"].startswith(BASE)
    assert "Restore access." in body and "Support" in body
    (folder / "notes.md").write_text("# Authored notes\nKeep me.\n")
    api(monkeypatch, response([record()], headers={"X-Total-Count": "1"}))
    code, out, err = run(store, capsys, "sync", "--key", "itsm")
    assert code == 0, err
    stats = json.loads(out)["synced"][0]
    assert stats["changed"] == 0 and stats["retained"] == 1
    assert len(list((folder / "records").glob("*.md"))) == 2
    assert "Keep me." in (folder / "notes.md").read_text()
    api(monkeypatch, response([record(description="Changed description", sys_updated_on="2026-08-28 13:00:00")]))
    assert run(store, capsys, "sync", "servicenow", "--key", "itsm")[0] == 0
    assert "Changed description" in file.read_text()
    code, out, err = run(store, capsys, "browse", "servicenow", "--key", "itsm")
    assert code == 0 and len(json.loads(out)["items"]) == 3
    code, out, err = run(store, capsys, "export", "--key", "itsm")
    assert code == 0, err
    with ZipFile(json.loads(out)["archive"]) as archive:
        text = "\n".join(archive.read(name).decode() for name in archive.namelist())
    assert "$env:SERVICENOW_PASSWORD" in text
    assert "private-password-value" not in text


def test_failed_sync_does_not_replace_last_successful_files_or_metadata(store, capsys, monkeypatch):
    source = register(store, capsys, "--page-size", "1")
    api(monkeypatch, response([record()], headers={"X-Total-Count": "1"}))
    sn.ServiceNowSource(source, store).sync()
    folder = store.source_dir(source)
    snapshot = {path.relative_to(folder): path.read_bytes() for path in folder.rglob("*") if path.is_file()}
    metadata = (store.root / "itsm" / "metadata.yaml").read_bytes()
    api(monkeypatch, response([record(description="Must not publish")]), response(status=403))
    with pytest.raises(KnowledgeError):
        sn.ServiceNowSource(source, store).sync()
    assert snapshot == {path.relative_to(folder): path.read_bytes() for path in folder.rglob("*") if path.is_file()}
    assert metadata == (store.root / "itsm" / "metadata.yaml").read_bytes()
    api(monkeypatch, response([record(sys_updated_on="bad timestamp")], headers={"X-Total-Count": "1"}))
    with pytest.raises(KnowledgeError, match="timestamp"):
        sn.ServiceNowSource(source, store).sync()
    assert snapshot == {path.relative_to(folder): path.read_bytes() for path in folder.rglob("*") if path.is_file()}


def test_knowledge_articles_have_native_base_scope_and_normalized_text(store, capsys, monkeypatch):
    source = register(store, capsys, "--table", "kb_knowledge", "--knowledge-base", KB, "--query", "workflow_state=published")
    article = record(
        number="KB001001", text="<h2>Reset VPN</h2><p>First &amp; second</p><script>hidden()</script>",
        kb_knowledge_base={"value": KB, "display_value": "IT Knowledge"},
        workflow_state={"value": "published", "display_value": "Published"},
    )
    calls = api(monkeypatch, response([article]))
    result = sn.ServiceNowSource(source, store).sync()
    assert result["documents"] == 1 and not result["truncated"]
    assert calls[0][2]["params"]["sysparm_query"] == f"workflow_state=published^kb_knowledge_base={KB}^ORDERBYsys_id"
    text = (store.source_dir(source) / "records" / (article["sys_id"] + ".md")).read_text()
    frontmatter, body, _ = split_frontmatter(text)
    assert frontmatter["type"] == "ServiceNow Knowledge Article"
    assert "Reset VPN\nFirst & second" in body
    assert "hidden()" not in body.split("## Source Data")[0]
    api(monkeypatch, response([record(kb_knowledge_base=GROUP)]))
    with pytest.raises(KnowledgeError, match="outside"):
        sn.ServiceNowSource(source, store).sync()


def test_search_uses_saved_scope_and_supports_json_tv_and_preview(store, capsys, monkeypatch):
    source = register(store, capsys, "--assignment-group", GROUP, "--query", "active=true")
    for fmt in ("json", "television", "television-preview"):
        calls = api(monkeypatch, response([record()]))
        code, out, err = run(
            store, capsys, "search", "servicenow", "VPN", "--key", "itsm",
            "--source-id", source["id"], "--query", "state=1", "--format", fmt,
        )
        assert code == 0, err
        assert calls[0][2]["params"]["sysparm_query"] == f"active=true^state=1^short_descriptionLIKEVPN^assignment_group={GROUP}^ORDERBYsys_id"
        assert "INC0000001" in out
    api(monkeypatch, response([record()]))
    assert "No matching" in run(store, capsys, "search", "servicenow", "--format", "television-preview", "--entry", "INC999")[1]
    code, _, err = run(store, capsys, "search", "servicenow", "--key", "itsm", "--assignment-group", KB)
    assert code == 1 and "cannot replace" in err


def test_connection_selection_never_guesses_a_registration(store, capsys):
    first = register(store, capsys)
    register(store, capsys, "--query", "active=true")
    for args, message in [
        (("--key", "itsm"), "Multiple"),
        (("--source-id", first["id"]), "requires --key"),
        (("--key", "itsm", "--source-id", "missing"), "not found"),
        (("--key", "itsm", "--base-url", BASE), "registered connection"),
    ]:
        code, _, err = run(store, capsys, "servicenow", "read-ticket", "INC0000001", *args)
        assert code == 1 and message in err
    assert run(store, capsys, "sync", "servicenow", "--key", "itsm", "--source-id", "missing")[0] == 1
    assert run(store, capsys, "add", "servicenow", "--key", "../outside")[0] == 1


def test_ticket_cli_read_create_and_network_free_preview(store, capsys, monkeypatch, tmp_path):
    source = register(store, capsys, "--assignment-group", GROUP)
    calls = api(monkeypatch, response([record()]))
    code, out, err = run(store, capsys, "servicenow", "read-ticket", "INC0000001", "--key", "itsm")
    assert code == 0 and json.loads(out)["record"]["number"] == "INC0000001"
    assert calls[0][0] == "GET"
    description = tmp_path / "description.txt"
    description.write_text("Test description with Unicode: café", encoding="utf-8")
    calls = api(monkeypatch)
    monkeypatch.delenv("SERVICENOW_PASSWORD")
    code, out, err = run(
        store, capsys, "servicenow", "create-ticket", "--key", "itsm", "--short-description", " Test incident ",
        "--description-file", str(description), "--caller-id", KB, "--impact", "3", "--urgency", "3",
        "--correlation-id", "know-test", "--dry-run",
    )
    assert code == 0, err
    fields = json.loads(out)["fields"]
    assert fields["assignment_group"] == GROUP and fields["short_description"] == "Test incident"
    assert "café" in fields["description"] and calls == []
    monkeypatch.setenv("SERVICENOW_PASSWORD", "private-password-value")
    calls = api(monkeypatch, response(record(), status=201), response(record()))
    code, out, err = run(store, capsys, "servicenow", "create-ticket", "--short-description", "VPN access", "--description", "Details")
    assert code == 0 and json.loads(out)["verified"]
    assert [call[0] for call in calls] == ["POST", "GET"]
    assert calls[0][2]["json"]["description"] == "Details"


def test_ticket_cli_prevents_wrong_scope_or_table(store, capsys, monkeypatch):
    source = register(store, capsys, "--assignment-group", GROUP)
    api(monkeypatch, response(record(assignment_group=KB)))
    assert run(store, capsys, "servicenow", "read-ticket", record()["sys_id"], "--key", "itsm")[0] == 1
    for args in [
        ("--short-description", " ", "--dry-run"),
        ("--short-description", "Test", "--key", "itsm", "--assignment-group", KB, "--dry-run"),
    ]:
        assert run(store, capsys, "servicenow", "create-ticket", *args)[0] == 1
    code, _, err = run(store, capsys, "servicenow", "read-ticket", "INC1", "--key", "itsm", "--table", "problem")
    assert code == 1 and "must match" in err
    article_source = register(store, capsys, "--table", "kb_knowledge")
    for operation, args in [("read-ticket", ("INC1",)), ("create-ticket", ("--short-description", "Test", "--dry-run"))]:
        assert run(store, capsys, "servicenow", operation, *args, "--key", "itsm", "--source-id", article_source["id"])[0] == 1


def test_knowledge_base_discovery_and_stored_credential_resolution(store, capsys, monkeypatch):
    store.set_key("snow_bearer", "private-stored-token")
    bases = [{"sys_id": KB, "title": "IT Knowledge", "description": "Support procedures", "sys_updated_on": "2026-08-28 12:00:00"}]
    calls = api(monkeypatch, response(bases))
    code, out, err = run(store, capsys, "servicenow", "knowledge-bases", "--token", "$snow_bearer")
    assert code == 0 and json.loads(out)["records"][0]["sys_id"] == KB
    assert calls[0][1].endswith("/api/now/table/kb_knowledge_base")
    assert calls[0][2]["auth"].token == "private-stored-token"
    assert "private-stored-token" not in out
    api(monkeypatch, response(bases))
    assert "IT Knowledge" in run(store, capsys, "servicenow", "knowledge-bases", "--format", "television-preview")[1]
    assert run(store, capsys, "servicenow", "knowledge-bases", "--token", "$missing")[0] == 1
