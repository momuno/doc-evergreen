"""AccuracyValidator - measures source discovery accuracy against ground truth."""

from typing import Any, Dict, List


class AccuracyValidator:
    """Validate source discovery accuracy against ground truth test cases."""
    
    def __init__(self, test_cases: List[Dict]):
        """Initialize validator with ground truth test cases.
        
        Args:
            test_cases: List of test case dictionaries with:
                - section_heading: Section heading text
                - section_content: Section content text
                - ground_truth_sources: List of expected source file paths
        """
        self.test_cases = test_cases
    
    def evaluate(self, discoverer: Any) -> Dict:
        """
        Evaluate discoverer accuracy against ground truth.
        
        Args:
            discoverer: Source discoverer with discover_sources() method
            
        Returns:
            Dictionary with:
            - precision: Average precision across all test cases
            - recall: Average recall across all test cases
            - f1_score: Average F1 score across all test cases
            - per_section: List of per-section results with details
        """
        per_section_results = []
        
        for test_case in self.test_cases:
            # Run discoverer on this test case
            discovered = discoverer.discover_sources(
                section_heading=test_case['section_heading'],
                section_content=test_case['section_content'],
                max_sources=10  # Allow up to 10 to measure precision/recall properly
            )
            
            # Extract paths from discovered results
            discovered_paths = {d['path'] for d in discovered}
            ground_truth_paths = set(test_case['ground_truth_sources'])
            
            # Compute metrics for this section
            metrics = self._compute_metrics(
                discovered=discovered_paths,
                ground_truth=ground_truth_paths
            )
            
            # Add section details
            section_result = {
                'section': test_case['section_heading'],
                'precision': metrics['precision'],
                'recall': metrics['recall'],
                'f1': metrics['f1'],
                'discovered': list(discovered_paths),
                'ground_truth': list(ground_truth_paths)
            }
            
            per_section_results.append(section_result)
        
        # Compute average metrics
        if per_section_results:
            avg_precision = sum(r['precision'] for r in per_section_results) / len(per_section_results)
            avg_recall = sum(r['recall'] for r in per_section_results) / len(per_section_results)
            avg_f1 = sum(r['f1'] for r in per_section_results) / len(per_section_results)
        else:
            avg_precision = 0.0
            avg_recall = 0.0
            avg_f1 = 0.0
        
        return {
            'precision': avg_precision,
            'recall': avg_recall,
            'f1_score': avg_f1,
            'per_section': per_section_results
        }
    
    def generate_report(self, metrics: Dict) -> str:
        """
        Generate human-readable accuracy report.
        
        Args:
            metrics: Metrics dictionary from evaluate()
            
        Returns:
            Formatted report string with checkpoint status
        """
        # Overall metrics
        precision = metrics['precision']
        recall = metrics['recall']
        f1 = metrics['f1_score']
        
        # Determine checkpoint status
        checkpoint_status = self._get_checkpoint_status(f1)
        
        # Build report
        report = []
        report.append("=" * 60)
        report.append("SOURCE DISCOVERY ACCURACY REPORT")
        report.append("Sprint 2 - Day 5 Checkpoint Evaluation")
        report.append("=" * 60)
        report.append("")
        
        # Overall metrics
        report.append("Overall Metrics:")
        report.append(f"  Precision: {precision:.1%} (How many discovered sources are correct?)")
        report.append(f"  Recall:    {recall:.1%} (How many correct sources did we find?)")
        report.append(f"  F1 Score:  {f1:.1%} (Harmonic mean of precision and recall)")
        report.append("")
        
        # Checkpoint status
        report.append("Day 5 Checkpoint Status:")
        report.append(f"  {checkpoint_status['icon']} {checkpoint_status['status']}")
        report.append(f"  {checkpoint_status['message']}")
        report.append("")
        
        # Per-section breakdown
        if metrics['per_section']:
            report.append("Per-Section Results:")
            report.append("-" * 60)
            
            for section_result in metrics['per_section']:
                section = section_result['section']
                p = section_result['precision']
                r = section_result['recall']
                f = section_result['f1']
                
                report.append(f"\n  Section: {section}")
                report.append(f"    Precision: {p:.1%} | Recall: {r:.1%} | F1: {f:.1%}")
                
                # Show discovered vs ground truth
                discovered = section_result['discovered']
                ground_truth = section_result['ground_truth']
                
                if discovered:
                    report.append(f"    Discovered: {', '.join(discovered[:3])}")
                    if len(discovered) > 3:
                        report.append(f"                (+{len(discovered)-3} more)")
                else:
                    report.append("    Discovered: (none)")
                
                if ground_truth:
                    report.append(f"    Expected:   {', '.join(ground_truth[:3])}")
                    if len(ground_truth) > 3:
                        report.append(f"                (+{len(ground_truth)-3} more)")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def _compute_metrics(self, discovered: set, ground_truth: set) -> Dict:
        """
        Compute precision, recall, F1 for a single test case.
        
        Args:
            discovered: Set of discovered source paths
            ground_truth: Set of expected source paths
            
        Returns:
            Dictionary with precision, recall, f1
        """
        # Handle empty cases
        if not ground_truth and not discovered:
            # Both empty - perfect match
            return {'precision': 1.0, 'recall': 1.0, 'f1': 1.0}
        
        if not ground_truth:
            # No expected sources but some discovered - precision=0, recall undefined
            return {'precision': 0.0, 'recall': 1.0, 'f1': 0.0}
        
        if not discovered:
            # Expected sources but none discovered
            return {'precision': 0.0, 'recall': 0.0, 'f1': 0.0}
        
        # Compute true positives, false positives, false negatives
        true_positives = len(discovered & ground_truth)
        false_positives = len(discovered - ground_truth)
        false_negatives = len(ground_truth - discovered)
        
        # Precision: What proportion of discovered sources are correct?
        if true_positives + false_positives > 0:
            precision = true_positives / (true_positives + false_positives)
        else:
            precision = 0.0
        
        # Recall: What proportion of correct sources did we find?
        if true_positives + false_negatives > 0:
            recall = true_positives / (true_positives + false_negatives)
        else:
            recall = 0.0
        
        # F1: Harmonic mean of precision and recall
        if precision + recall > 0:
            f1 = 2 * (precision * recall) / (precision + recall)
        else:
            f1 = 0.0
        
        return {
            'precision': precision,
            'recall': recall,
            'f1': f1
        }
    
    def _get_checkpoint_status(self, f1_score: float) -> Dict:
        """
        Determine Day 5 checkpoint status based on F1 score.
        
        Args:
            f1_score: Overall F1 score
            
        Returns:
            Dictionary with icon, status, message
        """
        if f1_score >= 0.70:
            # Success - proceed to Sprint 3
            return {
                'icon': '✅',
                'status': 'PASS - Proceed to Sprint 3',
                'message': f'Achieved target accuracy ({f1_score:.1%} >= 70%). Ready for Sprint 3 (Prompt Generation).'
            }
        elif f1_score >= 0.60:
            # Warning - adjust and extend
            return {
                'icon': '⚠️',
                'status': 'WARNING - Adjust Algorithm',
                'message': f'Accuracy ({f1_score:.1%}) below target (70%). Recommend: Adjust algorithm, extend sprint 1 day.'
            }
        else:
            # Fail - pivot required
            return {
                'icon': '❌',
                'status': 'FAIL - Pivot Required',
                'message': f'Accuracy ({f1_score:.1%}) significantly below target. Recommend: Simplify approach, defer advanced discovery to v0.7.0.'
            }
