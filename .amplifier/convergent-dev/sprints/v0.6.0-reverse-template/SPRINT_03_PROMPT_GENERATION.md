# Sprint 3: Prompt Generation & Complete Pipeline

**Duration:** 2-3 days  
**Goal:** LLM-generated prompts + content analysis + complete reverse → regen workflow  
**Value Delivered:** Fully automated template generation with intelligent prompts

---

## 🎯 Why This Sprint?

Sprint 2 delivered accurate source discovery (70-80%). Now we need **intelligent prompt generation** to complete the feature.

**The Challenge**: Given a documentation section and its sources, generate a prompt that would recreate similar content.

**Current State** (after Sprint 2):
- ✅ Accurate source discovery
- ❌ Placeholder prompts: "Document the {section_heading}"
- ❌ No content analysis
- ❌ No quadrant inference

**Goal State** (after Sprint 3):
- ✅ Intelligent, specific prompts based on section content
- ✅ Content intent analysis (what does this section do?)
- ✅ Quadrant inference (Tutorial, How-to, Reference, Explanation)
- ✅ Complete reverse → regen workflow works

Sprint 3 transforms the feature from "generates structure + sources" to "generates complete, usable templates."

---

## 📦 Deliverables

### 1. Content Intent Analyzer (LLM-Powered)
**Estimated Lines:** ~250 lines + 200 lines tests

**What it does:**
- Analyzes each section's content to understand purpose and intent
- Classifies section type (installation, API reference, troubleshooting, etc.)
- Extracts key topics, concepts, technical terms
- Infers Divio quadrant (Tutorial, How-to, Reference, Explanation)

**Why this sprint:**
Foundation for prompt generation. Can't generate good prompts without understanding what the section is about.

**Implementation notes:**
```python
class ContentIntentAnalyzer:
    """
    Analyze documentation section content with LLM to understand intent.
    """
    
    def __init__(self, llm_client):
        self.llm = llm_client
    
    def analyze_section(self, section_heading, section_content):
        """
        Analyze a documentation section to extract metadata.
        
        Returns:
            {
                'section_type': 'installation',
                'divio_quadrant': 'how-to',
                'key_topics': ['installation', 'package management', 'pip'],
                'intent': 'Guide users through installing the package',
                'technical_terms': ['pip', 'package manager', 'dependencies'],
                'content_style': 'instructional',
                'target_audience': 'users'
            }
        """
        prompt = f"""Analyze this documentation section and extract metadata:

**Section Heading:** {section_heading}

**Section Content:**
{section_content[:2000]}  # Limit to 2000 chars to control costs

Provide analysis in JSON format:

{{
    "section_type": "<installation|usage|api-reference|configuration|troubleshooting|contributing|architecture|other>",
    "divio_quadrant": "<tutorial|how-to|reference|explanation>",
    "key_topics": ["topic1", "topic2", ...],
    "intent": "<one sentence describing what this section does>",
    "technical_terms": ["term1", "term2", ...],
    "content_style": "<instructional|descriptive|reference|narrative>",
    "target_audience": "<users|developers|contributors|architects>"
}}

Classification guide:
- **Tutorial**: Learning-oriented, teaches concepts step-by-step
- **How-to**: Task-oriented, guides through solving specific problems
- **Reference**: Information-oriented, describes technical details
- **Explanation**: Understanding-oriented, clarifies concepts and design decisions
"""

        response = self.llm.generate(prompt, temperature=0)
        return self._parse_json_response(response)
```

