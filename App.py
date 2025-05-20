import streamlit as st
import requests
import json
import os
import pathlib
import configparser
from datetime import datetime

# Config setup - attempt to load API key from Streamlit secrets or environment variable
def load_api_key():
    # Try to get from Streamlit secrets (for Streamlit Cloud)
    try:
        return st.secrets["groq"]["api_key"]  # Fixed: Proper secrets structure
    except:
        pass
    
    # Try to get from environment variable
    api_key = os.environ.get("GROQ_API_KEY")
    if api_key:
        return api_key
        
    # If we're still here, check for a config file (local development)
    try:
        config = configparser.ConfigParser()
        config_path = pathlib.Path('config.ini')
        
        if config_path.exists():
            config.read(config_path)
            if 'GROQ' in config and 'API_KEY' in config['GROQ']:  # Fixed: Consistent naming
                return config['GROQ']['API_KEY']
    except Exception as e:
        st.error(f"Error reading config: {str(e)}")
        
    return None  # Fixed: Return None instead of empty string

# Initialize session state variables
def init_session_state():
    if 'content_history' not in st.session_state:
        st.session_state['content_history'] = []
    if 'delete_index' not in st.session_state:
        st.session_state['delete_index'] = None
    if 'api_key' not in st.session_state:
        st.session_state['api_key'] = load_api_key()

# Function to call Groq API with error handling
def call_groq_api(prompt, temperature, model, max_tokens):
    if not st.session_state.get('api_key'):
        st.error("Please enter your Groq API key in the sidebar and save it.")
        return None
    
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {st.session_state['api_key']}"
        }
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a professional content creator that specializes in creating high-quality, engaging content."},
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,  # Fixed: Use json parameter instead of data
            timeout=30  # Added timeout
        )
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {str(e)}")
        return None
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None

