"""Tests for the NLP gap detector and document analyzer."""

from __future__ import annotations

import numpy as np

from iso13485_audit.nlp.gap_detector import GapDetector
from iso13485_audit.nlp.preprocessing import chunk_text, split_sections


class _FakeReq:
    def __init__(self, number, risk_weight=3):
        self.risk_weight = risk_weight
        self.evidence_guidance = "evidence"
        self.clause = type("C", (), {"clause_number": number})()


def test_gap_detected_below_threshold():
    detector = GapDetector(similarity_threshold=0.2)
    requirements = [_FakeReq("7.3.1"), _FakeReq("7.3.2")]
    # First requirement well covered (0.5), second not (0.05).
    coverage = np.array([[0.5, 0.1], [0.05, 0.02]])
    gaps = detector.detect(coverage, requirements)
    assert len(gaps) == 1
    assert gaps[0].requirement.clause.clause_number == "7.3.2"


def test_coverage_score():
    detector = GapDetector(similarity_threshold=0.2)
    coverage = np.array([[0.5], [0.05], [0.3]])
    # 2 of 3 requirements covered.
    assert detector.coverage_score(coverage) == 2 / 3


def test_high_risk_gap_is_high_severity():
    detector = GapDetector(similarity_threshold=0.2)
    requirements = [_FakeReq("7.5.6", risk_weight=5)]
    coverage = np.array([[0.0]])
    gaps = detector.detect(coverage, requirements)
    assert gaps[0].severity == "high"
    assert gaps[0].confidence == 1.0


def test_split_sections_on_numbered_headings():
    text = "4.1 General\nSome body text.\n7.3 Design\nMore body."
    sections = split_sections(text)
    headings = [s.heading for s in sections]
    assert any("4.1" in h for h in headings)
    assert any("7.3" in h for h in headings)


def test_chunk_text_overlap():
    text = "x" * 2500
    chunks = chunk_text(text, max_chars=1000, overlap=100)
    assert len(chunks) >= 3
    assert all(len(c) <= 1000 for c in chunks)
