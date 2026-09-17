import pytest

from privilege_scrubber.scrubber import (
    redact_known_entities,
    redact_pii,
    scrub,
    strip_privilege_markers,
    unscrub,
)


class TestStripPrivilegeMarkers:
    def test_strips_privileged_and_confidential_header(self):
        text = "PRIVILEGED AND CONFIDENTIAL\n\nDear team,\n\nSee attached draft."
        assert strip_privilege_markers(text) == "Dear team,\n\nSee attached draft."

    def test_strips_dashed_attorney_work_product_variant(self):
        text = "--- ATTORNEY WORK PRODUCT ---\n\nBody text here."
        assert strip_privilege_markers(text) == "Body text here."

    def test_strips_attorney_client_privileged_communication_and_collapses_blank_line(self):
        text = (
            "Header line.\n\n"
            "ATTORNEY-CLIENT PRIVILEGED COMMUNICATION\n\n"
            "Body line."
        )
        assert strip_privilege_markers(text) == "Header line.\n\nBody line."


class TestRedactPii:
    def test_redacts_email(self):
        result = redact_pii("Contact jane.doe@example.com for details.")
        assert result.scrubbed_text == "Contact [REDACTED_EMAIL_1] for details."
        assert result.mapping == {"[REDACTED_EMAIL_1]": "jane.doe@example.com"}

    def test_redacts_phone_common_formats(self):
        text = "Call (555) 123-4567 or 555-987-6543 or 555.222.3333."
        result = redact_pii(text)
        assert result.scrubbed_text == (
            "Call [REDACTED_PHONE_1] or [REDACTED_PHONE_2] or [REDACTED_PHONE_3]."
        )
        assert result.mapping == {
            "[REDACTED_PHONE_1]": "(555) 123-4567",
            "[REDACTED_PHONE_2]": "555-987-6543",
            "[REDACTED_PHONE_3]": "555.222.3333",
        }

    def test_redacts_ssn(self):
        result = redact_pii("SSN on file: 123-45-6789.")
        assert result.scrubbed_text == "SSN on file: [REDACTED_SSN_1]."
        assert result.mapping == {"[REDACTED_SSN_1]": "123-45-6789"}

    def test_multiple_categories_redacted_together_with_repeat_reuse(self):
        text = (
            "Reach Jane at jane.doe@example.com or (555) 123-4567. "
            "Her SSN is 123-45-6789. Confirm again at jane.doe@example.com."
        )
        result = redact_pii(text)
        assert result.scrubbed_text == (
            "Reach Jane at [REDACTED_EMAIL_1] or [REDACTED_PHONE_1]. "
            "Her SSN is [REDACTED_SSN_1]. Confirm again at [REDACTED_EMAIL_1]."
        )
        assert result.mapping == {
            "[REDACTED_EMAIL_1]": "jane.doe@example.com",
            "[REDACTED_PHONE_1]": "(555) 123-4567",
            "[REDACTED_SSN_1]": "123-45-6789",
        }


class TestRedactKnownEntities:
    def test_stable_numbering_and_case_insensitive_repeat(self, known_entities):
        text = "Marcus Whitfield met with Elena Rodriguez. MARCUS WHITFIELD took notes afterward."
        result = redact_known_entities(text, known_entities)
        assert result.scrubbed_text == (
            "[REDACTED_PERSON_1] met with [REDACTED_PERSON_2]. "
            "[REDACTED_PERSON_1] took notes afterward."
        )
        assert result.mapping == {
            "[REDACTED_PERSON_1]": "Marcus Whitfield",
            "[REDACTED_PERSON_2]": "Elena Rodriguez",
        }

    def test_longer_name_matched_before_shorter_prefix(self, known_entities):
        text = "Jane Doe-Smith signed the NDA. Later, Jane Doe called to confirm."
        result = redact_known_entities(text, known_entities)
        assert result.scrubbed_text == (
            "[REDACTED_PERSON_1] signed the NDA. Later, [REDACTED_PERSON_2] called to confirm."
        )
        assert result.mapping == {
            "[REDACTED_PERSON_1]": "Jane Doe-Smith",
            "[REDACTED_PERSON_2]": "Jane Doe",
        }

    def test_word_boundary_prevents_partial_match(self, known_entities):
        text = "Grant Sable approved the plan. Grant Sableton, a vendor, was not involved."
        result = redact_known_entities(text, known_entities)
        assert result.scrubbed_text == (
            "[REDACTED_PERSON_1] approved the plan. Grant Sableton, a vendor, was not involved."
        )
        assert result.mapping == {"[REDACTED_PERSON_1]": "Grant Sable"}


