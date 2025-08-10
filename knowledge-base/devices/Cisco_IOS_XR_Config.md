


# Cisco IOS-XR Configuration Template

## デバイスタイプ
- **タイプ**: サービスプロバイダールータ
- **OS**: Cisco IOS-XR
- **モデル**: ASR9000/ASR9000シリーズ
- **用途**: コアルータ、エッジルータ

## 基本設定
```cisco
! 基本設定
!
! ターミナル設定
terminal length 0
!
! ホスト名設定
hostname {{hostname}}
!
! ドメイン名設定
domain name {{domain_name}}
!
! NTP設定
!
! NTPサーバー設定
ntp server {{ntp_server}}
!
! DNS設定
!
! DNSサーバー設定
dns server {{dns_server1}}
dns server {{dns_server2}}
!
! 特権EXECモードパスワード
username admin password {{admin_password}}
username admin group root-system
username admin group cisco-support
!
! VTYコンソール設定
!
! SSH設定
ssh server v2
ssh server port {{ssh_port}}
!
! Telnet設定（非推奨）
telnet server
!
! SNMP設定
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
!
! RADIUSサーバー設定
radius server {{radius_server}}
 address ipv4 {{radius_ip}} auth-port {{auth_port}} acct-port {{acct_port}}
 key {{radius_key}}
!
! TACACS+設定
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
! Bundle-Ethernetインターフェース設定
interface Bundle-Ethernet {{bundle_id}}
 description {{bundle_description}}
!
! Bundle-Ethernetメンバ設定
interface TenGigE {{interface_number}}
 description {{member_description}}
!
! Bundle-Ethernetメンバ追加
interface Bundle-Ethernet {{bundle_id}}
 TenGigE {{interface_number}}
!
! Loopbackインターフェース設定
interface Loopback{{loopback_id}}
 description {{loopback_description}}
!
! Loopback0（管理用）設定
interface Loopback0
 description Management Loopback
 ipv4 address {{loopback_ip}} {{loopback_mask}}
!
! Loopback1（Router-ID用）設定
interface Loopback1
 description Router-ID Loopback
 ipv4 address {{router_id_ip}} {{router_id_mask}}
!
! POSインターフェース設定
interface POS{{pos_interface_number}}
 description {{pos_description}}
!
! SONET/SDH設定
interface POS{{pos_interface_number}}
 sonet {{sonet_options}}
!
! DWDMインターフェース設定
interface HundredGigE {{interface_number}}
 description {{dwdm_description}}
!
! サブインターフェース設定
interface Bundle-Ethernet {{bundle_id}}.{{subinterface_id}}
 description {{subinterface_description}}
 ipv4 address {{subinterface_ip}} {{subinterface_mask}}
!
! VLANサブインターフェース設定
interface Bundle-Ethernet {{bundle_id}}.{{subinterface_id}}
 encapsulation dot1q {{vlan_id}}
 ipv4 address {{subinterface_ip}} {{subinterface_mask}}
!
! イーサネットインターフェース設定
interface HundredGigE {{interface_number}}
 description {{ethernet_description}}
!
! ギガビットイーサネットインターフェース設定
interface GigabitEthernet {{interface_number}}
 description {{gigabit_description}}
!
! ファイバーチャネルインターフェース設定
interface FibreChannel {{interface_number}}
 description {{fc_description}}
```