**TDD approach:**
```python
# 🔴 RED: Write failing test
def test_analyze_installation_section():
    analyzer = ContentIntentAnalyzer(mock_llm_client)
    
    section_heading = "Installation"
    section_content = """
    To install doc-evergreen, run:
    ```bash
    pip install doc-evergreen
    ```
    
    For development installation:
    ```bash
    git clone https://github.com/user/doc-evergreen.git
    cd doc-evergreen
    pip install -e ".[dev]"
    ```
    """
    
    result = analyzer.analyze_section(section_heading, section_content)
    
    assert result['section_type'] == 'installation'
    assert result['divio_quadrant'] == 'how-to'
    assert 'installation' in result['key_topics']
    assert 'pip' in result['technical_terms']
    # FAILS - analyzer doesn't exist

# 🟢 GREEN: Implement basic analysis
# Call LLM with prompt
# Parse JSON response

# 🔵 REFACTOR: Improve prompt
# Add few-shot examples
# Handle edge cases (empty sections, etc.)
```

**Key decisions:**
- **Use LLM for understanding**: Pattern matching can't understand intent
- **Limit content to 2000 chars**: Control costs, excerpt is sufficient
- **Temperature=0**: Deterministic results for consistency
- **Structured output**: JSON parsing easier than free-form text

---

### 2. Prompt Generator (LLM-Powered)
**Estimated Lines:** ~300 lines + 250 lines tests

**What it does:**
- Given section analysis + discovered sources, generates appropriate prompt
- Creates prompt that would recreate the section's content approach
- Uses prompt patterns based on section type
- Generates specific, actionable prompts (not generic)

**Why this sprint:**
Core value of Sprint 3. Intelligent prompts make generated templates actually usable.

**Implementation notes:**
```python
class PromptGenerator:
    """
    Generate documentation prompts based on section analysis.
    """
    
    def __init__(self, llm_client):
        self.llm = llm_client
    
    def generate_prompt(self, section_heading, section_analysis, discovered_sources):
        """
        Generate a prompt that would recreate similar content.
        
        Args:
            section_heading: "Installation"
            section_analysis: {section_type, divio_quadrant, key_topics, intent, ...}
            discovered_sources: ['pyproject.toml', 'setup.py']
        
        Returns:
            {
                'prompt': '<generated prompt text>',
                'prompt_pattern': 'instructional_how_to',
                'confidence': 'high'
            }
        """
        # Build context for LLM
        context = f"""Generate a documentation prompt for a section that would guide content generation.

**Section Heading:** {section_heading}

**Section Analysis:**
- Type: {section_analysis['section_type']}
- Quadrant: {section_analysis['divio_quadrant']}
- Intent: {section_analysis['intent']}
- Key Topics: {', '.join(section_analysis['key_topics'])}
- Style: {section_analysis['content_style']}
- Audience: {section_analysis['target_audience']}

**Available Sources:**
{self._format_sources(discovered_sources)}

**Task:** Generate a prompt that would guide an LLM to create content for this section. The prompt should:
1. Be specific to this section's purpose and topics
2. Reference the available sources
3. Match the content style ({section_analysis['content_style']})
4. Be actionable and clear
5. Include any specific instructions based on section type

**Example Prompts:**

For Installation (how-to):
"Provide clear installation instructions for both standard users and developers. Include pip installation command from pyproject.toml for users, and git clone + editable install for developers. Keep it concise and actionable. List prerequisites if any are mentioned in the sources."

For API Reference (reference):
"Document the main API endpoints defined in the source files. For each endpoint, include: route path, HTTP methods, parameters, return values, and example usage. Use the actual function signatures from the code. Keep descriptions brief and factual."

For Architecture (explanation):
"Explain the high-level architecture of the system based on the core modules. Describe the main components, their responsibilities, and how they interact. Use diagrams if helpful. Focus on 'why' decisions were made, not just 'what' exists."

**Your Generated Prompt:**"""

        response = self.llm.generate(context, temperature=0.3)  # Slight creativity
        
        # Extract and validate prompt
        generated_prompt = self._extract_prompt(response)
        
        # Determine prompt pattern
        pattern = self._classify_prompt_pattern(section_analysis)
        
        return {
            'prompt': generated_prompt,
            'prompt_pattern': pattern,
            'confidence': 'high' if len(generated_prompt) > 50 else 'medium'
        }
    
    def _classify_prompt_pattern(self, section_analysis):
        """Map section analysis to prompt pattern."""
        quadrant = section_analysis['divio_quadrant']
        section_type = section_analysis['section_type']
        
        if quadrant == 'tutorial':
            return 'tutorial_step_by_step'
        elif quadrant == 'how-to' and section_type == 'installation':
            return 'instructional_how_to'
        elif quadrant == 'reference':
            return 'reference_technical'
        elif quadrant == 'explanation':
            return 'explanation_conceptual'
        else:
            return 'generic'
```

