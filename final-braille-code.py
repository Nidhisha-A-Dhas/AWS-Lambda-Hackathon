import boto3
import base64
import uuid
import urllib.request
import urllib.parse
import json
import time
import re

print("Lambda invoked successfully")

s3 = boto3.client('s3')
transcribe = boto3.client('transcribe', region_name='ap-south-1')
translate = boto3.client('translate', region_name='ap-south-1')

INPUT_BUCKET = 'braille-bucket'
OUTPUT_BUCKET = 'output-bucket-braille'

language_config = {
    'hi': {'aws_code': 'hi', 'lang_code': 'hi-IN'},
    'ta': {'aws_code': 'ta', 'lang_code': 'ta-IN'},
    'kn': {'aws_code': 'kn', 'lang_code': 'kn-IN'},
    'te': {'aws_code': 'te', 'lang_code': 'te-IN'},
    'ml': {'aws_code': 'ml', 'lang_code': 'ml-IN'},
}


braille_maps = {
    'hi': {
    # Vowels
    'अ': '⠁', 'आ': '⠡', 'इ': '⠊', 'ई': '⠘', 'उ': '⠳', 'ऊ': '⠳⠳',
    'ऋ': '⠚', 'ए': '⠑', 'ऐ': '⠌', 'ओ': '⠕', 'औ': '⠕⠕',

    # Consonants
    'क': '⠅', 'ख': '⠓', 'ग': '⠛', 'घ': '⠣', 'ङ': '⠢',
    'च': '⠉', 'छ': '⠡', 'ज': '⠚', 'झ': '⠱', 'ञ': '⠴',
    'ट': '⠞', 'ठ': '⠟', 'ड': '⠙', 'ढ': '⠙⠤', 'ण': '⠻',
    'त': '⠞', 'थ': '⠹', 'द': '⠙', 'ध': '⠫', 'न': '⠝',
    'प': '⠏', 'फ': '⠋', 'ब': '⠃', 'भ': '⠃⠤', 'म': '⠍',
    'य': '⠽', 'र': '⠗', 'ल': '⠇', 'व': '⠧',
    'श': '⠱', 'ष': '⠮', 'स': '⠎', 'ह': '⠓',

    # Matras (vowel signs)
    'ा': '⠡', 'ि': '⠊', 'ी': '⠘', 'ु': '⠳', 'ू': '⠳⠳',
    'े': '⠑', 'ै': '⠌', 'ो': '⠕', 'ौ': '⠕⠕',

    # Special Characters
    'ं': '⠂',    # Anusvara
    'ः': '⠆',    # Visarga
    'ँ': '⠄',    # Chandrabindu
    '्': '',      # Halant (virama) – no braille output
    ' ': ' ',     # Space

    # Punctuation
    ',': '⠂',
    '.': '⠲',
    '।': '⠲',     # Danda
    '?': '⠦',
    '!': '⠖',
    '-': '⠤',
    ':': '⠒',
    ';': '⠆',
    '"': '⠶',
    "'": '⠄',
    '“': '⠶', '”': '⠶',
    '‘': '⠄', '’': '⠄',
    '(': '⠦', ')': '⠴'
    },

    'ta': {
    # Vowels
    'அ': '⠁', 'ஆ': '⠁⠁', 'இ': '⠊', 'ஈ': '⠊⠊', 'உ': '⠥', 'ஊ': '⠥⠥',
    'எ': '⠑', 'ஏ': '⠑⠑', 'ஐ': '⠡', 'ஒ': '⠕', 'ஓ': '⠕⠕', 'ஔ': '⠪',

    # Consonants
    'க': '⠅', 'ங': '⠝', 'ச': '⠉', 'ஞ': '⠯', 'ட': '⠞', 'ண': '⠻',
    'த': '⠞', 'ந': '⠝', 'ப': '⠏', 'ம': '⠍',
    'ய': '⠽', 'ர': '⠗', 'ல': '⠇', 'வ': '⠧',
    'ழ': '⠵', 'ள': '⠯', 'ற': '⠻', 'ன': '⠝',

    # Extra consonants
    'ஸ': '⠎',  # For Sanskrit-based Tamil words

    # Vowel signs (matras)
    'ா': '⠁', 'ி': '⠊', 'ீ': '⠊⠊', 'ு': '⠥', 'ூ': '⠥⠥',
    'ெ': '⠑', 'ே': '⠑⠑', 'ை': '⠡', 'ொ': '⠕', 'ோ': '⠕⠕', 'ௌ': '⠪',

    # Special characters
    'ஃ': '⠸',  # Aytham
    '்': '',     # Pulli (virama)
    ' ': ' ',    # Space

    # Common punctuation
    ',': '⠂',
    '.': '⠲',
    '?': '⠦',
    '!': '⠖',
    '-': '⠤',
    ':': '⠒',
    ';': '⠆',
    '"': '⠶',
    "'": '⠄',
    '“': '⠶',
    '”': '⠶',
    '‘': '⠄',
    '’': '⠄',
    '(': '⠦',
    ')': '⠴'
},
    'kn': {
    # Vowels
    "ಅ": "⠁", "ಆ": "⠁⠁", "ಇ": "⠊", "ಈ": "⠊⠊", "ಉ": "⠥", "ಊ": "⠥⠥",
    "ಋ": "⠗", "ಎ": "⠑", "ಏ": "⠑⠑", "ಐ": "⠊⠑", "ಒ": "⠕", "ಓ": "⠕⠕", "ಔ": "⠕⠑",

    # Consonants
    "ಕ": "⠅", "ಖ": "⠅⠕", "ಗ": "⠛", "ಘ": "⠛⠕", "ಙ": "⠢",
    "ಚ": "⠉", "ಛ": "⠉⠕", "ಜ": "⠚", "ಝ": "⠚⠕", "ಞ": "⠔",
    "ಟ": "⠞", "ಠ": "⠞⠕", "ಡ": "⠙", "ಢ": "⠙⠕", "ಣ": "⠝",
    "ತ": "⠞", "ಥ": "⠞⠕", "ದ": "⠙", "ಧ": "⠙⠕", "ನ": "⠝",
    "ಪ": "⠏", "ಫ": "⠏⠕", "ಬ": "⠃", "ಭ": "⠃⠕", "ಮ": "⠍",
    "ಯ": "⠽", "ರ": "⠗", "ಲ": "⠇", "ವ": "⠧",
    "ಶ": "⠎", "ಷ": "⠱", "ಸ": "⠎⠎", "ಹ": "⠓",
    "ಳ": "⠇⠕", "ಕ್ಷ": "⠅⠱", "ಜ್ಞ": "⠚⠔",

    # Matras
    "ಾ": "⠁", "ಿ": "⠊", "ೀ": "⠊⠊", "ು": "⠥", "ೂ": "⠥⠥",
    "ೆ": "⠑", "ೇ": "⠑⠑", "ೈ": "⠊⠑", "ೊ": "⠕", "ೋ": "⠕⠕", "ೌ": "⠕⠑", "ೃ": "⠗",

    # Other
    "ಂ": "⠄", "ಃ": "⠂", "್": "",  # Halant

    # Punctuation
    ".": "⠲", ",": "⠂", "?": "⠦", "!": "⠖", ":": "⠒", ";": "⠆",
    "“": "⠦", "”": "⠴", "'": "⠄", "\"": "⠶", "-": "⠤", "(": "⠣", ")": "⠜",
    "–": "⠤", "—": "⠤", "…": "⠄⠄⠄", "।": "⠲"
},

    'ml':  {
    # Independent vowels
    'അ': '⠁', 'ആ': '⠁⠁', 'ഇ': '⠊', 'ഈ': '⠊⠊', 'ഉ': '⠥', 'ഊ': '⠥⠥',
    'ഋ': '⠗', 'എ': '⠑', 'ഏ': '⠑⠑', 'ഐ': '⠡', 'ഒ': '⠕', 'ഓ': '⠕⠕', 'ഔ': '⠪',

    # Consonants
    'ക': '⠅', 'ഖ': '⠣', 'ഗ': '⠛', 'ഘ': '⠣⠤', 'ങ': '⠜',
    'ച': '⠉', 'ഛ': '⠡', 'ജ': '⠚', 'ഝ': '⠱', 'ഞ': '⠴',
    'ട': '⠞', 'ഠ': '⠟', 'ഡ': '⠙', 'ഢ': '⠙⠤', 'ണ': '⠻',
    'ത': '⠞', 'ഥ': '⠹', 'ദ': '⠙', 'ധ': '⠫', 'ന': '⠝',
    'പ': '⠏', 'ഫ': '⠋', 'ബ': '⠃', 'ഭ': '⠃⠤', 'മ': '⠍',
    'യ': '⠽', 'ര': '⠗', 'ല': '⠇', 'വ': '⠧',
    'ശ': '⠱', 'ഷ': '⠮', 'സ': '⠎', 'ഹ': '⠓',
    'ള': '⠳', 'ഴ': '⠵', 'റ': '⠻',

    # Vowel signs (matras)
    'ാ': '⠁', 'ി': '⠊', 'ീ': '⠊⠊', 'ു': '⠥', 'ൂ': '⠥⠥',
    'ൃ': '⠗', 'െ': '⠑', 'േ': '⠑⠑', 'ൈ': '⠡', 'ൊ': '⠕', 'ോ': '⠕⠕', 'ൌ': '⠪',

    # Diacritics and modifiers
    'ം': '⠂',  # anusvara
    'ഃ': '⠆',  # visarga
    '്': '',    # halant/virama

    # Special chillu characters (pure consonants)
    'ൻ': '⠝',  # chillu-n
    'ർ': '⠗',  # chillu-r
    'ൽ': '⠇',  # chillu-l
    'ൾ': '⠳',  # chillu-ll
    'ൗ': '⠪',  # length marker for 'ഔ'

    # Punctuation
    ',': '⠂', '.': '⠲', '?': '⠦', '!': '⠖', '-': '⠤',
    ':': '⠒', ';': '⠆', '"': '⠶', "'": '⠄',
    '“': '⠶', '”': '⠶', '‘': '⠄', '’': '⠄',
    '(': '⠦', ')': '⠴',

    # Space
    ' ': ' '
},

    'te':{
    # Vowels
    "అ": "⠁", "ఆ": "⠁⠁", "ఇ": "⠊", "ఈ": "⠊⠊", "ఉ": "⠥", "ఊ": "⠥⠥",
    "ఋ": "⠗", "ఎ": "⠑", "ఏ": "⠑⠑", "ఐ": "⠜", "ఒ": "⠕", "ఓ": "⠕⠕", "ఔ": "⠪",

    # Consonants
    "క": "⠅", "ఖ": "⠕", "గ": "⠛", "ఘ": "⠣", "ఙ": "⠻",
    "చ": "⠉", "ఛ": "⠡", "జ": "⠚", "ఝ": "⠵", "ఞ": "⠽",
    "ట": "⠞", "ఠ": "⠹", "డ": "⠙", "ఢ": "⠫", "ణ": "⠻",
    "త": "⠞", "థ": "⠹", "ద": "⠙", "ధ": "⠫", "న": "⠝",
    "ప": "⠏", "ఫ": "⠋", "బ": "⠃", "భ": "⠅⠃", "మ": "⠍",
    "య": "⠽", "ర": "⠗", "ల": "⠇", "వ": "⠧",
    "శ": "⠱", "ష": "⠩", "స": "⠎", "హ": "⠓",
    "ళ": "⠳", "క్ష": "⠅⠱", "ఱ": "⠯",

    # Vowel signs (matras)
    "ా": "⠁", "ి": "⠊", "ీ": "⠊⠊", "ు": "⠥", "ూ": "⠥⠥",
    "ె": "⠑", "ే": "⠑⠑", "ై": "⠜", "ొ": "⠕", "ో": "⠕⠕", "ౌ": "⠪",
    "్": "",  # Halant

    # Special characters
    "ం": "⠂",    # Anusvara (nasal sound)
    "ః": "⠄",    # Visarga
    "ఁ": "⠈",    # Chandrabindu (if needed)

    # Punctuation
    ",": "⠂",    # Comma
    ".": "⠲",    # Period / full stop
    "?": "⠦",    # Question mark
    "!": "⠖",    # Exclamation
    "-": "⠤",    # Hyphen
    ":": "⠒",    # Colon
    ";": "⠆",    # Semicolon
    "\"": "⠶",   # Quotation mark
    "'": "⠄",    # Apostrophe
    "(": "⠦",    # Opening parenthesis
    ")": "⠴",    # Closing parenthesis
    "“": "⠶", "”": "⠶",  # Double quotes
    "‘": "⠄", "’": "⠄",  # Single quotes

    # Whitespace
    " ": " ",    # Keep space as is
}
}