class TestScrub:
    def test_combines_privilege_stripping_entity_and_pii_redaction(self, known_entities):
        text = (
            "PRIVILEGED AND CONFIDENTIAL\n"
            "\n"
            "To: Jane Doe-Smith\n"
            "From: Marcus Whitfield\n"
            "\n"
            "Jane Doe called this morning to discuss the settlement. Her email is "
            "jane.doe@example.com and her cell is (555) 123-4567. Elena Rodriguez "
            "confirmed the SSN on file is 123-45-6789 for verification purposes.\n"
            "\n"
            "Grant Sable will follow up. Please do not contact Grant Sableton, an "
            "unrelated vendor, about this matter.\n"
            "\n"
            "ATTORNEY WORK PRODUCT"
        )
        result = scrub(text, known_entities)
        assert result.scrubbed_text == (
            "To: [REDACTED_PERSON_1]\n"
            "From: [REDACTED_PERSON_2]\n"
            "\n"
            "[REDACTED_PERSON_3] called this morning to discuss the settlement. Her email is "
            "[REDACTED_EMAIL_1] and her cell is [REDACTED_PHONE_1]. [REDACTED_PERSON_4] "
            "confirmed the SSN on file is [REDACTED_SSN_1] for verification purposes.\n"
            "\n"
            "[REDACTED_PERSON_5] will follow up. Please do not contact Grant Sableton, an "
            "unrelated vendor, about this matter."
        )
        assert result.mapping == {
            "[REDACTED_PERSON_1]": "Jane Doe-Smith",
            "[REDACTED_PERSON_2]": "Marcus Whitfield",
            "[REDACTED_PERSON_3]": "Jane Doe",
            "[REDACTED_PERSON_4]": "Elena Rodriguez",
            "[REDACTED_PERSON_5]": "Grant Sable",
            "[REDACTED_EMAIL_1]": "jane.doe@example.com",
            "[REDACTED_PHONE_1]": "(555) 123-4567",
            "[REDACTED_SSN_1]": "123-45-6789",
        }

    def test_ordinary_text_passes_through_completely_unredacted(self, known_entities):
        text = "Please review the attached zoning ordinance by end of week."
        result = scrub(text, known_entities)
        assert result.scrubbed_text == text
        assert result.mapping == {}


class TestUnscrub:
    def test_reverses_placeholder_mapping(self):
        mapping = {
            "[REDACTED_PERSON_1]": "Jane Doe",
            "[REDACTED_EMAIL_1]": "jane.doe@example.com",
        }
        text = "[REDACTED_PERSON_1] can be reached at [REDACTED_EMAIL_1]."
        assert unscrub(text, mapping) == "Jane Doe can be reached at jane.doe@example.com."


class TestRoundTrip:
    def test_scrub_then_unscrub_reconstructs_original_minus_privilege_markers(self, known_entities):
        original = (
            "PRIVILEGED AND CONFIDENTIAL\n"
            "\n"
            "To: Jane Doe-Smith\n"
            "From: Marcus Whitfield\n"
            "\n"
            "Jane Doe called this morning to discuss the settlement. Her email is "
            "jane.doe@example.com and her cell is (555) 123-4567. Elena Rodriguez "
            "confirmed the SSN on file is 123-45-6789 for verification purposes.\n"
            "\n"
            "Grant Sable will follow up. Please do not contact Grant Sableton, an "
            "unrelated vendor, about this matter.\n"
            "\n"
            "ATTORNEY WORK PRODUCT"
        )
        result = scrub(original, known_entities)
        restored = unscrub(result.scrubbed_text, result.mapping)
        assert restored == strip_privilege_markers(original)

    def test_round_trip_on_plain_text_with_nothing_to_redact(self, known_entities):
        text = "The parties agree to keep the meeting time flexible next week."
        result = scrub(text, known_entities)
        assert unscrub(result.scrubbed_text, result.mapping) == text
