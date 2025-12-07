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
import logging
import sys
import time
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('day5_checkpoint.log')
    ]
)
logger = logging.getLogger(__name__)

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
        logger.info(f"Calling Anthropic API with model: {self.model}")
        logger.debug(f"Prompt length: {len(prompt)} chars")
        start_time = time.time()
        
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            elapsed = time.time() - start_time
            logger.info(f"Anthropic API call completed in {elapsed:.2f}s")
            return message.content[0].text
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"ERROR calling Anthropic API after {elapsed:.2f}s: {e}")
            logger.exception("Full traceback:")
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
        logger.info(f"Calling OpenAI API with model: {self.model}")
        logger.debug(f"Prompt length: {len(prompt)} chars")
        start_time = time.time()
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=1024
            )
            elapsed = time.time() - start_time
            logger.info(f"OpenAI API call completed in {elapsed:.2f}s")
            return response.choices[0].message.content
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"ERROR calling OpenAI API after {elapsed:.2f}s: {e}")
            logger.exception("Full traceback:")
            raise


def load_ground_truth():
    """Load ground truth test cases.
    
    Returns:
        List of test case dictionaries
    """
    ground_truth_path = Path(__file__).parent / "ground_truth_test_cases.json"
    
    logger.info(f"Loading ground truth from: {ground_truth_path}")
    
    try:
        with open(ground_truth_path) as f:
            data = json.load(f)
        
        test_cases = data['test_cases']
        logger.info(f"Successfully loaded {len(test_cases)} test cases")
        return test_cases
    except FileNotFoundError:
        logger.error(f"Ground truth file not found: {ground_truth_path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in ground truth file: {e}")
        raise
    except KeyError as e:
        logger.error(f"Missing 'test_cases' key in ground truth file: {e}")
        raise


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
    
    logger.info(f"Starting evaluation with model: {model_name}")
    logger.info(f"Test cases count: {len(test_cases)}")
    logger.info(f"Project root: {project_root}")
    
    try:
        # Create discoverer with this LLM
        logger.info("Creating IntelligentSourceDiscoverer...")
        start_time = time.time()
        discoverer = IntelligentSourceDiscoverer(
            project_root=project_root,
            llm_client=llm_client
        )
        logger.info(f"Discoverer created in {time.time() - start_time:.2f}s")
        
        # Create validator
        logger.info("Creating AccuracyValidator...")
        validator = AccuracyValidator(test_cases=test_cases)
        logger.info("Validator created")
        
        # Run evaluation
        print("Running discovery on test cases...")
        logger.info("Starting evaluation - this may take several minutes...")
        eval_start = time.time()
        
        metrics = validator.evaluate(discoverer)
        
        eval_elapsed = time.time() - eval_start
        logger.info(f"Evaluation completed in {eval_elapsed:.2f}s ({eval_elapsed/60:.2f} minutes)")
        
        # Generate report
        logger.info("Generating report...")
        report = validator.generate_report(metrics)
        
        print("\n" + report)
        logger.info(f"Evaluation for {model_name} completed successfully")
        
        return metrics
        
    except Exception as e:
        logger.error(f"Error during evaluation with {model_name}: {e}")
        logger.exception("Full traceback:")
        raise


