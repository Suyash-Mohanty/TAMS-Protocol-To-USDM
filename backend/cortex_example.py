"""
Cortex API Connection Example
=============================

This script demonstrates how to connect to Cortex API using LIGHTClient.

Usage:
    python cortex_example.py

On first run, a browser window will open for Microsoft authentication.
Log in with your Lilly credentials.
"""

import sys
import os

# Add light_client to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from light_client import LIGHTClient


# =============================================================================
# CONFIGURATION
# =============================================================================

CORTEX_BASE = "https://api.cortex.lilly.com"

# Replace with your model name
MODEL_NAME = "programtoolassist"  # Example model


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_client() -> LIGHTClient: #Microsoft Auth Login
    """
    Create and return an authenticated LIGHTClient instance.
    First call will open browser for authentication.
    """
    return LIGHTClient()


def ask_model(client: LIGHTClient, model_name: str, question: str) -> str:
    """
    Send a question to a Cortex model and return the response.
    
    Args:
        client: Authenticated LIGHTClient instance
        model_name: Name of the model to query
        question: The question/prompt to send
        
    Returns:
        Model's response as a string
    """
    endpoint = f"{CORTEX_BASE}/model/ask/{model_name}"
    
    response = client.post(endpoint, data={"q": question})
    
    if response.status_code != 200:
        raise Exception(f"Error {response.status_code}: {response.text}")
    
    return response.json().get('message', '')


def list_models(client: LIGHTClient) -> list:
    """
    List available models in Cortex.
    
    Args:
        client: Authenticated LIGHTClient instance
        
    Returns:
        List of available models
    """
    endpoint = f"{CORTEX_BASE}/model/list"
    
    response = client.get(endpoint)
    
    if response.status_code != 200:
        raise Exception(f"Error {response.status_code}: {response.text}")
    
    return response.json()


def evaluate_rag(client: LIGHTClient, model_name: str, question: str, 
                 ground_truth: str, metrics: list = None) -> dict:
    """
    Evaluate RAG response using RAGAS metrics.
    
    Args:
        client: Authenticated LIGHTClient instance
        model_name: Name of the model to evaluate
        question: The question to ask
        ground_truth: Expected/reference answer
        metrics: List of metrics (default: answer_correctness, faithfulness, etc.)
        
    Returns:
        Dictionary with RAGAS evaluation scores
    """
    if metrics is None:
        metrics = ["answer_correctness", "faithfulness", "answer_relevancy", "semantic_similarity"]
    
    endpoint = f"{CORTEX_BASE}/model/evaluate-rag/{model_name}"
    
    params = {
        "q": question,
        "ground_truth": ground_truth,
        "metrics": ",".join(metrics)
    }
    
    response = client.get(endpoint, params=params)
    
    if response.status_code != 200:
        raise Exception(f"Error {response.status_code}: {response.text}")
    
    return response.json()


# =============================================================================
# MAIN EXAMPLE
# =============================================================================

def main():
    print("=" * 60)
    print("CORTEX API CONNECTION EXAMPLE")
    print("=" * 60)
    
    # Step 1: Create authenticated client
    print("\n[1] Authenticating with Cortex...")
    print("    (A browser window may open for login)")
    
    try:
        client = get_client()
        print("    ✓ Authentication successful!")
    except Exception as e:
        print(f"    ✗ Authentication failed: {e}")
        return
    
    # Step 2: Test basic model call
    print(f"\n[2] Testing model call to '{MODEL_NAME}'...")
    
    try:
        question = "What is your name and what can you help me with?"
        response = ask_model(client, MODEL_NAME, question)
        
        print(f"    Question: {question}")
        print(f"    Response: {response[:200]}..." if len(response) > 200 else f"    Response: {response}")
        print("    ✓ Model call successful!")
    except Exception as e:
        print(f"    ✗ Model call failed: {e}")
    
    # Step 3: Example with custom prompt
    print(f"\n[3] Custom prompt example...")
    
    try:
        custom_prompt = """
        Generate a simple R function that calculates the mean of a numeric vector.
        Include error handling for non-numeric input.
        """
        
        response = ask_model(client, MODEL_NAME, custom_prompt)
        
        print(f"    Prompt: Generate R function for mean calculation")
        print(f"    Response preview: {response[:300]}..." if len(response) > 300 else f"    Response: {response}")
        print("    ✓ Custom prompt successful!")
    except Exception as e:
        print(f"    ✗ Custom prompt failed: {e}")
    
    print("\n" + "=" * 60)
    print("SETUP COMPLETE - You can now use Cortex API!")
    print("=" * 60)
    
    print("\nNext steps:")
    print("  1. Modify MODEL_NAME to use your specific model")
    print("  2. Use ask_model() function with your prompts")
    print("  3. Use evaluate_rag() for RAGAS evaluation")


if __name__ == "__main__":
    main()
