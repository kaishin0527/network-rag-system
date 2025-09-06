#!/usr/bin/env python3
# llm_integration.py
from .llm_client import LLMClient, LLMConfig, LLMProvider
from typing import Dict, Any, List, Optional
import json
from dataclasses import dataclass
from datetime import datetime
import yaml


@dataclass
class GenerationRequest:
    """生成リクエスト"""

    query: str
    device_name: str
    config_type: str
    context: Optional[Dict[str, Any]] = None
    temperature: float = 0.7
    max_tokens: int = 2000


class LLMIntegration:
    """LLM APIとの統合クラス"""

    def __init__(self, config_path: str = "config/openhands_config.yaml"):
        self.config = self._load_config(config_path)
        self.client = self._create_llm_client()
        self.request_history: List[Dict[str, Any]] = []

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """設定ファイルの読み込み"""
        try:
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)
                return config if config is not None else {}
        except FileNotFoundError:
            return {}

    def _create_llm_client(self) -> LLMClient:
        """LLMクライアントを作成"""
        llm_config = self.config.get("llm", {})
        connection_config = llm_config.get("connection", {})

        # Local LLM (Ollama) を優先的に使用
        if llm_config.get("local", {}).get("enabled", False):
            local_config = llm_config["local"]
            config = LLMConfig(
                provider=LLMProvider.OLLAMA,
                api_url=local_config.get("api_url", "http://localhost:11434"),
                api_key=self._resolve_env_var(local_config.get("api_key")),
                model=local_config.get("model", "llama2"),
                max_tokens=local_config.get("max_tokens", 2000),
                temperature=local_config.get("temperature", 0.7),
                timeout=local_config.get("timeout", 60),
                system_prompt=local_config.get("system_prompt"),
                max_requests_per_minute=connection_config.get(
                    "rate_limit_per_minute", 60
                ),
                health_check_timeout=connection_config.get("health_check_timeout", 5),
                enable_fallback=connection_config.get("enable_fallback", True),
                enable_caching=connection_config.get("enable_caching", True),
                endpoints=self._process_endpoints(local_config.get("endpoints", [])),
                verify_ssl=local_config.get("verify_ssl", True),
            )
            return LLMClient(config)

        # OpenAI設定
        elif llm_config.get("openai", {}).get("enabled", False):
            openai_config = llm_config["openai"]
            config = LLMConfig(
                provider=LLMProvider.OPENAI,
                api_url=openai_config.get("api_url", "https://api.openai.com/v1"),
                api_key=self._resolve_env_var(openai_config.get("api_key")),
                model=openai_config.get("model", "gpt-4"),
                max_tokens=openai_config.get("max_tokens", 2000),
                temperature=openai_config.get("temperature", 0.7),
                timeout=openai_config.get("timeout", 30),
                max_requests_per_minute=connection_config.get(
                    "rate_limit_per_minute", 60
                ),
                health_check_timeout=connection_config.get("health_check_timeout", 5),
                enable_fallback=connection_config.get("enable_fallback", True),
                enable_caching=connection_config.get("enable_caching", True),
                endpoints=self._process_endpoints(openai_config.get("endpoints", [])),
                verify_ssl=openai_config.get("verify_ssl", True),
            )
            return LLMClient(config)

        # Anthropic設定
        elif llm_config.get("anthropic", {}).get("enabled", False):
            anthropic_config = llm_config["anthropic"]
            config = LLMConfig(
                provider=LLMProvider.ANTHROPIC,
                api_url=anthropic_config.get("api_url", "https://api.anthropic.com"),
                api_key=self._resolve_env_var(anthropic_config.get("api_key")),
                model=anthropic_config.get("model", "claude-3-sonnet-20240229"),
                max_tokens=anthropic_config.get("max_tokens", 2000),
                temperature=anthropic_config.get("temperature", 0.7),
                timeout=anthropic_config.get("timeout", 30),
                max_requests_per_minute=connection_config.get(
                    "rate_limit_per_minute", 60
                ),
                health_check_timeout=connection_config.get("health_check_timeout", 5),
                enable_fallback=connection_config.get("enable_fallback", True),
                enable_caching=connection_config.get("enable_caching", True),
                endpoints=self._process_endpoints(
                    anthropic_config.get("endpoints", [])
                ),
                verify_ssl=anthropic_config.get("verify_ssl", True),
            )
            return LLMClient(config)

        # デフォルト：Ollama
        else:
            config = LLMConfig(
                provider=LLMProvider.OLLAMA,
                api_url="http://localhost:11434",
                model="llama2",
                max_tokens=2000,
                temperature=0.7,
                timeout=60,
                system_prompt="You are a network configuration expert specializing in Cisco IOS, IOS-XE, and IOS-XR devices.",
                max_requests_per_minute=60,
                health_check_timeout=5,
                enable_fallback=True,
                enable_caching=True,
                verify_ssl=True,
            )
            return LLMClient(config)

    def _resolve_env_var(self, value: Optional[str]) -> Optional[str]:
        """環境変数を解決"""
        if not value:
            return None

        import os

        if value.startswith("${") and value.endswith("}"):
            env_var = value[2:-1]
            default_value = None
            if ":" in env_var:
                env_var, default_value = env_var.split(":", 1)
            return os.getenv(env_var, default_value)
        return value

    def _process_endpoints(
        self, endpoints: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """エンドポイント設定を処理"""
        processed_endpoints = []
        for endpoint in endpoints:
            processed_endpoint = {
                "url": endpoint["url"],
                "priority": endpoint.get("priority", 1),
                "verify_ssl": endpoint.get("verify_ssl", True),
                "api_key": self._resolve_env_var(endpoint.get("api_key")),
            }
            processed_endpoints.append(processed_endpoint)
        return processed_endpoints

    def generate_network_config(self, request: GenerationRequest) -> Dict[str, Any]:
        """ネットワークコンフィグを生成"""
        try:
            # プロンプトの生成
            prompt = self._generate_prompt(request)

            # コンフィグの生成
            config_content = self.client.generate_config(prompt)

            # 検証
            validation_result = self.client.validate_config(config_content)

            # リクエストの記録
            self.request_history.append(
                {
                    "query": request.query,
                    "device_name": request.device_name,
                    "config_type": request.config_type,
                    "timestamp": datetime.now().isoformat(),
                    "success": validation_result["is_valid"],
                    "provider": self.client.get_provider_info(),
                }
            )

            return {
                "device_name": request.device_name,
                "config_type": request.config_type,
                "config_content": config_content,
                "validation_result": validation_result,
                "metadata": {
                    "generation_time": datetime.now().isoformat(),
                    "provider_info": self.client.get_provider_info(),
                    "temperature": request.temperature,
                    "max_tokens": request.max_tokens,
                },
            }

        except Exception as e:
            return {
                "device_name": request.device_name,
                "config_type": request.config_type,
                "error": str(e),
                "validation_result": {"is_valid": False, "error": str(e)},
                "metadata": {
                    "generation_time": datetime.now().isoformat(),
                    "provider_info": self.client.get_provider_info(),
                },
            }

    def _generate_prompt(self, request: GenerationRequest) -> str:
        """プロンプトを生成"""
        template = f"""
ネットワーク設定生成タスク:

デバイス名: {request.device_name}
設定タイプ: {request.config_type}
クエリ: {request.query}

{self._format_context(request.context)}

上記の情報を基に、{request.device_name}の{request.config_type}設定を生成してください。
設定はCisco IOS形式で、以下の構造に従ってください:

1. 基本設定 (hostname, ip routing, etc.)
2. インターフェース設定
3. プロトコル設定 (OSPF, BGP, etc.)
4. セキュリティ設定
5. 監視設定

変数 {{hostname}} は {request.device_name} に置換してください。
"""
        return template

    def _format_context(self, context: Optional[Dict[str, Any]]) -> str:
        """コンテキストを整形"""
        if not context:
            return "追加情報はありません。"

        formatted = []
        if "relevant_devices" in context:
            formatted.append(f"関連デバイス: {', '.join(context['relevant_devices'])}")
        if "relevant_policies" in context:
            formatted.append(f"関連ポリシー: {', '.join(context['relevant_policies'])}")
        if "relevant_templates" in context:
            formatted.append(
                f"関連テンプレート: {', '.join(context['relevant_templates'])}"
            )

        return "\n".join(formatted)

    def get_generation_statistics(self) -> Dict[str, Any]:
        """生成統計を取得"""
        if not self.request_history:
            return {"total": 0, "success_rate": 0}

        total = len(self.request_history)
        success = sum(1 for req in self.request_history if req["success"])

        # プロバイダー別の統計
        provider_stats = {}
        for req in self.request_history:
            provider = req["provider"]["provider"]
            if provider not in provider_stats:
                provider_stats[provider] = {"total": 0, "success": 0}
            provider_stats[provider]["total"] += 1
            if req["success"]:
                provider_stats[provider]["success"] += 1

        return {
            "total": total,
            "success": success,
            "failed": total - success,
            "success_rate": success / total,
            "provider_statistics": provider_stats,
        }

    def switch_provider(self, provider: LLMProvider) -> bool:
        """LLMプロバイダーを切り替える"""
        try:
            self.client = self._create_llm_client_for_provider(provider)
            return True
        except Exception as e:
            print(f"Failed to switch provider: {e}")
            return False

    def _create_llm_client_for_provider(self, provider: LLMProvider) -> LLMClient:
        """指定されたプロバイダー用のクライアントを作成"""
        llm_config = self.config.get("llm", {})

        if provider == LLMProvider.OLLAMA:
            config = llm_config.get("local", {})
            client_config = LLMConfig(
                provider=provider,
                api_url=config.get("api_url", "http://localhost:11434"),
                model=config.get("model", "llama2"),
                max_tokens=config.get("max_tokens", 2000),
                temperature=config.get("temperature", 0.7),
                timeout=config.get("timeout", 60),
                system_prompt=config.get("system_prompt"),
            )
            return LLMClient(client_config)
        elif provider == LLMProvider.OPENAI:
            config = llm_config.get("openai", {})
            client_config = LLMConfig(
                provider=provider,
                api_url=config.get("api_url", "https://api.openai.com/v1"),
                api_key=config.get("api_key"),
                model=config.get("model", "gpt-4"),
                max_tokens=config.get("max_tokens", 2000),
                temperature=config.get("temperature", 0.7),
                timeout=config.get("timeout", 30),
            )
            return LLMClient(client_config)
        elif provider == LLMProvider.ANTHROPIC:
            config = llm_config.get("anthropic", {})
            client_config = LLMConfig(
                provider=provider,
                api_url=config.get("api_url", "https://api.anthropic.com"),
                api_key=config.get("api_key"),
                model=config.get("model", "claude-3-sonnet-20240229"),
                max_tokens=config.get("max_tokens", 2000),
                temperature=config.get("temperature", 0.7),
                timeout=config.get("timeout", 30),
            )
            return LLMClient(client_config)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def get_available_providers(self) -> List[Dict[str, Any]]:
        """利用可能なプロバイダーを取得"""
        providers = []
        llm_config = self.config.get("llm", {})

        if llm_config.get("local", {}).get("enabled", False):
            providers.append(
                {
                    "name": "ollama",
                    "display_name": "Ollama (Local)",
                    "enabled": True,
                    "description": "Local LLM running on Ollama",
                }
            )

        if llm_config.get("openai", {}).get("enabled", False):
            providers.append(
                {
                    "name": "openai",
                    "display_name": "OpenAI",
                    "enabled": True,
                    "description": "OpenAI GPT models",
                }
            )

        if llm_config.get("anthropic", {}).get("enabled", False):
            providers.append(
                {
                    "name": "anthropic",
                    "display_name": "Anthropic",
                    "enabled": True,
                    "description": "Anthropic Claude models",
                }
            )

        return providers
