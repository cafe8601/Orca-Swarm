#!/usr/bin/env python3
"""
Quality Enhancement Analysis Script

Analyzes Python files for documentation, type hints, and error handling quality.
Generates metrics and recommendations for systematic improvements.
"""

import ast
import os
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass


@dataclass
class FileMetrics:
    """Metrics for a single Python file."""
    path: str
    lines: int
    classes: int
    functions: int
    docstrings_module: int
    docstrings_class: int
    docstrings_function: int
    type_hints_function: int
    type_hints_params: int
    type_hints_returns: int
    exception_handling: int
    specific_exceptions: int
    generic_exceptions: int


class QualityAnalyzer:
    """Analyzes Python code quality metrics."""

    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.file_metrics: List[FileMetrics] = []

    def analyze_file(self, file_path: Path) -> FileMetrics:
        """Analyze a single Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content)

            lines = len(content.splitlines())
            classes = sum(1 for _ in ast.walk(tree) if isinstance(_, ast.ClassDef))
            functions = sum(1 for _ in ast.walk(tree) if isinstance(_, ast.FunctionDef))

            # Docstring analysis
            module_docstring = 1 if ast.get_docstring(tree) else 0
            class_docstrings = sum(
                1 for node in ast.walk(tree)
                if isinstance(node, ast.ClassDef) and ast.get_docstring(node)
            )
            function_docstrings = sum(
                1 for node in ast.walk(tree)
                if isinstance(node, ast.FunctionDef) and ast.get_docstring(node)
            )

            # Type hint analysis
            typed_functions = 0
            typed_params = 0
            typed_returns = 0
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    has_type_hints = False
                    for arg in node.args.args:
                        if arg.annotation:
                            typed_params += 1
                            has_type_hints = True
                    if node.returns:
                        typed_returns += 1
                        has_type_hints = True
                    if has_type_hints:
                        typed_functions += 1

            # Exception handling analysis
            exception_handlers = sum(
                1 for node in ast.walk(tree)
                if isinstance(node, ast.ExceptHandler)
            )
            specific_exceptions = sum(
                1 for node in ast.walk(tree)
                if isinstance(node, ast.ExceptHandler) and node.type is not None
            )
            generic_exceptions = exception_handlers - specific_exceptions

            relative_path = str(file_path.relative_to(self.base_path))

            return FileMetrics(
                path=relative_path,
                lines=lines,
                classes=classes,
                functions=functions,
                docstrings_module=module_docstring,
                docstrings_class=class_docstrings,
                docstrings_function=function_docstrings,
                type_hints_function=typed_functions,
                type_hints_params=typed_params,
                type_hints_returns=typed_returns,
                exception_handling=exception_handlers,
                specific_exceptions=specific_exceptions,
                generic_exceptions=generic_exceptions
            )
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return None

    def analyze_directory(self, directory: Path) -> List[FileMetrics]:
        """Analyze all Python files in directory."""
        python_files = list(directory.rglob("*.py"))

        for py_file in python_files:
            metrics = self.analyze_file(py_file)
            if metrics:
                self.file_metrics.append(metrics)

        return self.file_metrics

    def calculate_summary(self) -> Dict[str, Any]:
        """Calculate summary statistics."""
        if not self.file_metrics:
            return {}

        total_files = len(self.file_metrics)
        total_lines = sum(m.lines for m in self.file_metrics)
        total_classes = sum(m.classes for m in self.file_metrics)
        total_functions = sum(m.functions for m in self.file_metrics)

        # Documentation coverage
        files_with_module_docs = sum(1 for m in self.file_metrics if m.docstrings_module > 0)
        total_class_defs = sum(m.classes for m in self.file_metrics)
        total_func_defs = sum(m.functions for m in self.file_metrics)
        documented_classes = sum(m.docstrings_class for m in self.file_metrics)
        documented_functions = sum(m.docstrings_function for m in self.file_metrics)

        module_doc_coverage = (files_with_module_docs / total_files * 100) if total_files > 0 else 0
        class_doc_coverage = (documented_classes / total_class_defs * 100) if total_class_defs > 0 else 0
        function_doc_coverage = (documented_functions / total_func_defs * 100) if total_func_defs > 0 else 0

        # Type hint coverage
        total_typed_functions = sum(m.type_hints_function for m in self.file_metrics)
        total_typed_params = sum(m.type_hints_params for m in self.file_metrics)
        total_typed_returns = sum(m.type_hints_returns for m in self.file_metrics)

        function_type_coverage = (total_typed_functions / total_func_defs * 100) if total_func_defs > 0 else 0
        return_type_coverage = (total_typed_returns / total_func_defs * 100) if total_func_defs > 0 else 0

        # Error handling quality
        total_exception_handlers = sum(m.exception_handling for m in self.file_metrics)
        total_specific_exceptions = sum(m.specific_exceptions for m in self.file_metrics)
        specific_exception_ratio = (total_specific_exceptions / total_exception_handlers * 100) if total_exception_handlers > 0 else 0

        return {
            "total_files": total_files,
            "total_lines": total_lines,
            "total_classes": total_classes,
            "total_functions": total_functions,
            "module_doc_coverage": round(module_doc_coverage, 1),
            "class_doc_coverage": round(class_doc_coverage, 1),
            "function_doc_coverage": round(function_doc_coverage, 1),
            "function_type_coverage": round(function_type_coverage, 1),
            "return_type_coverage": round(return_type_coverage, 1),
            "specific_exception_ratio": round(specific_exception_ratio, 1),
            "total_exception_handlers": total_exception_handlers,
        }

    def identify_priorities(self) -> List[Tuple[str, str]]:
        """Identify files needing most improvement."""
        priorities = []

        for metrics in self.file_metrics:
            issues = []

            # Missing module docstring
            if metrics.docstrings_module == 0:
                issues.append("missing_module_docs")

            # Low documentation coverage
            if metrics.classes > 0:
                class_coverage = (metrics.docstrings_class / metrics.classes * 100)
                if class_coverage < 100:
                    issues.append(f"class_docs_{int(class_coverage)}%")

            if metrics.functions > 0:
                func_coverage = (metrics.docstrings_function / metrics.functions * 100)
                if func_coverage < 80:
                    issues.append(f"function_docs_{int(func_coverage)}%")

            # Low type hint coverage
            if metrics.functions > 0:
                type_coverage = (metrics.type_hints_function / metrics.functions * 100)
                if type_coverage < 50:
                    issues.append(f"type_hints_{int(type_coverage)}%")

            # Generic exception handling
            if metrics.generic_exceptions > 0:
                issues.append(f"generic_exceptions_{metrics.generic_exceptions}")

            if issues:
                priorities.append((metrics.path, ", ".join(issues)))

        # Sort by number of issues
        priorities.sort(key=lambda x: len(x[1].split(",")), reverse=True)
        return priorities

    def generate_report(self) -> str:
        """Generate comprehensive quality report."""
        summary = self.calculate_summary()
        priorities = self.identify_priorities()

        report = []
        report.append("=" * 80)
        report.append("CODE QUALITY ENHANCEMENT ANALYSIS")
        report.append("=" * 80)
        report.append("")

        report.append("SUMMARY METRICS")
        report.append("-" * 80)
        report.append(f"Total Files:          {summary['total_files']}")
        report.append(f"Total Lines:          {summary['total_lines']:,}")
        report.append(f"Total Classes:        {summary['total_classes']}")
        report.append(f"Total Functions:      {summary['total_functions']}")
        report.append("")

        report.append("DOCUMENTATION COVERAGE")
        report.append("-" * 80)
        report.append(f"Module Docstrings:    {summary['module_doc_coverage']}%")
        report.append(f"Class Docstrings:     {summary['class_doc_coverage']}%")
        report.append(f"Function Docstrings:  {summary['function_doc_coverage']}%")
        report.append("")

        report.append("TYPE HINT COVERAGE")
        report.append("-" * 80)
        report.append(f"Functions w/ Hints:   {summary['function_type_coverage']}%")
        report.append(f"Return Type Hints:    {summary['return_type_coverage']}%")
        report.append("")

        report.append("ERROR HANDLING QUALITY")
        report.append("-" * 80)
        report.append(f"Total Handlers:       {summary['total_exception_handlers']}")
        report.append(f"Specific Exceptions:  {summary['specific_exception_ratio']}%")
        report.append("")

        report.append("PRIORITY IMPROVEMENTS NEEDED")
        report.append("-" * 80)
        for i, (file_path, issues) in enumerate(priorities[:20], 1):
            report.append(f"{i:2}. {file_path}")
            report.append(f"    Issues: {issues}")
            report.append("")

        if len(priorities) > 20:
            report.append(f"... and {len(priorities) - 20} more files needing attention")
            report.append("")

        report.append("=" * 80)

        return "\n".join(report)


def main():
    """Main analysis function."""
    base_path = Path("/home/cafe99/voicetovoice/big-3-super-agent/apps/realtime-poc/big_three_realtime_agents")

    analyzer = QualityAnalyzer(base_path)
    analyzer.analyze_directory(base_path)

    report = analyzer.generate_report()
    print(report)

    # Save report
    report_path = Path("/home/cafe99/voicetovoice/big-3-super-agent/claudedocs/quality_analysis_report.txt")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, 'w') as f:
        f.write(report)
    print(f"\nReport saved to: {report_path}")


if __name__ == "__main__":
    main()