def clean_translated_text(text):
    # Removes English words left un-translated
    return ' '.join(word for word in text.split() if not re.match("^[a-zA-Z]+$", word))

def text_to_braille(text, lang):
    mapping = braille_maps.get(lang, {})
    return ''.join(mapping.get(c, '') for c in text)  # skip unknown characters

def process_audio(media_uri, media_format, target_lang):
    job_name = f"Transcribe-{uuid.uuid4()}"

    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': media_uri},
        MediaFormat=media_format,
        LanguageCode='en-US'
    )

    while True:
        result = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        status = result['TranscriptionJob']['TranscriptionJobStatus']
        if status in ['COMPLETED', 'FAILED']:
            break
        time.sleep(5)

    if status == 'FAILED':
        raise Exception("Transcription failed")

    transcript_url = result['TranscriptionJob']['Transcript']['TranscriptFileUri']
    with urllib.request.urlopen(transcript_url) as response:
        transcript_data = json.loads(response.read())
        original_text = transcript_data['results']['transcripts'][0]['transcript']

    config = language_config.get(target_lang, language_config['hi'])

    translated = translate.translate_text(
        Text=original_text,
        SourceLanguageCode='en',
        TargetLanguageCode=config['aws_code']
    )

    translated_text = translated['TranslatedText']
    cleaned_text = clean_translated_text(translated_text)
    braille_output = text_to_braille(cleaned_text, target_lang)

    return {
        'original_text': original_text,
        'translated_text': translated_text,
        'cleaned_text': cleaned_text,
        'braille': braille_output
    }

def lambda_handler(event, context):
    print("Received event:", json.dumps(event))  # log full event

    try:
        body = event["body"]
        print("Decoding base64 audio...")
        audio_data = base64.b64decode(body)

        target_lang = event.get("queryStringParameters", {}).get("targetLang", "ta")
        filename = f"audio_{uuid.uuid4()}.mp3"
        media_format = "mp3"

        s3.put_object(Bucket=INPUT_BUCKET, Key=filename, Body=audio_data)
        media_uri = f"https://{INPUT_BUCKET}.s3.ap-south-1.amazonaws.com/{filename}"
        result_data = process_audio(media_uri, media_format, target_lang)

        s3.put_object(
            Bucket=OUTPUT_BUCKET,
            Key=f"results_output/{uuid.uuid4()}.json",
            Body=json.dumps(result_data, ensure_ascii=False).encode('utf-8'),
            ContentType='application/json'
        )

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST,OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps(result_data, ensure_ascii=False)
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST,OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps({'error': str(e)})
        }
