import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"

def match_job(resume: str, job_description: str):
    prompt = f"Resume:\n{resume}\n\nJob Description:\n{job_description}\n\nOn a scale of 0 to 100, how well does this resume match the job description? Return ONLY the number."
    payload = {
        "model": "llama3",
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response_json = response.json()
        score_text = response_json.get("response", "0").strip()
        # Clean the response to only include digits
        score = "".join(filter(str.isdigit, score_text))
        return float(score) if score else 0.0
    except Exception as e:
        print(f"Error in match_job: {e}")
        return 0.0

def optimize_resume(resume: str, job_description: str):
    prompt = f"""
    You are an expert Career Coach and ATS (Applicant Tracking System) Specialist with 20 years of experience in recruitment.
    
    ### Task:
    Optimize the provided resume for the given job description. Ensure the resume is highly competitive for both ATS algorithms and human recruiters.
    
    ### Inputs:
    - **Current Resume:**
    {resume}
    
    - **Job Description:**
    {job_description}
    
    ### Requirements:
    1. **Keywords:** Naturally integrate high-impact keywords and skills identified from the job description.
    2. **Impact:** Use strong action verbs and the STAR (Situation, Task, Action, Result) method for bullet points where possible.
    3. **Formatting:** Use professional Markdown formatting (Headers, Bullet points, Bold text).
    4. **Conciseness:** Keep it professional and remove irrelevant details that don't align with the target role.
    5. **Truthfulness:** Do NOT hallucinate skills or experiences. Only optimize based on existing information and the job context.
    
    ### Output Format:
    Return your response ONLY as a JSON object with the following structure:
    {{
        "updated_resume": "The full optimized resume text in Markdown",
        "changes_made": [
            "List of specific changes made to optimize for ATS",
            "Example: Added keyword 'Kubernetes' to skills section",
            "Example: Rephrased experience at Google to emphasize leadership results"
        ]
    }}
    
    Ensure the response is valid JSON.
    """
    
    payload = {
        "model": "llama3",
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response_json = response.json()
        raw_content = response_json.get("response", "")
        
        # Try to parse the JSON response
        try:
            structured_data = json.loads(raw_content)
            return structured_data
        except json.JSONDecodeError:
            # Fallback if AI didn't return valid JSON
            return {
                "updated_resume": raw_content or resume,
                "changes_made": ["Optimization complete (structural changes applied)"]
            }
            
    except Exception as e:
        print(f"Error in optimize_resume: {e}")
        return {
            "updated_resume": resume,
            "changes_made": [f"Error occurred: {str(e)}"]
        }