def main():
    """Main evaluation script."""
    import os
    
    logger.info("="*60)
    logger.info("DAY 5 CHECKPOINT EVALUATION - Sprint 2")
    logger.info("Testing IntelligentSourceDiscoverer Accuracy")
    logger.info("="*60)
    
    print("="*60)
    print("DAY 5 CHECKPOINT EVALUATION - Sprint 2")
    print("Testing IntelligentSourceDiscoverer Accuracy")
    print("="*60)
    print(f"\nLogs being written to: day5_checkpoint.log")
    
    try:
        # Load ground truth
        print("\nLoading ground truth test cases...")
        logger.info("Loading ground truth test cases...")
        test_cases = load_ground_truth()
        print(f"Loaded {len(test_cases)} test cases from microsoft/amplifier-profiles")
        
        # Project root (we'll use a temp clone for evaluation)
        # For now, let's assume the repo is cloned to /tmp/amplifier-profiles
        project_root = Path("/tmp/amplifier-profiles")
        logger.info(f"Project root: {project_root}")
        
        if not project_root.exists():
            logger.error(f"Project not found at {project_root}")
            print(f"\nERROR: Project not found at {project_root}")
            print("Please clone the repo first:")
            print(f"  git clone https://github.com/microsoft/amplifier-profiles {project_root}")
            sys.exit(1)
        
        logger.info(f"Project root exists, checking contents...")
        logger.info(f"Project root contains {len(list(project_root.iterdir()))} items")
        
        # Read API keys
        print("\nSetting up LLM clients...")
        logger.info("Setting up LLM clients...")
        
        # Anthropic API key
        claude_key_path = Path.home() / ".claude" / "api_key.txt"
        logger.info(f"Looking for Anthropic API key at: {claude_key_path}")
        
        if not claude_key_path.exists():
            logger.error(f"Anthropic API key not found at {claude_key_path}")
            print(f"ERROR: Anthropic API key not found at {claude_key_path}")
            sys.exit(1)
        
        # Parse API key (handle both "sk-ant-..." and "CLAUDE_API_KEY=sk-ant-..." formats)
        logger.info("Reading Anthropic API key...")
        claude_api_key = claude_key_path.read_text().strip()
        if "=" in claude_api_key:
            claude_api_key = claude_api_key.split("=", 1)[1].strip()
        logger.info(f"Anthropic API key loaded (length: {len(claude_api_key)} chars)")
        
        # OpenAI API key (optional)
        openai_api_key = os.getenv("OPENAI_API_KEY")
        openai_model = os.getenv("OPENAI_MODEL", "gpt-4")
        
        if openai_api_key:
            logger.info(f"OpenAI API key found, will use model: {openai_model}")
        else:
            logger.info("No OpenAI API key found, will test Anthropic models only")
    
        # Create LLM clients
        logger.info("Creating LLM clients...")
        clients = []
        
        try:
            logger.info("Creating Claude Sonnet 4.5 client...")
            sonnet_client = AnthropicLLMClient("claude-sonnet-4-20250514", claude_api_key)
            clients.append(("Claude Sonnet 4.5", sonnet_client))
            logger.info("✅ Claude Sonnet 4.5 client created")
        except Exception as e:
            logger.error(f"Failed to create Claude Sonnet client: {e}")
            raise
        
        try:
            logger.info("Creating Claude Opus 4 client...")
            opus_client = AnthropicLLMClient("claude-opus-4-20250514", claude_api_key)
            clients.append(("Claude Opus 4", opus_client))
            logger.info("✅ Claude Opus 4 client created")
        except Exception as e:
            logger.error(f"Failed to create Claude Opus client: {e}")
            raise
        
        # Add OpenAI if API key is available
        if openai_api_key:
            try:
                logger.info(f"Creating OpenAI {openai_model} client...")
                openai_client = OpenAILLMClient(openai_model, openai_api_key)
                clients.append((f"OpenAI {openai_model}", openai_client))
                logger.info(f"✅ OpenAI {openai_model} client created")
                print(f"✅ Will test 3 models (including OpenAI {openai_model})")
            except Exception as e:
                logger.error(f"Failed to create OpenAI client: {e}")
                print(f"⚠️ Could not create OpenAI client, will test Anthropic models only")
        else:
            print(f"⚠️ OPENAI_API_KEY not set - will test 2 Anthropic models only")
            print(f"   To test OpenAI, set: export OPENAI_API_KEY=your-key")
        
        logger.info(f"Total clients to test: {len(clients)}")
        
        # Run evaluation for each model
        all_results = {}
        
        for idx, (model_name, client) in enumerate(clients, 1):
            logger.info(f"\n{'='*60}")
            logger.info(f"Starting evaluation {idx}/{len(clients)}: {model_name}")
            logger.info(f"{'='*60}")
            
            try:
                model_start = time.time()
                metrics = run_evaluation(model_name, client, test_cases, project_root)
                model_elapsed = time.time() - model_start
                
                all_results[model_name] = metrics
                logger.info(f"✅ {model_name} evaluation completed in {model_elapsed:.2f}s ({model_elapsed/60:.2f} minutes)")
                logger.info(f"   F1 Score: {metrics['f1_score']:.1%}")
                
            except KeyboardInterrupt:
                logger.warning(f"Evaluation interrupted by user during {model_name}")
                print(f"\n⚠️ Evaluation interrupted by user")
                all_results[model_name] = None
                break
            except Exception as e:
                logger.error(f"❌ ERROR evaluating {model_name}: {e}")
                print(f"\nERROR evaluating {model_name}: {e}")
                import traceback
                traceback.print_exc()
                all_results[model_name] = None
    
        # Summary comparison
        logger.info("Generating summary comparison...")
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
                logger.info(f"{model_name}: P={p:.1%}, R={r:.1%}, F1={f1:.1%} - {status}")
            else:
                print(f"{model_name:<25} {'ERROR':>10}  {'ERROR':>10}  {'ERROR':>10}  ❌ ERROR")
                logger.error(f"{model_name}: Evaluation failed")
        
        print("\n" + "="*60)
        print("Day 5 Checkpoint Decision:")
        logger.info("Making checkpoint decision...")
        
        # Check if ANY model passed
        passing_models = [name for name, m in all_results.items() if m and m['f1_score'] >= 0.70]
        warning_models = [name for name, m in all_results.items() if m and 0.60 <= m['f1_score'] < 0.70]
        
        if passing_models:
            decision = "proceed"
            print(f"✅ PROCEED TO SPRINT 3")
            print(f"   Models passing (F1 >= 70%): {', '.join(passing_models)}")
            print(f"   Recommendation: Use best-performing model for production")
            logger.info(f"Decision: PROCEED - {len(passing_models)} models passed")
        elif warning_models:
            decision = "adjust"
            print(f"⚠️ ADJUST ALGORITHM")
            print(f"   Models in warning range (60-70%): {', '.join(warning_models)}")
            print(f"   Recommendation: Extend sprint 1 day, tune algorithm")
            logger.warning(f"Decision: ADJUST - {len(warning_models)} models in warning range")
        else:
            decision = "pivot"
            print(f"❌ PIVOT REQUIRED")
            print(f"   All models below 60% accuracy")
            print(f"   Recommendation: Simplify approach, defer to v0.7.0")
            logger.error("Decision: PIVOT - All models below threshold")
        
        print("="*60)
        
        # Save results
        logger.info("Saving results...")
        results_path = Path(__file__).parent.parent / ".amplifier" / "convergent-dev" / "sprints" / "v0.6.0-reverse-template" / "day5_checkpoint_results.json"
        
        try:
            results_path.parent.mkdir(parents=True, exist_ok=True)
            
            results_data = {
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'models': list(all_results.keys()),
                'results': {k: v for k, v in all_results.items() if v is not None},
                'decision': decision
            }
            
            with open(results_path, 'w') as f:
                json.dump(results_data, f, indent=2)
            
            print(f"\nResults saved to: {results_path}")
            logger.info(f"Results saved to: {results_path}")
            
        except Exception as e:
            logger.error(f"Failed to save results: {e}")
            print(f"\n⚠️ Warning: Could not save results to {results_path}: {e}")
        
        logger.info("Evaluation script completed successfully")
        
    except KeyboardInterrupt:
        logger.warning("Script interrupted by user")
        print("\n\n⚠️ Script interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        logger.exception("Full traceback:")
        print(f"\n❌ Fatal error: {e}")
        print(f"\nCheck day5_checkpoint.log for full details")
        sys.exit(1)


if __name__ == "__main__":
    main()
