#!/usr/bin/env python3
"""
Enhanced Manuscript Assistant - Geava    action_count = len(re.findall(action_words, text, re.IGNORECASE))
    description_count = len(re.findall(description_words, text, re.IGNORECASE))
    
    # Dialog vs narrative ratio
    dialog_text = re.findall(r'["\'][^"\']["\']', text)
    dialog_words = sum(len(d.split()) for d in dialog_text)
    total_words = len(text.split())
    dialog_ratio = dialog_words / total_words if total_words > 0 else 0analyse en herschrijf functies
"""
import re
from pathlib import Path

# ====== GEAVANCEERDE ANALYSE FUNCTIES ======

def analyze_character_development(text):
    """Analyseer karakterontwikkeling en personages"""
    characters = {}
    
    # Verbeterde naam detectie - meer specifiek voor karakternamen
    names = re.findall(r'\b[A-Z][a-z]{2,}(?:\s+[A-Z][a-z]+)*\b', text)
    name_counts = {}
    
    # Uitgebreidere stopwoorden lijst
    stopwords = {
        'Het', 'De', 'Een', 'Maar', 'En', 'Of', 'Dan', 'Dus', 'Want', 'Omdat', 'Toen', 'Als',
        'Dat', 'Dit', 'Die', 'Deze', 'Wel', 'Niet', 'Ook', 'Nog', 'Al', 'Zo', 'Zeer',
        'Hoofdstuk', 'Chapter', 'Deel', 'Part', 'Sectie', 'Epiloog', 'Proloog'
    }
    
    for name in names:
        # Controleer of het geen stopwoord of algemeen woord is
        if len(name) >= 3 and name not in stopwords and not name.lower() in ['het', 'een', 'die', 'deze']:
            name_counts[name] = name_counts.get(name, 0) + 1
    
    # Filter for likely character names (mentioned >1 time, longer names get priority)
    likely_characters = {}
    for name, count in name_counts.items():
        if count >= 2 or (count >= 1 and len(name) >= 5):  # Longer names like "Eldrin" get priority
            likely_characters[name] = count
    
    # Search for emotion words per character
    emotions = r'\b(afraid|happy|sad|angry|frustrated|excited|nervous|calm|tense|joyful|unhappy|anxious|proud|ashamed|disappointed|scared|worried|confused|surprised|shocked)\b'
    
    character_analysis = {}
    for char in likely_characters:
        # Find sentences with this character
        char_sentences = re.findall(f'[^.!?]*\\b{char}\\b[^.!?]*[.!?]', text, re.IGNORECASE)
        emotions_found = []
        for sentence in char_sentences:
            emotions_found.extend(re.findall(emotions, sentence, re.IGNORECASE))
        
        character_analysis[char] = {
            'mentions': likely_characters[char],
            'emotions': emotions_found,
            'sentences': len(char_sentences)
        }
    
    return character_analysis

def analyze_pacing(text):
    """Analyze story rhythm and pacing"""
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    
    # Calculate sentence length variation
    lengths = [len(s.split()) for s in sentences]
    avg_length = sum(lengths) / len(lengths) if lengths else 0
    
    # Search for action words vs description
    action_words = r'\b(ran|jumped|grabbed|shouted|screamed|fought|hit|pushed|pulled|threw|rushed|leaped|struck|slammed|burst|charged)\b'
    description_words = r'\b(was|had|seemed|stood|lay|sat|looked|felt|thought|knew|appeared|remained)\b'
    
    action_count = len(re.findall(action_words, text, re.IGNORECASE))
    description_count = len(re.findall(description_words, text, re.IGNORECASE))
    
    # Dialog vs narratief ratio
    dialog_text = re.findall(r'["\'"][^"\']*["\']', text)
    dialog_words = sum(len(d.split()) for d in dialog_text)
    total_words = len(text.split())
    dialog_ratio = dialog_words / total_words if total_words > 0 else 0
    
    return {
        'avg_sentence_length': round(avg_length, 2),
        'sentence_variety': round(max(lengths) - min(lengths), 2) if lengths else 0,
        'action_description_ratio': round(action_count / max(description_count, 1), 2),
        'dialog_ratio': round(dialog_ratio, 3),
        'pacing_score': calculate_pacing_score(action_count, description_count, dialog_ratio)
    }

