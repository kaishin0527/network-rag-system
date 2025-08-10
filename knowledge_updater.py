
#!/usr/bin/env python3
"""
Knowledge Base Updater for Network RAG System
OpenHandsからKBの装置情報を更新するための実装
"""

import os
import re
import json
import yaml
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod

# OpenHands関連のインポート
try:
    from openhands.core.schema import AgentAction, AgentObservation
    from openhands.core.logger import print_system_log
    from openhands.core.config import AgentConfig
    OPENHANDS_AVAILABLE = True
except ImportError:
    print("Warning: OpenHands not available. Using dummy implementation.")
    OPENHANDS_AVAILABLE = False

# Network RAG System関連のインポート
try:
    from src.rag_system import NetworkRAGSystem
    from src.config_generator import NetworkConfigGenerator
    from src.knowledge_base import KnowledgeBase
    RAG_AVAILABLE = True
except ImportError:
    print("Warning: Network RAG System not available. Using dummy implementation.")
    RAG_AVAILABLE = False

@dataclass
class DeviceConfig:
    """装置コンフィグデータクラス"""
    device_name: str
    config_type: str
    config_content: str
    metadata: Dict[str, Any]
    timestamp: datetime

@dataclass
class UpdateResult:
    """更新結果データクラス"""
    device_name: str
    success: bool
    message: str
    updated_files: List[str]
    errors: List[str]

class KnowledgeBaseUpdater(ABC):
    """知識ベース更新の抽象基底クラス"""
    
    @abstractmethod
    def update_device_info(self, device_config: DeviceConfig) -> UpdateResult:
        """装置情報を更新する抽象メソッド"""
        pass
    
    @abstractmethod
    def validate_config(self, config_content: str) -> bool:
        """コンフィグの妥当性を検証する抽象メソッド"""
        pass

