# 系统配置文件
import os
from typing import Optional


class Config:
    """应用配置类"""
    
    # Flask配置
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # 数据库配置
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '123456')
    DB_NAME = os.environ.get('DB_NAME', 'library')
    DB_CHARSET = os.environ.get('DB_CHARSET', 'utf8')
    
    # DeepSeek API配置
    # 优先使用环境变量，如果没有则使用默认密钥（开发环境）
    DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', 'sk-9771ea2c242b4ac69186b8fdf767fcec')
    DEEPSEEK_API_URL = os.environ.get('DEEPSEEK_API_URL', 'https://api.deepseek.com/v1/chat/completions')
    DEEPSEEK_MODEL = os.environ.get('DEEPSEEK_MODEL', 'deepseek-chat')
    DEEPSEEK_TIMEOUT = int(os.environ.get('DEEPSEEK_TIMEOUT', '30'))
    
    @staticmethod
    def init_app(app):
        """初始化应用配置"""
        pass


# 开发环境配置
class DevelopmentConfig(Config):
    DEBUG = True


# 生产环境配置
class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'change-this-secret-key-in-production'


# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

