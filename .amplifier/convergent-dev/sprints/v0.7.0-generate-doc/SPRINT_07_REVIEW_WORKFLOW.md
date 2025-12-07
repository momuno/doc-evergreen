# Sprint 7: Outline Review Workflow

**Duration:** 1-2 days  
**Goal:** User can review/edit outline before generation  
**Value Delivered:** Production-ready two-command workflow

---

## 🎯 Why This Sprint?

Sprint 6 proved the full pipeline works end-to-end. But what if the user wants to **tweak the outline before generating**? This sprint adds the polish that makes v0.7.0 production-ready:
1. **Two-command workflow** - Separate outline generation from doc generation
2. **Outline review** - User can inspect/edit outline.json
3. **CLI polish** - Better help text, error messages, options
4. **Production readiness** - Edge case handling, documentation

**The difference:** Sprint 6 = "it works", Sprint 7 = "it's ready for users"

---

## 📦 Deliverables

### 1. Two-Command Workflow Implementation
**Estimated Lines:** ~180 lines + 140 lines tests

**What it does:**
- **Command 1**: `generate-outline` - Creates outline.json, stops before generation
- **Command 2**: `generate-from-outline` - Generates doc from (possibly edited) outline.json
- User can edit outline.json between commands

**Why this sprint:**
- Users want control over outline before committing to generation
- Editing JSON is easy, regenerating from scratch is expensive
- Common workflow: generate → review/edit → generate doc

**Implementation notes:**
- `generate-outline` runs Sprints 1-5 (stops before Sprint 6)
- `generate-from-outline` runs Sprint 6 only
- Both commands share underlying pipeline

**CLI design:**
```bash
# Command 1: Generate outline
$ doc-evergreen generate-outline README.md \
    --type tutorial \
    --purpose "Help developers get started in 5 minutes"

🔍 Analyzing project...
   Found 23 files, identified 8 relevant

📝 Generating outline...
   5 sections, 12 subsections
   Quality: 85%

✅ Outline saved to .doc-evergreen/outline.json

Review and edit the outline, then run:
  doc-evergreen generate-from-outline .doc-evergreen/outline.json

# User edits .doc-evergreen/outline.json (optional)

# Command 2: Generate doc from outline
$ doc-evergreen generate-from-outline .doc-evergreen/outline.json

✨ Generating documentation from outline...
   [Progress for each section]
   
✅ README.md created (450 lines)
```

### 2. Unified `generate-doc` Command with Options
**Estimated Lines:** ~120 lines + 80 lines tests

**What it does:**
- Adds `--dry-run` flag: Generate outline only, don't generate doc
- Adds `--from-outline` flag: Skip outline generation, use existing
- Default behavior: Full pipeline (outline → doc)

**Why this sprint:**
- Some users want single command (convenience)
- Others want two-step workflow (control)
- Flags provide flexibility

**Implementation notes:**
- Backward compatible: `generate-doc` still works as before
- New flags are optional
- Clear help text explaining options

**Enhanced CLI:**
```bash
# Option A: Single command (full pipeline)
$ doc-evergreen generate-doc README.md --type tutorial --purpose "..."
[Generates outline AND document]

# Option B: Dry-run (outline only)
$ doc-evergreen generate-doc README.md --type tutorial --purpose "..." --dry-run
[Generates outline, stops]

# Option C: From existing outline
$ doc-evergreen generate-doc README.md --from-outline .doc-evergreen/outline.json
[Uses existing outline, generates doc]
```

### 3. CLI Polish & User Experience
**Estimated Lines:** ~200 lines + 100 lines tests

**What it does:**
- Improved help text and examples
- Better error messages with actionable suggestions
- Progress feedback throughout pipeline
- Summary at end (what was created, next steps)

**Why this sprint:**
- Users need to understand what the tool does
- Errors should help users fix issues
- Clear feedback builds confidence

