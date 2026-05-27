import json
import uuid
import pytest
import pandas as pd
import os
from pathlib import Path
from src.orchestrator import Orchestrator
from src.config import Config

@pytest.fixture(autouse=True)
def clear_cache():
    cache_file = Config.DATA_DIR / "cache.json"
    if cache_file.exists():
        os.remove(cache_file)

@pytest.fixture
def mock_candidates():
    data = {
        'restaurant_name': ['A'],
        'location': ['delhi'],
        'location_clean': ['delhi'],
        'cuisines': ['Italian'],
        'average_cost': [500],
        'budget_tier': ['Low'],
        'rating': [4.5],
        'votes': [100]
    }
    return pd.DataFrame(data)

@pytest.mark.skipif(Config.GROQ_API_KEY is None or Config.GROQ_API_KEY == "your_api_key_here", reason="Requires real Groq API key")
def test_real_llm_call(mock_candidates):
    class DummyReq:
        location = "delhi"
        cuisine = "Italian"
        budget = "Low"
        min_rating = 4.0
        qualitative = "A romantic place for an anniversary dinner"

    engine = Orchestrator()
    engine.df = mock_candidates
    
    candidates, widened = engine.filter_candidates(
        location="delhi",
        cuisine="Italian",
        budget="Low",
        min_rating=4.0
    )
    
    result = engine.get_llm_recommendations(candidates, DummyReq(), str(uuid.uuid4()), widened)
    
    assert "recommendations" in result
    assert result["source"] in ["LLM_Cached", "LLM_Agent_Pipeline", "LLM"]
    if len(result['recommendations']) > 0:
        assert result['recommendations'][0]['restaurant_name'] == 'A'

def test_llm_malformed_json_fallback(mock_candidates, mocker):
    mocker.patch('src.agents.base.Config.GROQ_API_KEY', 'dummy_key')
    engine = Orchestrator()
    
    mock_client = mocker.MagicMock()
    mock_response = mocker.MagicMock()
    mock_response.choices[0].message.content = "{ broken json"
    mock_client.chat.completions.create.return_value = mock_response
    
    mocker.patch('src.agents.base.Groq', return_value=mock_client)
    
    class DummyReq:
        location = "delhi"
        cuisine = "Italian"
        budget = "Low"
        min_rating = 4.0
        qualitative = "Something that triggers fallback"
        
    result = engine.get_llm_recommendations(mock_candidates, DummyReq(), "test", None)
    
    assert result['source'] == 'Deterministic Fallback'
    assert result['recommendations'][0]['restaurant_name'] == 'A'

def test_successful_llm_parsing(mock_candidates, mocker):
    mocker.patch('src.agents.base.Config.GROQ_API_KEY', 'dummy_key')
    
    mock_client = mocker.MagicMock()
    mocker.patch('src.agents.base.Groq', return_value=mock_client)
    
    engine = Orchestrator()
    mocker.patch('src.orchestrator.prompt_cache.get', return_value=None)
    
    class DummyReq:
        location = "delhi"
        cuisine = "Italian"
        budget = "Low"
        min_rating = 4.0
        qualitative = "A completely different qualitative prompt to avoid cache hits"
        
    valid_ranker_json = json.dumps({
        "raw_recommendations": [
            {
                "restaurant_name": "A",
                "rank": 1,
                "cuisine": "Italian",
                "rating": 4.5,
                "estimated_cost_tier": "Low",
                "justification": "Because it matches the prompt",
                "highlighted_features": ["cozy"]
            }
        ]
    })
    
    valid_critic_json = json.dumps({
        "rqs_score": 5,
        "critic_notes": "Perfect match"
    })
    
    mock_response_ranker = mocker.MagicMock()
    mock_response_ranker.choices[0].message.content = valid_ranker_json
    
    mock_response_critic = mocker.MagicMock()
    mock_response_critic.choices[0].message.content = valid_critic_json
    
    mock_client.chat.completions.create.side_effect = [mock_response_ranker, mock_response_critic]
    
    result = engine.get_llm_recommendations(mock_candidates, DummyReq(), "test", None)
    
    assert result['source'] == 'LLM_Agent_Pipeline'
    assert result['recommendations'][0]['justification'] == "Because it matches the prompt"
    assert result['recommendations'][0]['restaurant_name'] == 'A'
