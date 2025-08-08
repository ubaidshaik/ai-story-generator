import os
import gradio as gr
from gtts import gTTS, lang
import tempfile
import google.generativeai as genai
import html

# --- Gemini API Configuration ---
try:
    api_key = os.environ["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    GEMINI_MODEL = genai.GenerativeModel('gemini-1.5-flash')
    print("Gemini API configured successfully.")
except KeyError:
    print("🚨 Critical Error: GOOGLE_API_KEY environment variable not found.")
    GEMINI_MODEL = None
except Exception as e:
    print(f"An error occurred during Gemini configuration: {e}")
    GEMINI_MODEL = None

# --- Constants ---
SUPPORTED_LANGUAGES = {
    "English": "en", "Spanish": "es", "French": "fr", "German": "de", 
    "Italian": "it", "Portuguese": "pt", "Dutch": "nl", "Russian": "ru",
    "Japanese": "ja", "Korean": "ko", "Chinese (Mandarin)": "zh-CN",
    "Hindi": "hi", "Arabic": "ar", "Bengali": "bn", "Indonesian": "id",
    "Turkish": "tr", "Telugu": "te", "Tamil": "ta", "Malayalam": "ml", "Kannada": "kn"
}

# --- Content Generation Function (Unchanged) ---
def generate_content(content_type, genre, theme, tone, characters, creativity_level, language):
    if not GEMINI_MODEL:
        return "❌ Error: Gemini API is not configured. Please set your GOOGLE_API_KEY."
    temperature_map = {"Low (Structured)": 0.3, "Medium (Balanced)": 0.7, "High (Imaginative)": 1.0, "Wild (Experimental)": 1.3}
    temperature = temperature_map.get(creativity_level, 0.7)
    generation_config = genai.types.GenerationConfig(temperature=temperature, top_p=0.95, max_output_tokens=2048)
    language_instruction = f"IMPORTANT: The entire output must be written in the following language: {language}."
    if content_type == "Story":
        prompt = f"{language_instruction}\n\nPlease write a short {genre} story with the theme '{theme}' in a {tone} tone. Include characters: {characters}."
    else:
        prompt = f"{language_instruction}\n\nPlease write a {tone} poem about '{theme}' in the style of {genre}. Include elements of: {characters}."
    try:
        response = GEMINI_MODEL.generate_content(prompt, generation_config=generation_config)
        return response.text.strip()
    except Exception as e:
        return f"❌ Error generating content with Gemini: {str(e)}"

# --- Save to HTML Function (Unchanged) ---
def save_to_html(content, title="output"):
    try:
        safe_title = html.escape(title if title else "Generated Content")
        escaped_content = html.escape(content)
        html_template = f"""
        <!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>{safe_title}</title>
        <style>body{{font-family: sans-serif; line-height: 1.6; padding: 2em; max-width: 800px; margin: 20px auto;}}
        .container{{padding: 2em; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);}}
        pre{{white-space: pre-wrap; word-wrap: break-word; font-size: 1.1em;}}</style></head>
        <body><div class="container"><h1>{safe_title}</h1><hr><pre>{escaped_content}</pre></div></body></html>
        """
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode='w', encoding='utf-8') as tmp_file:
            tmp_file.write(html_template)
            return tmp_file.name
    except Exception as e:
        print(f"Error creating HTML file: {e}")
        return None

# --- Text to Audio (Unchanged) ---
def generate_audio(text, language_name):
    try:
        lang_code = SUPPORTED_LANGUAGES.get(language_name, 'en')
        if len(text) > 4800: text = text[:4800] + "..."
        tts = gTTS(text, lang=lang_code, slow=False)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_audio:
            tts.save(tmp_audio.name)
            return tmp_audio.name
    except Exception as e:
        print(f"Error generating audio: {e}")
        return None

# --- Main Interface Logic (Unchanged) ---
def interface(content_type, genre, theme, tone, characters, creativity_level, language):
    gr.Info(f"Generating your creative content in {language}...")
    generated_text = generate_content(content_type, genre, theme, tone, characters, creativity_level, language)
    
    pdf_instructions_text = """
    **To save as PDF:**
    1.  Open the downloaded HTML file in your browser.
    2.  Press `Ctrl+P` (or `Cmd+P` on Mac).
    3.  Change the destination to **"Save as PDF"** and click Save.
    """
    
    if "❌ Error" in generated_text:
        return generated_text, None, None, gr.Button(interactive=False), gr.Markdown(visible=False)
    
    html_path = save_to_html(generated_text, theme[:30])
    audio_path = generate_audio(generated_text, language)
    
    return (
        gr.Textbox(value=generated_text, interactive=False), 
        gr.File(value=html_path, visible=True if html_path else False), 
        gr.Audio(value=audio_path, visible=True if audio_path else False), 
        gr.Button(interactive=True),
        gr.Markdown(value=pdf_instructions_text, visible=True if html_path else False)
    )

# --- Plot Outline Generator (Unchanged) ---
def generate_outline(content_type, genre, theme, tone, characters, language):
    if not GEMINI_MODEL: return "❌ Error: Gemini API is not configured."
    gr.Info(f"Generating plot outline in {language}...")
    language_instruction = f"IMPORTANT: Write the output in this language: {language}."
    if content_type == "Story":
        prompt = f"{language_instruction}\n\nGenerate a concise plot outline for a {genre} story with theme '{theme}' and tone '{tone}', featuring: {characters}."
    else:
        prompt = f"{language_instruction}\n\nGenerate a structural outline for a {tone} poem about '{theme}' in the style of {genre}, featuring: {characters}."
    try:
        response = GEMINI_MODEL.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"❌ Error generating outline: {str(e)}"

