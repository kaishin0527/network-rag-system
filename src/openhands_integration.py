



#!/usr/bin/env python3
# openhands_integration.py
from .openhands_agent import NetworkConfigAgent
from typing import List, Dict, Any
import asyncio
import json
from datetime import datetime

class OpenHandsIntegration:
    """OpenHandsエージェントとの統合クラス"""
    
    def __init__(self, config_path: str = "config/openhands_config.yaml"):
        self.agent = NetworkConfigAgent(config_path)
        self.task_queue = []
        self.completed_tasks = []
    
    async def process_batch_queries(self, queries: List[str]) -> List[Dict[str, Any]]:
        """バッチクエリの処理"""
        results = []
        
        for query in queries:
            try:
                result = await asyncio.to_thread(
                    self.agent.process_network_query, 
                    query
                )
                results.append(result)
                self.completed_tasks.append(result)
            except Exception as e:
                results.append({
                    'task_id': query,
                    'error': str(e),
                    'status': 'failed',
                    'timestamp': datetime.now().isoformat()
                })
        
        return results
    
    def process_single_query(self, query: str) -> Dict[str, Any]:
        """単一クエリの処理"""
        try:
            result = self.agent.process_network_query(query)
            self.completed_tasks.append(result)
            return result
        except Exception as e:
            return {
                'task_id': query,
                'error': str(e),
                'status': 'failed',
                'timestamp': datetime.now().isoformat()
            }
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """タスクの状態を取得"""
        for task in self.completed_tasks:
            if task.get('task_id') == task_id:
                return task
        return {'status': 'pending'}
    
    def get_statistics(self) -> Dict[str, Any]:
        """処理統計を取得"""
        total = len(self.completed_tasks)
        completed = sum(1 for task in self.completed_tasks if task.get('status') == 'completed')
        failed = sum(1 for task in self.completed_tasks if task.get('status') == 'failed')
        
        return {
            'total_tasks': total,
            'completed_tasks': completed,
            'failed_tasks': failed,
            'success_rate': completed / total if total > 0 else 0
        }
    
    def get_completed_configs(self) -> List[Dict[str, Any]]:
        """完了したコンフィグを取得"""
        return [
            task for task in self.completed_tasks 
            if task.get('status') == 'completed' and 'config_content' in task
        ]
    
    def save_results_to_file(self, filename: str = "openhands_results.json") -> str:
        """結果をファイルに保存"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'statistics': self.get_statistics(),
            'completed_tasks': self.get_completed_configs(),
            'all_tasks': self.completed_tasks
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        return filename



