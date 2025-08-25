


#!/usr/bin/env python3
# openhands_agent.py
from openhands import Agent
from typing import Dict, Any, Optional
import json
import requests
import yaml
import re
from dataclasses import dataclass
from datetime import datetime

@dataclass
class NetworkConfigTask:
    """ネットワーク設定タスク"""
    query: str
    device_name: str
    config_type: str
    priority: str = "normal"
    deadline: Optional[str] = None

class NetworkConfigAgent(Agent):
    """ネットワーク設定生成用OpenHandsエージェント"""
    
    def __init__(self, config_path: str = "config/openhands_config.yaml"):
        super().__init__()
        self.config = self._load_config(config_path)
        self.rag_system = None  # 後で初期化
        self.config_generator = None  # 後で初期化
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """設定ファイルの読み込み"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            # デフォルト設定
            return {
                'openhands': {
                    'api_url': 'http://localhost:8001',
                    'api_key': 'default_api_key',
                    'timeout': 30,
                    'max_retries': 3
                }
            }
    
    def process_network_query(self, query: str) -> Dict[str, Any]:
        """ネットワーククエリの処理"""
        try:
            # 1. タスクの解析
            task = self._parse_query_to_task(query)
            
            # 2. RAGシステムで関連情報を検索
            relevant_info = self._get_relevant_info(query)
            
            # 3. プロンプトを生成
            prompt = self._generate_network_prompt(task, relevant_info)
            
            # 4. LLM APIでコンフィグを生成
            config_content = self._call_llm_api(prompt)
            
            # 5. コンフィグの検証
            validation_result = self._validate_config(config_content)
            
            return {
                'task_id': task.query,
                'device_name': task.device_name,
                'config_content': config_content,
                'validation_result': validation_result,
                'relevant_info': relevant_info,
                'status': 'completed',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'task_id': query,
                'error': str(e),
                'status': 'failed',
                'timestamp': datetime.now().isoformat()
            }
    
    def _parse_query_to_task(self, query: str) -> NetworkConfigTask:
        """クエリからタスクを解析"""
        # デバイス名の抽出
        device_name = self._extract_device_name(query)
        
        # 設定タイプの判定
        config_type = self._determine_config_type(query)
        
        return NetworkConfigTask(
            query=query,
            device_name=device_name,
            config_type=config_type
        )
    
    def _extract_device_name(self, query: str) -> str:
        """クエリからデバイス名を抽出"""
        # 正規表現でデバイス名を抽出
        pattern = r'(R\d+|SW\d+|Router\d+|Switch\d+)'
        match = re.search(pattern, query)
        return match.group(1) if match else "unknown"
    
    def _determine_config_type(self, query: str) -> str:
        """クエリから設定タイプを判定"""
        query_lower = query.lower()
        if any(keyword in query_lower for keyword in ['basic', '初期', '基本']):
            return "basic"
        elif any(keyword in query_lower for keyword in ['ospf', 'ルーティング', 'routing']):
            return "routing"
        elif any(keyword in query_lower for keyword in ['vlan', 'スイッチ', 'switching']):
            return "switching"
        elif any(keyword in query_lower for keyword in ['security', 'セキュリティ', 'acl']):
            return "security"
        elif any(keyword in query_lower for keyword in ['monitoring', '監視', 'snmp']):
            return "monitoring"
        else:
            return "general"
    
    def _get_relevant_info(self, query: str) -> Dict:
        """RAGシステムで関連情報を検索"""
        try:
            # 後でRAGシステムを実装
            return {
                'relevant_devices': ['R1', 'R2', 'SW1'],
                'relevant_policies': ['standard_acl', 'ospf_policy'],
                'relevant_templates': ['router_template', 'switch_template']
            }
        except Exception:
            return {
                'relevant_devices': [],
                'relevant_policies': [],
                'relevant_templates': []
            }
    
    def _generate_network_prompt(self, task: NetworkConfigTask, relevant_info: Dict) -> str:
        """ネットワーク設定用プロンプトを生成"""
        template = f"""
ネットワーク設定生成タスク:

デバイス名: {task.device_name}
設定タイプ: {task.config_type}
クエリ: {task.query}

関連情報:
- デバイスポリシー: {relevant_info.get('relevant_devices', [])}
- 関連ポリシー: {relevant_info.get('relevant_policies', [])}
- 関連テンプレート: {relevant_info.get('relevant_templates', [])}

上記の情報を基に、{task.device_name}の{task.config_type}設定を生成してください。
設定はCisco IOS形式で、以下の構造に従ってください:

1. 基本設定 (hostname, ip routing, etc.)
2. インターフェース設定
3. プロトコル設定 (OSPF, BGP, etc.)
4. セキュリティ設定
5. 監視設定

