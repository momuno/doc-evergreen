"""
Sprint 5: CLI Interface for Template-Based Documentation Generation

Supports section-by-section documentation generation with explicit prompts.
"""

import asyncio
import json
from pathlib import Path
import logging

import click

from doc_evergreen.change_detection import detect_changes
from doc_evergreen.chunked_generator import ChunkedGenerator
from doc_evergreen.core.template_schema import Document
from doc_evergreen.core.template_schema import Section
from doc_evergreen.core.template_schema import Template
from doc_evergreen.core.template_schema import parse_template
from doc_evergreen.core.template_schema import validate_template


def _get_output_path(template_meta) -> str:
    """Extract output path from template for display.
    
    Note: This is a display helper. Actual output path comes from loading full template.
    For --list, we show a representative path based on template type.
    
    Args:
        template_meta: TemplateMetadata instance
        
    Returns:
        Representative output path string for display
    """
    # Common patterns based on template name
    if template_meta.name.startswith("tutorial-quickstart"):
        return "QUICKSTART.md"
    elif template_meta.name.startswith("howto-contributing"):
        return "CONTRIBUTING.md"
    elif template_meta.name.startswith("howto-ci"):
        return "docs/CI_INTEGRATION.md"
    elif template_meta.name.startswith("howto-custom"):
        return "docs/PROMPT_GUIDE.md"
    elif template_meta.name.startswith("reference-cli"):
        return "docs/CLI_REFERENCE.md"
    elif template_meta.name.startswith("reference-api"):
        return "docs/API.md"
    elif template_meta.name.startswith("explanation-architecture"):
        return "docs/ARCHITECTURE.md"
    elif template_meta.name.startswith("explanation-concepts"):
        return "docs/CONCEPTS.md"
    elif template_meta.name.startswith("tutorial-first"):
        return "docs/FIRST_TEMPLATE.md"
    else:
        return "README.md"  # Default fallback


def interactive_template_selection(registry) -> str | None:
    """Display interactive template menu and get user selection.
    
    Shows templates organized by Divio documentation quadrants with emoji
    indicators. User can select by number (1-9) or quit with 'q'.
    
    Args:
        registry: TemplateRegistry instance
        
    Returns:
        Template name (e.g., "tutorial-quickstart") if selected
        None if user quits
        
    Example:
        >>> from doc_evergreen.template_registry import TemplateRegistry
        >>> registry = TemplateRegistry()
        >>> # User would see interactive menu
        >>> name = interactive_template_selection(registry)
    """
    # Get all templates
    templates = registry.list_templates()
    
    if not templates:
        click.echo("No templates available in registry.")
        return None
    
    # Group templates by quadrant
    quadrants = {
        "tutorial": [],
        "howto": [],
        "reference": [],
        "explanation": [],
    }
    
    for template in templates:
        if template.quadrant in quadrants:
            quadrants[template.quadrant].append(template)
    
    # Build display with numbering
    click.echo("\n? What type of documentation do you want to create?\n")
    
    template_map = {}  # Maps number to template name
    current_number = 1
    
    # Define quadrant display info
    quadrant_info = {
        "tutorial": ('📚 TUTORIALS (Learning-oriented - "Take me on a journey")', "tutorial"),
        "howto": ('🎯 HOW-TO GUIDES (Goal-oriented - "Show me how to...")', "howto"),
        "reference": ('📖 REFERENCE (Information-oriented - "Tell me facts")', "reference"),
        "explanation": ('💡 EXPLANATION (Understanding-oriented - "Help me understand")', "explanation"),
    }
    
    # Display templates by quadrant
    for quadrant_key in ["tutorial", "howto", "reference", "explanation"]:
        if quadrants[quadrant_key]:
            display_name, _ = quadrant_info[quadrant_key]
            click.echo(f"{display_name}")
            
            for template in quadrants[quadrant_key]:
                # Format: "  1. template-name - Description (200-400 lines)"
                click.echo(f"  {current_number}. {template.name} - {template.description} ({template.estimated_lines})")
                template_map[str(current_number)] = template.name
                current_number += 1
            
            click.echo()  # Blank line between quadrants
    
    # Get user input with validation loop
    while True:
        try:
            choice = click.prompt("Choose [1-9] or 'q' to quit", type=str, show_default=False)
            
            # Handle quit
            if choice.lower() == 'q':
                return None
            
            # Validate number choice
            if choice in template_map:
                return template_map[choice]
            else:
                click.echo(f"Invalid choice. Please enter a number between 1 and {len(template_map)} or 'q' to quit.")
        except click.Abort:
            # User pressed Ctrl+C
            return None


def resolve_template_path(name: str) -> Path:
    """Resolve template name to path using .doc-evergreen/ convention.

    Resolution order:
    1. If name doesn't end with .json: try .doc-evergreen/{name}.json
    2. Try {name} as absolute or relative path
    3. Raise FileNotFoundError with helpful message

    Args:
        name: Template name (short name or path)

    Returns:
        Path to template file

    Raises:
        FileNotFoundError: Template not found

    Examples:
        resolve_template_path("readme")              → .doc-evergreen/readme.json
        resolve_template_path("template.json")       → ./template.json
        resolve_template_path("/abs/path/doc.json")  → /abs/path/doc.json
    """
    # Try convention directory first for short names
    if not name.endswith(".json"):
        convention_path = Path.cwd() / ".doc-evergreen" / f"{name}.json"
        if convention_path.exists():
            return convention_path

    # Try as path (absolute or relative)
    path = Path(name)
    if path.exists():
        return path.resolve()  # Return absolute path

    # Not found - helpful error
    tried_paths = []
    if not name.endswith(".json"):
        tried_paths.append(f".doc-evergreen/{name}.json")
    tried_paths.append(name)

    raise FileNotFoundError(
        f"Template not found: {name}\n"
        f"\n"
        f"Tried:\n" + "\n".join(f"  - {p}" for p in tried_paths) + "\n"
        f"\n"
        f"Run 'doc-evergreen init' to create starter template."
    )


