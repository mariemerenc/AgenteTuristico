from moviepy.editor import *
import whisper
import os

# Caminho da pasta com os vídeos e onde os arquivos de texto serão salvos
video_folder = "pasta_com_videos"  # Substitua pelo caminho da sua pasta de vídeos
txt_folder = "pdf"  # Pasta onde os arquivos de texto serão salvos

# Cria a pasta para salvar os arquivos de texto, caso não exista
if not os.path.exists(txt_folder):
    os.makedirs(txt_folder)

# Carregar o modelo Whisper
modelo = whisper.load_model("base")

# Contador para nomear os arquivos de transcrição
contador = 1

# Iterar sobre os arquivos de vídeo na pasta
for video_filename in os.listdir(video_folder):
    if video_filename.endswith(('.mp4', '.avi', '.mov')):  # Filtrar apenas arquivos de vídeo
        # Caminho completo do arquivo de vídeo
        video_path = os.path.join(video_folder, video_filename)
        
        # Carregar o vídeo
        video = VideoFileClip(video_path)
        
        # Extrair áudio do vídeo e salvar como um arquivo WAV temporário
        audio_path = "audio_extraido.wav"
        video.audio.write_audiofile(audio_path, codec='pcm_s16le')
        
        # Transcrever o áudio
        result = modelo.transcribe(audio_path)
        
        # Nome do arquivo de transcrição
        txt_filename = f"transcription_{contador}.txt"
        txt_path = os.path.join(txt_folder, txt_filename)
        
        # Salvar a transcrição em um arquivo de texto
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(result["text"])
        
        # Excluir o arquivo de áudio temporário
        os.remove(audio_path)
        
        # Incrementar o contador para o próximo arquivo
        contador += 1

print(f"Transcrições concluídas e salvas na pasta '{txt_folder}'.")
