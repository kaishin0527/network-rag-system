



#!/usr/bin/env python3
# utils.py
import os
import re
import json
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime

def load_config_file(file_path: str) -> Dict[str, Any]:
    """設定ファイルの読み込み"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            if file_path.endswith('.json'):
                return json.load(f)
            elif file_path.endswith('.yaml') or file_path.endswith('.yml'):
                import yaml
                return yaml.safe_load(f)
            else:
                # テキストファイルとして読み込み
                return {'content': f.read()}
    except Exception as e:
        print(f"Error loading config file {file_path}: {e}")
        return {}

def save_config_file(data: Any, file_path: str, format: str = 'auto') -> bool:
    """設定ファイルの保存"""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        if format == 'auto':
            if file_path.endswith('.json'):
                format = 'json'
            elif file_path.endswith('.yaml') or file_path.endswith('.yml'):
                format = 'yaml'
            else:
                format = 'text'
        
        with open(file_path, 'w', encoding='utf-8') as f:
            if format == 'json':
                json.dump(data, f, indent=2, ensure_ascii=False)
            elif format == 'yaml':
                import yaml
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
            else:
                if isinstance(data, dict):
                    f.write(str(data))
                else:
                    f.write(data)
        
        return True
    except Exception as e:
        print(f"Error saving config file {file_path}: {e}")
        return False

def validate_ip_address(ip: str) -> bool:
    """IPアドレスの検証"""
    pattern = r'^(\d{1,3}\.){3}\d{1,3}/\d{1,2}$'
    if not re.match(pattern, ip):
        return False
    
    # マスクの検証
    prefix = int(ip.split('/')[1])
    if prefix < 0 or prefix > 32:
        return False
    
    return True

def validate_subnet_mask(mask: str) -> bool:
    """サブネットマスクの検証"""
    try:
        if '/' in mask:
            prefix = int(mask.split('/')[1])
            if prefix < 0 or prefix > 32:
                return False
        else:
            # マスク表記の場合
            octets = mask.split('.')
            if len(octets) != 4:
                return False
            
            # 各オクテットの検証
            for octet in octets:
                value = int(octet)
                if value < 0 or value > 255:
                    return False
            
            # 連続した1の検証
            binary_mask = ''.join([format(int(octet), '08b') for octet in octets])
            if '0' in binary_mask:
                first_zero = binary_mask.index('0')
                if '1' in binary_mask[first_zero:]:
                    return False
        
        return True
    except:
        return False

def extract_network_from_ip(ip_with_mask: str) -> str:
    """IPアドレスからネットワークアドレスを抽出"""
    try:
        ip = ip_with_mask.split('/')[0]
        prefix = int(ip_with_mask.split('/')[1])
        
        octets = ip.split('.')
        network_octets = []
        
        for i in range(4):
            if i * 8 < prefix:
                if (i + 1) * 8 <= prefix:
                    network_octets.append(int(octets[i]))
                else:
                    bits_in_octet = prefix - i * 8
                    network_octets.append(int(octets[i]) & (255 << (8 - bits_in_octet)))
                    break
            else:
                network_octets.append(0)
        
        return f"{network_octets[0]}.{network_octets[1]}.{network_octets[2]}.{network_octets[3]}/{prefix}"
    except:
        return ip_with_mask

def format_config_output(config: str, style: str = 'cisco') -> str:
    """コンフィグ出力のフォーマット"""
    lines = config.split('\n')
    formatted_lines = []
    
    for line in lines:
        line = line.rstrip()
        if not line:
            formatted_lines.append('')
            continue
        
        if style == 'cisco':
            # Ciscoスタイルのフォーマット
            if line.startswith('!'):
                formatted_lines.append(line)
            elif line.startswith('interface '):
                formatted_lines.append('')
                formatted_lines.append(line)
            elif line.startswith('router '):
                formatted_lines.append('')
                formatted_lines.append(line)
            elif line.startswith('ip '):
                formatted_lines.append(f" {line}")
            else:
                formatted_lines.append(f" {line}")
        else:
            # 通常のフォーマット
            formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)

def generate_backup_filename(device_name: str, config_type: str = 'running') -> str:
    """バックアップファイル名の生成"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{device_name}_{config_type}_config_{timestamp}.txt"

