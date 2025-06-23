from pydantic import BaseSettings, AnyHttpUrl, Field

class Settings(BaseSettings):
    # URL base da B3
    B3_BASE_URL: AnyHttpUrl = Field(
        "https://sistemaswebb3-listados.b3.com.br",
        env="B3_BASE_URL",
    )
    # Caminho específico para dados do IBOV
    IBOV_PATH: str = Field(
        "/indexPage/day/IBOV",
        env="IBOV_PATH",
    )

    # Tamanho da página de dados do IBOV
    PAGE_SIZE: int = Field(120, env="PAGE_SIZE")
    # Nome do índice para consulta no endpoint JSON (por ex. "IBOV")
    INDEX: str = Field("IBOV", env="INDEX")
    # Segmento de mercado para consulta no endpoint JSON (por ex. "1")
    SEGMENT: str = Field("1", env="SEGMENT")

    # Bucket S3 onde os dados serão persistidos
    S3_BUCKET: str = Field(..., env="S3_BUCKET")
    # Região AWS para o bucket
    AWS_REGION: str = Field("us-east-1", env="AWS_REGION")
    # Chaves de acesso AWS para autenticação programática
    AWS_ACCESS_KEY_ID: str = Field(..., env="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str = Field(..., env="AWS_SECRET_ACCESS_KEY")
    # Timeout de requisição em segundos
    TIMEOUT: int = Field(10, env="TIMEOUT")
    # Prefixo de pasta dentro do bucket S3
    S3_PREFIX: str = Field("raw/ibov", env="S3_PREFIX")

    class Config:
        # Arquivo de variáveis de ambiente default
        env_file = ".env.default"
        env_file_encoding = "utf-8"

# Instância única para uso em toda a aplicação
settings = Settings()