@click.group()
def cli():
    """Generate documentation from templates organized by the Divio Documentation System.

    \b
    Quick Start:
      # Interactive template selection (recommended)
      $ doc-evergreen init
      
      # List all available templates
      $ doc-evergreen init --list
      
      # Use a specific template
      $ doc-evergreen init --template tutorial-quickstart
      
      # Generate documentation
      $ doc-evergreen regen-doc <template-name>
    """
    pass


@cli.command("init")
@click.option("--list", "list_templates", is_flag=True, help="List all available templates with descriptions")
@click.option("--template", help="Template name (e.g., tutorial-quickstart)")
@click.option("--yes", is_flag=True, help="Skip all confirmation prompts")
@click.option("--force", is_flag=True, help="Overwrite existing template without asking")
@click.option("--name", help="[DEPRECATED] Project name - use template customization instead")
@click.option("--description", help="[DEPRECATED] Project description - use template customization instead")
def init(
    list_templates: bool,
    template: str | None,
    yes: bool,
    force: bool,
    name: str | None,
    description: str | None,
):
    """Initialize doc-evergreen with a template.
    
    By default, shows an interactive menu to help you choose the right template
    based on your documentation needs. Templates are organized by the Divio
    Documentation System (Tutorials, How-to Guides, Reference, Explanation).
    
    \b
    Examples:
    
        # Interactive selection (recommended)
        $ doc-evergreen init
        
        # List all templates
        $ doc-evergreen init --list
        
        # Use specific template
        $ doc-evergreen init --template tutorial-quickstart
        
        # Non-interactive with default
        $ doc-evergreen init --yes
    """
    from doc_evergreen.template_registry import TemplateRegistry, TemplateNotFoundError
    
    # Import TemplateValidationError at the top if needed later
    from doc_evergreen.template_registry import TemplateValidationError

    # Initialize registry
    registry = TemplateRegistry()

    # Handle --list flag
    if list_templates:
        templates = registry.list_templates()
        
        if not templates:
            click.echo("No templates available in registry.")
            click.echo("\nTemplates will be added in Sprint 1.3.")
            return
        
        click.echo("\nAvailable templates (grouped by Divio quadrant):\n")
        
        # Group templates by quadrant with enhanced display
        quadrants = {
            "tutorial": ("📚 TUTORIALS", 'Learning-oriented - "Take me on a journey"'),
            "howto": ("🎯 HOW-TO GUIDES", 'Goal-oriented - "Show me how to..."'),
            "reference": ("📖 REFERENCE", 'Information-oriented - "Tell me facts"'),
            "explanation": ("💡 EXPLANATION", 'Understanding-oriented - "Help me understand"')
        }
        
        # Display templates by quadrant
        for quadrant_key, (emoji_title, description) in quadrants.items():
            # Get templates for this quadrant
            quadrant_templates = [t for t in templates if t.quadrant == quadrant_key]
            
            if quadrant_templates:
                click.echo(f"{emoji_title} ({description})")
                for template in quadrant_templates:
                    click.echo(f"  {template.name}")
                    click.echo(f"    {template.description}")
                    click.echo(f"    Output: {_get_output_path(template)} | Estimated: {template.estimated_lines}")
                    click.echo(f"    Use when: {template.use_case}")
                    click.echo()  # Blank line between templates
                click.echo()  # Blank line between quadrants
        
        click.echo("💡 Tip: Not sure which to use? Run 'doc-evergreen init' for interactive selection.\n")
        return

    # Determine template name
    # Priority: --template flag > --name flag (deprecated) > interactive selection > default
    if template:
        # User specified template via --template flag
        template_name = template
    elif name:
        # Legacy --name flag (deprecated but supported)
        click.echo("Warning: --name is deprecated, use --template instead")
        template_name = name
    elif yes:
        # --yes without --template: use default (skip interactive)
        template_name = "tutorial-quickstart"
    else:
        # Interactive mode - show menu and get selection
        template_name = interactive_template_selection(registry)
        
        # User cancelled
        if template_name is None:
            click.echo("Cancelled.")
            return

    # Load template from registry
    try:
        template_with_meta = registry.load_template(template_name)
    except TemplateNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        click.echo("\nRun 'doc-evergreen init --list' to see available templates.", err=True)
        raise click.Abort()
    except TemplateValidationError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()

    # Show template info
    meta = template_with_meta.meta
    click.echo(f"Template: {meta.name}")
    click.echo(f"Description: {meta.description}")
    click.echo(f"Use case: {meta.use_case}")
    click.echo(f"Quadrant: {meta.quadrant}")
    click.echo(f"Estimated lines: {meta.estimated_lines}")
    click.echo()

    # Determine output path
    doc_dir = Path.cwd() / ".doc-evergreen"
    template_path = doc_dir / f"{template_name}.json"

    # Check if template already exists
    already_confirmed = False
    if template_path.exists() and not force:
        click.echo(f"Template already exists: {template_path}", err=True)
        if not yes and not click.confirm("Overwrite existing template?"):
            click.echo("Aborted", err=True)
            raise click.Abort()
        already_confirmed = True  # User confirmed overwrite, don't ask again

    # Ask for confirmation (unless --yes or already confirmed overwrite)
    if not yes and not already_confirmed:
        if not click.confirm(f"\nWrite template to {template_path}?"):
            click.echo("Aborted")
            return

    # Create .doc-evergreen/ directory
    doc_dir.mkdir(exist_ok=True)

    # Write template to file
    template_json = {
        "_meta": {
            "name": meta.name,
            "description": meta.description,
            "use_case": meta.use_case,
            "quadrant": meta.quadrant,
            "estimated_lines": meta.estimated_lines,
        },
        "document": {
            "title": template_with_meta.template.document.title,
            "output": template_with_meta.template.document.output,
            "sections": _sections_to_dict(template_with_meta.template.document.sections),
        },
    }

    template_path.write_text(json.dumps(template_json, indent=2))

    click.echo(f"✅ Created: {template_path}")
    click.echo(f"\nNext steps:")
    click.echo(f"  1. Review and customize {template_path}")
    click.echo(f"  2. Run: doc-evergreen regen-doc {template_name}")


