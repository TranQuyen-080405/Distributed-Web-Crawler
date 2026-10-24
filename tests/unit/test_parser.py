from crawler.parser import parse


def test_parse_title_text_and_links():
    html = (
        "<html><head><title>Hi</title></head>"
        "<body><a href='/a'>A</a><a href='https://other.test/b#x'>B</a></body></html>"
    )
    title, content, links = parse(html, "https://example.com/start")
    assert title == "Hi"
    assert "A" in content
    assert links == ["https://example.com/a", "https://other.test/b"]
