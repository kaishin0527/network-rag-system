
# Cisco IOS XE Router Configuration Template

## デバイスタイプ
- **タイプ**: ルータ
- **OS**: Cisco IOS XE
- **モデル**: Cisco ISR 4000シリーズ
- **用途**: エッジルータ、コアルータ

## 基本設定
```cisco
! 基本設定
hostname {{hostname}}
ip routing
service timestamps debug datetime msec
service timestamps log datetime msec
no ip domain-lookup
ip domain-name {{domain_name}}
!
! NTP設定
ntp server {{ntp_server}} prefer
ntp server {{ntp_server_backup}}
!
! DNS設定
ip name-server {{dns_server1}}
ip name-server {{dns_server2}}
!
! 特権EXECモードパスワード
enable secret {{enable_secret}}
!
! VTYコンソール設定
line con 0
 exec-timeout 0 0
 logging synchronous
line vty 0 4
 login local
line vty 5 15
 login local
!
! ローカルユーザー設定
username admin privilege 15 secret {{admin_password}}
username monitor privilege 1 secret {{monitor_password}}
```

## インターフェース設定
```cisco
! インターフェース設定
interface GigabitEthernet0/0/0
 description {{description}}
 ip address {{ip_address}} {{subnet_mask}}
 no shutdown
!
interface GigabitEthernet0/0/1
 description {{description}}
 ip address {{ip_address}} {{subnet_mask}}
 no shutdown
!
! ループバックインターフェース
interface Loopback0
 ip address {{loopback_ip}} {{loopback_mask}}
 description Management Loopback
!
! サブインターフェース（MPLS用）
interface GigabitEthernet0/1/0.100
 encapsulation dot1Q 100
 ip address {{sub_ip}} {{sub_mask}}
!
! Serialインターフェース（WAN用）
interface Serial0/0/0
 description WAN Connection
 ip address {{wan_ip}} {{wan_mask}
 encapsulation ppp
 no shutdown
```

## ルーティング設定
```cisco
! OSPF設定
router ospf {{ospf_process_id}}
 router-id {{router_id}}
 log-adjacency-changes
!
! エリア設定
 area {{area_id}} range {{network_address}} {{wildcard_mask}}
!
! インターフェース設定
 network {{network_address}} {{wildcard_mask}} area {{area_id}}
!
! パッシブインターフェース
 passive-interface default
 no passive-interface {{active_interfaces}}
!
! BGP設定（外部接続用）
router bgp {{as_number}}
 bgp router-id {{router_id}}
 neighbor {{peer_ip}} remote-as {{peer_as}}
 neighbor {{peer_ip}} description {{peer_description}}
!
! ルートフィルタリング
ip prefix-list {{prefix_list_name}} permit {{network_address}} {{prefix_length}}
!
! ルートリフレクタ設定（必要な場合）
neighbor {{rr_ip}} route-map {{route_map_name}} in
neighbor {{rr_ip}} route-map {{route_map_name}} out
```

## セキュリティ設定
```cisco
! ACL設定
ip access-list extended {{acl_name}}
 permit tcp {{source_network}} {{wildcard}} {{destination_network}} {{wildcard}} eq {{port}}
 permit udp {{source_network}} {{wildcard}} {{destination_network}} {{wildcard}} eq {{port}}
 deny   ip any any
!
! ACL適用
interface {{interface_name}}
 ip access-group {{acl_name}} in
!
! SSH設定
ip domain-name {{domain_name}}
crypto key generate rsa modulus 2048
line vty 0 15
 transport input ssh
!
! ファイアウォール設定（Zone-Based）
zone security {{zone_name}}
 description {{zone_description}}
!
! クラスマップ
class-map match-all {{class_map_name}}
 match access-group name {{acl_name}}
!
! ポリシーマップ
policy-map {{policy_map_name}}
 class {{class_map_name}}
  drop
!
! ゾン間ポリシー
zone-pair security {{zone_pair_name}} source {{source_zone}} destination {{destination_zone}}
 service-policy type inspect {{policy_map_name}}
!
! AAA設定
aaa new-model
!
! AAA認証
aaa authentication login {{auth_method}} local
aaa authentication enable default enable
!
! AAA認可
aaa authorization exec {{auth_method}} local
!
! AAA会計
aaa accounting exec start-stop group {{accounting_group}}
!
! RADIUS設定（外部AAAサーバー）
aaa server radius dynamic-author
 client {{radius_server}} server-key {{radius_key}}
!
! TACACS+設定
aaa group server tacacs+ {{tac_group_name}}
 server {{tacacs_server}}
!
! IKEv2設定（IPsec用）
crypto ikev2 proposal {{proposal_name}}
 encryption aes 256
 integrity sha384
 group 14
!
! IPsecポリシー
crypto ipsec transform-set {{transform_set_name}}
 esp-aes 256 esp-sha-hmac
 mode tunnel
!
! トンネルインターフェース
interface Tunnel0
 ip address {{tunnel_ip}} {{tunnel_mask}}
 tunnel source {{source_interface}}
 tunnel destination {{destination_ip}}
 tunnel mode ipsec ipv4
 tunnel protection ipsec profile {{profile_name}}
```

