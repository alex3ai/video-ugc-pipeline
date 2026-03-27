import os
import time
import logging
from gradio_client import Client
from moviepy.editor import VideoFileClip, concatenate_videoclips


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_and_combine_videos(prompt, huggingface_token, output_filename="video_final_wan21_10s.mp4"):
    """
    Gera dois vídeos de 5 segundos cada usando o modelo Wan2.1 do Hugging Face e os combina
    com uma transição de 1s (crossfade).
    
    Args:
        prompt (str): Prompt para gerar os vídeos
        huggingface_token (str): Token do Hugging Face
        output_filename (str): Nome do arquivo de saída para o vídeo combinado
    """
    # Criar cliente para o modelo Wan-AI/Wan2.1
    client = Client('Wan-AI/Wan2.1', hf_token=huggingface_token)
    
    videos_to_cleanup = []

    # Primeira geração de vídeo
    logger.info("Gerando primeiro clipe de 5 segundos...")
    result_1 = client.predict(
        prompt,
        "1280*720",
        True,  # watermark_wan
        -1,    # seed
        api_name='/t2v_generation_async'
    )

    # Exibir tempo estimado de espera
    if result_1 and len(result_1) > 0:
        estimated_time = result_1[0].get('estimated_waiting_time', 'desconhecido')
        logger.info(f'Tempo estimado de espera: {estimated_time}')

    # Monitorar até que o vídeo esteja pronto
    video_path_1 = None
    while True:
        status_result = client.predict(api_name='/status_refresh')
        if status_result and len(status_result) > 0 and status_result[0]['video']:
            video_url_1 = status_result[0]['video']
            video_path_1 = "temp_video_1.mp4"
            
            # Baixar o vídeo para um arquivo local
            import requests
            response = requests.get(video_url_1)
            with open(video_path_1, 'wb') as f:
                f.write(response.content)
            
            logger.info("Primeiro clipe gerado com sucesso!")
            videos_to_cleanup.append(video_path_1)
            break
        else:
            logger.info("Aguardando geração do primeiro clipe...")
            time.sleep(5)

    # Segunda geração de vídeo
    logger.info("Gerando segundo clipe de 5 segundos...")
    second_prompt = f"{prompt} with different perspective"
    result_2 = client.predict(
        second_prompt,
        "1280*720",
        True,  # watermark_wan
        -1,    # seed
        api_name='/t2v_generation_async'
    )

    # Exibir tempo estimado de espera
    if result_2 and len(result_2) > 0:
        estimated_time = result_2[0].get('estimated_waiting_time', 'desconhecido')
        logger.info(f'Tempo estimado de espera: {estimated_time}')

    # Monitorar até que o vídeo esteja pronto
    video_path_2 = None
    while True:
        status_result = client.predict(api_name='/status_refresh')
        if status_result and len(status_result) > 0 and status_result[0]['video']:
            video_url_2 = status_result[0]['video']
            video_path_2 = "temp_video_2.mp4"
            
            # Baixar o vídeo para um arquivo local
            import requests
            response = requests.get(video_url_2)
            with open(video_path_2, 'wb') as f:
                f.write(response.content)
            
            logger.info("Segundo clipe gerado com sucesso!")
            videos_to_cleanup.append(video_path_2)
            break
        else:
            logger.info("Aguardando geração do segundo clipe...")
            time.sleep(5)

    # Carregar os clipes de vídeo
    clip1 = VideoFileClip(video_path_1)
    clip2 = VideoFileClip(video_path_2)
    
    # Aplicar crossfadein(1) no segundo clipe para uma transição suave
    clip2_with_fade = clip2.crossfadein(1)

    # Combinar os clipes
    final_clip = concatenate_videoclips([clip1, clip2_with_fade])

    # Exportar o vídeo final
    final_clip.write_videofile(output_filename, codec="libx264", audio_codec="aac")

    # Fechar os clipes para liberar recursos
    clip1.close()
    clip2.close()
    final_clip.close()

    # Limpar arquivos temporários
    for temp_video in videos_to_cleanup:
        if os.path.exists(temp_video):
            os.remove(temp_video)
            logger.info(f"Arquivo temporário removido: {temp_video}")

    logger.info(f"Vídeo final de 10 segundos salvo como: {output_filename}")


def main():
    # Exemplo de uso
    prompt = "A beautiful landscape with mountains and sunset, cinematic, 4k quality"
    
    # Obter token do Hugging Face das variáveis de ambiente
    huggingface_token = os.getenv("HF_API_KEY") or os.getenv("HUGGINGFACE_TOKEN")
    
    if not huggingface_token:
        print("Erro: É necessário fornecer um token do Hugging Face nas variáveis de ambiente como HF_API_KEY ou HUGGINGFACE_TOKEN")
        print("Nunca faça hardcode do token no código!")
        return

    generate_and_combine_videos(prompt, huggingface_token)


if __name__ == "__main__":
    main()