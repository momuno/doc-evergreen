# Sprint 4: Polish & Production Readiness

**Duration:** 1-2 days  
**Goal:** Production-ready CLI with error handling, options, and documentation  
**Value Delivered:** Polished, robust feature ready for user testing

---

## 🎯 Why This Sprint?

Sprint 3 delivered the complete feature: parse → analyze → discover → generate → assemble. Now we need to make it **production-ready** for real users.

**Current State** (after Sprint 3):
- ✅ Complete reverse template pipeline works
- ✅ Intelligent source discovery (70-80% accuracy)
- ✅ LLM-generated prompts
- ❌ Basic error handling only
- ❌ No CLI options (--dry-run, --verbose, etc.)
- ❌ Limited progress feedback
- ❌ Missing edge case handling

**Goal State** (after Sprint 4):
- ✅ Robust error handling for all failure modes
- ✅ CLI options for flexibility (--dry-run, --verbose, --output)
- ✅ Clear progress feedback and helpful error messages
- ✅ Edge cases handled gracefully
- ✅ Documentation and examples
- ✅ Ready for user testing

Sprint 4 transforms the feature from "works on happy path" to "production-ready."

---

## 📦 Deliverables

### 1. CLI Options & Flexibility
**Estimated Lines:** ~150 lines + 100 lines tests

**What it does:**
- `--dry-run`: Preview without generating template
- `--verbose`: Show detailed progress and LLM reasoning
- `--output <path>`: Specify output template path
- `--max-sources <n>`: Limit sources per section (default: 5)
- `--skip-llm`: Use pattern matching only (fast, less accurate)

**Why this sprint:**
Gives users control over the generation process. Power users want options.

**Implementation notes:**
```python
@click.command()
@click.argument('doc_path', type=click.Path(exists=True))
@click.option('--output', '-o', 
              help='Output template path (default: .doc-evergreen/templates/{name}-reversed.json)')
@click.option('--dry-run', is_flag=True,
              help='Preview analysis without generating template')
@click.option('--verbose', '-v', is_flag=True,
              help='Show detailed progress and LLM reasoning')
@click.option('--max-sources', type=int, default=5,
              help='Maximum sources per section (default: 5)')
@click.option('--skip-llm', is_flag=True,
              help='Use pattern matching only (faster, less accurate)')
def reverse(doc_path, output, dry_run, verbose, max_sources, skip_llm):
    """Generate template from existing documentation.
    
    Examples:
    
      # Basic usage
      doc-evergreen template reverse README.md
      
      # Preview without generating
      doc-evergreen template reverse README.md --dry-run
      
      # Verbose output with reasoning
      doc-evergreen template reverse README.md --verbose
      
      # Custom output path
      doc-evergreen template reverse README.md -o my-template.json
      
      # Fast mode (pattern matching only)
      doc-evergreen template reverse README.md --skip-llm
    """
    
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    
    try:
        # Parse
        if verbose:
            print(f"🔍 Parsing {doc_path}...")
        # ... rest of pipeline ...
        
        if dry_run:
            print("\n✅ Dry run complete. Template preview:")
            print(json.dumps(template, indent=2))
            print("\nNo template file created (dry-run mode).")
            return
        
        # Save template
        # ...
        
    except FileNotFoundError:
        click.echo(f"❌ Error: File not found: {doc_path}", err=True)
        raise click.Abort()
    except Exception as e:
        if verbose:
            import traceback
            traceback.print_exc()
        click.echo(f"❌ Error: {str(e)}", err=True)
        raise click.Abort()
```

**TDD approach:**
```python
# 🔴 RED: Test CLI options
def test_dry_run_mode():
    runner = CliRunner()
    result = runner.invoke(reverse, ['README.md', '--dry-run'])
    
    assert result.exit_code == 0
    assert 'Template preview:' in result.output
    assert 'No template file created' in result.output
    # Template file should NOT be created
    assert not Path('.doc-evergreen/templates/README-reversed.json').exists()
    # FAILS - dry-run not implemented

# 🟢 GREEN: Implement dry-run
# 🔵 REFACTOR: Add other options
```

---

