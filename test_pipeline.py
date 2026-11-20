import json
from unittest.mock import MagicMock, patch
from agent import run_verity_agent

@patch("agent.search_tavily")
@patch("agent.get_nebius_client")
@patch("agent.fetch_available_nebius_models")
def test_full_pipeline_flow(mock_fetch_models, mock_get_client, mock_search):
    # 1. Mock search return
    mock_search.return_value = [
        {
            "id": 1,
            "title": "NASA Artemis II Details",
            "url": "https://nasa.gov/artemis-2",
            "content": "Artemis II is targeted for September 2025 with Reid Wiseman, Victor Glover, Christina Koch, and Jeremy Hansen.",
            "domain": "nasa.gov",
            "score": 0.95
        },
        {
            "id": 2,
            "title": "ESA Artemis Participation",
            "url": "https://esa.int/artemis",
            "content": "ESA provides the European Service Module for the Orion spacecraft.",
            "domain": "esa.int",
            "score": 0.91
        }
    ]

    # 2. Mock model discovery
    mock_fetch_models.return_value = [
        "meta-llama/Llama-3.3-70B-Instruct",
        "Qwen/Qwen2.5-72B-Instruct"
    ]

    # 3. Mock LLM completion
    mock_client = MagicMock()
    mock_completion = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = json.dumps({
        "answer": "Artemis II is scheduled for September 2025 carrying a crew of four [1]. The Orion spacecraft features a service module provided by ESA [2].",
        "key_findings": [
            {
                "claim": "Mission target launch is September 2025 with four crew members.",
                "source_ids": [1]
            },
            {
                "claim": "ESA supplies the European Service Module.",
                "source_ids": [2, 99] # 99 is phantom
            }
        ],
        "confidence": "High",
        "confidence_reason": "Direct confirmation from space agencies.",
        "conflicts": "None identified across retrieved sources.",
        "gaps": "Final countdown rehearsal dates not specified in sources."
    })
    mock_completion.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_completion
    mock_get_client.return_value = mock_client

    # Execute
    res = run_verity_agent(
        question="What is the launch date and crew of Artemis II?",
        tavily_api_key="tvly-mock",
        nebius_api_key="neb-mock"
    )

    # Assertions
    assert res["model_used"] == "meta-llama/Llama-3.3-70B-Instruct", f"Expected Llama-3.3, got {res['model_used']}"
    assert len(res["sources"]) == 2, "Expected 2 sources"
    assert res["confidence"] == "High"
    assert len(res["key_findings"]) == 2
    # Verify phantom 99 was stripped
    assert res["key_findings"][1]["source_ids"] == [2], f"Expected [2], got {res['key_findings'][1]['source_ids']}"
    assert res["citations_verified"] is True
    print("ALL FULL PIPELINE ASSERTIONS PASSED!")

if __name__ == "__main__":
    test_full_pipeline_flow()
