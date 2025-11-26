# Sprint 3: Prompt Quality & Testing

**Duration:** 1 week (5 days)
**Goal:** Consistent, appropriate-length output from all templates
**Value Delivered:** Templates produce reliable, predictable, high-quality documentation

---

## Why This Sprint?

**Quality Over Quantity**: Sprint 1-2 built the library. Now we make it production-ready through systematic testing and refinement.

**Data-Driven Refinement**: Test all 6 templates across multiple projects, gather real output data, refine prompts based on actual results (not guesses).

**Solve the Core Problem**: The original pain point was "996-line READMEs." This sprint ensures templates consistently produce appropriately-sized docs.

**Production Readiness**: After this sprint, templates are reliable enough for real projects. Sprint 4 focuses on documentation, not functionality.

---

## Deliverables

### 1. Cross-Project Testing Framework
**Estimated Lines:** ~150 lines test infrastructure + data collection

**What it does:**
Systematic testing of all 6 templates across multiple project types to gather real output data.

**Why this sprint:**
- Need real data to guide prompt refinement
- Can't optimize what we don't measure
- Validates templates work beyond doc-evergreen itself

**Implementation approach:**

**Test Projects:**
```python
# Test across diverse project types
TEST_PROJECTS = [
    {
        "name": "doc-evergreen",
        "type": "Python CLI tool",
        "templates": ["readme-concise", "readme-standard", "readme-detailed", 
                     "api-docs", "contributing"]
    },
    {
        "name": "hypothetical-library",  # Or use real open source project
        "type": "Python library",
        "templates": ["readme-standard", "api-docs"]
    },
    {
        "name": "hypothetical-webapp",
        "type": "Python web app",
        "templates": ["readme-standard", "architecture"]
    }
]
```

**Data Collection:**
```python
# For each template + project combination, collect:
test_results = {
    "template": "readme-concise",
    "project": "doc-evergreen",
    "metrics": {
        "total_lines": 450,
        "section_lengths": {
            "Overview": 85,
            "Quick Start": 120,
            "Key Features": 140,
            "Links": 45
        },
        "generation_time": "23s",
        "quality_notes": "Overview slightly long, otherwise good"
    }
}
```

**Output Report:**
```
Template Testing Report
=======================

readme-concise:
  doc-evergreen (Python CLI):
    Lines: 450 ✓ (target: 300-500)
    Issues: Overview section 85 lines (high)
    
  hypothetical-library:
    Lines: 380 ✓ (target: 300-500)
    Issues: None
    
readme-standard:
  doc-evergreen:
    Lines: 720 ⚠ (target: 500-700, actual: 720)
    Issues: Usage section 280 lines (too long)
  
  hypothetical-library:
    Lines: 650 ✓ (target: 500-700)
    Issues: None

... (repeat for all templates)

Summary:
  readme-concise: 2/2 within target ✓
  readme-standard: 1/2 within target ⚠
  readme-detailed: Not tested yet
  api-docs: 1/2 within target ⚠
  architecture: 1/1 within target ✓
  contributing: 1/1 within target ✓
```

**Files to create:**
- `tests/test_cross_project.py` - Cross-project test runner
- `tests/data/test_results.json` - Collected test data
- `.amplifier/convergent-dev/sprints/v0.5.0-template-library/TESTING_REPORT.md` - Human-readable report

---

### 2. Prompt Refinement: Length Control
**Estimated Lines:** Template updates (~50 lines per template)

**What it does:**
Refine all template prompts based on testing data to achieve consistent length targets.

**Why this sprint:**
- Core value proposition: appropriately-sized docs
- Testing data shows which prompts need tightening/expanding
- Ensures templates deliver on promises

**Refinement strategy:**

**Pattern 1: Too Long? Add Scope Constraints**

Before (generates 280 lines):
```json
{
  "heading": "## Usage",
  "prompt": "Provide usage examples. Show common use cases with code examples."
}
```

After (generates 120-150 lines):
```json
{
  "heading": "## Usage",
  "prompt": "Provide concise usage examples (3-5 paragraphs). Show 2-3 common use cases with brief code examples. Focus on essential workflows. Skip advanced features and edge cases."
}
```

**Pattern 2: Too Short? Request More Detail**

Before (generates 45 lines):
```json
{
  "heading": "## Installation",
  "prompt": "Explain installation briefly."
}
```

