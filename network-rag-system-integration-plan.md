
# Network RAG System + OpenHands Integration Plan

## 概要

このドキュメントでは、network-rag-systemをOpenHandsと連携させるための具体的な構成と実装計画を提案します。Ubuntu VM上にOpenHandsをデプロイし、社内LLMとAPI連携させながら、ネットワーク工事時の追加コンフィグを生成するためのソリューションです。

## システムアーキテクチャ

### 1. 全体構成

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   OpenHands     │    │  Network RAG    │    │   Knowledge     │
│   Agent         │◄──►│   System        │◄──►│   Base          │
│                 │    │                 │    │                 │
│ - Ubuntu VM     │    │ - RAG Engine    │    │ - Device Policies│
│ - LLM API Client│    │ - Config Gen    │    │ - Templates     │
│ - Web Interface │    │ - Validation    │    │ - Validation    │
│ - API Server    │    │                 │    │   Rules         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Internal      │    │   Network       │    │   Network       │
│   LLM API       │    │   Devices       │    │   Monitoring    │
│                 │    │                 │    │   System        │
│ - 社内LLM       │    │ - R1, R2, SW1   │    │ - Syslog        │
│ - API Gateway   │    │ - Configuration │    │ - SNMP          │
│ - Authentication│    │   Management    │    │ - Monitoring    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 2. デプロイ構成

#### 2.1 Ubuntu VM環境
- **OS**: Ubuntu 22.04 LTS
- **Python**: 3.8+
- **Docker**: コンテナ化されたサービス管理
- **Docker Compose**: サービスオーケストレーション

#### 2.2 コンポーネント構成
1. **OpenHands Agent Service**
2. **Network RAG System Service**
3. **LLM API Gateway Service**
4. **Web Interface Service**
5. **Knowledge Base Management Service**

## 実装計画

### Phase 1: 基盤構築

#### 1.1 環境セットアップ
```bash
# Ubuntu VM上での環境構築
sudo apt update
sudo apt install -y python3.8 python3.8-venv python3-pip docker.io docker-compose

# Python仮想環境の作成
python3.8 -m venv openhands-env
source openhands-env/bin/activate

# 依存関係のインストール
pip install -r requirements/base.txt
pip install openhands
```

#### 1.2 Docker Compose設定
```yaml
# docker-compose.yml
version: '3.8'

services:
  openhands-agent:
    build: ./openhands
    ports:
      - "8001:8000"
    environment:
      - LLM_API_URL=http://llm-gateway:8000
      - RAG_API_URL=http://rag-system:8002
    volumes:
      - ./openhands:/app
    depends_on:
      - llm-gateway
      - rag-system

  rag-system:
    build: ./network-rag-system
    ports:
      - "8002:8000"
    volumes:
      - ./network-rag-system:/app
      - ./knowledge-base:/app/knowledge-base
    environment:
      - KB_DIR=/app/knowledge-base

  llm-gateway:
    build: ./llm-gateway
    ports:
      - "8000:8000"
    environment:
      - LLM_MODEL=internal-model
      - LLM_API_KEY=your-api-key
      - AUTH_ENABLED=true

  web-interface:
    build: ./web-interface
    ports:
      - "3000:3000"
    depends_on:
      - openhands-agent
      - rag-system
```

### Phase 2: OpenHands連携

#### 2.1 OpenHandsカスタムエージェントの実装
```python
# openhands_agent.py
from openhands import Agent
from network_rag_system.src.rag_system import NetworkRAGSystem
from network_rag_system.src.config_generator import NetworkConfigGenerator
import requests

class NetworkConfigAgent(Agent):
    def __init__(self, llm_api_url, rag_api_url):
        super().__init__()
        self.llm_api_url = llm_api_url
        self.rag_api_url = rag_api_url
        self.rag_system = NetworkRAGSystem()
        self.config_generator = NetworkConfigGenerator()
        
    def process_network_query(self, query: str) -> dict:
        """ネットワーククエリの処理"""
        try:
            # 1. RAGシステムで関連情報を検索
            relevant_info = self.rag_system.retrieve_relevant_info(query)
            
            # 2. プロンプトを生成
            prompt = self.rag_system.generate_config_prompt(query)
            
            # 3. LLM APIでコンフィグを生成
            config_content = self._call_llm_api(prompt)
            
            # 4. コンフィグの検証
            validation_result = self.config_generator._validate_config(config_content)
            
            return {
                'query': query,
                'config_content': config_content,
                'validation_result': validation_result,
                'relevant_info': relevant_info
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _call_llm_api(self, prompt: str) -> str:
        """LLM APIの呼び出し"""
        payload = {
            'prompt': prompt,
            'max_tokens': 2000,
            'temperature': 0.1
        }
        
        response = requests.post(
            f"{self.llm_api_url}/generate",
            json=payload,
            headers={'Authorization': f'Bearer {self.api_key}'}
        )
        
        if response.status_code == 200:
            return response.json()['text']
        else:
            raise Exception(f"LLM API Error: {response.status_code}")
```

