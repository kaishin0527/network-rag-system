

#!/usr/bin/env python3
"""
Automatic Knowledge Base Updater
ネットワーク装置から自動でコンフィグを取得しKBを更新する実装
"""

import os
import json
import yaml
import paramiko
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

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
class DeviceConnection:
    """装置接続情報"""
    hostname: str
    ip_address: str
    username: str
    password: str
    enable_password: str = ""
    device_type: str = "cisco_ios"
    port: int = 22
    timeout: int = 30

@dataclass
class AutoUpdateConfig:
    """自動更新設定"""
    update_interval: int = 3600  # 1時間
    max_retries: int = 3
    timeout: int = 300
    batch_size: int = 5
    enable_validation: bool = True
    backup_enabled: bool = True
    auto_commit: bool = True
    log_level: str = "INFO"
    output_dir: str = "/tmp/auto_kb_updates"
    excluded_devices: List[str] = None
    
    def __post_init__(self):
        if self.excluded_devices is None:
            self.excluded_devices = []

class NetworkConfigFetcher:
    """ネットワーク装置からコンフィグを取得するクラス"""
    
    def __init__(self, config: AutoUpdateConfig):
        self.config = config
        self.logger = self._setup_logger()
        self.ssh_pool = {}
    
    def _setup_logger(self) -> logging.Logger:
        """ロガーのセットアップ"""
        logger = logging.getLogger(__name__)
        logger.setLevel(getattr(logging, self.config.log_level))
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def create_ssh_client(self, device: DeviceConnection) -> paramiko.SSHClient:
        """SSHクライアントを作成する"""
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            client.connect(
                hostname=device.ip_address,
                port=device.port,
                username=device.username,
                password=device.password,
                timeout=device.timeout,
                look_for_keys=False,
                allow_agent=False
            )
            
            # 特権モードへの移行
            if device.enable_password:
                client.exec_command("enable")
                stdin, stdout, stderr = client.exec_command(f"enable {device.enable_password}")
                if "Password:" in stdout.channel.recv(1024).decode():
                    stdin.write(device.enable_password + "\n")
                    stdin.flush()
            
            return client
            
        except Exception as e:
            self.logger.error(f"Failed to create SSH client for {device.hostname}: {e}")
            raise
    
    def fetch_running_config(self, device: DeviceConnection) -> str:
        """実行コンフィグを取得する"""
        try:
            client = self.create_ssh_client(device)
            
            # コンフィグ取得コマンド
            stdin, stdout, stderr = client.exec_command("show running-config")
            config_content = stdout.read().decode('utf-8')
            
            # エラーチェック
            error_output = stderr.read().decode('utf-8')
            if error_output:
                self.logger.warning(f"Warning during config fetch for {device.hostname}: {error_output}")
            
            client.close()
            
            return config_content.strip()
            
        except Exception as e:
            self.logger.error(f"Failed to fetch config from {device.hostname}: {e}")
            raise
    
    def fetch_startup_config(self, device: DeviceConnection) -> str:
        """スタートアップコンフィグを取得する"""
        try:
            client = self.create_ssh_client(device)
            
            # コンフィグ取得コマンド
            stdin, stdout, stderr = client.exec_command("show startup-config")
            config_content = stdout.read().decode('utf-8')
            
            # エラーチェック
            error_output = stderr.read().decode('utf-8')
            if error_output:
                self.logger.warning(f"Warning during startup config fetch for {device.hostname}: {error_output}")
            
            client.close()
            
            return config_content.strip()
            
        except Exception as e:
            self.logger.error(f"Failed to fetch startup config from {device.hostname}: {e}")
            raise
    
    def fetch_device_info(self, device: DeviceConnection) -> Dict[str, Any]:
        """装置情報を取得する"""
        try:
            client = self.create_ssh_client(device)
            
            # 基本情報取得
            stdin, stdout, stderr = client.exec_command("show version | include Version")
            version_info = stdout.read().decode('utf-8').strip()
            
            # インターフェース情報取得
            stdin, stdout, stderr = client.exec_command("show ip interface brief")
            interface_info = stdout.read().decode('utf-8').strip()
            
            # ライセンス情報取得
            stdin, stdout, stderr = client.exec_command("show license")
            license_info = stdout.read().decode('utf-8').strip()
            
            client.close()
            
            return {
                "hostname": device.hostname,
                "ip_address": device.ip_address,
                "device_type": device.device_type,
                "version_info": version_info,
                "interface_info": interface_info,
                "license_info": license_info,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to fetch device info from {device.hostname}: {e}")
            raise
    
    async def fetch_multiple_configs(self, devices: List[DeviceConnection]) -> Dict[str, str]:
        """複数の装置からコンフィグを並行で取得する"""
        loop = asyncio.get_event_loop()
        
        def fetch_single_config(device):
            try:
                return device.hostname, self.fetch_running_config(device)
            except Exception as e:
                self.logger.error(f"Failed to fetch config from {device.hostname}: {e}")
                return device.hostname, None
        
        # スレッドプールを使用して並行処理
        with ThreadPoolExecutor(max_workers=len(devices)) as executor:
            futures = [
                loop.run_in_executor(executor, fetch_single_config, device)
                for device in devices
            ]
            
            results = {}
            for future in asyncio.as_completed(futures):
                hostname, config = await future
                if config:
                    results[hostname] = config
            
            return results

class AutoKBUpdater:
    """自動KB更新クラス"""
    
    def __init__(self, config: AutoUpdateConfig):
        self.config = config
        self.logger = self._setup_logger()
        self.config_fetcher = NetworkConfigFetcher(config)
        self.kb_updater = NetworkRAGKnowledgeUpdater()
        self.openhands_updater = OpenHandsKnowledgeUpdater(self.kb_updater)
        self.last_update_time = {}
        self.update_history = []
        
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
    
    def _setup_logger(self) -> logging.Logger:
        """ロガーのセットアップ"""
        logger = logging.getLogger(__name__)
        logger.setLevel(getattr(logging, self.config.log_level))
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def add_device(self, device: DeviceConnection):
        """装置を追加する"""
        if device.hostname in self.config.excluded_devices:
            self.logger.warning(f"Device {device.hostname} is excluded from updates")
            return
        
        self.last_update_time[device.hostname] = datetime.now() - timedelta(hours=24)
        self.logger.info(f"Added device: {device.hostname} ({device.ip_address})")
    
    def should_update_device(self, device: DeviceConnection) -> bool:
        """装置の更新が必要か判定する"""
        if device.hostname in self.config.excluded_devices:
            return False
        
        last_update = self.last_update_time.get(device.hostname)
        if not last_update:
            return True
        
        time_since_update = datetime.now() - last_update
        return time_since_update.total_seconds() >= self.config.update_interval
    
    async def update_single_device(self, device: DeviceConnection) -> UpdateResult:
        """単一の装置を更新する"""
        try:
            self.logger.info(f"Updating device: {device.hostname}")
            
            # コンフィグの取得
            config_content = self.config_fetcher.fetch_running_config(device)
            
            # メタデータの作成
            metadata = {
                "source": "auto_fetch",
                "fetch_date": datetime.now().isoformat(),
                "device_ip": device.ip_address,
                "device_type": device.device_type,
                "auto_update": True
            }
            
            # デバイスコンフィグの作成
            device_config = DeviceConfig(
                device_name=device.hostname,
                config_type="running_config",
                config_content=config_content,
                metadata=metadata,
                timestamp=datetime.now()
            )
            
            # KB更新の実行
            result = self.openhands_updater.process_update_request(device_config)
            
            # 更新時間の記録
            if result.success:
                self.last_update_time[device.hostname] = datetime.now()
            
            # 更新履歴の記録
            self.update_history.append({
                "device_name": device.hostname,
                "update_time": datetime.now().isoformat(),
                "success": result.success,
                "message": result.message,
                "updated_files": result.updated_files
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to update device {device.hostname}: {e}")
            return UpdateResult(
                device_name=device.hostname,
                success=False,
                message=f"Update failed: {str(e)}",
                updated_files=[],
                errors=[str(e)]
            )
    
    async def update_all_devices(self, devices: List[DeviceConnection]) -> List[UpdateResult]:
        """すべての装置を更新する"""
        results = []
        
        # 更新が必要な装置をフィルタリング
        devices_to_update = [
            device for device in devices 
            if self.should_update_device(device)
        ]
        
        if not devices_to_update:
            self.logger.info("No devices require updates")
            return results
        
        self.logger.info(f"Updating {len(devices_to_update)} devices")
        
        # バッチ処理で更新を実行
        for i in range(0, len(devices_to_update), self.config.batch_size):
            batch_devices = devices_to_update[i:i + self.config.batch_size]
            
            # バッチの並行処理
            batch_results = await asyncio.gather(*[
                self.update_single_device(device) for device in batch_devices
            ], return_exceptions=True)
            
            # 結果の処理
            for result in batch_results:
                if isinstance(result, Exception):
                    self.logger.error(f"Batch processing error: {result}")
                else:
                    results.append(result)
        
        return results
    
    def generate_update_report(self) -> Dict[str, Any]:
        """更新レポートを生成する"""
        report = {
            "generated_at": datetime.now().isoformat(),
            "config": asdict(self.config),
            "total_devices": len(self.last_update_time),
            "excluded_devices": self.config.excluded_devices,
            "last_update_times": {
                hostname: time.isoformat() 
                for hostname, time in self.last_update_time.items()
            },
            "recent_updates": self.update_history[-10:],  # 最近の10件
            "statistics": {
                "total_updates": len(self.update_history),
                "successful_updates": len([u for u in self.update_history if u["success"]]),
                "failed_updates": len([u for u in self.update_history if not u["success"]])
            }
        }
        
        return report
    
    def save_report(self, report: Dict[str, Any], filename: str = None) -> str:
        """レポートを保存する"""
        if filename is None:
            filename = f"auto_kb_update_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        output_dir = Path(self.config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = output_dir / filename
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Report saved: {report_file}")
        return str(report_file)

def main():
    """メイン関数"""
    # 自動更新設定
    auto_config = AutoUpdateConfig(
        update_interval=3600,  # 1時間
        max_retries=3,
        timeout=300,
        batch_size=2,
        enable_validation=True,
        backup_enabled=True,
        auto_commit=True,
        log_level="INFO",
        output_dir="/tmp/auto_kb_updates",
        excluded_devices=["TEST-DEVICE-1", "TEST-DEVICE-2"]
    )
    
    # 自動KBアップデーターの初期化
    auto_updater = AutoKBUpdater(auto_config)
    
    # サンプル装置接続情報
    sample_devices = [
        DeviceConnection(
            hostname="R1",
            ip_address="192.168.1.1",
            username="admin",
            password="password",
            enable_password="enable_password",
            device_type="cisco_ios"
        ),
        DeviceConnection(
            hostname="SW1",
            ip_address="192.168.1.10",
            username="admin",
            password="password",
            enable_password="enable_password",
            device_type="cisco_ios"
        ),
        DeviceConnection(
            hostname="R2",
            ip_address="192.168.1.2",
            username="admin",
            password="password",
            enable_password="enable_password",
            device_type="cisco_ios"
        )
    ]
    
    # 装置の追加
    for device in sample_devices:
        auto_updater.add_device(device)
    
    print("Starting Automatic Knowledge Base Update...")
    print(f"Configuration: {auto_config.update_interval} seconds interval")
    print(f"Devices to monitor: {len(sample_devices)}")
    
    # 非同期で更新を実行
    async def run_update():
        results = await auto_updater.update_all_devices(sample_devices)
        return results
    
    # イベントループの実行
    try:
        results = asyncio.run(run_update())
    except KeyboardInterrupt:
        print("\nUpdate interrupted by user")
    except Exception as e:
        print(f"Update failed: {e}")
    
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
    report = auto_updater.generate_update_report()
    report_file = auto_updater.save_report(report)
    
    print(f"\nUpdate report saved to: {report_file}")
    
    # レポートのサマリー
    print(f"\nReport Summary:")
    print(f"Total devices: {report['total_devices']}")
    print(f"Successful updates: {report['statistics']['successful_updates']}")
    print(f"Failed updates: {report['statistics']['failed_updates']}")
    print(f"Total updates: {report['statistics']['total_updates']}")

if __name__ == "__main__":
    main()

