

#!/usr/bin/env python3
"""
OpenHands Knowledge Base Updater Example
OpenhandsからKBの装置情報を更新する具体的な実装例
"""

import os
import json
import yaml
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

# OpenHands関連のインポート
try:
    from openhands.core.schema import AgentAction, AgentObservation
    from openhands.core.logger import print_system_log
    from openhands.core.config import AgentConfig
    from openhands.agents import Agent
    OPENHANDS_AVAILABLE = True
except ImportError:
    print("Warning: OpenHands not available. Using dummy implementation.")
    OPENHANDS_AVAILABLE = False

# Network RAG System関連のインポート
try:
    from src.rag_system import NetworkRAGSystem
    from src.config_generator import NetworkConfigGenerator
    RAG_AVAILABLE = True
except ImportError:
    print("Warning: Network RAG System not available. Using dummy implementation.")
    RAG_AVAILABLE = False

from knowledge_updater import (
    NetworkRAGKnowledgeUpdater, 
    OpenHandsKnowledgeUpdater, 
    DeviceConfig, 
    UpdateResult
)

@dataclass
class KBUpdateTask:
    """KB更新タスク"""
    task_id: str
    device_name: str
    config_type: str
    config_content: str
    metadata: Dict[str, Any]
    priority: str = "normal"
    status: str = "pending"
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

class OpenHandsKBUpdateAgent:
    """OpenHands用のKB更新エージェント"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._default_config()
        self.logger = self._setup_logger()
        self.kb_updater = NetworkRAGKnowledgeUpdater()
        self.openhands_updater = OpenHandsKnowledgeUpdater(self.kb_updater)
        self.task_queue = []
        self.completed_tasks = []
        
        # Network RAG Systemの初期化
        if RAG_AVAILABLE:
            try:
                self.rag_system = NetworkRAGSystem()
                self.config_generator = NetworkConfigGenerator()
                self.logger.info("Network RAG System initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize RAG system: {e}")
                self.rag_system = None
                self.config_generator = None
        else:
            self.rag_system = None
            self.config_generator = None
    
    def _default_config(self) -> Dict[str, Any]:
        """デフォルト設定"""
        return {
            "max_retries": 3,
            "timeout": 300,
            "batch_size": 5,
            "enable_validation": True,
            "log_level": "INFO",
            "output_dir": "/tmp/kb_updates",
            "backup_enabled": True,
            "auto_commit": True
        }
    
    def _setup_logger(self) -> logging.Logger:
        """ロガーのセットアップ"""
        logger = logging.getLogger(__name__)
        logger.setLevel(getattr(logging, self.config.get("log_level", "INFO")))
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def add_update_task(self, device_config: DeviceConfig, priority: str = "normal") -> str:
        """更新タスクを追加する"""
        task_id = f"kb_update_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{device_config.device_name}"
        
        task = KBUpdateTask(
            task_id=task_id,
            device_name=device_config.device_name,
            config_type=device_config.config_type,
            config_content=device_config.config_content,
            metadata=device_config.metadata,
            priority=priority,
            status="pending"
        )
        
        self.task_queue.append(task)
        self.logger.info(f"Added update task: {task_id} for device {device_config.device_name}")
        
        return task_id
    
    def process_task_queue(self) -> List[UpdateResult]:
        """タスクキューを処理する"""
        results = []
        
        while self.task_queue:
            task = self.task_queue.pop(0)
            self.logger.info(f"Processing task: {task.task_id}")
            
            try:
                # タスクの状態を更新
                task.status = "processing"
                
                # デバイスコンフィグの作成
                device_config = DeviceConfig(
                    device_name=task.device_name,
                    config_type=task.config_type,
                    config_content=task.config_content,
                    metadata=task.metadata,
                    timestamp=datetime.now()
                )
                
                # 更新処理の実行
                result = self.openhands_updater.process_update_request(device_config)
                
                # タスクの状態を更新
                task.status = "completed" if result.success else "failed"
                
                # 結果の保存
                results.append(result)
                self.completed_tasks.append(task)
                
                self.logger.info(f"Task completed: {task.task_id} - Success: {result.success}")
                
            except Exception as e:
                self.logger.error(f"Task failed: {task.task_id} - Error: {e}")
                
                # エラーレザルトの作成
                result = UpdateResult(
                    device_name=task.device_name,
                    success=False,
                    message=f"Task processing failed: {str(e)}",
                    updated_files=[],
                    errors=[str(e)]
                )
                
                # タスクの状態を更新
                task.status = "failed"
                results.append(result)
                self.completed_tasks.append(task)
        
        return results
    
    def create_openhands_prompt(self, task: KBUpdateTask) -> str:
        """OpenHands用のプロンプトを作成する"""
        prompt = f"""
Network RAG System Knowledge Base Update Task

=== Task Information ===
Task ID: {task.task_id}
Device Name: {task.device_name}
Config Type: {task.config_type}
Priority: {task.priority}
Status: {task.status}
Created At: {task.created_at.strftime('%Y-%m-%d %H:%M:%S')}

