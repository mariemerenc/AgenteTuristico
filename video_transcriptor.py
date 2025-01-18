from moviepy.editor import *
import whisper
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# Caminho da pasta principal com as subpastas de vídeos e onde os PDFs serão salvos
videos_root_folder = "pasta_com_videos"  # Pasta principal contendo as subpastas por cidade
pdf_root_folder = "pdf"  # Pasta principal para salvar os PDFs

# Criar a pasta PDF principal, caso não exista
if not os.path.exists(pdf_root_folder):
    os.makedirs(pdf_root_folder)

# Carregar o modelo Whisper
modelo = whisper.load_model("base")

# Configurações da página PDF
page_width, page_height = letter
margin_left = 50
margin_top = 750
line_spacing = 14
line_length = 90  # Limite de caracteres por linha (ajuste conforme necessário)

# Iterar pelas subpastas dentro da pasta principal de vídeos
for city_folder in os.listdir(videos_root_folder):
    city_path = os.path.join(videos_root_folder, city_folder)
    
    if os.path.isdir(city_path):  # Verificar se é uma pasta (cidade)
        # Criar a subpasta correspondente na pasta PDF
        city_pdf_folder = os.path.join(pdf_root_folder, city_folder)
        if not os.path.exists(city_pdf_folder):
            os.makedirs(city_pdf_folder)
        
        # Contador para nomear os arquivos de transcrição dentro da cidade
        contador = 1
        
        # Iterar pelos arquivos de vídeo dentro da subpasta da cidade
        for video_filename in os.listdir(city_path):
            if video_filename.endswith(('.mp4', '.avi', '.mov')):  # Filtrar apenas arquivos de vídeo
                # Caminho completo do arquivo de vídeo
                video_path = os.path.join(city_path, video_filename)
                
                # Carregar o vídeo
                video = VideoFileClip(video_path)
                
                # Extrair áudio do vídeo e salvar como um arquivo WAV temporário
                audio_path = "audio_extraido.wav"
                video.audio.write_audiofile(audio_path, codec='pcm_s16le')
                
                # Transcrever o áudio
                result = modelo.transcribe(audio_path)
                
                # Nome do arquivo PDF
                pdf_filename = f"transcription_{contador}.pdf"
                pdf_path = os.path.join(city_pdf_folder, pdf_filename)
                
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

print(f"Transcrições concluídas e salvas como PDFs na pasta '{pdf_root_folder}'.")