### 2. Error Handling & Edge Cases
**Estimated Lines:** ~200 lines + 150 lines tests

**What it does:**
- Graceful handling of all failure modes
- Clear, actionable error messages
- Fallback behaviors for partial failures
- Edge case handling (empty docs, malformed markdown, etc.)

**Why this sprint:**
Production code must handle errors gracefully. Users shouldn't see stack traces.

**Implementation notes:**
```python
class ReverseTemplateError(Exception):
    """Base exception for reverse template generation."""
    pass

class DocumentParseError(ReverseTemplateError):
    """Failed to parse document."""
    pass

class SourceDiscoveryError(ReverseTemplateError):
    """Failed to discover sources."""
    pass

class LLMError(ReverseTemplateError):
    """LLM API failure."""
    pass

class ReverseTemplateOrchestrator:
    """
    Orchestrates reverse template generation with robust error handling.
    """
    
    def generate_template(self, doc_path, options):
        """
        Generate template with comprehensive error handling.
        """
        try:
            # Parse document
            parsed_doc = self._parse_document_safe(doc_path)
            
            # Handle empty document
            if not parsed_doc['sections']:
                raise DocumentParseError(
                    f"No sections found in {doc_path}. "
                    "Document may be empty or improperly formatted."
                )
            
            # Analyze content
            section_analyses = self._analyze_content_safe(parsed_doc, options)
            
            # Discover sources
            source_mappings = self._discover_sources_safe(
                parsed_doc, section_analyses, options
            )
            
            # Generate prompts
            prompt_mappings = self._generate_prompts_safe(
                parsed_doc, section_analyses, source_mappings, options
            )
            
            # Assemble template
            template = self._assemble_template_safe(
                doc_path, parsed_doc, section_analyses, 
                source_mappings, prompt_mappings
            )
            
            return template
            
        except DocumentParseError as e:
            self._handle_parse_error(e, doc_path)
        except LLMError as e:
            self._handle_llm_error(e, options)
        except Exception as e:
            self._handle_unexpected_error(e, doc_path)
    
    def _parse_document_safe(self, doc_path):
        """Parse with error handling."""
        try:
            with open(doc_path) as f:
                content = f.read()
            
            if not content.strip():
                raise DocumentParseError("Document is empty")
            
            parsed = DocumentParser.parse(content)
            return parsed
            
        except FileNotFoundError:
            raise DocumentParseError(f"File not found: {doc_path}")
        except UnicodeDecodeError:
            raise DocumentParseError(f"Cannot read file (encoding issue): {doc_path}")
        except Exception as e:
            raise DocumentParseError(f"Failed to parse document: {str(e)}")
    
    def _discover_sources_safe(self, parsed_doc, section_analyses, options):
        """Discover sources with fallback."""
        source_mappings = {}
        
        for section_id, section in parsed_doc['sections'].items():
            try:
                sources = self.discoverer.discover_sources(
                    section['heading'],
                    section['content'],
                    max_sources=options.get('max_sources', 5)
                )
                
                # If no sources found, use fallback
                if not sources:
                    sources = self._fallback_sources(section, options)
                
                source_mappings[section_id] = sources
                
            except Exception as e:
                # Log warning but continue
                logger.warning(f"Source discovery failed for section '{section['heading']}': {e}")
                # Use fallback
                source_mappings[section_id] = self._fallback_sources(section, options)
        
        return source_mappings
    
    def _fallback_sources(self, section, options):
        """Provide fallback when source discovery fails."""
        # Suggest project root or common files
        return [
            {'path': '.', 'relevance_score': 3, 'match_reason': 'Fallback: Project root'}
        ]
    
    def _handle_llm_error(self, error, options):
        """Handle LLM failures gracefully."""
        if options.get('skip_llm'):
            # Already skipping LLM, can't recover
            raise error
        else:
            # Suggest fallback
            print("\n⚠️  LLM API error. Try:")
            print("  1. Check your API key and internet connection")
            print("  2. Use --skip-llm for faster pattern-based generation")
            print(f"\nError details: {str(error)}")
            raise click.Abort()
```

