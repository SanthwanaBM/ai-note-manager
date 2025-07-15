from transformers import pipeline
import docx
import pdfplumber
import spacy
import random
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
    if len(text) > 2000:
        return "Note too large to summarize. Please upload a smaller file or split it."

    result = summarizer(text, max_length=150, min_length=50, do_sample=False)
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



def generate_quiz(summary_text, num_questions=3):
    if not summary_text or len(summary_text) < 50:
        return "Not enough content to generate quiz."

    sentences = [s.strip() for s in summary_text.split('.') if len(s.strip()) > 20]
    if not sentences:
        return "No suitable sentences found for quiz."

    questions = []
    for _ in range(min(num_questions, len(sentences))):
        sentence = random.choice(sentences)
        words = sentence.split()

        if len(words) < 5:
            continue  # skip short ones

        # Randomly blank out a non-trivial word
        index = random.randint(1, len(words)-2)
        answer = words[index]
        words[index] = '____'

        question = ' '.join(words)
        questions.append(f"{question}  [Answer: {answer}]")

    if not questions:
        return "No suitable quiz questions generated."

    return "\n\n".join(questions)




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



