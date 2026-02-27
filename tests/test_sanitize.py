"""Tests for content sanitization."""

import logging

from to_markdown.core.sanitize import SanitizeResult, sanitize_content


class TestSanitizeContent:
    """Tests for sanitize_content()."""

    def test_clean_content_passes_through(self):
        """Normal text with no invisible chars is unchanged."""
        result = sanitize_content("Hello, world!")
        assert result.content == "Hello, world!"
        assert result.chars_removed == 0
        assert result.was_modified is False

    def test_empty_string(self):
        """Empty input returns empty result."""
        result = sanitize_content("")
        assert result.content == ""
        assert result.chars_removed == 0
        assert result.was_modified is False

    def test_zero_width_space_stripped(self):
        """Zero-width space (U+200B) is removed."""
        result = sanitize_content("hello\u200bworld")
        assert result.content == "helloworld"
        assert result.chars_removed == 1
        assert result.was_modified is True

    def test_zero_width_non_joiner_stripped(self):
        """Zero-width non-joiner (U+200C) is removed."""
        result = sanitize_content("ab\u200ccd")
        assert result.content == "abcd"
        assert result.chars_removed == 1

    def test_zero_width_joiner_stripped(self):
        """Zero-width joiner (U+200D) is removed."""
        result = sanitize_content("ab\u200dcd")
        assert result.content == "abcd"
        assert result.chars_removed == 1

    def test_bom_stripped(self):
        """BOM / zero-width no-break space (U+FEFF) is removed."""
        result = sanitize_content("\ufeffHello")
        assert result.content == "Hello"
        assert result.chars_removed == 1

    def test_soft_hyphen_stripped(self):
        """Soft hyphen (U+00AD) is removed."""
        result = sanitize_content("hyphen\u00adated")
        assert result.content == "hyphenated"
        assert result.chars_removed == 1

    def test_null_byte_stripped(self):
        """Null byte (U+0000) is removed."""
        result = sanitize_content("hello\x00world")
        assert result.content == "helloworld"
        assert result.chars_removed == 1

    def test_control_chars_stripped(self):
        """Control characters (U+0001-U+0008) are removed."""
        result = sanitize_content("a\x01b\x02c\x07d")
        assert result.content == "abcd"
        assert result.chars_removed == 3

    def test_shift_out_through_unit_separator_stripped(self):
        """Control chars U+000E-U+001F are removed."""
        result = sanitize_content("a\x0eb\x1fc")
        assert result.content == "abc"
        assert result.chars_removed == 2

    def test_delete_char_stripped(self):
        """DEL character (U+007F) is removed."""
        result = sanitize_content("hello\x7fworld")
        assert result.content == "helloworld"
        assert result.chars_removed == 1

    def test_rtl_ltr_overrides_stripped(self):
        """Bidirectional override chars (U+202A-U+202E) are removed."""
        result = sanitize_content("hello\u202aworld\u202e!")
        assert result.content == "helloworld!"
        assert result.chars_removed == 2

    def test_directional_isolates_stripped(self):
        """Directional isolate chars (U+2066-U+2069) are removed."""
        result = sanitize_content("a\u2066b\u2067c\u2068d\u2069e")
        assert result.content == "abcde"
        assert result.chars_removed == 4

    def test_normal_whitespace_preserved(self):
        """Spaces, tabs, newlines, and carriage returns are NOT stripped."""
        text = "hello world\tmore\nlines\r\nhere"
        result = sanitize_content(text)
        assert result.content == text
        assert result.chars_removed == 0
        assert result.was_modified is False

    def test_mixed_visible_and_invisible(self):
        """Mixed content: visible chars preserved, invisible stripped."""
        result = sanitize_content("Hello\u200b \u202aWorld\x00!")
        assert result.content == "Hello World!"
        assert result.chars_removed == 3
        assert result.was_modified is True

    def test_unicode_letters_preserved(self):
        """Unicode letters (accented, CJK, etc.) are preserved."""
        text = "caf\u00e9 r\u00e9sum\u00e9 \u65e5\u672c\u8a9e \ud55c\uad6d\uc5b4"
        result = sanitize_content(text)
        assert result.content == text
        assert result.chars_removed == 0

    def test_emoji_preserved(self):
        """Emoji characters are preserved."""
        text = "Hello \U0001f30d\U0001f389 World"
        result = sanitize_content(text)
        assert result.content == text
        assert result.chars_removed == 0

    def test_chars_removed_count_accurate(self):
        """Removal count matches actual chars removed."""
        # 5 invisible chars scattered in text
        text = "\u200bhello\u200c\u200d world\u202a\ufeff"
        result = sanitize_content(text)
        assert result.content == "hello world"
        assert result.chars_removed == 5

    def test_all_invisible_content(self):
        """String of only invisible chars becomes empty."""
        text = "\u200b\u200c\u200d\ufeff\x00\x01\u202a"
        result = sanitize_content(text)
        assert result.content == ""
        assert result.chars_removed == 7
        assert result.was_modified is True

    def test_result_is_frozen_dataclass(self):
        """SanitizeResult is immutable."""
        result = sanitize_content("test")
        assert isinstance(result, SanitizeResult)
        # Frozen dataclass should raise on attribute assignment
        try:
            result.content = "changed"  # type: ignore[misc]
            msg = "Should have raised"
            raise AssertionError(msg)
        except AttributeError:
            pass

    def test_info_log_when_chars_removed(self, caplog):
        """INFO log emitted when characters are stripped."""
        with caplog.at_level(logging.INFO):
            sanitize_content("hello\u200bworld")
        assert "Sanitized: removed 1 non-visible characters" in caplog.text

    def test_no_log_when_clean(self, caplog):
        """No log when content has no invisible chars."""
        with caplog.at_level(logging.INFO):
            sanitize_content("clean text")
        assert "Sanitized" not in caplog.text