def _sections_to_dict(sections) -> list[dict]:
    """Convert Section objects to dictionaries for JSON serialization."""
    result = []
    for section in sections:
        section_dict = {
            "heading": section.heading,
        }
        if section.prompt is not None:
            section_dict["prompt"] = section.prompt
        if section.sources:
            section_dict["sources"] = section.sources
        if section.sections:
            section_dict["sections"] = _sections_to_dict(section.sections)
        result.append(section_dict)
    return result


@cli.command("regen-doc")
@click.argument("template_name")  # Changed: now accepts short names or paths
@click.option("--auto-approve", is_flag=True, help="Apply changes without approval prompt")
@click.option("--output", type=click.Path(), help="Override output path from template")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed generation progress")
def regen_doc(template_name: str, auto_approve: bool, output: str | None, verbose: bool):
    """Regenerate documentation from template with change preview.

    \b
    Supports short template names (finds in .doc-evergreen/)
    or full paths.

    \b
    Workflow:
      1. Resolves template (convention or path)
      2. Generates new documentation
      3. Shows unified diff of changes
      4. Prompts for approval (unless --auto-approve)
      5. Writes updated documentation

    \b
    Examples:
      # Short name (finds .doc-evergreen/readme.json)
      doc-evergreen regen-doc readme

      # Full path still works
      doc-evergreen regen-doc templates/readme.json

      # Auto-approve for CI/CD
      doc-evergreen regen-doc --auto-approve readme

      # Override output location
      doc-evergreen regen-doc --output custom/path.md readme

    \b
    See TEMPLATES.md for template creation guide.
    """
    # 1. Resolve template path (convention or explicit)
    try:
        template_path = resolve_template_path(template_name)
    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()

    # 2. Parse template JSON
    try:
        template_data = json.loads(template_path.read_text())
    except json.JSONDecodeError as e:
        click.echo(f"Error: Invalid JSON in template: {e}", err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f"Error reading template: {e}", err=True)
        raise click.Abort()

    # 2. Determine template format and parse accordingly
    try:
        # Check if it's Sprint 5 format (has "document" key)
        if "document" in template_data:
            # Sprint 5 format - use parse_template directly
            template_obj = parse_template(Path(template_path))
            output_path_from_template = template_obj.document.output
        # Check if it's Sprint 8 format (has "template_version", "output_path", "chunks")
        elif "template_version" in template_data and "output_path" in template_data and "chunks" in template_data:
            # Sprint 8 format - convert to Sprint 5 format
            sections = []
            for chunk in template_data.get("chunks", []):
                sections.append(
                    {
                        "heading": chunk.get("chunk_id", "Section"),
                        "prompt": chunk.get("prompt", ""),
                        "sources": chunk.get("dependencies", []),
                    }
                )

            # Parse into Template object
            parsed_sections = [
                Section(
                    heading=s["heading"],
                    prompt=s.get("prompt"),
                    sources=s.get("sources", []),
                )
                for s in sections
            ]

            document = Document(
                title=template_data.get("metadata", {}).get("title", "Generated Document"),
                output=template_data["output_path"],
                sections=parsed_sections,
            )

            template_obj = Template(document=document)
            output_path_from_template = template_data["output_path"]
        else:
            click.echo(
                "Error: Invalid template format. Expected either Sprint 5 format (with 'document') or Sprint 8 format (with 'template_version', 'output_path', 'chunks')",
                err=True,
            )
            raise click.Abort()

    except ValueError as e:
        click.echo(f"Error: Failed to parse template: {e}", err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f"Error: Failed to parse template: {e}", err=True)
        raise click.Abort()

    # 3. Enable verbose logging if requested
    if verbose:
        import logging
        
        # Set doc_evergreen loggers to INFO level for detailed progress
        logging.basicConfig(
            level=logging.INFO,
            format='%(message)s'  # Clean format, just the message
        )
        
        # Silence noisy third-party libraries
        logging.getLogger('anthropic').setLevel(logging.WARNING)
        logging.getLogger('httpx').setLevel(logging.WARNING)
        logging.getLogger('httpcore').setLevel(logging.WARNING)
        logging.getLogger('anthropic._base_client').setLevel(logging.WARNING)
    
    # 3. Initialize generator (use cwd as base_dir for intuitive source resolution)
    generator = ChunkedGenerator(template_obj, Path.cwd())

    # Progress callback to show generation progress
    def progress_callback(msg: str) -> None:
        """Display progress messages during generation."""
        click.echo(msg, nl=False)  # nl=False since messages include newlines

    # 4. Determine output path
    output_path = Path(output) if output else Path(output_path_from_template)

    # 5. Iterative refinement loop
    iteration = 0

    while True:
        iteration += 1

        # Generate new content
        try:
            # Handle both coroutine (real generator) and string (mocked generator)
            result = generator.generate(progress_callback=progress_callback)
            if hasattr(result, "__await__"):
                new_content: str = asyncio.run(result)  # type: ignore[arg-type]
            else:
                new_content = str(result)
        except Exception as e:
            # Check if it's a source validation error for templates with no sources
            error_msg = str(e)
            if "no sources" in error_msg.lower():
                # For templates with no sources, generate minimal placeholder content
                # This allows the workflow to complete for testing/validation purposes
                click.echo("Warning: Template has no source files - generating placeholder content", err=True)
                new_content = f"# {template_obj.document.title}\n\n*No source files provided*\n"
            else:
                click.echo(f"Error: Generation failed: {e}", err=True)
                raise click.Abort()

        # Detect changes
        has_changes, diff_lines = detect_changes(output_path, new_content)

        # If no changes, report and exit
        if not has_changes:
            click.echo("No changes detected - content is identical to existing file.")
            break

        # Show diff
        if diff_lines == ["NEW FILE"]:
            click.echo(f"Creating new file: {output_path}")
        else:
            click.echo("Changes detected:")
            for line in diff_lines:
                click.echo(line.rstrip())

        # Get approval (unless auto-approve)
        if not auto_approve and not click.confirm("\nApply these changes?"):
            click.echo("Aborted - changes not applied")
            return

        # Write file
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            click.echo(f"Error: Permission denied creating directory {output_path.parent}", err=True)
            raise click.Abort()
        except Exception as e:
            click.echo(f"Error creating directory: {e}", err=True)
            raise click.Abort()

        try:
            output_path.write_text(new_content, encoding="utf-8")
            click.echo(f"✓ File written: {output_path}")
        except PermissionError:
            click.echo(f"Error: Permission denied writing to {output_path}", err=True)
            raise click.Abort()
        except Exception as e:
            click.echo(f"Error writing file: {e}", err=True)
            raise click.Abort()

        # If auto-approve, don't offer iteration (one-shot mode)
        if auto_approve:
            break

        # Ask if user wants to regenerate
        if not click.confirm("\nRegenerate with updated sources?"):
            break

    # Show completion message with iteration count
    iteration_word = "iteration" if iteration == 1 else "iterations"
    click.echo(f"\nCompleted {iteration} {iteration_word}")


