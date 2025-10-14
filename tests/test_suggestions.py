from bot.suggestion_generator import SuggestionGenerator


def test_render_unknown_category_includes_title():
    gen = SuggestionGenerator(suggestions_path=None)
    body = gen.render("non-existent", matches=["error: something"], confidence=0.42)
    assert "## non-existent" in body or "Build failed" in body


def test_render_includes_confidence_when_provided():
    gen = SuggestionGenerator(suggestions_path=None)
    body = gen.render("timeout", matches=None, confidence=0.9)
    assert "Confidence:" in body 