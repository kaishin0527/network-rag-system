

# Cisco IOS XE Switch Configuration Template

## デバイスタイプ
- **タイプ**: L2/L3スイッチ
- **OS**: Cisco IOS XE
- **モデル**: Catalyst 9000シリーズ
- **用途**: コアスイッチ、アクセススイッチ

## 基本設定
```cisco
! 基本設定
hostname {{hostname}}
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
!
! スタック設定（スタック可能な場合）
switch {{stack_member_number}} priority {{stack_priority}}
switch {{stack_member_number}} provision {{switch_model}}
!
! スパニングツリー設定
spanning-tree mode rapid-pvst
spanning-tree extend system-id
```

### VLAN設定
```cisco
! VLAN定義
vlan {{vlan_id}}
 name {{vlan_name}}
!
! 主要VLAN
vlan 10
 name Management
!
vlan 20
 name Voice
!
vlan 30
 name Data
!
vlan 40
 name Servers
!
vlan 50
 name Guest
!
! VLANインターフェース設定
interface Vlan{{vlan_id}}
 description {{vlan_description}}
 ip address {{vlan_ip}} {{vlan_mask}}
!
! SVI（スイッチ仮想インターフェース）
interface Vlan10
 description Management Network
 ip address 192.168.10.1 255.255.255.0
!
interface Vlan20
 description Voice Network
 ip address 192.168.20.1 255.255.255.0
!
interface Vlan30
 description Data Network
 ip address 192.168.30.1 255.255.255.0
!
interface Vlan40
 description Server Network
 ip address 192.168.40.1 255.255.255.0
!
interface Vlan50
 description Guest Network
 ip address 192.168.50.1 255.255.255.0
```

### インターフェース設定
```cisco
! 物理インターフェース設定
interface GigabitEthernet1/0/{{port_number}}
 description {{description}}
 switchport mode {{switchport_mode}}
!
! アクセスポート
interface GigabitEthernet1/0/1
 description PC Port
 switchport mode access
 switchport access vlan {{access_vlan}}
 switchport voice vlan {{voice_vlan}}
 spanning-tree portfast
 spanning-tree bpduguard enable
!
! トランクポート
interface GigabitEthernet1/0/24
 description Uplink to Core Switch
 switchport mode trunk
 switchport trunk allowed vlan {{allowed_vlans}}
 switchport trunk encapsulation dot1q
!
! ポートチャネル設定
interface Port-channel{{channel_group}}
 description {{channel_description}}
 switchport mode {{channel_mode}}
 switchport trunk allowed vlan {{allowed_vlans}}
!
! ポートチャネルメンバ
interface range GigabitEthernet1/0/23-24
 channel-group {{channel_group}} mode active
!
! ループバックインターフェース
interface Loopback0
 ip address {{loopback_ip}} {{loopback_mask}}
 description Management Loopback
!
! 管理インターフェース
interface Vlan1
 no ip address
!
interface Management1
 description OOB Management
 ip address {{mgmt_ip}} {{mgmt_mask}}
!
! ギガビットインターフェース
interface TenGigabitEthernet1/0/{{port_number}}
 description {{description}}
 no shutdown
!
! 25Gインターフェース
interface TwentyFiveGigE1/0/{{port_number}}
 description {{description}}
 no shutdown
```