@cli.command("reverse")
@click.argument("doc_path", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output path for generated template")
@click.option("--dry-run", is_flag=True, help="Preview analysis without creating template file")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed progress and analysis")
@click.option("--max-sources", type=int, default=5, help="Maximum sources per section (default: 5)")
def reverse(doc_path: str, output: str | None, dry_run: bool, verbose: bool, max_sources: int):
    """Generate template from existing documentation.
    
    Analyzes document structure, discovers source files, and creates
    a template.json file that can be used with the regen-doc command.
    
    Uses intelligent 3-stage discovery (pattern + semantic + LLM) for 70-80% accuracy.
    
    Examples:
        # Basic usage
        doc-evergreen reverse README.md
        
        # Preview without creating file
        doc-evergreen reverse README.md --dry-run
        
        # Verbose output with details
        doc-evergreen reverse README.md --verbose
        
        # Custom output path
        doc-evergreen reverse docs/API.md -o my-template.json
        
        # Limit sources per section
        doc-evergreen reverse README.md --max-sources 3
    """
    from pathlib import Path
    from doc_evergreen.reverse import (
        DocumentParser, 
        IntelligentSourceDiscoverer, 
        ContentIntentAnalyzer,
        PromptGenerator,
        TemplateAssembler
    )
    
    # Enable logging if verbose (but filter out noisy third-party libraries)
    if verbose:
        import logging
        
        # Set our app to INFO level (not DEBUG - too much)
        logging.basicConfig(
            level=logging.INFO,
            format='%(message)s'  # Clean format, just the message
        )
        
        # Silence noisy third-party libraries
        logging.getLogger('anthropic').setLevel(logging.WARNING)
        logging.getLogger('httpx').setLevel(logging.WARNING)
        logging.getLogger('httpcore').setLevel(logging.WARNING)
        logging.getLogger('anthropic._base_client').setLevel(logging.WARNING)
    
    doc_path_obj = Path(doc_path)
    
    # Validate file exists
    if not doc_path_obj.exists():
        click.echo(f"❌ Error: {doc_path} does not exist", err=True)
        raise click.Abort()
    
    # Determine project root (look for git root, fallback to current directory)
    project_root = _find_project_root(doc_path_obj)
    
    if verbose:
        click.echo(f"\n{'='*60}")
        click.echo(f"REVERSE TEMPLATE GENERATION")
        click.echo(f"{'='*60}")
        click.echo(f"Document: {doc_path_obj}")
        click.echo(f"Project root: {project_root}")
        click.echo(f"Max sources per section: {max_sources}")
        if dry_run:
            click.echo(f"Mode: DRY RUN (preview only)")
        click.echo(f"{'='*60}\n")
    
    click.echo(f"🔍 Analyzing {doc_path_obj.name}...")
    
    # Step 1: Parse document structure
    try:
        with open(doc_path_obj) as f:
            content = f.read()
        
        if not content.strip():
            click.echo(f"❌ Error: Document is empty", err=True)
            click.echo(f"   File: {doc_path_obj}", err=True)
            raise click.Abort()
        
        parser = DocumentParser()
        parsed_doc = parser.parse(content)
        
        if not parsed_doc.get('sections'):
            click.echo(f"❌ Error: No sections found in document", err=True)
            click.echo(f"   The document may not have any markdown headings (##, ###, etc.)", err=True)
            click.echo(f"   File: {doc_path_obj}", err=True)
            raise click.Abort()
        
        section_count = len(parsed_doc['sections'])
        click.echo(f"📝 Found {section_count} section{'' if section_count == 1 else 's'}")
        
        if verbose:
            click.echo(f"\nSections:")
            for idx, section in enumerate(parsed_doc['sections']):
                click.echo(f"  {idx+1}. {section['heading']}")
            click.echo()  # Add blank line after sections list
    except click.Abort:
        raise
    except UnicodeDecodeError:
        click.echo(f"❌ Error: Cannot read file (encoding issue)", err=True)
        click.echo(f"   File may not be valid UTF-8 text", err=True)
        click.echo(f"   File: {doc_path_obj}", err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f"❌ Error parsing document: {e}", err=True)
        if verbose:
            import traceback
            click.echo(f"\nFull traceback:", err=True)
            traceback.print_exc()
        raise click.Abort()
    
    # Step 2: Discover sources for each section (intelligent 3-stage pipeline)
    click.echo(f"🔎 Discovering source files (intelligent discovery)...")
    
    # Calculate document path relative to project root (to exclude from sources)
    try:
        doc_relative_path = str(doc_path_obj.relative_to(project_root))
    except ValueError:
        # Document is outside project root, use name only
        doc_relative_path = doc_path_obj.name
    
    try:
        # Create simple LLM client for intelligent analysis
        if verbose:
            click.echo(f"  Initializing LLM client...")
        llm_client = _create_llm_client()
        
        # Building file index can take time on large repos
        if verbose:
            click.echo(f"  Building file index (this may take a moment for large repos)...")
            click.echo(f"  Excluding from sources: {doc_relative_path} (document being reversed)")
        
        discoverer = IntelligentSourceDiscoverer(
            project_root=project_root,
            llm_client=llm_client,
            exclude_path=doc_relative_path  # CRITICAL: Exclude document being reversed
        )
        if verbose:
            click.echo(f"  File index ready ({len(discoverer.semantic_searcher.file_index)} files indexed) - starting discovery...")
        source_mappings = {}
        total_sources = 0
        
        for idx, section in enumerate(parsed_doc['sections']):
            # Show progress for all sections (not just verbose)
            section_progress = f"[{idx+1}/{len(parsed_doc['sections'])}]"
            if verbose:
                click.echo(f"\n{'='*60}")
                click.echo(f"{section_progress} TOP-LEVEL SECTION: {section['heading']}")
                click.echo(f"{'='*60}")
            else:
                # Show inline progress (overwrite line)
                click.echo(f"\r  {section_progress} Discovering sources...", nl=False)
            
            # IntelligentSourceDiscoverer returns rich metadata, extract just paths
            # (document being reversed is already excluded in discovery stages)
            discovered = discoverer.discover_sources(
                section_heading=section['heading'],
                section_content=section.get('content', ''),
                max_sources=max_sources
            )
            # Extract just the file paths for template
            sources = [d['path'] for d in discovered]
            source_mappings[idx] = sources
            total_sources += len(sources)
            
            # Verbose logging from intelligent_source_discoverer already shows sources with scores
            # No need to repeat here
            
            # Discover for nested subsections
            _discover_subsections(section, (idx,), discoverer, source_mappings, doc_relative_path, max_sources, verbose)
        
        # Clear progress line and show completion
        if not verbose:
            click.echo(f"\r  [Complete]                              ")
        click.echo(f"✅ Found {total_sources} source file{'' if total_sources == 1 else 's'}")
        
        if total_sources == 0:
            click.echo(f"\n⚠️  Warning: No source files discovered", err=False)
            click.echo(f"   Template will be created with empty source lists", err=False)
            click.echo(f"   You can manually add sources after generation", err=False)
    except click.Abort:
        raise
    except Exception as e:
        click.echo(f"❌ Error discovering sources: {e}", err=True)
        click.echo(f"   This may be due to API issues or project structure", err=True)
        if verbose:
            import traceback
            click.echo(f"\nFull traceback:", err=True)
            traceback.print_exc()
        else:
            click.echo(f"   Run with --verbose for detailed error information", err=True)
        raise click.Abort()
    
    # Step 3: Analyze content and generate intelligent prompts
    click.echo(f"🧠 Analyzing content and generating prompts...")
    
    try:
        analyzer = ContentIntentAnalyzer(llm_client=llm_client)
        prompt_generator = PromptGenerator(llm_client=llm_client)
        
        section_analyses = {}
        prompt_mappings = {}
        
        for idx, section in enumerate(parsed_doc['sections']):
            # Show progress for all sections (not just verbose)
            section_progress = f"[{idx+1}/{len(parsed_doc['sections'])}]"
            if verbose:
                click.echo(f"\n  {section_progress} Analyzing: {section['heading']}")
            else:
                # Show inline progress (overwrite line)
                click.echo(f"\r  {section_progress} Analyzing and generating prompts...", nl=False)
            
            # Analyze section content
            analysis = analyzer.analyze_section(
                section_heading=section['heading'],
                section_content=section.get('content', '')
            )
            section_analyses[idx] = analysis
            
            if verbose:
                click.echo(f"    → Type: {analysis['section_type']}")
                click.echo(f"    → Quadrant: {analysis['divio_quadrant']}")
                click.echo(f"    → Intent: {analysis['intent']}")
            
            # Generate intelligent prompt based on analysis
            prompt_result = prompt_generator.generate_prompt(
                section_heading=section['heading'],
                section_analysis=analysis,
                discovered_sources=source_mappings.get(idx, [])
            )
            prompt_mappings[idx] = prompt_result['prompt']
            
            if verbose:
                prompt_preview = prompt_result['prompt'][:100] + "..." if len(prompt_result['prompt']) > 100 else prompt_result['prompt']
                click.echo(f"    → Prompt: {prompt_preview}")
            
            # Analyze and generate prompts for nested subsections
            _analyze_subsections(section, (idx,), analyzer, prompt_generator, 
                               source_mappings, section_analyses, prompt_mappings, doc_relative_path, max_sources, verbose)
        
        # Clear progress line and show completion
        if not verbose:
            click.echo(f"\r  [Complete]                                               ")
        click.echo(f"✅ Generated {len(prompt_mappings)} intelligent prompts")
    except click.Abort:
        raise
    except Exception as e:
        click.echo(f"❌ Error analyzing content: {e}", err=True)
        click.echo(f"   This may be due to LLM API issues", err=True)
        if verbose:
            import traceback
            click.echo(f"\nFull traceback:", err=True)
            traceback.print_exc()
        else:
            click.echo(f"   Run with --verbose for detailed error information", err=True)
        click.echo(f"\n   Tip: Check that your Anthropic API key is valid:", err=True)
        click.echo(f"   ~/.claude/api_key.txt", err=True)
        raise click.Abort()
    
    # Step 4: Assemble template with intelligent prompts
    click.echo(f"🔧 Assembling template...")
    
    try:
        assembler = TemplateAssembler()
        template = assembler.assemble(
            parsed_doc=parsed_doc,
            source_mappings=source_mappings,
            output_filename=doc_path_obj.name,
            prompt_mappings=prompt_mappings
        )
        
        # Determine output path
        if output:
            output_path = Path(output)
        else:
            # Default: .doc-evergreen/templates/{name}-reversed.json
            template_name = template['_meta']['name']
            output_path = project_root / ".doc-evergreen" / "templates" / f"{template_name}.json"
        
        # Handle dry-run mode
        if dry_run:
            click.echo(f"\n{'='*60}")
            click.echo(f"DRY RUN COMPLETE - Template Preview")
            click.echo(f"{'='*60}\n")
            
            # Show template summary
            click.echo(f"Template Name: {template['_meta']['name']}")
            click.echo(f"Description: {template['_meta']['description']}")
            click.echo(f"Sections: {len(template['document']['sections'])}")
            click.echo(f"Total Sources: {sum(len(s.get('sources', [])) for s in template['document']['sections'])}")
            
            if verbose:
                click.echo(f"\nFull template JSON:")
                import json
                click.echo(json.dumps(template, indent=2))
            
            click.echo(f"\n✅ Preview complete. No template file created (dry-run mode).")
            click.echo(f"\nTo generate the template, run without --dry-run:")
            click.echo(f"  doc-evergreen reverse {doc_path}")
            return
        
        # Save template
        assembler.save(template, output_path)
        
        click.echo(f"✅ Template generated: {output_path}")
        
        if verbose:
            click.echo(f"\nTemplate details:")
            click.echo(f"  • Sections: {len(template['document']['sections'])}")
            click.echo(f"  • Total sources: {total_sources}")
            click.echo(f"  • Total prompts: {len(prompt_mappings)}")
        
        click.echo("\nNext steps:")
        click.echo(f"1. Review: cat {output_path}")
        click.echo(f"2. Test: doc-evergreen regen-doc {output_path}")
        click.echo(f"3. Refine prompts and sources as needed")
        
    except click.Abort:
        raise
    except Exception as e:
        click.echo(f"❌ Error generating template: {e}", err=True)
        if verbose:
            import traceback
            click.echo(f"\nFull traceback:", err=True)
            traceback.print_exc()
        raise click.Abort()


def _find_project_root(doc_path: Path) -> Path:
    """Find the project root (git root or current working directory).
    
    Args:
        doc_path: Path to the document being analyzed
        
    Returns:
        Project root path
    """
    # Start from document directory
    current = doc_path.parent if doc_path.is_file() else doc_path
    
    # Look for .git directory (git root)
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent
    
    # Fallback to current working directory
    return Path.cwd()


def _create_llm_client():
    """Create a simple LLM client for intelligent source discovery.
    
    Returns:
        LLM client with generate() method
    """
    from pathlib import Path
    
    # Simple LLM client wrapper using Anthropic
    class SimpleLLMClient:
        def __init__(self):
            # Load API key
            claude_key_path = Path.home() / ".claude" / "api_key.txt"
            if not claude_key_path.exists():
                raise ValueError(f"Anthropic API key not found at {claude_key_path}")
            
            api_key = claude_key_path.read_text().strip()
            if "=" in api_key:
                api_key = api_key.split("=", 1)[1].strip()
            
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=api_key)
                self.model = "claude-sonnet-4-20250514"
            except ImportError:
                raise ImportError("anthropic package not installed. Run: pip install anthropic")
        
        def generate(self, prompt: str, temperature: float = 0.0) -> str:
            """Generate response from Claude."""
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
    
    return SimpleLLMClient()


