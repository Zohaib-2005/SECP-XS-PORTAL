import httpx, orjson
from .config import settings

def fallback_classifier(complaint: str, taxonomy: dict):
    """Simple rule-based classifier as fallback"""
    complaint_lower = complaint.lower()
    
    # Simple keyword-based classification rules
    if any(word in complaint_lower for word in ['broker', 'agent', 'advisor']):
        return {
            "category": "Broker",
            "sub_category": "Conduct", 
            "nature_of_issue": "General broker issue"
        }
    elif any(word in complaint_lower for word in ['insurance', 'policy', 'claim', 'health']):
        return {
            "category": "Insurance",
            "sub_category": "Policyholder Claims",
            "nature_of_issue": "Insurance-related issue"
        }
    elif any(word in complaint_lower for word in ['investment', 'fund', 'portfolio', 'mutual']):
        return {
            "category": "Investment",
            "sub_category": "Fund Management",
            "nature_of_issue": "Investment-related issue"
        }
    else:
        return {
            "category": "General",
            "sub_category": "Other",
            "nature_of_issue": "General financial complaint"
        }

async def classify_with_llm(complaint: str, examples: list, taxonomy: dict):
    try:
        # OpenAI API compatible payload
        payload = {
            "model": "gpt-3.5-turbo",
            "temperature": 0.1,
            "messages": [
                {
                    "role": "system", 
                    "content": """You are a SECP complaint classifier. Return JSON with: category, sub_category, nature_of_issue."""
                },
                {
                    "role": "user", 
                    "content": f"Classify this complaint: {complaint}"
                }
            ]
        }
        
        headers = {
            "Authorization": f"Bearer {settings.llm_key}",
            "Content-Type": "application/json"
        }
        
        print(f"Attempting LLM classification...")
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(settings.llm_url, headers=headers, json=payload)
            
            if resp.status_code != 200:
                print(f"LLM API failed with {resp.status_code}, using fallback classifier")
                return fallback_classifier(complaint, taxonomy)
            
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            result = orjson.loads(content)
            print("LLM classification successful!")
            return result
            
    except Exception as e:
        print(f"LLM Error: {e}, using fallback classifier")
        return fallback_classifier(complaint, taxonomy)