# Main app function
def main():
    st.set_page_config(
        page_title="Groq Content Generator",
        layout="wide",
        page_icon="🚀"
    )

    # Load custom CSS
    with open("style.css") as f:  # Moved CSS to external file
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
    # Initialize session state
    init_session_state()
    
    # App header
    st.markdown("""
    <div class="header-card">
        <h1>🚀 Groq Content Generator</h1>
        <p>Create high-quality content powered by Groq's cutting-edge AI models</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar configuration
    with st.sidebar:
        st.markdown('<div class="sidebar-header">Configuration</div>', unsafe_allow_html=True)
        
        # API Key input
        api_key_input = st.text_input(
            "**Groq API Key**",
            value=st.session_state.get('api_key', ''),
            type="password",
            help="For Streamlit Cloud deployment, set this in your secrets"
        )
        
        if api_key_input and api_key_input != st.session_state.get('api_key'):
            st.session_state['api_key'] = api_key_input
            st.success("API key updated!")
        
        # Model and content type selection
        model = st.selectbox(
            "**Select Model**",
            [
                "llama3-70b-8192",
                "mixtral-8x7b-32768",
                "gemma-7b-it"
            ],
            index=0  # Default to first option
        )
        
        content_type = st.selectbox(
            "**Content Type**",
            [
                "Blog Post",
                "Social Media Post",
                "Email Newsletter",
                "Product Description",
                "Marketing Copy",
                "Creative Story",
                "Technical Documentation",
                "Custom Prompt"
            ],
            index=0  # Default to first option
        )
        
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
    
    # Main content area
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        prompt = generate_prompt_form(content_type)
        
        if st.button("✨ Generate Content", type="primary", use_container_width=True):
            if not st.session_state.get('api_key'):
                st.error("Please enter your Groq API key first.")
            elif not prompt.strip():
                st.error("Please provide a valid prompt.")
            else:
                with st.spinner("Generating content..."):
                    response = call_groq_api(prompt, temperature, model, max_tokens)
                    if response:
                        st.session_state.update({
                            'current_response': response,
                            'current_prompt': prompt,
                            'generation_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'content_type': content_type
                        })
                        st.experimental_rerun()

    with col2:
        display_output_content()

    # Content history section
    if st.checkbox("📚 Show Content History"):
        display_content_history()

    # Footer
    st.markdown("""
    <div class="footer">
        <p>Built with ❤️ using Streamlit and powered by Groq API</p>
    </div>
    """, unsafe_allow_html=True)

# Helper function to generate prompt based on content type
def generate_prompt_form(content_type):
    with st.container():
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.subheader("📝 Content Parameters")
        
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
            
        # ... (other content type cases remain similar but should be similarly structured)
        
        else:  # Custom Prompt
            prompt = st.text_area("**Enter your custom prompt**", height=200, 
                                placeholder="Be specific about what content you want generated...")

        additional_instructions = st.text_area("**Additional Instructions** (optional)", 
                                            placeholder="Any other specifications or requirements...")
        
        if additional_instructions:
            prompt += f"\n\nAdditional instructions: {additional_instructions}"
        
        st.markdown('</div>', unsafe_allow_html=True)
        return prompt

# Helper function to display output content
def display_output_content():
    if 'current_response' in st.session_state:
        with st.container():
            st.markdown('<div class="output-container">', unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="output-header">
                <div>
                    <h3>📄 Generated Content</h3>
                    <span class="tag">{st.session_state.get('content_type', '')}</span>
                    <span style="color: var(--light-text); font-size: 0.9rem;">
                        {st.session_state.get('generation_time', '')}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(st.session_state['current_response'])
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Download options
            col_d1, col_d2 = st.columns([3, 1])
            with col_d1:
                output_format = st.selectbox("**Download Format**", ["TXT", "MD", "HTML", "JSON"])
            with col_d2:
                format_mappings = {
                    "TXT": {"ext": "txt", "mime": "text/plain"},
                    "MD": {"ext": "md", "mime": "text/markdown"},
                    "HTML": {"ext": "html", "mime": "text/html"},
                    "JSON": {"ext": "json", "mime": "application/json"}
                }
                
                download_content = st.session_state['current_response']
                if output_format == "JSON":
                    download_content = json.dumps({
                        "content": download_content,
                        "metadata": {
                            "content_type": st.session_state.get('content_type', ''),
                            "generation_time": st.session_state.get('generation_time', ''),
                            "model": "llama3-70b-8192"  # Default model
                        }
                    }, indent=2)
                
                st.download_button(
                    label="💾 Download",
                    data=download_content,
                    file_name=f"groq_content_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format_mappings[output_format]['ext']}",
                    mime=format_mappings[output_format]['mime'],
                    use_container_width=True,
                    key="download_btn"
                )
            
            if st.button("💾 Save to History", use_container_width=True):
                st.session_state['content_history'].append({
                    'type': st.session_state.get('content_type', ''),
                    'prompt': st.session_state.get('current_prompt', ''),
                    'response': st.session_state['current_response'],
                    'timestamp': st.session_state.get('generation_time', '')
                })
                st.success("Content saved to history")

# Helper function to display content history
def display_content_history():
    st.subheader("Content History")
    
    if not st.session_state['content_history']:
        st.info("No content history yet. Generate and save content to see it here.")
    else:
        for i, item in enumerate(reversed(st.session_state['content_history'])):
            with st.container():
                col_hist1, col_hist2 = st.columns([5, 1])
                
                with col_hist1:
                    st.markdown(f"**{item['type']}** - {item['timestamp']}")
                
                with col_hist2:
                    if st.button("🗑️ Delete", key=f"del_{i}"):
                        st.session_state['content_history'].pop(len(st.session_state['content_history']) - i - 1)
                        st.experimental_rerun()
                
                with st.expander("View Content"):
                    st.markdown(item['response'])
                
                st.markdown("---")

if __name__ == "__main__":
    main()