### L2プロトコル設定
```cisco
! DHCPスヌーピング設定
ip dhcp snooping
ip dhcp snooping vlan {{dhcp_snoop_vlans}}
ip dhcp snooping information option
ip dhcp snooping verify no-relay
!
! DAI（Dynamic ARP Inspection）
ip arp inspection vlan {{arp_inspect_vlans}}
ip arp inspection trust
!
! IP Source Guard
ip source binding {{mac_address}} {{ip_address}} vlan {{vlan_id}} interface {{interface_name}}
!
! スパニングツリー設定
spanning-tree vlan {{vlan_id}} root primary
spanning-tree vlan {{vlan_id}} root secondary
!
! スパニングツリーポート設定
spanning-tree portfast default
spanning-tree bpduguard default
!
! UplinkFast設定
spanning-tree uplinkfast
!
! BackboneFast設定
spanning-tree backbonefast
!
! スパニングツリーポリス
spanning-tree guard root
spanning-tree loopguard default
!
! Link Aggregation Control Protocol（LACP）
channel-protocol lacp
!
! Port Security
interface {{interface_name}}
 switchport port-security
 switchport port-security maximum {{max_mac}}
 switchport port-security violation {{violation_mode}}
 switchport port-security mac-address sticky
!
! Storm Control
interface {{interface_name}}
 storm-control broadcast level {{broadcast_level}}
 storm-control multicast level {{multicast_level}}
 storm-control unicast level {{unicast_level}}
!
! IGMP Snooping
ip igmp snooping
ip igmp snooping vlan {{vlan_id}}
!
! MLD Snooping（IPv6）
ipv6 mld snooping
ipv6 mld snooping vlan {{vlan_id}}
```

### L3ルーティング設定
```cisco
! IPルーティング有効化
ip routing
!
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
! EIGRP設定
router eigrp {{as_number}}
 network {{network_address}}
 eigrp router-id {{router_id}}
!
! BGP設定（必要な場合）
router bgp {{as_number}}
 bgp router-id {{router_id}}
 neighbor {{peer_ip}} remote-as {{peer_as}}
!
! 静的ルート設定
ip route {{destination_network}} {{subnet_mask}} {{next_hop}}
!
! デフォルトルート
ip route 0.0.0.0 0.0.0.0 {{default_gateway}}
!
! ルートリフレクタ設定
neighbor {{rr_ip}} route-map {{route_map_name}} in
neighbor {{rr_ip}} route-map {{route_map_name}} out
```

### セキュリティ設定
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
! MAC ACL設定
mac access-list extended {{mac_acl_name}}
 permit host {{source_mac}} host {{destination_mac}}
 deny any any
!
! MAC ACL適用
interface {{interface_name}}
 mac access-group {{mac_acl_name}} in
!
! DHCP Snooping Trust
interface {{interface_name}}
 ip dhcp snooping trust
!
! Port Security
interface {{interface_name}}
 switchport port-security
 switchport port-security maximum {{max_mac}}
 switchport port-security violation {{violation_mode}}
 switchport port-security mac-address sticky
!
! Private VLAN設定
vlan {{private_vlan_id}}
 private-vlan {{pvlan_type}}
!
! Primary VLAN
vlan {{primary_vlan_id}}
 private-vlan primary
!
! Secondary VLAN
vlan {{secondary_vlan_id}}
 private-vlan association {{primary_vlan_id}}
!
! Private VLANポート設定
interface {{interface_name}}
 switchport mode private-vlan host
 switchport private-vlan host-association {{primary_vlan_id}} {{secondary_vlan_id}}
!
! Private VLANトランク設定
interface {{interface_name}}
 switchport mode private-vlan promiscuous
 switchport private-vlan mapping {{primary_vlan_id}} {{secondary_vlan_ids}}
!
! 802.1X設定
dot1x system-auth-control
!
! 802.1Xポート設定
interface {{interface_name}}
 authentication order dot1x mab
 authentication priority dot1x mab
 authentication port-control auto
!
! MAC認証バイパス（MAB）
interface {{interface_name}}
 mab
!
! RADIUS設定
aaa new-model
!
! RADIUSサーバー設定
radius server {{radius_server}}
 address ipv4 {{radius_ip}} auth-port {{auth_port}} acct-port {{acct_port}}
 key {{radius_key}}
