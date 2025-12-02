# Template Quality & Customization

This guide explains what to expect from doc-evergreen's bundled templates and how to customize them for your needs.

---

## Expected Behavior

The bundled templates provide **starting points** for documentation generation. They have been validated to:

- ✅ Generate successfully on typical Python projects
- ✅ Include all expected sections as defined in the template
- ✅ Produce reasonable output lengths (within estimated ranges)
- ✅ Follow the Divio Documentation System framework
- ✅ Pass comprehensive automated tests

**Validation**: All 9 templates have been tested on doc-evergreen itself and validated for structural correctness, appropriate prompts, and sensible source selections. See [VALIDATION_REPORT.md](../.amplifier/convergent-dev/sprints/v0.5.0-template-library/VALIDATION_REPORT.md) for details.

---

## Known Limitations

### Prompt Engineering is Empirical

**What this means**:
- LLM output is non-deterministic (same prompt may produce slightly different results each time)
- Templates work best on projects similar to doc-evergreen (Python projects with clear structure)
- You may need to adjust prompts for your specific project, domain, or documentation style

**Why this is acceptable**:
- Templates provide 80% of what most projects need
- Customization is expected and encouraged
- Prompt refinement is an iterative process

**What to do**:
- Generate documentation and review the output
- Adjust prompts in `.doc-evergreen/` if needed
- Iterate until you get the results you want

### Output Variability

**Length may vary based on**:
- Project complexity and size
- Source code clarity and structure
- LLM model being used (different models produce different lengths)
- Specific content in your codebase

**Content quality depends on**:
- Source code clarity (well-documented code → better docs)
- Project structure (clear organization → clearer docs)
- Prompt specificity (more specific prompts → more targeted output)

**Section relevance varies by**:
- Project type (CLI tools vs libraries vs web apps)
- Documentation needs (internal vs external, technical vs user-facing)
- Audience (developers vs end users)

### Template Applicability

**Best for**:
- Python projects (templates designed with Python in mind)
- Projects with conventional structure (README, pyproject.toml, etc.)
- Open source projects (assuming public repository patterns)

**May need adjustment for**:
- Non-Python projects (different file patterns, conventions)
- Monorepos or unconventional structures
- Closed-source projects with different documentation needs
- Domain-specific terminology or conventions

---

## Customization Guide

After running `doc-evergreen init`, the template is copied to `.doc-evergreen/` in your project. **This copy is yours to modify freely.**

### Common Customizations

#### 1. Adjust Prompt Length Guidance

**Example**: Make a section shorter
```json
{
  "heading": "## Installation",
  "prompt": "Provide brief installation instructions (2-3 paragraphs): prerequisites, installation command, verification."
}
```

Change to more detailed:
```json
{
  "heading": "## Installation",
  "prompt": "Provide detailed installation instructions (6-8 paragraphs): prerequisites with versions, multiple installation methods, configuration options, verification steps, troubleshooting."
}
```

#### 2. Add Domain-Specific Instructions

**Example**: Add context about your domain
```json
{
  "heading": "## Usage",
  "prompt": "Provide usage examples for machine learning model deployment (4-5 paragraphs): loading models, making predictions, batch processing, monitoring. Include code examples using our MLOps framework."
}
```

#### 3. Modify Source Selections

**Example**: Focus on specific directories
```json
{
  "sources": ["src/**/*.py"]
}
```

Change to more targeted:
```json
{
  "sources": ["src/api/**/*.py", "src/models/**/*.py"]
}
```

#### 4. Add or Remove Sections

**Example**: Add a new section
```json
{
  "sections": [
    {
      "heading": "## Security Considerations",
      "prompt": "Document security best practices (3-4 paragraphs): authentication, authorization, data protection, common vulnerabilities.",
      "sources": ["docs/SECURITY.md", "src/auth/**/*.py"]
    }
  ]
}
```

#### 5. Adjust Tone and Style

**Example**: Make more formal
```json
{
  "prompt": "Provide technical overview (3-4 paragraphs). Use formal, precise language. Focus on architectural decisions and design rationale."
}
```

Or more casual:
```json
{
  "prompt": "Explain how this works (3-4 paragraphs). Keep it friendly and conversational. Use examples and analogies."
}
```

