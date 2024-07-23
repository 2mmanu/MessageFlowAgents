from pydantic import Field, KafkaDsn, RedisDsn, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class BlackboardSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    dns: RedisDsn = Field(default="redis://localhost:6379/0")
    redis_pwd: SecretStr


class ChannelsSettings(BaseSettings):
    dns: KafkaDsn = Field(default="kafka://localhost:9092")
    ch_sys_name: str = Field(default="sys-channel")
    ch_knw_name: str = Field(default="knw-channel")
    ch_req_name: str = Field(default="req-channel")


class BusSettings(BaseSettings):
    blackboard: BlackboardSettings = Field(default=BlackboardSettings())
    channels: ChannelsSettings = Field(default=ChannelsSettings())