### L3ルーティング設定
```cisco
! L3ルーティング設定
!
! IPルーティング有効化
!
! OSPF設定
router ospf {{ospf_process_id}}
!
! OSPFインスタンス設定
router ospf {{ospf_process_id}}
 vrf {{vrf_name}}
!
! OSPFネットワーク設定
router ospf {{ospf_process_id}}
 area {{area_id}}
  interface {{interface_name}}
   network {{network_address}} {{wildcard_mask}}
!
! OSPFエリア設定
router ospf {{ospf_process_id}}
 area {{area_id}}
  range {{network_address}} {{wildcard_mask}}
!
! OSPFインターフェース設定
router ospf {{ospf_process_id}}
 area {{area_id}}
  interface {{interface_name}}
   cost {{cost}}
   hello-interval {{hello_interval}}
   dead-interval {{dead_interval}}
!
! OSPFパラメータ設定
router ospf {{ospf_process_id}}
 auto-cost reference-bandwidth {{reference_bandwidth}}
!
! OSPF外部ルート設定
router ospf {{ospf_process_id}}
 area {{area_id}}
  external-type {{external_type}}
!
! BGP設定
router bgp {{as_number}}
!
! BGPグローバル設定
router bgp {{as_number}}
 bgp router-id {{router_id}}
!
! BGPネイバー設定
router bgp {{as_number}}
 neighbor {{neighbor_ip}} remote-as {{neighbor_as}}
 neighbor {{neighbor_ip}} description {{neighbor_description}}
!
! BGPネイバー設定（IPv6）
router bgp {{as_number}}
 neighbor {{neighbor_ipv6}} remote-as {{neighbor_as}}
 neighbor {{neighbor_ipv6}} description {{neighbor_description}}
!
! BGPネットワーク設定
router bgp {{as_number}}
 address-family ipv4
  network {{network_address}} mask {{subnet_mask}}
!
! BGPネットワーク設定（IPv6）
router bgp {{as_number}}
 address-family ipv6
  network {{network_address}}/{{prefix_length}}
!
! BGPコミュニティ設定
router bgp {{as_number}}
 address-family ipv4
  neighbor {{neighbor_ip}} send-community
  neighbor {{neighbor_ip}} route-map {{route_map_name}} in
  neighbor {{neighbor_ip}} route-map {{route_map_name}} out
!
! BGPルートリフレクタ設定
router bgp {{as_number}}
 address-family ipv4
  neighbor {{rr_ip}} route-reflector-client
!
! BGPルートフィルタリング設定
router bgp {{as_number}}
 address-family ipv4
  prefix-list {{prefix_list_name}} permit {{network_address}} {{prefix_length}}
!
! BGPパス属性設定
router bgp {{as_number}}
 address-family ipv4
  neighbor {{neighbor_ip}} weight {{weight}}
  neighbor {{neighbor_ip}} local-preference {{local_pref}}
!
! BGPアグリゲート設定
router bgp {{as_number}}
 address-family ipv4
  aggregate-address {{aggregate_address}} {{aggregate_mask}} {{summary_only}}
!
! 静的ルート設定
!
! IPv4静的ルート設定
ip route {{destination_network}} {{subnet_mask}} {{next_hop}}
!
! IPv4静的ルート設定（VRF）
ip route vrf {{vrf_name}} {{destination_network}} {{subnet_mask}} {{next_hop}}
!
! IPv6静的ルート設定
ipv6 route {{destination_network}}/{{prefix_length}} {{next_hop}}
!
! IPv6静的ルート設定（VRF）
ipv6 route vrf {{vrf_name}} {{destination_network}}/{{prefix_length}} {{next_hop}}
!
! デフォルトルート設定
!
! IPv4デフォルトルート設定
ip route 0.0.0.0 0.0.0.0 {{default_gateway}}
!
! IPv6デフォルトルート設定
ipv6 route ::/0 {{next_hop}}
!
! PBR設定
!
! PBRルートマップ設定
route-map {{route_map_name}} permit 10
 match ip address {{acl_name}}
 set ip next-hop {{next_hop}}
!
! PBRインターフェース適用
interface {{interface_name}}
 service-policy input {{policy_map_name}}
```

