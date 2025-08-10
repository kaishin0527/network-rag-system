


#!/usr/bin/env python3
# rag_system.py
import re
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from .knowledge_base import KnowledgeBase, DevicePolicy

@dataclass
class QueryContext:
    """クエリコンテキスト"""
    query: str
    device_name: Optional[str] = None
    requirements: Optional[str] = None
    config_type: Optional[str] = None
    priority: str = "normal"

class NetworkRAGSystem:
    def __init__(self, kb_dir: str = "/workspace/network-rag-system/knowledge-base"):
        self.kb = KnowledgeBase(kb_dir)
        self.query_history = []
    
    def retrieve_relevant_info(self, query: str) -> Dict[str, Any]:
        """関連情報の検索"""
        print(f"Retrieving relevant info for query: {query}")
        
        # クエリの解析
        context = self._parse_query(query)
        
        # 関連デバイスの検索
        relevant_devices = self._find_relevant_devices(query)
        
        # 関連ポリシーの検索
        relevant_policies = self._find_relevant_policies(query)
        
        # 関連テンプレートの検索
        relevant_templates = self._find_relevant_templates(query)
        
        # 関連検証ルールの検索
        relevant_rules = self._find_relevant_rules(query)
        
        return {
            'query_context': context,
            'relevant_devices': relevant_devices,
            'relevant_policies': relevant_policies,
            'relevant_templates': relevant_templates,
            'relevant_rules': relevant_rules,
            'network_summary': self.kb.get_network_summary()
        }
    
    def _parse_query(self, query: str) -> QueryContext:
        """クエリの解析"""
        # デバイス名の抽出
        device_name = self._extract_device_name(query)
        
        # 設定タイプの抽出
        config_type = self._extract_config_type(query)
        
        # 要件の抽出
        requirements = self._extract_requirements(query)
        
        # 優先度の抽出
        priority = self._extract_priority(query)
        
        return QueryContext(
            query=query,
            device_name=device_name,
            requirements=requirements,
            config_type=config_type,
            priority=priority
        )
    
    def _extract_device_name(self, query: str) -> Optional[str]:
        """デバイス名の抽出"""
        # クエリからデバイス名を抽出
        device_pattern = r'(?:R1|R2|SW1|router|switch)'
        match = re.search(device_pattern, query, re.IGNORECASE)
        return match.group(0).upper() if match else None
    
    def _extract_config_type(self, query: str) -> Optional[str]:
        """設定タイプの抽出"""
        config_patterns = {
            'ospf': r'ospf|ルーティング',
            'interface': r'interface|インターフェース',
            'security': r'security|セキュリティ|acl',
            'ha': r'ha|高可用性|hsrp',
            'monitoring': r'monitoring|監視'
        }
        
        for config_type, pattern in config_patterns.items():
            if re.search(pattern, query, re.IGNORECASE):
                return config_type
        
        return None
    
    def _extract_requirements(self, query: str) -> Optional[str]:
        """要件の抽出"""
        # クエリから要件部分を抽出
        requirement_pattern = r'要件|要求|必要|追加|設定'
        match = re.search(requirement_pattern, query)
        
        if match:
            # クエリ全体を要件として返す（実際にはより高度な解析が必要）
            return query
        
        return None
    
    def _extract_priority(self, query: str) -> str:
        """優先度の抽出"""
        priority_patterns = {
            'high': r'緊急|重要|high|urgent',
            'low': r'低|low|後で|later',
            'normal': r'通常|normal|一般|general'
        }
        
        for priority, pattern in priority_patterns.items():
            if re.search(pattern, query, re.IGNORECASE):
                return priority
        
        return "normal"
    
    def _find_relevant_devices(self, query: str) -> List[str]:
        """関連デバイスの検索"""
        # クエリに基づいて関連デバイスを検索
        relevant_devices = []
        
        for device_name in self.kb.list_devices():
            policy = self.kb.get_device_policy(device_name)
            if policy:
                # デバイス情報とクエリのマッチング
                device_info = f"{policy.hostname} {policy.device_type} {policy.ip_address}"
                if self._is_relevant(query, device_info):
                    relevant_devices.append(device_name)
        
        return relevant_devices
    
    def _find_relevant_policies(self, query: str) -> List[str]:
        """関連ポリシーの検索"""
        # クエリに基づいて関連ポリシーを検索
        return self.kb.search_policies(query)
    
    def _find_relevant_templates(self, query: str) -> List[str]:
        """関連テンプレートの検索"""
        relevant_templates = []
        
        # クエリに基づいて関連テンプレートを検索
        template_patterns = {
            'router': r'router|ルータ',
            'switch': r'switch|スイッチ',
            'interface': r'interface|インターフェース',
            'ospf': r'ospf|ルーティング'
        }
        
        for template_name, template_content in self.kb.templates.items():
            for pattern, keyword in template_patterns.items():
                if re.search(keyword, query, re.IGNORECASE) and pattern in template_name:
                    relevant_templates.append(template_name)
                    break
        
        return relevant_templates
    
    def _find_relevant_rules(self, query: str) -> Dict[str, Any]:
        """関連検証ルールの検索"""
        relevant_rules = {}
        
        # クエリに基づいて関連検証ルールを検索
        rules = self.kb.get_validation_rules()
        
        if 'validation_rules' in rules:
            for rule_category, rule_content in rules['validation_rules'].items():
                if self._is_relevant(query, rule_category):
                    relevant_rules[rule_category] = rule_content
        
        return relevant_rules
    
    def _is_relevant(self, query: str, text: str) -> bool:
        """関連性の判定"""
        query_lower = query.lower()
        text_lower = text.lower()
        
        # クエリのキーワードがテキストに含まれているか判定
        query_words = re.findall(r'\b\w+\b', query_lower)
        text_words = re.findall(r'\b\w+\b', text_lower)
        
        # 共通するキーワードがあるか判定
        common_words = set(query_words) & set(text_words)
        return len(common_words) > 0
    
    def generate_config_prompt(self, query: str) -> str:
        """コンフィグ生成用プロンプトの構築"""
        print(f"Generating config prompt for query: {query}")
        
        # 関連情報の検索
        relevant_info = self.retrieve_relevant_info(query)
        
        # プロンプトの構築
        prompt = self._build_prompt(relevant_info)
        
        # クエリ履歴に追加
        self.query_history.append({
            'query': query,
            'timestamp': str(datetime.now()),
            'relevant_info': relevant_info
        })
        
        return prompt
    
    def _build_prompt(self, relevant_info: Dict[str, Any]) -> str:
        """プロンプトの構築"""
        prompt = f"""
# ネットワークコンフィグ生成依頼

## クエリ情報
- クエリ: {relevant_info['query_context'].query}
- 対象デバイス: {', '.join(relevant_info['relevant_devices']) if relevant_info['relevant_devices'] else '指定なし'}
- 設定タイプ: {relevant_info['query_context'].config_type or '指定なし'}
- 優先度: {relevant_info['query_context'].priority}

## ネットワークサマリー
- デバイス数: {relevant_info['network_summary']['total_devices']}
- デバイスタイプ: {relevant_info['network_summary']['device_types']}
- OSPFエリア: {', '.join(relevant_info['network_summary']['ospf_areas'])}

## 関連デバイスポリシー
"""
        
        # 関連デバイスポリシーの追加
        for device_name in relevant_info['relevant_devices']:
            policy = self.kb.get_device_policy(device_name)
            if policy:
                prompt += f"""
### {device_name} ポリシー
- ホスト名: {policy.hostname}
- デバイスタイプ: {policy.device_type}
- IPアドレス: {policy.ip_address}
- インターフェース: {', '.join(policy.interfaces[:3])}...
- OSPF設定: {policy.ospf_config}
"""
        
        # 関連テンプレートの追加
        if relevant_info['relevant_templates']:
            prompt += f"""
## 関連テンプレート
"""
            for template_name in relevant_info['relevant_templates']:
                template = self.kb.get_template(template_name)
                if template:
                    prompt += f"""
### {template_name} テンプレート
```cisco
{template}
```
"""
        
        # 関連検証ルールの追加
        if relevant_info['relevant_rules']:
            prompt += f"""
## 検証ルール
"""
            for rule_category, rule_content in relevant_info['relevant_rules'].items():
                prompt += f"""
### {rule_category} ルール
{json.dumps(rule_content, indent=2, ensure_ascii=False)}
"""
        
        # 要件の追加
        if relevant_info['query_context'].requirements:
            prompt += f"""
## 追加要件
{relevant_info['query_context'].requirements}
"""
        
        prompt += f"""
## タスク
上記のポリシー情報と要件に基づき、対象デバイスの追加コンフィグを生成してください。

## 出力形式
```cisco
! 追加設定コンフィグ
[具体的な設定コマンド]
```

## 注意事項
1. 既存設定との整合性を確認してください
2. ネットワーク全体への影響を考慮してください
3. 検証ルールに従ってください
4. コメントを適切に追加してください
"""
        
        return prompt
    
    def get_query_history(self) -> List[Dict[str, Any]]:
        """クエリ履歴の取得"""
        return self.query_history
    
    def clear_history(self):
        """クエリ履歴のクリア"""
        self.query_history.clear()


