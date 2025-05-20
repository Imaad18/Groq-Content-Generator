import streamlit as st
import requests
import json
import os
import pathlib
import configparser
from datetime import datetime
from functools import lru_cache

# Constants
MODELS = [
    "llama3-70b-8192",
    "mixtral-8x7b-32768",
    "gemma-7b-it"
]

CONTENT_TYPES = [
    "Blog Post",
    "Social Media Post",
    "Email Newsletter",
    "Product Description",
    "Marketing Copy",
    "Creative Story",
    "Technical Documentation",
    "Custom Prompt"
]

# Cache API key loading to avoid repeated checks
@lru_cache(maxsize=1)
def load_api_key():
    """Load API key from various sources with caching"""
    # Try Streamlit secrets first
    try:
        if "groq" in st.secrets and "api_key" in st.secrets["groq"]:
            return st.secrets["groq"]["api_key"]
    except Exception:
        pass
    
    # Try environment variable
    api_key = os.environ.get("GROQ_API_KEY")
    if api_key:
        return api_key
        
    # Try config file
    try:
        config = configparser.ConfigParser()
        config_path = pathlib.Path('config.ini')
        if config_path.exists():
            config.read(config_path)
            if config.has_section('GROQ') and 'API_KEY' in config['GROQ']:
                return config['GROQ']['API_KEY']
    except Exception:
        pass
        
    return None

def initialize_app():
    """Initialize the app configuration and session state"""
    st.set_page_config(
        page_title="Groq Content Generator",
        layout="wide",
        page_icon="🚀"
    )
    
    # Initialize session state
    if 'content_history' not in st.session_state:
        st.session_state.content_history = []
    if 'api_key' not in st.session_state:
        st.session_state.api_key = load_api_key()
    if 'current_response' not in st.session_state:
        st.session_state.current_response = None

