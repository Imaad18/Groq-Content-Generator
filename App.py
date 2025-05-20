import streamlit as st

st.set_page_config(
    page_title="Groq Content Generator",
    layout="wide",
    page_icon="🚀"
)

# Imports
import requests
import json
import os
import pathlib
import configparser
import time
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


def initialize_app():
    """Initialize the app configuration and session state"""
    # Initialize session state
    if 'content_history' not in st.session_state:
        st.session_state.content_history = []
    if 'api_key' not in st.session_state:
        st.session_state.api_key = load_api_key()
    if 'current_response' not in st.session_state:
        st.session_state.current_response = None
    if 'generation_in_progress' not in st.session_state:
        st.session_state.generation_in_progress = False
    if 'last_activity_time' not in st.session_state:
        st.session_state.last_activity_time = time.time()
    
    # Update last activity time
    st.session_state.last_activity_time = time.time()


# Load API key from various sources
def load_api_key():
    """Load API key from various sources"""
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
            
            system_prompt = st.text_area(
                "**System Prompt**",
                value="You are a professional content creator that specializes in creating high-quality, engaging content.",
                help="Customize the system prompt to guide the AI's behavior"
            )
    
    return {
        'model': model,
        'content_type': content_type,
        'temperature': temperature,
        'max_tokens': max_tokens,
        'system_prompt': system_prompt
    }

def generate_product_description_prompt():
    """Generate prompt for product description content type"""
    product_name = st.text_input("**Product Name**", placeholder="E.g., Wireless Earbuds")
    target_audience = st.text_input("**Target Audience**", placeholder="E.g., Active professionals")
    key_features = st.text_area("**Key Features**", placeholder="List the main features, one per line")
    tone = st.selectbox("**Tone**", ["Professional", "Exciting", "Friendly", "Luxurious", "Technical"])
    word_limit = st.slider("**Word Count**", 100, 500, 200)
    
    prompt = f"""Write a compelling product description for {product_name}, targeting {target_audience}.
    Key features to highlight:
    {key_features}
    
    Use a {tone.lower()} tone and keep it approximately {word_limit} words.
    The description should be persuasive and highlight the unique selling points."""
    
    return prompt

def generate_marketing_copy_prompt():
    """Generate prompt for marketing copy content type"""
    campaign_type = st.selectbox("**Campaign Type**", ["Ad Copy", "Landing Page", "Brochure", "Sales Email"])
    product_service = st.text_input("**Product/Service**", placeholder="E.g., Fitness App Subscription")
    unique_selling_point = st.text_input("**Unique Selling Point**", placeholder="E.g., AI-powered personalized workouts")
    tone = st.selectbox("**Tone**", ["Persuasive", "Urgent", "Friendly", "Authoritative", "Inspirational"])
    
    prompt = f"""Create {campaign_type} marketing copy for {product_service}.
    Unique selling point: {unique_selling_point}
    
    Use a {tone.lower()} tone that engages the reader and drives action.
    Make it compelling, concise, and focused on benefits rather than just features."""
    
    return prompt

def generate_creative_story_prompt():
    """Generate prompt for creative story content type"""
    genre = st.selectbox("**Genre**", ["Science Fiction", "Fantasy", "Mystery", "Romance", "Horror", "Adventure"])
    main_character = st.text_input("**Main Character**", placeholder="E.g., A time-traveling archaeologist")
    setting = st.text_input("**Setting**", placeholder="E.g., Ancient Egypt during construction of pyramids")
    theme = st.text_input("**Theme/Conflict**", placeholder="E.g., Moral dilemma of changing the past")
    story_length = st.slider("**Approximate Word Count**", 300, 2000, 800)
    
    prompt = f"""Write a {genre.lower()} short story with the following elements:
    - Main character: {main_character}
    - Setting: {setting}
    - Theme/Conflict: {theme}
    
    The story should be approximately {story_length} words, with a clear beginning, middle, and end.
    Make it engaging with descriptive language and compelling dialogue."""
    
    return prompt

def generate_technical_doc_prompt():
    """Generate prompt for technical documentation content type"""
    doc_type = st.selectbox("**Documentation Type**", ["User Guide", "API Documentation", "Tutorial", "Reference Manual"])
    subject = st.text_input("**Subject/Product**", placeholder="E.g., Cloud Database Service")
    audience = st.selectbox("**Technical Level**", ["Beginner", "Intermediate", "Advanced", "Expert"])
    key_sections = st.text_area("**Key Sections to Include**", placeholder="E.g., Installation, Configuration, Troubleshooting")
    
    prompt = f"""Create {doc_type} for {subject} aimed at {audience.lower()}-level users.
    Include the following sections:
    {key_sections}
    
    The documentation should be clear, concise, and follow best practices for technical writing.
    Use appropriate formatting, headings, and include examples where relevant."""
    
    return prompt