#### 2.2 APIサーバーの実装
```python
# api_server.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openhands_agent import NetworkConfigAgent

app = FastAPI()
agent = NetworkConfigAgent(
    llm_api_url="http://localhost:8000",
    rag_api_url="http://localhost:8002"
)

class QueryRequest(BaseModel):
    query: str
    device_name: str = None
    config_type: str = None

class QueryResponse(BaseModel):
    query: str
    config_content: str
    validation_result: dict
    relevant_info: dict

@app.post("/api/generate-config", response_model=QueryResponse)
async def generate_config(request: QueryRequest):
    """ネットワークコンフィグの生成"""
    try:
        result = agent.process_network_query(request.query)
        return QueryResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/devices")
async def list_devices():
    """デバイスリストの取得"""
    return agent.rag_system.kb.list_devices()

@app.get("/api/templates")
async def list_templates():
    """テンプレートリストの取得"""
    return list(agent.rag_system.kb.templates.keys())
```

### Phase 3: 拡張機能

#### 3.1 Webインターフェースの実装
```javascript
// frontend/src/components/NetworkConfigGenerator.js
import React, { useState, useEffect } from 'react';

const NetworkConfigGenerator = () => {
    const [query, setQuery] = useState('');
    const [deviceName, setDeviceName] = useState('');
    const [configType, setConfigType] = useState('');
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    
    const devices = ['R1', 'R2', 'SW1'];
    const configTypes = ['ospf', 'interface', 'security', 'ha', 'monitoring'];
    
    const generateConfig = async () => {
        setLoading(true);
        try {
            const response = await fetch('/api/generate-config', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query,
                    device_name: deviceName,
                    config_type: configType
                })
            });
            
            const data = await response.json();
            setResult(data);
        } catch (error) {
            console.error('Error:', error);
        } finally {
            setLoading(false);
        }
    };
    
    return (
        <div className="config-generator">
            <h1>ネットワークコンフィグ生成</h1>
            
            <div className="form-group">
                <label>クエリ:</label>
                <textarea
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="例: R1に新しい支社Cの接続を追加してOSPFで設定してください"
                />
            </div>
            
            <div className="form-group">
                <label>デバイス:</label>
                <select value={deviceName} onChange={(e) => setDeviceName(e.target.value)}>
                    <option value="">選択してください</option>
                    {devices.map(device => (
                        <option key={device} value={device}>{device}</option>
                    ))}
                </select>
            </div>
            
            <div className="form-group">
                <label>設定タイプ:</label>
                <select value={configType} onChange={(e) => setConfigType(e.target.value)}>
                    <option value="">選択してください</option>
                    {configTypes.map(type => (
                        <option key={type} value={type}>{type}</option>
                    ))}
                </select>
            </div>
            
            <button onClick={generateConfig} disabled={loading}>
                {loading ? '生成中...' : 'コンフィグ生成'}
            </button>
            
            {result && (
                <div className="result">
                    <h2>生成結果</h2>
                    <pre>{result.config_content}</pre>
                    <div className="validation">
                        <h3>検証結果:</h3>
                        <p>ステータス: {result.validation_result.is_valid ? '合格' : '不合格'}</p>
                        {result.validation_result.errors && (
                            <div className="errors">
                                <h4>エラー:</h4>
                                <ul>
                                    {result.validation_result.errors.map((error, index) => (
                                        <li key={index}>{error}</li>
                                    ))}
                                </ul>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default NetworkConfigGenerator;
```

