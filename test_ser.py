import asyncio
from pydantic_ai.messages import ModelMessage, ModelRequest, ModelResponse, UserPromptPart, TextPart
from pydantic import TypeAdapter
import json

async def test():
    messages = [
        ModelRequest(parts=[UserPromptPart(content="Hello")]),
        ModelResponse(parts=[TextPart(content="Hi")])
    ]
    
    # Serialize
    # ModelMessage is a Union, so we can use TypeAdapter
    adapter = TypeAdapter(list[ModelMessage])
    data = adapter.dump_python(messages, mode='json')
    print(f"Serialized: {json.dumps(data, indent=2)}")
    
    # Deserialize
    messages2 = adapter.validate_python(data)
    print(f"Deserialized: {messages2}")
    assert messages == messages2

if __name__ == "__main__":
    asyncio.run(test())
