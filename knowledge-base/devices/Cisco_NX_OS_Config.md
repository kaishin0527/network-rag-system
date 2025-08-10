


# Cisco Nexus NX-OS Configuration Template

## デバイスタイプ
- **タイプ**: データセンタースイッチ
- **OS**: Cisco NX-OS
- **モデル**: Nexus 9000シリーズ
- **用途**: データセンターコア、スパインリーフ

## 基本設定
```cisco
! 基本設定
terminal length 0
!
! ホスト名設定
hostname {{hostname}}
!
! ドメイン名設定
domain name {{domain_name}}
!
! NTP設定
feature ntp
!
! NTPサーバー設定
ntp server {{ntp_server}}
!
! DNS設定
feature dns
!
! DNSサーバー設定
dns server {{dns_server1}}
dns server {{dns_server2}}
!
! 特権EXECモードパスワード
username admin password {{admin_password}}
username admin role network-admin
!
! VTYコンソール設定
line vty 0 15
!
! SSH設定
feature ssh
ssh key rsa 2048
!
! Telnet設定（非推奨）
feature telnet
!
! SNMP設定
feature snmp
!
! SNMPコミュニティ設定
snmp-server community {{community_string}} ro
snmp-server community {{community_string_rw}} rw
snmp-server host {{snmp_server}} version 2c {{community_string}}
!
! Syslog設定
logging host {{syslog_server}}
logging level {{severity_level}}
!
! RADIUS設定
feature radius
!
! RADIUSサーバー設定
radius server {{radius_server}}
 address ipv4 {{radius_ip}} auth-port {{auth_port}} acct-port {{acct_port}}
 key {{radius_key}}
!
! TACACS+設定
feature tacacs+
!
! TACACS+サーバー設定
tacacs server {{tacacs_server}}
 address ipv4 {{tacacs_ip}}
 key {{tacacs_key}}
!
! AAA設定
aaa authentication login default group radius local
aaa authentication enable default enable
aaa authorization exec default group radius local
aaa accounting exec default start-stop group radius
```

### インターフェース設定
```cisco
! インターフェース設定
!
! 物理インターフェース設定
interface {{interface_name}}
 description {{description}}
!
! Ethernetインターフェース
interface Ethernet1/{{interface_number}}
 description {{description}}
 no shutdown
!
! Port-channel設定
interface port-channel {{channel_id}}
 description {{channel_description}}
!
! Port-channelメンバ設定
interface range Ethernet1/{{start_port}}-{{end_port}}
 channel-group {{channel_id}} mode active
!
! VLANインターフェース設定
interface Vlan{{vlan_id}}
 description {{vlan_description}}
 no shutdown
!
! ループバックインターフェース設定
interface loopback{{loopback_id}}
 description {{loopback_description}}
 no shutdown
!
! マネジメントインターフェース設定
interface mgmt0
 description {{mgmt_description}}
!
! サブインターフェース設定
interface Ethernet1/{{interface_number}}.{{subinterface_id}}
 encapsulation dot1q {{vlan_id}}
 no shutdown
```

### VLAN設定
```cisco
! VLAN設定
!
! VLAN作成
vlan {{vlan_id}}
 name {{vlan_name}}
!
! VLAN属性設定
vlan {{vlan_id}}
 state {{vlan_state}}
!
! VLAN範囲設定
vlan {{vlan_start}}-{{vlan_end}}
!
! VLANプロファイル設定
vlan {{vlan_id}}
 private-vlan {{pvlan_type}}
!
! Primary VLAN設定
vlan {{primary_vlan_id}}
 private-vlan primary
!
! Secondary VLAN設定
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
```

