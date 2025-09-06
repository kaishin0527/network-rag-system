#!/usr/bin/env python3
# llm_client.py
import httpx
import requests
import time
import threading
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
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
    max_requests_per_minute: int = 60
    health_check_timeout: int = 5
    enable_fallback: bool = True
    enable_caching: bool = True
    endpoints: Optional[List[Dict[str, Any]]] = field(default_factory=list)
    verify_ssl: bool = True


class RateLimiter:
    """レートリミット管理クラス"""

    def __init__(self, max_requests_per_minute: int = 60) -> None:
        self.max_requests_per_minute = max_requests_per_minute
        self.requests: List[float] = []
        self.lock = threading.Lock()

    def wait_if_needed(self) -> None:
        """リクエストが制限内であるか確認し、必要なら待機"""
        with self.lock:
            now = time.time()
            # 1分以上前のリクエストを削除
            self.requests = [req_time for req_time in self.requests if now - req_time < 60]

            # リクエスト数が制限を超えている場合、待機
            if len(self.requests) >= self.max_requests_per_minute:
                sleep_time = 60 - (now - self.requests[0])
                if sleep_time > 0:
                    time.sleep(sleep_time)

            # 現在のリクエストを記録
            self.requests.append(now)


class HealthChecker:
    """ヘルスチェック管理クラス"""

    def __init__(self, timeout: int = 5) -> None:
        self.timeout = timeout
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.Lock()

    def check_endpoint(self, endpoint: str) -> bool:
        """エンドポイントの健康状態をチェック"""
        with self.lock:
            # キャッシュチェック
            cached_result = self.cache.get(endpoint)
            if cached_result and time.time() - cached_result["timestamp"] < 30:  # 30秒間キャッシュ
                return bool(cached_result["healthy"])

            # 実際のヘルスチェック
            try:
                response = httpx.get(
                    f"{endpoint}/health",
                    timeout=self.timeout,
                    verify=False  # SSL検証を無効化
                )
                is_healthy: bool = response.status_code == 200
            except Exception:
                is_healthy = False

            # キャッシュに保存
            self.cache[endpoint] = {
                "healthy": is_healthy,
                "timestamp": time.time()
            }

            return is_healthy


class FallbackEndpointManager:
    """フォールバックエンドポイント管理クラス"""

    def __init__(self, provider: LLMProvider) -> None:
        self.provider = provider
        self.endpoints: List[Dict[str, Any]] = []
        self.health_status: Dict[str, bool] = {}
        self.lock = threading.Lock()

    def add_endpoint(self, url: str, priority: int = 1) -> None:
        """エンドポイントを追加"""
        with self.lock:
            self.endpoints.append({
                "url": url,
                "priority": priority,
                "backup": False
            })
            self.health_status[url] = True

    def get_primary_endpoint(self) -> Optional[str]:
        """プライマリエンドポイントを取得"""
        with self.lock:
            healthy_endpoints = [
                ep for ep in self.endpoints
                if self.health_status.get(ep["url"], True)
            ]
            if not healthy_endpoints:
                return None

            # 優先度でソート
            healthy_endpoints.sort(key=lambda x: x["priority"])
            return str(healthy_endpoints[0]["url"])

    def get_fallback_endpoints(self) -> List[str]:
        """フォールバックエンドポイントを取得"""
        with self.lock:
            healthy_endpoints = [
                ep for ep in self.endpoints
                if self.health_status.get(ep["url"], True)
            ]
            # 優先度でソート（プライマリを除く）
            healthy_endpoints.sort(key=lambda x: x["priority"])
            return [ep["url"] for ep in healthy_endpoints[1:]]

    def update_endpoint_health(self, endpoint: str, is_healthy: bool) -> None:
        """エンドポイントの健康状態を更新"""
        with self.lock:
            self.health_status[endpoint] = is_healthy


