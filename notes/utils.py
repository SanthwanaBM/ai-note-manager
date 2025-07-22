from transformers import pipeline
import docx
import pdfplumber
import spacy
import random
import json
import speech_recognition as sr
from pydub import AudioSegment

# Load summarizer
summarizer = pipeline("summarization", model="t5-small")

def extract_text_from_file(file_path):
    if file_path.endswith('.txt'):
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    elif file_path.endswith('.docx'):
        doc = docx.Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])
    elif file_path.endswith('.pdf'):
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text
    else:
        return "Unsupported file format."

def generate_summary(text):
    if len(text) < 50:
        return "Text too short to summarize."
    if len(text) > 4000:
        return "Note too large to summarize. Please upload a smaller file or split it."

    result = summarizer(text, max_length=200, min_length=50, do_sample=False)
    return result[0]['summary_text']


# Load spaCy model once
nlp = spacy.load("en_core_web_sm")


def extract_glossary(text, num_terms=10):
    doc = nlp(text)

    # Collect all unique noun and proper noun lemmas
    terms = {}
    for token in doc:
        if token.pos_ in ['NOUN', 'PROPN'] and len(token.text) > 2:
            token_text = token.lemma_.lower()
            terms[token_text] = terms.get(token_text, 0) + 1

    # Sort terms by frequency
    sorted_terms = sorted(terms.items(), key=lambda x: -x[1])

    # Return top N terms (capitalize for display)
    top_terms = [term[0].capitalize() for term in sorted_terms[:num_terms]]

    return top_terms




def generate_quiz(summary_text, num_questions=10):
    if not summary_text or len(summary_text) < 50:
        return {"questions": []}

    sentences = [s.strip() for s in summary_text.split('.') if len(s.strip()) > 20]
    if not sentences:
        return {"questions": []}

    questions = []
    used_sentences = set()

    for _ in range(min(num_questions, len(sentences))):
        sentence = random.choice(sentences)

        if sentence in used_sentences:
            continue
        used_sentences.add(sentence)

        words = sentence.split()
        if len(words) < 5:
            continue

        index = random.randint(1, len(words) - 2)
        answer = words[index]

        # Skip very common or punctuation-heavy words
        if not answer.isalpha() or answer.lower() in {"the", "and", "but", "with", "have"}:
            continue

        words[index] = "____"
        question = ' '.join(words)

        # Generate distractors (random words from other sentences)
        distractors = set()
        all_words = [w for s in sentences for w in s.split() if w.isalpha() and w.lower() != answer.lower()]
        while len(distractors) < 3 and all_words:
            distractor = random.choice(all_words)
            if distractor.lower() != answer.lower():
                distractors.add(distractor)

        options = list(distractors) + [answer]
        random.shuffle(options)

        questions.append({
            "question": question,
            "options": options,
            "correctAnswer": answer
        })

    return {"questions": questions}




def convert_voice_to_text(file_path):
    recognizer = sr.Recognizer()

    # Convert to wav if not already
    if not file_path.endswith('.wav'):
        audio = AudioSegment.from_file(file_path)
        wav_path = file_path.rsplit('.', 1)[0] + '.wav'
        audio.export(wav_path, format='wav')
        file_path = wav_path

    with sr.AudioFile(file_path) as source:
        audio_data = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio_data)
        return text
    except sr.UnknownValueError:
        return "Could not understand audio."
    except sr.RequestError:
        return "Could not connect to recognition service."