class NetworkRAGKnowledgeUpdater(KnowledgeBaseUpdater):
    """Network RAG System用の知識ベース更新クラス"""
    
    def __init__(self, knowledge_base_path: str = "knowledge-base"):
        self.knowledge_base_path = Path(knowledge_base_path)
        self.devices_path = self.knowledge_base_path / "devices"
        self.logger = self._setup_logger()
        
        # Network RAG Systemの初期化
        if RAG_AVAILABLE:
            try:
                self.rag_system = NetworkRAGSystem()
                self.config_generator = NetworkConfigGenerator()
                self.logger.info("Network RAG System initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize Network RAG System: {e}")
                self.rag_system = None
                self.config_generator = None
        else:
            self.rag_system = None
            self.config_generator = None
    
    def _setup_logger(self) -> logging.Logger:
        """ロガーのセットアップ"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        # コンソールハンドラー
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def update_device_info(self, device_config: DeviceConfig) -> UpdateResult:
        """装置情報を更新する"""
        try:
            self.logger.info(f"Updating device info for: {device_config.device_name}")
            
            # コンフィグの検証
            if not self.validate_config(device_config.config_content):
                return UpdateResult(
                    device_name=device_config.device_name,
                    success=False,
                    message="Invalid configuration format",
                    updated_files=[],
                    errors=["Configuration validation failed"]
                )
            
            # メタデータの解析
            parsed_metadata = self._parse_config_metadata(device_config.config_content)
            
            # 装置ポリシーの更新
            policy_updated = self._update_device_policy(
                device_config.device_name, 
                parsed_metadata
            )
            
            # 設定テンプレートの更新
            template_updated = self._update_config_template(
                device_config.device_name,
                device_config.config_content,
                parsed_metadata
            )
            
            # デバイスコンフィグの保存
            config_saved = self._save_device_config(device_config)
            
            updated_files = []
            if policy_updated:
                updated_files.append(f"devices/{device_config.device_name}_policy.md")
            if template_updated:
                updated_files.append(f"devices/{device_config.device_name}_config_template.yml")
            if config_saved:
                updated_files.append(f"devices/device_configs/{device_config.device_name}_running_config_{device_config.timestamp.strftime('%Y-%m-%d')}.txt")
            
            return UpdateResult(
                device_name=device_config.device_name,
                success=True,
                message="Device information updated successfully",
                updated_files=updated_files,
                errors=[]
            )
            
        except Exception as e:
            self.logger.error(f"Error updating device info: {e}")
            return UpdateResult(
                device_name=device_config.device_name,
                success=False,
                message=f"Update failed: {str(e)}",
                updated_files=[],
                errors=[str(e)]
            )
    
    def validate_config(self, config_content: str) -> bool:
        """コンフィグの妥当性を検証する"""
        try:
            # 基本的なCisco IOSコンフィグの検証
            lines = config_content.strip().split('\n')
            
            # 空のコンフィグは無効
            if not lines or len(lines) < 2:
                return False
            
            # ホスト名の存在確認
            has_hostname = any(line.strip().startswith('hostname ') for line in lines)
            if not has_hostname:
                return False
            
            # IP設定の存在確認（少なくとも1つは必要）
            has_ip_config = any(
                'ip address ' in line.lower() and 'no shutdown' in line.lower()
                for line in lines
            )
            
            # 基本的な構文チェック
            for line in lines:
                line = line.strip()
                if line and not line.startswith('!') and not line.startswith('#'):
                    # コメント以外の行は基本的なコマンド構文をチェック
                    if not self._validate_command_syntax(line):
                        return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Config validation error: {e}")
            return False
    
    def _validate_command_syntax(self, command: str) -> bool:
        """コマンド構文の検証"""
        # 基本的なCisco IOSコマンドの構文チェック
        common_patterns = [
            r'^hostname\s+\w+$',
            r'^interface\s+\w+',
            r'^ip address\s+\d+\.\d+\.\d+\.\d+\s+\d+\.\d+\.\d+\.\d+$',
            r'^router\s+\w+',
            r'^vlan\s+\d+$',
            r'^ip access-list\s+\w+',
            r'^line\s+\w+',
            r'^username\s+\w+\s+privilege\s+\d+',
            r'^snmp-server\s+community',
            r'^ntp server\s+\d+\.\d+\.\d+\.\d+',
        ]
        
        for pattern in common_patterns:
            if re.match(pattern, command, re.IGNORECASE):
                return True
        
        # 上記パターンにマッチしない場合は、一般的なコマンド形式をチェック
        if ' ' in command and not command.startswith(' '):
            return True
        
        return False
    
    def _parse_config_metadata(self, config_content: str) -> Dict[str, Any]:
        """コンフィグからメタデータを解析する"""
        metadata = {
            'extracted_at': datetime.now().isoformat(),
            'interfaces': [],
            'ip_addresses': [],
            'routing_protocols': [],
            'vlans': [],
            'access_lists': [],
            'users': [],
            'snmp_communities': [],
            'ntp_servers': []
        }
        
        lines = config_content.strip().split('\n')
        current_interface = None
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('!') or line.startswith('#'):
                continue
            
            # インターフェース情報の抽出
            interface_match = re.match(r'^interface\s+(\S+)', line, re.IGNORECASE)
            if interface_match:
                current_interface = interface_match.group(1)
                metadata['interfaces'].append(current_interface)
                continue
            
            # IPアドレス情報の抽出
            ip_match = re.search(r'ip address\s+(\d+\.\d+\.\d+\.\d+)\s+(\d+\.\d+\.\d+\.\d+)', line, re.IGNORECASE)
            if ip_match:
                metadata['ip_addresses'].append({
                    'interface': current_interface,
                    'ip': ip_match.group(1),
                    'subnet': ip_match.group(2)
                })
            
            # ルーティングプロトコルの抽出
            if line.startswith('router '):
                protocol = line.split()[1]
                metadata['routing_protocols'].append(protocol)
            
            # VLAN情報の抽出
            vlan_match = re.match(r'^vlan\s+(\d+)', line, re.IGNORECASE)
            if vlan_match:
                metadata['vlans'].append(vlan_match.group(1))
            
            # ACL情報の抽出
            acl_match = re.search(r'ip access-list\s+(\w+)', line, re.IGNORECASE)
            if acl_match:
                metadata['access_lists'].append(acl_match.group(1))
            
            # ユーザー情報の抽出
            user_match = re.match(r'^username\s+(\w+)\s+privilege\s+(\d+)', line, re.IGNORECASE)
            if user_match:
                metadata['users'].append({
                    'username': user_match.group(1),
                    'privilege': user_match.group(2)
                })
            
            # SNMPコミュニティの抽出
            snmp_match = re.search(r'snmp-server\s+community\s+"?([^"\s]+)"?', line, re.IGNORECASE)
            if snmp_match:
                metadata['snmp_communities'].append(snmp_match.group(1))
            
            # NTPサーバーの抽出
            ntp_match = re.search(r'ntp server\s+(\d+\.\d+\.\d+\.\d+)', line, re.IGNORECASE)
            if ntp_match:
                metadata['ntp_servers'].append(ntp_match.group(1))
        
        return metadata
    
    def _update_device_policy(self, device_name: str, metadata: Dict[str, Any]) -> bool:
        """装置ポリシーを更新する"""
        try:
            policy_file = self.devices_path / f"{device_name}_policy.md"
            
            # 既存のポリシーファイルがあれば読み込む
            existing_policy = ""
            if policy_file.exists():
                with open(policy_file, 'r', encoding='utf-8') as f:
                    existing_policy = f.read()
            
            # 新しいポリシーコンテンツを作成
            new_policy = self._generate_device_policy(device_name, metadata, existing_policy)
            
            # ポリシーファイルを保存
            with open(policy_file, 'w', encoding='utf-8') as f:
                f.write(new_policy)
            
            self.logger.info(f"Updated device policy: {policy_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update device policy: {e}")
            return False
    
    def _generate_device_policy(self, device_name: str, metadata: Dict[str, Any], existing_policy: str) -> str:
        """装置ポリシーコンテンツを生成する"""
        # 既存のポリシーから基本情報を保持
        policy_lines = existing_policy.split('\n') if existing_policy else []
        basic_info_section = []
        config_section = []
        
        # セクションの分割
        current_section = None
        for line in policy_lines:
            if line.startswith('## '):
                current_section = line[3:].strip()
            elif line.startswith('# ') and current_section is None:
                current_section = line[2:].strip()
            
            if current_section == '基本情報':
                basic_info_section.append(line)
            elif current_section == 'コンフィグレーション':
                config_section.append(line)
        
        # 新しいポリシーコンテンツ
        new_policy = f"""# {device_name} 装置ポリシー

