from openai import OpenAI


def transcribe_audio(file_path):
    client = OpenAI()
    audio_file= open(file_path, "rb")
    transcription = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_file,
        response_format="text",
        prompt="token,实操,周老师",
    )
    audio_file.close()
    print(transcription)
    return transcription