def generate_blog_post_prompt():
    """Generate prompt for blog post content type"""
    topic = st.text_input("**Topic**", placeholder="E.g., Artificial Intelligence Trends")
    tone = st.selectbox("**Tone**", ["Informative", "Casual", "Professional", "Enthusiastic"])
    word_count = st.slider("**Approximate Word Count**", 300, 2000, 800)
    include_headers = st.checkbox("**Include Section Headers**", value=True)
    include_conclusion = st.checkbox("**Include Conclusion**", value=True)
    target_audience = st.text_input("**Target Audience**", placeholder="E.g., Tech professionals, General readers")
    
    prompt = f"""Write a {tone.lower()} blog post about {topic} targeting {target_audience}. 
    The post should be approximately {word_count} words.
    {"Include section headers to organize the content." if include_headers else ""}
    {"Include a conclusion section at the end." if include_conclusion else ""}
    Make it engaging, informative, and well-structured.
    
    Add relevant statistics or examples to support key points when appropriate.
    The post should provide value to readers and maintain their interest throughout."""
        
    return prompt

def generate_social_media_prompt():
    """Generate prompt for social media post content type"""
    platform = st.selectbox("**Platform**", ["LinkedIn", "Twitter/X", "Instagram", "Facebook"])
    topic = st.text_input("**Topic**", placeholder="E.g., Product Launch")
    include_hashtags = st.checkbox("**Include Hashtags**", value=True)
    include_cta = st.checkbox("**Include Call to Action**", value=True)
    cta_type = ""
    if include_cta:
        cta_type = st.selectbox("**Call to Action Type**", ["Visit website", "Sign up", "Follow", "Comment", "Share", "Custom"])
        if cta_type == "Custom":
            cta_type = st.text_input("**Custom CTA**", placeholder="E.g., Download our free guide")
    
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
    {"Include a clear call to action to " + cta_type + "." if include_cta else ""}
    Make it attention-grabbing and designed for maximum engagement.
    
    The tone should match {platform}'s typical successful posts and resonate with the platform's audience."""
        
    return prompt

def generate_email_newsletter_prompt():
    """Generate prompt for email newsletter content type"""
    purpose = st.selectbox("**Purpose**", ["Promotional", "Informational", "Newsletter", "Announcement"])
    audience = st.text_input("**Target Audience**", placeholder="E.g., Tech Professionals")
    subject_line = st.text_input("**Subject Line Guidance**", placeholder="E.g., Holiday offer, Monthly update")
    call_to_action = st.text_input("**Call to Action**", placeholder="E.g., Visit our website")
    include_sections = st.multiselect(
        "**Sections to Include**",
        ["Introduction", "Main Content", "Featured Product/Service", "Testimonials", "Upcoming Events", "Conclusion"],
        default=["Introduction", "Main Content", "Conclusion"]
    )
    
    prompt = f"""Write a {purpose.lower()} email newsletter targeting {audience}.
    Include a compelling subject line related to: {subject_line}
    
    Structure to include:
    {', '.join(include_sections)}
    
    {"End with a clear call to action: " + call_to_action if call_to_action else ""}
    
    Make it professional yet engaging, with a tone appropriate for {audience}.
    The email should be scannable with clear sections and a professional layout."""
    
    return prompt

def generate_prompt(content_type):
    """Generate prompt based on content type"""
    prompt = ""
    
    content_generators = {
        "Blog Post": generate_blog_post_prompt,
        "Social Media Post": generate_social_media_prompt,
        "Email Newsletter": generate_email_newsletter_prompt,
        "Product Description": generate_product_description_prompt,
        "Marketing Copy": generate_marketing_copy_prompt,
        "Creative Story": generate_creative_story_prompt,
        "Technical Documentation": generate_technical_doc_prompt
    }
    
    if content_type in content_generators:
        prompt = content_generators[content_type]()
    else:  # Custom Prompt
        prompt = st.text_area("**Enter your custom prompt**", height=200, 
                            placeholder="Be specific about what content you want generated...")
    
    additional_instructions = st.text_area("**Additional Instructions** (optional)", 
                                        placeholder="Any other specifications or requirements...")
    
    if additional_instructions:
        prompt += f"\n\nAdditional instructions: {additional_instructions}"
    
    return prompt

def validate_api_key(api_key):
    """Validate if the API key is provided"""
    if not api_key or api_key.strip() == "":
        st.error("Please enter your Groq API key in the sidebar.")
        return False
    return True

def call_groq_api(prompt, config):
    """Call Groq API with proper error handling"""
    if not validate_api_key(st.session_state.api_key):
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
                    "content": config['system_prompt']
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "temperature": config['temperature'],
            "max_tokens": config['max_tokens']
        }
        
        # Add a progress bar for the API call
        progress_bar = st.progress(0)
        for i in range(100):
            # Simulating progress while waiting for API response
            progress_bar.progress(i + 1)
            if i < 70:  # Slow down initial progress to reflect API call time
                time.sleep(0.01)
            else:
                time.sleep(0.003)
                
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        progress_bar.empty()
        
        # Check for HTTP errors first
        response.raise_for_status()
        
        # Parse the response
        response_json = response.json()
        
        # Validate response structure
        if "choices" not in response_json or len(response_json["choices"]) == 0:
            st.error("Received invalid response format from Groq API")
            return None
            
        if "message" not in response_json["choices"][0] or "content" not in response_json["choices"][0]["message"]:
            st.error("Response missing required content field")
            return None
            
        return response_json["choices"][0]["message"]["content"]
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            st.error("Authentication error: Invalid API key")
        elif e.response.status_code == 429:
            st.error("Rate limit exceeded. Please try again later.")
        elif e.response.status_code >= 500:
            st.error("Groq server error. Please try again later.")
        else:
            st.error(f"HTTP error: {e}")
        return None
    except requests.exceptions.ConnectionError:
        st.error("Connection error: Could not connect to Groq API")
        return None
    except requests.exceptions.Timeout:
        st.error("Request timed out. The Groq API is taking too long to respond.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {str(e)}")
        return None
    except ValueError as e:
        st.error(f"Invalid response from API (JSON parsing error): {str(e)}")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
        return None

def render_content_output():
    """Render the content output section"""
    if not st.session_state.current_response:
        return
    
    with st.container():
        # Create tabs for different viewing options
        tab1, tab2 = st.tabs(["Formatted", "Raw"])
        
        with tab1:
            # Show formatted content with proper markdown rendering
            st.markdown(f"""
            ### 📄 Generated Content
            <span class="tag">{st.session_state.get('content_type', '')}</span>
            <span style="color: var(--light-text); font-size: 0.9rem;">{st.session_state.get('generation_time', '')}</span>
            """, unsafe_allow_html=True)
            
            st.markdown(st.session_state.current_response)
            
        with tab2:
            # Show raw text content
            st.markdown(f"""
            ### 📄 Raw Content
            <span class="tag">{st.session_state.get('content_type', '')}</span>
            <span style="color: var(--light-text); font-size: 0.9rem;">{st.session_state.get('generation_time', '')}</span>
            """, unsafe_allow_html=True)
            
            st.code(st.session_state.current_response, language="text")
        
        # Download options
        col1, col2, col3 = st.columns([3, 1, 1])
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
            elif output_format == "HTML":
                download_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Generated Content - {st.session_state.get('content_type', '')}</title>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1, h2, h3 {{ color: #333; }}
        .metadata {{ color: #666; font-size: 0.9em; margin-bottom: 20px; }}
        .content {{ background-color: #f9f9f9; padding: 20px; border-radius: 5px; }}
    </style>
</head>
<body>
    <h1>Generated Content</h1>
    <div class="metadata">
        <p><strong>Content Type:</strong> {st.session_state.get('content_type', '')}</p>
        <p><strong>Generation Time:</strong> {st.session_state.get('generation_time', '')}</p>
        <p><strong>Model:</strong> {st.session_state.get('model', 'llama3-70b-8192')}</p>
    </div>
    <div class="content">
        {st.session_state.current_response.replace('\n', '<br>')}
    </div>
</body>
</html>"""
            
            st.download_button(
                label="💾 Download",
                data=download_content,
                file_name=f"groq_content_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format_mappings[output_format]['ext']}",
                mime=format_mappings[output_format]['mime'],
                use_container_width=True
            )
        
        with col3:
            # Copy to clipboard button (using JavaScript)
            st.markdown(
                """
                <button 
                    onclick="navigator.clipboard.writeText(document.getElementById('content-to-copy').innerText); alert('Content copied to clipboard!');"
                    style="width: 100%; padding: 0.375rem 0.75rem; color: white; background-color: #4a6fa5; border: none; border-radius: 0.25rem; cursor: pointer;">
                    📋 Copy to Clipboard
                </button>
                <div id="content-to-copy" style="display:none;"></div>
                <script>
                    document.getElementById('content-to-copy').innerText = `""" + st.session_state.current_response.replace("`", "\\`").replace("$", "\\$") + """`;
                </script>
                """, 
                unsafe_allow_html=True
            )
        
        if st.button("💾 Save to History", use_container_width=True):
            # Create a unique ID for this content
            content_id = f"content_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            st.session_state.content_history.append({
                'id': content_id,
                'type': st.session_state.get('content_type', ''),
                'prompt': st.session_state.get('current_prompt', ''),
                'response': st.session_state.current_response,
                'timestamp': st.session_state.get('generation_time', ''),
                'model': st.session_state.get('model', '')
            })
            st.success("Content saved to history")