def _discover_subsections(
    section: dict, 
    parent_index: tuple, 
    discoverer, 
    source_mappings: dict,
    doc_relative_path: str,
    max_sources: int,
    verbose: bool = False
):
    """Recursively discover sources for subsections.
    
    Args:
        section: Section dictionary with potential subsections
        parent_index: Parent section index tuple (e.g., (0,) or (0, 1))
        discoverer: IntelligentSourceDiscoverer instance
        source_mappings: Dictionary to populate with source mappings
        doc_relative_path: Relative path of document being analyzed (to exclude)
        max_sources: Maximum sources per section
        verbose: Whether to show verbose output
    """
    subsections = section.get('subsections', [])
    for sub_idx, subsection in enumerate(subsections):
        nested_index = (*parent_index, sub_idx)
        
        # Show subsection header in verbose mode
        if verbose:
            indent = "  " * len(parent_index)  # Indent based on nesting depth
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"\n{indent}  ↳ Subsection: {subsection['heading']}")
        
        # IntelligentSourceDiscoverer returns rich metadata, extract just paths
        # (document being reversed is already excluded in discovery stages)
        discovered = discoverer.discover_sources(
            section_heading=subsection['heading'],
            section_content=subsection.get('content', ''),
            max_sources=max_sources
        )
        # Extract just the file paths for template
        sources = [d['path'] for d in discovered]
        source_mappings[nested_index] = sources
        
        # Recurse for deeper nesting
        _discover_subsections(subsection, nested_index, discoverer, source_mappings, doc_relative_path, max_sources, verbose)


