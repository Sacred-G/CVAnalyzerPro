import streamlit as st
import sqlite3
from gpt_response import get_gpt_response
from gemini_response import get_gemini_response
from pdf_scraper import extract_text_from_pdf
import hashlib

# Initialize session state for login
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ''
if 'last_page' not in st.session_state:
    st.session_state.last_page = 'Home 🏠'

# Function to hash passwords
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# Function to check hashes
def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False

# Database connection
conn = sqlite3.connect('data.db', check_same_thread=False)
c = conn.cursor()

# Create the table
def create_usertable():
    c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT, password TEXT, gemini_key TEXT, openai_key TEXT)')

# Add user data
def add_userdata(username, password, gemini_key, openai_key):
    c.execute('INSERT INTO userstable(username, password, gemini_key, openai_key) VALUES (?,?,?,?)', (username, password, gemini_key, openai_key))
    conn.commit()

# Login user
def login_user(username, password):
    c.execute('SELECT * FROM userstable WHERE username =? AND password = ?', (username, password))
    data = c.fetchall()
    return data

# Update user data
def update_userdata(username, new_password, new_gemini_key, new_openai_key):
    c.execute('UPDATE userstable SET password = ?, gemini_key = ?, openai_key = ? WHERE username = ?', (new_password, new_gemini_key, new_openai_key, username))
    conn.commit()

