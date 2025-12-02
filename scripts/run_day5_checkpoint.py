#!/usr/bin/env python3
"""Day 5 Checkpoint Evaluation - Sprint 2 Accuracy Validation.

Tests IntelligentSourceDiscoverer accuracy against ground truth using 3 LLM models:
1. Claude Sonnet 4.5 (Anthropic)
2. Claude Opus 4 (Anthropic)  
3. OpenAI model (non-coding, set via OPENAI_MODEL env var)

Usage:
    python scripts/run_day5_checkpoint.py
    
Environment:
    OPENAI_API_KEY - OpenAI API key (required)
    OPENAI_MODEL - Model name (default: gpt-4)
"""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from doc_evergreen.reverse import IntelligentSourceDiscoverer, AccuracyValidator


class AnthropicLLMClient:
    """Simple LLM client for Anthropic Claude API."""
    
    def __init__(self, model: str, api_key: str):
        """Initialize client.
        
        Args:
            model: Model name (e.g., "claude-sonnet-4-20250514")
            api_key: Anthropic API key
        """
        self.model = model
        self.api_key = api_key
        
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=api_key)
        except ImportError:
            print("ERROR: anthropic package not installed")
            print("Install: pip install anthropic")
            sys.exit(1)
    
    def generate(self, prompt: str, temperature: float = 0.0) -> str:
        """Generate response from Claude.
        
        Args:
            prompt: Prompt text
            temperature: Temperature (0 for deterministic)
            
        Returns:
            Response text
        """
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except Exception as e:
            print(f"ERROR calling Anthropic API: {e}")
            raise