def calculate_pacing_score(action_count, description_count, dialog_ratio):
    """Bereken overall pacing score (1-10)"""
    # Ideaal: balans tussen actie/beschrijving, goede dialog ratio
    action_balance = min(action_count / max(description_count, 1), 2.0) / 2.0  # Max 1.0
    dialog_balance = min(dialog_ratio * 2, 1.0)  # Ideaal rond 0.3-0.5
    
    return round((action_balance + dialog_balance) * 5, 1)

def analyze_style_issues(text):
    """Detect common style problems"""
    issues = []
    
    # Too many adverbs
    adverbs = re.findall(r'\b\w+ly\b', text, re.IGNORECASE)
    if len(adverbs) > len(text.split()) * 0.05:  # More than 5%
        issues.append(f"Too many adverbs ({len(adverbs)} found). Replace with stronger verbs.")
    
    # Repeated words
    words = re.findall(r'\b\w+\b', text.lower())
    word_counts = {}
    for word in words:
        if len(word) > 3:  # Only longer words
            word_counts[word] = word_counts.get(word, 0) + 1
    
    repeated = {w: c for w, c in word_counts.items() if c > 5}
    if repeated:
        issues.append(f"Repeated words: {', '.join([f'{w} ({c}x)' for w, c in list(repeated.items())[:5]])}")
    
    # Weak verbs
    weak_verbs = ['was', 'had', 'went', 'came', 'did', 'made', 'got', 'put', 'took']
    weak_count = sum(text.lower().count(verb) for verb in weak_verbs)
    total_verbs = len(re.findall(r'\b\w+(?:ed|ing|s)\b', text)) + weak_count
    
    if weak_count > total_verbs * 0.3:
        issues.append(f"Many weak verbs ({weak_count}). Use more specific actions.")
    
    # Info dumps (long paragraphs without dialog)
    paragraphs = text.split('\n\n')
    long_paras = [p for p in paragraphs if len(p.split()) > 100 and '"' not in p]
    if long_paras:
        issues.append(f"{len(long_paras)} possible info-dumps found. Break up with action/dialog.")
    
    return issues

def analyze_show_vs_tell(text):
    """Analyze show vs tell ratio"""
    # "Tell" indicators
    tell_words = r'\b(felt|thought|knew|understood|realized|was\s+\w+|seemed\s+\w+|appeared\s+\w+)\b'
    tell_matches = len(re.findall(tell_words, text, re.IGNORECASE))
    
    # "Show" indicators (actions, senses, dialog)
    show_words = r'\b(looked|listened|smelled|tasted|felt|grabbed|whispered|shouted|trembled|sweated|glanced|stared|reached|touched|smiled|frowned)\b'
    show_matches = len(re.findall(show_words, text, re.IGNORECASE))
    
    sensory_words = r'\b(saw|heard|smelled|tasted|felt|warm|cold|soft|rough|sweet|sour|bright|dark|loud|quiet)\b'
    sensory_count = len(re.findall(sensory_words, text, re.IGNORECASE))
    
    total_words = len(text.split())
    
    return {
        'tell_ratio': round(tell_matches / max(total_words, 1) * 100, 2),
        'show_ratio': round((show_matches + sensory_count) / max(total_words, 1) * 100, 2),
        'show_vs_tell_score': calculate_show_tell_score(show_matches + sensory_count, tell_matches)
    }

def calculate_show_tell_score(show_count, tell_count):
    """Calculate show vs tell score (1-10)"""
    if tell_count == 0:
        return 10.0
    ratio = show_count / tell_count
    return min(round(ratio * 2, 1), 10.0)

# ====== ADVANCED PROMPT FUNCTIONS ======

def p_advanced_rewrite(title, text, focus_area="overall"):
    """Advanced rewrite prompt with specific focus"""
    focus_instructions = {
        "overall": "improve overall quality, increase tension and emotional impact",
        "pacing": "improve rhythm, alternate short and long sentences, add micro-tension",
        "character": "deepen characterization, show emotions through actions instead of telling",
        "dialog": "make dialogues more natural and characteristic, add subtext",
        "description": "make descriptions more vivid with sensory details",
        "tension": "increase tension and conflict in every scene",
        "style": "improve writing style, replace weak verbs and remove unnecessary adverbs"
    }
    
    instruction = focus_instructions.get(focus_area, focus_instructions["overall"])
    
    return f"""Rewrite this section professionally to {instruction}. 

SPECIFIC FOCUS: {focus_area.upper()}

GUIDELINES:
- Maintain all core events and plot points
- Show emotions through actions, body language and senses instead of telling
- Use powerful, specific verbs
- Vary sentence length for better flow
- Add subtext to dialogues
- Make every sentence relevant to plot or character
- Avoid info-dumps, weave information naturally

SECTION: {title}

ORIGINAL TEXT:
{text[:8000]}

REWRITTEN VERSION:"""