**TDD approach:**
```python
# 🔴 RED: Test prompt generation
def test_generate_installation_prompt():
    generator = PromptGenerator(mock_llm_client)
    
    section_analysis = {
        'section_type': 'installation',
        'divio_quadrant': 'how-to',
        'intent': 'Guide users through installing the package',
        'key_topics': ['installation', 'pip', 'development setup'],
        'content_style': 'instructional',
        'target_audience': 'users'
    }
    
    sources = ['pyproject.toml', 'setup.py']
    
    result = generator.generate_prompt(
        "Installation",
        section_analysis,
        sources
    )
    
    # Prompt should be specific and actionable
    assert len(result['prompt']) > 50
    assert 'install' in result['prompt'].lower()
    assert result['prompt_pattern'] == 'instructional_how_to'
    # FAILS - generator doesn't exist

# 🟢 GREEN: Implement basic generation
# 🔵 REFACTOR: Improve prompt quality
# Test with real LLM, iterate on examples
```

**Cost optimization:**
- Use temperature=0.3 (slight creativity, still deterministic enough)
- Include few-shot examples in system prompt (improves quality)
- Cache common section types (installation, usage, etc.)

---

### 3. Enhanced Template Assembly
**Estimated Lines:** ~200 lines + 150 lines tests

**What it does:**
- Integrates all components: structure + sources + analysis + prompts
- Generates complete, production-ready template.json
- Infers quadrant from section analyses
- Adds rich metadata

**Why this sprint:**
Brings everything together into final template output.

**Implementation notes:**
```python
class EnhancedTemplateAssembler:
    """
    Assemble complete template from all analyzed components.
    """
    
    def assemble_template(self, doc_path, parsed_doc, section_analyses, 
                         source_mappings, prompt_mappings):
        """
        Build complete template.json with all intelligence.
        
        Returns:
            {
                "name": "README-reversed",
                "description": "Auto-generated template from existing README.md",
                "quadrant": "explanation",  # Inferred from sections
                "metadata": {
                    "generated_from": "README.md",
                    "generated_at": "2025-12-01T18:00:00",
                    "accuracy_estimate": "70-80%",
                    "requires_review": true
                },
                "sections": [
                    {
                        "heading": "Installation",
                        "prompt": "<intelligent prompt>",
                        "sources": ["pyproject.toml", "setup.py"],
                        "metadata": {
                            "section_type": "installation",
                            "quadrant": "how-to",
                            "confidence": "high"
                        }
                    },
                    ...
                ]
            }
        """
        # Infer overall quadrant from section quadrants (majority vote)
        overall_quadrant = self._infer_overall_quadrant(section_analyses)
        
        # Generate template name and description
        doc_name = Path(doc_path).stem
        template_name = f"{doc_name}-reversed"
        description = f"Auto-generated template from existing {doc_name}.md"
        
        # Build sections
        sections = []
        for section_id, section in parsed_doc['sections'].items():
            section_analysis = section_analyses[section_id]
            sources = source_mappings.get(section_id, [])
            prompt_data = prompt_mappings[section_id]
            
            sections.append({
                'heading': section['heading'],
                'prompt': prompt_data['prompt'],
                'sources': [s['path'] for s in sources],
                'metadata': {
                    'section_type': section_analysis['section_type'],
                    'quadrant': section_analysis['divio_quadrant'],
                    'confidence': prompt_data['confidence'],
                    'key_topics': section_analysis['key_topics']
                }
            })
        
        template = {
            'name': template_name,
            'description': description,
            'quadrant': overall_quadrant,
            'metadata': {
                'generated_from': str(doc_path),
                'generated_at': datetime.now().isoformat(),
                'accuracy_estimate': '70-80%',
                'requires_review': True,
                'generator_version': '0.6.0'
            },
            'sections': sections
        }
        
        # Validate
        self._validate_template(template)
        
        return template
    
    def _infer_overall_quadrant(self, section_analyses):
        """
        Infer overall document quadrant from section quadrants.
        Use majority vote, with tie-breaker rules.
        """
        quadrant_counts = {}
        for analysis in section_analyses.values():
            q = analysis['divio_quadrant']
            quadrant_counts[q] = quadrant_counts.get(q, 0) + 1
        
        # Return most common quadrant
        return max(quadrant_counts.items(), key=lambda x: x[1])[0]
```