def render_header():
    """Render the app header"""
    st.markdown("""
    <div class="header-card">
        <h1>🚀 Groq Content Generator</h1>
        <p>Create high-quality content powered by Groq's cutting-edge AI models</p>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Render the sidebar configuration"""
    with st.sidebar:
        st.markdown('<div class="sidebar-header">Configuration</div>', unsafe_allow_html=True)
        
        # API Key input
        api_key = st.text_input(
            "**Groq API Key**",
            value=st.session_state.get('api_key', ''),
            type="password",
            help="Get your API key from Groq's console"
        )
        
        if api_key and api_key != st.session_state.get('api_key'):
            st.session_state.api_key = api_key
            st.success("API key updated!")
        
        # Model selection
        model = st.selectbox("**Select Model**", MODELS, index=0)
        
        # Content type selection
        content_type = st.selectbox("**Content Type**", CONTENT_TYPES, index=0)
        
        # Advanced settings
        with st.expander("Advanced Settings"):
            temperature = st.slider(
                "**Creativity Level**", 
                0.0, 1.0, 0.7,
                help="Higher values make output more creative but less predictable"
            )
            
            max_tokens = st.slider(
                "**Max Tokens**", 
                100, 8192, 2048,
                help="Limit the length of the generated response"
            )
    
    return {
        'model': model,
        'content_type': content_type,
        'temperature': temperature,
        'max_tokens': max_tokens
    }

def generate_prompt(content_type):
    """Generate prompt based on content type"""
    prompt = ""
    
    if content_type == "Blog Post":
        topic = st.text_input("**Topic**", placeholder="E.g., Artificial Intelligence Trends")
        tone = st.selectbox("**Tone**", ["Informative", "Casual", "Professional", "Enthusiastic"])
        word_count = st.slider("**Approximate Word Count**", 300, 2000, 800)
        include_headers = st.checkbox("**Include Section Headers**", value=True)
        include_conclusion = st.checkbox("**Include Conclusion**", value=True)
        
        prompt = f"""Write a {tone.lower()} blog post about {topic}. 
        The post should be approximately {word_count} words.
        {"Include section headers to organize the content." if include_headers else ""}
        {"Include a conclusion section at the end." if include_conclusion else ""}
        Make it engaging, informative, and well-structured."""
        
    elif content_type == "Social Media Post":
        platform = st.selectbox("**Platform**", ["LinkedIn", "Twitter/X", "Instagram", "Facebook"])
        topic = st.text_input("**Topic**", placeholder="E.g., Product Launch")
        include_hashtags = st.checkbox("**Include Hashtags**", value=True)
        
        char_limits = {
            "Twitter/X": 280,
            "LinkedIn": 3000,
            "Instagram": 2200,
            "Facebook": 5000
        }
        
        post_length = st.slider("**Length (characters)**", 100, char_limits[platform], min(500, char_limits[platform]))
        
        prompt = f"""Create a compelling {platform} post about {topic}.
        Keep it under {post_length} characters.
        {"Include relevant hashtags." if include_hashtags else ""}
        Make it attention-grabbing and designed for maximum engagement."""
        
    elif content_type == "Email Newsletter":
        purpose = st.selectbox("**Purpose**", ["Promotional", "Informational", "Newsletter", "Announcement"])
        audience = st.text_input("**Target Audience**", placeholder="E.g., Tech Professionals")
        call_to_action = st.text_input("**Call to Action**", placeholder="E.g., Visit our website")
        
        prompt = f"""Write a {purpose.lower()} email newsletter targeting {audience}.
        Include a compelling subject line and body content.
        {"End with a clear call to action: " + call_to_action if call_to_action else ""}
        Make it professional yet engaging."""
    
    else:  # Custom Prompt
        prompt = st.text_area("**Enter your custom prompt**", height=200, 
                            placeholder="Be specific about what content you want generated...")
    
    additional_instructions = st.text_area("**Additional Instructions** (optional)", 
                                        placeholder="Any other specifications or requirements...")
    
    if additional_instructions:
        prompt += f"\n\nAdditional instructions: {additional_instructions}"
    
    return prompt

def call_groq_api(prompt, config):
    """Call Groq API with proper error handling"""
    if not st.session_state.api_key:
        st.error("Please enter your Groq API key in the sidebar and save it.")
        return None
    
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {st.session_state.api_key}"
        }
        
        payload = {
            "model": config['model'],
            "messages": [
                {
                    "role": "system", 
                    "content": "You are a professional content creator that specializes in creating high-quality, engaging content."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "temperature": config['temperature'],
            "max_tokens": config['max_tokens']
        }
        
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
        
    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {str(e)}")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
        return None

def render_content_output():
    """Render the content output section"""
    if not st.session_state.current_response:
        return
    
    with st.container():
        st.markdown("""
        <div class="output-container">
            <div class="output-header">
                <div>
                    <h3>📄 Generated Content</h3>
                    <span class="tag">%s</span>
                    <span style="color: var(--light-text); font-size: 0.9rem;">%s</span>
                </div>
            </div>
            %s
        </div>
        """ % (
            st.session_state.get('content_type', ''),
            st.session_state.get('generation_time', ''),
            st.session_state.current_response
        ), unsafe_allow_html=True)
        
        # Download options
        col1, col2 = st.columns([3, 1])
        with col1:
            output_format = st.selectbox("**Download Format**", ["TXT", "MD", "HTML", "JSON"])
        with col2:
            format_mappings = {
                "TXT": {"ext": "txt", "mime": "text/plain"},
                "MD": {"ext": "md", "mime": "text/markdown"},
                "HTML": {"ext": "html", "mime": "text/html"},
                "JSON": {"ext": "json", "mime": "application/json"}
            }
            
            download_content = st.session_state.current_response
            if output_format == "JSON":
                download_content = json.dumps({
                    "content": download_content,
                    "metadata": {
                        "content_type": st.session_state.get('content_type', ''),
                        "generation_time": st.session_state.get('generation_time', ''),
                        "model": st.session_state.get('model', 'llama3-70b-8192')
                    }
                }, indent=2)
            
            st.download_button(
                label="💾 Download",
                data=download_content,
                file_name=f"groq_content_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format_mappings[output_format]['ext']}",
                mime=format_mappings[output_format]['mime'],
                use_container_width=True
            )
        
        if st.button("💾 Save to History", use_container_width=True):
            st.session_state.content_history.append({
                'type': st.session_state.get('content_type', ''),
                'prompt': st.session_state.get('current_prompt', ''),
                'response': st.session_state.current_response,
                'timestamp': st.session_state.get('generation_time', '')
            })
            st.success("Content saved to history")

def render_content_history():
    """Render the content history section"""
    st.subheader("Content History")
    
    if not st.session_state.content_history:
        st.info("No content history yet. Generate and save content to see it here.")
        return
    
    for i, item in enumerate(reversed(st.session_state.content_history)):
        with st.container():
            col1, col2 = st.columns([5, 1])
            
            with col1:
                st.markdown(f"**{item['type']}** - {item['timestamp']}")
            
            with col2:
                if st.button("🗑️ Delete", key=f"del_{i}"):
                    del st.session_state.content_history[len(st.session_state.content_history) - i - 1]
                    st.experimental_rerun()
            
            with st.expander("View Content"):
                st.markdown(item['response'])
            
            st.markdown("---")

def main():
    """Main app function"""
    # Load CSS (inline for deployment simplicity)
    st.markdown("""
    <style>
    .header-card {
        background-color: #0e1117;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1.5rem;
    }
    .sidebar-header {
        font-size: 1.25rem;
        font-weight: bold;
        margin-bottom: 1rem;
        color: #ffffff;
    }
    .output-container {
        background-color: #0e1117;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1.5rem;
    }
    .output-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }
    .tag {
        background-color: #4a6fa5;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.8rem;
        margin-left: 0.5rem;
    }
    .footer {
        margin-top: 2rem;
        text-align: center;
        color: #6c757d;
        font-size: 0.9rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    initialize_app()
    render_header()
    
    # Get sidebar configuration
    config = render_sidebar()
    
    # Main content columns
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        with st.container():
            st.subheader("📝 Content Parameters")
            prompt = generate_prompt(config['content_type'])
            
            if st.button("✨ Generate Content", type="primary", use_container_width=True):
                if not st.session_state.api_key:
                    st.error("Please enter your Groq API key first.")
                elif not prompt.strip():
                    st.error("Please provide a valid prompt.")
                else:
                    with st.spinner("Generating content..."):
                        response = call_groq_api(prompt, config)
                        if response:
                            st.session_state.update({
                                'current_response': response,
                                'current_prompt': prompt,
                                'generation_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                'content_type': config['content_type'],
                                'model': config['model']
                            })
                            st.experimental_rerun()
    
    with col2:
        render_content_output()
    
    # Content history section
    if st.checkbox("📚 Show Content History"):
        render_content_history()
    
    # Footer
    st.markdown("""
    <div class="footer">
        <p>Built with ❤️ using Streamlit and powered by Groq API</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
