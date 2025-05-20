# Grok-Content-Generator  🚀

* A powerful Streamlit application that leverages Groq's ultra-fast LLMs to generate high-quality content for various use cases.

## Features ✨

- **Multiple Content Types**: Generate blog posts, social media content, product descriptions, marketing copy, technical docs, and more
- **Model Selection**: Choose between Groq's fastest models (Llama3-70B, Mixtral, Gemma)
- **Customizable Outputs**: Control creativity, length, and tone of generated content
- **Content History**: Save and revisit previous generations
- **Export Options**: Download content in TXT, MD, HTML, or JSON formats
- **Responsive Design**: Works on desktop and mobile devices

## Installation 💻

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/groq-content-generator.git
   cd groq-content-generator

2. Create & activate virtual environment
   ```bash
      python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install Dependencies
   ```bash
   pip install -r requirements.txt
```

## Configuration ⚙️

1. Obtain your Groq API key from console.groq.com

2. Set up your API key using one of these methods:

* **Environment Variable:**
   ```bash
   export GROQ_API_KEY='your-api-key-here'
   ```

* Streamlit Secrets(for cloud deployment):
   Create .streamlit/secrets.toml with:
  ```bash
    [groq]
api_key = "your-api-key-here"
```