## QoS設定
```cisco
! QoSポリシー
class-map {{class_map_name}}
 match protocol {{protocol}}
!
! ポリシーマップ
policy-map {{policy_map_name}}
 class {{class_map_name}}
  priority percent {{priority_percent}}
  police {{cir}} {{bc}} conform-action transmit exceed-action drop
!
! シェイプ
policy-map {{shape_policy_name}}
 class class-default
  shape average {{shape_rate}}
!
! QoS適用
interface {{interface_name}}
 service-policy input {{policy_map_name}}
 service-policy output {{shape_policy_name}}
```

## 高可用性設定
```cisco
! HSRP設定
interface {{interface_name}}
 standby {{group_id}} ip {{virtual_ip}}
 standby {{group_id}} priority {{priority}}
 standby {{group_id}} preempt
 standby {{group_id}} authentication md5 key-string {{auth_key}}
 standby {{group_id}} track {{tracked_object}} {{priority_decrement}}
!
! VRRP設定（代替案）
vrrp {{vrrp_id}} ip {{virtual_ip}}
 vrrp {{vrrp_id}} priority {{priority}}
 vrrp {{vrrp_id}} preempt
 vrrp {{vrrp_id}} authentication md5 key-string {{auth_key}}
!
! GLBP設定（代替案）
interface {{interface_name}}
 glbp {{group_id}} ip {{virtual_ip}}
 glbp {{group_id}} priority {{priority}}
 glbp {{group_id}} preempt
 glbp {{group_id}} authentication md5 key-string {{auth_key}}
```

## 監視設定
```cisco
! SNMP設定
snmp-server community {{community_string}} RO
snmp-server community {{community_string_rw}} RW
snmp-server host {{snmp_server}} version 2c {{community_string}}
snmp-server host {{snmp_server}} version 3 {{user_name}} auth sha {{auth_key}} priv aes 128 {{priv_key}}
!
! Syslog設定
logging host {{syslog_server}}
logging trap {{severity_level}}
logging buffered {{buffer_size}}
logging origin-id hostname
!
! NetFlow設定
ip flow-export destination {{netflow_server}} {{port}}
ip flow-export version 9
ip flow-export source {{loopback_interface}}
ip flow-export template timeout-rate {{timeout_rate}}
!
! IP SLA設定
ip sla {{operation_id}}
 icmp-echo {{target_ip}}
 frequency {{frequency}}
 timeout {{timeout}}
!
! IP SLA追跡
track {{track_id}} ip sla {{operation_id}} reachability
!
! RMON設定
rmon {{rmon_group}} {{rmon_interval}}
```

## その他の設定
```cisco
! NTPマルチキャスト設定
ntp multicast
!
! DHCPリレー設定
ip dhcp relay information option
ip dhcp relay information policy replace
!
! IPv6設定（必要な場合）
ipv unicast-routing
!
! IPv6基本設定
interface {{interface_name}}
 ipv6 address {{ipv6_address}}/{{prefix_length}}
 ipv6 enable
!
! IPv6 OSPF設定
ipv6 router ospf {{process_id}}
!
! トラブルシューティング用設定
! デバッグ設定（運用時はコメントアウト）
debug ip packet {{debug_level}}
debug ip routing {{debug_level}}
!
! 保存設定
end
write memory
```