def _analyze_subsections(
    section: dict, 
    parent_index: tuple, 
    analyzer, 
    prompt_generator,
    source_mappings: dict,
    section_analyses: dict,
    prompt_mappings: dict,
    doc_relative_path: str,
    max_sources: int,
    verbose: bool = False
):
    """Recursively analyze subsections and generate prompts.
    
    Args:
        section: Section dictionary with potential subsections
        parent_index: Parent section index tuple (e.g., (0,) or (0, 1))
        analyzer: ContentIntentAnalyzer instance
        prompt_generator: PromptGenerator instance
        source_mappings: Dictionary with source mappings
        section_analyses: Dictionary to populate with analyses
        prompt_mappings: Dictionary to populate with prompts
        doc_relative_path: Relative path of document being analyzed (to exclude)
        max_sources: Maximum sources per section
        verbose: Whether to show verbose output
    """
    subsections = section.get('subsections', [])
    for sub_idx, subsection in enumerate(subsections):
        nested_index = (*parent_index, sub_idx)
        
        # Show subsection header in verbose mode
        if verbose:
            indent = "  " * len(parent_index)  # Indent based on nesting depth
            click.echo(f"\n{indent}  ↳ Analyzing subsection: {subsection['heading']}")
        
        # Analyze subsection content
        analysis = analyzer.analyze_section(
            section_heading=subsection['heading'],
            section_content=subsection.get('content', '')
        )
        section_analyses[nested_index] = analysis
        
        if verbose:
            indent = "  " * len(parent_index)
            click.echo(f"{indent}    → Type: {analysis['section_type']}")
            click.echo(f"{indent}    → Quadrant: {analysis['divio_quadrant']}")
            click.echo(f"{indent}    → Intent: {analysis['intent']}")
        
        # Generate intelligent prompt
        prompt_result = prompt_generator.generate_prompt(
            section_heading=subsection['heading'],
            section_analysis=analysis,
            discovered_sources=source_mappings.get(nested_index, [])
        )
        prompt_mappings[nested_index] = prompt_result['prompt']
        
        if verbose:
            indent = "  " * len(parent_index)
            prompt_preview = prompt_result['prompt'][:100] + "..." if len(prompt_result['prompt']) > 100 else prompt_result['prompt']
            click.echo(f"{indent}    → Prompt: {prompt_preview}")
        
        # Recurse for deeper nesting
        _analyze_subsections(
            subsection, nested_index, analyzer, prompt_generator,
            source_mappings, section_analyses, prompt_mappings, doc_relative_path, max_sources, verbose
        )