### MPLS設定
```cisco
! MPLS設定
!
! MPLS有効化
mpls ldp
!
! MPLS LDP設定
mpls ldp
!
! MPLS LDPインターフェース設定
mpls ldp
 interface {{interface_name}}
!
! MPLS TE設定
mpls traffic-eng
!
! MPLS TEインターフェース設定
mpls traffic-eng
 interface {{interface_name}}
!
! MPLS TEトンネル設定
mpls traffic-eng tunnels
!
! MPLS TEトンネル作成
mpls traffic-eng tunnel {{tunnel_id}}
 destination {{destination_ip}}
!
! MPLS TEトンネル設定
mpls traffic-eng tunnel {{tunnel_id}}
 bandwidth {{bandwidth}}
!
! MPLS VPN設定
!
! VRF設定
vrf {{vrf_name}}
!
! VRF RD設定
vrf {{vrf_name}}
 rd {{route_distinguisher}}
!
! VRF RT設定
vrf {{vrf_name}}
 route-target {{route_target}}
!
! VRFインターフェース設定
interface {{interface_name}}
 vrf attach {{vrf_name}}
!
! MP-BGP設定
!
! MP-BGP設定
router bgp {{as_number}}
 address-family vpnv4
!
! MP-BGPネイバー設定
router bgp {{as_number}}
 address-family vpnv4
  neighbor {{neighbor_ip}} activate
  neighbor {{neighbor_ip}} send-community both
!
! MP-BGPルートリフレクタ設定
router bgp {{as_number}}
 address-family vpnv4
  neighbor {{rr_ip}} route-reflector-client
!
! L2VPN設定
!
! L2VPN VPLS設定
l2vpn vpls {{vpls_name}}
!
! L2VPN VPLSサイト設定
l2vpn vpls {{vpls_name}}
 site {{site_id}}
  ce-id {{ce_id}}
  ce-range {{ce_range}}
!
! L2VPN VPLS接続設定
l2vpn vpls {{vpls_name}}
 site {{site_id}}
  neighbor {{neighbor_site_id}}
   pw-id {{pw_id}}
```

### セキュリティ設定
```cisco
! セキュリティ設定
!
! ACL設定
!
! IPv4 ACL設定
ip access-list {{acl_name}}
!
! IPv4 ACLエントリ設定
ip access-list {{acl_name}}
 {{action}} {{protocol}} {{source_network}} {{wildcard}} {{destination_network}} {{wildcard}} eq {{port}}
!
! IPv6 ACL設定
ipv6 access-list {{ipv6_acl_name}}
!
! IPv6 ACLエントリ設定
ipv6 access-list {{ipv6_acl_name}}
 {{action}} {{protocol}} {{source_ipv6}}/{{prefix_length}} {{destination_ipv6}}/{{prefix_length}} eq {{port}}
!
! ACL適用
!
! IPv4 ACL適用
interface {{interface_name}}
 ip access-group {{acl_name}} {{direction}}
!
! IPv6 ACL適用
interface {{interface_name}}
 ipv6 traffic-filter {{ipv6_acl_name}} {{direction}}
!
! ZBFW設定
!
! ゾーン設定
zone security {{zone_name}}
 description {{zone_description}}
!
! ゾーンペア設定
zone-pair security {{zone_pair_name}} source {{source_zone}} destination {{destination_zone}}
 service-policy type inspect {{policy_map_name}}
!
! クラスマップ設定
class-map {{class_map_name}}
 match access-group name {{acl_name}}
!
! ポリシーマップ設定
policy-map {{policy_map_name}}
 class {{class_map_name}}
  inspect {{inspection_name}}
!
! ZBFW適用
interface {{interface_name}
 zone security {{zone_name}}
!
! NTPアクセス制御
!
! NTPアクセスリスト設定
ntp access-group peer {{acl_name}}
!
! NTPアクセスリストエントリ設定
ip access-list {{acl_name}}
 permit {{ntp_server}}
!
! SSHアクセス制御
!
! SSHアクセスリスト設定
ssh server acl {{acl_name}}
!
! SSHアクセスリストエントリ設定
ip access-list {{acl_name}}
 permit {{ssh_network}} {{wildcard}}
!
! ローカル認証設定
!
! ローカルユーザー設定
username {{username}} password {{password}}
username {{username}} group {{group}}
!
! ローカルユーザーロール設定
role {{role_name}}
 description {{role_description}}
!
! ローカルユーザーロール権限設定
role {{role_name}}
 command {{command_permission}} {{command}}
!
! ローカルユーザーロール割り当て
username {{username}} role {{role_name}}
```