After (generates 100-120 lines):
```json
{
  "heading": "## Installation",
  "prompt": "Provide installation instructions (4-6 paragraphs): (1) Prerequisites with versions, (2) Installation command with explanation, (3) Basic configuration, (4) Verification step. Include troubleshooting if common issues exist."
}
```

**Pattern 3: Inconsistent? Add Structural Guidance**

Before (varies 80-200 lines):
```json
{
  "heading": "## Features",
  "prompt": "List the key features of this project."
}
```

After (consistently 120-140 lines):
```json
{
  "heading": "## Features",
  "prompt": "List 5-7 key features as bullet points with explanations. Format: Feature name (1 sentence) followed by 1-2 sentence explanation. Group related features. Focus on user benefits."
}
```

**Refinement Principles:**
1. **Explicit length**: "3-5 paragraphs", "5-7 bullet points", "2-3 examples"
2. **Scope limits**: "Focus on X", "Skip Y", "Only include Z"
3. **Structure hints**: "Format: X", "Group by Y", "Start with Z"
4. **Style guidance**: "Be concise", "Be thorough", "Be actionable"

**Files to modify:**
- All 6 template JSON files based on testing data
- Document changes in TESTING_REPORT.md

---

### 3. Validation: Length Targets
**Estimated Lines:** ~100 lines validation tests

**What it does:**
Automated tests that verify templates produce output within target length ranges.

