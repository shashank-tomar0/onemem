from __future__ import annotations

from onemem.onemem_types import ExtractionStatus


def test_extraction_status_values():
    assert ExtractionStatus.PENDING == "pending"
    assert ExtractionStatus.COMPLETED == "completed"
