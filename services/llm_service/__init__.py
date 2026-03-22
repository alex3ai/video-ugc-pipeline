from typing import Optional
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LLMService:
    def __init__(self):
        """
        Initialize the LLM Service with Google Gemini API key
        """
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    async def test_connection(self) -> bool:
        """
        Test the connection to the Gemini API with a simple request
        """
        try:
            response = await self.model.generate_content_async("Hello")
            return response is not None
        except Exception as e:
            print(f"Error testing Gemini connection: {e}")
            return False
    
    async def generate_prompt_from_brief(self, brief: str) -> Optional[str]:
        """
        Generate a video prompt from a campaign brief using Gemini
        """
        try:
            prompt = f"""
                Based on the following campaign brief, generate a detailed prompt for a video generation AI.
                
                Campaign Brief: {brief}
                
                Generate a creative and detailed prompt that describes a video scene with vivid details,
                including visual elements, actions, duration, and any important aspects for video generation.
                Keep the prompt under 500 words.
            """
            
            response = await self.model.generate_content_async(prompt)
            return response.text if response else None
        except Exception as e:
            print(f"Error generating prompt from brief: {e}")
            return None


# Singleton instance
llm_service = LLMService()


def test_gemini_connection():
    """
    Test function to verify the connection to the Gemini API
    """
    try:
        import asyncio
        
        async def _test():
            return await llm_service.test_connection()
        
        return asyncio.run(_test())
    except Exception as e:
        print(f"Error during connection test: {e}")
        return False