class OpenAILLMClient:
    """Simple LLM client for OpenAI API."""
    
    def __init__(self, model: str, api_key: str):
        """Initialize client.
        
        Args:
            model: Model name (e.g., "gpt-4")
            api_key: OpenAI API key
        """
        self.model = model
        self.api_key = api_key
        
        try:
            import openai
            self.client = openai.OpenAI(api_key=api_key)
        except ImportError:
            print("ERROR: openai package not installed")
            print("Install: pip install openai")
            sys.exit(1)
    
    def generate(self, prompt: str, temperature: float = 0.0) -> str:
        """Generate response from OpenAI.
        
        Args:
            prompt: Prompt text
            temperature: Temperature (0 for deterministic)
            
        Returns:
            Response text
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=1024
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"ERROR calling OpenAI API: {e}")
            raise


def load_ground_truth():
    """Load ground truth test cases.
    
    Returns:
        List of test case dictionaries
    """
    ground_truth_path = Path(__file__).parent.parent / ".amplifier" / "convergent-dev" / "sprints" / "v0.6.0-reverse-template" / "ground_truth_test_cases.json"
    
    with open(ground_truth_path) as f:
        data = json.load(f)
    
    return data['test_cases']


def run_evaluation(model_name: str, llm_client, test_cases: list, project_root: Path):
    """Run evaluation with a specific model.
    
    Args:
        model_name: Model name for reporting
        llm_client: LLM client instance
        test_cases: Ground truth test cases
        project_root: Root of project to evaluate
        
    Returns:
        Metrics dictionary with precision, recall, f1_score, per_section
    """
    print(f"\n{'='*60}")
    print(f"Evaluating with: {model_name}")
    print(f"{'='*60}\n")
    
    # Create discoverer with this LLM
    discoverer = IntelligentSourceDiscoverer(
        project_root=project_root,
        llm_client=llm_client
    )
    
    # Create validator
    validator = AccuracyValidator(test_cases=test_cases)
    
    # Run evaluation
    print("Running discovery on test cases...")
    metrics = validator.evaluate(discoverer)
    
    # Generate report
    report = validator.generate_report(metrics)
    
    print("\n" + report)
    
    return metrics


def main():
    """Main evaluation script."""
    import os
    
    print("="*60)
    print("DAY 5 CHECKPOINT EVALUATION - Sprint 2")
    print("Testing IntelligentSourceDiscoverer Accuracy")
    print("="*60)
    
    # Load ground truth
    print("\nLoading ground truth test cases...")
    test_cases = load_ground_truth()
    print(f"Loaded {len(test_cases)} test cases from microsoft/amplifier-profiles")
    
    # Project root (we'll use a temp clone for evaluation)
    # For now, let's assume the repo is cloned to /tmp/amplifier-profiles
    project_root = Path("/tmp/amplifier-profiles")
    
    if not project_root.exists():
        print(f"\nERROR: Project not found at {project_root}")
        print("Please clone the repo first:")
        print(f"  git clone https://github.com/microsoft/amplifier-profiles {project_root}")
        sys.exit(1)
    
    # Read API keys
    print("\nSetting up LLM clients...")
    
    # Anthropic API key
    claude_key_path = Path.home() / ".claude" / "api_key.txt"
    if not claude_key_path.exists():
        print(f"ERROR: Anthropic API key not found at {claude_key_path}")
        sys.exit(1)
    
    claude_api_key = claude_key_path.read_text().strip()
    
    # OpenAI API key
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("ERROR: OPENAI_API_KEY environment variable not set")
        sys.exit(1)
    
    openai_model = os.getenv("OPENAI_MODEL", "gpt-4")
    
    # Create LLM clients
    clients = [
        ("Claude Sonnet 4.5", AnthropicLLMClient("claude-sonnet-4-20250514", claude_api_key)),
        ("Claude Opus 4", AnthropicLLMClient("claude-opus-4-20250514", claude_api_key)),
        (f"OpenAI {openai_model}", OpenAILLMClient(openai_model, openai_api_key))
    ]
    
    # Run evaluation for each model
    all_results = {}
    
    for model_name, client in clients:
        try:
            metrics = run_evaluation(model_name, client, test_cases, project_root)
            all_results[model_name] = metrics
        except Exception as e:
            print(f"\nERROR evaluating {model_name}: {e}")
            import traceback
            traceback.print_exc()
            all_results[model_name] = None
    
    # Summary comparison
    print("\n" + "="*60)
    print("SUMMARY - Model Comparison")
    print("="*60)
    print(f"\n{'Model':<25} {'Precision':<12} {'Recall':<12} {'F1 Score':<12} {'Status'}")
    print("-"*80)
    
    for model_name, metrics in all_results.items():
        if metrics:
            p = metrics['precision']
            r = metrics['recall']
            f1 = metrics['f1_score']
            
            if f1 >= 0.70:
                status = "✅ PASS"
            elif f1 >= 0.60:
                status = "⚠️ WARNING"
            else:
                status = "❌ FAIL"
            
            print(f"{model_name:<25} {p:>10.1%}  {r:>10.1%}  {f1:>10.1%}  {status}")
        else:
            print(f"{model_name:<25} {'ERROR':>10}  {'ERROR':>10}  {'ERROR':>10}  ❌ ERROR")
    
    print("\n" + "="*60)
    print("Day 5 Checkpoint Decision:")
    
    # Check if ANY model passed
    passing_models = [name for name, m in all_results.items() if m and m['f1_score'] >= 0.70]
    warning_models = [name for name, m in all_results.items() if m and 0.60 <= m['f1_score'] < 0.70]
    
    if passing_models:
        print(f"✅ PROCEED TO SPRINT 3")
        print(f"   Models passing (F1 >= 70%): {', '.join(passing_models)}")
        print(f"   Recommendation: Use best-performing model for production")
    elif warning_models:
        print(f"⚠️ ADJUST ALGORITHM")
        print(f"   Models in warning range (60-70%): {', '.join(warning_models)}")
        print(f"   Recommendation: Extend sprint 1 day, tune algorithm")
    else:
        print(f"❌ PIVOT REQUIRED")
        print(f"   All models below 60% accuracy")
        print(f"   Recommendation: Simplify approach, defer to v0.7.0")
    
    print("="*60)
    
    # Save results
    results_path = Path(__file__).parent.parent / ".amplifier" / "convergent-dev" / "sprints" / "v0.6.0-reverse-template" / "day5_checkpoint_results.json"
    results_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(results_path, 'w') as f:
        json.dump({
            'models': list(all_results.keys()),
            'results': {k: v for k, v in all_results.items() if v is not None},
            'decision': 'proceed' if passing_models else ('adjust' if warning_models else 'pivot')
        }, f, indent=2)
    
    print(f"\nResults saved to: {results_path}")


if __name__ == "__main__":
    main()