---

## Prompt Engineering Best Practices

### Be Explicit About Length

✅ **Good**: "Provide 3-5 paragraphs"  
❌ **Bad**: "Be brief"

✅ **Good**: "List 5-7 key features as bullet points"  
❌ **Bad**: "List features"

### Specify What to Include/Exclude

✅ **Good**: "Focus on core functionality. Skip advanced features and edge cases."  
❌ **Bad**: "Explain the functionality"

✅ **Good**: "Include installation, basic usage, and common troubleshooting. Do not include API reference."  
❌ **Bad**: "Cover everything users need to know"

### Give Structure Hints

✅ **Good**: "Format as numbered steps: 1) Prerequisites, 2) Installation, 3) Verification"  
❌ **Bad**: "Explain installation"

✅ **Good**: "Group by category with subheadings: Core features, Advanced features, Utilities"  
❌ **Bad**: "List all features"

### Match Sources to Section Purpose

✅ **Good**: API section uses `["src/**/*.py"]`  
❌ **Bad**: API section uses `["README.md"]`

✅ **Good**: Overview uses `["README.md", "pyproject.toml"]`  
❌ **Bad**: Overview uses `["src/**/*.py"]` (too detailed for overview)

---

## Troubleshooting

### Output Too Long

**Symptoms**: Generated documentation is 2-3x longer than expected

**Solutions**:
1. Add explicit length constraints: "3-5 paragraphs" → "2-3 paragraphs"
2. Add scope limitations: "Focus only on X, Y, Z"
3. Add exclusions: "Skip advanced features, edge cases, and detailed API docs"
4. Narrow source selections: `["src/**/*.py"]` → `["src/core/*.py"]`

### Output Too Short or Generic

**Symptoms**: Generated documentation is vague, missing details, or too brief

**Solutions**:
1. Increase length guidance: "2-3 paragraphs" → "5-7 paragraphs"
2. Request more detail: "Include examples, edge cases, and detailed explanations"
3. Broaden source selections: Add more relevant source files
4. Be more specific in prompts: "Reference actual classes and functions from the code"

### Output Not Relevant

**Symptoms**: Generated content doesn't match project or includes hallucinations

**Solutions**:
1. Review source selections: Are you including the right files?
2. Add context to prompts: "Based on the FastAPI framework" or "For command-line tools"
3. Be more specific: "Document the DatabaseManager class specifically"
4. Verify sources exist: Check that files referenced in `sources` actually exist

### Inconsistent Output

**Symptoms**: Running `regen-doc` multiple times produces very different results

**Solutions**:
1. Add more structure to prompts: Specify format, order, number of items
2. Make prompts less open-ended: "Exactly 5 features" vs "List features"
3. LLM output is inherently variable - some variation is normal
4. Consider if variability is actually a problem (different ≠ wrong)

---

## Template Evolution

### Post-v0.5.0 Improvements

Templates will evolve based on user feedback and real-world usage:

- **Prompt refinement**: Adjust based on common issues reported
- **New templates**: Add templates for common project types or domains
- **Template versioning**: Track changes if breaking updates needed
- **Best practices**: Document patterns that work well

### Contributing Template Improvements

If you develop useful customizations or new templates:
1. Share your template in GitHub Discussions
2. Submit a PR with your template and use case description
3. Document what problem it solves and why it's better

### Philosophy

Doc-evergreen follows a **trust-but-verify** approach:
- Templates are opinionated starting points (not universal solutions)
- Customization is expected (not a fallback)
- Quality emerges through iteration (not upfront perfection)
- User feedback drives improvement (not theoretical optimization)

---

## Summary

**Templates are tools, not magic solutions.** They provide excellent starting points that work for 80% of projects. For the remaining 20%, customization is your friend.

**Key Takeaways**:
- ✅ Templates work best on projects similar to doc-evergreen (Python, conventional structure)
- ✅ Some customization is normal and expected
- ✅ LLM output varies - iteration is part of the process
- ✅ You control the templates - modify them freely
- ✅ Report issues and share improvements with the community

**When in doubt**: Generate → Review → Adjust prompts → Regenerate → Repeat

Happy documenting! 📚