変数 {{hostname}} は {task.device_name} に置換してください。
"""
        return template
    
    def _call_llm_api(self, prompt: str) -> str:
        """LLM APIを呼び出してコンフィグを生成"""
        try:
            # Local LLM (Ollama) を優先的に使用
            if self.config.get('llm', {}).get('local', {}).get('enabled', False):
                return self._call_ollama_api(prompt)
            else:
                # デフォルトのダミー実装
                return self._generate_dummy_config(prompt)
        except Exception as e:
            # フォールバック
            return self._generate_dummy_config(prompt)
    
    def _call_ollama_api(self, prompt: str) -> str:
        """Ollama APIを呼び出す"""
        ollama_config = self.config.get('llm', {}).get('local', {})
        
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "model": ollama_config.get('model', 'llama2'),
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": ollama_config.get('temperature', 0.7),
                "num_predict": ollama_config.get('max_tokens', 2000)
            }
        }
        
        try:
            response = requests.post(
                f"{ollama_config.get('api_url', 'http://localhost:11434')}/api/generate",
                headers=headers,
                json=data,
                timeout=ollama_config.get('timeout', 60)
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '')
            else:
                raise Exception(f"Ollama API error: {response.status_code}")
        except Exception as e:
            raise Exception(f"Ollama API call failed: {str(e)}")
    
    def _generate_dummy_config(self, prompt: str) -> str:
        """ダミーコンフィグを生成（デモ用）"""
        device_name = self._extract_device_name(prompt)
        
        dummy_configs = {
            'basic': f"""! {device_name} - Basic Configuration
! Generated based on network policy
! Requirements: {prompt.split('Query:')[1] if 'Query:' in prompt else prompt}

! Basic Settings
hostname {device_name}
ip routing
service timestamps debug datetime msec
service timestamps log datetime msec
no ip domain-lookup
ip domain-name company.local

! Interface Configuration
interface GigabitEthernet0/0/0
 description Uplink to Core
 no shutdown
!
interface GigabitEthernet0/0/1
 description Downlink to Access
 no shutdown
!""",
            
            'routing': f"""! {device_name} - Routing Configuration
! Generated based on network policy
! Requirements: {prompt.split('Query:')[1] if 'Query:' in prompt else prompt}

! Basic Settings
hostname {device_name}
ip routing
service timestamps debug datetime msec
service timestamps log datetime msec

! OSPF Configuration
router ospf 1
 router-id 10.1.1.{device_name[-1]}
 network 10.1.1.0 0.0.0.255 area 0
 network 10.2.1.0 0.0.0.255 area 1
 passive-interface default
 no passive-interface GigabitEthernet0/0/0
 no passive-interface GigabitEthernet0/0/1
!""",
            
            'switching': f"""! {device_name} - Switching Configuration
! Generated based on network policy
! Requirements: {prompt.split('Query:')[1] if 'Query:' in prompt else prompt}

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
vlan 30
 name Marketing
!

! Interface Configuration
interface GigabitEthernet0/1
 switchport mode access
 switchport access vlan 10
!
interface GigabitEthernet0/2
 switchport mode access
 switchport access vlan 20
!
interface GigabitEthernet0/3
 switchport mode access
 switchport access vlan 30
!""",
            
            'security': f"""! {device_name} - Security Configuration
! Generated based on network policy
! Requirements: {prompt.split('Query:')[1] if 'Query:' in prompt else prompt}

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
ip access-list standard ACL_TRUSTED
 permit 10.0.0.0 0.255.255.255
 deny any
!

! Interface Security
interface GigabitEthernet0/0/0
 ip access-group ACL_MANAGEMENT in
!
interface GigabitEthernet0/0/1
 ip access-group ACL_TRUSTED in
!""",
            
            'monitoring': f"""! {device_name} - Monitoring Configuration
! Generated based on network policy
! Requirements: {prompt.split('Query:')[1] if 'Query:' in prompt else prompt}

! Basic Settings
hostname {device_name}
ip routing
service timestamps debug datetime msec
service timestamps log datetime msec

! SNMP Configuration
snmp-server community public RO
snmp-server community RW RW
snmp-server host 192.168.100.100 public
snmp-server location Data Center
snmp-server contact network-admin@company.com

! NTP Configuration
ntp server 192.168.100.100 prefer
ntp server 192.168.100.101

! Logging Configuration
logging buffered 16384
logging host 192.168.100.100
logging trap debugging
!"""
        }
        
        config_type = self._determine_config_type(prompt)
        return dummy_configs.get(config_type, dummy_configs['basic'])
    
    def _validate_config(self, config: str) -> Dict[str, Any]:
        """生成されたコンフィグを検証"""
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'suggestions': []
        }
        
        # 基本的な構文チェック
        if 'hostname' not in config:
            validation_result['warnings'].append('Hostname not found in configuration')
        
        if 'ip routing' not in config and 'no ip routing' not in config:
            validation_result['warnings'].append('IP routing configuration not found')
        
        # エラーのチェック
        if 'error' in config.lower() or 'invalid' in config.lower():
            validation_result['is_valid'] = False
            validation_result['errors'].append('Configuration contains error messages')
        
        return validation_result


