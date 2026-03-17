#!/usr/bin/env python
"""
CIAF Coverage Tracking and Reporting Tool
Monitors progress toward 100% code coverage goal

Usage:
    python track_coverage.py                    # Run current coverage report
    python track_coverage.py --history         # Show coverage history
    python track_coverage.py --detailed        # Show detailed by-file analysis
    python track_coverage.py --compare <file>  # Compare against previous report
"""

import subprocess
import json
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import re


class CoverageTracker:
    """Track and report code coverage metrics"""

    HISTORY_FILE = Path(__file__).parent / ".coverage_history.json"
    COVERAGE_THRESHOLDS = {
        'critical': 0.80,  # Must reach 80% per pytest.ini
        'good': 0.70,
        'fair': 0.50,
        'poor': 0.20,
    }

    def __init__(self):
        self.history = self._load_history()

    def _load_history(self) -> List[Dict]:
        """Load previous coverage reports"""
        if self.HISTORY_FILE.exists():
            with open(self.HISTORY_FILE) as f:
                return json.load(f)
        return []

    def _save_history(self):
        """Save current history"""
        with open(self.HISTORY_FILE, 'w') as f:
            json.dump(self.history, f, indent=2)

    def run_coverage(self) -> Dict:
        """Run pytest with coverage and parse results"""
        try:
            result = subprocess.run(
                ['python', '-m', 'pytest', 'tests/', '--cov=ciaf', '--cov-report=json', '-q'],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=Path(__file__).parent
            )

            # Parse coverage.json file
            coverage_file = Path(__file__).parent / '.coverage'
            if coverage_file.exists():
                # Use the standard coverage tool
                result = subprocess.run(
                    ['python', '-m', 'coverage', 'json'],
                    capture_output=True,
                    text=True,
                    cwd=Path(__file__).parent
                )

            coverage_json = Path(__file__).parent / 'coverage.json'
            if coverage_json.exists():
                with open(coverage_json) as f:
                    data = json.load(f)
                    return {
                        'total_lines': data['totals']['num_statements'],
                        'covered_lines': data['totals']['num_statements'] - data['totals']['missing_lines'],
                        'coverage_pct': data['totals']['percent_covered'],
                        'files': self._parse_file_coverage(data),
                        'timestamp': datetime.now().isoformat(),
                    }

            # Fallback: parse text output
            return self._parse_coverage_text(result.stdout)

        except Exception as e:
            print(f"Error running coverage: {e}")
            return {}

    def _parse_coverage_text(self, output: str) -> Dict:
        """Parse coverage from text output"""
        lines = output.split('\n')
        for line in lines:
            if 'TOTAL' in line:
                match = re.search(r'(\d+)\s+(\d+)\s+([\d.]+)%', line)
                if match:
                    total = int(match.group(1))
                    covered = int(match.group(2))
                    pct = float(match.group(3))
                    return {
                        'total_lines': total,
                        'covered_lines': covered,
                        'coverage_pct': pct,
                        'timestamp': datetime.now().isoformat(),
                    }
        return {}

    def _parse_file_coverage(self, data: Dict) -> Dict[str, float]:
        """Extract per-file coverage from coverage.json"""
        files = {}
        for file_path, file_data in data.get('files', {}).items():
            if 'ciaf/' in file_path:
                summary = file_data.get('summary', {})
                pct = summary.get('percent_covered', 0)
                files[file_path] = pct
        return files

    def get_coverage_status(self) -> Tuple[str, str]:
        """Determine coverage status and color"""
        if not self.history:
            return "UNKNOWN", "⚪"

        latest = self.history[-1]
        pct = latest.get('coverage_pct', 0)

        if pct >= self.COVERAGE_THRESHOLDS['critical']:
            return "✅ CRITICAL", "🟢"
        elif pct >= self.COVERAGE_THRESHOLDS['good']:
            return "✅ GOOD", "🟢"
        elif pct >= self.COVERAGE_THRESHOLDS['fair']:
            return "⚠️  FAIR", "🟡"
        else:
            return "❌ POOR", "🔴"

    def display_report(self):
        """Display current coverage report"""
        print("\n" + "=" * 80)
        print("CIAF CODE COVERAGE REPORT".center(80))
        print("=" * 80)

        if not self.history:
            print("No coverage data available. Run with coverage first.")
            return

        latest = self.history[-1]
        timestamp = latest.get('timestamp', 'Unknown')
        total = latest.get('total_lines', 0)
        covered = latest.get('covered_lines', 0)
        pct = latest.get('coverage_pct', 0)

        status, icon = self.get_coverage_status()

        print(f"\n{icon} {status}")
        print(f"   Date: {timestamp}")
        print(f"   Covered: {covered:,} / {total:,} lines")
        print(f"   Coverage: {pct:.1f}%")
        print(f"   Target: 80% (fail_under threshold)")

        # Show progress
        if len(self.history) > 1:
            prev = self.history[-2]
            prev_pct = prev.get('coverage_pct', 0)
            delta = pct - prev_pct
            symbol = "↑" if delta > 0 else "↓" if delta < 0 else "→"
            print(f"   Change: {symbol} {delta:+.1f}% from last run")

        # Show files by coverage
        files = latest.get('files', {})
        if files:
            print("\n📊 Top Priority Files (< 50% coverage):")
            low_coverage = sorted(
                [(f, c) for f, c in files.items() if c < 50],
                key=lambda x: x[1]
            )[:10]

            for fpath, cov in low_coverage:
                fname = fpath.split('/')[-1]
                bar = self._coverage_bar(cov)
                print(f"   {bar} {fname:40s} {cov:5.1f}%")

            print("\nFiles at Target (80%+ coverage):")
            high_coverage = sorted(
                [(f, c) for f, c in files.items() if c >= 80],
                key=lambda x: x[1],
                reverse=True
            )[:5]

            for fpath, cov in high_coverage:
                fname = fpath.split('/')[-1]
                bar = self._coverage_bar(cov)
                print(f"   {bar} {fname:40s} {cov:5.1f}%")

        print("\n" + "=" * 80)

    def display_history(self):
        """Display coverage history"""
        print("\n📈 COVERAGE HISTORY\n")

        if not self.history:
            print("No history available.")
            return

        print(f"{'Date':<20} {'Coverage':<15} {'Lines':<20} {'Change':<10}")
        print("-" * 65)

        for i, record in enumerate(self.history):
            timestamp = record.get('timestamp', 'Unknown')[:16]
            pct = record.get('coverage_pct', 0)
            covered = record.get('covered_lines', 0)
            total = record.get('total_lines', 0)

            if i > 0:
                prev_pct = self.history[i-1].get('coverage_pct', 0)
                delta = pct - prev_pct
                delta_str = f"{delta:+.1f}%"
            else:
                delta_str = "—"

            print(f"{timestamp:<20} {pct:>5.1f}%         {covered:>6}/{total:<6} {delta_str:>10}")

    def display_detailed(self):
        """Display detailed coverage by file"""
        print("\n📋 DETAILED COVERAGE BY FILE\n")

        if not self.history:
            print("No coverage data available.")
            return

        latest = self.history[-1]
        files = latest.get('files', {})

        if not files:
            print("No file data available.")
            return

        # Group by coverage level
        groups = {
            '0% (Untested)': [],
            '1-20% (Critical)': [],
            '21-50% (Low)': [],
            '51-80% (Fair)': [],
            '81-100% (Good)': [],
        }

        for fpath, cov in files.items():
            fname = fpath.split('\\')[-1] if '\\' in fpath else fpath.split('/')[-1]

            if cov == 0:
                groups['0% (Untested)'].append((fname, cov))
            elif cov <= 20:
                groups['1-20% (Critical)'].append((fname, cov))
            elif cov <= 50:
                groups['21-50% (Low)'].append((fname, cov))
            elif cov <= 80:
                groups['51-80% (Fair)'].append((fname, cov))
            else:
                groups['81-100% (Good)'].append((fname, cov))

        for group_name, items in groups.items():
            if items:
                print(f"\n{group_name} ({len(items)} files):")
                for fname, cov in sorted(items, key=lambda x: x[1]):
                    bar = self._coverage_bar(cov, length=30)
                    print(f"   {bar} {fname:45s} {cov:5.1f}%")

    @staticmethod
    def _coverage_bar(pct: float, length: int = 20) -> str:
        """Create a coverage progress bar"""
        filled = int(pct / 100 * length)
        bar = "█" * filled + "░" * (length - filled)
        return f"[{bar}]"

    @staticmethod
    def _get_test_count() -> int:
        """Get total test count"""
        try:
            result = subprocess.run(
                ['python', '-m', 'pytest', 'tests/', '--collect-only', '-q'],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=Path(__file__).parent
            )

            # Parse test count from output
            for line in result.stdout.split('\n'):
                if 'test' in line.lower():
                    match = re.search(r'(\d+)', line)
                    if match:
                        return int(match.group(1))
        except:
            pass
        return 0

    def record_session(self):
        """Record current coverage metrics"""
        coverage = self.run_coverage()
        if coverage:
            coverage['test_count'] = self._get_test_count()
            self.history.append(coverage)
            self._save_history()
            return coverage
        return {}

    def print_summary(self):
        """Print one-line summary"""
        if not self.history:
            print("No coverage data")
            return

        latest = self.history[-1]
        pct = latest.get('coverage_pct', 0)
        covered = latest.get('covered_lines', 0)
        total = latest.get('total_lines', 0)
        tests = latest.get('test_count', 0)

        print(f"✅ Coverage: {pct:.1f}% ({covered:,}/{total:,}) | Tests: {tests}")


def main():
    """Main entry point"""
    tracker = CoverageTracker()

    if len(sys.argv) > 1:
        if sys.argv[1] == '--history':
            tracker.display_history()
        elif sys.argv[1] == '--detailed':
            tracker.display_detailed()
        elif sys.argv[1] == '--record':
            tracker.record_session()
            tracker.display_report()
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Options: --history, --detailed, --record")
    else:
        # Display current report
        tracker.display_report()


if __name__ == '__main__':
    main()