!
! AAA認証
aaa authentication dot1x {{auth_method}} group radius
aaa authentication dot1x {{auth_method}} group radius
!
! AAA認可
aaa authorization network {{auth_method}} group radius
!
! AAA会計
aaa accounting dot1x {{accounting_method} start-stop group radius
!
! SSH設定
ip domain-name {{domain_name}}
crypto key generate rsa modulus 2048
line vty 0 15
 transport input ssh
!
! Telnet設定（非推奨）
line vty 0 15
 transport input telnet ssh
!
! ローカル認証設定
aaa authentication login {{auth_method}} local
aaa authentication enable default enable
!
! ローカルユーザー設定
username admin privilege 15 secret {{admin_password}}
username monitor privilege 1 secret {{monitor_password}}
```

### QoS設定
```cisco
! QoSグローバル設定
mls qos
mls qos map cos-dscp {{dscp_map}}
mls qos map dscp-cos {{dscp_cos_map}}
!
! QoSポリシー
class-map match-all {{class_map_name}}
 match access-group name {{acl_name}}
 match cos {{cos_value}}
 match dscp {{dscp_value}}
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
!
! シェーピング
interface {{interface_name}}
 shape average {{shape_rate}}
!
! ポリシング
interface {{interface_name}}
 service-policy input {{policy_map_name}}
!
! DSCPマーキング
interface {{interface_name}}
 trust device cisco
!
! CoSマーキング
interface {{interface_name}}
 trust cos
!
! ポートチャネルQoS
interface Port-channel{{channel_group}}
 service-policy input {{policy_map_name}}
```

### 高可用性設定
```cisco
! VRRP設定
interface {{interface_name}}
 vrrp {{vrrp_id}} ip {{virtual_ip}}
 vrrp {{vrrp_id}} priority {{priority}}
 vrrp {{vrrp_id}} preempt
 vrrp {{vrrp_id}} authentication md5 key-string {{auth_key}}
!
! HSRP設定（代替案）
interface {{interface_name}}
 standby {{group_id}} ip {{virtual_ip}}
 standby {{group_id}} priority {{priority}}
 standby {{group_id}} preempt
 standby {{group_id}} authentication md5 key-string {{auth_key}}
!
! GLBP設定（代替案）
interface {{interface_name}}
 glbp {{group_id}} ip {{virtual_ip}}
 glbp {{group_id}} priority {{priority}}
 glbp {{group_id}} preempt
 glbp {{group_id}} authentication md5 key-string {{auth_key}}
!
! スタック設定（スタック可能な場合）
switch {{stack_member_number}} priority {{stack_priority}}
switch {{stack_member_number}} provision {{switch_model}}
!
! スタックリング設定
stacking-speed {{stacking_speed}}
!
! スタックマスター設定
switch {{stack_master_priority}} provision {{switch_model}}
!
! スタックバックアップ設定
switch {{stack_backup_priority}} provision {{switch_model}}
```

### 監視設定
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
!
! CDP設定
cdp run
cdp timer {{cdp_timer}}
cdp holdtime {{cdp_holdtime}}
!
! LLDP設定
lldp run
lldp timer {{lldp_timer}}
lldp reinit {{lldp_reinit}}
lldp holdtime {{lldp_holdtime}}
!
! 電源管理設定
power inline auto
power inline max {{max_watt}}
!
! 温度監視
temperature threshold {{temp_threshold}}
!
! 電源冗長設定
power redundancy mode {{redundancy_mode}}
```

### その他の設定
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
debug platform packet mac
debug platform packet ip
debug platform packet ipv6
!
! 保存設定
end
write memory
```

## 変数一覧
| 変数名 | 説明 | 例 |
|--------|------|-----|
| {{hostname}} | ホスト名 | SW1 |
| {{domain_name}} | ドメイン名 | company.local |
| {{ntp_server}} | NTPサーバー | 192.168.1.1 |
| {{dns_server1}} | DNSサーバー1 | 8.8.8.8 |
| {{dns_server2}} | DNSサーバー2 | 8.8.4.4 |
| {{enable_secret}} | 特権EXECパスワード | $1$secret$ |
| {{admin_password}} | 管理者パスワード | $1$admin$ |
| {{monitor_password}} | 監視用パスワード | $1$monitor$ |
| {{stack_member_number}} | スタックメンバー番号 | 1 |
| {{stack_priority}} | スタック優先度 | 100 |
| {{switch_model}} | スイッチモデル | C9300-48P |
| {{vlan_id}} | VLAN ID | 10 |
| {{vlan_name}} | VLAN名 | Management |
| {{vlan_description}} | VLAN説明 | Management Network |
| {{vlan_ip}} | VLAN IPアドレス | 192.168.10.1 |
| {{vlan_mask}} | VLANサブネットマスク | 255.255.255.0 |
| {{access_vlan}} | アクセスVLAN | 30 |
| {{voice_vlan}} | ボイスVLAN | 20 |
| {{allowed_vlans}} | 許可VLAN | 10,20,30,40,50 |
| {{port_number}} | ポート番号 | 1 |
| {{description}} | インターフェース説明 | PC Port |
| {{switchport_mode}} | スイッチポートモード | access |
| {{channel_group}} | チャネルグループ | 1 |
| {{channel_description}} | チャネル説明 | Uplink Channel |
| {{channel_mode}} | チャネルモード | trunk |
| {{loopback_ip}} | ループバックIP | 10.1.1.1 |
| {{loopback_mask}} | ループバックマスク | 255.255.255.255 |
| {{mgmt_ip}} | 管理IP | 192.168.1.100 |
| {{mgmt_mask}} | 管理サブネットマスク | 255.255.255.0 |
| {{ospf_process_id}} | OSPFプロセスID | 1 |
| {{router_id}} | ルータID | 10.1.1.1 |
| {{area_id}} | OSPFエリアID | 0 |
| {{network_address}} | ネットワークアドレス | 10.1.1.0 |
| {{wildcard_mask}} | ワイルドカードマスク | 0.0.0.255 |
| {{active_interfaces}} | アクティブインターフェース | Vlan10 |
| {{acl_name}} | ACL名 | INBOUND_ACL |
| {{interface_name}} | インターフェース名 | GigabitEthernet1/0/1 |
| {{mac_address}} | MACアドレス | 00:1A:2B:3C:4D:5E |
| {{ip_address}} | IPアドレス | 192.168.30.10 |
| {{max_mac}} | 最大MACアドレス数 | 2 |
| {{violation_mode}} | 違反モード | restrict |
| {{broadcast_level}} | ブロードキャストレベル | 20 |
| {{multicast_level}} | マルチキャストレベル | 20 |
| {{unicast_level}} | ユニキャストレベル | 20 |
| {{dscp_map}} | DSCPマップ | 0:8,16:26,32:46,48:56 |
| {{dscp_cos_map}} | DSCP-COSマップ | 0:0,8:1,16:2,24:3,32:4,40:5,48:6,56:7 |
| {{class_map_name}} | クラスマップ名 | CRITICAL_TRAFFIC |
| {{policy_map_name}} | ポリシーマップ名 | QOS_POLICY |
| {{priority_percent}} | 優先度パーセント | 30 |
| {{cir}} | コミットレート | 1000000 |
| {{bc}} | バーストカレント | 100000 |
| {{shape_rate}} | シェイプレート | 5000000 |
| {{vrrp_id}} | VRRP ID | 10 |
| {{virtual_ip}} | 仮想IP | 192.168.100.100 |
| {{priority}} | VRRP優先度 | 110 |
| {{auth_key}} | 認証キー | secret123 |
| {{group_id}} | HSRPグループID | 10 |
| {{stacking_speed}} | スタッキング速度 | 10g |
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
| {{cdp_timer}} | CDPタイマー | 60 |
| {{cdp_holdtime}} | CDPホールドタイム | 180 |
| {{lldp_timer}} | LLDPタイマー | 30 |
| {{lldp_reinit}} | LLDPリイニット | 2 |
| {{lldp_holdtime}} | LLDPホールドタイム | 120 |
| {{max_watt}} | 最大ワット数 | 30 |
| {{temp_threshold}} | 温度しきい値 | 75 |
| {{redundancy_mode}} | 冗長モード | redundant |