**TDD approach:**
```python
# 🔴 RED: Test complete assembly
def test_assemble_complete_template():
    assembler = EnhancedTemplateAssembler()
    
    # Mock all inputs
    parsed_doc = {...}
    section_analyses = {...}
    source_mappings = {...}
    prompt_mappings = {...}
    
    template = assembler.assemble_template(
        doc_path="README.md",
        parsed_doc=parsed_doc,
        section_analyses=section_analyses,
        source_mappings=source_mappings,
        prompt_mappings=prompt_mappings
    )
    
    # Validate structure
    assert template['name'] == 'README-reversed'
    assert 'sections' in template
    assert len(template['sections']) > 0
    assert all('prompt' in s for s in template['sections'])
    assert all('sources' in s for s in template['sections'])
    # Validate prompts are intelligent (not placeholders)
    assert all(len(s['prompt']) > 50 for s in template['sections'])
    # FAILS - assembler doesn't exist

# 🟢 GREEN: Implement assembly
# 🔵 REFACTOR: Validation, metadata
```

---

### 4. Enhanced CLI Orchestration
**Estimated Lines:** ~150 lines + 100 lines tests

**What it does:**
- Updates CLI to use new content analysis and prompt generation
- Improved progress output showing each analysis stage
- Better error messages

**Why this sprint:**
User-facing integration of all Sprint 3 components.

**Implementation notes:**
```python
@click.command()
@click.argument('doc_path', type=click.Path(exists=True))
@click.option('--output', '-o', help='Output template path')
def reverse(doc_path, output):
    """Generate template from existing documentation."""
    
    print(f"🔍 Analyzing {doc_path}...")
    
    # Parse document
    with open(doc_path) as f:
        content = f.read()
    parsed_doc = DocumentParser.parse(content)
    print(f"📝 Found {len(parsed_doc['sections'])} sections")
    
    # Analyze content (NEW in Sprint 3)
    print("🤖 Analyzing section content with LLM...")
    content_analyzer = ContentIntentAnalyzer(llm_client)
    section_analyses = {}
    for section_id, section in parsed_doc['sections'].items():
        analysis = content_analyzer.analyze_section(
            section['heading'],
            section['content']
        )
        section_analyses[section_id] = analysis
    print(f"✅ Analyzed {len(section_analyses)} sections")
    
    # Discover sources (from Sprint 2)
    print("🔎 Discovering relevant source files...")
    project_root = Path(doc_path).parent
    discoverer = IntelligentSourceDiscoverer(project_root, llm_client)
    source_mappings = {}
    total_sources = 0
    for section_id, section in parsed_doc['sections'].items():
        sources = discoverer.discover_sources(
            section['heading'],
            section['content']
        )
        source_mappings[section_id] = sources
        total_sources += len(sources)
    print(f"✅ Found {total_sources} relevant sources")
    
    # Generate prompts (NEW in Sprint 3)
    print("💡 Generating prompts for each section...")
    prompt_generator = PromptGenerator(llm_client)
    prompt_mappings = {}
    for section_id, section in parsed_doc['sections'].items():
        prompt_data = prompt_generator.generate_prompt(
            section['heading'],
            section_analyses[section_id],
            source_mappings[section_id]
        )
        prompt_mappings[section_id] = prompt_data
    print(f"✅ Generated {len(prompt_mappings)} prompts")
    
    # Assemble template (ENHANCED in Sprint 3)
    print("📦 Assembling template...")
    assembler = EnhancedTemplateAssembler()
    template = assembler.assemble_template(
        doc_path,
        parsed_doc,
        section_analyses,
        source_mappings,
        prompt_mappings
    )
    
    # Save
    output_path = output or f".doc-evergreen/templates/{template['name']}.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(template, f, indent=2)
    
    print(f"\n✅ Template generated: {output_path}")
    print(f"\nTemplate details:")
    print(f"  - Quadrant: {template['quadrant']}")
    print(f"  - Sections: {len(template['sections'])}")
    print(f"  - Sources: {sum(len(s['sources']) for s in template['sections'])}")
    print(f"  - Accuracy estimate: {template['metadata']['accuracy_estimate']}")
    print(f"\nNext steps:")
    print(f"  1. Review template: cat {output_path}")
    print(f"  2. Test regeneration: doc-evergreen regen --template {output_path} --output {doc_path.replace('.md', '-NEW.md')}")
    print(f"  3. Compare results: diff {doc_path} {doc_path.replace('.md', '-NEW.md')}")
    print(f"  4. Refine template if needed, then use for updates")
```

