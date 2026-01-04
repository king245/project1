
import os
import sys

# Add backend to path so we can import app modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

try:
    from app.services.llm_factory import llm_factory
    from app.core.config import settings
    from app.services.llm_factory import llm_factory
    from app.core.config import settings
    from langchain_anthropic import ChatAnthropic
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

def test_llm_integration():
    print("--- Testing LLM Integration ---")
    
    # 1. Check Config
    print(f"API Key Configured: {'Yes' if settings.ANTHROPIC_API_KEY else 'No'}")
    
    # 2. Check Factory
    llm = llm_factory.create_llm()
    print(f"LLM Type: {type(llm)}")
    
    if isinstance(llm, ChatAnthropic):
        print("Success: Factory returned ChatAnthropic instance.")
        
        # 3. Test Call
        print("Sending test message...")
        try:
            response = llm.invoke("Hello, are you ready?")
            print(f"Response: {response.content}")
            print("Integration Success!")
        except Exception as e:
            print(f"Error calling API: {e}")
    else:
        print(f"Failure: Expected ChatAnthropic, got {type(llm)}")

if __name__ == "__main__":
    test_llm_integration()