**Implementation notes:**
- Rich help text with examples
- Validate inputs early (helpful error messages)
- Show clear next steps at each stage

**Example error messages:**
```bash
# Bad
Error: Invalid outline file

# Good
❌ Error: Cannot read outline file

File: .doc-evergreen/outline.json
Reason: File does not exist

Did you mean to:
1. Generate outline first:
   $ doc-evergreen generate-outline README.md --type tutorial --purpose "..."
   
2. Use a different outline file:
   $ doc-evergreen generate-from-outline /path/to/outline.json
```

**Example help text:**
```bash
$ doc-evergreen generate-doc --help

Usage: doc-evergreen generate-doc [OPTIONS] OUTPUT

  Generate documentation from scratch.

  This command analyzes your project, generates an intelligent outline, and
  creates documentation. It's like writing a research paper with a structured
  process.

Examples:
  
  Generate a tutorial README:
    $ doc-evergreen generate-doc README.md \
        --type tutorial \
        --purpose "Help developers get started in 5 minutes"
  
  Generate outline only (review before generating doc):
    $ doc-evergreen generate-doc README.md \
        --type tutorial \
        --purpose "..." \
        --dry-run
    
    # Edit .doc-evergreen/outline.json, then:
    $ doc-evergreen generate-from-outline .doc-evergreen/outline.json
  
  Generate from existing outline:
    $ doc-evergreen generate-doc README.md \
        --from-outline .doc-evergreen/outline.json

Options:
  --type [tutorial|howto|reference|explanation]
                                  Documentation type (Diataxis framework)
                                  [required]
  --purpose TEXT                  Purpose of the documentation [required]
  --dry-run                       Generate outline only, don't generate doc
  --from-outline PATH             Use existing outline file
  --verbose                       Show detailed progress
  --help                          Show this message and exit

Documentation types:
  tutorial      Learning-oriented, step-by-step lessons
  howto         Goal-oriented, practical guides  
  reference     Information-oriented, technical details
  explanation   Understanding-oriented, conceptual depth

Learn more: https://docs.doc-evergreen.dev/generate-doc
```

### 4. Edge Case Handling & Validation
**Estimated Lines:** ~150 lines + 120 lines tests

**What it does:**
- Validates outline.json before generation
- Handles missing/corrupt files gracefully
- Provides clear error recovery guidance
- Handles empty results (no relevant files, minimal outline)

**Why this sprint:**
- Real-world usage will hit edge cases
- Graceful failures > cryptic errors
- Users need recovery guidance

**Implementation notes:**
- Validate outline schema before generation
- Check file existence before reading
- Provide helpful suggestions for recovery

**Edge cases to handle:**
```python
# Edge Case 1: No relevant files found
if len(relevant_files) == 0:
    print("⚠️  Warning: No relevant files found")
    print()
    print("Suggestions:")
    print("  1. Check that files exist in project directory")
    print("  2. Try a different doc purpose")
    print("  3. Check .docignore - may be excluding too much")
    print()
    proceed = click.confirm("Generate outline anyway (may be low quality)?")
    if not proceed:
        raise click.Abort()

# Edge Case 2: Outline quality too low
if outline_quality < 60:
    print(f"⚠️  Warning: Outline quality is low ({outline_quality}%)")
    print()
    print("Suggestions:")
    print("  1. Review .doc-evergreen/outline.json and edit manually")
    print("  2. Try a more specific purpose")
    print("  3. Add more relevant source files")
    print()
    proceed = click.confirm("Continue with generation?")
    if not proceed:
        raise click.Abort()

# Edge Case 3: Corrupted outline file
try:
    outline = json.loads(outline_path.read_text())
except json.JSONDecodeError as e:
    print(f"❌ Error: Invalid JSON in outline file")
    print(f"   Location: {e.msg} at line {e.lineno}")
    print()
    print("Fix the JSON syntax and try again.")
    raise click.Abort()

# Edge Case 4: Missing required fields
validator = OutlineValidator()
errors = validator.validate(outline)
if errors:
    print("❌ Error: Invalid outline structure")
    print()
    for error in errors:
        print(f"  • {error}")
    print()
    print("Fix the outline and try again.")
    raise click.Abort()
```

