import os
import asyncio
from dotenv import load_dotenv
from anthropic import AsyncAnthropic

# Load environment variables
load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_BASE_URL = os.getenv("ANTHROPIC_BASE_URL")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-opus-4-6")

print(f"API Key: {ANTHROPIC_API_KEY[:20]}...")
print(f"Base URL: {ANTHROPIC_BASE_URL}")
print(f"Model: {ANTHROPIC_MODEL}")

async def test_claude():
    try:
        # Create client with custom base URL
        if ANTHROPIC_BASE_URL:
            client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY, base_url=ANTHROPIC_BASE_URL)
            print(f"✅ Using custom API endpoint: {ANTHROPIC_BASE_URL}")
        else:
            client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)

        print("\n🔄 Testing Claude API connection with new configuration...")

        # Send a test message
        response = await client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=100,
            messages=[{
                "role": "user",
                "content": "Hello! Please respond with just 'Test successful'"
            }]
        )

        response_text = response.content[0].text
        print(f"✅ Response: {response_text}")
        print("\n✅ Test passed! New API configuration works.")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_claude())
    exit(0 if success else 1)
