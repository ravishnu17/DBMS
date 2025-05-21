from pydantic_settings import BaseSettings, SettingsConfigDict
    
# env variable access code here
class Secret(BaseSettings):
    database: str
    dbuser: str
    password: str
    host: str
    port: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    s_admin_role:int
    s_admin_id:int
    s_key:str
    admin_role:int
    migrant_role:int
    profile_url: str
    model_config= SettingsConfigDict(env_file=".env")
    
secret= Secret()

