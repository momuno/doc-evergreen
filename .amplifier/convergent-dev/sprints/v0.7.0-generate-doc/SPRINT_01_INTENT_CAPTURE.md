# Sprint 1: Intent Capture & CLI Foundation

**Duration:** 1-2 days  
**Goal:** User can specify doc type and purpose via CLI  
**Value Delivered:** Working command that captures user intent immediately

---

## 🎯 Why This Sprint?

Before any intelligence can work, we need to know WHAT the user wants to generate. This sprint establishes the foundation by capturing:
1. **Doc type** (tutorial/howto/reference/explanation) - guides structure
2. **Purpose** (freeform text) - guides content selection
3. **Output path** - where to write the generated doc

This is a quick win (1-2 days) that provides immediate value and sets up all downstream features.

---

## 📦 Deliverables

### 1. CLI Command Structure
**Estimated Lines:** ~150 lines + 100 lines tests

**What it does:**
- Adds `generate-doc` subcommand to doc-evergreen CLI
- Accepts required arguments: output path, doc type, purpose
- Validates doc type against Diataxis types
- Provides clear help text and error messages

**Why this sprint:**
- Users need a working command immediately
- Sets the API contract for the entire feature
- Enables testing of downstream features

**Implementation notes:**
- Use Click framework (consistent with existing CLI)
- Follow existing command patterns from v0.6.0
- Doc type validation: tutorial, howto, reference, explanation
- Purpose is freeform text (no validation)

**CLI signature:**
```bash
doc-evergreen generate-doc <output-path> \
  --type <doc-type> \
  --purpose <purpose-description>
```

**Example usage:**
```bash
doc-evergreen generate-doc README.md \
  --type tutorial \
  --purpose "Help developers get started in 5 minutes"
```

### 2. Intent Context Storage
**Estimated Lines:** ~80 lines + 60 lines tests

**What it does:**
- Creates `.doc-evergreen/` directory if doesn't exist
- Stores intent context in `.doc-evergreen/context.json`
- JSON structure includes: doc_type, purpose, output_path, timestamp

**Why this sprint:**
- Downstream features need access to user intent
- Enables resume/retry workflows
- Provides audit trail of generation parameters

**Implementation notes:**
- Use JSON for serialization (human-readable, editable)
- Include timestamp for versioning/debugging
- Validate context can be read back correctly

**Context JSON structure:**
```json
{
  "version": "0.7.0",
  "doc_type": "tutorial",
  "purpose": "Help developers get started in 5 minutes",
  "output_path": "README.md",
  "timestamp": "2025-12-06T23:14:17Z",
  "status": "intent_captured"
}
```

### 3. Doc Type Validation Module
**Estimated Lines:** ~100 lines + 80 lines tests

**What it does:**
- Validates doc type against Diataxis framework
- Provides helpful error messages for invalid types
- Includes doc type descriptions for help text

**Why this sprint:**
- Ensures downstream features receive valid input
- Educates users about doc types
- Prevents confusing errors later in pipeline

**Implementation notes:**
- Enum or constants for valid doc types
- Rich error messages with examples
- Help text explaining each doc type

**Diataxis types:**
- **tutorial**: Learning-oriented, step-by-step lessons
- **howto**: Goal-oriented, practical guides
- **reference**: Information-oriented, technical descriptions
- **explanation**: Understanding-oriented, conceptual discussions

---

## 🧪 Testing Requirements

### TDD Approach

Follow red-green-refactor cycle for all features:

#### 1. 🔴 RED - Write Failing Tests First

**CLI Command Tests:**
```python
def test_generate_doc_requires_output_path():
    # Test that command fails without output path
    result = runner.invoke(cli, ['generate-doc'])
    assert result.exit_code != 0
    assert 'output path' in result.output.lower()

def test_generate_doc_requires_type():
    # Test that --type is required
    result = runner.invoke(cli, ['generate-doc', 'README.md'])
    assert result.exit_code != 0
    assert 'type' in result.output.lower()

def test_generate_doc_validates_type():
    # Test that invalid doc type is rejected
    result = runner.invoke(cli, [
        'generate-doc', 'README.md',
        '--type', 'invalid-type',
        '--purpose', 'Test purpose'
    ])
    assert result.exit_code != 0
    assert 'invalid-type' in result.output
```

