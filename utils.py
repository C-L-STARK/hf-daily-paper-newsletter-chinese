import logging
import os
from datetime import datetime

def setup_logger():
    """设置日志记录器"""
    # 创建logs目录
    os.makedirs('logs', exist_ok=True)
    
    # 创建日志记录器
    logger = logging.getLogger('HF-daily-paper')
    logger.setLevel(logging.INFO)
    
    # 创建文件处理器
    log_file = os.path.join('logs', f"{datetime.now().strftime('%Y-%m-%d')}.log")
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # 创建格式化器
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 添加处理器到日志记录器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def get_logger():
    """获取日志记录器"""
    return logging.getLogger('HF-daily-paper') 