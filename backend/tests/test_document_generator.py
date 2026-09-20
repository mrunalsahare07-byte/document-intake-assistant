from app.domain.state import PersonalWishesState
from app.document.generator import DocumentGenerator

def test_document_disclaimer_and_generation():
    state = PersonalWishesState(full_name="Clark Kent", covers_worldwide_assets=True)
    doc = DocumentGenerator.generate(state)
    assert "DISCLAIMER: This document is entirely fictional" in doc
    assert "Clark Kent" in doc
    assert "worldwide" in doc