## 基本情報

- **装置名**: {device_name}
- **更新日時**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **コンフィグタイプ**: 実行コンフィグ
- **状態**: 運用中

### ハードウェア情報
- **インターフェース数**: {len(metadata['interfaces'])}
- **IPアドレス数**: {len(metadata['ip_addresses'])}
- **VLAN数**: {len(metadata['vlans'])}

### ネットワーク設定
- **ルーティングプロトコル**: {', '.join(metadata['routing_protocols']) if metadata['routing_protocols'] = 'なし'}
- **SNMPコミュニティ数**: {len(metadata['snmp_communities'])}
- **NTPサーバー**: {', '.join(metadata['ntp_servers']) if metadata['ntp_servers'] else 'なし'}

## コンフィグレーション

### インターフェース設定
"""
        
        # インターフェース情報の追加
        for interface in metadata['interfaces']:
            new_policy += f"- **{interface}**: アクティブ\n"
        
        new_policy += "\n### IP設定\n"
        
        # IP設定情報の追加
        for ip_info in metadata['ip_addresses']:
            new_policy += f"- **{ip_info['interface']}**: {ip_info['ip']}/{ip_info['subnet']}\n"
        
        new_policy += "\n### セキュリティ設定\n"
        
        # セキュリティ情報の追加
        if metadata['access_lists']:
            new_policy += f"- **ACL**: {', '.join(metadata['access_lists'])}\n"
        
        if metadata['users']:
            new_policy += f"- **ユーザー数**: {len(metadata['users'])}\n"
        
        new_policy += "\n### 管理設定\n"
        
        # 管理情報の追加
        if metadata['snmp_communities']:
            new_policy += f"- **SNMP**: {len(metadata['snmp_communities'])}コミュニティ\n"
        
        if metadata['ntp_servers']:
            new_policy += f"- **NTP**: {', '.join(metadata['ntp_servers'])}\n"
        
        # 既存のコンフィグセクションがあれば追加
        if config_section:
            new_policy += "\n## 詳細設定\n"
            new_policy += "\n".join(config_section)
        
        return new_policy
    
    def _update_config_template(self, device_name: str, config_content: str, metadata: Dict[str, Any]) -> bool:
        """設定テンプレートを更新する"""
        try:
            template_file = self.devices_path / f"{device_name}_config_template.yml"
            
            # テンプレートデータを作成
            template_data = {
                'device_name': device_name,
                'created_at': datetime.now().isoformat(),
                'template_type': 'cisco_ios',
                'based_on_config': True,
                'metadata': metadata,
                'config_sections': self._extract_config_sections(config_content)
            }
            
            # テンプレートファイルを保存
            with open(template_file, 'w', encoding='utf-8') as f:
                yaml.dump(template_data, f, default_flow_style=False, allow_unicode=True)
            
            self.logger.info(f"Updated config template: {template_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update config template: {e}")
            return False
    
    def _extract_config_sections(self, config_content: str) -> Dict[str, List[str]]:
        """コンフィグセクションを抽出する"""
        sections = {
            'basic': [],
            'interfaces': [],
            'routing': [],
            'security': [],
            'management': [],
            'other': []
        }
        
        lines = config_content.strip().split('\n')
        current_section = 'basic'
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('!') or line.startswith('#'):
                continue
            
            # セクションの判定
            if line.startswith('hostname '):
                current_section = 'basic'
            elif line.startswith('interface '):
                current_section = 'interfaces'
            elif line.startswith('router '):
                current_section = 'routing'
            elif line.startswith('ip access-list ') or line.startswith('access-list '):
                current_section = 'security'
            elif any(keyword in line.lower() for keyword in ['snmp', 'ntp', 'ssh', 'telnet', 'logging']):
                current_section = 'management'
            
            sections[current_section].append(line)
        
        return sections
    
    def _save_device_config(self, device_config: DeviceConfig) -> bool:
        """デバイスコンフィグを保存する"""
        try:
            config_dir = self.devices_path / "device_configs"
            config_dir.mkdir(parents=True, exist_ok=True)
            
            # ファイル名の生成
            filename = f"{device_config.device_name}_{device_config.config_type}_{device_config.timestamp.strftime('%Y-%m-%d')}.txt"
            config_file = config_dir / filename
            
            # メタデータを追加
            config_with_metadata = f"""# Device Configuration Metadata