---

## 🚫 What Gets Punted (Deliberately Excluded)

### ❌ Template Learning from User Edits
- **Why**: Manual refinement is sufficient for MVP
- **Reconsider**: v0.7.0+ after usage patterns emerge
- Don't over-engineer feedback loops yet

### ❌ Multi-Pass Prompt Refinement
- **Why**: Single-pass generation is good enough
- **Reconsider**: If prompts are consistently poor quality
- Keep it simple for now

### ❌ Prompt Pattern Library
- **Why**: LLM generates prompts dynamically
- **Reconsider**: v0.7.0+ if patterns emerge from usage
- Dynamic generation more flexible than templates

### ❌ A/B Testing Different Prompts
- **Why**: Adds complexity without clear benefit
- **Reconsider**: Future version if quality varies significantly
- Single best-effort prompt is sufficient

---

## 🧪 Testing Requirements

### TDD Approach (Red-Green-Refactor)

**Day 1: Content Analysis**
- 🔴 Write content analyzer tests (mocked LLM)
- 🟢 Implement analysis prompt
- 🟢 Implement JSON parsing
- 🔵 Refactor for edge cases
- Test with real LLM on doc-evergreen README
- ✅ Commit (tests green)

**Day 2: Prompt Generation**
- 🔴 Write prompt generator tests
- 🟢 Implement generation logic
- 🟢 Test prompt patterns
- 🔵 Refactor prompt quality
- Test generated prompts with real LLM
- Validate prompts produce good docs
- ✅ Commit (tests green)

**Day 3: Integration & End-to-End**
- 🔴 Write integration tests
- 🟢 Wire all components
- 🟢 Update CLI
- Test full reverse → regen workflow
- Manual testing on multiple docs
- ✅ Final commit & sprint review

### Unit Tests (Write First)
- **Content analyzer**:
  - Analyzes installation sections correctly
  - Analyzes API reference sections correctly
  - Infers quadrant appropriately
  - Extracts key topics
  - Handles empty/short sections

- **Prompt generator**:
  - Generates specific prompts (not generic)
  - Includes source context
  - Matches section style
  - Different patterns for different quadrants

- **Template assembler**:
  - Infers overall quadrant correctly
  - Includes all metadata
  - Validates template structure

### Integration Tests (After Unit Tests Pass)
- **End-to-end workflow**:
  - Parse → Analyze → Discover → Generate → Assemble
  - Validate final template is complete
  - All prompts are intelligent
  - All sources are relevant