### L2プロトコル設定
```cisco
! L2プロトコル設定
!
! スパニングツリー設定
feature spanning-tree
!
! スパニングツリープロトコル設定
spanning-tree mode {{spanning_tree_mode}}
!
! スパニングツリーポート設定
spanning-tree port type edge
spanning-tree port type network
!
! スパニングツリーガード設定
spanning-tree port guard {{guard_type}}
!
! スパニングツリーBPDUガード設定
spanning-tree port bpduguard enable
!
! スパニングツリールートガード設定
spanning-tree port rootguard
!
! スパニングツリーポリス設定
spanning-tree port default {{port_type}}
!
! LACP設定
feature lacp
!
! LACPポートチャネル設定
interface port-channel {{channel_id}}
 lacp {{lacp_mode}}
!
! LACPメンバ設定
interface range Ethernet1/{{start_port}}-{{end_port}}
 channel-group {{channel_id}} mode {{channel_mode}}
!
! LLDP設定
feature lldp
!
! LLDPグローバル設定
lldp timer {{lldp_timer}}
lldp reinit {{lldp_reinit}}
lldp holdtime {{lldp_holdtime}}
!
! LLDPインターフェース設定
interface {{interface_name}}
 lldp transmit
 lldp receive
!
! CDP設定
feature cdp
!
! CDPグローバル設定
cdp timer {{cdp_timer}}
cdp holdtime {{cdp_holdtime}}
!
! CDPインターフェース設定
interface {{interface_name}}
 cdp enable
```

### L3ルーティング設定
```cisco
! L3ルーティング設定
!
! IPルーティング有効化
feature ospf
feature bgp
!
! OSPF設定
router ospf {{ospf_process_id}}
 router-id {{router_id}}
!
! OSPFネットワーク設定
router ospf {{ospf_process_id}}
 network {{network_address}} {{wildcard_mask}} area {{area_id}}
!
! OSPFエリア設定
router ospf {{ospf_process_id}}
 area {{area_id}} range {{network_address}} {{wildcard_mask}}
!
! OSPFインターフェース設定
router ospf {{ospf_process_id}}
 passive-interface {{interface_name}}
!
! OSPFパラメータ設定
router ospf {{ospf_process_id}}
 auto-cost reference-bandwidth {{reference_bandwidth}}
!
! BGP設定
router bgp {{as_number}}
 bgp router-id {{router_id}}
!
! BGPネイバー設定
router bgp {{as_number}}
 neighbor {{neighbor_ip}} remote-as {{neighbor_as}}
 neighbor {{neighbor_ip}} description {{neighbor_description}}
!
! BGPネットワーク設定
router bgp {{as_number}}
 network {{network_address}} mask {{subnet_mask}}
!
! BGPコミュニティ設定
router bgp {{as_number}}
 neighbor {{neighbor_ip}} send-community
 neighbor {{neighbor_ip}} route-map {{route_map_name}} in
 neighbor {{neighbor_ip}} route-map {{route_map_name}} out
!
! BGPルートリフレクタ設定
router bgp {{as_number}}
 neighbor {{rr_ip}} route-reflector-client
!
! BGPルートフィルタリング設定
router bgp {{as_number}}
 address-family ipv4
  prefix-list {{prefix_list_name}} permit {{network_address}} {{prefix_length}}
!
! 静的ルート設定
ip route {{destination_network}} {{subnet_mask}} {{next_hop}}
!
! デフォルトルート設定
ip route 0.0.0.0 0.0.0.0 {{default_gateway}}
!
! IPv6設定
feature ipv6
!
! IPv6 OSPF設定
ipv6 router ospf {{ospf_process_id}}
!
! IPv6 BGP設定
router bgp {{as_number}}
 address-family ipv6
```

### VRF設定
```cisco
! VRF設定
!
! VRF作成
vrf context {{vrf_name}}
!
! VRFRD設定
vrf context {{vrf_name}}
 rd {{route_distinguisher}}
!
! VRFルートリミット設定
vrf context {{vrf_name}}
 maximum routes {{route_limit}}
!
! VRFインターフェース設定
interface {{interface_name}}
 vrf attach {{vrf_name}}
!
! VRF OSPF設定
router ospf {{ospf_process_id}}
 vrf {{vrf_name}}
!
! VRF BGP設定
router bgp {{as_number}}
 vrf {{vrf_name}}
```