def render_content_history():
    """Render the content history section"""
    st.subheader("Content History")
    
    if not st.session_state.content_history:
        st.info("No content history yet. Generate and save content to see it here.")
        return
    
    # Add search functionality
    search_term = st.text_input("🔍 Search history", placeholder="Search by content type, text, or date...")
    
    # Filter content history based on search term
    filtered_history = st.session_state.content_history
    if search_term:
        filtered_history = [
            item for item in st.session_state.content_history 
            if search_term.lower() in item['type'].lower() or 
               search_term.lower() in item['response'].lower() or 
               search_term.lower() in item['timestamp'].lower()
        ]
    
    # Add functionality to clear all history
    col1, col2 = st.columns([5, 1])
    with col2:
        if st.button("🗑️ Clear All", use_container_width=True):
            st.session_state.content_history = []
            st.experimental_rerun()
    
    # Display history items
    for i, item in enumerate(reversed(filtered_history)):
        with st.container():
            col1, col2, col3 = st.columns([4, 1, 1])
            
            with col1:
                st.markdown(f"**{item['type']}** - {item['timestamp']}")
            
            with col2:
                if st.button("📋 Use Again", key=f"reuse_{i}"):
                    # Pre-populate the content generation form with this item's settings
                    st.session_state.update({
                        'content_type': item['type'],
                        'current_prompt': item['prompt']
                    })
                    st.experimental_rerun()
            
            with col3:
                if st.button("🗑️ Delete", key=f"del_{i}"):
                    # Find the item by ID to avoid index issues with filtered list
                    for idx, hist_item in enumerate(st.session_state.content_history):
                        if hist_item.get('id', '') == item.get('id', ''):
                            del st.session_state.content_history[idx]
                            break
                    st.experimental_rerun()
            
            with st.expander("View Content"):
                st.markdown(f"**Model:** {item.get('model', 'Unknown')}")
                st.markdown("**Prompt:**")
                st.markdown(f"```\n{item['prompt']}\n```")
                st.markdown("**Generated Content:**")
                st.markdown(item['response'])
            
            st.markdown("---")