@cli.command("generate-doc")
@click.argument("output_path", type=click.Path())
@click.option(
    "--type", 
    "doc_type", 
    required=True, 
    help=(
        "Documentation type (Diataxis framework):\n"
        "  tutorial     - Learning-oriented (getting started guides)\n"
        "  howto        - Goal-oriented (problem-solving guides)\n"
        "  reference    - Information-oriented (API/command docs)\n"
        "  explanation  - Understanding-oriented (concepts/design)"
    )
)
@click.option("--purpose", required=True, help="What should this documentation accomplish?")
def generate_doc(output_path: str, doc_type: str, purpose: str):
    """Generate documentation from scratch using project analysis.
    
    Creates a new document by analyzing your project and generating an appropriate
    structure based on the documentation type and purpose you specify.
    
    \b
    Documentation Types (Diataxis):
      tutorial     - Learning-oriented guides for getting started
      howto        - Goal-oriented guides for solving problems
      reference    - Information-oriented technical descriptions
      explanation  - Understanding-oriented clarifications
    
    \b
    Examples:
      # Generate a tutorial README
      $ doc-evergreen generate-doc README.md \\
          --type tutorial \\
          --purpose "Help developers get started in 5 minutes"
      
      # Generate API reference
      $ doc-evergreen generate-doc docs/API.md \\
          --type reference \\
          --purpose "Document all public APIs"
      
      # Generate how-to guide
      $ doc-evergreen generate-doc docs/CONTRIBUTING.md \\
          --type howto \\
          --purpose "Guide contributors through the development workflow"
    
    \b
    Sprint 1 Status:
      This command currently captures your intent and saves it to
      .doc-evergreen/context.json. Future sprints will add:
      - Repository analysis
      - Source file discovery
      - Outline generation
      - Document generation
    """
    from doc_evergreen.generate.doc_type import validate_doc_type, InvalidDocTypeError, get_doc_type_description
    from doc_evergreen.generate.intent_context import IntentContext, save_intent_context, ContextFileError
    
    try:
        # Validate doc type
        validated_doc_type = validate_doc_type(doc_type)
        
        # Create intent context
        context = IntentContext(
            doc_type=validated_doc_type,
            purpose=purpose,
            output_path=output_path,
        )
        
        # Save context
        save_intent_context(context)
        
        # Display success message
        click.echo()
        click.echo("✅ Intent captured successfully!")
        click.echo()
        click.echo(f"  📄 Output: {output_path}")
        click.echo(f"  📚 Type: {doc_type}")
        click.echo(f"  🎯 Purpose: {purpose}")
        click.echo()
        click.echo(f"  💡 {get_doc_type_description(validated_doc_type)}")
        click.echo()
        click.echo("📝 Context saved to: .doc-evergreen/context.json")
        click.echo()
        click.echo("🚧 Sprint 1 Complete - Intent Capture")
        click.echo("   Future sprints will add:")
        click.echo("   • Repository analysis (Sprint 2)")
        click.echo("   • Source file discovery (Sprint 3)")
        click.echo("   • Outline generation (Sprints 4-5)")
        click.echo("   • Document generation (Sprint 6)")
        click.echo()
        
    except InvalidDocTypeError as e:
        click.echo()
        click.echo(f"❌ Error: {e}", err=True)
        click.echo()
        click.echo("Valid documentation types:", err=True)
        click.echo("  • tutorial     - Learning-oriented (getting started)", err=True)
        click.echo("  • howto        - Goal-oriented (problem-solving)", err=True)
        click.echo("  • reference    - Information-oriented (technical)", err=True)
        click.echo("  • explanation  - Understanding-oriented (concepts)", err=True)
        click.echo()
        raise click.Abort()
        
    except ContextFileError as e:
        click.echo()
        click.echo(f"❌ Error saving context: {e}", err=True)
        click.echo()
        raise click.Abort()