## 変数一覧
| 変数名 | 説明 | 例 |
|--------|------|-----|
| {{hostname}} | ホスト名 | R1 |
| {{domain_name}} | ドメイン名 | company.local |
| {{ntp_server}} | NTPサーバー | 192.168.1.1 |
| {{dns_server1}} | DNSサーバー1 | 8.8.8.8 |
| {{dns_server2}} | DNSサーバー2 | 8.8.4.4 |
| {{enable_secret}} | 特権EXECパスワード | $1$secret$ |
| {{admin_password}} | 管理者パスワード | $1$admin$ |
| {{monitor_password}} | 監視用パスワード | $1$monitor$ |
| {{description}} | インターフェース説明 | WAN Link to ISP |
| {{ip_address}} | IPアドレス | 192.168.1.1 |
| {{subnet_mask}} | サブネットマスク | 255.255.255.0 |
| {{loopback_ip}} | ループバックIP | 10.1.1.1 |
| {{loopback_mask}} | ループバックマスク | 255.255.255.255 |
| {{ospf_process_id}} | OSPFプロセスID | 1 |
| {{router_id}} | ルータID | 10.1.1.1 |
| {{area_id}} | OSPFエリアID | 0 |
| {{network_address}} | ネットワークアドレス | 10.1.1.0 |
| {{wildcard_mask}} | ワイルドカードマスク | 0.0.0.255 |
| {{active_interfaces}} | アクティブインターフェース | GigabitEthernet0/0/0 |
| {{acl_name}} | ACL名 | INBOUND_ACL |
| {{interface_name}} | インターフェース名 | GigabitEthernet0/0/0 |
| {{zone_name}} | セキュリティゾーン名 | INSIDE |
| {{zone_description}} | ゾーン説明 | Internal Network |
| {{class_map_name}} | クラスマップ名 | CRITICAL_TRAFFIC |
| {{policy_map_name}} | ポリシーマップ名 | QOS_POLICY |
| {{priority_percent}} | 優先度パーセント | 30 |
| {{cir}} | コミットレート | 1000000 |
| {{bc}} | バーストカレント | 100000 |
| {{shape_rate}} | シェイプレート | 5000000 |
| {{group_id}} | HSRPグループID | 10 |
| {{virtual_ip}} | 仮想IP | 192.168.100.100 |
| {{priority}} | HSRP優先度 | 110 |
| {{auth_key}} | 認証キー | secret123 |
| {{tracked_object}} | トラッキング対象 | 1 |
| {{priority_decrement}} | 優先度減少値 | 20 |
| {{community_string}} | SNMPコミュニティ文字列 | public_ro |
| {{community_string_rw}} | SNMP RWコミュニティ文字列 | private_rw |
| {{snmp_server}} | SNMPサーバー | 192.168.1.100 |
| {{user_name}} | SNMPv3ユーザー名 | snmpuser |
| {{auth_key}} | SNMPv3認証キー | authkey123 |
| {{priv_key}} | SNMPv3暗号化キー | privkey456 |
| {{syslog_server}} | Syslogサーバー | 192.168.1.200 |
| {{severity_level}} | シverityレベル | 6 |
| {{buffer_size}} | バッファサイズ | 8192 |
| {{netflow_server}} | NetFlowサーバー | 192.168.1.300 |
| {{port}} | ポート番号 | 2055 |
| {{loopback_interface}} | NetFlowソースインターフェース | Loopback0 |
| {{timeout_rate}} | テンプレートタイムアウト | 600 |
| {{operation_id}} | IP SLA操作ID | 1 |
| {{target_ip}} | IP SLA対象IP | 8.8.8.8 |
| {{frequency}} | IP SLA頻度 | 60 |
| {{timeout}} | IP SLAタイムアウト | 1000 |
| {{track_id}} | トラッキングID | 1 |
| {{rmon_group}} | RMONグループ | history |
| {{rmon_interval}} | RMON間隔 | 300 |
| {{debug_level}} | デバッグレベル | all |