=== Device Configuration ===
{task.config_content}

=== Metadata ===
{json.dumps(task.metadata, indent=2, ensure_ascii=False)}

=== Update Instructions ===

You are a Network RAG System Knowledge Base Updater. Your task is to analyze the provided device configuration and update the knowledge base accordingly.

Please perform the following steps:

1. **Configuration Analysis**:
   - Analyze the device configuration structure
   - Identify device type and model information
   - Extract interface configurations and IP assignments
   - Identify routing protocols and configurations
   - Document security policies and ACLs
   - Record management settings (SNMP, NTP, SSH, etc.)

2. **Knowledge Base Updates**:
   - Update device policy file: `knowledge-base/devices/{task.device_name}_policy.md`
   - Update configuration template: `knowledge-base/devices/{task.device_name}_config_template.yml`
   - Save raw configuration: `knowledge-base/devices/device_configs/{task.device_name}_running_config_{datetime.now().strftime('%Y-%m-%d')}.txt`

3. **File Format Requirements**:
   - Device policy: Markdown format with sections for basic info, configuration, and best practices
   - Config template: YAML format with structured data and metadata
   - Raw config: Cisco IOS format with metadata header

4. **Validation**:
   - Ensure all configuration sections are properly documented
   - Validate that IP addresses and interfaces are correctly identified
   - Check that routing protocols are properly categorized
   - Verify that security policies are accurately described

5. **Output Requirements**:
   - Provide the complete updated content for each file
   - Confirm which files were successfully updated
   - Report any validation errors or issues
   - Include a summary of changes made

Please proceed with the knowledge base update and provide a detailed report of your actions and results.

=== Expected Output Format ===

Update Report for {task.device_name}:
==========================================

1. Files Updated:
   - [ ] knowledge-base/devices/{task.device_name}_policy.md
   - [ ] knowledge-base/devices/{task.device_name}_config_template.yml
   - [ ] knowledge-base/devices/device_configs/{task.device_name}_running_config_{datetime.now().strftime('%Y-%m-%d')}.txt

2. Configuration Analysis:
   - Device Type: [Identified device type]
   - Interfaces: [List of interfaces]
   - IP Addresses: [List of IP assignments]
   - Routing Protocols: [List of protocols]
   - Security Policies: [List of ACLs and policies]
   - Management Settings: [List of management configurations]

3. Updated File Contents:
   [Provide the complete content for each updated file]

4. Validation Results:
   - [ ] All configuration sections documented
   - [ ] IP addresses and interfaces correctly identified
   - [ ] Routing protocols properly categorized
   - [ ] Security policies accurately described

5. Summary:
   [Summary of changes made and any issues encountered]

Please proceed with the update.
"""
        return prompt
    
    def process_with_openhands_agent(self, task: KBUpdateTask) -> UpdateResult:
        """OpenHandsエージェントを使用してタスクを処理する"""
        try:
            if not OPENHANDS_AVAILABLE:
                return self._process_with_dummy(task)
            
            # OpenHands用のプロンプトを作成
            prompt = self.create_openhands_prompt(task)
            
            # ここで実際のOpenHandsエージェントを使用して処理を実行
            # 実際の実装では、OpenHandsのエージェントがプロンプトを処理し、
            # ファイルを更新するアクションを実行
            
            # ダミーの実装として、直接アップデーターを使用
            device_config = DeviceConfig(
                device_name=task.device_name,
                config_type=task.config_type,
                config_content=task.config_content,
                metadata=task.metadata,
                timestamp=datetime.now()
            )
            
            result = self.kb_updater.update_device_info(device_config)
            
            return result
            
        except Exception as e:
            self.logger.error(f"OpenHands agent processing failed: {e}")
            return UpdateResult(
                device_name=task.device_name,
                success=False,
                message=f"OpenHands processing failed: {str(e)}",
                updated_files=[],
                errors=[str(e)]
            )
    
    def _process_with_dummy(self, task: KBUpdateTask) -> UpdateResult:
        """ダミーの処理"""
        print(f"Dummy processing for task: {task.task_id}")
        print(f"Device: {task.device_name}")
        print(f"Config type: {task.config_type}")
        print(f"Config length: {len(task.config_content)} characters")
        
        # ダミーの成功結果
        return UpdateResult(
            device_name=task.device_name,
            success=True,
            message="Dummy update completed successfully",
            updated_files=[
                f"devices/{task.device_name}_policy.md",
                f"devices/{task.device_name}_config_template.yml",
                f"devices/device_configs/{task.device_name}_running_config_{datetime.now().strftime('%Y-%m-%d')}.txt"
            ],
            errors=[]
        )
    
    def batch_update_from_configs(self, configs: List[Dict[str, Any]]) -> List[UpdateResult]:
        """複数のコンフィグからバッチ更新を実行する"""
        results = []
        
        for config_data in configs:
            device_config = DeviceConfig(
                device_name=config_data["device_name"],
                config_type=config_data["config_type"],
                config_content=config_data["config_content"],
                metadata=config_data.get("metadata", {}),
                timestamp=datetime.now()
            )
            
            task_id = self.add_update_task(device_config, config_data.get("priority", "normal"))
        
        # タスクキューの処理
        results = self.process_task_queue()
        
        return results
    
    def generate_update_report(self) -> Dict[str, Any]:
        """更新レポートを生成する"""
        report = {
            "total_tasks": len(self.completed_tasks),
            "successful_tasks": len([t for t in self.completed_tasks if t.status == "completed"]),
            "failed_tasks": len([t for t in self.completed_tasks if t.status == "failed"]),
            "pending_tasks": len([t for t in self.completed_tasks if t.status == "pending"]),
            "completed_at": datetime.now().isoformat(),
            "tasks": []
        }
        
        for task in self.completed_tasks:
            task_info = {
                "task_id": task.task_id,
                "device_name": task.device_name,
                "config_type": task.config_type,
                "priority": task.priority,
                "status": task.status,
                "created_at": task.created_at.isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            report["tasks"].append(task_info)
        
        return report
    
    def save_report(self, report: Dict[str, Any], filename: str = None) -> str:
        """レポートを保存する"""
        if filename is None:
            filename = f"kb_update_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        output_dir = Path(self.config["output_dir"])
        output_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = output_dir / filename
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Report saved: {report_file}")
        return str(report_file)

def main():
    """メイン関数"""
    # エージェントの初期化
    agent = OpenHandsKBUpdateAgent()
    
    # サンプルコンフィグデータ
    sample_configs = [
        {
            "device_name": "R1",
            "config_type": "running_config",
            "config_content": """