# Streamlit UI
def main():
    st.markdown("<h1 style='text-align: center; color: blue;'>📄 CVAnalyzerPro 🚀</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Empower Your Hiring with AI 🤖</h3>", unsafe_allow_html=True)

    


    menu = ["Home 🏠", "Login 🔑", "SignUp 📝", "Resume Scorer 📊", "Settings ⚙️"]
    
    # Function to update the last page and rerun the app
    def update_page_and_rerun(new_page):
        st.session_state.last_page = new_page
        st.experimental_rerun()

    if st.session_state.logged_in:
        if st.session_state.last_page not in menu:
            st.session_state.last_page = 'Home 🏠'
        choice = st.sidebar.selectbox("Menu 📜", menu, index=menu.index(st.session_state.last_page))
        # Update and rerun if the page choice has changed
        if choice != st.session_state.last_page:
            update_page_and_rerun(choice)
    else:
        choice = st.sidebar.selectbox("Menu 📜", ["Home 🏠", "Login 🔑", "SignUp 📝"])
        if choice != st.session_state.last_page:
            update_page_and_rerun(choice)

    if choice == "Home 🏠":
        st.subheader("Welcome to CVAnalyzerPro! 🌟")
        st.info("The ultimate tool for AI-driven resume analysis and scoring! 💼")
        st.info("""
        ## About CVAnalyzerPro 🚀
        
        **CVAnalyzerPro** is a cutting-edge tool designed to revolutionize the hiring process. 🤖💼 Using advanced AI algorithms, it provides insightful analysis and scoring of resumes, helping recruiters and HR professionals make informed decisions. 

        Whether you're dealing with hundreds of applications or searching for that one perfect candidate, **CVAnalyzerPro** simplifies and streamlines your workflow. 📊🔍

        ### Features:
        - **AI-Powered Scoring**: Utilizing the latest in machine learning, CVAnalyzerPro scores resumes based on your custom requirements. 🧠✅
        - **Customizable Criteria**: Tailor the scoring criteria to fit the specific needs of your job opening. 🎯📝
        - **Efficient Filtering**: Quickly identify top candidates from a large pool of applicants. 🏅📈
        - **User-Friendly Interface**: Easy to use, no matter your tech skill level. 👩‍💻👨‍💻

        ### Get in Touch:
        - **Email**: [kowshikcseruet1998@gmail.com](mailto:kowshikcseruet1998@gmail.com) 📧
        - **LinkedIn**: [https://www.linkedin.com/in/kowshik24/](https://www.linkedin.com/in/kowshik24/) 💼
        - **GitHub**: [https://github.com/kowshik24](https://github.com/kowshik24) 🌐

        ### Stay ahead in the recruitment game with CVAnalyzerPro! 🏆🚀
        """)
        st.session_state.last_page = choice

    elif choice == "Login 🔑":
        if st.session_state.logged_in:
            st.success(f"Already logged in as {st.session_state.username} 👋")
        else:
            st.subheader("Login Section 🔐")
            username = st.sidebar.text_input("User Name 👤")
            password = st.sidebar.text_input("Password 🔒", type='password')
            if st.sidebar.button("Login 🚪"):
                create_usertable()
                hashed_password = make_hashes(password)
                result = login_user(username, check_hashes(password, hashed_password))
                if result:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.last_page = "Resume Scorer 📊"
                    st.experimental_rerun()

    elif choice == "SignUp 📝":
        st.subheader("Create New Account 🌱")
        st.info("Don't have GOOGLE API KEY? Get one here: https://makersuite.google.com/app/apikey")
        st.info("Don't have OPENAI API KEY? Get one here: https://platform.openai.com/api-keys")
        new_user = st.text_input("Username 👤")
        new_password = st.text_input("Password 🔑", type='password')
        new_gemini_key = st.text_input("Gemini API Key 🌐")
        new_openai_key = st.text_input("OpenAI API Key 🌐")
        if st.button("Signup 🌟"):
            create_usertable()
            add_userdata(new_user, make_hashes(new_password), new_gemini_key, new_openai_key)
            st.success("You have successfully created an account ✅")
            st.info("Go to Login Menu to login 🔑")

    elif choice == "Resume Scorer 📊":
        if st.session_state.logged_in:
            st.subheader("Resume Scorer 📈")
            resume_file = st.file_uploader("Upload Resume 📁", type=['pdf'])
            requirement_method = st.selectbox("Requirement Input Method 📋", ["Type", "Upload PDF"])
            if requirement_method == "Type":
                requirements = st.text_area("Enter Requirements ✍️")
            else:
                requirements_file = st.file_uploader("Upload Requirements 📁", type=['pdf'])
                if requirements_file is not None:
                    requirements = extract_text_from_pdf(requirements_file)
            model_choice = st.selectbox("Choose AI Model 🤖", ["GPT", "Gemini"])
            if st.button("Score 🏆"):
                if resume_file is not None:
                    resume_text = extract_text_from_pdf(resume_file)
                    username = st.session_state.username
                    if model_choice == "GPT":
                        score = get_gpt_response(username,resume_text, requirements)
                        if score == False:
                            st.error("Error: OpenAI API key not found. Please update your API keys in the Settings menu.")
                            st.stop()
                    elif model_choice == "Gemini":
                        score = get_gemini_response(username,resume_text, requirements)
                        if score == False:
                            st.error("Error: Gemini API key not found. Please update your API keys in the Settings menu.")
                            st.stop()
                    st.write("Score: ", score)
            st.session_state.last_page = choice
        else:
            st.warning("Please login to access this feature 🔐")
    elif choice == "Settings ⚙️":
        if st.session_state.logged_in:
            st.subheader("Update Your API Keys and Password 🔧")
            new_password = st.text_input("New Password 🔑", type='password')
            new_gemini_key = st.text_input("New Gemini API Key 🌐",type='password')
            new_openai_key = st.text_input("New OpenAI API Key 🌐",type='password')
            if st.button("Update 🔄"):
                update_userdata(st.session_state.username, make_hashes(new_password), new_gemini_key, new_openai_key)
                st.success("Settings Updated Successfully ✅")
            st.session_state.last_page = choice
        else:
            st.warning("Please login to access this feature 🔐")
    # Contact Form
    with st.expander("Contact us"):
        with st.form(key='contact', clear_on_submit=True):
            email = st.text_input('Contact Email')
            st.text_area("Query",placeholder="Please fill in all the information or we may not be able to process your request")  
            submit_button = st.form_submit_button(label='Send Information')

if __name__ == '__main__':
    st.set_page_config(page_title="📄CVAnalyzerPro🔎",
                       page_icon="✨", layout="centered", initial_sidebar_state="auto")
    main()
