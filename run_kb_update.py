


#!/usr/bin/env python3
"""
Knowledge Base Update Runner
KB更新機能の統合実行スクリプト
"""

import os
import sys
import json
import yaml
import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

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

from knowledge_updater import NetworkRAGKnowledgeUpdater, OpenHandsKnowledgeUpdater, DeviceConfig, UpdateResult
from openhands_kb_updater_example import OpenHandsKBUpdateAgent
from auto_kb_updater import AutoKBUpdater, AutoUpdateConfig, DeviceConnection

class KBUpdateRunner:
    """KB更新ランナー"""
    
    def __init__(self, config_file: str = None):
        self.config = self._load_config(config_file)
        self.logger = self._setup_logger()
        self.output_dir = Path(self.config.get("output_dir", "/tmp/kb_updates"))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # コンポーネントの初期化
        self.kb_updater = NetworkRAGKnowledgeUpdater()
        self.openhands_updater = OpenHandsKnowledgeUpdater(self.kb_updater)
        self.agent = OpenHandsKBUpdateAgent(self.config.get("agent", {}))
        
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
    
    def _load_config(self, config_file: str = None) -> Dict[str, Any]:
        """設定ファイルを読み込む"""
        default_config = {
            "output_dir": "/tmp/kb_updates",
            "log_level": "INFO",
            "agent": {
                "max_retries": 3,
                "timeout": 300,
                "batch_size": 5,
                "enable_validation": True,
                "backup_enabled": True,
                "auto_commit": True
            },
            "auto_update": {
                "update_interval": 3600,
                "max_retries": 3,
                "timeout": 300,
                "batch_size": 5,
                "enable_validation": True,
                "backup_enabled": True,
                "auto_commit": True,
                "excluded_devices": []
            }
        }
        
        if config_file and Path(config_file).exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                if config_file.endswith('.json'):
                    user_config = json.load(f)
                elif config_file.endswith('.yml') or config_file.endswith('.yaml'):
                    user_config = yaml.safe_load(f)
                else:
                    raise ValueError(f"Unsupported config file format: {config_file}")
            
            # 設定のマージ
            default_config.update(user_config)
        
        return default_config
    
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
    
    def run_manual_update(self, config_data: Dict[str, Any]) -> UpdateResult:
        """手動更新を実行する"""
        try:
            self.logger.info("Starting manual KB update...")
            
            # デバイスコンフィグの作成
            device_config = DeviceConfig(
                device_name=config_data["device_name"],
                config_type=config_data["config_type"],
                config_content=config_data["config_content"],
                metadata=config_data.get("metadata", {}),
                timestamp=datetime.now()
            )
            
            # 更新処理の実行
            result = self.openhands_updater.process_update_request(device_config)
            
            self.logger.info(f"Manual update completed: {result.device_name} - {result.success}")
            return result
            
        except Exception as e:
            self.logger.error(f"Manual update failed: {e}")
            return UpdateResult(
                device_name=config_data.get("device_name", "unknown"),
                success=False,
                message=f"Manual update failed: {str(e)}",
                updated_files=[],
                errors=[str(e)]
            )
    
    def run_batch_update(self, configs: List[Dict[str, Any]]) -> List[UpdateResult]:
        """バッチ更新を実行する"""
        try:
            self.logger.info(f"Starting batch KB update for {len(configs)} devices...")
            
            # バッチ更新の実行
            results = self.agent.batch_update_from_configs(configs)
            
            successful = len([r for r in results if r.success])
            failed = len([r for r in results if not r.success])
            
            self.logger.info(f"Batch update completed: {successful} successful, {failed} failed")
            return results
            
        except Exception as e:
            self.logger.error(f"Batch update failed: {e}")
            return []
    
    def run_auto_update(self, devices: List[Dict[str, Any]]) -> List[UpdateResult]:
        """自動更新を実行する"""
        try:
            self.logger.info("Starting automatic KB update...")
            
            # 自動更新設定の作成
            auto_config = AutoUpdateConfig(**self.config.get("auto_update", {}))
            
            # 自動KBアップデーターの初期化
            auto_updater = AutoKBUpdater(auto_config)
            
            # 装置接続情報の作成
            device_connections = []
            for device_data in devices:
                device = DeviceConnection(
                    hostname=device_data["hostname"],
                    ip_address=device_data["ip_address"],
                    username=device_data["username"],
                    password=device_data["password"],
                    enable_password=device_data.get("enable_password", ""),
                    device_type=device_data.get("device_type", "cisco_ios"),
                    port=device_data.get("port", 22),
                    timeout=device_data.get("timeout", 30)
                )
                device_connections.append(device)
                auto_updater.add_device(device)
            
            # 非同期更新の実行
            import asyncio
            
            async def run_update():
                return await auto_updater.update_all_devices(device_connections)
            
            results = asyncio.run(run_update())
            
            successful = len([r for r in results if r.success])
            failed = len([r for r in results if not r.success])
            
            self.logger.info(f"Auto update completed: {successful} successful, {failed} failed")
            return results
            
        except Exception as e:
            self.logger.error(f"Auto update failed: {e}")
            return []
    
    def generate_report(self, results: List[UpdateResult], report_type: str = "summary") -> Dict[str, Any]:
        """レポートを生成する"""
        report = {
            "report_type": report_type,
            "generated_at": datetime.now().isoformat(),
            "total_results": len(results),
            "successful_results": len([r for r in results if r.success]),
            "failed_results": len([r for r in results if not r.success]),
            "results": []
        }
        
        for result in results:
            result_info = {
                "device_name": result.device_name,
                "success": result.success,
                "message": result.message,
                "updated_files": result.updated_files,
                "errors": result.errors
            }
            report["results"].append(result_info)
        
        return report
    
    def save_report(self, report: Dict[str, Any], filename: str = None) -> str:
        """レポートを保存する"""
        if filename is None:
            filename = f"kb_update_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report_file = self.output_dir / filename
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Report saved: {report_file}")
        return str(report_file)
    
    def validate_config(self, config_data: Dict[str, Any]) -> bool:
        """設定データの検証"""
        required_fields = ["device_name", "config_type", "config_content"]
        
        for field in required_fields:
            if field not in config_data:
                self.logger.error(f"Missing required field: {field}")
                return False
        
        return True