### QoS設定
```cisco
! QoS設定
!
! QoSポリシー設定
!
! クラスマップ設定
class-map {{class_map_name}}
!
! クラスマップマッチ条件設定
class-map {{class_map_name}}
 match {{match_criteria}}
!
! ポリシーマップ設定
policy-map {{policy_map_name}}
!
! ポリシーマップクラス設定
policy-map {{policy_map_name}}
 class {{class_map_name}}
  {{action}} {{action_parameters}}
!
! QoS適用
!
! QoSポリシー適用
interface {{interface_name}}
 service-policy input {{policy_map_name}}
 service-policy output {{policy_map_name}}
!
! シェイプ設定
!
! シェイプポリシー設定
policy-map {{shape_policy_name}}
 class class-default
  shape average {{shape_rate}}
!
! ポリシング設定
!
! ポリスポリシー設定
policy-map {{police_policy_name}}
 class {{class_map_name}}
  police {{cir}} {{bc}} conform-action {{conform_action}} exceed-action {{exceed_action}}
!
! マーキング設定
!
! マークポリシー設定
policy-map {{mark_policy_name}}
 class {{class_map_name}}
  set dscp {{dscp_value}}
  set precedence {{precedence_value}}
!
! CBWFQ設定
!
! CBWFQポリシー設定
policy-map {{cbwfq_policy_name}}
 class {{class_map_name}}
  bandwidth {{bandwidth_value}}
!
! LLQ設定
!
! LLQポリシー設定
policy-map {{llq_policy_name}}
 class {{class_map_name}}
  priority {{priority_value}}
!
! ポートQoS設定
!
! ポートQoS有効化
qos
!
! ポートQoSポリシー設定
policy-map {{port_qos_policy_name}}
 class class-default
  shape average {{port_shape_rate}}
```

### 高可用性設定
```cisco
! 高可用性設定
!
! SRG設定
!
! SRGグループ設定
redundancy group {{redundancy_group_id}}
!
! SRGインターフェース設定
redundancy group {{redundancy_group_id}}
 interface {{interface_name}}
!
! SRGトラッキング設定
redundancy group {{redundancy_group_id}}
 track {{track_object}}
!
! SRG優先度設定
redundancy group {{redundancy_group_id}}
 priority {{priority}}
!
! SRG状態設定
redundancy group {{redundancy_group_id}}
 mode {{redundancy_mode}}
!
! FHRP設定
!
! VRRP設定
!
! VRRPバーチャルルータ設定
vrrp {{vrrp_id}}
!
! VRRPバーチャルルータインターフェース設定
vrrp {{vrrp_id}}
 interface {{interface_name}}
!
! VRRPバーチャルルータIP設定
vrrp {{vrrp_id}}
 ip address {{virtual_ip}}
!
! VRRPバーチャルルータ優先度設定
vrrp {{vrrp_id}}
 priority {{priority}}
!
! VRRPバーチャルルータトラッキング設定
vrrp {{vrrp_id}}
 track {{track_object}}
!
! HSRP設定
!
! HSRPグループ設定
standby {{hsrp_group_id}}
!
! HSRPグループインターフェース設定
standby {{hsrp_group_id}}
 interface {{interface_name}}
!
! HSRPグループIP設定
standby {{hsrp_group_id}}
 ip address {{virtual_ip}}
!
! HSRPグループ優先度設定
standby {{hsrp_group_id}}
 priority {{priority}}
!
! HSRPグループトラッキング設定
standby {{hsrp_group_id}}
 track {{track_object}}
```

### 監視設定
```cisco
! 監視設定
!
! NetFlow設定
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
!
! EEMアプレット設定
event manager applet {{applet_name}}
 event {{event_type}}
 action {{action_type}} {{action_parameters}}
!
! セッション設定
!
! セッション名設定
session-name {{session_name}}
!
! セッションタイムアウト設定
session-timeout {{timeout}}
!
! セッションログ設定
session-logging
```

### その他の設定
```cisco
! その他の設定
!
! 設定バックアップ設定
!
! 設定バックアップ実行
commit
!
! 設定バックアップ確認
show running-config
!
! 設定リストア設定
!
! 設定リストア実行
commit replace
!
! 設定リストア確認
show running-config
!
! 設定エクスポート設定
!
! 設定エクスポート実行
copy running-config {{export_destination}}
!
! 設定インポート設定
!
! 設定インポート実行
copy {{import_source}} running-config
!
! 設定バージョン設定
!
! 設定バージョン確認
show version
!
! 設定コミット設定
!
! 設定コミット実行
commit
!
! 設定コミット確認
show commit
!
! 設定ロールバック設定
!
! 設定ロールバック実行
rollback {{rollback_number}}
!
! 設定ロールバック確認
show running-config rollback {{rollback_number}}
!
! 設定同期設定
!
! 設定同期実行
sync
!
! 設定同期確認
show sync status
!
! 保存設定
!
! 設定保存実行
commit
!
! 設定保存確認
show running-config
```

