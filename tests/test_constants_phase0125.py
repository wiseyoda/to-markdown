"""Tests for Phase 0125 constants (sanitization and parallel LLM)."""

from to_markdown.core.constants import (
    PARALLEL_LLM_MAX_CONCURRENCY,
    SANITIZE_CONTROL_CHARS,
    SANITIZE_DIRECTIONAL_CHARS,
    SANITIZE_ZERO_WIDTH_CHARS,
)


class TestSanitizeZeroWidthChars:
    """Tests for SANITIZE_ZERO_WIDTH_CHARS constant."""

    def test_is_frozenset(self) -> None:
        assert isinstance(SANITIZE_ZERO_WIDTH_CHARS, frozenset)

    def test_contains_zero_width_space(self) -> None:
        assert "\u200b" in SANITIZE_ZERO_WIDTH_CHARS

    def test_contains_bom(self) -> None:
        assert "\ufeff" in SANITIZE_ZERO_WIDTH_CHARS

    def test_contains_soft_hyphen(self) -> None:
        assert "\u00ad" in SANITIZE_ZERO_WIDTH_CHARS

    def test_contains_word_joiner(self) -> None:
        assert "\u2060" in SANITIZE_ZERO_WIDTH_CHARS

    def test_contains_all_expected_chars(self) -> None:
        expected = {
            "\u200b",
            "\u200c",
            "\u200d",
            "\ufeff",
            "\u200e",
            "\u200f",
            "\u00ad",
            "\u2060",
            "\u2061",
            "\u2062",
            "\u2063",
            "\u2064",
        }
        assert expected == SANITIZE_ZERO_WIDTH_CHARS

    def test_count(self) -> None:
        assert len(SANITIZE_ZERO_WIDTH_CHARS) == 12


class TestSanitizeControlChars:
    """Tests for SANITIZE_CONTROL_CHARS constant."""

    def test_is_frozenset(self) -> None:
        assert isinstance(SANITIZE_CONTROL_CHARS, frozenset)

    def test_contains_null(self) -> None:
        assert "\x00" in SANITIZE_CONTROL_CHARS

    def test_contains_delete(self) -> None:
        assert "\x7f" in SANITIZE_CONTROL_CHARS

    def test_excludes_tab(self) -> None:
        """Tab (0x09) should NOT be in control chars - it is valid whitespace."""
        assert "\t" not in SANITIZE_CONTROL_CHARS

    def test_excludes_newline(self) -> None:
        """Newline (0x0a) should NOT be in control chars."""
        assert "\n" not in SANITIZE_CONTROL_CHARS

    def test_excludes_carriage_return(self) -> None:
        """Carriage return (0x0d) should NOT be in control chars."""
        assert "\r" not in SANITIZE_CONTROL_CHARS

    def test_contains_backspace(self) -> None:
        assert "\x08" in SANITIZE_CONTROL_CHARS

    def test_contains_shift_out(self) -> None:
        assert "\x0e" in SANITIZE_CONTROL_CHARS

    def test_count(self) -> None:
        # 0x00-0x08 = 9 chars, 0x0e-0x1f = 18 chars, 0x7f = 1 char => 28 total
        assert len(SANITIZE_CONTROL_CHARS) == 28


class TestSanitizeDirectionalChars:
    """Tests for SANITIZE_DIRECTIONAL_CHARS constant."""

    def test_is_frozenset(self) -> None:
        assert isinstance(SANITIZE_DIRECTIONAL_CHARS, frozenset)

    def test_contains_ltr_embedding(self) -> None:
        assert "\u202a" in SANITIZE_DIRECTIONAL_CHARS

    def test_contains_rtl_embedding(self) -> None:
        assert "\u202b" in SANITIZE_DIRECTIONAL_CHARS

    def test_contains_rtl_override(self) -> None:
        """RTL override is a known security vector (bidi attack)."""
        assert "\u202e" in SANITIZE_DIRECTIONAL_CHARS

    def test_contains_all_expected_chars(self) -> None:
        expected = {
            "\u202a",
            "\u202b",
            "\u202c",
            "\u202d",
            "\u202e",
            "\u2066",
            "\u2067",
            "\u2068",
            "\u2069",
        }
        assert expected == SANITIZE_DIRECTIONAL_CHARS

    def test_count(self) -> None:
        assert len(SANITIZE_DIRECTIONAL_CHARS) == 9


class TestParallelLlmMaxConcurrency:
    """Tests for PARALLEL_LLM_MAX_CONCURRENCY constant."""

    def test_is_int(self) -> None:
        assert isinstance(PARALLEL_LLM_MAX_CONCURRENCY, int)

    def test_value(self) -> None:
        assert PARALLEL_LLM_MAX_CONCURRENCY == 5

    def test_positive(self) -> None:
        assert PARALLEL_LLM_MAX_CONCURRENCY > 0