---

## 🧪 Testing Requirements

### TDD Approach

Follow red-green-refactor cycle for all features:

#### 1. 🔴 RED - Write Failing Tests First

**Two-Command Workflow Tests:**
```python
def test_generate_outline_creates_outline_only():
    # Test that generate-outline doesn't generate doc
    result = runner.invoke(cli, [
        'generate-outline', 'README.md',
        '--type', 'tutorial',
        '--purpose', 'Test purpose'
    ])
    
    assert result.exit_code == 0
    assert Path('.doc-evergreen/outline.json').exists()
    assert not Path('README.md').exists()  # Doc not generated

def test_generate_from_outline_uses_existing_outline():
    # Test that generate-from-outline uses provided outline
    # Create test outline
    create_test_outline('.doc-evergreen/outline.json')
    
    result = runner.invoke(cli, [
        'generate-from-outline',
        '.doc-evergreen/outline.json'
    ])
    
    assert result.exit_code == 0
    assert Path('README.md').exists()  # Doc generated

def test_generate_doc_dry_run_stops_before_generation():
    # Test that --dry-run generates outline only
    result = runner.invoke(cli, [
        'generate-doc', 'README.md',
        '--type', 'tutorial',
        '--purpose', 'Test',
        '--dry-run'
    ])
    
    assert result.exit_code == 0
    assert Path('.doc-evergreen/outline.json').exists()
    assert not Path('README.md').exists()
```

**Validation Tests:**
```python
def test_validates_outline_before_generation():
    # Test that invalid outline is rejected
    create_invalid_outline('.doc-evergreen/outline.json')
    
    result = runner.invoke(cli, [
        'generate-from-outline',
        '.doc-evergreen/outline.json'
    ])
    
    assert result.exit_code != 0
    assert 'Invalid outline' in result.output

def test_handles_missing_outline_file():
    # Test helpful error for missing file
    result = runner.invoke(cli, [
        'generate-from-outline',
        'nonexistent.json'
    ])
    
    assert result.exit_code != 0
    assert 'does not exist' in result.output
```

Run tests → Watch them fail → Good!

#### 2. 🟢 GREEN - Write Minimal Implementation

```python
@cli.command('generate-outline')
@click.argument('output_path', type=click.Path())
@click.option('--type', 'doc_type', required=True, type=click.Choice([...]))
@click.option('--purpose', required=True)
def generate_outline(output_path: str, doc_type: str, purpose: str):
    """Generate outline without creating document."""
    
    # Run Sprints 1-5 (intent capture → outline generation)
    context = capture_intent(output_path, doc_type, purpose)
    file_index = index_repository()
    relevant_files = analyze_relevance(context, file_index)
    outline = generate_outline_structure(context, relevant_files)
    
    # Save and exit
    outline_path = Path('.doc-evergreen/outline.json')
    outline_path.write_text(json.dumps(outline, indent=2))
    
    click.echo(f"✅ Outline saved to {outline_path}")
    click.echo()
    click.echo("Review and edit the outline, then run:")
    click.echo(f"  doc-evergreen generate-from-outline {outline_path}")

@cli.command('generate-from-outline')
@click.argument('outline_path', type=click.Path(exists=True))
def generate_from_outline(outline_path: str):
    """Generate document from existing outline."""
    
    # Load and validate outline
    outline_path = Path(outline_path)
    outline = json.loads(outline_path.read_text())
    
    # Validate
    validator = OutlineValidator()
    errors = validator.validate(outline)
    if errors:
        click.echo("❌ Error: Invalid outline")
        for error in errors:
            click.echo(f"  • {error}")
        raise click.Abort()
    
    # Run Sprint 6 (document generation)
    generator = ContentGenerator()
    document = generator.generate_document(outline_path)
    
    click.echo(f"✅ Document generated: {outline['document']['output']}")
```

