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
        return st.secrets["groq_api_key"]
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
            if 'API' in config and 'key' in config['API']:
                return config['API']['key']
    except:
        pass
        
    return ""

st.set_page_config(
    page_title="Groq Content Generator",
    layout="wide",
    page_icon="🚀"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    :root {
        --primary: #6e48aa;
        --secondary: #9d50bb;
        --accent: #4776E6;
        --background: #f8f9fa;
        --card-bg: #ffffff;
        --text: #333333;
        --light-text: #666666;
        --border: #e0e0e0;
        --success: #28a745;
        --warning: #ffc107;
        --danger: #dc3545;
    }
    
    .main {
        background-color: var(--background) !important;
    }
    
    .stApp {
        background-color: var(--background);
        color: var(--text);
    }
    
    .sidebar .sidebar-content {
        background-color: var(--card-bg) !important;
        border-right: 1px solid var(--border);
    }
    
    .stTextInput, .stSelectbox, .stTextArea, .stSlider, .stCheckbox {
        background-color: var(--card-bg) !important;
    }
    
    .stTextInput input, .stSelectbox select, .stTextArea textarea {
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        padding: 10px !important;
    }
    
    .stButton>button {
        background-color: var(--primary) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton>button:hover {
        background-color: var(--secondary) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(110, 72, 170, 0.2) !important;
    }
    
    .content-card {
        background-color: var(--card-bg);
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
        border: 1px solid var(--border);
        margin-bottom: 20px;
    }
    
    .header-card {
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        color: white;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(110, 72, 170, 0.2);
    }
    
    .header-card h1 {
        color: white !important;
        margin-bottom: 0;
    }
    
    .header-card p {
        color: rgba(255, 255, 255, 0.9) !important;
        margin-bottom: 0;
    }
    
    .sidebar-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: var(--primary);
        margin-bottom: 16px;
        padding-bottom: 8px;
        border-bottom: 2px solid var(--primary);
    }
    
    .sidebar-section {
        margin-bottom: 24px;
    }
    
    .output-container {
        background-color: var(--card-bg);
        border-radius: 12px;
        padding: 24px;
        border: 1px solid var(--border);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        height: 100%;
    }
    
    .output-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
        border-bottom: 1px solid var(--border);
        padding-bottom: 12px;
    }
    
    .history-item {
        background-color: var(--card-bg);
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
        border: 1px solid var(--border);
        transition: all 0.2s ease;
    }
    
    .history-item:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        transform: translateY(-2px);
    }
    
    .tag {
        display: inline-block;
        background-color: var(--primary);
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 500;
        margin-right: 8px;
    }
    
    .download-btn {
        background-color: var(--accent) !important;
    }
    
    .download-btn:hover {
        background-color: #3a62c4 !important;
    }
    
    .stMarkdown h2 {
        color: var(--primary) !important;
        border-bottom: 2px solid var(--primary);
        padding-bottom: 8px;
        margin-top: 24px;
    }
    
    .stMarkdown h3 {
        color: var(--secondary) !important;
    }
    
    .footer {
        text-align: center;
        padding: 16px;
        color: var(--light-text);
        font-size: 0.9rem;
        margin-top: 40px;
        border-top: 1px solid var(--border);
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .content-card {
            padding: 16px;
        }
        
        .header-card {
            padding: 16px;
        }
    }
</style>
""", unsafe_allow_html=True)

# Function to call Groq API
def call_groq_api(prompt, temperature, model, max_tokens):
    if not st.session_state.get('api_key'):
        return "Please enter your Groq API key in the sidebar and save it."
    
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
            data=json.dumps(payload)
        )  # Fixed: Added missing closing parenthesis
        
        if response.status_code == 200:
            response_json = response.json()
            return response_json["choices"][0]["message"]["content"]
        else:
            return f"Error: {response.status_code} - {response.text}"
            
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Load API key from various sources
api_key = load_api_key()

# Initialize session state for history
if 'content_history' not in st.session_state:
    st.session_state['content_history'] = []

if 'delete_index' not in st.session_state:
    st.session_state['delete_index'] = None

# App header with gradient background
st.markdown("""
<div class="header-card">
    <h1>🚀 Groq Content Generator</h1>
    <p>Create high-quality content powered by Groq's cutting-edge AI models</p>
