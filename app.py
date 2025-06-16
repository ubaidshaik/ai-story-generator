import os
import gradio as gr
from fpdf import FPDF
from gtts import gTTS
import tempfile
import ollama

# --- Model Configuration ---
# This is set to the model you successfully downloaded.
OLLAMA_MODEL_NAME = "gemma:2b" 

# --- Content Generation Function ---
def generate_content(content_type, genre, theme, tone):
    """
    Generates creative content (story or poem) using a locally running Ollama model.
    """
    if content_type == "Story":
        prompt = f"Write a short {genre} story with the theme '{theme}' in a {tone} tone. Make it engaging and imaginative."
        messages = [
            {"role": "system", "content": "You are a creative and vivid storyteller. Be concise."},
            {"role": "user", "content": prompt}
        ]
    else: # content_type == "Poem"
        prompt = f"Write a {tone} poem about '{theme}' in the style of {genre}. Use vivid imagery, rhymes if possible, and emotional depth."
        messages = [
            {"role": "system", "content": "You are a poetic and expressive language model. Focus on emotional depth and imagery."},
            {"role": "user", "content": prompt}
        ]

    try:
        print(f"Attempting to generate with Ollama model: {OLLAMA_MODEL_NAME}")
        # Call the local Ollama server
        response = ollama.chat(
            model=OLLAMA_MODEL_NAME,
            messages=messages,
            options={
                "temperature": 0.9,
                "num_predict": 700 # Maximum tokens for output
            }
        )
        return response['message']['content'].strip()
    except Exception as e:
        return f"❌ Error generating content with Ollama: {str(e)}\n\n**Troubleshooting:**\n1. Ensure the Ollama application is running in the background.\n2. Ensure you have downloaded the '{OLLAMA_MODEL_NAME}' model using `ollama run {OLLAMA_MODEL_NAME}` in your terminal."

# --- Utility Functions ---
def save_to_pdf(content, title="output"):
    """
    Saves the given text content to a PDF file.
    Includes a fix for common Unicode characters like smart quotes.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    
    # --- FIX for UnicodeEncodeError ---
    # Replace common "smart quotes" with standard ASCII quotes
    # This resolves the 'latin-1' codec error for these specific characters.
    content = content.replace('’', "'").replace('“', '"').replace('”', '"')
    # If other Unicode characters cause issues, you might need to add more .replace() calls
    # or consider switching to the 'fpdf2' library which has better native Unicode support.
    # ---------------------------------

    pdf.multi_cell(0, 10, content) # Pass the sanitized content
    
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(tmp_file.name)
    return tmp_file.name

def generate_audio(text):
    """
    Converts the given text to speech and saves it as an MP3 file.
    """
    tts = gTTS(text)
    tmp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(tmp_audio.name)
    return tmp_audio.name

def interface(content_type, genre, theme, tone):
    """
    Main interface function for Gradio, orchestrating content generation,
    PDF saving, and audio generation.
    """
    generated_text = generate_content(content_type, genre, theme, tone)

    if "❌ Error" in generated_text:
        return generated_text, None, None

    pdf_title = theme[:30].replace(" ", "_").replace("/", "_") if theme else "output"
    pdf_path = save_to_pdf(generated_text, title=pdf_title)

    audio_path = generate_audio(generated_text)
    
    return generated_text, pdf_path, audio_path

# --- Gradio Interface Setup ---
iface = gr.Interface(
    fn=interface,
    inputs=[
        gr.Radio(["Story", "Poem"], label="Content Type", value="Story"),
        gr.Dropdown(["Fantasy", "Sci-Fi", "Mystery", "Romance", "Horror", "Historical", "Adventure", "Thriller", "Sonnet", "Haiku", "Free Verse"],
                    label="Genre/Style", value="Fantasy"),
        gr.Textbox(label="Theme or Prompt", placeholder="e.g. A haunted clock tower, Time-traveling poet, or The last star in the universe"),
        gr.Radio(["Light-hearted", "Dramatic", "Funny", "Serious", "Inspiring", "Melancholy", "Suspenseful", "Whimsical"],
                 label="Tone", value="Serious"),
    ],
    outputs=[
        gr.Textbox(label="Generated Output", show_copy_button=True),
        gr.File(label="Download as PDF"),
        gr.Audio(label="Listen to Audio", type="filepath")
    ],
    title="📝 AI Story & Poem Generator (Powered by Local Ollama)",
    description=f"""
    Create original creative writing with AI! Choose a content type (Story or Poem),
    pick a genre/style, provide a theme, and select a tone.
    The AI will generate unique content, which you can then download as a PDF or listen to as audio.
    **This version uses the locally running Ollama with the '{OLLAMA_MODEL_NAME}' model, requiring no billing.**
    **IMPORTANT:** Ensure Ollama is installed, running in the background, and the '{OLLAMA_MODEL_NAME}' model is downloaded on your system.
    """,
    examples=[
        ["Story", "Fantasy", "A wizard's lost spellbook", "Inspiring"],
        ["Poem", "Romance", "First snow of winter", "Melancholy"],
        ["Story", "Sci-Fi", "The last human colony on Mars", "Dramatic"],
        ["Poem", "Haiku", "Cherry blossoms in spring", "Inspiring"]
    ],
    live=False
)

if __name__ == "__main__":
    print("Starting Gradio AI Story & Poem Generator...")
    print(f"Attempting to use Ollama model: {OLLAMA_MODEL_NAME}")
    print("Please ensure Ollama is installed and running, and the specified model is downloaded via `ollama run {OLLAMA_MODEL_NAME}`.")
    iface.launch()