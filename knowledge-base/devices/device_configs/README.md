

# Device Configuration Files

## ファイル命名規則
- `{device_name}_{config_type}_{date}.txt`
  - `device_name`: デバイス名 (R1, SW1, R2, FTD, etc.)
  - `config_type`: コンフィグタイプ (running_config, startup_config, backup, etc.)
  - `date`: 日付 (YYYY-MM-DD)

## メタデータフォーマット
各コンフィグファイルの先頭に以下のメタデータを追加：

```
# Device Configuration Metadata
# Device: R1
# Type: Router
# OS: Cisco IOS XE
# Model: ISR4331
# Config Type: running_config
# Date: 2025-08-10
# Version: 15.2(4)M5
# Contact: network-admin@company.com
# Description: Production router configuration

! ここから実際のコンフィグ
hostname R1
ip routing
...
```

## サンプルコンフィグファイル

### R1 Running Config サンプル
```
# Device Configuration Metadata
# Device: R1
# Type: Router
# OS: Cisco IOS XE
# Model: ISR4331
# Config Type: running_config
# Date: 2025-08-10
# Version: 15.2(4)M5
# Contact: network-admin@company.com
# Description: Production router configuration

! 基本設定
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

! BGP設定
router bgp 65001
 bgp router-id 10.1.1.1
 neighbor 203.0.113.2 remote-as 65002
 neighbor 203.0.113.2 description ISP-PEER

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
```

### SW1 Running Config サンプル
```
# Device Configuration Metadata
# Device: SW1
# Type: Switch
# OS: Cisco IOS XE
# Model: C9500-24Y4C
# Config Type: running_config
# Date: 2025-08-10
# Version: 16.9.3
# Contact: network-admin@company.com
# Description: Production core switch configuration

! 基本設定
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
```

## アップロード手順

### 1. コンフィグファイルの準備
```bash
# 実際のコンフィグを取得
show running-config > R1_running_config_2025-08-10.txt
show startup-config > R1_startup_config_2025-08-10.txt

# メタデータを追加
cat > R1_running_config_2025-08-10.txt << EOF
# Device Configuration Metadata
# Device: R1
# Type: Router
# OS: Cisco IOS XE
# Model: ISR4331
# Config Type: running_config
# Date: 2025-08-10
# Version: 15.2(4)M5
# Contact: network-admin@company.com
# Description: Production router configuration

$(cat R1_running_config_2025-08-10.txt)
EOF
```

### 2. ファイルの配置
```bash
# ディレクトリを作成
mkdir -p /workspace/network-rag-system/knowledge-base/devices/device_configs

# ファイルをコピー
cp R1_running_config_2025-08-10.txt /workspace/network-rag-system/knowledge-base/devices/device_configs/
```

### 3. Gitでの管理
```bash
# 変更をコミット
cd /workspace/network-rag-system
git add knowledge-base/devices/device_configs/
git commit -m "feat: Add actual device configuration files"
git push origin main
```

## 4. RAGシステムでの利用

### コンフィグファイルの検索
```python
from src.rag_system import NetworkRAGSystem

# RAGシステムの初期化
rag_system = NetworkRAGSystem()

# デバイスコンフィグの検索
results = rag_system.search("R1 running config OSPF settings")
print(results)
```

### コンフィグ生成への活用
```python
from src.config_generator import NetworkConfigGenerator

# コンフィグ生成器の初期化
config_generator = NetworkConfigGenerator()

# 実際のコンフィグを参考にした生成
query = "R1に新しい支社C接続を追加してOSPFで設定してください"
generated_config = config_generator.generate_config(query)

# 参考コンフィグとの比較
config_generator.compare_with_reference("R1_running_config_2025-08-10.txt")
```

## 5. ベストプラクティス

1. **バージョン管理**: コンフィグの変更履歴を保持
2. **メタデータ**: 各ファイルにデバイス情報を明記
3. **バックアップ**: 定期的なコンフィグバックアップを実施
4. **セキュリティ**: 機密情報を含むコンフィグは暗号化
5. **整理**: 古いコンフィグはアーカイブ化

## 6. 自動化スクリプト

コンフィグの自動取得とアップロードスクリプトを作成することも可能です：

```bash
#!/bin/bash
# config_backup.sh

# デバイスリスト
DEVICES=("R1" "SW1" "R2" "FTD")

# バックアップディレクトリ
BACKUP_DIR="/workspace/network-rag-system/knowledge-base/devices/device_configs"

# 各デバイスからコンフィグを取得
for device in "${DEVICES[@]}"; do
    # 実際の環境ではSSHやAPIを使用してコンフィグを取得
    # show running-config | ssh $device
    
    # ダミーデータの作成（実際にはデバイスから取得）
    cat > "$BACKUP_DIR/${device}_running_config_$(date +%Y-%m-%d).txt" << EOF
# Device Configuration Metadata
# Device: $device
# Type: Router/Switch
# OS: Cisco IOS XE
# Config Type: running_config
# Date: $(date +%Y-%m-%d)
# Contact: network-admin@company.com
# Description: Production configuration

! Configuration for $device
hostname $device
ip routing
...
EOF
done

# Gitコミット
cd /workspace/network-rag-system
git add knowledge-base/devices/device_configs/
git commit -m "feat: Auto-backup device configurations $(date +%Y-%m-%d)"
git push origin main
```

この方法で、実際のデバイスコンフィグを参考情報としてKBに追加し、RAGシステムで活用できます。