def generate_change_log(old_config: str, new_config: str) -> str:
    """変更ログの生成"""
    import difflib
    
    old_lines = old_config.split('\n')
    new_lines = new_config.split('\n')
    
    differ = difflib.Differ()
    diff = list(differ.compare(old_lines, new_lines))
    
    change_log = []
    change_log.append(f"Change Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    change_log.append("=" * 50)
    
    for line in diff:
        if line.startswith('  '):
            change_log.append(f"  {line[2:]}")
        elif line.startswith('- '):
            change_log.append(f"-REMOVED: {line[2:]}")
        elif line.startswith('+ '):
            change_log.append(f"+ADDED: {line[2:]}")
    
    return '\n'.join(change_log)

def create_network_diagram(devices: List[Dict[str, Any]]) -> str:
    """ネットワーク図の生成（Mermaid形式）"""
    diagram = ["graph TD"]
    
    # デバイスのノード定義
    for device in devices:
        device_id = device['hostname'].replace(' ', '_')
        device_type = device['device_type']
        
        if device_type == 'router':
            diagram.append(f"    {device_id}[\"📡 {device['hostname']}\"]")
        elif device_type == 'switch':
            diagram.append(f"    {device_id}[\"🔌 {device['hostname']}\"]")
        else:
            diagram.append(f"    {device_id}[\"💻 {device['hostname']}\"]")
    
    # 接続の定義（簡略化）
    if len(devices) >= 2:
        diagram.append(f"    {devices[0]['hostname'].replace(' ', '_')} --- {devices[1]['hostname'].replace(' ', '_')}")
    
    if len(devices) >= 3:
        diagram.append(f"    {devices[1]['hostname'].replace(' ', '_')} --- {devices[2]['hostname'].replace(' ', '_')}")
    
    return '\n'.join(diagram)

def calculate_network_stats(configs: List[str]) -> Dict[str, Any]:
    """ネットワーク統計情報の計算"""
    stats = {
        'total_configs': len(configs),
        'total_lines': 0,
        'total_devices': 0,
        'device_types': {},
        'ip_addresses': [],
        'protocols': {}
    }
    
    for config in configs:
        lines = config.split('\n')
        stats['total_lines'] += len(lines)
        
        # IPアドレスの抽出
        ip_pattern = r'ip address (\d+\.\d+\.\d+\.\d+/\d+)'
        ip_matches = re.findall(ip_pattern, config)
        stats['ip_addresses'].extend(ip_matches)
        
        # プロトコルの抽出
        protocol_pattern = r'router (\w+)'
        protocol_matches = re.findall(protocol_pattern, config)
        for protocol in protocol_matches:
            if protocol not in stats['protocols']:
                stats['protocols'][protocol] = 0
            stats['protocols'][protocol] += 1
    
    return stats

def sanitize_filename(filename: str) -> str:
    """ファイル名のサニタイズ"""
    # 不正な文字を置換
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # 末尾のスペースとドットを除去
    filename = filename.rstrip('. ')
    
    return filename

def ensure_directory_exists(directory: str) -> bool:
    """ディレクトリの存在確認と作成"""
    try:
        os.makedirs(directory, exist_ok=True)
        return True
    except Exception as e:
        print(f"Error creating directory {directory}: {e}")
        return False

def get_file_size(file_path: str) -> int:
    """ファイルサイズの取得"""
    try:
        return os.path.getsize(file_path)
    except:
        return 0

def format_file_size(size_bytes: int) -> str:
    """ファイルサイズのフォーマット"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"




