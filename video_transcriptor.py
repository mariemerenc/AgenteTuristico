from moviepy.editor import *
import whisper
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# Caminho da pasta com os vídeos e onde os arquivos PDF serão salvos
video_folder = "pasta_com_videos"  # Substitua pelo caminho da sua pasta de vídeos
pdf_folder = "pdf"  # Pasta onde os arquivos PDF serão salvos

# Cria a pasta para salvar os arquivos PDF, caso não exista
if not os.path.exists(pdf_folder):
    os.makedirs(pdf_folder)

# Carregar o modelo Whisper
modelo = whisper.load_model("base")

# Contador para nomear os arquivos de transcrição
contador = 1

# Configurações da página PDF
page_width, page_height = letter
margin_left = 50
margin_top = 750
line_spacing = 14
line_length = 90  # Limite de caracteres por linha (ajuste conforme necessário)

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
        
        # Nome do arquivo PDF
        pdf_filename = f"transcription_{contador}.pdf"
        pdf_path = os.path.join(pdf_folder, pdf_filename)
        
        # Criar o PDF e adicionar o texto transcrito
        c = canvas.Canvas(pdf_path, pagesize=letter)
        text = result["text"]
        
        # Configurar o texto no PDF
        c.setFont("Helvetica", 12)  # Fonte e tamanho
        c.drawString(margin_left, margin_top, f"Transcrição do vídeo: {video_filename}")  # Título
        
        # Posição inicial do texto
        y_position = margin_top - 30
        
        # Adicionar o texto transcrito ao PDF, quebrando em linhas menores
        for paragraph in text.split("\n"):
            while len(paragraph) > 0:
                # Pegar um trecho que caiba na linha
                line = paragraph[:line_length]
                paragraph = paragraph[line_length:]
                
                # Adicionar a linha ao PDF
                c.drawString(margin_left, y_position, line.strip())
                y_position -= line_spacing
                
                # Se chegar ao final da página, criar uma nova
                if y_position < 50:
                    c.showPage()
                    c.setFont("Helvetica", 12)
                    y_position = margin_top

        # Salvar o PDF
        c.save()
        
        # Excluir o arquivo de áudio temporário
        os.remove(audio_path)
        
        # Incrementar o contador para o próximo arquivo
        contador += 1

print(f"Transcrições concluídas e salvas como PDFs na pasta '{pdf_folder}'.")