def p_character_voice_analysis(text):
    """Analyze and improve character voices"""
    return f"""Analyze the character voices in this text. Be VERY PRECISE with character names - use EXACTLY the names as they appear in the text.

CRITICAL INSTRUCTION: Copy character names LITERALLY from the text. Don't change names, don't invent new names.

1. CHARACTER IDENTIFICATION: Which characters speak/act? (use exact names from text)
2. VOICE DISTINCTION: How do the character voices distinguish themselves?
3. CONSISTENCY: Are the voices consistent throughout the text?
4. IMPROVEMENT SUGGESTIONS: How to make each voice more unique?

For each character (with exact name from text):
- Speech patterns/word choice
- Typical expressions
- Emotional tone
- Improvement points

IMPORTANT: Use ONLY names that actually appear in the text. Don't invent alternative names.

TEXT:
{text[:10000]}"""

def p_scene_structure_analysis(text):
    """Analyze scene structure and dramatic development"""
    return f"""Analyze the scene structure of this text according to dramatic principles:

1. OPENING: How does the scene draw the reader in?
2. CONFLICT/TENSION: What conflicts or tensions are present?
3. TURNING POINT: Are there plot twists or changes?
4. CLIMAX: What is the peak moment of the scene?
5. ENDING: How does the scene end (hook for next)?

For each element provide:
- What works well
- What's missing
- Concrete improvement points
- Example sentences for improvement

TEXT:
{text[:12000]}"""

def p_emotional_depth_analysis(text):
    """Analyze emotional depth and impact"""
    return f"""Analyze the emotional impact of this text:

1. EMOTIONS: What emotions are evoked in the reader?
2. TECHNIQUES: How are emotions conveyed (show vs tell)?
3. INTENSITY: How intense are the emotional moments?
4. AUTHENTICITY: Do the emotions feel real and believable?

Improvement points:
- Replace "emotion telling" with "emotion showing"
- Add sensory details to emotional moments
- Use body reactions to show emotions
- Make dialogue more emotionally charged

TEXT:
{text[:10000]}"""

def p_prose_quality_analysis(text):
    """Analyze prose quality and style"""
    return f"""Provide an in-depth analysis of prose quality:

1. SENTENCE STRUCTURE: Variation in length and complexity
2. WORD CHOICE: Power and precision of words
3. RHYTHM: Flow and readability
4. IMAGERY: Use of metaphors and comparisons
5. ORIGINALITY: Avoiding clichés

For each aspect, provide:
- Strong points
- Weak points
- 3 concrete improvements with examples
- Rewrite 2-3 weak sentences as demonstration

TEXT:
{text[:8000]}"""

# ====== GENRE-SPECIFIC ANALYSIS ======

def p_genre_specific_analysis(text, genre="fantasy"):
    """Genre-specific analysis and suggestions"""
    genre_guidelines = {
        "fantasy": {
            "elements": ["worldbuilding", "magic systems", "mythical creatures", "hero's journey"],
            "tone": "epic and immersive",
            "pacing": "alternating between action and character building"
        },
        "thriller": {
            "elements": ["tension", "danger", "time pressure", "plot twists"],
            "tone": "tense and urgent", 
            "pacing": "fast with short, gripping sentences"
        },
        "romance": {
            "elements": ["emotional connection", "sexual tension", "relationship dynamics"],
            "tone": "emotional and intimate",
            "pacing": "building romantic tension"
        },
        "mystery": {
            "elements": ["clues", "red herrings", "deduction", "revelations"],
            "tone": "intriguing and mysterious",
            "pacing": "gradual revelation of information"
        }
    }
    
    guide = genre_guidelines.get(genre, genre_guidelines["fantasy"])
    
    return f"""Analyze this text from a {genre.upper()} perspective:

GENRE REQUIREMENTS:
- Elements: {', '.join(guide['elements'])}
- Tone: {guide['tone']}
- Pacing: {guide['pacing']}

EVALUATION:
1. Which genre elements are present?
2. Which are missing or weak?
3. Does the tone match the genre?
4. Is the pacing suitable for {genre}?

IMPROVEMENT POINTS:
- 5 concrete suggestions to strengthen genre authenticity
- Example sentences that better fit {genre}
- What should be added/removed?

TEXT:
{text[:10000]}"""