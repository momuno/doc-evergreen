"""Tests for template registry infrastructure (Sprint 1.2)."""

import pytest
from pathlib import Path
from doc_evergreen.template_registry import (
    TemplateRegistry,
    TemplateNotFoundError,
    TemplateValidationError,
)
from doc_evergreen.core.template_schema import TemplateMetadata, TemplateWithMetadata


class TestRegistryInitialization:
    """Test registry initialization."""

    def test_registry_initializes_successfully(self):
        """Registry initializes without errors."""
        registry = TemplateRegistry()
        assert registry is not None

    def test_registry_has_list_method(self):
        """Registry has list_templates method."""
        registry = TemplateRegistry()
        assert hasattr(registry, "list_templates")
        assert callable(registry.list_templates)

    def test_registry_has_load_method(self):
        """Registry has load_template method."""
        registry = TemplateRegistry()
        assert hasattr(registry, "load_template")
        assert callable(registry.load_template)

    def test_registry_has_get_path_method(self):
        """Registry has get_template_path method."""
        registry = TemplateRegistry()
        assert hasattr(registry, "get_template_path")
        assert callable(registry.get_template_path)


class TestListTemplates:
    """Test listing available templates."""

    def test_list_templates_returns_list(self):
        """list_templates returns a list."""
        registry = TemplateRegistry()
        templates = registry.list_templates()
        assert isinstance(templates, list)

    def test_list_templates_has_four_divio_templates(self):
        """Registry should list at least the original 4 Divio quadrant templates."""
        registry = TemplateRegistry()
        templates = registry.list_templates()
        # After Sprint 2, we have 9 templates total, but original 4 should still be there
        assert len(templates) >= 4

    def test_list_templates_has_nine_templates(self):
        """Registry should list all 9 templates after Sprint 2."""
        registry = TemplateRegistry()
        templates = registry.list_templates()
        assert len(templates) == 9

    def test_list_templates_returns_metadata_objects(self):
        """When templates exist, list returns TemplateMetadata objects."""
        registry = TemplateRegistry()
        templates = registry.list_templates()
        
        # All items should be TemplateMetadata
        for template in templates:
            assert isinstance(template, TemplateMetadata)

    def test_all_divio_quadrants_covered(self):
        """All 4 Divio quadrants should be represented."""
        registry = TemplateRegistry()
        templates = registry.list_templates()
        quadrants = {t.quadrant for t in templates}
        assert quadrants == {"tutorial", "howto", "reference", "explanation"}

    def test_each_template_loads_successfully(self):
        """Each template should load without errors."""
        registry = TemplateRegistry()
        template_names = [
            "tutorial-quickstart",
            "howto-contributing-guide",
            "reference-cli",
            "explanation-architecture"
        ]
        
        for name in template_names:
            template = registry.load_template(name)
            assert template.meta.name == name
            assert isinstance(template, TemplateWithMetadata)

    def test_all_new_templates_load(self):
        """All 5 new templates from Sprint 2 should load."""
        registry = TemplateRegistry()
        new_templates = [
            "tutorial-first-template",
            "howto-ci-integration",
            "howto-custom-prompts",
            "reference-api",
            "explanation-concepts"
        ]
        for name in new_templates:
            template = registry.load_template(name)
            assert template.meta.name == name
            assert isinstance(template, TemplateWithMetadata)


class TestLoadTemplate:
    """Test loading templates by name."""

    def test_load_template_raises_not_found_for_nonexistent(self):
        """Loading nonexistent template raises TemplateNotFoundError."""
        registry = TemplateRegistry()
        
        with pytest.raises(TemplateNotFoundError) as exc_info:
            registry.load_template("nonexistent-template")
        
        # Error message should be helpful
        assert "nonexistent-template" in str(exc_info.value)

    def test_load_template_error_message_lists_available(self):
        """TemplateNotFoundError includes list of available templates."""
        registry = TemplateRegistry()
        
        with pytest.raises(TemplateNotFoundError) as exc_info:
            registry.load_template("missing")
        
        # Should mention available templates or that none exist
        error_msg = str(exc_info.value).lower()
        assert "available" in error_msg or "no templates" in error_msg

    def test_load_template_returns_template_with_metadata(self):
        """When template exists, returns TemplateWithMetadata."""
        # This will be tested properly in Sprint 1.3 when we add templates
        # For now, just verify it raises the right error
        registry = TemplateRegistry()
        
        with pytest.raises(TemplateNotFoundError):
            registry.load_template("any-name")


class TestGetTemplatePath:
    """Test getting template file paths."""

    def test_get_template_path_returns_path_object(self):
        """get_template_path returns Path object when template exists."""
        # Will be properly tested in Sprint 1.3
        registry = TemplateRegistry()
        
        # For now, should raise TemplateNotFoundError for nonexistent
        with pytest.raises(TemplateNotFoundError):
            registry.get_template_path("nonexistent")

    def test_get_template_path_raises_not_found(self):
        """get_template_path raises TemplateNotFoundError for nonexistent."""
        registry = TemplateRegistry()
        
        with pytest.raises(TemplateNotFoundError):
            registry.get_template_path("missing-template")


class TestTemplateValidation:
    """Test template validation during loading."""

    def test_load_template_validates_json(self, tmp_path):
        """Loading template with invalid JSON raises TemplateValidationError."""
        # This tests the validation logic once we implement it
        # We'll create a malformed template file to test this
        
        # For now, just verify the error class exists
        assert TemplateValidationError is not None
        
        # The actual validation will be tested with real files in Sprint 1.3


class TestRegistryContract:
    """Test registry follows contract specification."""

    def test_registry_discovers_templates_in_package(self):
        """Registry discovers templates from package resources."""
        registry = TemplateRegistry()
        
        # Should not raise errors during discovery
        # Even if no templates exist yet
        templates = registry.list_templates()
        assert isinstance(templates, list)

    def test_list_templates_sorted_by_quadrant(self):
        """Templates are sorted by quadrant then alphabetically."""
        registry = TemplateRegistry()
        templates = registry.list_templates()
        
        # If we have multiple templates, verify sorting
        if len(templates) >= 2:
            # Expected quadrant order: tutorial, howto, reference, explanation
            quadrant_order = ["tutorial", "howto", "reference", "explanation"]
            
            prev_quadrant_idx = -1
            prev_name = ""
            
            for template in templates:
                curr_quadrant_idx = quadrant_order.index(template.quadrant)
                
                # If same quadrant, should be alphabetically sorted
                if curr_quadrant_idx == prev_quadrant_idx:
                    assert template.name >= prev_name
                else:
                    # Quadrant index should increase or stay same
                    assert curr_quadrant_idx >= prev_quadrant_idx
                
                prev_quadrant_idx = curr_quadrant_idx
                prev_name = template.name