def check_session_timeout():
    """Check if session has timed out (30 minutes of inactivity)"""
    timeout_minutes = 30
    current_time = time.time()
    last_activity = st.session_state.get('last_activity_time', current_time)
    
    if current_time - last_activity > (timeout_minutes * 60):
        # Reset session state
        for key in list(st.session_state.keys()):
            if key != 'api_key':  # Keep the API key
                del st.session_state[key]
        
        st.session_state.last_activity_time = current_time
        st.warning(f"Your session was reset due to {timeout_minutes} minutes of inactivity.")
        return True
    
    return False

def generate_content(prompt, config):
    """Generate content with proper state management"""
    if not prompt.strip():
        st.error("Please provide a valid prompt.")
        return
    
    if not validate_api_key(st.session_state.api_key):
        return
    
    try:
        # Set flag to prevent multiple generations
        st.session_state.generation_in_progress = True
        
        with st.spinner("Generating content..."):
            response = call_groq_api(prompt, config)
            
            if response:
                # Update session state with the new response
                st.session_state.update({
                    'current_response': response,
                    'current_prompt': prompt,
                    'generation_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'content_type': config['content_type'],
                    'model': config['model']
                })
    finally:
        # Reset flag regardless of outcome
        st.session_state.generation_in_progress = False

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
    /* Improved form layout */
    .stTextInput, .stTextArea, .stSelectbox {
        margin-bottom: 1rem;
    }
    /* Make buttons more consistent */
    .stButton button {
        width: 100%;
    }
    /* Improve tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 16px;
        border-radius: 4px 4px 0 0;
    }
    /* Add animations */
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    .stMarkdown, .output-container {
        animation: fadeIn 0.5s ease-in-out;
    }
    </style>
    """, unsafe_allow_html=True)
    
    initialize_app()
    
    # Check for session timeout
    if check_session_timeout():
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
            
            # Prevent multiple submissions while generating
                        # Prevent multiple submissions while generating
            generate_button = st.button(
                "✨ Generate Content",
                disabled=st.session_state.get('generation_in_progress', False),
                type="primary",
                use_container_width=True
            )
            
            if generate_button:
                generate_content(prompt, config)
    
    with col2:
        render_content_output()
    
    # Content history section (full width below)
    render_content_history()
    
    # Footer
    st.markdown("""
    <div class="footer">
        <p>Powered by Groq API • Generated content may require review before use</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
