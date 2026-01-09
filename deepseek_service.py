# DeepSeek大模型服务模块
import os
import json
import urllib.request
import urllib.error
from typing import Optional, List, Dict

# 导入配置
try:
    from config import Config
except ImportError:
    # 如果config模块不存在，使用默认值
    class Config:
        DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', 'sk-9771ea2c242b4ac69186b8fdf767fcec')
        DEEPSEEK_API_URL = os.environ.get('DEEPSEEK_API_URL', 'https://api.deepseek.com/v1/chat/completions')
        DEEPSEEK_MODEL = os.environ.get('DEEPSEEK_MODEL', 'deepseek-chat')
        DEEPSEEK_TIMEOUT = int(os.environ.get('DEEPSEEK_TIMEOUT', '30'))


class DeepSeekService:
    """DeepSeek API服务封装类"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        初始化DeepSeek服务
        :param api_key: API密钥，如果为None则从配置或环境变量获取
        :param base_url: API基础URL，如果为None则使用默认的DeepSeek API地址
        """
        # 优先级：参数 > 环境变量 > 配置文件
        self.api_key = api_key or os.environ.get('DEEPSEEK_API_KEY') or getattr(Config, 'DEEPSEEK_API_KEY', '')
        self.base_url = base_url or os.environ.get('DEEPSEEK_API_URL') or getattr(Config, 'DEEPSEEK_API_URL', 'https://api.deepseek.com/v1/chat/completions')
        self.model = os.environ.get('DEEPSEEK_MODEL') or getattr(Config, 'DEEPSEEK_MODEL', 'deepseek-chat')
        self.timeout = int(os.environ.get('DEEPSEEK_TIMEOUT') or getattr(Config, 'DEEPSEEK_TIMEOUT', '30'))
        
        # 调试信息
        if self.api_key:
            print(f"DeepSeek服务已初始化，API密钥: {self.api_key[:10]}...{self.api_key[-4:]}")
        else:
            print("警告: DeepSeek API密钥未配置")
    
    def is_available(self) -> bool:
        """检查服务是否可用（是否有API密钥）"""
        return bool(self.api_key and self.base_url)
    
    def chat(self, 
             message: str, 
             system_prompt: str = "",
             context: Optional[List[Dict]] = None,
             role: str = "reader") -> Optional[str]:
        """
        发送聊天请求到DeepSeek API
        
        :param message: 用户消息
        :param system_prompt: 系统提示词
        :param context: 上下文信息（如书籍数据）
        :param role: 用户角色（reader/admin）
        :return: AI回复内容，如果失败返回None
        """
        if not self.is_available():
            return None
        
        if not message or not message.strip():
            return None
        
        # 构建消息列表
        messages = []
        
        # 根据角色设置不同的系统提示词
        if role == "admin":
            default_system = "你是图书管理系统的智能助手'小灵'，专门为管理员提供帮助。你可以帮助管理员：\n" \
                            "- 回答关于图书管理的问题\n" \
                            "- 提供数据统计和分析建议\n" \
                            "- 协助处理借阅记录查询\n" \
                            "- 提供系统使用指导\n" \
                            "请用简洁、专业的中文回答。"
        else:
            default_system = "你是图书管理系统的智能助手'小灵'，专门为读者提供帮助。你可以帮助读者：\n" \
                            "- 推荐合适的图书\n" \
                            "- 回答关于图书的问题\n" \
                            "- 提供借阅建议\n" \
                            "- 解答使用问题\n" \
                            "请用友好、简洁的中文回答。"
        
        # 使用自定义系统提示词或默认提示词
        final_system_prompt = system_prompt if system_prompt else default_system
        
        # 如果有上下文信息，添加到系统提示词中
        if context:
            context_str = json.dumps(context, ensure_ascii=False, indent=2)
            final_system_prompt += f"\n\n以下是相关的图书数据（JSON格式）：\n{context_str}"
        
        messages.append({"role": "system", "content": final_system_prompt})
        messages.append({"role": "user", "content": message.strip()})
        
        # 构建请求payload
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        try:
            # 创建HTTP请求
            req = urllib.request.Request(
                self.base_url,
                data=json.dumps(payload).encode('utf-8'),
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.api_key}'
                }
            )
            
            # 发送请求
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                response_data = resp.read().decode('utf-8')
                response_obj = json.loads(response_data)
                
                # 提取回复内容
                choices = response_obj.get('choices', [])
                if choices and len(choices) > 0:
                    message_obj = choices[0].get('message', {})
                    content = message_obj.get('content', '')
                    return content if content else "抱歉，我暂时无法回答这个问题。"
                
                return "抱歉，API返回了空回复。"
                
        except urllib.error.HTTPError as e:
            error_msg = f"HTTP错误 {e.code}: {e.reason}"
            error_body = ""
            is_insufficient = False
            try:
                # 读取错误响应体
                error_body = e.read().decode('utf-8')
                print(f"DeepSeek API HTTP错误响应: {error_body}")
                try:
                    error_obj = json.loads(error_body)
                    if isinstance(error_obj, dict):
                        error_detail = error_obj.get('error', {})
                        if isinstance(error_detail, dict):
                            error_msg = error_detail.get('message', error_msg)
                        else:
                            error_msg = str(error_detail) if error_detail else error_msg
                except json.JSONDecodeError:
                    # 如果不是JSON格式，直接使用响应体
                    if error_body:
                        error_msg = error_body[:200]  # 限制长度
            except Exception as parse_error:
                print(f"读取错误响应失败: {str(parse_error)}")
            
            print(f"DeepSeek API HTTP错误: {error_msg} (状态码: {e.code})")
            
            # 检查是否是余额不足
            is_insufficient = ("Insufficient Balance" in error_msg or 
                            "余额不足" in error_msg or 
                            "insufficient" in error_msg.lower() or
                            (error_body and "insufficient" in error_body.lower()))
            
            # 对于余额不足等错误，抛出特殊异常以便app.py识别
            if is_insufficient:
                print("⚠️ 检测到余额不足(Insufficient Balance)，将使用降级方案")
                # 抛出异常，包含余额不足信息
                raise ValueError("Insufficient Balance: API余额不足")
            elif e.code == 401:
                print("API密钥无效，将使用降级方案")
                return None  # 返回None以便使用降级方案
            elif e.code == 429:
                print("请求过于频繁，将使用降级方案")
                return None  # 请求过于频繁，使用降级方案
            elif e.code >= 500:
                print("服务器错误，将使用降级方案")
                return None  # 服务器错误，使用降级方案
            else:
                # 其他错误也使用降级方案
                print(f"API调用失败，将使用降级方案: {error_msg}")
                return None
            
        except urllib.error.URLError as e:
            error_msg = f"网络连接错误: {str(e)}"
            print(f"DeepSeek API URL错误: {error_msg}")
            print("将使用降级方案")
            return None  # 网络错误，使用降级方案
            
        except json.JSONDecodeError as e:
            error_msg = f"JSON解析错误: {str(e)}"
            print(f"DeepSeek API JSON解析错误: {error_msg}")
            print("将使用降级方案")
            return None  # 解析错误，使用降级方案
            
        except Exception as e:
            error_msg = f"未知错误: {str(e)}"
            print(f"DeepSeek API 未知错误: {error_msg}")
            import traceback
            print(traceback.format_exc())
            print("将使用降级方案")
            return None  # 未知错误，使用降级方案
    
    def get_recommendations(self, 
                           preferences: Dict,
                           available_books: List[Dict]) -> Optional[str]:
        """
        获取图书推荐
        
        :param preferences: 用户偏好（包含authors和keywords）
        :param available_books: 可用图书列表
        :return: 推荐结果
        """
        system_prompt = "你是图书推荐专家。根据用户的阅读偏好和馆藏图书，推荐最合适的图书。" \
                       "请用简洁的中文列出推荐的图书，并简要说明推荐理由。"
        
        user_message = f"根据以下偏好推荐图书：\n" \
                      f"喜欢的作者：{', '.join(preferences.get('authors', []))}\n" \
                      f"关键词：{', '.join(preferences.get('keywords', []))}\n\n" \
                      f"可用图书：{json.dumps(available_books[:50], ensure_ascii=False)}"
        
        return self.chat(user_message, system_prompt=system_prompt)


# 全局服务实例
_deepseek_service = None


def get_deepseek_service() -> DeepSeekService:
    """获取全局DeepSeek服务实例（单例模式）"""
    global _deepseek_service
    if _deepseek_service is None:
        _deepseek_service = DeepSeekService()
    return _deepseek_service