**Context Storage Tests:**
```python
def test_context_json_created():
    # Test that context.json is created in .doc-evergreen/
    runner.invoke(cli, [
        'generate-doc', 'README.md',
        '--type', 'tutorial',
        '--purpose', 'Test purpose'
    ])
    assert Path('.doc-evergreen/context.json').exists()

def test_context_json_contains_intent():
    # Test that context includes all required fields
    runner.invoke(cli, [...])
    with open('.doc-evergreen/context.json') as f:
        context = json.load(f)
    assert context['doc_type'] == 'tutorial'
    assert context['purpose'] == 'Test purpose'
    assert context['output_path'] == 'README.md'
```

Run tests → Watch them fail → Good!

#### 2. 🟢 GREEN - Write Minimal Implementation

```python
@cli.command('generate-doc')
@click.argument('output_path')
@click.option('--type', required=True, help='Doc type: tutorial, howto, reference, explanation')
@click.option('--purpose', required=True, help='Description of doc purpose')
def generate_doc(output_path: str, type: str, purpose: str):
    """Generate documentation from scratch."""
    
    # Validate doc type
    if type not in ['tutorial', 'howto', 'reference', 'explanation']:
        raise click.BadParameter(f"Invalid doc type: {type}")
    
    # Create .doc-evergreen directory
    Path('.doc-evergreen').mkdir(exist_ok=True)
    
    # Store context
    context = {
        'version': '0.7.0',
        'doc_type': type,
        'purpose': purpose,
        'output_path': output_path,
        'timestamp': datetime.now().isoformat() + 'Z',
        'status': 'intent_captured'
    }
    
    with open('.doc-evergreen/context.json', 'w') as f:
        json.dump(context, f, indent=2)
    
    click.echo(f"✅ Intent captured: {type} - {purpose}")
    click.echo(f"📝 Context saved to .doc-evergreen/context.json")
```

Run tests → Watch them pass → Good!

#### 3. 🔵 REFACTOR - Improve Code Quality

- Extract doc type validation to separate function
- Create DocType enum for type safety
- Add context save/load utilities
- Improve error messages
- Add logging

Run tests → Still pass → Good!

### Unit Tests (Write First)

- **CLI argument parsing**: Required args, optional args, validation
- **Doc type validation**: Valid types, invalid types, error messages
- **Context storage**: File creation, JSON structure, read/write
- **Path handling**: Absolute paths, relative paths, invalid paths
- **Error handling**: Missing args, invalid types, file permissions

### Integration Tests (Write First)

- **End-to-end CLI**: Run command, verify context.json created
- **Context persistence**: Write context, read back, verify contents
- **Error scenarios**: Invalid args, permission errors, edge cases

### Manual Testing (After Automated Tests Pass)

- [ ] Run command with tutorial type - verify friendly output
- [ ] Run command with invalid type - verify helpful error message
- [ ] Run command without purpose - verify clear error
- [ ] Check .doc-evergreen/context.json - verify human-readable format
- [ ] Run command twice - verify context is overwritten correctly

**Test Coverage Target:** >80% for new code

**Commit Strategy:**
- Commit after each red-green-refactor cycle
- All commits should have passing tests

---

## 🚫 What Gets Punted (Deliberately Excluded)

### ❌ Repository Indexing
- **Why**: That's Sprint 2 - separate concern
- **Reconsider**: Sprint 2 implementation

### ❌ File Relevance Analysis
- **Why**: Sprint 3 - needs repo index first
- **Reconsider**: Sprint 3 implementation

### ❌ Outline Generation
- **Why**: Core innovation for Sprint 4-5, needs supporting features first
- **Reconsider**: Sprint 4 after foundation is solid

### ❌ Advanced CLI Options
- **Why**: Keep it simple for MVP, add polish in Sprint 7
- **Examples**: --verbose, --dry-run, --config-file
- **Reconsider**: Sprint 7 polish phase