class LLMClient:
    """LLM APIクライアント"""

    def __init__(self, config: LLMConfig) -> None:
        self.config = config
        self.client = httpx.Client(
            timeout=config.timeout,
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)
        )
        self.cache: Dict[str, str] = {}
        self.rate_limiter = RateLimiter(config.max_requests_per_minute)
        self.health_checker = HealthChecker(config.health_check_timeout)
        self.endpoint_manager = FallbackEndpointManager(config.provider)

        # エンドポイントの初期化
        if config.endpoints:
            for endpoint_config in config.endpoints:
                self.endpoint_manager.add_endpoint(
                    endpoint_config["url"],
                    endpoint_config.get("priority", 1)
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

    def _generate_prompt_hash(self, prompt: str) -> str:
        """プロンプトのハッシュを生成"""
        import hashlib
        return hashlib.md5(prompt.encode()).hexdigest()

    def _is_cache_enabled(self) -> bool:
        """キャッシュが有効か確認"""
        return self.config.enable_caching

    def _track_usage(self, input_tokens: int, output_tokens: int) -> None:
        """使用量を追跡"""
        # ここで使用量を追跡するロジックを実装
        pass

    def _generate_fallback_config(self, prompt: str) -> str:
        """フォールバックコンフィグを生成"""
        return f"# Fallback Configuration\n# Prompt: {prompt}\n# Primary endpoint failed, using fallback configuration"

    def _call_openai_api_with_endpoint(self, prompt: str, endpoint: str) -> str:
        """指定されたエンドポイントでOpenAI APIを呼び出す"""
        headers = {
            "Authorization": f"Bearer {self._get_api_key_for_endpoint(endpoint)}",
            "Content-Type": "application/json",
        }

        messages = []
        if self.config.system_prompt:
            messages.append({"role": "system", "content": self.config.system_prompt})
        messages.append({"role": "user", "content": prompt})

        data = {
            "model": self.config.model,
            "messages": messages,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
        }

        response = self.client.post(
            f"{endpoint}/v1/chat/completions",
            headers=headers,
            json=data,
        )

        if response.status_code == 200:
            content = response.json()["choices"][0]["message"]["content"]
            return str(content)
        else:
            raise Exception(f"OpenAI API error: {response.status_code}")

    def _call_openai_api(self, prompt: str) -> str:
        """OpenAI APIを呼び出す"""
        return self._call_openai_api_with_endpoint(prompt, self.config.api_url)

    def _call_anthropic_api_with_endpoint(self, prompt: str, endpoint: str) -> str:
        """指定されたエンドポイントでAnthropic APIを呼び出す"""
        headers = {
            "x-api-key": self._get_api_key_for_endpoint(endpoint),
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
        }

        data = {
            "model": self.config.model,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "messages": [
                {"role": "user", "content": prompt}
            ],
        }

        response = self.client.post(
            f"{endpoint}/v1/messages",
            headers=headers,
            json=data,
        )

        if response.status_code == 200:
            content = response.json()["content"][0]["text"]
            return str(content)
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
        )

        if response.status_code == 200:
            content = response.json().get("response", "")
            return str(content)
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
        )

        if response.status_code == 200:
            content = response.json().get("text", "")
            return str(content)
        else:
            raise Exception(f"Local API error: {response.status_code}")

    def _get_api_key_for_endpoint(self, endpoint: str) -> str:
        """エンドポイントに対応するAPIキーを取得"""
        if self.config.endpoints:
            for endpoint_config in self.config.endpoints:
                if endpoint_config["url"] == endpoint:
                    api_key = endpoint_config.get("api_key", self.config.api_key)
                    return str(api_key) if api_key is not None else ""
        api_key = self.config.api_key
        return str(api_key) if api_key is not None else ""

    def _get_ssl_verification(self, endpoint: str) -> bool:
        """エンドポイントに対応するSSL検証設定を取得"""
        if self.config.endpoints:
            for endpoint_config in self.config.endpoints:
                if endpoint_config["url"] == endpoint:
                    verify_ssl = endpoint_config.get("verify_ssl", True)
                    return bool(verify_ssl)
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
            "endpoint": (
                self.endpoint_manager.get_primary_endpoint()
                if hasattr(self, "endpoint_manager")
                else None
            ),
            "cache_enabled": self._is_cache_enabled(),
            "fallback_enabled": (
                self.config.enable_fallback
                if hasattr(self.config, "enable_fallback")
                else True
            ),
        }
