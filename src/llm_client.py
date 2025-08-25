#!/usr/bin/env python3
# llm_client.py
import httpx
import requests
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import json
import yaml

class LLMProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    LOCAL = "local"

@dataclass
class LLMConfig:
    """LLM設定"""
    provider: LLMProvider
    api_url: str
    api_key: Optional[str] = None
    model: str = "default"
    max_tokens: int = 2000
    temperature: float = 0.7
    timeout: int = 30
    max_retries: int = 3
    system_prompt: Optional[str] = None

class LLMClient:
    """LLM APIクライアント"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.client = httpx.Client(
            timeout=config.timeout,
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)
        )
        self.cache = {}
        self.rate_limiter = RateLimiter(config.max_requests_per_minute if hasattr(config, 'max_requests_per_minute') else 60)
        self.health_checker = HealthChecker(config.health_check_timeout if hasattr(config, 'health_check_timeout') else 5)
        self.endpoint_manager = FallbackEndpointManager(config.provider)
        
        # エンドポイントの初期化
        if hasattr(config, 'endpoints') and config.endpoints:
            for endpoint_config in config.endpoints:
                self.endpoint_manager.add_endpoint(
                    endpoint_config['url'], 
                    endpoint_config.get('priority', 1)
                )
    
    def generate_config(self, prompt: str) -> str:
        """コンフィグを生成"""
        try:
            # キャッシュチェック
            prompt_hash = self._generate_prompt_hash(prompt)
            if self._is_cache_enabled() and prompt_hash in self.cache:
                return self.cache[prompt_hash]
            
            # レートリミットチェック
            self.rate_limiter.wait_if_needed()
            
            # 健康チェックとエンドポイント選択
            endpoint = self.endpoint_manager.get_primary_endpoint()
            if not endpoint:
                raise Exception("No healthy endpoints available")
            
            # プロバイダーに応じたAPI呼び出し
            if self.config.provider == LLMProvider.OPENAI:
                response = self._call_openai_api_with_endpoint(prompt, endpoint)
            elif self.config.provider == LLMProvider.ANTHROPIC:
                response = self._call_anthropic_api_with_endpoint(prompt, endpoint)
            elif self.config.provider == LLMProvider.OLLAMA:
                response = self._call_ollama_api_with_endpoint(prompt, endpoint)
            elif self.config.provider == LLMProvider.LOCAL:
                response = self._call_local_api_with_endpoint(prompt, endpoint)
            else:
                raise ValueError(f"Unsupported provider: {self.config.provider}")
            
            # キャッシュに保存
            if self._is_cache_enabled():
                self.cache[prompt_hash] = response
            
            # 使用量監視
            self._track_usage(len(prompt), len(response))
            
            return response
            
        except Exception as e:
            # フォールバックエンドポイントの試行
            if self.config.enable_fallback:
                return self._try_fallback_endpoints(prompt)
            else:
                # フォールバックとしてダミーコンフィグを生成
                return self._generate_fallback_config(prompt)
    
    def _call_openai_api(self, prompt: str) -> str:
        """OpenAI APIを呼び出す"""
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        messages = []
        if self.config.system_prompt:
            messages.append({"role": "system", "content": self.config.system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        data = {
            "model": self.config.model,
            "messages": messages,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature
        }
        
        response = self.client.post(
            f"{self.config.api_url}/chat/completions",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            raise Exception(f"OpenAI API error: {response.status_code}")
    
    def _call_anthropic_api(self, prompt: str) -> str:
        """Anthropic APIを呼び出す"""
        headers = {
            "x-api-key": self.config.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": self.config.model,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        response = self.client.post(
            f"{self.config.api_url}/v1/messages",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            return response.json()["content"][0]["text"]
        else:
            raise Exception(f"Anthropic API error: {response.status_code}")
    
    def _call_ollama_api(self, prompt: str) -> str:
        """Ollama APIを呼び出す"""
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.config.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.config.temperature,
                "num_predict": self.config.max_tokens
            }
        }
        
        if self.config.system_prompt:
            data["system"] = self.config.system_prompt
        
        response = self.client.post(
            f"{self.config.api_url}/api/generate",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            return response.json().get("response", "")
        else:
            raise Exception(f"Ollama API error: {response.status_code}")
    
    def _call_local_api(self, prompt: str) -> str:
        """ローカルLLM APIを呼び出す"""
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.config.model,
            "prompt": prompt,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature
        }
        
        response = self.client.post(
            self.config.api_url,
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            return response.json().get("text", "")
        else:
            raise Exception(f"Local API error: {response.status_code}")
    
    def _generate_fallback_config(self, prompt: str) -> str:
        """フォールバック用ダミーコンフィグを生成"""
        # デバイス名を抽出
        import re
        device_match = re.search(r'(R\d+|SW\d+|Router\d+|Switch\d+)', prompt)
        device_name = device_match.group(1) if device_match else "Router1"
        
        # 設定タイプを判定
        prompt_lower = prompt.lower()
        if any(keyword in prompt_lower for keyword in ['basic', '初期', '基本']):
            config_type = "basic"
        elif any(keyword in prompt_lower for keyword in ['ospf', 'ルーティング']):
            config_type = "routing"
        elif any(keyword in prompt_lower for keyword in ['vlan', 'スイッチ']):
            config_type = "switching"
        elif any(keyword in prompt_lower for keyword in ['security', 'セキュリティ']):
            config_type = "security"
        else:
            config_type = "general"
        
        # ダミーコンフィグのテンプレート
        templates = {
            "basic": f"""! {device_name} - Basic Configuration
