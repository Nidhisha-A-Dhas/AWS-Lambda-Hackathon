# AWS-Lambda-Hackathon
Braille Audio Translator (Indian Languages):
Braille Audio Translator is a serverless, multilingual accessibility application designed to convert spoken audio into Braille text in major Indian languages. Built on AWS, it helps visually impaired users receive content in regional Braille scripts.
This serverless application takes audio input, converts it to text, translates it into a selected Indian language (Tamil, Hindi, Telugu, Malayalam, Kannada), and outputs the result in Unicode Braille format. The application is built using AWS Lambda, Amazon S3, Amazon Transcribe, and Amazon Translate.
Features:
-	Accepts audio input via API Gateway in .wav or .mp3 format
-	Automatic transcription using Amazon Transcribe
-	Real-time language translation to,
•	Hindi (`hi`)
•	Tamil (`ta`)
•	Telugu (`te`)
•	Malayalam (`ml`)
•	Kannada (`kn`)
-	Braille conversion using Unicode Braille maps
-	JSON output saved to and fetched from S3
-	Serverless architecture with fast, event-driven execution
AI/ML Capabilities:
-	Amazon Transcribe: Converts speech to text
-	Amazon Translate: Translates English text to target Indian language
-	Custom Braille Mapper:
-	Maps each language's characters (vowels, consonants, matras) to Unicode Braille
-	Optional Extension: Add Amazon Polly for Braille-to-speech feedback in local language
 Architecture Overview:
1. Audio Upload: Base64-encoded audio sent to API Gateway
2. AWS Lambda:
   - Decodes and uploads to input S3 bucket (‘braille-bucket)
   - Triggers transcription via Amazon Transcribe
   - Translates result using Amazon Translate
   - Converts to Unicode Braille using language-specific mappings
   - Saves final output in ‘output-braille-bucket’
3. Returns: JSON response containing Braille text with CORS support
Requirements:
-	AWS Account with:
-	S3 buckets: ‘braille-bucket’, ‘output-braille-bucket’
-	IAM Role with S3, Transcribe, Translate permissions
-	Lambda function: ‘BrailleFunction’
-	API Gateway endpoint for POST requests
-	Input format: Base64-encoded ‘.wav’ or ‘.mp3’ file in request body