! Router R1 Configuration
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
""",
            "metadata": {
                "source": "actual_device",
                "backup_date": "2025-01-10",
                "admin": "network-admin",
                "location": "Data Center A"
            },
            "priority": "high"
        },
        {
            "device_name": "SW1",
            "config_type": "running_config",
            "config_content": """
! Switch SW1 Configuration
hostname SW1
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

! VLAN設定
vlan 10
 name Management
vlan 20
 name Sales
vlan 30
 name Development
vlan 40
 name Guest

! インターフェース設定
interface Vlan10
 description Management Network
 ip address 192.168.100.10 255.255.255.0

interface Vlan20
 description Sales Network
 ip address 10.1.20.1 255.255.255.0

interface Vlan30
 description Development Network
 ip address 10.1.30.1 255.255.255.0

interface Vlan40
 description Guest Network
 ip address 10.1.40.1 255.255.255.0

! ポートチャネル設定
interface Port-channel1
 description Uplink to R1
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30,40

interface range GigabitEthernet1/1-2
 channel-group 1 mode active

! OSPF設定
router ospf 1
 router-id 10.1.10.10
 log-adjacency-changes
 network 10.1.10.0 0.0.0.255 area 0
 network 192.168.100.0 0.0.0.255 area 0
 passive-interface Vlan10
 passive-interface Vlan20
 passive-interface Vlan30
 passive-interface Vlan40

! セキュリティ設定
ip access-list extended INBOUND_ACL
 permit tcp 10.1.20.0 0.0.0.255 10.1.30.0 0.0.0.255 eq 22
 permit tcp 10.1.30.0 0.0.0.255 10.1.20.0 0.0.0.255 eq 22
 deny   ip any any

! ACL適用
interface Vlan20
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
""",
            "metadata": {
                "source": "actual_device",
                "backup_date": "2025-01-10",
                "admin": "network-admin",
                "location": "Data Center A"
            },
            "priority": "normal"
        }
    ]
    
    print("Starting OpenHands Knowledge Base Update...")
    print(f"Processing {len(sample_configs)} device configurations")
    
    # バッチ更新の実行
    results = agent.batch_update_from_configs(sample_configs)
    
    # 結果の表示
    print(f"\nUpdate Results:")
    print(f"Total devices processed: {len(results)}")
    print(f"Successful updates: {len([r for r in results if r.success])}")
    print(f"Failed updates: {len([r for r in results if not r.success])}")
    
    for result in results:
        print(f"\nDevice: {result.device_name}")
        print(f"Success: {result.success}")
        print(f"Message: {result.message}")
        if result.updated_files:
            print(f"Updated files: {result.updated_files}")
        if result.errors:
            print(f"Errors: {result.errors}")
    
    # レポートの生成と保存
    report = agent.generate_update_report()
    report_file = agent.save_report(report)
    
    print(f"\nUpdate report saved to: {report_file}")
    
    # レポートのサマリー
    print(f"\nReport Summary:")
    print(f"Total tasks: {report['total_tasks']}")
    print(f"Successful: {report['successful_tasks']}")
    print(f"Failed: {report['failed_tasks']}")
    print(f"Pending: {report['pending_tasks']}")

if __name__ == "__main__":
    main()