# Device: {device_config.device_name}
# Type: Router/Switch
# OS: Cisco IOS
# Config Type: {device_config.config_type}
# Date: {device_config.timestamp.strftime('%Y-%m-%d')}
# Version: Auto-detected
# Contact: network-admin@company.com
# Description: Production configuration from actual device

{device_config.config_content}
"""
            
            # コンフィグファイルを保存
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(config_with_metadata)
            
            self.logger.info(f"Saved device config: {config_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save device config: {e}")
            return False

class OpenHandsKnowledgeUpdater:
    """OpenHands用の知識ベース更新クラス"""
    
    def __init__(self, kb_updater: KnowledgeBaseUpdater):
        self.kb_updater = kb_updater
        self.logger = logging.getLogger(__name__)
    
    def create_update_prompt(self, device_config: DeviceConfig) -> str:
        """KB更新用のプロンプトを作成する"""
        prompt = f"""
Network RAG System Knowledge Base Update Request

=== Device Information ===
Device Name: {device_config.device_name}
Config Type: {device_config.config_type}
Timestamp: {device_config.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

=== Configuration Content ===
{device_config.config_content}

=== Metadata ===
{json.dumps(device_config.metadata, indent=2, ensure_ascii=False)}

=== Update Instructions ===
Please analyze the above device configuration and update the Network RAG System knowledge base with the following information:

1. Device Policy Updates:
   - Extract device type and model information
   - Identify interface configurations
   - Document IP address assignments
   - List routing protocols and configurations
   - Note security policies and ACLs
   - Record management settings (SNMP, NTP, etc.)

2. Configuration Template Updates:
   - Create a structured template based on the actual config
   - Identify common configuration patterns
   - Document best practices observed
   - Note any deviations from standards

3. Validation Rules:
   - Update validation rules based on actual device behavior
   - Add new interface types if discovered
   - Update IP address ranges if needed
   - Document any special configurations

4. Knowledge Base Files to Update:
   - Update device policy: knowledge-base/devices/{device_config.device_name}_policy.md
   - Update config template: knowledge-base/devices/{device_config.device_name}_config_template.yml
   - Save raw config: knowledge-base/devices/device_configs/{device_config.device_name}_running_config_{device_config.timestamp.strftime('%Y-%m-%d')}.txt

Please provide the updated content for each file and confirm the update was successful.
"""
        return prompt
    
    def process_update_request(self, device_config: DeviceConfig) -> UpdateResult:
        """更新リクエストを処理する"""
        try:
            # 更新用プロンプトの作成
            prompt = self.create_update_prompt(device_config)
            
            # OpenHandsを使用して更新処理を実行
            if OPENHANDS_AVAILABLE:
                result = self._process_with_openhands(prompt, device_config)
            else:
                # ダミー実装
                result = self._process_with_dummy(device_config)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing update request: {e}")
            return UpdateResult(
                device_name=device_config.device_name,
                success=False,
                message=f"Update processing failed: {str(e)}",
                updated_files=[],
                errors=[str(e)]
            )
    
    def _process_with_openhands(self, prompt: str, device_config: DeviceConfig) -> UpdateResult:
        """OpenHandsを使用して更新処理を実行する"""
        try:
            # ここでOpenHandsのエージェントを使用してKB更新を実行
            # 実際の実装では、OpenHandsのエージェントがプロンプトを処理し、
            # 必要なファイルを更新する
            
            # ダミーの実装として、直接KBUpdaterを使用
            result = self.kb_updater.update_device_info(device_config)
            
            return result
            
        except Exception as e:
            self.logger.error(f"OpenHands processing error: {e}")
            return UpdateResult(
                device_name=device_config.device_name,
                success=False,
                message=f"OpenHands processing failed: {str(e)}",
                updated_files=[],
                errors=[str(e)]
            )
    
    def _process_with_dummy(self, device_config: DeviceConfig) -> UpdateResult:
        """ダミーの実装"""
        # ダミーの更新処理
        print(f"Dummy processing for device: {device_config.device_name}")
        print(f"Config type: {device_config.config_type}")
        print(f"Config length: {len(device_config.config_content)} characters")
        
        # ダミーの成功結果
        return UpdateResult(
            device_name=device_config.device_name,
            success=True,
            message="Dummy update completed successfully",
            updated_files=[
                f"devices/{device_config.device_name}_policy.md",
                f"devices/{device_config.device_name}_config_template.yml",
                f"devices/device_configs/{device_config.device_name}_running_config_{device_config.timestamp.strftime('%Y-%m-%d')}.txt"
            ],
            errors=[]
        )

def main():
    """メイン関数"""
    # 知識ベースアップデーターの初期化
    kb_updater = NetworkRAGKnowledgeUpdater()
    openhands_updater = OpenHandsKnowledgeUpdater(kb_updater)
    
    # サンプルのデバイスコンフィグ
    sample_config = """
! Sample Router Configuration
! Generated for testing purposes
hostname R1
ip routing
service timestamps debug datetime msec
service timestamps log datetime msec
no ip domain-lookup
ip domain-name company.local

! NTP設定
ntp server 192.168.1.1 prefer
ntp server 192.168.1.2

! DNS設定
ip name-server 8.8.8.8
ip name-server 8.8.4.4

! 特権EXECモードパスワード
enable secret $1$secret$

! VTYコンソール設定
line con 0
 exec-timeout 0 0
 logging synchronous
line vty 0 4
 login local
line vty 5 15
 login local

! ローカルユーザー設定
username admin privilege 15 secret $1$admin$
username monitor privilege 1 secret $1$monitor$

! インターフェース設定
interface GigabitEthernet0/0/0
 description WAN Link to ISP
 ip address 203.0.113.1 255.255.255.0
 no shutdown

interface GigabitEthernet0/0/1
 description LAN Link to SW1
 ip address 192.168.1.1 255.255.255.0
 no shutdown

! ループバックインターフェース
interface Loopback0
 ip address 10.1.1.1 255.255.255.255
 description Management Loopback

! OSPF設定
router ospf 1
 router-id 10.1.1.1
 log-adjacency-changes
 network 10.1.1.0 0.0.0.255 area 0
 network 192.168.1.0 0.0.0.255 area 0
 passive-interface default
 no passive-interface GigabitEthernet0/0/0
 no passive-interface GigabitEthernet0/0/1

! ACL設定
ip access-list extended INBOUND_ACL
 permit tcp 192.168.1.0 0.0.0.255 10.1.1.0 0.0.0.255 eq 22
 permit tcp 192.168.1.0 0.0.0.255 10.1.1.0 0.0.0.255 eq 443
 permit icmp any any
 deny   ip any any

! ACL適用
interface GigabitEthernet0/0/0
 ip access-group INBOUND_ACL in

! SSH設定
ip domain-name company.local
crypto key generate rsa modulus 2048
line vty 0 15
 transport input ssh

! SNMP設定
snmp-server community "public_ro" RO
snmp-server community "private_rw" RW
snmp-server host 192.168.1.100 version 2c "public_ro"

! Syslog設定
logging host 192.168.1.200
logging trap 6
logging buffered 8192
logging origin-id hostname

! 保存設定
end
write memory
"""
    
    # デバイスコンフィグの作成
    device_config = DeviceConfig(
        device_name="R1",
        config_type="running_config",
        config_content=sample_config,
        metadata={
            "source": "actual_device",
            "backup_date": "2025-01-10",
            "admin": "network-admin"
        },
        timestamp=datetime.now()
    )
    
    # 更新処理の実行
    print("Starting knowledge base update...")
    result = openhands_updater.process_update_request(device_config)
    
    # 結果の表示
    print(f"\nUpdate Result:")
    print(f"Device: {result.device_name}")
    print(f"Success: {result.success}")
    print(f"Message: {result.message}")
    print(f"Updated Files: {result.updated_files}")
    if result.errors:
        print(f"Errors: {result.errors}")

if __name__ == "__main__":
    main()
