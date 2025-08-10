

# R1 (Core Router) ポリシー

## 基本情報
- **ホスト名**: R1
- **IPアドレス**: 192.168.100.1
- **デバイスタイプ**: ルータ
- **モデル**: ISR4331
- **IOSバージョン**: 15.2(4)M5

## インターフェース設定
- **Loopback0**: 10.1.1.1/32 (Router-ID)
- **GigabitEthernet0/0**: 192.168.100.1/30 (管理用)
- **GigabitEthernet0/1**: 10.1.12.1/30 (R2へのリンク)
- **GigabitEthernet0/2**: 10.1.10.1/30 (SW1へのリンク)

## OSPF設定
- **プロセスID**: 1
- **Router-ID**: 10.1.1.1
- **エリア設定**:
  - Area 0: 10.1.0.0/16 (本社ネットワーク)
  - Area 0: 10.1.12.0/30 (R2リンク)
  - Area 0: 10.1.10.0/30 (SW1リンク)
- **パッシブインターフェース**: Loopback0

## セキュリティ設定
- **ACL設定**:
  - Standard ACL 1: 管理アクセス許可
  - Extended ACL 101: 本社-支社間通信
- **SNMP設定**:
  - Community: "public_ro" (RO), "private_rw" (RW)
  - Location: "Tokyo_Data_Center"

## 高可用性設定
- **HSRP設定**:
  - Group 10: 192.168.100.100 (仮想IP)
  - Priority: 100
  - Authentication: "cisco123"

## 監視設定
- **Syslog**: 192.168.100.100
- **NTP**: 192.168.100.100
- **NetFlow**: 192.168.100.100