### セキュリティ設定
```cisco
! セキュリティ設定
!
! ACL設定
ip access-list {{acl_name}}
!
! 標準ACL設定
ip access-list {{acl_name}}
 {{action}} {{source_network}} {{wildcard}}
!
! 拡張ACL設定
ip access-list {{acl_name}}
 {{action}} {{protocol}} {{source_network}} {{wildcard}} {{destination_network}} {{wildcard}} eq {{port}}
!
! ACL適用
interface {{interface_name}}
 ip access-group {{acl_name}} {{direction}}
!
! MAC ACL設定
mac access-list {{mac_acl_name}}
!
! MAC ACL設定
mac access-list {{mac_acl_name}}
 {{action}} host {{source_mac}} host {{destination_mac}}
!
! MAC ACL適用
interface {{interface_name}}
 mac access-group {{mac_acl_name}} {{direction}}
!
! DHCPスヌーピング設定
feature dhcp snooping
!
! DHCPスヌーピンググローバル設定
dhcp snooping
!
! DHCPスヌーピングVLAN設定
dhcp snooping vlan {{vlan_id}}
!
! DHCPスヌーピングポート設定
interface {{interface_name}}
 ip dhcp snooping trust
!
! IP Source Guard設定
feature ip source guard
!
! IP Source Guardインターフェース設定
interface {{interface_name}}
 ip verify source
!
! Dynamic ARP Inspection設定
feature arp inspection
!
! Dynamic ARP InspectionVLAN設定
arp inspection vlan {{vlan_id}}
!
! Dynamic ARP Inspectionポート設定
interface {{interface_name}}
 ip arp inspection trust
!
! Port Security設定
interface {{interface_name}}
 switchport port-security
 switchport port-security maximum {{max_mac}}
 switchport port-security violation {{violation_mode}}
 switchport port-security mac-address sticky
!
! Storm Control設定
interface {{interface_name}}
 storm-control broadcast level {{broadcast_level}}
 storm-control multicast level {{multicast_level}}
 storm-control unicast level {{unicast_level}}
```

### FCoE設定
```cisco
! FCoE設定
!
! FCoE有効化
feature fcoe
!
! FCoE VLAN設定
vlan {{fcoe_vlan_id}}
 name {{fcoe_vlan_name}}
!
! FCoEインターフェース設定
interface {{interface_name}}
 fcoe
!
! FCoEポートチャネル設定
interface port-channel {{channel_id}}
 fcoe
!
! FCoEマルチキャスト設定
fcoe fcf priority {{fcf_priority}}
!
! FCoEマップ設定
fcoe map {{fcoe_map_name}}
 interface {{interface_name}}
```

### QoS設定
```cisco
! QoS設定
!
! QoS有効化
feature qos
!
! QoSポリシー設定
class-map {{class_map_name}}
!
! QoSクラスマップ設定
class-map {{class_map_name}}
 match {{match_criteria}}
!
! QoSポリシーマップ設定
policy-map {{policy_map_name}}
!
! QoSポリシーマップクラス設定
policy-map {{policy_map_name}}
 class {{class_map_name}}
  {{action}} {{action_parameters}}
!
! QoS適用
interface {{interface_name}}
 service-policy input {{policy_map_name}}
 service-policy output {{policy_map_name}}
!
! QoSシェイプ設定
policy-map {{shape_policy_name}}
 class class-default
  shape average {{shape_rate}}
!
! QoSポリシング設定
policy-map {{police_policy_name}}
 class {{class_map_name}}
  police {{cir}} {{bc}} conform-action {{conform_action}} exceed-action {{exceed_action}}
!
! QoSマーキング設定
policy-map {{mark_policy_name}}
 class {{class_map_name}}
  set dscp {{dscp_value}}
  set cos {{cos_value}}
```