Run tests → Watch them pass → Good!

#### 3. 🔵 REFACTOR - Improve Code Quality

- Extract validation to separate module
- Improve error messages
- Add comprehensive logging
- Optimize pipeline execution

Run tests → Still pass → Good!

### Unit Tests (Write First)

- **Command separation**: generate-outline vs generate-from-outline
- **Flag handling**: --dry-run, --from-outline, combinations
- **Validation**: Outline schema, file existence, JSON parsing
- **Error handling**: Missing files, invalid JSON, validation failures

### Integration Tests (Write First)

- **Two-command workflow**: generate-outline → edit → generate-from-outline
- **Single-command workflow**: generate-doc (full pipeline)
- **Flag combinations**: --dry-run, --from-outline, --verbose

### Manual Testing (After Automated Tests Pass)

- [ ] Test two-command workflow - verify user can edit outline
- [ ] Test help text - verify clear and useful
- [ ] Test error messages - verify helpful and actionable
- [ ] Test edge cases - verify graceful handling
- [ ] Test on real project - verify production-ready

**Test Coverage Target:** >80% for new code

**Commit Strategy:**
- Commit after each red-green-refactor cycle
- All commits should have passing tests

---

## 🚫 What Gets Punted (Deliberately Excluded)

### ❌ Interactive Outline Editor
- **Why**: Manual JSON editing is sufficient for MVP
- **Examples**: TUI editor, web UI for outline editing
- **Reconsider**: v0.8.0 if users find JSON editing difficult

### ❌ Outline Diffing
- **Why**: v0.7.0 generates fresh each time
- **Examples**: Show what changed between outline versions
- **Reconsider**: v0.8.0 for iterative refinement workflows

### ❌ Configuration Files
- **Why**: CLI args are sufficient for MVP
- **Examples**: .doc-evergreen/config.yaml for defaults
- **Reconsider**: v0.8.0 if users request persistent settings

### ❌ Outline Templates
- **Why**: Generate fresh each time for MVP
- **Examples**: Save/load outline templates for reuse
- **Reconsider**: v0.8.0 for common patterns

### ❌ Batch Generation
- **Why**: Single doc for v0.7.0
- **Examples**: Generate multiple docs from multiple outlines
- **Reconsider**: v0.8.0 if users need multi-doc workflows

---

## 📋 Dependencies

### Requires from previous sprints:
- **Sprints 1-6**: Complete pipeline (all functionality)
- **Sprint 5**: Outline validation logic
- **Sprint 6**: Document generation logic

### Provides:
- **Production-ready CLI** for users
- **User documentation** for README
- **Complete v0.7.0 feature** ready to ship!

---

## ✅ Acceptance Criteria

### Must Have

- ✅ **Two-command workflow works**: generate-outline → edit → generate-from-outline
- ✅ **Single-command workflow works**: generate-doc (full pipeline)
- ✅ **Flags work**: --dry-run, --from-outline
- ✅ **Help text is clear**: Users understand commands and options
- ✅ **Error messages are helpful**: Users know how to fix issues
- ✅ **Edge cases handled**: Graceful failures with recovery guidance
- ✅ **Validation works**: Invalid outlines rejected with clear errors
- ✅ **Tests pass**: >80% coverage, all tests green

### User Experience Targets

- Users understand the two workflows (single-command vs two-command)
- Error messages provide actionable guidance
- Help text includes examples
- Progress feedback throughout
- Clear next steps after each command

### Production Readiness Checklist

- [ ] All commands have help text
- [ ] All error paths have helpful messages
- [ ] Edge cases handled gracefully
- [ ] README updated with usage examples
- [ ] CLI is discoverable (tab completion works)
- [ ] No confusing behaviors or surprises