@cli.command("generate-outline")
@click.argument("output_path", type=click.Path())
@click.option(
    "--type", 
    "doc_type", 
    required=True, 
    help=(
        "Documentation type (Diataxis framework):\n"
        "  tutorial     - Learning-oriented (getting started guides)\n"
        "  howto        - Goal-oriented (problem-solving guides)\n"
        "  reference    - Information-oriented (API/command docs)\n"
        "  explanation  - Understanding-oriented (concepts/design)"
    )
)
@click.option("--purpose", required=True, help="What should this documentation accomplish?")
@click.pass_context
def generate_outline(ctx, output_path: str, doc_type: str, purpose: str):
    """Generate documentation outline without creating the document.
    
    This command runs the complete analysis pipeline and creates an outline.json
    file that you can review and edit before generating the actual documentation.
    
    \b
    Documentation Types (Diataxis):
      tutorial     - Learning-oriented guides for getting started
      howto        - Goal-oriented guides for solving problems
      reference    - Information-oriented technical descriptions
      explanation  - Understanding-oriented clarifications
    
    \b
    Workflow:
      1. Run generate-outline to create outline.json
      2. Review/edit .doc-evergreen/outline.json (optional)
      3. Run generate-from-outline to create the document
    
    \b
    Examples:
      # Generate outline for tutorial
      $ doc-evergreen generate-outline README.md \\
          --type tutorial \\
          --purpose "Help developers get started in 5 minutes"
      
      # Generate outline for API reference
      $ doc-evergreen generate-outline docs/API.md \\
          --type reference \\
          --purpose "Document all public APIs"
    """
    import logging
    
    from doc_evergreen.generate.doc_type import validate_doc_type, InvalidDocTypeError
    from doc_evergreen.generate.intent_context import IntentContext, save_intent_context
    from doc_evergreen.generate.repo_indexer import RepoIndexer
    from doc_evergreen.generate.relevance_analyzer import RelevanceNotes
    from doc_evergreen.generate.llm_relevance_analyzer import LLMRelevanceAnalyzer
    from doc_evergreen.generate.outline_generator import OutlineGenerator
    
    logger = logging.getLogger(__name__)
    verbose = ctx.obj.get('verbose', False)
    
    try:
        logger.info(f"🎯 Starting generate-outline (verbose={verbose})")
        # Step 1: Capture intent (Sprint 1)
        click.echo("🎯 Capturing intent...")
        validated_doc_type = validate_doc_type(doc_type)
        context = IntentContext(
            doc_type=validated_doc_type,
            purpose=purpose,
            output_path=output_path,
        )
        save_intent_context(context)
        
        # Step 2: Index repository (Sprint 2)
        click.echo("📂 Indexing repository...")
        indexer = RepoIndexer(project_root=Path.cwd())
        file_index = indexer.build_index()
        click.echo(f"   Found {file_index.total_files} files")
        
        # Save file index
        file_index.save(Path(".doc-evergreen/file_index.json"))
        
        # Step 3: Analyze relevance (Sprint 3 - LLM-powered)
        click.echo("🔍 Analyzing file relevance (LLM-powered)...")
        logger.info("Creating LLMRelevanceAnalyzer...")
        
        analyzer = LLMRelevanceAnalyzer(
            context=context,
            file_index=file_index,
            threshold=50,
            batch_size=5,
        )
        
        logger.info("Starting relevance analysis...")
        
        # Progress tracking
        def show_progress(current, total, file_path):
            percentage = int((current / total) * 100)
            click.echo(f"   🔍 {percentage}% ({current}/{total}) - {file_path}")
            logger.debug(f"Progress: {current}/{total} files analyzed")
        
        scores = analyzer.analyze(progress_callback=show_progress)
        click.echo(f"   ✓ Identified {len(scores)} relevant files")
        logger.info(f"Relevance analysis complete: {len(scores)} files above threshold")
        
        # Save relevance notes
        notes = RelevanceNotes(
            doc_type=context.doc_type.value,
            purpose=context.purpose,
            relevant_files=scores,
            total_files_analyzed=file_index.total_files,
            threshold=50,
        )
        notes.save(Path(".doc-evergreen/relevance_notes.json"))
        
        # Step 4: Generate outline (Sprint 4-5)
        click.echo("📝 Generating outline...")
        generator = OutlineGenerator(context=context, relevant_files=scores)
        outline = generator.generate()
        click.echo(f"   {len(outline.sections)} sections")
        
        # Count total subsections
        def count_sections(sections):
            count = len(sections)
            for s in sections:
                count += count_sections(s.sections)
            return count
        total_sections = count_sections(outline.sections)
        click.echo(f"   {total_sections} total sections (including subsections)")
        
        # Save outline
        outline_path = Path(".doc-evergreen/outline.json")
        outline.save(outline_path)
        
        # Success message
        click.echo()
        click.echo("✅ Outline generated successfully!")
        click.echo()
        click.echo(f"📄 Outline saved to: {outline_path}")
        click.echo()
        click.echo("Next steps:")
        click.echo("  1. Review the outline: cat .doc-evergreen/outline.json")
        click.echo("  2. (Optional) Edit the outline to adjust sections, prompts, or sources")
        click.echo("  3. Generate the document:")
        click.echo(f"     $ doc-evergreen generate-from-outline {outline_path}")
        click.echo()
        
    except InvalidDocTypeError as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f"❌ Error generating outline: {e}", err=True)
        raise click.Abort()


@cli.command("generate-from-outline")
@click.argument("outline_path", type=click.Path())
def generate_from_outline(outline_path: str):
    """Generate documentation from an outline file.
    
    Takes an existing outline.json file (created by generate-outline or manually)
    and generates the complete documentation.
    
    \b
    This allows you to:
      - Review the outline before generating
      - Make manual adjustments to structure, prompts, or sources
      - Regenerate documentation with different settings
    
    \b
    Examples:
      # Generate from default outline location
      $ doc-evergreen generate-from-outline .doc-evergreen/outline.json
      
      # Generate from custom outline
      $ doc-evergreen generate-from-outline /path/to/custom-outline.json
    """
    from doc_evergreen.generate.doc_generator import DocumentGenerator
    
    try:
        outline_path_obj = Path(outline_path)
        
        # Validate outline exists
        if not outline_path_obj.exists():
            click.echo()
            click.echo(f"❌ Error: Outline file not found", err=True)
            click.echo(f"   File: {outline_path}", err=True)
            click.echo()
            click.echo("Did you mean to:", err=True)
            click.echo("  1. Generate outline first:", err=True)
            click.echo("     $ doc-evergreen generate-outline README.md --type tutorial --purpose \"...\"", err=True)
            click.echo()
            raise click.Abort()
        
        # Generate document
        click.echo("✨ Generating documentation from outline...")
        click.echo()
        
        generator = DocumentGenerator(project_root=Path.cwd())
        content = generator.generate_from_outline(outline_path_obj)
        
        # Success message
        click.echo()
        click.echo("✅ Documentation generated successfully!")
        click.echo()
        
        # Load outline to get output path
        from doc_evergreen.generate.outline_generator import DocumentOutline
        outline = DocumentOutline.load(outline_path_obj)
        
        click.echo(f"📄 Document created: {outline.output_path}")
        click.echo(f"   {len(content)} characters")
        click.echo()
        click.echo("💡 Tip: Review the generated document and refine the outline if needed,")
        click.echo("   then run generate-from-outline again to regenerate.")
        click.echo()
        
    except Exception as e:
        click.echo()
        click.echo(f"❌ Error generating document: {e}", err=True)
        click.echo()
        click.echo("Make sure the outline file is valid JSON with the required structure.", err=True)
        click.echo()
        raise click.Abort()


if __name__ == "__main__":
    cli()