### 高可用性設定
```cisco
! 高可用性設定
!
! VPC設定
feature vpc
!
! VPCドメイン設定
vpc domain {{vpc_domain_id}}
!
! VPCピアリンク設定
interface port-channel {{peer_link_id}}
 vpc peer-link
!
! VPC設定
interface {{interface_name}}
 vpc {{vpc_id}}
!
! VPC冗長設定
vpc domain {{vpc_domain_id}}
 redundancy {{redundancy_mode}}
!
! VPCトラッキング設定
vpc domain {{vpc_domain_id}}
 peer-keepalive destination {{peer_keepalive_ip}}
 peer-keepalive source {{peer_keepalive_source}}
!
! VPCプロファイル設定
vpc domain {{vpc_domain_id}}
 auto-recovery
!
! スタック設定
feature switch virtual
!
! スタックドメイン設定
switch virtual domain {{domain_id}}
!
! スタックピア設定
switch virtual peer {{peer_ip}}
!
! スタック設定
switch virtual link {{link_id}}
```

### 監視設定
```cisco
! 監視設定
!
! NetFlow設定
feature netflow
!
! NetFlowエクスポート設定
flow exporter {{exporter_name}}
 destination {{exporter_destination}}
 source {{exporter_source}}
!
! NetFlowレコード設定
flow record {{record_name}}
 match ipv4 source address
 match ipv4 destination address
 match transport source port
 match transport destination port
!
! NetFlowインターフェース設定
interface {{interface_name}}
 flow record {{record_name}}
 flow exporter {{exporter_name}}
!
! IP SLA設定
feature ip sla
!
! IP SLA操作設定
ip sla {{operation_id}}
 icmp-echo {{target_ip}}
!
! IP SLAスケジュール設定
ip sla schedule {{operation_id}} life forever start-time now
!
! IP SLA追跡設定
track {{track_id}} ip sla {{operation_id}} reachability
!
! EEM設定
event manager applet {{applet_name}}
 event {{event_type}}
 action {{action_type}} {{action_parameters}}
!
! セッション設定
session-name {{session_name}}
```

### その他の設定
```cisco
! その他の設定
!
! 設定バックアップ設定
copy running-config startup-config
!
! 設定リストア設定
copy startup-config running-config
!
! 設定エクスポート設定
copy running-config {{export_destination}}
!
! 設定インポート設定
copy {{import_source}} running-config
!
! 設定バージョン設定
version {{version_string}}
!
! 設定コミット設定
commit
!
! 設定ロールバック設定
rollback {{rollback_number}}
!
! 設定同期設定
sync
!
! 設定バックアップ設定
backup
!
! 設定リストア設定
restore
!
! 設定エクスポート設定
export
!
! 設定インポート設定
import
!
! 保存設定
end
```