### Manual Testing (After Automated Tests Pass)
- [ ] Run on doc-evergreen README (full workflow)
- [ ] Review generated prompts (are they specific and useful?)
- [ ] Test template with `regen` command
- [ ] Compare regenerated doc to original (structure, content, quality)
- [ ] Test on secondary project (different doc type)
- [ ] Measure time to generate template (should be <5 minutes)

**Test Coverage Target:** >80% for new code

---

## 📊 What You Learn

After Sprint 3, you'll discover:

1. **Prompt quality achievability**
   - Can LLM generate useful prompts from analysis?
   - Do generated prompts recreate similar content?
   - What prompt patterns work best?
   → **Validates complete automation approach**

2. **Content analysis accuracy**
   - Does LLM correctly identify section types?
   - Is quadrant inference accurate?
   - What sections are hardest to analyze?

3. **Full workflow viability**
   - Does reverse → regen workflow actually work?
   - Is the output good enough to use?
   - What manual refinement is typically needed?
   → **Validates v0.6.0 value proposition**

4. **User workflow insights**
   - How long does full generation take?
   - What's the biggest friction point?
   - What features are most valuable?

---

## ✅ Success Criteria

### Must Have
- ✅ Content analyzer correctly identifies section types (>80% accuracy)
- ✅ Prompt generator creates specific, actionable prompts (not generic)
- ✅ Quadrant inference works correctly
- ✅ Complete reverse → regen workflow works end-to-end
- ✅ Regenerated doc structure matches original (>90% similarity)
- ✅ All tests pass with >80% coverage

### Nice to Have (Defer if Time Constrained)
- ❌ Prompt pattern library → Defer to v0.7.0
- ❌ Multi-pass refinement → Defer if single-pass works
- ❌ Advanced metadata → Keep minimal for MVP

---

## 🛠️ Technical Approach

### Key Decisions

**1. Use LLM for both analysis and generation**
- Analysis: Understand section intent
- Generation: Create prompts based on analysis
- Leverages LLM's strength in understanding and generation

**2. Two-stage prompt generation**
- Stage 1: Analyze content (understand what it is)
- Stage 2: Generate prompt (how to recreate it)
- Separation of concerns, easier to debug

**3. Include few-shot examples in prompts**
- Improves LLM output quality
- Makes prompt patterns clear
- More consistent results

**4. Validate generated prompts**
- Check length (>50 chars)
- Check specificity (not just "Document {heading}")
- Provide confidence scores

---

## 📅 Implementation Order

### Day 1: Content Analysis
- 🔴 Write analyzer tests
- 🟢 Implement analysis prompts
- 🔵 Refactor for accuracy
- Test on real docs
- ✅ Commit

### Day 2: Prompt Generation
- 🔴 Write generator tests
- 🟢 Implement generation logic
- 🔵 Refactor for quality
- Test generated prompts
- ✅ Commit

### Day 3: Integration
- 🔴 Write end-to-end tests
- 🟢 Wire components
- Update CLI
- Full workflow testing
- Documentation
- ✅ Final commit & sprint review

---

## 🎯 Known Limitations (By Design)

1. **Single-pass prompt generation**
   - Acceptable: Good enough for MVP
   - No iterative refinement for now

2. **No user feedback loop**
   - Acceptable: Manual editing works
   - Future enhancement

3. **LLM costs scale with sections**
   - Acceptable: Typical doc has 5-10 sections
   - Monitor costs during testing

4. **Generic fallback for unknown section types**
   - Acceptable: Handles edge cases gracefully
   - Most sections match known patterns

---

## 🔄 Next Sprint Preview

After Sprint 3 ships, the **most pressing need** will be:

**Polish and production readiness** - Core functionality works, but we need:
- CLI options (--dry-run, --verbose, --output)
- Robust error handling
- Edge case handling (empty docs, malformed markdown, etc.)
- Progress feedback improvements
- Documentation and examples

Sprint 3 delivers the complete feature. Sprint 4 makes it production-ready.

---

**Ready to complete the pipeline?** 🚀 After this sprint, reverse template generation works end-to-end!