## 変数一覧
| 変数名 | 説明 | 例 |
|--------|------|-----|
| {{hostname}} | ホスト名 | ASR-9001 |
| {{domain_name}} | ドメイン名 | isp.local |
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
| {{interface_name}} | インターフェース名 | Bundle-Ether1 |
| {{description}} | インターフェース説明 | Core Link |
| {{bundle_id}} | バンドルID | 1 |
| {{bundle_description}} | バンドル説明 | Uplink Bundle |
| {{interface_number}} | インターフェース番号 | 0/1/0/0 |
| {{member_description}} | メンバ説明 | Member Interface |
| {{loopback_id}} | ループバックID | 0 |
| {{loopback_description}} | ループバック説明 | Management Loopback |
| {{loopback_ip}} | ループバックIP | 10.1.1.1 |
| {{loopback_mask}} | ループバックマスク | 255.255.255.255 |
| {{router_id_ip}} | ルータID IP | 10.1.1.1 |
| {{router_id_mask}} | ルータIDマスク | 255.255.255.255 |
| {{pos_interface_number}} | POSインターフェース番号 | 0/1/0/1 |
| {{pos_description}} | POS説明 | OC-192 Link |
| {{sonet_options}} | SONETオプション | sonet |
| {{dwdm_description}} | DWDM説明 | 100G DWDM Link |
| {{subinterface_id}} | サブインターフェースID | 100 |
| {{subinterface_description}} | サブインターフェース説明 | Customer Subinterface |
| {{subinterface_ip}} | サブインターフェースIP | 10.1.1.1 |
| {{subinterface_mask}} | サブインターフェースマスク | 255.255.255.0 |
| {{vlan_id}} | VLAN ID | 100 |
| {{ethernet_description}} | イーサネット説明 | 100G Ethernet |
| {{gigabit_description}} | ギガビット説明 | 1G Ethernet |
| {{fc_description}} | ファイバー説明 | Fibre Channel |
| {{ospf_process_id}} | OSPFプロセスID | 1 |
| {{vrf_name}} | VRF名 | CUSTOMER-A |
| {{area_id}} | OSPFエリアID | 0 |
| {{network_address}} | ネットワークアドレス | 10.1.1.0 |
| {{wildcard_mask}} | ワイルドカードマスク | 0.0.0.255 |
| {{cost}} | コスト | 10 |
| {{hello_interval}} | Hello間隔 | 10 |
| {{dead_interval}} | Dead間隔 | 40 |
| {{reference_bandwidth}} | 参照帯域幅 | 10000 |
| {{external_type}} | 外部タイプ | 1 |
| {{as_number}} | AS番号 | 65001 |
| {{router_id}} | ルータID | 10.1.1.1 |
| {{neighbor_ip}} | ネイバーIP | 10.1.1.2 |
| {{neighbor_as}} | ネイバーAS | 65002 |
| {{neighbor_description}} | ネイバー説明 | Peer Router |
| {{neighbor_ipv6}} | ネイバーIPv6 | 2001:db8::2 |
| {{subnet_mask}} | サブネットマスク | 255.255.255.0 |
| {{prefix_length}} | プレフィックス長 | 24 |
| {{route_map_name}} | ルートマップ名 | ROUTE_MAP |
| {{rr_ip}} | ルートリフレクタIP | 10.1.1.3 |
| {{prefix_list_name}} | プレフィックスリスト名 | PREFIX_LIST |
| {{weight}} | ウェイト | 100 |
| {{local_pref}} | ローカルプリファレンス | 200 |
| {{aggregate_address}} | 集約アドレス | 10.1.0.0 |
| {{aggregate_mask}} | 集約マスク | 255.255.0.0 |
| {{summary_only}} | サマリーのみ | summary-only |
| {{destination_network}} | 宛先ネットワーク | 0.0.0.0 |
| {{next_hop}} | ネクストホップ | 192.168.1.1 |
| {{default_gateway}} | デフォルトゲートウェイ | 192.168.1.1 |
| {{vrf_name}} | VRF名 | MANAGEMENT |
| {{route_distinguisher}} | ルートディスティングイッシャー | 65001:100 |
| {{route_target}} | ルートターゲット | 65001:100 |
| {{acl_name}} | ACL名 | INBOUND_ACL |
| {{action}} | アクション | permit |
| {{protocol}} | プロトコル | tcp |
| {{port}} | ポート番号 | 80 |
| {{direction}} | 方向 | in |
| {{ipv6_acl_name}} | IPv6 ACL名 | INBOUND_IPV6_ACL |
| {{source_ipv6}} | ソースIPv6 | 2001:db8::1 |
| {{destination_ipv6}} | 宛先IPv6 | 2001:db8::2 |
| {{zone_name}} | ゾーン名 | TRUSTED |
| {{zone_description}} | ゾーン説明 | Trusted Zone |
| {{zone_pair_name}} | ゾーンペア名 | TRUSTED-UNTRUSTED |
| {{source_zone}} | ソースゾーン | TRUSTED |
| {{destination_zone}} | 宛先ゾーン | UNTRUSTED |
| {{policy_map_name}} | ポリシーマップ名 | INSPECT_POLICY |
| {{class_map_name}} | クラスマップ名 | CRITICAL_TRAFFIC |
| {{match_criteria}} | マッチ基準 | dscp ef |
| {{inspection_name}} | 検査名 | default-inspection |
| {{ssh_port}} | SSHポート | 22 |
| {{ssh_network}} | SSHネットワーク | 192.168.1.0 |
| {{wildcard}} | ワイルドカード | 0.0.0.255 |
| {{username}} | ユーザー名 | admin |
| {{password}} | パスワード | password123 |
| {{group}} | グループ | network-admin |
| {{role_name}} | ロール名 | NETWORK_ADMIN |
| {{role_description}} | ロール説明 | Network Administrator |
| {{command_permission}} | コマンド権限 | permit |
| {{command}} | コマンド | configure |
| {{shape_policy_name}} | シェイプポリシー名 | SHAPE_POLICY |
| {{shape_rate}} | シェイプレート | 1000000 |
| {{police_policy_name}} | ポリスポリシー名 | POLICE_POLICY |
| {{cir}} | コミットレート | 1000000 |
| {{bc}} | バーストカレント | 100000 |
| {{conform_action}} | コンフォームアクション | transmit |
| {{exceed_action}} | 超過アクション | drop |
| {{mark_policy_name}} | マークポリシー名 | MARK_POLICY |
| {{dscp_value}} | DSCP値 | ef |
| {{precedence_value}} | プリセンス値 | 5 |
| {{cbwfq_policy_name}} | CBWFQポリシー名 | CBWFQ_POLICY |
| {{bandwidth_value}} | 帯域幅値 | 1000000 |
| {{llq_policy_name}} | LLQポリシー名 | LLQ_POLICY |
| {{priority_value}} | 優先度値 | 500000 |
| {{port_qos_policy_name}} | ポートQoSポリシー名 | PORT_QOS_POLICY |
| {{port_shape_rate}} | ポートシェイプレート | 10000000 |
| {{redundancy_group_id}} | 冗長グループID | 1 |
| {{track_object}} | トラッキングオブジェクト | 1 |
| {{priority}} | 優先度 | 100 |
| {{redundancy_mode}} | 冗長モード | active-standby |
| {{vrrp_id}} | VRRP ID | 1 |
| {{virtual_ip}} | 仮想IP | 192.168.1.100 |
| {{hsrp_group_id}} | HSRPグループID | 1 |
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
| {{timeout}} | タイムアウト | 3600 |
| {{export_destination}} | エクスポート先 | tftp://192.168.1.200/backup.cfg |
| {{import_source}} | インポート元 | tftp://192.168.1.200/backup.cfg |
| {{rollback_number}} | ロールバック番号 | 1 |
| {{tunnel_id}} | トンネルID | 1 |
| {{destination_ip}} | 宛先IP | 10.1.1.2 |
| {{bandwidth}} | 帯域幅 | 1000000 |
| {{vpls_name}} | VPLS名 | VPLS-CUSTOMER |
| {{site_id}} | サイトID | 1 |
| {{ce_id}} | CE ID | 100 |
| {{ce_range}} | CEレンジ | 100-199 |
| {{neighbor_site_id}} | ネイバーサイトID | 2 |
| {{pw_id}} | PW ID | 1000 |