def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description="Knowledge Base Update Runner")
    parser.add_argument("--config", "-c", help="Configuration file path")
    parser.add_argument("--mode", "-m", choices=["manual", "batch", "auto"], 
                       default="manual", help="Update mode")
    parser.add_argument("--input", "-i", help="Input file path")
    parser.add_argument("--output", "-o", help="Output directory")
    parser.add_argument("--report", "-r", action="store_true", help="Generate report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # ランナーの初期化
    runner = KBUpdateRunner(args.config)
    
    # ログレベルの設定
    if args.verbose:
        runner.logger.setLevel(logging.DEBUG)
    
    # 出力ディレクトリの設定
    if args.output:
        runner.output_dir = Path(args.output)
        runner.output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"KB Update Runner - Mode: {args.mode}")
    print(f"Output directory: {runner.output_dir}")
    
    results = []
    
    try:
        if args.mode == "manual":
            # 手動更新モード
            if not args.input:
                print("Error: Input file required for manual mode")
                sys.exit(1)
            
            if not Path(args.input).exists():
                print(f"Error: Input file not found: {args.input}")
                sys.exit(1)
            
            # 設定ファイルの読み込み
            with open(args.input, 'r', encoding='utf-8') as f:
                if args.input.endswith('.json'):
                    config_data = json.load(f)
                elif args.input.endswith('.yml') or args.input.endswith('.yaml'):
                    config_data = yaml.safe_load(f)
                else:
                    print("Error: Unsupported input file format")
                    sys.exit(1)
            
            # 設定の検証
            if not runner.validate_config(config_data):
                print("Error: Invalid configuration data")
                sys.exit(1)
            
            # 更新の実行
            result = runner.run_manual_update(config_data)
            results.append(result)
            
            print(f"Manual update completed: {result.device_name} - {result.success}")
            
        elif args.mode == "batch":
            # バッチ更新モード
            if not args.input:
                print("Error: Input file required for batch mode")
                sys.exit(1)
            
            if not Path(args.input).exists():
                print(f"Error: Input file not found: {args.input}")
                sys.exit(1)
            
            # 設定ファイルの読み込み
            with open(args.input, 'r', encoding='utf-8') as f:
                if args.input.endswith('.json'):
                    configs = json.load(f)
                elif args.input.endswith('.yml') or args.input.endswith('.yaml'):
                    configs = yaml.safe_load(f)
                else:
                    print("Error: Unsupported input file format")
                    sys.exit(1)
            
            if not isinstance(configs, list):
                print("Error: Batch mode requires a list of configurations")
                sys.exit(1)
            
            # 更新の実行
            results = runner.run_batch_update(configs)
            
            successful = len([r for r in results if r.success])
            failed = len([r for r in results if not r.success])
            
            print(f"Batch update completed: {successful} successful, {failed} failed")
            
        elif args.mode == "auto":
            # 自動更新モード
            if not args.input:
                print("Error: Input file required for auto mode")
                sys.exit(1)
            
            if not Path(args.input).exists():
                print(f"Error: Input file not found: {args.input}")
                sys.exit(1)
            
            # 設定ファイルの読み込み
            with open(args.input, 'r', encoding='utf-8') as f:
                if args.input.endswith('.json'):
                    devices = json.load(f)
                elif args.input.endswith('.yml') or args.input.endswith('.yaml'):
                    devices = yaml.safe_load(f)
                else:
                    print("Error: Unsupported input file format")
                    sys.exit(1)
            
            if not isinstance(devices, list):
                print("Error: Auto mode requires a list of device configurations")
                sys.exit(1)
            
            # 更新の実行
            results = runner.run_auto_update(devices)
            
            successful = len([r for r in results if r.success])
            failed = len([r for r in results if not r.success])
            
            print(f"Auto update completed: {successful} successful, {failed} failed")
        
        # レポートの生成
        if args.report and results:
            report = runner.generate_report(results, args.mode)
            report_file = runner.save_report(report)
            print(f"Report saved to: {report_file}")
            
            # レポートのサマリー表示
            print(f"\nReport Summary:")
            print(f"Total results: {report['total_results']}")
            print(f"Successful: {report['successful_results']}")
            print(f"Failed: {report['failed_results']}")
        
        # 詳細結果の表示
        if results:
            print(f"\nDetailed Results:")
            for result in results:
                print(f"Device: {result.device_name}")
                print(f"Success: {result.success}")
                print(f"Message: {result.message}")
                if result.updated_files:
                    print(f"Updated files: {result.updated_files}")
                if result.errors:
                    print(f"Errors: {result.errors}")
                print("-" * 50)
    
    except Exception as e:
        print(f"Error: {e}")
        runner.logger.error(f"Update failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