</div>
""", unsafe_allow_html=True)

# Sidebar for API configuration
with st.sidebar:
    st.markdown('<div class="sidebar-header">Configuration</div>', unsafe_allow_html=True)
    
    # API Key input with secure handling (for local development)
    api_key_input = st.text_input("**Groq API Key**", 
                              value=api_key if api_key else "",
                              type="password",
                              help="For Streamlit Cloud deployment, set this in your secrets")
    
    # Use API key from input if provided
    if api_key_input:
        st.session_state['api_key'] = api_key_input
    # Otherwise use the one loaded from secrets/env/config
    elif api_key:
        st.session_state['api_key'] = api_key
    
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    
    # Model selection
    model = st.selectbox(
        "**Select Model**",
        [
            "llama3-70b-8192",
            "mixtral-8x7b-32768",
            "gemma-7b-it",
            "meta-llama/llama-4-scout-17b-16e-instruct",
            "meta-llama/llama-4-open-8b-base"
        ]
    )
    
    # Content type selection
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
        ]
    )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Advanced settings
    with st.expander("Advanced Settings"):
        temperature = st.slider("**Creativity Level**", 0.0, 1.0, 0.7, 
                              help="Higher values make output more creative but less predictable")
        
        max_tokens = st.slider("**Max Tokens**", 100, 8192, 2048,
                              help="Limit the length of the generated response")
        
        st.caption("Adjust these settings to fine-tune the AI's output behavior.")

# Main content area
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    with st.container():
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.subheader("📝 Content Parameters")
        
        # Dynamic form based on content type
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
            subject = st.text_input("**Newsletter Subject**", placeholder="E.g., Weekly Industry Updates")
            target_audience = st.text_input("**Target Audience**", placeholder="E.g., Marketing Professionals")
            sections = st.multiselect("**Include Sections**", 
                                     ["Introduction", "Main Content", "News Roundup", "Tips & Tricks", "Featured Product", "Call to Action"])
            
            prompt = f"""Write an email newsletter with the subject: "{subject}" 
            targeting {target_audience}.
            Include the following sections: {', '.join(sections)}
            Make it professional, engaging, and valuable to the audience."""
            
        elif content_type == "Product Description":
            product_name = st.text_input("**Product Name**", placeholder="E.g., EcoFriendly Water Bottle")
            product_type = st.text_input("**Product Type**", placeholder="E.g., Reusable Water Bottle")
            features = st.text_area("**Key Features** (one per line)", placeholder="Insulated\nBPA-free\n24-hour cold retention")
            target_market = st.text_input("**Target Market**", placeholder="E.g., Outdoor enthusiasts")
            
            prompt = f"""Create a compelling product description for {product_name}, which is a {product_type}.
            Key features include:
            {features}
            
            Target market: {target_market}
            
            The description should highlight benefits, unique selling points, and appeal to the target audience."""
            
        elif content_type == "Marketing Copy":
            campaign_purpose = st.selectbox("**Campaign Purpose**", 
                                          ["Product Launch", "Promotional Offer", "Brand Awareness", "Event Promotion"])
            product_service = st.text_input("**Product/Service Name**", placeholder="E.g., CloudSync Pro")
            key_benefits = st.text_area("**Key Benefits** (one per line)", placeholder="Automatic backup\nReal-time syncing\nSecure encryption")
            call_to_action = st.text_input("**Call to Action**", placeholder="E.g., Sign up for a free trial today")
            
            prompt = f"""Create marketing copy for a {campaign_purpose.lower()} campaign for {product_service}.
            Highlight these key benefits:
            {key_benefits}
            
            Include this call to action: {call_to_action}
            
            Make it persuasive, compelling, and focused on customer benefits."""
            
        elif content_type == "Creative Story":
            genre = st.selectbox("**Genre**", ["Science Fiction", "Fantasy", "Mystery", "Romance", "Horror", "Adventure"])
            setting = st.text_input("**Setting**", placeholder="E.g., Underwater civilization in year 3000")
            characters = st.text_area("**Main Characters** (one per line)", placeholder="Dr. Eliza Chen - Marine Biologist\nKorm - Amphibious alien")
            plot_elements = st.text_area("**Key Plot Elements** (one per line)", placeholder="Discovery of ancient technology\nThreat from surface world")
            
            prompt = f"""Write a short {genre.lower()} story with the following elements:
            
            Setting: {setting}
            
            Characters:
            {characters}
            
            Key plot elements:
            {plot_elements}
            
            Make it creative, engaging, and well-structured with a clear beginning, middle, and end."""
            
        elif content_type == "Technical Documentation":
            subject = st.text_input("**Subject/Product**", placeholder="E.g., API Integration")
            doc_type = st.selectbox("**Documentation Type**", ["User Guide", "API Reference", "Tutorial", "Troubleshooting Guide"])
            technical_level = st.selectbox("**Technical Level**", ["Beginner", "Intermediate", "Advanced"])
            include_code = st.checkbox("**Include Code Examples**", value=True)
            
            prompt = f"""Create a {technical_level.lower()}-level {doc_type.lower()} for {subject}.
            
            {"Include relevant code examples." if include_code else ""}
            
            Make it clear, concise, and easy to follow. Use proper technical writing conventions."""
            
        else:  # Custom Prompt
            prompt = st.text_area("**Enter your custom prompt**", height=200, 
                                placeholder="Be specific about what content you want generated...")

        # Add any additional parameters
        additional_instructions = st.text_area("**Additional Instructions** (optional)", 
                                            placeholder="Any other specifications or requirements...")
        
        if additional_instructions:
            prompt += f"\n\nAdditional instructions: {additional_instructions}"
        
        st.markdown('</div>', unsafe_allow_html=True)  # Close content-card
        
        # Generate button with improved styling
        if st.button("✨ Generate Content", type="primary", use_container_width=True):
            with st.spinner("Generating content..."):
                if 'api_key' not in st.session_state:
                    st.error("Please enter your Groq API key first and save it.")
                else:
                    # Store the prompt for reference
                    st.session_state['current_prompt'] = prompt
                    
                    # Call API and get response
                    response = call_groq_api(prompt, temperature, model, max_tokens)
                    
                    # Store the response
                    st.session_state['current_response'] = response
                    st.session_state['generation_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    st.session_state['content_type'] = content_type
                    st.experimental_rerun()

# Display the output in the second column
with col2:
    if 'current_response' in st.session_state:
        with st.container():
            st.markdown('<div class="output-container">', unsafe_allow_html=True)
            
            # Output header with timestamp and type
            st.markdown(f"""
            <div class="output-header">
                <div>
                    <h3>📄 Generated Content</h3>
                    <span class="tag">{st.session_state.get('content_type', '')}</span>
                    <span style="color: var(--light-text); font-size: 0.9rem;">{st.session_state.get('generation_time', '')}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # The generated content
            st.markdown(st.session_state['current_response'])
            
            st.markdown('</div>', unsafe_allow_html=True)  # Close output-container
            
            # Download options
            col_d1, col_d2 = st.columns([3, 1])
            with col_d1:
                output_format = st.selectbox("**Download Format**", ["TXT", "MD", "HTML", "JSON"])
            with col_d2:
                download_disabled = 'current_response' not in st.session_state
                
                # Fix: Properly set file extension and MIME type based on selected format
                format_mappings = {
                    "TXT": {"ext": "txt", "mime": "text/plain"},
                    "MD": {"ext": "md", "mime": "text/markdown"},
                    "HTML": {"ext": "html", "mime": "text/html"},
                    "JSON": {"ext": "json", "mime": "application/json"}
                }
                
                # For JSON format, wrap content in a JSON structure
                download_content = st.session_state['current_response']
                if output_format == "JSON":
                    download_content = json.dumps({
                        "content": st.session_state['current_response'],
                        "metadata": {
                            "content_type": st.session_state.get('content_type', ''),
                            "generation_time": st.session_state.get('generation_time', ''),
                            "model": model
                        }
                    }, indent=2)
                
                st.download_button(
                    label="💾 Download",
                    data=download_content,
                    file_name=f"groq_{st.session_state.get('content_type', 'content').replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d')}.{format_mappings[output_format]['ext']}",
                    mime=format_mappings[output_format]['mime'],
                    use_container_width=True,
                    key="download_btn",
                    disabled=download_disabled
                )
            
            # History management
            if st.button("💾 Save to History", use_container_width=True):
                if 'content_history' not in st.session_state:
                    st.session_state['content_history'] = []
                
                st.session_state['content_history'].append({
                    'type': st.session_state.get('content_type', ''),
                    'prompt': st.session_state.get('current_prompt', ''),
                    'response': st.session_state['current_response'],
                    'timestamp': st.session_state.get('generation_time', '')
                })
                
                st.success("Content saved to history")