! Generated by fallback system
! Requirements: {prompt}

! Basic Settings
hostname {device_name}
ip routing
service timestamps debug datetime msec
service timestamps log datetime msec
no ip domain-lookup
ip domain-name company.local

! Interface Configuration
interface GigabitEthernet0/0/0
 description Uplink Connection
 no shutdown
!
interface GigabitEthernet0/0/1
 description Downlink Connection
 no shutdown
!""",
            
            "routing": f"""! {device_name} - Routing Configuration
! Generated by fallback system
! Requirements: {prompt}

! Basic Settings
hostname {device_name}
ip routing
service timestamps debug datetime msec
service timestamps log datetime msec

! OSPF Configuration
router ospf 1
 router-id 10.1.1.{device_name[-1]}
 network 10.1.1.0 0.0.0.255 area 0
 passive-interface default
 no passive-interface GigabitEthernet0/0/0
 no passive-interface GigabitEthernet0/0/1
!""",
            
            "switching": f"""! {device_name} - Switching Configuration
! Generated by fallback system
! Requirements: {prompt}

! Basic Settings
hostname {device_name}
ip routing
service timestamps debug datetime msec
service timestamps log datetime msec

! VLAN Configuration
vlan 10
 name Engineering
!
vlan 20
 name Sales
!

! Interface Configuration
interface GigabitEthernet0/1
 switchport mode access
 switchport access vlan 10
!
interface GigabitEthernet0/2
 switchport mode access
 switchport access vlan 20
!""",
            
            "security": f"""! {device_name} - Security Configuration
! Generated by fallback system
! Requirements: {prompt}

! Basic Settings
hostname {device_name}
ip routing
service timestamps debug datetime msec
service timestamps log datetime msec

! Standard ACL
ip access-list standard ACL_MANAGEMENT
 permit 192.168.100.0 0.0.0.255
 deny any
!

! Interface Security
interface GigabitEthernet0/0/0
 ip access-group ACL_MANAGEMENT in
!""",
            
            "general": f"""! {device_name} - General Configuration
! Generated by fallback system
! Requirements: {prompt}

! Basic Settings
hostname {device_name}
ip routing
service timestamps debug datetime msec
service timestamps log datetime msec

! Interface Configuration
interface GigabitEthernet0/0/0
 no shutdown
!
interface GigabitEthernet0/0/1
 no shutdown