---

## 🛠️ Technical Approach

### Key Decisions

**Decision 1: Two explicit commands (not single command with complex flags)**
- **Rationale**: Clearer user intent, simpler mental model
- **Alternative considered**: Single command with many flags
- **Why two commands**: Easier to understand, common workflow pattern

**Decision 2: Outline.json in .doc-evergreen/ (not arbitrary path)**
- **Rationale**: Consistent location, easy to find
- **Alternative considered**: User-specified path
- **Why fixed location**: Simplicity, convention over configuration

**Decision 3: JSON for outline format (not YAML)**
- **Rationale**: Already using JSON, consistent with context.json
- **Alternative considered**: YAML (more human-readable)
- **Why JSON**: Consistency, stdlib support

**Decision 4: Validate before generation (fail fast)**
- **Rationale**: Better to fail early with clear message
- **Alternative considered**: Try to generate, fail during generation
- **Why validate first**: Better user experience, clearer errors

### CLI Command Structure

```python
# src/doc_evergreen/cli/forward.py

@cli.group('forward')
def forward_commands():
    """Forward documentation generation (from scratch)."""
    pass

@forward_commands.command('generate-outline')
@click.argument('output_path', type=click.Path())
@click.option('--type', 'doc_type', required=True, type=click.Choice([...]))
@click.option('--purpose', required=True, help='Documentation purpose')
@click.option('--verbose', is_flag=True, help='Show detailed progress')
def generate_outline_cmd(output_path: str, doc_type: str, purpose: str, verbose: bool):
    """Generate outline without creating document."""
    # Implementation

@forward_commands.command('generate-from-outline')
@click.argument('outline_path', type=click.Path(exists=True))
@click.option('--verbose', is_flag=True, help='Show detailed progress')
def generate_from_outline_cmd(outline_path: str, verbose: bool):
    """Generate document from existing outline."""
    # Implementation

@forward_commands.command('generate-doc')
@click.argument('output_path', type=click.Path())
@click.option('--type', 'doc_type', type=click.Choice([...]))
@click.option('--purpose', help='Documentation purpose')
@click.option('--dry-run', is_flag=True, help='Generate outline only')
@click.option('--from-outline', type=click.Path(exists=True), help='Use existing outline')
@click.option('--verbose', is_flag=True, help='Show detailed progress')
def generate_doc_cmd(output_path: str, doc_type: str, purpose: str, dry_run: bool, 
                     from_outline: str, verbose: bool):
    """Generate documentation (full pipeline or partial)."""
    
    if from_outline:
        # Skip to generation from outline
        generate_from_outline_cmd(from_outline, verbose)
    elif dry_run:
        # Generate outline only
        generate_outline_cmd(output_path, doc_type, purpose, verbose)
    else:
        # Full pipeline
        generate_outline_cmd(output_path, doc_type, purpose, verbose)
        outline_path = Path('.doc-evergreen/outline.json')
        generate_from_outline_cmd(str(outline_path), verbose)
```

---

## 🔍 What You Learn

After this sprint, you'll discover:

1. **User workflow preferences**: Do users prefer single-command or two-command?
   - → Informs default behavior in future versions
   
2. **Outline editing patterns**: What do users typically edit?
   - → Could inform outline generation improvements
   
3. **Error frequency**: Which errors are most common?
   - → Prioritizes better validation or defaults
   
4. **Help text effectiveness**: Do users understand the commands?
   - → Guides documentation improvements

---

## 📊 Success Metrics

### Quantitative
- All commands have comprehensive help text
- All error paths have actionable messages
- Test coverage >80%
- Zero confusing behaviors reported in testing

### Qualitative
- Users understand the two workflows
- Error messages help users fix issues
- Help text provides sufficient guidance
- Tool feels polished and production-ready

