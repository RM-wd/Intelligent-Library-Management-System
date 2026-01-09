#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DeepSeek API测试脚本
用于测试API配置是否正确
"""

from deepseek_service import get_deepseek_service

def test_deepseek():
    """测试DeepSeek服务"""
    print("=" * 50)
    print("DeepSeek API 测试")
    print("=" * 50)
    
    # 获取服务实例
    service = get_deepseek_service()
    
    # 检查服务是否可用
    print(f"\n1. 检查服务配置:")
    print(f"   API密钥: {'已配置' if service.api_key else '未配置'}")
    if service.api_key:
        print(f"   API密钥(前10位): {service.api_key[:10]}...")
    print(f"   API地址: {service.base_url}")
    print(f"   模型: {service.model}")
    print(f"   超时: {service.timeout}秒")
    
    is_available = service.is_available()
    print(f"\n   服务状态: {'可用' if is_available else '不可用'}")
    
    if not is_available:
        print("\n❌ 服务不可用，请检查配置")
        return False
    
    # 测试简单对话
    print(f"\n2. 测试API调用:")
    test_message = "你好，请介绍一下你自己"
    print(f"   测试消息: {test_message}")
    
    try:
        reply = service.chat(test_message, role="reader")
        if reply:
            print(f"\n✅ API调用成功!")
            print(f"   回复: {reply[:200]}...")
            return True
        else:
            print(f"\n❌ API调用失败: 返回空回复")
            return False
    except Exception as e:
        print(f"\n❌ API调用异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_deepseek()
    print("\n" + "=" * 50)
    if success:
        print("✅ 测试通过！DeepSeek API配置正确")
    else:
        print("❌ 测试失败！请检查配置和网络连接")
    print("=" * 50)

