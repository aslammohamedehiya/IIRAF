"""
AI-powered solution generator using Google Gemini LLM
"""
import os
import google.generativeai as genai
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SolutionGenerator:
    def __init__(self):
        """Initialize the Gemini AI solution generator."""
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.model = None
        
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-pro')
                print("[OK] Gemini AI solution generator initialized successfully")
            except Exception as e:
                print(f"[WARNING] Failed to initialize Gemini AI: {e}")
                print("  Falling back to simple aggregation method")
        else:
            print("[WARNING] GEMINI_API_KEY not found in environment")
            print("  Falling back to simple aggregation method")
    
    def generate_solution(self, query: str, search_results: List[Dict]) -> Dict:
        """
        Generate an AI-powered solution based on search results.
        
        Args:
            query: User's incident description
            search_results: List of similar incidents and KB articles
            
        Returns:
            Dict with 'steps', 'source', and 'metadata'
        """
        # If AI not available, use fallback
        if not self.model:
            return self._fallback_solution(search_results)
        
        try:
            # Prepare context from search results
            incidents = [r for r in search_results if r.get('type') == 'incident']
            kb_articles = [r for r in search_results if r.get('type') == 'kb']
            
            # Build the prompt
            prompt = self._build_prompt(query, incidents, kb_articles)
            
            # Generate solution using Gemini
            response = self.model.generate_content(prompt)
            
            # Parse the response
            solution_text = response.text
            steps = self._parse_steps(solution_text)
            
            return {
                'steps': steps,
                'source': 'ai_generated',
                'metadata': {
                    'incident_count': len(incidents),
                    'kb_count': len(kb_articles),
                    'model': 'gemini-pro'
                }
            }
            
        except Exception as e:
            print(f"[WARNING] AI generation failed: {e}")
            print("  Falling back to simple aggregation")
            return self._fallback_solution(search_results)
    
    def _build_prompt(self, query: str, incidents: List[Dict], kb_articles: List[Dict]) -> str:
        """Build the prompt for Gemini AI."""
        
        prompt = f"""You are an expert IT incident resolution assistant. A user has reported the following issue:

**User's Issue:**
{query}

**Context from Similar Incidents:**
"""
        
        # Add incident resolutions
        for i, inc in enumerate(incidents[:5], 1):
            resolution = inc.get('resolution', 'No resolution provided')
            prompt += f"\n{i}. Incident {inc.get('id', 'N/A')}: {resolution}"
        
        prompt += "\n\n**Context from Knowledge Base Articles:**\n"
        
        # Add KB article content
        for i, kb in enumerate(kb_articles[:3], 1):
            title = kb.get('title', 'Untitled')
            content = kb.get('content', 'No content')
            prompt += f"\n{i}. {title}: {content}"
        
        prompt += """

**Your Task:**
Based on the user's issue and the context provided above, generate a clear, step-by-step resolution plan. 

**Requirements:**
1. Synthesize information from multiple sources into a coherent plan
2. Provide 3-5 specific, actionable steps
3. Number each step clearly (Step 1, Step 2, etc.)
4. Be concise but specific
5. Include relevant commands or technical details where applicable
6. If steps conflict, choose the most common or reliable approach

**Format your response as:**
Step 1: [First action]
Step 2: [Second action]
Step 3: [Third action]
...

Generate the solution now:"""
        
        return prompt
    
    def _parse_steps(self, solution_text: str) -> List[str]:
        """Parse the AI response into individual steps."""
        steps = []
        lines = solution_text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            # Look for lines starting with "Step X:" or just numbered steps
            if line.startswith('Step ') or (line and line[0].isdigit() and ':' in line):
                # Remove "Step X:" prefix if present
                if line.startswith('Step '):
                    step_text = line.split(':', 1)[1].strip() if ':' in line else line
                else:
                    step_text = line.split(':', 1)[1].strip() if ':' in line else line
                
                if step_text:
                    steps.append(step_text)
        
        # If no steps found, try to split by sentences
        if not steps:
            steps = [s.strip() for s in solution_text.split('.') if s.strip()][:5]
        
        return steps[:5]  # Limit to 5 steps
    
    def _fallback_solution(self, search_results: List[Dict]) -> Dict:
        """Fallback to simple aggregation if AI is unavailable."""
        incidents = [r for r in search_results if r.get('type') == 'incident']
        kb_articles = [r for r in search_results if r.get('type') == 'kb']
        
        # Extract resolutions and KB content
        resolutions = [inc.get('resolution', '') for inc in incidents if inc.get('resolution')]
        kb_content = [kb.get('content', '') for kb in kb_articles if kb.get('content')]
        
        # Combine and deduplicate
        all_steps = resolutions + kb_content
        unique_steps = list(dict.fromkeys(all_steps))  # Preserve order while deduplicating
        
        return {
            'steps': unique_steps[:5],
            'source': 'aggregated',
            'metadata': {
                'incident_count': len(incidents),
                'kb_count': len(kb_articles),
                'model': 'fallback'
            }
        }

# Test the generator
if __name__ == "__main__":
    generator = SolutionGenerator()
    
    # Test data
    test_query = "Payment gateway returning 500 errors"
    test_results = [
        {
            'type': 'incident',
            'id': 'INC-001',
            'resolution': 'Restart the payment service pods using kubectl'
        },
        {
            'type': 'kb',
            'title': 'Payment Gateway Troubleshooting',
            'content': 'Check API rate limits and verify pod health'
        }
    ]
    
    solution = generator.generate_solution(test_query, test_results)
    print("\nGenerated Solution:")
    print(f"Source: {solution['source']}")
    print(f"Steps: {solution['steps']}")