### User Validation
**Usability test** (with 2-3 users):
1. Give user generate-doc --help - can they understand the command?
2. Ask them to generate outline - do they succeed?
3. Ask them to edit outline - do they know where to find it?
4. Ask them to generate from outline - do they succeed?
5. Introduce error (invalid outline) - can they recover?

**Target**: 80%+ success rate on all tasks

---

## 📅 Implementation Order

### TDD-driven workflow (1-2 days)

**Day 1 (Morning): Two-Command Implementation**
- 🔴 Write failing tests for generate-outline and generate-from-outline
- 🟢 Implement both commands with basic functionality
- 🔵 Refactor: Extract common logic, improve structure
- ✅ Commit: "feat: add two-command workflow"

**Day 1 (Afternoon): Flags & Options**
- 🔴 Write failing tests for --dry-run and --from-outline flags
- 🟢 Implement flags in generate-doc command
- 🔵 Refactor: Unify command handling, improve flow
- ✅ Commit: "feat: add CLI flags for flexible workflows"

**Day 2 (Morning): Validation & Error Handling**
- 🔴 Write failing tests for edge cases and validation
- 🟢 Implement validation and helpful error messages
- 🔵 Refactor: Extract validators, improve error formatting
- ✅ Commit: "feat: add validation and error handling"

**Day 2 (Afternoon): Help Text & Polish**
- 🔴 Write tests for help text content
- 🟢 Implement comprehensive help text with examples
- 🔵 Polish: Improve formatting, add progress feedback
- ✅ Manual usability testing
- ✅ Update README with usage examples
- ✅ Sprint review: Demo production-ready v0.7.0!

**Note:** Each feature follows multiple red-green-refactor micro-cycles

---

## ⚠️ Known Limitations (By Design)

1. **Manual JSON editing** - No GUI or TUI editor
   - Why acceptable: JSON editing is common workflow, users have tools
   
2. **Fixed outline location** - .doc-evergreen/outline.json
   - Why acceptable: Convention over configuration, simpler
   
3. **No outline versioning** - Overwrites on each generation
   - Why acceptable: Users can manually save copies if needed
   
4. **No incremental update** - Full regeneration each time
   - Why acceptable: v0.7.0 is "generate from scratch" focused

---

## 🎯 Definition of Done (v0.7.0 Complete!)

After Sprint 7, v0.7.0 is **DONE** when:

- ✅ **Full end-to-end workflow works**: CLI → outline → doc
- ✅ **Two-command workflow works**: generate-outline → edit → generate-from-outline
- ✅ **All acceptance criteria met**: From convergence session
- ✅ **All tests pass**: >80% coverage across all sprints
- ✅ **README updated**: With generate-doc usage examples
- ✅ **Production-ready**: Can be shipped to users
- ✅ **Dogfood successful**: Can generate doc-evergreen's own docs

### Final Validation

**Generate doc-evergreen's own README:**
```bash
$ cd /path/to/doc-evergreen

$ doc-evergreen generate-doc README.md \
    --type tutorial \
    --purpose "Help developers adopt doc-evergreen for their projects"

[... full pipeline runs ...]

✅ README.md created (500 lines)

# Review output - is it good?
# - 80%+ outline quality? ✓
# - Content makes sense? ✓
# - Would ship with minor edits? ✓
```

**If dogfood succeeds → v0.7.0 is DONE! 🎉**

---

## 🎉 Sprint 7 Delivers

**For users:**
- Production-ready generate-doc command
- Clear documentation and help text
- Flexible workflows (single or two-command)
- Graceful error handling

**For v0.7.0:**
- Complete feature implementation
- All acceptance criteria met
- Ready to ship!

**For doc-evergreen:**
- Solves "no existing docs" problem ✓
- Complements v0.6.0 reverse templates ✓
- Delivers core innovation (hierarchical outline) ✓

**Next after v0.7.0:** v0.8.0 can focus on refinements, performance, advanced features!
