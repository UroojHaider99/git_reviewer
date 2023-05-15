import streamlit as st
import openai
import requests
import base64

# Set up the OpenAI API key
openai.api_key = st.secrets["API_KEY"]

# Headers to authenticate with the API using a Personal Access Token
headers = {
    "Authorization": st.secrets["GIT_KEY"],
    "Accept": "application/vnd.github.v3+json"
}

# Define a function to recursively process files and directories
def process_files(path):
    # GitHub API endpoint to retrieve the list of files in a path
    api_url = f"https://api.github.com/repos/{repo_name}/contents/{path}"
    
    # Make a GET request to the API to retrieve the list of files in the path
    response = requests.get(api_url, headers=headers)
    
    if response.status_code != 200:
        st.error(f"Error {response.status_code}: {response.reason}")
        st.stop()
    
    # Iterate over each file in the path
    summary = ""
    for file in response.json():
        if not isinstance(file, dict):
            st.warning(f"Unexpected file format: {file}")
            continue
        if file.get("type") == "file" and file.get("name").endswith((".txt", ".md", ".py", ".html", ".css", ".js")):
            # Get the content of the file and decode it from base64
            content = requests.get(file['download_url'], headers=headers).text

            # Limit the length of the code for summarization
            if len(content) > 20000:
                summary += f"{file['name']}: too long to summarize\n\n"
            else:
                # Call the OpenAI API to summarize the code
                result = openai.Completion.create(
                    engine="text-davinci-002",
                    prompt=f"Summarize this {file['name'].split('.')[-1]} code:\n\n{content}",
                    max_tokens=60,
                    n=1,
                    stop=None,
                    temperature=0.5,
                )

                # Add the name of the file and its summary to the final summary
                summary += f"{file['name']}:\n{result.choices[0].text}\n\n"
        
        elif file.get("type") == "dir":
            # Recursively process the subdirectory
            summary += process_files(f"{path}/{file['name']}")
    
    return summary

# Ask the user to enter the repository name
repo_name = st.text_input("Enter the name of the repository (e.g. UroojHaider99/casestudy_generator):")

# Process the files in the root directory of the repository
summary = process_files("")

# Display the summary of the code
st.write(summary)