## 変数一覧
| 変数名 | 説明 | 例 |
|--------|------|-----|
| {{hostname}} | ホスト名 | NEXUS-01 |
| {{domain_name}} | ドメイン名 | company.local |
| {{ntp_server}} | NTPサーバー | 192.168.1.1 |
| {{dns_server1}} | DNSサーバー1 | 8.8.8.8 |
| {{dns_server2}} | DNSサーバー2 | 8.8.4.4 |
| {{admin_password}} | 管理者パスワード | password123 |
| {{community_string}} | SNMPコミュニティ文字列 | public_ro |
| {{community_string_rw}} | SNMP RWコミュニティ文字列 | private_rw |
| {{snmp_server}} | SNMPサーバー | 192.168.1.100 |
| {{severity_level}} | シverityレベル | 6 |
| {{radius_server}} | RADIUSサーバー | RADIUS-SRV |
| {{radius_ip}} | RADIUS IP | 192.168.1.200 |
| {{auth_port}} | 認証ポート | 1812 |
| {{acct_port}} | アカウンティングポート | 1813 |
| {{radius_key}} | RADIUSキー | radiuskey123 |
| {{tacacs_server}} | TACACS+サーバー | TACACS-SRV |
| {{tacacs_ip}} | TACACS+ IP | 192.168.1.300 |
| {{tacacs_key}} | TACACS+キー | tacacskey123 |
| {{interface_name}} | インターフェース名 | Ethernet1/1 |
| {{description}} | インターフェース説明 | Server Connection |
| {{interface_number}} | インターフェース番号 | 1 |
| {{channel_id}} | チャネルID | 1 |
| {{channel_description}} | チャネル説明 | Uplink Channel |
| {{start_port}} | 開始ポート | 1 |
| {{end_port}} | 終了ポート | 2 |
| {{vlan_id}} | VLAN ID | 10 |
| {{vlan_name}} | VLAN名 | Management |
| {{vlan_description}} | VLAN説明 | Management Network |
| {{vlan_state}} | VLAN状態 | active |
| {{vlan_start}} | VLAN開始ID | 10 |
| {{vlan_end}} | VLAN終了ID | 100 |
| {{pvlan_type}} | Private VLANタイプ | community |
| {{primary_vlan_id}} | Primary VLAN ID | 100 |
| {{secondary_vlan_id}} | Secondary VLAN ID | 101 |
| {{secondary_vlan_ids}} | Secondary VLAN IDs | 101,102 |
| {{loopback_id}} | ループバックID | 0 |
| {{loopback_description}} | ループバック説明 | Management Loopback |
| {{mgmt_description}} | 管理インターフェース説明 | OOB Management |
| {{subinterface_id}} | サブインターフェースID | 100 |
| {{spanning_tree_mode}} | スパニングツリーモード | rapid-pvst |
| {{guard_type}} | ガードタイプ | root |
| {{lacp_mode}} | LACPモード | active |
| {{channel_mode}} | チャネルモード | active |
| {{lldp_timer}} | LLDPタイマー | 30 |
| {{lldp_reinit}} | LLDPリイニット | 2 |
| {{lldp_holdtime}} | LLDPホールドタイム | 120 |
| {{cdp_timer}} | CDPタイマー | 60 |
| {{cdp_holdtime}} | CDPホールドタイム | 180 |
| {{ospf_process_id}} | OSPFプロセスID | 1 |
| {{router_id}} | ルータID | 10.1.1.1 |
| {{network_address}} | ネットワークアドレス | 10.1.1.0 |
| {{wildcard_mask}} | ワイルドカードマスク | 0.0.0.255 |
| {{area_id}} | OSPFエリアID | 0 |
| {{reference_bandwidth}} | 参照帯域幅 | 1000 |
| {{as_number}} | AS番号 | 65001 |
| {{neighbor_ip}} | ネイバーIP | 10.1.1.2 |
| {{neighbor_as}} | ネイバーAS | 65002 |
| {{neighbor_description}} | ネイバー説明 | Peer Router |
| {{route_map_name}} | ルートマップ名 | ROUTE_MAP |
| {{rr_ip}} | ルートリフレクタIP | 10.1.1.3 |
| {{prefix_list_name}} | プレフィックスリスト名 | PREFIX_LIST |
| {{prefix_length}} | プレフィックス長 | 24 |
| {{destination_network}} | 宛先ネットワーク | 0.0.0.0 |
| {{subnet_mask}} | サブネットマスク | 0.0.0.0 |
| {{default_gateway}} | デフォルトゲートウェイ | 192.168.1.1 |
| {{vrf_name}} | VRF名 | MANAGEMENT |
| {{route_distinguisher}} | ルートディスティングイッシャー | 65001:100 |
| {{route_limit}} | ルート制限 | 1000 |
| {{acl_name}} | ACL名 | INBOUND_ACL |
| {{action}} | アクション | permit |
| {{protocol}} | プロトコル | tcp |
| {{port}} | ポート番号 | 80 |
| {{direction}} | 方向 | in |
| {{mac_acl_name}} | MAC ACL名 | MAC_ACL |
| {{source_mac}} | ソースMAC | 00:1A:2B:3C:4D:5E |
| {{destination_mac}} | 宛先MAC | 00:1A:2B:3C:4D:5F |
| {{max_mac}} | 最大MAC数 | 2 |
| {{violation_mode}} | 違反モード | restrict |
| {{broadcast_level}} | ブロードキャストレベル | 20 |
| {{multicast_level}} | マルチキャストレベル | 20 |
| {{unicast_level}} | ユニキャストレベル | 20 |
| {{fcoe_vlan_id}} | FCoE VLAN ID | 50 |
| {{fcoe_vlan_name}} | FCoE VLAN名 | FCoE |
| {{fcf_priority}} | FCF優先度 | 128 |
| {{fcoe_map_name}} | FCoEマップ名 | FCOE_MAP |
| {{class_map_name}} | クラスマップ名 | CRITICAL_TRAFFIC |
| {{match_criteria}} | マッチ基準 | dscp ef |
| {{policy_map_name}} | ポリシーマップ名 | QOS_POLICY |
| {{action}} | アクション | bandwidth |
| {{action_parameters}} | アクションパラメータ | percent 30 |
| {{shape_policy_name}} | シェイプポリシー名 | SHAPE_POLICY |
| {{shape_rate}} | シェイプレート | 1000000 |
| {{police_policy_name}} | ポリスポリシー名 | POLICE_POLICY |
| {{cir}} | コミットレート | 1000000 |
| {{bc}} | バーストカレント | 100000 |
| {{conform_action}} | コンフォームアクション | transmit |
| {{exceed_action}} | 超過アクション | drop |
| {{mark_policy_name}} | マークポリシー名 | MARK_POLICY |
| {{dscp_value}} | DSCP値 | ef |
| {{cos_value}} | COS値 | 5 |
| {{vpc_domain_id}} | VPCドメインID | 1 |
| {{peer_link_id}} | ピアリンクID | 100 |
| {{vpc_id}} | VPC ID | 10 |
| {{redundancy_mode}} | 冗長モード | high-availability |
| {{peer_keepalive_ip}} | ピアキープアライブIP | 192.168.1.100 |
| {{peer_keepalive_source}} | ピアキープアライブソース | 192.168.1.101 |
| {{domain_id}} | ドメインID | 1 |
| {{peer_ip}} | ピアIP | 192.168.1.102 |
| {{link_id}} | リンクID | 1 |
| {{exporter_name}} | エクスポーター名 | NETFLOW_EXPORTER |
| {{exporter_destination}} | エクスポーターデスティネーション | 192.168.1.300 |
| {{exporter_source}} | エクスポーターソース | loopback0 |
| {{record_name}} | レコード名 | FLOW_RECORD |
| {{operation_id}} | 操作ID | 1 |
| {{target_ip}} | ターゲットIP | 8.8.8.8 |
| {{track_id}} | トラッキングID | 1 |
| {{applet_name}} | アプレット名 | MONITOR_APPLET |
| {{event_type}} | イベントタイプ | timer |
| {{action_type}} | アクションタイプ | cli |
| {{action_parameters}} | アクションパラメータ | show interface |
| {{session_name}} | セッション名 | CONFIG_SESSION |
| {{export_destination}} | エクスポート先 | tftp://192.168.1.200/backup.cfg |
| {{import_source}} | インポート元 | tftp://192.168.1.200/backup.cfg |
| {{version_string}} | バージョン文字列 | 8.0(3)I7(1) |
| {{rollback_number}} | ロールバック番号 | 1 |


