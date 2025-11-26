"""Smoke tests for bundled template library (Sprint 3.1).

These tests catch obvious template breakage by validating that all bundled
templates exist, load correctly, have required sections, and have valid metadata.

Fast tests that run in < 1 second with no LLM calls.
"""

import pytest
from doc_evergreen.template_registry import TemplateRegistry


# All 9 bundled templates (Sprint 2 complete)
BUNDLED_TEMPLATES = [
    "tutorial-quickstart",
    "tutorial-first-template",
    "howto-custom-prompts",
    "howto-ci-integration",
    "howto-contributing-guide",
    "explanation-concepts",
    "explanation-architecture",
    "reference-api",
    "reference-cli",
]


class TestTemplateLibrarySmoke:
    """Smoke tests for bundled template library."""

    @pytest.mark.parametrize("template_name", BUNDLED_TEMPLATES)
    def test_template_exists_and_loads(self, template_name):
        """Each template file exists and can be loaded as valid JSON."""
        registry = TemplateRegistry()
        
        # Load template using registry
        template = registry.load_template(template_name)
        
        # Verify template loaded successfully
        assert template is not None
        assert template.template is not None
        assert template.template.document is not None
        assert template.template.document.title is not None

    @pytest.mark.parametrize("template_name", BUNDLED_TEMPLATES)
    def test_template_has_sections(self, template_name):
        """Each template has at least one section defined."""
        registry = TemplateRegistry()
        template = registry.load_template(template_name)
        
        sections = template.template.document.sections
        assert len(sections) > 0, f"{template_name} has no sections"
        
        # Each section has required fields
        for i, section in enumerate(sections):
            assert section.heading, f"{template_name} section {i} missing heading"
            assert section.prompt, f"{template_name} section {i} missing prompt"
            assert len(section.sources) > 0, f"{template_name} section {i} has no sources"

    @pytest.mark.parametrize("template_name", BUNDLED_TEMPLATES)
    def test_template_metadata_valid(self, template_name):
        """Each template has valid metadata."""
        registry = TemplateRegistry()
        template = registry.load_template(template_name)
        
        # Verify metadata fields exist and are non-empty
        assert template.meta.name == template_name
        assert template.meta.description, f"{template_name} missing description"
        assert template.meta.use_case, f"{template_name} missing use_case"
        assert template.meta.quadrant in ["tutorial", "howto", "reference", "explanation"], \
            f"{template_name} has invalid quadrant: {template.meta.quadrant}"
        assert template.meta.estimated_lines, f"{template_name} missing estimated_lines"

    def test_all_bundled_templates_registered(self):
        """Ensure template registry includes all 9 bundled templates."""
        registry = TemplateRegistry()
        templates = registry.list_templates()
        template_names = {t.name for t in templates}
        
        expected_templates = set(BUNDLED_TEMPLATES)
        
        # All expected templates are registered
        missing = expected_templates - template_names
        assert expected_templates.issubset(template_names), \
            f"Missing templates: {missing}"
        
        # Verify we have exactly 9 templates (no extras)
        assert len(template_names) == 9, \
            f"Expected 9 templates, found {len(template_names)}: {template_names}"
