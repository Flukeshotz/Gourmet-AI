import pytest
import pandas as pd
from src.orchestrator import Orchestrator
from src.config import Config

@pytest.fixture
def mock_candidates():
    data = {
        'restaurant_name': ['A', 'B', 'C', 'D'],
        'location': ['delhi', 'delhi', 'mumbai', 'delhi'],
        'location_clean': ['delhi', 'delhi', 'mumbai', 'delhi'],
        'cuisines': ['Italian', 'North Indian', 'Italian', 'Italian'],
        'average_cost': [500, 2000, 500, 500],
        'budget_tier': ['Low', 'High', 'Low', 'Low'],
        'rating': [4.5, 4.0, 4.8, 3.5],
        'votes': [100, 200, 300, 50]
    }
    return pd.DataFrame(data)

def test_strict_deterministic_filtering(mock_candidates):
    engine = Orchestrator()
    engine.df = mock_candidates
    
    # Filter for Delhi, Italian, Low budget, rating >= 4.0
    res, msg = engine.filter_candidates("delhi", cuisine="Italian", budget="Low", min_rating=4.0)
    
    # Only A matches all
    assert len(res) == 1
    assert res.iloc[0]['restaurant_name'] == 'A'

def test_auto_widening_edge_case(mock_candidates):
    engine = Orchestrator()
    engine.df = mock_candidates
    
    # Filter for a non-existent combination: Delhi, Mexican, High budget, Rating 5.0
    # The engine should widen and eventually just return top rated places in Delhi
    res, msg = engine.filter_candidates("delhi", cuisine="Mexican", budget="High", min_rating=5.0)
    
    # Should not be empty because it relaxes constraints
    assert len(res) > 0
    # Should be sorted by popularity (rating * votes) -> B has 4.0*200 = 800, A has 4.5*100=450
    assert res.iloc[0]['restaurant_name'] == 'B'

def test_candidate_truncation(mock_candidates, monkeypatch):
    engine = Orchestrator()
    
    # Create a large dataset of 50 identical items
    large_df = pd.concat([mock_candidates] * 20, ignore_index=True)
    engine.df = large_df
    
    # Set MAX_CANDIDATES to 5 for test
    monkeypatch.setattr(Config, 'MAX_CANDIDATES', 5)
    
    res, msg = engine.filter_candidates("delhi", cuisine="Italian", budget="Low", min_rating=3.0)
    
    # Should be truncated to 5
    assert len(res) == 5