### ❌ Input Validation Beyond Doc Type
- **Why**: Purpose is freeform by design, validate later if needed
- **Reconsider**: Post-v0.7.0 if users provide problematic input

### ❌ Context Versioning/Migration
- **Why**: v0.7.0 is first version, no migration needed
- **Reconsider**: v0.8.0 when context format changes

---

## 📋 Dependencies

### Requires from previous sprints:
- None (this is Sprint 1 - foundation)

### Provides for future sprints:
- **context.json** for Sprint 2 (repo indexing uses doc_type and purpose)
- **CLI command** for Sprint 3+ (all features extend this command)
- **Doc type** for Sprint 4-5 (outline generation is doc-type-aware)

---

## ✅ Acceptance Criteria

### Must Have

- ✅ **CLI command works**: `doc-evergreen generate-doc README.md --type tutorial --purpose "..."`
- ✅ **Doc type validation**: Accepts only valid Diataxis types, rejects others
- ✅ **Context storage**: Creates `.doc-evergreen/context.json` with all required fields
- ✅ **Clear feedback**: User sees confirmation of intent capture
- ✅ **Error handling**: Helpful messages for missing/invalid arguments
- ✅ **Tests pass**: >80% coverage, all tests green

### Nice to Have (Defer if time constrained)

- ❌ **Interactive mode**: Prompt for type/purpose if not provided (defer to Sprint 7)
- ❌ **Config file**: Load defaults from .doc-evergreen/config.yaml (defer to Sprint 7)
- ❌ **Verbose mode**: Show detailed context information (defer to Sprint 7)

---

## 🛠️ Technical Approach

### Key Decisions

**Decision 1: Use Click framework**
- **Rationale**: Consistent with existing doc-evergreen CLI (v0.6.0 uses Click)
- **Alternative considered**: argparse (stdlib, but less powerful)
- **Why Click**: Better help text, automatic validation, decorator syntax

**Decision 2: Store context as JSON**
- **Rationale**: Human-readable, editable, widely supported
- **Alternative considered**: YAML (more readable) or binary (faster)
- **Why JSON**: Simplicity, stdlib support, good enough for small files

**Decision 3: Use Diataxis framework for doc types**
- **Rationale**: Well-established, clear categories, widely adopted
- **Alternative considered**: Custom taxonomy (reinventing wheel)
- **Why Diataxis**: Industry standard, user-facing documentation

**Decision 4: Make purpose freeform text**
- **Rationale**: Can't predict all use cases, let users express naturally
- **Alternative considered**: Structured templates (too restrictive)
- **Why freeform**: Maximum flexibility, better LLM input

### Implementation Pattern

```python
# src/doc_evergreen/cli/generate_doc.py

from enum import Enum
from pathlib import Path
import json
from datetime import datetime
import click

class DocType(str, Enum):
    """Diataxis documentation types."""
    TUTORIAL = "tutorial"
    HOWTO = "howto"
    REFERENCE = "reference"
    EXPLANATION = "explanation"

def save_context(doc_type: DocType, purpose: str, output_path: str) -> Path:
    """Save generation context to .doc-evergreen/context.json."""
    context_dir = Path('.doc-evergreen')
    context_dir.mkdir(exist_ok=True)
    
    context = {
        'version': '0.7.0',
        'doc_type': doc_type.value,
        'purpose': purpose,
        'output_path': output_path,
        'timestamp': datetime.now().isoformat() + 'Z',
        'status': 'intent_captured'
    }
    
    context_path = context_dir / 'context.json'
    with open(context_path, 'w') as f:
        json.dump(context, f, indent=2)
    
    return context_path

@click.command('generate-doc')
@click.argument('output_path', type=click.Path())
@click.option(
    '--type',
    'doc_type',
    type=click.Choice([t.value for t in DocType]),
    required=True,
    help='Documentation type (Diataxis framework)'
)
@click.option(
    '--purpose',
    required=True,
    help='Description of documentation purpose'
)
def generate_doc(output_path: str, doc_type: str, purpose: str):
    """Generate documentation from scratch.
    
    Examples:
    
      Generate a tutorial README:
      
        $ doc-evergreen generate-doc README.md \\
            --type tutorial \\
            --purpose "Help developers get started in 5 minutes"
    
      Generate a reference guide:
      
        $ doc-evergreen generate-doc docs/API.md \\
            --type reference \\
            --purpose "Complete API reference"
    """
    click.echo(f"🎯 Generating {doc_type} documentation...")
    click.echo(f"📝 Purpose: {purpose}")
    click.echo(f"📄 Output: {output_path}")
    
    # Save context
    context_path = save_context(DocType(doc_type), purpose, output_path)
    
    click.echo(f"✅ Intent captured!")
    click.echo(f"📋 Context saved to {context_path}")
    click.echo()
    click.echo("⏭️  Next: Repository indexing (Sprint 2)")
```