# Content history section
if st.checkbox("📚 Show Content History", key="show_history"):
    st.subheader("Content History")
    
    if 'content_history' not in st.session_state or len(st.session_state['content_history']) == 0:
        st.info("No content history yet. Generate and save content to see it here.")
    else:
        # Reverse to show newest first
        for i, item in enumerate(reversed(st.session_state['content_history'])):
            with st.container():
                col_hist1, col_hist2 = st.columns([5, 1])
                
                with col_hist1:
                    st.markdown(f"**{item['type']}** - {item['timestamp']}")
                
                with col_hist2:
                    # Fixed: Using Streamlit's built-in functionality for deletion instead of JavaScript
                    if st.button("🗑️ Delete", key=f"del_{i}"):
                        st.session_state['delete_index'] = len(st.session_state['content_history']) - i - 1
                        st.experimental_rerun()
                
                with st.expander("View Content"):
                    st.markdown(item['response'])
                
                st.markdown("---")
        
        # Handle deletion if triggered
        if st.session_state['delete_index'] is not None:
            st.session_state['content_history'].pop(st.session_state['delete_index'])
            st.session_state['delete_index'] = None
            st.experimental_rerun()

# Footer
st.markdown("""
<div class="footer">
    <p>Built with ❤️ using Streamlit and powered by Groq API</p>
</div>
""", unsafe_allow_html=True)
