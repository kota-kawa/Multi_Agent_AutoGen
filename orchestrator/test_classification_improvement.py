#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script to verify that the improved classification logic works correctly.
This tests the fallback keyword-based classification without requiring API keys.
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, '.')

async def test_classification():
    """Test the improved classification logic"""
    print("=== Testing Improved Classification Logic ===\n")
    
    # Create a mock orchestrator to test classification logic
    try:
        from autogen_router import Orchestrator
        
        # Mock the _chat method to simulate classifier failure/success
        class TestOrchestrator(Orchestrator):
            def __init__(self):
                # Don't initialize the client - we'll mock the _chat method
                pass
            
            async def _chat(self, system: str, user: str) -> str:
                # Simulate a malformed JSON response to test fallback logic
                return "Invalid JSON response that should trigger keyword fallback"
        
        orch = TestOrchestrator()
        
        # Test cases
        test_cases = [
            {
                "prompt": "Pythonでウェブサーバーのコードを書いてください",
                "expected": "coder",
                "description": "Programming request"
            },
            {
                "prompt": "データ分析をして統計的な検証をしたい",
                "expected": "analyst", 
                "description": "Data analysis request"
            },
            {
                "prompt": "京都旅行のプランを立ててください。おすすめの観光スポットは？",
                "expected": "travel",
                "description": "Travel planning request"
            },
            {
                "prompt": "今日の天気はどうですか？",
                "expected": "none",
                "description": "General question"
            },
            {
                "prompt": "FlaskのAPIサーバーを実装したい。デプロイメント方法も教えて",
                "expected": "coder",
                "description": "Complex programming request"
            },
            {
                "prompt": "機械学習モデルの評価指標について。精度と再現率の違いは？",
                "expected": "analyst",
                "description": "ML analysis question" 
            }
        ]
        
        print(f"Running {len(test_cases)} classification tests...\n")
        
        results = []
        for i, test_case in enumerate(test_cases, 1):
            print(f"Test {i}: {test_case['description']}")
            print(f"Prompt: {test_case['prompt']}")
            
            try:
                # Test just the classification
                result = await orch.classify_async(test_case['prompt'])
                expected = test_case['expected']
                
                print(f"Expected: {expected}")
                print(f"Actual: {result}")
                
                if result == expected:
                    print("✅ PASS: Correct classification")
                    results.append(True)
                else:
                    print(f"❌ FAIL: Expected {expected}, got {result}")
                    results.append(False)
                    
            except Exception as e:
                print(f"❌ ERROR: {e}")
                results.append(False)
            
            print("-" * 50)
        
        success_rate = sum(results) / len(results) * 100
        print(f"\n=== Results ===")
        print(f"Success Rate: {success_rate:.0f}% ({sum(results)}/{len(results)})")
        
        if all(results):
            print("✅ All classification tests passed!")
        else:
            print("⚠️ Some tests failed. Check the logic above.")
            
        return all(results)
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

async def test_mock_orchestrator():
    """Test that the mock orchestrator still works correctly"""
    print("\n=== Testing Mock Orchestrator ===\n")
    
    try:
        from app import MockOrchestrator
        
        orch = MockOrchestrator()
        
        test_cases = [
            ("Pythonでコードを書いて", "coder"),
            ("データ分析をしたい", "analyst"),
            ("旅行プランを作って", "travel"),
            ("今日は何曜日？", "none")
        ]
        
        results = []
        for prompt, expected in test_cases:
            result = await orch.ask_async(prompt)
            actual = result.get('selected')
            
            if actual == expected:
                print(f"✅ '{prompt}' → {actual}")
                results.append(True)
            else:
                print(f"❌ '{prompt}' → expected {expected}, got {actual}")
                results.append(False)
        
        success_rate = sum(results) / len(results) * 100
        print(f"\nMock Success Rate: {success_rate:.0f}% ({sum(results)}/{len(results)})")
        
        return all(results)
        
    except Exception as e:
        print(f"❌ Mock test error: {e}")
        return False

async def main():
    """Main test function"""
    print("Agent Classification Improvement Test")
    print("=" * 60)
    
    classification_success = await test_classification()
    mock_success = await test_mock_orchestrator()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print(f"Improved Classification: {'✅ Working' if classification_success else '❌ Issues'}")
    print(f"Mock Functionality: {'✅ Working' if mock_success else '❌ Issues'}")
    
    if classification_success and mock_success:
        print("\n🎉 All tests passed! The agent orchestration improvements are working correctly.")
        print("💡 The system now has better fallback classification logic.")
    else:
        print("\n⚠️ Some tests failed. Please check the implementation.")

if __name__ == "__main__":
    asyncio.run(main())