!"""
        }
        
        return templates.get(config_type, templates["general"])
    
    def get_provider_info(self) -> Dict[str, Any]:
        """プロバイダー情報を取得"""
        return {
            "provider": self.config.provider.value,
            "model": self.config.model,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "timeout": self.config.timeout,
            "endpoint": self.endpoint_manager.get_primary_endpoint() if hasattr(self, 'endpoint_manager') else None,
            "cache_enabled": self._is_cache_enabled(),
            "fallback_enabled": self.config.enable_fallback if hasattr(self.config, 'enable_fallback') else True
        }

    def _generate_prompt_hash(self, prompt: str) -> str:
        """プロンプトのハッシュを生成"""
        import hashlib
        return hashlib.md5(prompt.encode()).hexdigest()

    def _is_cache_enabled(self) -> bool:
        """キャッシュが有効かどうかを確認"""
        return hasattr(self.config, 'enable_caching') and self.config.enable_caching

    def _track_usage(self, prompt_length: int, response_length: int):
        """使用量を追跡"""
        if hasattr(self.config, 'track_tokens') and self.config.track_tokens:
            # トークン使用量の追跡（簡略化）
            pass

    def _call_openai_api_with_endpoint(self, prompt: str, endpoint: str) -> str:
        """指定されたエンドポイントでOpenAI APIを呼び出す"""
        headers = {
            "Authorization": f"Bearer {self._get_api_key_for_endpoint(endpoint)}",
            "Content-Type": "application/json"
        }
        
        messages = []
        if self.config.system_prompt:
            messages.append({"role": "system", "content": self.config.system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        data = {
            "model": self.config.model,
            "messages": messages,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature
        }
        
        response = self.client.post(
            f"{endpoint}/chat/completions",
            headers=headers,
            json=data,
            verify=self._get_ssl_verification(endpoint)
        )
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            raise Exception(f"OpenAI API error: {response.status_code}")

    def _call_anthropic_api_with_endpoint(self, prompt: str, endpoint: str) -> str:
        """指定されたエンドポイントでAnthropic APIを呼び出す"""
        headers = {
            "x-api-key": self._get_api_key_for_endpoint(endpoint),
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": self.config.model,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        response = self.client.post(
            f"{endpoint}/v1/messages",
            headers=headers,
            json=data,
            verify=self._get_ssl_verification(endpoint)
        )
        
        if response.status_code == 200:
            return response.json()["content"][0]["text"]
        else:
            raise Exception(f"Anthropic API error: {response.status_code}")

    def _call_ollama_api_with_endpoint(self, prompt: str, endpoint: str) -> str:
        """指定されたエンドポイントでOllama APIを呼び出す"""
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.config.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.config.temperature,
                "num_predict": self.config.max_tokens
            }
        }
        
        if self.config.system_prompt:
            data["system"] = self.config.system_prompt
        
        response = self.client.post(
            f"{endpoint}/api/generate",
            headers=headers,
            json=data,
            verify=self._get_ssl_verification(endpoint)
        )
        
        if response.status_code == 200:
            return response.json().get("response", "")
        else:
            raise Exception(f"Ollama API error: {response.status_code}")

    def _call_local_api_with_endpoint(self, prompt: str, endpoint: str) -> str:
        """指定されたエンドポイントでLocal LLM APIを呼び出す"""
        headers = {
            "Authorization": f"Bearer {self._get_api_key_for_endpoint(endpoint)}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.config.model,
            "prompt": prompt,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature
        }
        
        response = self.client.post(
            endpoint,
            headers=headers,
            json=data,
            verify=self._get_ssl_verification(endpoint)
        )
        
        if response.status_code == 200:
            return response.json().get("text", "")
        else:
            raise Exception(f"Local API error: {response.status_code}")

    def _get_api_key_for_endpoint(self, endpoint: str) -> str:
        """エンドポイントに対応するAPIキーを取得"""
        if hasattr(self.config, 'endpoints'):
            for endpoint_config in self.config.endpoints:
                if endpoint_config['url'] == endpoint:
                    return endpoint_config.get('api_key', self.config.api_key)
        return self.config.api_key

    def _get_ssl_verification(self, endpoint: str) -> bool:
        """エンドポイントに対応するSSL検証設定を取得"""
        if hasattr(self.config, 'endpoints'):
            for endpoint_config in self.config.endpoints:
                if endpoint_config['url'] == endpoint:
                    return endpoint_config.get('verify_ssl', True)
        return True

    def _try_fallback_endpoints(self, prompt: str) -> str:
        """フォールバックエンドポイントを試行"""
        fallback_endpoints = self.endpoint_manager.get_fallback_endpoints()
        
        for endpoint in fallback_endpoints:
            try:
                # エンドポイントの健康状態をチェック
                if not self.health_checker.check_endpoint(endpoint):
                    continue
                
                # プロバイダーに応じたAPI呼び出し
                if self.config.provider == LLMProvider.OPENAI:
                    return self._call_openai_api_with_endpoint(prompt, endpoint)
                elif self.config.provider == LLMProvider.ANTHROPIC:
                    return self._call_anthropic_api_with_endpoint(prompt, endpoint)
                elif self.config.provider == LLMProvider.OLLAMA:
                    return self._call_ollama_api_with_endpoint(prompt, endpoint)
                elif self.config.provider == LLMProvider.LOCAL:
                    return self._call_local_api_with_endpoint(prompt, endpoint)
                    
            except Exception as e:
                # エンドポイントを不健康としてマーク
                self.endpoint_manager.update_endpoint_health(endpoint, False)
                continue
        
        # すべてのフォールバックエンドポイントが失敗した場合
        return self._generate_fallback_config(prompt)
    
    def validate_config(self, config: str) -> Dict[str, Any]:
        """生成されたコンフィグを検証"""
        validation_prompt = f"""
以下のネットワーク設定を検証してください:
{config}

検証項目:
1. 構文エラーの有無
2. 設定の一貫性
3. セキュリティ上の問題
4. ベストプラクティス違反

JSON形式で結果を返してください:
{{
    "is_valid": true/false,
    "errors": ["error1", "error2"],
    "warnings": ["warning1", "warning2"],
    "suggestions": ["suggestion1", "suggestion2"]
}}
"""
        
        try:
            validation_result = self.generate_config(validation_prompt)
            # 簡易的なJSONパース（実際にはより堅牢なパーサーを使用）
            return {"is_valid": True, "validation_text": validation_result}
        except Exception as e:
            return {"is_valid": False, "error": str(e)}
    
    def get_provider_info(self) -> Dict[str, Any]:
        """プロバイダー情報を取得"""
        return {
            "provider": self.config.provider.value,
            "model": self.config.model,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "timeout": self.config.timeout,
            "endpoint": self.endpoint_manager.get_primary_endpoint() if hasattr(self, 'endpoint_manager') else None,
            "cache_enabled": self._is_cache_enabled(),
            "fallback_enabled": self.config.enable_fallback if hasattr(self.config, 'enable_fallback') else True
        }
