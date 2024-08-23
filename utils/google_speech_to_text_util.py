
# Imports the Google Cloud client library

import os
from google.cloud import speech

def get_encoding_from_file_extension(file_path):
    _, extension = os.path.splitext(file_path.lower())
    encoding_map = {
        '.wav': speech.RecognitionConfig.AudioEncoding.LINEAR16,
        '.flac': speech.RecognitionConfig.AudioEncoding.FLAC,
        '.mp3': speech.RecognitionConfig.AudioEncoding.MP3,
        '.ogg': speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
        # '.m4a': speech.RecognitionConfig.AudioEncoding.MP3,
    }
    return encoding_map.get(extension, speech.RecognitionConfig.AudioEncoding.ENCODING_UNSPECIFIED)


def run_quickstart(gcs_uri) -> speech.RecognizeResponse:
    # Instantiates a client
    client = speech.SpeechClient()


    audio = speech.RecognitionAudio(uri=gcs_uri)
    # 从 gcs_uri 获取文件扩展名并确定编码
    encoding = get_encoding_from_file_extension(gcs_uri)
    
    config = speech.RecognitionConfig(
        encoding=encoding,
        sample_rate_hertz=16000,
        language_code="cmn-Hans-CN",
    )

    # Detects speech in the audio file
    response = client.recognize(config=config, audio=audio)

    print(response)
    for result in response.results:
        print(f"Transcript: {result.alternatives[0].transcript}")
    return response.results[0].alternatives[0].transcript   