#### 3.2 バッチ処理機能
```python
# batch_processor.py
import asyncio
from typing import List, Dict
from openhands_agent import NetworkConfigAgent

class BatchConfigProcessor:
    def __init__(self, agent: NetworkConfigAgent):
        self.agent = agent
    
    async def process_batch(self, queries: List[Dict]) -> List[Dict]:
        """バッチ処理の実行"""
        results = []
        
        for query_info in queries:
            try:
                result = await asyncio.to_thread(
                    self.agent.process_network_query,
                    query_info['query']
                )
                result['query_info'] = query_info
                results.append(result)
                
                # レートリミットのための待機
                await asyncio.sleep(1)
                
            except Exception as e:
                results.append({
                    'query_info': query_info,
                    'error': str(e)
                })
        
        return results
    
    def generate_report(self, results: List[Dict]) -> str:
        """処理結果のレポート生成"""
        report = []
        report.append("# バッチ処理結果レポート")
        report.append(f"処理日時: {datetime.now().isoformat()}")
        report.append(f"総クエリ数: {len(results)}")
        
        success_count = sum(1 for r in results if 'error' not in r)
        report.append(f"成功数: {success_count}")
        report.append(f"失敗数: {len(results) - success_count}")
        
        report.append("\n## 詳細結果")
        for result in results:
            if 'error' in result:
                report.append(f"- {result['query_info']['query']}: 失敗 ({result['error']})")
            else:
                validation_status = "合格" if result['validation_result']['is_valid'] else "不合格"
                report.append(f"- {result['query_info']['query']}: {validation_status}")
        
        return "\n".join(report)
```

### Phase 4: 運用機能

#### 4.1 認証と認可
```python
# auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """認証の確認"""
    # 実際の実装ではJWTやAPIキーを検証
    if credentials.credentials != "your-secret-api-key":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"username": "authenticated-user"}

def check_permission(user: dict, required_permission: str):
    """権限の確認"""
    # 実際の実装ではユーザーの権限をチェック
    if required_permission == "admin" and user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
```

#### 4.2 ロギングと監視
```python
# monitoring.py
import logging
import json
from datetime import datetime
from typing import Dict, Any

class NetworkConfigMonitor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_logging()
    
    def setup_logging(self):
        """ロギングの設定"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('network_config.log'),
                logging.StreamHandler()
            ]
        )
    
    def log_config_generation(self, query: str, result: Dict[str, Any]):
        """コンフィグ生成のログ記録"""
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'device_name': result.get('device_name', 'unknown'),
            'config_type': result.get('config_type', 'unknown'),
            'validation_status': result.get('validation_result', {}).get('is_valid', False),
            'config_length': len(result.get('config_content', ''))
        }
        
        self.logger.info(f"Config generation: {json.dumps(log_data, ensure_ascii=False)}")
    
    def log_error(self, error: Exception, context: Dict[str, Any]):
        """エラーログの記録"""
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context
        }
        
        self.logger.error(f"Error occurred: {json.dumps(log_data, ensure_ascii=False)}")
```

## デプロイ手順

### 1. 環境準備
```bash
# リポジトリのクローン
git clone <repository-url>
cd network-rag-system-integration

# 依存関係のインストール
pip install -r requirements.txt

# 環境変数の設定
export LLM_API_URL="http://internal-llm-api:8000"
export RAG_API_URL="http://rag-system:8002"
export API_KEY="your-secret-api-key"
```

### 2. サービス起動
```bash
# Docker Composeでサービス起動
docker-compose up -d

# または個別に起動
python api_server.py
python openhands_agent.py
```

### 3. 動作確認
```bash
# APIテスト
curl -X POST "http://localhost:8001/api/generate-config" \
     -H "Content-Type: application/json" \
     -d '{"query": "R1に新しい支社Cの接続を追加してOSPFで設定してください"}'

# Webインターフェースの確認
# http://localhost:3000 にアクセス
```

## まとめ

この統合ソリューションにより、以下のメリットを実現できます：

1. **自動化されたコンフィグ生成**: Network RAG Systemの知識ベースを活用した高品質なコンフィグ生成
2. **OpenHandsとの連携**: 強力なエージェント機能による複雑なネットワーク操作の自動化
3. **拡張性**: モジュール化された構成により、容易に機能追加が可能
4. **運用性**: WebインターフェースとAPIによる使いやすさ
5. **信頼性**: 検証機能と監視機能による品質保証

この構成により、ネットワーク工事時の追加コンフィグ生成を効率化し、人為的ミスを削減することが可能です。
