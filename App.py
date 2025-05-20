import streamlit as st
import requests
import json
import os
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
        import configparser
        import pathlib
        
        config = configparser.ConfigParser()
        config_path = pathlib.Path('config.ini')
        
        if config_path.exists():
            config.read(config_path)
            if 'API' in config and 'key' in config['API']:
                return config['API']['key']
    except:
        pass
        
    return ""

st.set_page_config(page_title="Groq Content Generator", layout="wide")

# Style and UI configuration
st.markdown("""
<style>
    .main {
        background-color: #f5f7f9;
    }
    .stTextInput, .stSelectbox, .stTextArea {
        background-color: white;
    }
    .content-output {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

# App title and description
st.title("🤖 Groq Content Generator")
st.markdown("Generate various types of content using the Groq API")

# Sidebar for API configuration
with st.sidebar:
    st.header("API Configuration")
    
    # Load API key from various sources
    api_key = load_api_key()
    
    # API Key input with secure handling (for local development)
    api_key_input = st.text_input("Enter your Groq API Key", 
                              value=api_key if api_key else "",
                              type="password",
                              help="For Streamlit Cloud deployment, set this in your secrets")
    
    # Model selection
    model = st.selectbox(
        "Select Model",
        [
            "meta-llama/llama-4-scout-17b-16e-instruct",
            "meta-llama/llama-4-open-8b-base",
            "llama3-70b-8192",
            "mixtral-8x7b-32768",
            "gemma-7b-it"
        ]
    )
    
    # Use API key from input if provided
    if api_key_input:
        st.session_state['api_key'] = api_key_input
    # Otherwise use the one loaded from secrets/env/config
    elif api_key:
        st.session_state['api_key'] = api_key
    
    st.markdown("---")
    
    # Content type selection
    content_type = st.selectbox(
        "Select Content Type",
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

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Input Parameters")
    
    # Dynamic form based on content type
    if content_type == "Blog Post":
        topic = st.text_input("Topic", placeholder="E.g., Artificial Intelligence Trends")
        tone = st.selectbox("Tone", ["Informative", "Casual", "Professional", "Enthusiastic"])
        word_count = st.slider("Approximate Word Count", 300, 2000, 800)
        include_headers = st.checkbox("Include Section Headers", value=True)
        include_conclusion = st.checkbox("Include Conclusion", value=True)
        
        prompt = f"""Write a {tone.lower()} blog post about {topic}. 
        The post should be approximately {word_count} words.
        {"Include section headers to organize the content." if include_headers else ""}
        {"Include a conclusion section at the end." if include_conclusion else ""}
        Make it engaging, informative, and well-structured."""
        
    elif content_type == "Social Media Post":
        platform = st.selectbox("Platform", ["LinkedIn", "Twitter/X", "Instagram", "Facebook"])
        topic = st.text_input("Topic", placeholder="E.g., Product Launch")
        include_hashtags = st.checkbox("Include Hashtags", value=True)
        
        char_limits = {
            "Twitter/X": 280,
            "LinkedIn": 3000,
            "Instagram": 2200,
            "Facebook": 5000
        }
        
        post_length = st.slider("Length (characters)", 100, char_limits[platform], min(500, char_limits[platform]))
        
        prompt = f"""Create a compelling {platform} post about {topic}.
        Keep it under {post_length} characters.
        {"Include relevant hashtags." if include_hashtags else ""}
        Make it attention-grabbing and designed for maximum engagement."""
        
    elif content_type == "Email Newsletter":
        subject = st.text_input("Newsletter Subject", placeholder="E.g., Weekly Industry Updates")
        target_audience = st.text_input("Target Audience", placeholder="E.g., Marketing Professionals")
        sections = st.multiselect("Include Sections", 
                                 ["Introduction", "Main Content", "News Roundup", "Tips & Tricks", "Featured Product", "Call to Action"])
        
        prompt = f"""Write an email newsletter with the subject: "{subject}" 
        targeting {target_audience}.
        Include the following sections: {', '.join(sections)}
        Make it professional, engaging, and valuable to the audience."""
        
    elif content_type == "Product Description":
        product_name = st.text_input("Product Name", placeholder="E.g., EcoFriendly Water Bottle")
        product_type = st.text_input("Product Type", placeholder="E.g., Reusable Water Bottle")
        features = st.text_area("Key Features (one per line)", placeholder="Insulated\nBPA-free\n24-hour cold retention")
        target_market = st.text_input("Target Market", placeholder="E.g., Outdoor enthusiasts")
        
        prompt = f"""Create a compelling product description for {product_name}, which is a {product_type}.
        Key features include:
        {features}
        
        Target market: {target_market}
        
        The description should highlight benefits, unique selling points, and appeal to the target audience."""
        
    elif content_type == "Marketing Copy":
        campaign_purpose = st.selectbox("Campaign Purpose", 
                                      ["Product Launch", "Promotional Offer", "Brand Awareness", "Event Promotion"])
        product_service = st.text_input("Product/Service Name", placeholder="E.g., CloudSync Pro")
        key_benefits = st.text_area("Key Benefits (one per line)", placeholder="Automatic backup\nReal-time syncing\nSecure encryption")
        call_to_action = st.text_input("Call to Action", placeholder="E.g., Sign up for a free trial today")
        
        prompt = f"""Create marketing copy for a {campaign_purpose.lower()} campaign for {product_service}.
        Highlight these key benefits:
        {key_benefits}
        
        Include this call to action: {call_to_action}
        
        Make it persuasive, compelling, and focused on customer benefits."""
        
    elif content_type == "Creative Story":
        genre = st.selectbox("Genre", ["Science Fiction", "Fantasy", "Mystery", "Romance", "Horror", "Adventure"])
        setting = st.text_input("Setting", placeholder="E.g., Underwater civilization in year 3000")
        characters = st.text_area("Main Characters (one per line)", placeholder="Dr. Eliza Chen - Marine Biologist\nKorm - Amphibious alien")
        plot_elements = st.text_area("Key Plot Elements (one per line)", placeholder="Discovery of ancient technology\nThreat from surface world")
        
        prompt = f"""Write a short {genre.lower()} story with the following elements:
        
        Setting: {setting}
        
        Characters:
        {characters}
        
        Key plot elements:
        {plot_elements}
        
        Make it creative, engaging, and well-structured with a clear beginning, middle, and end."""
        
    elif content_type == "Technical Documentation":
        subject = st.text_input("Subject/Product", placeholder="E.g., API Integration")
        doc_type = st.selectbox("Documentation Type", ["User Guide", "API Reference", "Tutorial", "Troubleshooting Guide"])
        technical_level = st.selectbox("Technical Level", ["Beginner", "Intermediate", "Advanced"])
        include_code = st.checkbox("Include Code Examples", value=True)
        
        prompt = f"""Create a {technical_level.lower()}-level {doc_type.lower()} for {subject}.
        
        {"Include relevant code examples." if include_code else ""}
        
        Make it clear, concise, and easy to follow. Use proper technical writing conventions."""
        
    else:  # Custom Prompt
        prompt = st.text_area("Enter your custom prompt", height=200, 
                            placeholder="Be specific about what content you want generated...")

    # Add any additional parameters
    additional_instructions = st.text_area("Additional Instructions (optional)", 
                                        placeholder="Any other specifications or requirements...")
    
    if additional_instructions:
        prompt += f"\n\nAdditional instructions: {additional_instructions}"
    
    # Temperature setting for response variability
    temperature = st.slider("Creativity Level (Temperature)", 0.0, 1.0, 0.7, 
                          help="Higher values make output more creative but less predictable")

    # Function to call Groq API
    def call_groq_api(prompt, temperature, model):
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
                "temperature": temperature
            }
            
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                data=json.dumps(payload)
            )
            
            if response.status_code == 200:
                response_json = response.json()
                return response_json["choices"][0]["message"]["content"]
            else:
                return f"Error: {response.status_code} - {response.text}"
                
        except Exception as e:
            return f"An error occurred: {str(e)}"

    # Generate button
    if st.button("Generate Content", type="primary"):
        with st.spinner("Generating content..."):
            if 'api_key' not in st.session_state:
                st.error("Please enter your Groq API key first and save it.")
            else:
                # Store the prompt for reference
                st.session_state['current_prompt'] = prompt
                
                # Call API and get response
                response = call_groq_api(prompt, temperature, model)
                
                # Store the response
                st.session_state['current_response'] = response
                st.session_state['generation_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Display the output in the second column
with col2:
    st.subheader("Generated Content")
    
    if 'current_response' in st.session_state:
        with st.container():
            st.markdown(f"<div class='content-output'>{st.session_state['current_response']}</div>", unsafe_allow_html=True)
            st.caption(f"Generated on: {st.session_state.get('generation_time', '')}")
            
            # Download options
            output_format = st.selectbox("Download Format", ["TXT", "MD", "HTML"])
            
            if st.download_button(
                label=f"Download as {output_format}",
                data=st.session_state['current_response'],
                file_name=f"grok_content_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{output_format.lower()}",
                mime=f"text/{output_format.lower()}"
            ):
                st.success(f"Content downloaded as {output_format}")
            
            # History management
            if st.button("Save to History"):
                if 'content_history' not in st.session_state:
                    st.session_state['content_history'] = []
                
                st.session_state['content_history'].append({
                    'type': content_type,
                    'prompt': st.session_state.get('current_prompt', ''),
                    'response': st.session_state['current_response'],
                    'timestamp': st.session_state.get('generation_time', '')
                })
                
                st.success("Content saved to history")

# Content history section
if st.checkbox("Show Content History"):
    st.subheader("Content History")
    
    if 'content_history' not in st.session_state or len(st.session_state['content_history']) == 0:
        st.info("No content history yet. Generate and save content to see it here.")
    else:
        for i, item in enumerate(st.session_state['content_history']):
            with st.expander(f"{item['type']} - {item['timestamp']}"):
                st.markdown("**Prompt:**")
                st.text(item['prompt'])
                st.markdown("**Response:**")
                st.markdown(item['response'])
                
                if st.button(f"Delete Item {i+1}"):
                    st.session_state['content_history'].pop(i)
                    st.experimental_rerun()

# Footer
st.markdown("---")
st.markdown("Built with Streamlit and powered by Groq API")
