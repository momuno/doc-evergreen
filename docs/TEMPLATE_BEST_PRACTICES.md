# Template Best Practices Guide

**Learn how to create effective documentation templates for doc-evergreen.**

This guide captures lessons learned from building the v0.5.0 template library and provides practical guidance for creating your own templates.

---

## Quick Reference

**Creating a good template requires**:
- 📏 Explicit length guidance in prompts
- 🎯 Clear scope constraints (what to include/exclude)
- 📁 Appropriate source selections
- 🏗️ Logical section organization
- 🔄 Iteration based on real output

**Common patterns** → See [Examples](#real-world-examples) section

---

## Understanding the Divio Documentation System

The bundled templates follow the [Divio Documentation System](https://docs.divio.com/documentation-system/), which organizes documentation into 4 quadrants:

### 📚 Tutorials (Learning-oriented)
**Purpose**: Take users on a learning journey  
**Characteristics**: Step-by-step, beginner-friendly, confidence-building  
**Example**: `tutorial-quickstart` - Get started in 5 minutes

**When to use**: New users need to learn by doing

### 🎯 How-To Guides (Goal-oriented)
**Purpose**: Show how to solve specific problems  
**Characteristics**: Practical recipes, task-focused, assumes basic knowledge  
**Example**: `howto-ci-integration` - Add doc-evergreen to your CI pipeline

**When to use**: Experienced users need to accomplish specific tasks

### 📖 Reference (Information-oriented)
**Purpose**: Provide complete, accurate information  
**Characteristics**: Comprehensive, precise, dry, factual  
**Example**: `reference-cli` - Complete command reference

**When to use**: Users need to look up details

### 💡 Explanation (Understanding-oriented)
**Purpose**: Help users understand concepts and design  
**Characteristics**: Philosophical, contextual, explanatory  
**Example**: `explanation-architecture` - Why the system works this way

**When to use**: Users need to build mental models

**Key insight**: Different documentation types need different writing styles and content. Don't mix them.

---

## Template Anatomy

A doc-evergreen template has two main parts:

### 1. Metadata (`_meta`)

```json
{
  "_meta": {
    "name": "my-template",
    "description": "Brief description for CLI display",
    "use_case": "When to use this template",
    "quadrant": "tutorial | howto | reference | explanation",
    "estimated_lines": "200-400 lines"
  }
}
```

**Best practices**:
- Choose descriptive name (lowercase, hyphens)
- Description should be < 10 words
- Use case answers "When would I use this?"
- Quadrant guides tone and style
- Estimated lines sets expectations

### 2. Document Structure

```json
{
  "document": {
    "title": "Document Title",
    "output": "OUTPUT.md",
    "sections": [
      {
        "heading": "## Section Name",
        "prompt": "Detailed instructions for LLM...",
        "sources": ["relevant/files/**"]
      }
    ]
  }
}
```

**Best practices**:
- 4-7 sections for most templates (not too few, not too many)
- Logical progression (overview → details → conclusion)
- Each section has focused purpose
- Output path follows conventions (README.md, docs/*.md)

---

## Prompt Engineering Essentials

### Pattern 1: Explicit Length Guidance

**Problem**: LLM generates too much or too little content

**Solution**: Specify exact amounts

✅ **Good examples**:
- "3-5 paragraphs"
- "5-7 bullet points with 1-2 sentence explanations"
- "2-3 code examples with commentary"
- "4-6 paragraphs covering X, Y, and Z"

❌ **Bad examples**:
- "Be brief" (too vague)
- "Write a lot" (no upper bound)
- "Comprehensive" (undefined scope)

### Pattern 2: Scope Constraints

**Problem**: LLM includes irrelevant or excessive detail

**Solution**: Explicitly state what to include/exclude

✅ **Good examples**:
- "Focus on installation and basic usage. Skip advanced features."
- "Common use cases only. Do not include edge cases or troubleshooting."
- "Cover prerequisites, installation, and verification. Exclude detailed API docs."

❌ **Bad examples**:
- "Explain everything" (too broad)
- "Make it useful" (subjective)

### Pattern 3: Structure Hints

**Problem**: Output is unorganized or inconsistent

**Solution**: Specify format and structure

✅ **Good examples**:
- "Format as numbered steps: (1) Prerequisites, (2) Installation, (3) Verification"
- "Group by category with subheadings: Core features, Advanced features, Utilities"
- "Present in alphabetical order"
- "List format with feature name followed by 1-2 sentence explanation"

❌ **Bad examples**:
- "Organize well" (no guidance)
- "Make it clear" (subjective)

### Pattern 4: Context and Tone

**Problem**: Writing style doesn't match documentation type

**Solution**: Specify tone and approach

✅ **Good examples**:
- "Be encouraging and beginner-friendly" (tutorials)
- "Be precise and technical" (reference)
- "Be philosophical and explanatory" (explanation)
- "Be practical and action-oriented" (how-to)

❌ **Bad examples**:
- "Be good" (meaningless)
- "Write professionally" (vague)

---

## Source Selection Strategy

### Match Sources to Section Purpose

| Section Type | Good Sources | Poor Sources |
|-------------|--------------|--------------|
| Overview | README.md, pyproject.toml | src/**/*.py (too detailed) |
| API Reference | src/**/*.py | README.md (too high-level) |
| Installation | pyproject.toml, setup.py | tests/** (irrelevant) |
| Usage Examples | examples/**, README.md | internal implementation files |
| Architecture | docs/**, src/**/core.py | test files, config files |

### Source Selection Rules

1. **Be specific over broad**: `src/core/*.py` > `src/**/*.py`
2. **Match detail level**: High-level sections use high-level sources
3. **Avoid information overload**: 5-10 files is usually enough
4. **Check files exist**: Verify paths are correct for your project
5. **Consider context limits**: Too many sources may hit LLM limits

### Common Patterns

```json
// Overview / Introduction
"sources": ["README.md", "pyproject.toml", "docs/overview.md"]

// Installation / Setup
"sources": ["pyproject.toml", "setup.py", "README.md", "docs/installation.md"]

// API Documentation
"sources": ["src/**/*.py"]  // OK if codebase is small
"sources": ["src/core/*.py", "src/api/*.py"]  // Better for larger projects

// Usage Examples
"sources": ["examples/**", "tests/**/test_*.py", "README.md"]

// Contributing Guidelines
"sources": ["CONTRIBUTING.md", "README.md", ".github/workflows/**", "pyproject.toml"]

// Architecture
"sources": ["docs/**", "README.md", "src/**/core.py"]
```

---

## Real-World Examples

### Example 1: Tutorial Template

```json
{
  "_meta": {
    "name": "tutorial-quickstart",
    "description": "Brief quickstart guide for new users",
    "use_case": "New users need to get started in 5 minutes",
    "quadrant": "tutorial",
    "estimated_lines": "200-400 lines"
  },
  "document": {
    "title": "Quick Start Guide",
    "output": "QUICKSTART.md",
    "sections": [
      {
        "heading": "# Quick Start",
        "prompt": "Write a friendly 5-minute getting started guide (3-4 paragraphs). Cover: (1) What this project does in one sentence, (2) Prerequisites (just the essentials), (3) One-command installation, (4) Simplest possible first example. Be encouraging and beginner-friendly. Skip edge cases.",
        "sources": ["README.md", "pyproject.toml", "examples/**"]
      }
    ]
  }
}
```

**Why this works**:
- ✅ Explicit length: "3-4 paragraphs"
- ✅ Structure: "(1), (2), (3), (4)"
- ✅ Scope: "just the essentials", "skip edge cases"
- ✅ Tone: "friendly", "encouraging", "beginner-friendly"
- ✅ Sources: High-level overview files

### Example 2: How-To Template

```json
{
  "heading": "## Development Setup",
  "prompt": "Step-by-step development environment setup (5-6 paragraphs): (1) Prerequisites with versions, (2) Installation commands in order, (3) Running tests, (4) Code formatting tools, (5) Pre-commit hooks if used, (6) Common troubleshooting. Focus on common path, note platform differences if critical.",
  "sources": ["README.md", "pyproject.toml", "setup.py", ".github/workflows/**"]
}
```

**Why this works**:
- ✅ Length: "5-6 paragraphs"
- ✅ Structure: Numbered steps
- ✅ Scope: "common path", "note platform differences if critical"
- ✅ Tone: Procedural, action-oriented
- ✅ Sources: Setup-related files

### Example 3: Reference Template

```json
{
  "heading": "## Commands",
  "prompt": "Comprehensive command reference (one subsection per command). For each command document: (1) Synopsis with syntax, (2) Description, (3) All options with types and defaults, (4) Exit codes, (5) Two example usages (basic and advanced). Be thorough and structured. Present in alphabetical order.",
  "sources": ["src/**/cli.py", "README.md"]
}
```

**Why this works**:
- ✅ Completeness: "Comprehensive", "all options"
- ✅ Structure: "(1), (2), (3), (4), (5)", "alphabetical order"
- ✅ Tone: "thorough", "structured" (reference style)
- ✅ Sources: CLI implementation files

---

## Iteration Workflow

**Creating a good template is iterative**:

1. **Start simple**: Basic structure, best-guess prompts
2. **Generate**: Run `doc-evergreen init --template your-template`
3. **Review**: Check output quality, length, relevance
4. **Identify issues**: Too long? Too short? Off-topic?
5. **Refine prompts**: Adjust length, scope, or sources
6. **Regenerate**: Test the changes
7. **Repeat**: Until output meets your needs

**Common refinement cycles**:

| Issue | First Try | After Refinement |
|-------|-----------|------------------|
| Too long (500 lines expected, 1200 actual) | "Explain usage" | "Explain usage (4-5 paragraphs): basic workflow, 2-3 common examples. Skip advanced features." |
| Too short (400 lines expected, 100 actual) | "Document API" | "Document API (10-15 paragraphs): For each major class: purpose, constructor params, key methods with examples. Be comprehensive." |
| Off-topic | "Explain features" | "Explain user-facing features only. Focus on what users can do, not implementation details. Examples: X, Y, Z." |

---

## Common Mistakes to Avoid

### ❌ Vague Prompts
**Bad**: "Write good documentation about this"  
**Good**: "Write beginner-friendly tutorial (3-5 paragraphs) covering installation and first example"

### ❌ No Length Guidance
**Bad**: "Explain the API"  
**Good**: "Document main API classes (8-12 paragraphs, one per class)"

### ❌ Wrong Sources
**Bad**: API section using only README.md  
**Good**: API section using `src/**/*.py`

### ❌ Mixed Documentation Types
**Bad**: Tutorial that includes complete API reference  
**Good**: Tutorial focuses on learning path, links to separate API reference

### ❌ Too Many Sections
**Bad**: 15 sections in one template  
**Good**: 5-7 focused sections, or split into multiple templates

---

## Template Design Checklist

Before finalizing a template, verify:

**Metadata**:
- [ ] Name is descriptive and follows naming convention
- [ ] Description is concise (< 10 words)
- [ ] Use case clearly states when to use this template
- [ ] Quadrant is correct (tutorial/howto/reference/explanation)
- [ ] Estimated lines are realistic

**Structure**:
- [ ] 4-7 sections (appropriate for content)
- [ ] Sections follow logical order
- [ ] Each section has focused purpose
- [ ] Output path follows conventions

**Prompts**:
- [ ] Every prompt has explicit length guidance
- [ ] Scope is clearly defined (what to include/exclude)
- [ ] Structure hints provided where needed
- [ ] Tone matches documentation type

**Sources**:
- [ ] Sources match section purpose
- [ ] File paths are correct for typical projects
- [ ] Not too many sources (5-10 per section)
- [ ] Appropriate detail level

**Testing**:
- [ ] Generated output on at least one project
- [ ] Output length is within estimated range
- [ ] Content is relevant and useful
- [ ] All sections appear in output

---

## Advanced Techniques

### Conditional Content

Use prompts that adapt to what's available:

```json
{
  "prompt": "Document configuration options (3-4 paragraphs). If config files exist, explain the format and all available options. If no config files, explain that configuration is code-based and show examples.",
  "sources": ["*.json", "*.yaml", "*.toml", "README.md"]
}
```

### Progressive Disclosure

Structure sections from simple to complex:

```json
{
  "sections": [
    {"heading": "## Quick Start", "prompt": "Basic usage in 5 minutes..."},
    {"heading": "## Common Use Cases", "prompt": "5-7 typical workflows..."},
    {"heading": "## Advanced Usage", "prompt": "Complex scenarios..."},
    {"heading": "## API Reference", "prompt": "Complete API documentation..."}
  ]
}
```

### Domain-Specific Templates

Create templates for specific project types:

```json
{
  "_meta": {
    "name": "fastapi-service",
    "description": "Documentation for FastAPI microservices",
    "use_case": "REST API services built with FastAPI",
    "quadrant": "howto",
    "estimated_lines": "400-600 lines"
  }
}
```

---

## Resources

**Official Divio Documentation System**:  
https://docs.divio.com/documentation-system/

**Example Templates**:  
See `src/doc_evergreen/templates/` for all bundled templates

**Template Quality Guide**:  
See [TEMPLATE_QUALITY.md](TEMPLATE_QUALITY.md) for customization guidance

**Troubleshooting**:  
See [TEMPLATE_QUALITY.md - Troubleshooting](TEMPLATE_QUALITY.md#troubleshooting)

---

## Summary

**Key Principles**:
1. **Be explicit**: Specify length, scope, structure
2. **Match sources**: Right files for right sections
3. **Stay focused**: 4-7 sections with clear purposes
4. **Follow Divio**: Use appropriate quadrant and tone
5. **Iterate**: Generate → Review → Refine → Repeat

**Remember**: Templates are starting points. Customization is normal and expected. The best template is one that works for *your* project and *your* documentation needs.

Happy templating! 📚
