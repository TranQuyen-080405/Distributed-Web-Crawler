from common.url_utils import normalize_url


def test_normalize_canonical_form():
    assert (
        normalize_url("HTTPS://Example.COM:443/a/?b=2&a=1#frag")
        == "https://example.com/a?a=1&b=2"
    )


def test_normalize_relative_and_reject():
    assert normalize_url("../b", "https://example.com/a/c") == "https://example.com/b"
    assert normalize_url("mailto:a@b.c") is None
