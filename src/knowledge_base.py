

#!/usr/bin/env python3
# knowledge_base.py
import os
import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class DevicePolicy:
    hostname: str
    device_type: str
    ip_address: str
    interfaces: List[str]
    ospf_config: Dict[str, Any]
    security_config: Dict[str, Any]
    ha_config: Dict[str, Any]
    monitoring_config: Dict[str, Any]
    template_name: Optional[str] = None


@dataclass
class Template:
    name: str
    content: str


class KnowledgeBase:
    def __init__(self, kb_dir: str = "/workspace/network-rag-system/knowledge-base"):
        self.kb_dir = Path(kb_dir)
        self.policies: Dict[str, Any] = {}
        self.templates: Dict[str, Any] = {}
        self.validation_rules: Dict[str, Any] = {}
        self._load_knowledge_base()
    
    def _load_knowledge_base(self) -> None:
        """知識ベースの読み込み"""
        print(f"Loading knowledge base from: {self.kb_dir}")
        
        # ポリシーの読み込み
        self._load_policies()
        
        # テンプレートの読み込み
        self._load_templates()
        
        # 検証ルールの読み込み
        self._load_validation_rules()
        
        print("Knowledge base loaded successfully")
    
    def _load_policies(self) -> None:
        """ポリシーの読み込み"""
        devices_dir = self.kb_dir / "devices"
        if not devices_dir.exists():
            raise FileNotFoundError(f"Devices directory not found: {devices_dir}")
        
        for policy_file in devices_dir.glob("*_policy.md"):
            device_name = policy_file.stem.replace("_policy", "")
            self.policies[device_name] = self._parse_device_policy(policy_file)
    
    def _parse_device_policy(self, policy_file: Path) -> DevicePolicy:
        """デバイスポリシーのパース"""
        with open(policy_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 簡易的なパーサー（実際にはより高度なパーサーを実装）
        hostname = self._extract_field(content, "ホスト名")
        device_type = self._extract_field(content, "デバイスタイプ")
        ip_address = self._extract_field(content, "IPアドレス")
        
        interfaces = self._extract_interfaces(content)
        ospf_config = self._extract_ospf_config(content)
        security_config = self._extract_security_config(content)
        ha_config = self._extract_ha_config(content)
        monitoring_config = self._extract_monitoring_config(content)
        
        # デバイスタイプに基づいてテンプレート名を決定
        template_name = None
        if device_type in ["ルーター", "router"]:
            template_name = "router-template"
        elif device_type in ["L2/L3スイッチ", "switch"]:
            template_name = "switch-template"
        
        return DevicePolicy(
            hostname=hostname,
            device_type=device_type,
            ip_address=ip_address,
            interfaces=interfaces,
            ospf_config=ospf_config,
            security_config=security_config,
            ha_config=ha_config,
            monitoring_config=monitoring_config,
            template_name=template_name
        )
    
    def _extract_field(self, content: str, field_name: str) -> str:
        """フィールドの抽出"""
        # 1. 標準的な「フィールド名: 値」形式の検索
        pattern = rf"{field_name}[:：]\s*(.+)"
        match = re.search(pattern, content)
        if match:
            return match.group(1).strip()
        
        # 2. リスト形式の検索（例: **タイプ**: ルーター）
        list_pattern = rf"\*\*{field_name}\*\*[:：]\s*(.+)"
        match = re.search(list_pattern, content)
        if match:
            return match.group(1).strip()
        
        # 3. ポリシー要件からの抽出（例: **基本設定**: ホスト名はR1）
        requirement_pattern = rf"\*\*{field_name}\*\*[:：]\s*[^:]+?は\s*([^、\s]+)"
        match = re.search(requirement_pattern, content)
        if match:
            return match.group(1).strip()
        
        # 4. 特殊なケースの処理
        if field_name == "ホスト名":
            # 「ホスト名はR1」のような形式
            hostname_pattern = r"ホスト名は(\w+)"
            match = re.search(hostname_pattern, content)
            if match:
                return match.group(1).strip()
        
        if field_name == "デバイスタイプ":
            # 「**タイプ**: ルーター」のような形式から値を抽出
            type_pattern = r"\*\*タイプ\*\*\s*[:：]\s*(.+)"
            match = re.search(type_pattern, content)
            if match:
                return match.group(1).strip()
        
        if field_name == "IPアドレス":
            # IPアドレスの抽出
            ip_pattern = r"(\d+\.\d+\.\d+\.\d+/\d+)"
            match = re.search(ip_pattern, content)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def _extract_interfaces(self, content: str) -> List[str]:
        """インターフェース設定の抽出"""
        interfaces = []
        
        # 特殊要件セクションからインターフェースを抽出
        interface_pattern = r"## 特殊要件(.*?)(## |$)"
        match = re.search(interface_pattern, content, re.DOTALL)
        
        if match:
            interface_section = match.group(1)
            # インターフェース名を抽出（例: GigabitEthernet0/0/0, Loopback0）
            interface_name_pattern = r"は\s*(GigabitEthernet\d+/\d+/\d+|Loopback\d+)"
            interface_matches = re.findall(interface_name_pattern, interface_section)
            
            for interface in interface_matches:
                interfaces.append(interface)
        
        return interfaces
    
    def _extract_ospf_config(self, content: str) -> Dict[str, Any]:
        """OSPF設定の抽出"""
        ospf_config = {}
        
        # Router-IDの抽出
        router_id = self._extract_field(content, "Router-ID")
        if router_id:
            ospf_config['router_id'] = router_id
        
        # エリア設定の抽出
        area_pattern = r"Area (\d+): ([^\n]+)"
        area_matches = re.findall(area_pattern, content)
        if area_matches:
            ospf_config['areas'] = {str(k): str(v) for k, v in dict(area_matches).items()}
        
        return ospf_config
    
    def _extract_security_config(self, content: str) -> Dict[str, Any]:
        """セキュリティ設定の抽出"""
        security_config = {}
        
        # SNMP設定の抽出
        snmp_pattern = r"Community: \"([^\"]+)\""
        snmp_matches = re.findall(snmp_pattern, content)
        if snmp_matches:
            security_config['snmp_community'] = snmp_matches
        
        # ACL設定の抽出
        acl_pattern = r"ACL (\d+): ([^\n]+)"
        acl_matches = re.findall(acl_pattern, content)
        if acl_matches:
            security_config['acls'] = {str(k): str(v) for k, v in dict(acl_matches).items()}
        
        return security_config
    
    def _extract_ha_config(self, content: str) -> Dict[str, Any]:
        """高可用性設定の抽出"""
        ha_config: Dict[str, Any] = {}
        
        # HSRP設定の抽出
        hsrp_pattern = r"Group (\d+): ([^\n]+)"
        hsrp_matches = re.findall(hsrp_pattern, content)
        if hsrp_matches:
            ha_config['hsrp_groups'] = dict(hsrp_matches)
        
        # Priorityの抽出
        priority_pattern = r"Priority: (\d+)"
        priority_match = re.search(priority_pattern, content)
        if priority_match:
            ha_config['priority'] = int(priority_match.group(1))
        
        return ha_config
    
    def _extract_monitoring_config(self, content: str) -> Dict[str, Any]:
        """監視設定の抽出"""
        monitoring_config = {}
        
        # Syslog設定の抽出
        syslog_pattern = r"Syslog: ([^\n]+)"
        syslog_match = re.search(syslog_pattern, content)
        if syslog_match:
            monitoring_config['syslog_server'] = syslog_match.group(1)
        
        # NTP設定の抽出
        ntp_pattern = r"NTP: ([^\n]+)"
        ntp_match = re.search(ntp_pattern, content)
        if ntp_match:
            monitoring_config['ntp_server'] = ntp_match.group(1)
        
        return monitoring_config
    
    def _load_templates(self) -> None:
        """テンプレートの読み込み"""
        templates_dir = self.kb_dir / "automation" / "templates"
        if templates_dir.exists():
            for template_file in templates_dir.glob("*.txt"):
                with open(template_file, 'r', encoding='utf-8') as f:
                    self.templates[template_file.stem] = Template(template_file.stem, f.read())
    
    def _load_validation_rules(self) -> None:
        """検証ルールの読み込み"""
        validation_file = self.kb_dir / "automation" / "validation-rules.yaml"
        if validation_file.exists():
            with open(validation_file, 'r', encoding='utf-8') as f:
                self.validation_rules = yaml.safe_load(f)
    
    def get_device_policy(self, device_name: str) -> Optional[DevicePolicy]:
        """デバイスポリシーの取得"""
        return self.policies.get(device_name)
    
    def get_template(self, template_name: str) -> Optional[str]:
        """テンプレートの取得"""
        return self.templates.get(template_name)
    
    def get_validation_rules(self) -> Dict[str, Any]:
        """検証ルールの取得"""
        return self.validation_rules
    
    def search_policies(self, keyword: str) -> List[str]:
        """ポリシー検索"""
        results = []
        keyword_lower = keyword.lower()
        
        for device_name, policy in self.policies.items():
            # ポリシー内容の検索
            policy_text = f"{policy.hostname} {policy.device_type} {policy.ip_address}".lower()
            if keyword_lower in policy_text:
                results.append(device_name)
        
        return results
    
    def list_devices(self) -> List[str]:
        """デバイスリストの取得"""
        return list(self.policies.keys())
    
    def search_policies_advanced(self, query: str) -> List[str]:
        """ポリシーの高度検索"""
        relevant_policies = []
        
        # クエリの単語を抽出
        query_words = set(re.findall(r'[a-zA-Z0-9]+|[\u3040-\u309f]+|[\u30a0-\u30ff]+', query.lower()))
        
        for device_name, policy in self.policies.items():
            # ポリシー内容をテキスト化
            policy_text = f"{policy.hostname} {policy.device_type} {policy.ip_address} {policy.interfaces}"
            
            # ポリシーテンプレートの内容を追加
            if policy.template_name:
                template = self.templates.get(policy.template_name)
                if template:
                    policy_text += f" {template.content}"
            
            # 関連性判定
            policy_words = set(re.findall(r'[a-zA-Z0-9]+|[\u3040-\u309f]+|[\u30a0-\u30ff]+', policy_text.lower()))
            if query_words.intersection(policy_words):
                relevant_policies.append(device_name)
        
        return relevant_policies
    
    def get_network_summary(self) -> Dict[str, Any]:
        """ネットワークサマリーの取得"""
        summary: Dict[str, Any] = {
            'total_devices': len(self.policies),
            'device_types': {},
            'ip_addresses': [],
            'ospf_areas': set(),
            'last_updated': datetime.now().isoformat()
            }
        
        for policy in self.policies.values():
            # デバイスタイプの集計
            if policy.device_type not in summary['device_types']:
                summary['device_types'][policy.device_type] = 0
            summary['device_types'][policy.device_type] = int(summary['device_types'][policy.device_type]) + 1
            
            # IPアドレスの収集
            summary['ip_addresses'].append(policy.ip_address)
            
            # OSPFエリアの収集
            if 'areas' in policy.ospf_config:
                summary['ospf_areas'].update(policy.ospf_config['areas'].keys())
        
        summary['ospf_areas'] = list(summary['ospf_areas'])
        return summary


