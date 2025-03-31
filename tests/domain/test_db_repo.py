import pytest
from counter.adapters.db_count_repo import DbObjectCountRepo

@pytest.fixture(scope='module')
def repo():
    repo = DbObjectCountRepo("sqlite:///:memory:")
    yield repo  # In-memory SQLite for fast integration tests

def test_save_counts(repo):
    counts = {"cat": 3, "dog": 2}
    threshold = 0.5

    # Test clearly saving to the database
    repo.save_counts(counts, threshold)

    # Verify data was saved
    session = repo.Session()
    results = session.query(repo.ObjectCount).all()

    assert len(results) == 2
    saved_classes = {result.object_class for result in results}
    assert saved_classes == {"cat", "dog"}