# --- Gradio UI (MODIFIED) ---
with gr.Blocks(theme=gr.themes.Soft(primary_hue="blue")) as demo:
    # UPDATED HEADING
    gr.Markdown(
        """
        <h1 style="text-align:center; color:#4A90E2;">AI STORY AND POEM GENERATOR</h1>
        <p style="text-align:center;">
        Create stories and poems in any language. Powered by <strong>Google Gemini</strong>.
        </p>
        """
    )
    with gr.Row():
        with gr.Column(scale=1):
            content_type_radio = gr.Radio(["Story", "Poem"], label="✨ Content Type", value="Story")
            genre_dropdown = gr.Dropdown(["Fantasy", "Sci-Fi", "Mystery", "Romance", "Horror", "Historical", "Adventure", "Thriller", "Sonnet", "Haiku", "Free Verse", "Epic", "Children's"], label="🎭 Genre/Style", value="Fantasy")
            language_dropdown = gr.Dropdown(list(SUPPORTED_LANGUAGES.keys()), label="🌐 Language", value="English")
            # UPDATED TONES
            tone_radio = gr.Radio(
                ["Light-hearted", "Dramatic", "Funny", "Serious", "Inspiring", "Melancholy", 
                 "Suspenseful", "Whimsical", "Philosophical", "Hopeful"],
                label="🎶 Tone", value="Serious"
            )
            creativity_slider = gr.Radio(["Low (Structured)", "Medium (Balanced)", "High (Imaginative)", "Wild (Experimental)"], label="💡 Creativity Level", value="Medium (Balanced)")
        with gr.Column(scale=2):
            theme_textbox = gr.Textbox(label="📖 Theme/Concept", placeholder="e.g., A haunted clock tower")
            characters_textbox = gr.Textbox(label="👥 Key Characters/Elements", placeholder="e.g., Elara the mage, Captain Zeke")
            outline_btn = gr.Button("✏️ Generate Plot Outline", variant="secondary")
            outline_output = gr.Textbox(label="Plot Outline/Poem Structure", interactive=False, lines=5)
            outline_btn.click(fn=generate_outline, inputs=[content_type_radio, genre_dropdown, theme_textbox, tone_radio, characters_textbox, language_dropdown], outputs=outline_output)
            generate_btn = gr.Button("🚀 Generate Story/Poem", variant="primary")
    with gr.Row():
        generated_text_output = gr.Textbox(label="✍️ Generated Content", show_copy_button=True, interactive=False, lines=15)
    with gr.Row():
        html_download_button = gr.File(label="📄 Download as HTML (for PDF)", visible=False)
        audio_player = gr.Audio(label="🔊 Listen to Audio", visible=False)
        regenerate_button = gr.Button("🔄 Regenerate", interactive=False)
    
    pdf_instructions = gr.Markdown(visible=False)

    all_inputs = [content_type_radio, genre_dropdown, theme_textbox, tone_radio, characters_textbox, creativity_slider, language_dropdown]
    all_outputs = [generated_text_output, html_download_button, audio_player, regenerate_button, pdf_instructions]
    
    generate_btn.click(fn=interface, inputs=all_inputs, outputs=all_outputs)
    regenerate_button.click(fn=interface, inputs=all_inputs, outputs=all_outputs)
    
    # UPDATED EXAMPLES
    gr.Examples(
        examples=[
            ["Story", "Fantasy", "The last dragon's secret", "Inspiring", "Elandra the elf, Drogor the dragon", "Medium (Balanced)", "English"],
            ["Story", "Thriller", "ఒక డిటెక్టివ్ చివరి కేసు", "Suspenseful", "డిటెక్టివ్ విక్రమ్, ఒక పాత భవంతి", "High (Imaginative)", "Telugu"],
            ["Poem", "Free Verse", "மழைக்குப் பிறகு நகரத்தின் வாசனை", "Melancholy", "ஈரமான தெருக்கள், தேநீர் கடைகள்", "Medium (Balanced)", "Tamil"],
            ["Story", "Horror", " ഉപേക്ഷിക്കപ്പെട്ട ആശുപത്രിയുടെ രഹസ്യം", "Suspenseful", "നാല് കോളേജ് വിദ്യാർത്ഥികൾ, ഒരു പഴയ ഡയറി", "High (Imaginative)", "Malayalam"],
            ["Story", "Sci-Fi", "Una IA colonial que funciona mal", "Suspenseful", "Comandante Eva, el núcleo de la IA", "Medium (Balanced)", "Spanish"],
            ["Poem", "Sonnet", "L'amour dans un café parisien", "Light-hearted", "Deux amants, clair de lune", "High (Imaginative)", "French"],
            ["Story", "Historical", "A samurai's final battle", "Dramatic", "Kenshin, a rival warrior", "Medium (Balanced)", "Japanese"],
            ["Story", "Adventure", "एक खोया हुआ खजाना", "Inspiring", "आर्यन, एक युवा साहसी", "Low (Structured)", "Hindi"],
            ["Poem", "Epic", "Сказание о древнем герое", "Serious", "Иван, дракон, принцесса", "High (Imaginative)", "Russian"]
        ],
        inputs=all_inputs,
        outputs=all_outputs,
        fn=interface,
        cache_examples=False,
    )

if __name__ == "__main__":
    if not GEMINI_MODEL:
        print("\nApplication cannot start. Please set your GOOGLE_API_KEY environment variable.")
    else:
        print("Launching AI Story and Poem Generator...")
        demo.launch()