**Why this sprint:**
- Regression prevention (future changes don't break length targets)
- Confidence that templates deliver on promises
- Clear pass/fail criteria for template quality

**Validation tests:**

```python
def test_readme_concise_length_target():
    """Verify readme-concise produces 300-500 line docs."""
    # Generate doc with readme-concise
    output = generate_test_doc("readme-concise", "doc-evergreen")
    line_count = count_lines(output)
    
    # Allow 20% variance (240-600 lines acceptable)
    assert 240 <= line_count <= 600, \
        f"readme-concise produced {line_count} lines (target: 300-500)"
    
    # Warn if outside target but within variance
    if line_count < 300 or line_count > 500:
        warnings.warn(f"Outside target range: {line_count} lines")

def test_readme_standard_length_target():
    """Verify readme-standard produces 500-700 line docs."""
    output = generate_test_doc("readme-standard", "doc-evergreen")
    line_count = count_lines(output)
    
    # Allow 20% variance (400-840 lines acceptable)
    assert 400 <= line_count <= 840, \
        f"readme-standard produced {line_count} lines (target: 500-700)"

# Similar tests for all 6 templates
```

**Validation report:**
```
Length Validation Results
=========================

readme-concise:
  ✓ doc-evergreen: 450 lines (target: 300-500)
  ✓ library-project: 380 lines (target: 300-500)
  
readme-standard:
  ✓ doc-evergreen: 680 lines (target: 500-700)
  ✓ library-project: 620 lines (target: 500-700)
  
readme-detailed:
  ✓ doc-evergreen: 920 lines (target: 800-1000)
  
api-docs:
  ✓ doc-evergreen: 650 lines (target: 500-700)
  
architecture:
  ✓ doc-evergreen: 520 lines (target: 400-600)
  
contributing:
  ✓ doc-evergreen: 420 lines (target: 300-500)

Overall: 7/7 tests passed ✓
```

**Files to create:**
- `tests/test_length_validation.py` - Automated length tests
- Update TESTING_REPORT.md with validation results

---

### 4. Quality Review: Content Appropriateness
**Estimated Lines:** Manual review + template adjustments

**What it does:**
Manual review of generated docs for quality beyond just length: relevance, clarity, organization, tone.

**Why this sprint:**
- Length isn't everything - content must be good
- Human review catches issues automation can't
- Ensures templates are production-ready

**Review criteria:**

**1. Relevance:**
- Does content match section purpose?
- Is information accurate to the project?
- Are examples relevant and helpful?

**2. Clarity:**
- Is writing clear and understandable?
- Are technical terms explained?
- Are examples easy to follow?

**3. Organization:**
- Is information logically structured?
- Do sections flow well?
- Are headings appropriate?

**4. Tone:**
- Is tone appropriate for doc type?
  - README: Welcoming, user-focused
  - API docs: Technical, precise
  - Architecture: Thoughtful, explanatory
  - Contributing: Encouraging, clear

**Review process:**

```bash
# Generate docs with each template
doc-evergreen init --template readme-concise
doc-evergreen regen-doc readme

# Manual review checklist:
# - Read generated README.md
# - Check relevance, clarity, organization, tone
# - Note specific issues
# - Identify patterns across sections

# Refine prompts based on findings
# Re-generate and verify improvements
```

**Common issues and fixes:**

**Issue: Too much implementation detail in Overview**
Fix: Add to prompt: "Focus on 'what' and 'why', not 'how'. Keep technical details for later sections."

**Issue: Generic examples that don't match project**
Fix: Add to prompt: "Use concrete examples from the source code. Reference actual classes/functions."

**Issue: Inconsistent voice (formal → casual)**
Fix: Add to prompt: "Maintain consistent professional tone throughout."

**Files to update:**
- Template JSON files (prompt refinements)
- TESTING_REPORT.md (quality review findings)

---

### 5. Regression Test Suite
**Estimated Lines:** ~200 lines comprehensive tests

**What it does:**
Comprehensive test suite that ensures templates continue working correctly as codebase evolves.

**Why this sprint:**
- Protect quality improvements from future regressions
- Enable confident refactoring in future sprints
- Automated validation of template integrity

**Test categories:**

**1. Template Integrity:**
```python
def test_all_templates_have_required_metadata():
    """Verify all templates have name, description, use_case."""
    for template_name in registry.list_templates():
        template = registry.load_template(template_name)
        assert "_meta" in template
        assert "name" in template["_meta"]
        assert "description" in template["_meta"]
        assert "use_case" in template["_meta"]

def test_all_templates_have_valid_structure():
    """Verify all templates have document.sections."""
    for template_name in registry.list_templates():
        template = registry.load_template(template_name)
        assert "document" in template
        assert "sections" in template["document"]
        assert len(template["document"]["sections"]) > 0
```

**2. Prompt Quality:**
```python
def test_all_prompts_have_length_guidance():
    """Verify all prompts include explicit length guidance."""
    length_indicators = ["paragraph", "bullet", "sentence", "brief", "concise", "detailed"]
    
    for template_name in registry.list_templates():
        template = registry.load_template(template_name)
        for section in template["document"]["sections"]:
            prompt = section["prompt"].lower()
            has_guidance = any(indicator in prompt for indicator in length_indicators)
            assert has_guidance, \
                f"{template_name} section '{section['heading']}' lacks length guidance"
```

**3. Generation:**
```python
def test_all_templates_generate_without_errors():
    """Verify all templates can generate docs without errors."""
    for template_name in registry.list_templates():
        result = runner.invoke(cli, ["init", "--template", template_name])
        assert result.exit_code == 0
        
        # Verify template file created
        expected_file = f".doc-evergreen/{template_name}.json"
        assert os.path.exists(expected_file)
```

**Files to create:**
- `tests/test_regression.py` - Comprehensive regression tests
- Integration into CI/CD (future)

---

## What Gets Punted (Deliberately Excluded)

### ❌ Template Variant Testing (Multiple LLM Providers)
- **Why**: Focus on OpenAI/Anthropic (current support)
- **Reconsider**: Future if other providers added

### ❌ Exhaustive Edge Case Testing
- **Why**: Test common projects, not every edge case
- **Reconsider**: Address specific issues as they arise

### ❌ Performance Optimization
- **Why**: No evidence of performance issues
- **Reconsider**: v0.6.0+ if generation is slow

### ❌ Template Comparison UI
- **Why**: Testing is developer-focused, not user-facing
- **Reconsider**: Future if users want to compare templates

---

## Dependencies

**Requires from previous sprints:**
- Sprint 1: 3 README templates
- Sprint 2: 3 specialized templates
- Sprint 2: Complete template library infrastructure

**Provides for future sprints:**
- High-quality, tested templates (Sprint 4 documents)
- Testing methodology (reusable for future templates)
- Baseline quality metrics (for future comparisons)

---

## Acceptance Criteria

### Must Have

**Cross-Project Testing:**
- ✅ All 6 templates tested on doc-evergreen
- ✅ At least 3 templates tested on second project
- ✅ Test data collected and documented
- ✅ TESTING_REPORT.md created with findings

**Prompt Refinement:**
- ✅ All templates refined based on test data
- ✅ Length targets achieved (within 20% variance)
- ✅ Prompt improvements documented
- ✅ Before/after data shows improvement

**Validation:**
- ✅ Length validation tests written and passing
- ✅ Regression test suite created
- ✅ All tests passing (>80% coverage)
- ✅ CI-ready test structure

**Quality Review:**
- ✅ Manual review of all 6 templates completed
- ✅ Quality issues identified and fixed
- ✅ Generated docs are production-quality
- ✅ Tone and style appropriate for each doc type

### Nice to Have (Defer if time constrained)

- ❌ Testing on 5+ different projects
- ❌ Automated quality scoring
- ❌ Performance benchmarks
- ❌ Template comparison report

---

## Technical Approach

### TDD Approach

Follow red-green-refactor cycle:

**For Validation Tests:**
1. 🔴 Write length validation test → Fail (templates not refined yet)
2. 🟢 Refine prompts until test passes
3. 🔵 Clean up prompt wording
4. ✅ Commit

**For Regression Tests:**
1. 🔴 Write regression test → Fail (catch current issues)
2. 🟢 Fix issues
3. 🔵 Ensure test is robust
4. ✅ Commit

### Key Decisions

**Decision 1: Testing Approach**
- **Choice**: Mix of automated (length) + manual (quality) testing
- **Rationale**: Length is measurable, quality needs human judgment
- **Trade-off**: Manual review takes time but ensures quality

**Decision 2: Length Variance Tolerance**
- **Choice**: Allow 20% variance from target
- **Rationale**: LLM output varies, too strict is brittle
- **Trade-off**: Some docs outside target but acceptable

**Decision 3: Test Project Selection**
- **Choice**: doc-evergreen + 1-2 real open source projects
- **Rationale**: Diverse project types validate template flexibility
- **Trade-off**: Can't test every project type

**Decision 4: Refinement Strategy**
- **Choice**: Iterative (test → refine → retest)
- **Rationale**: Prompt engineering is empirical, need iteration
- **Trade-off**: Takes time but produces better results

---

## Testing Requirements

### TDD Approach

**🔴 RED - Write Failing Tests First:**

**Length Validation Tests:**
```python
# These tests fail initially, pass after prompt refinement
def test_readme_concise_length():
    doc = generate_doc("readme-concise")
    assert 240 <= count_lines(doc) <= 600  # 20% variance

def test_readme_standard_length():
    doc = generate_doc("readme-standard")
    assert 400 <= count_lines(doc) <= 840

# Repeat for all 6 templates
```

**Regression Tests:**
```python
def test_templates_have_length_guidance():
    # Catches templates missing length hints
    for template in all_templates:
        for section in template.sections:
            assert has_length_guidance(section.prompt)
```

**🟢 GREEN - Refine Until Tests Pass:**

Iteratively refine prompts:
1. Run tests → Identify failures
2. Refine prompts → Re-run tests
3. Repeat until all pass

**🔵 REFACTOR - Polish Prompts:**

After tests pass:
- Improve prompt wording
- Ensure consistency across templates
- Add helpful hints for LLM

**Test Coverage Target:** >80% for validation code

**Commit Strategy:**
- Commit after each refinement iteration
- Document what was learned in TESTING_REPORT.md

---

## Implementation Order

**TDD-driven daily workflow:**

### Day 1: Cross-Project Testing Setup
- 🔴 Write test framework
- 🟢 Implement test runner
- 🔵 Refactor for reusability
- ✅ Run initial tests on all 6 templates
- ✅ Collect baseline data
- ✅ Commit (test framework ready)

### Day 2: Data Collection + Analysis
- ✅ Test all templates on doc-evergreen
- ✅ Test 3 templates on second project (if available)
- ✅ Analyze results: which templates need refinement?
- ✅ Create TESTING_REPORT.md with findings
- ✅ Identify specific prompt issues
- ✅ Commit (testing complete, report created)

### Day 3: Prompt Refinement (Iteration 1)
- 🔴 Write length validation tests (will fail)
- 🟢 Refine prompts for templates with issues
- 🟢 Re-test refined templates
- 🔵 Polish prompt wording
- ✅ Commit (first refinement iteration)
- 🟢 Continue refinement if needed
- ✅ Commit (tests passing)

### Day 4: Quality Review + Refinement (Iteration 2)
- ✅ Manual review of all generated docs
- ✅ Check relevance, clarity, organization, tone
- 🟢 Refine prompts based on quality findings
- ✅ Re-generate and verify improvements
- 🔵 Final polish on all templates
- ✅ Update TESTING_REPORT.md with quality notes
- ✅ Commit (quality improvements)

### Day 5: Regression Tests + Validation
- 🔴 Write comprehensive regression tests
- 🟢 Fix any issues found
- 🔵 Ensure test suite is robust
- ✅ Verify all tests passing
- ✅ Final validation run (all templates)
- ✅ Update TESTING_REPORT.md (final results)
- ✅ Final commit & sprint review

---

## Manual Testing Checklist

After automated tests pass:

### Cross-Project Testing
- [ ] Generate docs with all 6 templates on doc-evergreen
- [ ] Verify lengths are within target ranges
- [ ] Check content quality for each template
- [ ] Test on at least one other project
- [ ] Document any patterns or issues found

### Quality Review
- [ ] **readme-concise**: Brief, focused, actionable
- [ ] **readme-standard**: Balanced, comprehensive, clear
- [ ] **readme-detailed**: Thorough, well-organized, not overwhelming
- [ ] **api-docs**: Technical, precise, well-structured
- [ ] **architecture**: Thoughtful, explanatory, high-level
- [ ] **contributing**: Encouraging, clear, actionable

### Regression Verification
- [ ] All regression tests pass
- [ ] Length validation tests pass
- [ ] Template integrity tests pass
- [ ] No errors during generation

### Final Validation
- [ ] Generate fresh doc with each template
- [ ] Verify output matches expectations
- [ ] Check for consistency across templates
- [ ] Confirm production-ready quality

---

## What You Learn

After this sprint, you'll discover:

1. **Which Prompts Work Best**
   - What length guidance is most effective?
   - Which scope constraints prevent over-documentation?
   - → Codify as best practices in Sprint 4

2. **Template Flexibility**
   - Do templates adapt well to different projects?
   - Which templates need project-specific tuning?
   - → Informs future template additions

3. **LLM Output Patterns**
   - How much variance is normal?
   - Which prompts produce consistent results?
   - → Improves future prompt engineering

4. **Quality vs. Length Trade-offs**
   - Can we hit length targets without sacrificing quality?
   - When should we relax length constraints?
   - → Refines target ranges if needed

---

## Success Metrics

### Quantitative
- **All templates tested**: 6/6 templates tested across 2+ projects
- **Length targets met**: 100% of templates within 20% variance
- **Test coverage**: >80% for validation code
- **Regression tests**: 15+ tests passing

### Qualitative
- **Production quality**: All generated docs are good enough to ship
- **Consistency**: Templates produce predictable results
- **Developer confidence**: Tests provide safety net for changes
- **User satisfaction**: Templates solve the "996 lines" problem

---

## Known Limitations (By Design)

1. **LLM Non-Determinism** - Output varies slightly each generation
   - Why acceptable: 20% variance tolerance accounts for this
   - Tests verify results are within acceptable range

2. **Project-Specific Tuning** - Some projects may need custom prompts
   - Why acceptable: Templates work well for common cases
   - Users can customize templates after init

3. **Manual Quality Review** - Not fully automated
   - Why acceptable: Quality judgment requires human expertise
   - Regression tests catch obvious issues

4. **Limited Test Projects** - Can't test every project type
   - Why acceptable: Test representative projects
   - Community usage will reveal edge cases

---

## Next Sprint Preview

After Sprint 3 ships, the most pressing need will be:

**Sprint 4: Documentation & Polish**
- Create TEMPLATE_BEST_PRACTICES.md guide
- Document all learnings from Sprint 3
- Update user documentation
- Prepare v0.5.0 release

**Why Sprint 4 is ready:**
- Templates are production-ready (this sprint)
- Rich learnings to document (prompt patterns, testing insights)
- Clear best practices emerged from refinement
- All functionality complete, just needs documentation

---

## Sprint 3 Philosophy

**Quality Over Quantity**: 6 good templates > 20 mediocre ones

**Data-Driven**: Test, measure, refine based on real results

**Production-Ready**: Don't ship until it's good enough to use

**Learning Mindset**: Every test reveals something useful

**User Impact**: This sprint makes v0.5.0 actually valuable

---

**Sprint 3 Mantra**: "Test, refine, validate = production quality"
