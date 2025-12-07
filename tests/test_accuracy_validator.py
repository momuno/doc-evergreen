"""Tests for AccuracyValidator - measures source discovery accuracy."""

import pytest
from unittest.mock import Mock

try:
    from doc_evergreen.reverse.accuracy_validator import AccuracyValidator
except ImportError:
    AccuracyValidator = None


class TestAccuracyValidator:
    """Tests for accuracy validation and metrics computation."""
    
    def test_validate_computes_precision_recall_f1(self):
        """
        Given: Ground truth test cases and discoverer
        When: Evaluate accuracy
        Then: Computes precision, recall, F1 score
        """
        # ARRANGE
        test_cases = [
            {
                'section_heading': 'Installation',
                'section_content': 'Install using pip...',
                'ground_truth_sources': ['pyproject.toml', 'setup.py']
            }
        ]
        
        # Mock discoverer that returns 1 correct + 1 incorrect
        mock_discoverer = Mock()
        mock_discoverer.discover_sources.return_value = [
            {'path': 'pyproject.toml'},  # Correct (TP)
            {'path': 'README.md'}         # Incorrect (FP)
        ]
        
        validator = AccuracyValidator(test_cases=test_cases)
        
        # ACT
        metrics = validator.evaluate(discoverer=mock_discoverer)
        
        # ASSERT
        assert 'precision' in metrics
        assert 'recall' in metrics
        assert 'f1_score' in metrics
        
        # TP=1, FP=1, FN=1 (missed setup.py)
        # Precision = 1/(1+1) = 0.5
        # Recall = 1/(1+1) = 0.5
        # F1 = 0.5
        assert metrics['precision'] == 0.5
        assert metrics['recall'] == 0.5
        assert metrics['f1_score'] == 0.5
    
    def test_validate_handles_perfect_discovery(self):
        """
        Given: Discoverer finds all ground truth sources
        When: Evaluate accuracy
        Then: Returns 100% precision, recall, F1
        """
        # ARRANGE
        test_cases = [
            {
                'section_heading': 'API',
                'section_content': 'API endpoints...',
                'ground_truth_sources': ['src/api.py', 'src/routes.py']
            }
        ]
        
        # Mock discoverer that finds exactly the ground truth
        mock_discoverer = Mock()
        mock_discoverer.discover_sources.return_value = [
            {'path': 'src/api.py'},
            {'path': 'src/routes.py'}
        ]
        
        validator = AccuracyValidator(test_cases=test_cases)
        
        # ACT
        metrics = validator.evaluate(discoverer=mock_discoverer)
        
        # ASSERT
        assert metrics['precision'] == 1.0
        assert metrics['recall'] == 1.0
        assert metrics['f1_score'] == 1.0
    
    def test_validate_handles_no_matches(self):
        """
        Given: Discoverer finds no correct sources
        When: Evaluate accuracy
        Then: Returns 0% precision, recall, F1
        """
        # ARRANGE
        test_cases = [
            {
                'section_heading': 'Config',
                'section_content': 'Configuration...',
                'ground_truth_sources': ['config.yaml']
            }
        ]
        
        # Mock discoverer that finds wrong files
        mock_discoverer = Mock()
        mock_discoverer.discover_sources.return_value = [
            {'path': 'README.md'},
            {'path': 'main.py'}
        ]
        
        validator = AccuracyValidator(test_cases=test_cases)
        
        # ACT
        metrics = validator.evaluate(discoverer=mock_discoverer)
        
        # ASSERT
        assert metrics['precision'] == 0.0
        assert metrics['recall'] == 0.0
        assert metrics['f1_score'] == 0.0
    
    def test_validate_returns_per_section_metrics(self):
        """
        Given: Multiple test cases
        When: Evaluate accuracy
        Then: Returns per-section breakdown
        """
        # ARRANGE
        test_cases = [
            {
                'section_heading': 'Installation',
                'section_content': 'Install...',
                'ground_truth_sources': ['setup.py']
            },
            {
                'section_heading': 'API',
                'section_content': 'API...',
                'ground_truth_sources': ['api.py']
            }
        ]
        
        mock_discoverer = Mock()
        mock_discoverer.discover_sources.side_effect = [
            [{'path': 'setup.py'}],  # Perfect for first section
            [{'path': 'wrong.py'}]   # Wrong for second section
        ]
        
        validator = AccuracyValidator(test_cases=test_cases)
        
        # ACT
        metrics = validator.evaluate(discoverer=mock_discoverer)
        
        # ASSERT
        assert 'per_section' in metrics
        assert len(metrics['per_section']) == 2
        
        # First section should be perfect
        assert metrics['per_section'][0]['section'] == 'Installation'
        assert metrics['per_section'][0]['precision'] == 1.0
        assert metrics['per_section'][0]['recall'] == 1.0
        
        # Second section should be wrong
        assert metrics['per_section'][1]['section'] == 'API'
        assert metrics['per_section'][1]['precision'] == 0.0
        assert metrics['per_section'][1]['recall'] == 0.0
    
    def test_validate_computes_average_across_sections(self):
        """
        Given: Multiple test cases with different scores
        When: Evaluate accuracy
        Then: Returns averaged metrics
        """
        # ARRANGE
        test_cases = [
            {
                'section_heading': 'Section 1',
                'section_content': 'Content 1',
                'ground_truth_sources': ['file1.py']
            },
            {
                'section_heading': 'Section 2',
                'section_content': 'Content 2',
                'ground_truth_sources': ['file2.py']
            }
        ]
        
        mock_discoverer = Mock()
        mock_discoverer.discover_sources.side_effect = [
            [{'path': 'file1.py'}],              # Perfect (F1=1.0)
            [{'path': 'file2.py'}, {'path': 'wrong.py'}]  # 1 correct, 1 wrong (F1=0.67)
        ]
        
        validator = AccuracyValidator(test_cases=test_cases)
        
        # ACT
        metrics = validator.evaluate(discoverer=mock_discoverer)
        
        # ASSERT
        # Average F1 should be (1.0 + 0.67) / 2 = 0.835
        assert metrics['f1_score'] > 0.8
        assert metrics['f1_score'] < 0.9
    
    def test_validate_handles_empty_ground_truth(self):
        """
        Given: Test case with no ground truth sources
        When: Evaluate accuracy
        Then: Handles gracefully (skips or returns 0)
        """
        # ARRANGE
        test_cases = [
            {
                'section_heading': 'Abstract',
                'section_content': 'Overview...',
                'ground_truth_sources': []  # No expected sources
            }
        ]
        
        mock_discoverer = Mock()
        mock_discoverer.discover_sources.return_value = []
        
        validator = AccuracyValidator(test_cases=test_cases)
        
        # ACT
        metrics = validator.evaluate(discoverer=mock_discoverer)
        
        # ASSERT
        # Should handle gracefully without division by zero
        assert isinstance(metrics['precision'], (int, float))
        assert isinstance(metrics['recall'], (int, float))
        assert isinstance(metrics['f1_score'], (int, float))
    
    def test_validate_includes_discovered_and_ground_truth_in_details(self):
        """
        Given: Test cases
        When: Evaluate accuracy
        Then: Per-section results include discovered and ground truth lists
        """
        # ARRANGE
        test_cases = [
            {
                'section_heading': 'Test',
                'section_content': 'Content',
                'ground_truth_sources': ['truth1.py', 'truth2.py']
            }
        ]
        
        mock_discoverer = Mock()
        mock_discoverer.discover_sources.return_value = [
            {'path': 'truth1.py'},
            {'path': 'found.py'}
        ]
        
        validator = AccuracyValidator(test_cases=test_cases)
        
        # ACT
        metrics = validator.evaluate(discoverer=mock_discoverer)
        
        # ASSERT
        section_result = metrics['per_section'][0]
        assert 'discovered' in section_result
        assert 'ground_truth' in section_result
        
        assert 'truth1.py' in section_result['discovered']
        assert 'found.py' in section_result['discovered']
        
        assert 'truth1.py' in section_result['ground_truth']
        assert 'truth2.py' in section_result['ground_truth']
    
    def test_validate_generates_accuracy_report(self):
        """
        Given: Evaluation complete
        When: Generate report
        Then: Returns formatted report string
        """
        # ARRANGE
        test_cases = [
            {
                'section_heading': 'Installation',
                'section_content': 'Install...',
                'ground_truth_sources': ['setup.py']
            }
        ]
        
        mock_discoverer = Mock()
        mock_discoverer.discover_sources.return_value = [{'path': 'setup.py'}]
        
        validator = AccuracyValidator(test_cases=test_cases)
        
        # ACT
        metrics = validator.evaluate(discoverer=mock_discoverer)
        report = validator.generate_report(metrics)
        
        # ASSERT
        assert isinstance(report, str)
        assert len(report) > 0
        
        # Report should include key metrics
        assert 'Precision' in report or 'precision' in report
        assert 'Recall' in report or 'recall' in report
        assert 'F1' in report or 'f1' in report.lower()
        
        # Should include overall scores
        assert '1.0' in report or '100' in report  # Perfect score
    
    def test_validate_report_includes_checkpoint_status(self):
        """
        Given: Accuracy metrics computed
        When: Generate report
        Then: Includes Day 5 checkpoint status (pass/warning/fail)
        """
        # ARRANGE
        test_cases = [
            {
                'section_heading': 'Test',
                'section_content': 'Content',
                'ground_truth_sources': ['file.py']
            }
        ]
        
        # High accuracy (should pass checkpoint)
        mock_discoverer = Mock()
        mock_discoverer.discover_sources.return_value = [{'path': 'file.py'}]
        
        validator = AccuracyValidator(test_cases=test_cases)
        
        # ACT
        metrics = validator.evaluate(discoverer=mock_discoverer)
        report = validator.generate_report(metrics)
        
        # ASSERT
        # With F1=1.0, should indicate checkpoint passed
        assert 'PASS' in report or 'Success' in report or '✅' in report or 'achieved' in report.lower()
    
    def test_validate_checkpoint_warns_for_60_70_accuracy(self):
        """
        Given: Accuracy in 60-70% range
        When: Generate report
        Then: Shows WARNING status for Day 5 checkpoint
        """
        # ARRANGE
        test_cases = [
            {
                'section_heading': 'Test',
                'section_content': 'Content',
                'ground_truth_sources': ['file1.py', 'file2.py', 'file3.py']
            }
        ]
        
        # Return 2 correct + 1 wrong = 67% precision, 67% recall
        mock_discoverer = Mock()
        mock_discoverer.discover_sources.return_value = [
            {'path': 'file1.py'},
            {'path': 'file2.py'},
            {'path': 'wrong.py'}
        ]
        
        validator = AccuracyValidator(test_cases=test_cases)
        
        # ACT
        metrics = validator.evaluate(discoverer=mock_discoverer)
        report = validator.generate_report(metrics)
        
        # ASSERT
        # F1 should be ~0.67 (60-70% range)
        assert 0.6 <= metrics['f1_score'] <= 0.7
        
        # Report should show warning
        assert 'WARNING' in report or 'Adjust' in report or '⚠️' in report