**Edge cases to handle:**
- Empty documents
- Documents with no headings
- Malformed markdown
- Very large documents (>10MB)
- Binary files passed as input
- No sources found for any section
- LLM API failures (rate limits, timeouts)
- Invalid file permissions
- Output directory doesn't exist

**TDD approach:**
```python
# 🔴 RED: Test edge cases
def test_empty_document():
    orchestrator = ReverseTemplateOrchestrator()
    
    with pytest.raises(DocumentParseError) as exc:
        orchestrator.generate_template('empty.md', {})
    
    assert 'empty' in str(exc.value).lower()
    # FAILS - error handling doesn't exist

def test_no_sources_found():
    # Should use fallback, not crash
    result = orchestrator.generate_template('minimal.md', {})
    assert all(len(s['sources']) > 0 for s in result['sections'])
    # FAILS - fallback not implemented

# 🟢 GREEN: Implement error handling
# 🔵 REFACTOR: Improve error messages
```

---

### 3. Progress Feedback & UX
**Estimated Lines:** ~100 lines + 50 lines tests

**What it does:**
- Detailed progress output (what's happening now?)
- Time estimates ("analyzing section 3 of 8...")
- Helpful hints ("This may take 1-2 minutes for large docs")
- Success summary with next steps

**Why this sprint:**
Good UX prevents frustration. Users need to know what's happening, especially with slow LLM calls.

**Implementation notes:**
```python
class ProgressReporter:
    """Report progress with helpful feedback."""
    
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.start_time = None
    
    def start(self, total_sections):
        """Start progress tracking."""
        self.start_time = time.time()
        print(f"\n🚀 Starting reverse template generation")
        print(f"   Total sections to process: {total_sections}")
        print(f"   Estimated time: {self._estimate_time(total_sections)}")
        print()
    
    def _estimate_time(self, total_sections):
        """Estimate total time based on section count."""
        # Rough estimates:
        # - Parsing: <1s
        # - Analysis per section: ~2s (LLM call)
        # - Source discovery per section: ~3s (semantic + LLM)
        # - Prompt generation per section: ~2s (LLM call)
        seconds = 1 + (total_sections * 7)  # ~7s per section
        if seconds < 60:
            return f"{seconds} seconds"
        else:
            return f"{seconds // 60} minutes"
    
    def step(self, step_name, current=None, total=None):
        """Report a step in progress."""
        if current and total:
            progress = f"[{current}/{total}]"
        else:
            progress = ""
        
        print(f"   {self._get_emoji(step_name)} {step_name} {progress}")
    
    def detail(self, message):
        """Show detailed progress (if verbose)."""
        if self.verbose:
            print(f"      └─ {message}")
    
    def complete(self, template_path, template):
        """Show completion summary."""
        elapsed = time.time() - self.start_time
        
        print(f"\n✅ Template generation complete in {elapsed:.1f}s")
        print(f"\n📋 Template Summary:")
        print(f"   • Name: {template['name']}")
        print(f"   • Quadrant: {template['quadrant']}")
        print(f"   • Sections: {len(template['sections'])}")
        print(f"   • Total sources: {sum(len(s['sources']) for s in template['sections'])}")
        print(f"   • Accuracy estimate: {template['metadata']['accuracy_estimate']}")
        print(f"\n💾 Saved to: {template_path}")
        print(f"\n🔄 Next steps:")
        print(f"   1. Review template:")
        print(f"      cat {template_path}")
        print(f"   2. Test regeneration:")
        print(f"      doc-evergreen regen --template {template_path}")
        print(f"   3. Compare results and refine template if needed")
```

**TDD approach:**
```python
# 🔴 RED: Test progress output
def test_progress_reporter(capsys):
    reporter = ProgressReporter(verbose=False)
    reporter.start(total_sections=5)
    reporter.step("Parsing document")
    reporter.step("Analyzing content", current=3, total=5)
    
    captured = capsys.readouterr()
    assert "Starting reverse template generation" in captured.out
    assert "[3/5]" in captured.out
    # FAILS - reporter doesn't exist

# 🟢 GREEN: Implement reporter
# 🔵 REFACTOR: Better time estimates
```

---

### 4. Documentation & Examples
**Estimated Lines:** ~300 lines documentation

**What it does:**
- README section for `template reverse` command
- Usage examples (basic, advanced, troubleshooting)
- FAQ section
- Architecture notes for developers

**Why this sprint:**
Documentation enables self-service. Users shouldn't need to ask how to use the feature.

**Documentation structure:**
```markdown
# Reverse Template Generation

## Overview

The `doc-evergreen template reverse` command generates templates FROM existing documentation, enabling the "update workflow" (UC2).

## Quick Start

```bash
# Generate template from existing README
doc-evergreen template reverse README.md

# Review generated template
cat .doc-evergreen/templates/README-reversed.json

# Test regeneration
doc-evergreen regen --template .doc-evergreen/templates/README-reversed.json

# Compare results
diff README.md README-NEW.md
```

## Command Options

- `--dry-run`: Preview without creating template file
- `--verbose`: Show detailed progress and reasoning
- `--output <path>`: Custom output path
- `--max-sources <n>`: Limit sources per section (default: 5)
- `--skip-llm`: Fast mode using pattern matching only

## Examples

### Example 1: Basic Usage
[...]

### Example 2: Custom Output Path
[...]

### Example 3: Verbose Mode
[...]

## How It Works

The reverse template generator uses a multi-stage pipeline:

1. **Document Parser**: Extracts heading structure and content
2. **Content Analyzer**: LLM analyzes section intent and classification
3. **Source Discovery**: Pattern + semantic + LLM-based source matching
4. **Prompt Generator**: LLM generates prompts from section analysis
5. **Template Assembly**: Combines all components into template.json

## Accuracy Expectations

Generated templates are typically **70-80% accurate**, meaning:
- ✅ Structure matches original document
- ✅ Sources are relevant to sections
- ✅ Prompts guide similar content generation
- ⚠️ May need 5-10 minutes of manual refinement

## Troubleshooting

**Problem**: No sources found for sections
**Solution**: Sources may not match expected patterns. Review and manually add sources.

**Problem**: LLM API errors
**Solution**: Check API key and connection. Try `--skip-llm` for fast mode.

**Problem**: Generated prompts are too generic
**Solution**: Manually refine prompts to be more specific.

## FAQ

**Q: Can I use this on documentation other than README?**
A: Yes! Works on any markdown documentation.

**Q: How long does generation take?**
A: Typically 1-5 minutes depending on document size.

**Q: Can I edit the generated template?**
A: Absolutely! Generated templates are starting points. Refine as needed.
```

---

## 🚫 What Gets Punted (Deliberately Excluded)

### ❌ GUI/Web Interface
- **Why**: CLI is sufficient for MVP
- **Reconsider**: v0.7.0+ if users request it
- Focus on CLI polish first

### ❌ Template Comparison Tool
- **Why**: Manual review is sufficient
- **Reconsider**: Future version
- `diff` command works for now

### ❌ Automated Template Testing
- **Why**: Manual testing is sufficient
- **Reconsider**: v0.7.0+ for CI/CD integration
- Test on real docs during development

### ❌ Performance Profiling
- **Why**: Premature optimization
- **Reconsider**: If performance becomes issue
- Current speed is acceptable (<5 min)

---

## 🧪 Testing Requirements

### TDD Approach (Red-Green-Refactor)

**Day 1: CLI Options & Error Handling**
- 🔴 Write tests for CLI options
- 🟢 Implement --dry-run, --verbose, etc.
- 🔵 Refactor option handling
- 🔴 Write edge case tests
- 🟢 Implement error handling
- 🔵 Refactor error messages
- ✅ Commit (tests green)

**Day 2: UX & Documentation**
- 🔴 Write progress reporter tests
- 🟢 Implement progress feedback
- 🔵 Refactor UX
- Write documentation
- Manual testing on multiple projects
- ✅ Final commit & v0.6.0 complete!

### Unit Tests (Write First)
- **CLI options**:
  - --dry-run mode works
  - --verbose shows details
  - --output custom path
  - --max-sources limits correctly
  - --skip-llm uses pattern matching only

- **Error handling**:
  - Empty document handled
  - Malformed markdown handled
  - No sources found (uses fallback)
  - LLM failures handled gracefully
  - File permission errors

- **Progress reporting**:
  - Shows progress correctly
  - Time estimates reasonable
  - Verbose mode shows details

### Integration Tests (After Unit Tests Pass)
- **End-to-end with options**:
  - All CLI options work in combination
  - Error recovery works
  - Progress output is clear

### Manual Testing (After Automated Tests Pass)
- [ ] Test all CLI options
- [ ] Test on doc-evergreen README
- [ ] Test on simple project README
- [ ] Test on complex technical doc
- [ ] Test error cases (empty file, malformed markdown, etc.)
- [ ] Test on slow network (LLM timeouts)
- [ ] Verify documentation is accurate
- [ ] Get external user to test (dogfooding)

**Test Coverage Target:** >80% for new code

---

## 📊 What You Learn

After Sprint 4, you'll discover:

1. **Production readiness**
   - What edges cases exist in real usage?
   - What errors do users encounter?
   - What UX improvements matter most?

2. **User workflow**
   - Do CLI options improve experience?
   - Is progress feedback helpful?
   - What documentation is most valuable?

3. **Feature completeness**
   - Is the feature ready to ship?
   - What's missing?
   - What polish is most valuable?

---

## ✅ Success Criteria

### Must Have
- ✅ All CLI options implemented and tested
- ✅ Robust error handling for common failures
- ✅ Clear progress feedback
- ✅ Edge cases handled gracefully
- ✅ Documentation complete and accurate
- ✅ Manual testing on 3+ different projects
- ✅ Ready for user testing

### Nice to Have (Defer if Time Constrained)
- ❌ Automated performance testing → Not critical
- ❌ GUI interface → CLI is sufficient
- ❌ Advanced analytics → Future version

---

## 🛠️ Technical Approach

### Key Decisions

**1. Graceful degradation everywhere**
- Never crash with stack trace
- Always provide fallback
- Clear error messages with solutions

**2. Progress feedback for long operations**
- LLM calls can be slow
- Users need to know it's working
- Show estimated time remaining

**3. Comprehensive documentation**
- Self-service is key
- Examples over descriptions
- Troubleshooting section essential

**4. CLI-first design**
- Polish CLI before GUI
- Power users prefer CLI
- Good CLI enables scripting

---

## 📅 Implementation Order

### Day 1: Options & Errors
- 🔴 Write CLI option tests
- 🟢 Implement options
- 🔵 Refactor
- 🔴 Write error handling tests
- 🟢 Implement error handling
- 🔵 Refactor error messages
- ✅ Commit

### Day 2: UX & Docs
- 🔴 Write progress tests
- 🟢 Implement progress reporter
- 🔵 Refactor UX
- Write documentation
- Manual testing
- Final polish
- ✅ Final commit & v0.6.0 COMPLETE! 🎉

---

## 🎯 Known Limitations (By Design)

1. **CLI only (no GUI)**
   - Acceptable: CLI is sufficient for developers
   - Future: Consider GUI for broader audience

2. **Manual template refinement**
   - Acceptable: 70-80% accuracy requires some refinement
   - Good UX makes refinement easy

3. **Single document at a time**
   - Acceptable: Batch processing not needed for MVP
   - Future: Add batch mode if requested

4. **No offline mode**
   - Acceptable: LLM APIs require internet
   - Future: Consider local LLM support

---

## 🎉 Sprint 4 Complete = v0.6.0 DONE!

After Sprint 4, you have:
- ✅ Complete reverse template generation feature
- ✅ 70-80% accuracy on source discovery
- ✅ Intelligent prompt generation
- ✅ Production-ready CLI
- ✅ Comprehensive documentation
- ✅ Ready for user testing

**v0.6.0 Success Metrics:**
- Can generate template from README in <5 minutes
- Generated template works with `regen` command
- 70-80% accuracy (minimal manual refinement needed)
- Clear documentation enables self-service
- Users successfully adopt update workflow (UC2)

---

**Congratulations!** 🎉 v0.6.0 Reverse Template Generation is complete and ready to ship!

**Next steps:**
1. Tag v0.6.0 release
2. Update README with new feature
3. User testing and feedback collection
4. Plan v0.7.0 based on learnings

---

**Ship it!** 🚢
