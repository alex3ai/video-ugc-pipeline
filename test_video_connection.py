import os
import sys
from pathlib import Path
import traceback

# Adicionando o diretório raiz ao path para importar módulos
sys.path.insert(0, str(Path(__file__).parent))

try:
    from config import settings
    from services.video_service.video_service import (
        _authenticate_huggingface,
        validate_hf_space_access,
        check_space_status,
        test_video_api_connection
    )

    def main():
        print("Testando conexão com o provedor de vídeo...")
        print(f"Modelo configurado: {settings.HF_SPACE_MODEL}")
        print(f"Token disponível: {'Sim' if os.getenv('HF_TOKEN') or os.getenv('HF_API_KEY') else 'Não'}")
        
        # Teste 1: autenticação (whoami) — já funciona, manter.
        print("\n1. Testando autenticação no Hugging Face...")
        token = _authenticate_huggingface()
        if not token:
            print("✗ Falha na autenticação - token não encontrado")
            return False
        else:
            print("✓ Autenticação realizada com sucesso")
        
        # Teste 2: verificar se o Space existe com repo_type="space".
        print("\n2. Testando acesso ao Space...")
        if validate_hf_space_access(settings.HF_SPACE_MODEL):
            print("✓ Space acessível")
        else:
            print("✗ Falha ao acessar o Space")
            return False
        
        # Teste 3: verificar status de runtime do Space
        print("\n3. Verificando status do Space...")
        status = check_space_status(settings.HF_SPACE_MODEL)
        if status:
            print(f"✓ Status do Space: {status}")
            
            if status == "Sleeping":
                print("  - O Space está dormindo, será ativado automaticamente quando necessário")
            elif status == "Building":
                print("  - O Space está sendo construído, aguarde antes de tentar gerar vídeos")
            elif status == "Running":
                print("  - O Space está ativo e pronto para uso")
            else:
                print(f"  - O Space está em estado: {status}")
        else:
            print("✗ Não foi possível obter o status do Space")
            return False
        
        # Teste 4: testar uma chamada de geração simples com prompt curto
        print("\n4. Testando conexão com API de vídeo...")
        if test_video_api_connection():
            print("✓ Conexão com API de vídeo bem-sucedida")
            print("\nTodos os testes passaram! O provedor de vídeo está configurado corretamente.")
            return True
        else:
            print("✗ Falha na conexão com a API de vídeo")
            return False

    if __name__ == "__main__":
        success = main()
        if not success:
            print("\nFalha nos testes de conexão. Por favor, verifique sua configuração.")
            sys.exit(1)
        else:
            print("\nTestes concluídos com sucesso!")
except Exception as e:
    print(f"Ocorreu um erro ao tentar importar os módulos ou executar o teste: {e}")
    traceback.print_exc()