---

## 🔍 What You Learn

After this sprint, you'll discover:

1. **User intent patterns**: How users describe their documentation needs
   - → Informs Sprint 4-5 outline generation prompts
   
2. **Doc type usage**: Which Diataxis types are most common
   - → Validates framework choice, informs testing priorities
   
3. **CLI ergonomics**: What arguments feel natural vs. awkward
   - → Guides Sprint 7 polish decisions
   
4. **Context structure**: What metadata is actually needed downstream
   - → May inform context schema evolution in Sprint 2-3

---

## 📊 Success Metrics

### Quantitative
- Command runs successfully with valid input (100% of test cases)
- All required fields captured in context.json (100%)
- Test coverage >80%
- Command response time <100ms (instant feedback)

### Qualitative
- Users understand what the command does (clear help text)
- Error messages are helpful (users know how to fix issues)
- Context.json is human-readable (users can inspect/edit)
- Command feels consistent with existing CLI (familiar patterns)

---

## 📅 Implementation Order

### TDD-driven daily workflow

**Day 1 (Morning): CLI Command Structure**
- 🔴 Write failing tests for CLI argument parsing
- 🟢 Implement basic Click command with required args
- 🔵 Refactor: Extract validation, improve error messages
- ✅ Commit: "feat: add generate-doc CLI command"

**Day 1 (Afternoon): Doc Type Validation**
- 🔴 Write failing tests for doc type validation
- 🟢 Implement DocType enum and validation logic
- 🔵 Refactor: Add helpful error messages with examples
- ✅ Commit: "feat: add Diataxis doc type validation"

**Day 2 (Morning): Context Storage**
- 🔴 Write failing tests for context.json creation
- 🟢 Implement save_context() function
- 🔵 Refactor: Extract context utilities, add logging
- ✅ Commit: "feat: add intent context storage"

**Day 2 (Afternoon): Integration & Polish**
- 🔴 Write integration tests for end-to-end workflow
- 🟢 Wire CLI → validation → storage together
- 🔵 Polish: Improve feedback messages, add examples
- ✅ Manual testing & final commit
- ✅ Sprint review: Demo working command

**Note:** Each feature follows multiple red-green-refactor micro-cycles

---

## ⚠️ Known Limitations (By Design)

1. **No actual generation yet** - Command captures intent only
   - Why acceptable: Foundation for Sprint 2+, delivers value through clear workflow start
   
2. **No validation of purpose text** - Freeform input accepted
   - Why acceptable: LLM handles variety well, over-constraining reduces usefulness
   
3. **Context overwrites previous runs** - No versioning yet
   - Why acceptable: Single-doc generation for v0.7.0, multi-doc is future work
   
4. **No resume capability** - Can't continue interrupted generation
   - Why acceptable: Generation is fast enough to re-run if needed

---

## 🎯 Next Sprint Preview

After this sprint ships, the most pressing need will be:

**Sprint 2: Repository Indexing** - Now that we know WHAT to generate, we need to discover WHAT FILES exist in the project. Sprint 2 will build the file inventory and traversal structure that feeds Sprint 3's relevance analysis.

The intent captured in Sprint 1's context.json becomes the filter for Sprint 2's indexing decisions (respect .gitignore, focus on code files relevant to documentation).
