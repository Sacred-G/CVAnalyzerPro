import google.generativeai as genai
import sqlite3
import os

def get_gemini_key(username):
    conn = sqlite3.connect('data.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('SELECT gemini_key FROM userstable WHERE username = ?', (username,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def get_gemini_response(username,resume_text, requirements):
    # Fetch Gemini key from database
    gemini_api_key = get_gemini_key(username)
    if not gemini_api_key:
        return False
    
    os.environ['GOOGLE_API_KEY'] = gemini_api_key
    genai.configure(api_key=gemini_api_key)
    

    model = genai.GenerativeModel('gemini-pro')

    try:
        response = model.generate_content(
        "Act like you are an expert Resume Scorer. You will always give the similarities and dissimilarities with the Requirements and Resume. Then give the score on a range of 100 percent. Now, score this resume based on the following requirements:\n\n" +
        "Requirements: " + requirements + "\n\n" +
        "Resume: " + resume_text
        )
        return response.text
    except Exception as e:
        print(e)
        return False
