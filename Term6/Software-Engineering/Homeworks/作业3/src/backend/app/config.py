from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "mysql+pymysql://root:root@localhost:3306/charging_station"
    SECRET_KEY: str = "bupt-charging-station-secret-key-2025"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    FAST_CHARGING_PILE_NUM: int = 3
    TRICKLE_CHARGING_PILE_NUM: int = 2
    WAITING_AREA_SIZE: int = 6
    CHARGING_QUEUE_LEN: int = 2

    PEAK_RATE: float = 1.0
    NORMAL_RATE: float = 0.7
    VALLEY_RATE: float = 0.4
    SERVICE_RATE: float = 0.8

    class Config:
        env_file = ".env"


settings = Settings()
