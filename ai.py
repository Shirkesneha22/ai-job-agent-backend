import os
import json
from openai import OpenAI

# The OpenAI client automatically reads the OPENAI_API_KEY environment variable.
# We will initialize it lazily to avoid crashing immediately if the key is not set.

def get_client():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set.")
    return OpenAI(api_key=api_key)

def match_job(resume: str, job_description: str):
    prompt = f"Resume:\n{resume}\n\nJob Description:\n{job_description}\n\nOn a scale of 0 to 100, how well does this resume match the job description? Return ONLY the number."
    
    try:
        client = get_client()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10,
            temperature=0
        )
        score_text = response.choices[0].message.content.strip()
        score = "".join(filter(str.isdigit, score_text))
        return float(score) if score else 0.0
    except Exception as e:
        print(f"Error in match_job: {e}")
        return 0.0

def optimize_resume(resume: str, job_description: str):
    prompt = f"""
    You are an expert Career Coach and ATS (Applicant Tracking System) Specialist.
    
    Please optimize the provided resume for the given job description following these rules:
    - Improve summary
    - Add relevant skills
    - Optimize for ATS
    - Keep it realistic (do not hallucinate experiences)
    
    ### Inputs:
    - **Current Resume:**
    {resume}
    
    - **Job Description:**
    {job_description}
    
    ### Output Format:
    Return your response ONLY as a valid JSON object with the following structure:
    {{
        "updated_resume": "The full optimized resume text in Markdown",
        "changes_made": [
            "List of specific changes made to optimize for ATS"
        ]
    }}
    """
    
    try:
        client = get_client()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that only outputs JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" }
        )
        raw_content = response.choices[0].message.content
        structured_data = json.loads(raw_content)
        return structured_data
    except Exception as e:
        print(f"Error in optimize_resume: {e}")
        return {
            "updated_resume": resume,
            "changes_made": [f"Error occurred: OpenAI API request failed. Details: {str(e)}."]
        }
