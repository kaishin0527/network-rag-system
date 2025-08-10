

# Cisco Firepower Threat Defense (FTD) Configuration Template

## デバイスタイプ
- **タイプ**: ファイアウォール/UTM
- **OS**: Cisco Firepower Threat Defense
- **モデル**: Firepower 2100/4100シリーズ
- **用途**: エッジセキュリティ、UTM

## 基本設定
```cisco
! 基本設定
hostname {{hostname}}
domain-name {{domain_name}}
!
! NTP設定
ntp server {{ntp_server}} prefer
ntp server {{ntp_server_backup}}
!
! DNS設定
dns server {{dns_server1}}
dns server {{dns_server2}}
!
! 管理アクセス設定
management-access
!
! 特権EXECモードパスワード
enable password {{enable_password}}
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
username admin privilege 15 password {{admin_password}}
username monitor privilege 1 password {{monitor_password}}
!
! SSH設定
ssh key generate rsa modulus 2048
ssh server version 2
ssh server {{ssh_ip}} {{ssh_subnet}}
!
! Telnet設定（非推奨）
telnet server enable
telnet server {{telnet_ip}} {{telnet_subnet}}
```

### インターフェース設定
```cisco
! 物理インターフェース設定
interface {{interface_name}}
 description {{description}}
!
! イーサネットインターフェース
interface GigabitEthernet0/0
 description Outside Interface
 nameif outside
 security-level {{outside_security_level}}
 ip address {{outside_ip}} {{outside_mask}}
!
interface GigabitEthernet0/1
 description Inside Interface
 nameif inside
 security-level {{inside_security_level}}
 ip address {{inside_ip}} {{inside_mask}}
!
interface GigabitEthernet0/2
 description DMZ Interface
 nameif dmz
 security-level {{dmz_security_level}}
 ip address {{dmz_ip}} {{dmz_mask}}
!
! サブインターフェース設定
interface GigabitEthernet0/0.100
 encapsulation dot1Q 100
 nameif guest
 security-level {{guest_security_level}}
 ip address {{guest_ip}} {{guest_mask}}
!
! ループバックインターフェース
interface Loopback0
 description Management Loopback
 ip address {{loopback_ip}} {{loopback_mask}}
 management-only
!
! VLANインターフェース
interface Vlan10
 description Management Network
 nameif management
 security-level {{management_security_level}}
 ip address {{management_ip}} {{management_mask}}
 management-only
!
! ポートチャネル設定
interface Port-channel1
 description Uplink Channel
 nameif outside
 security-level {{outside_security_level}}
 ip address {{channel_ip}} {{channel_mask}}
!
! ポートチャネルメンバ
interface range GigabitEthernet0/0-1
 channel-group 1 mode active
!
! サブインターフェース（MPLS用）
interface GigabitEthernet0/0.200
 encapsulation dot1Q 200
 nameif mpls
 security-level {{mpls_security_level}}
 ip address {{mpls_ip}} {{mpls_mask}}
```

### ネットワークオブジェクト設定
```cisco
! ネットワークオブジェクト
object network {{object_name}}
 subnet {{network_address}} {{subnet_mask}}
!
! ホストオブジェクト
object network {{host_object_name}}
 host {{host_ip}}
!
! オブジェクトグループ
object-group network {{object_group_name}}
 network-object {{network_address}} {{subnet_mask}}
!
! サービスオブジェクト
object service {{service_object_name}}
 protocol {{protocol}}
 port {{port}}
!
! サービスオブジェクトグループ
object-group service {{service_group_name}}
 description {{service_group_description}}
 group-object {{service_object_name}}
!
! ICMPオブジェクト
object-group icmp-type {{icmp_group_name}}
 description {{icmp_group_description}}
 icmp-object {{icmp_type}}
!
! NATオブジェクト
object network {{nat_object_name}}
 nat {{nat_type}} {{interface_name}} {{mapped_ip}}
!
! ACLオブジェクト
object network {{acl_object_name}}
 description {{acl_object_description}}
 subnet {{network_address}} {{subnet_mask}}
```

### ACL設定
```cisco
! 標準ACL
access-list {{acl_name}} standard permit {{source_network}} {{wildcard}}
access-list {{acl_name}} standard deny any
!
! 拡張ACL
access-list {{acl_name}} extended permit tcp {{source_network}} {{wildcard}} {{destination_network}} {{wildcard}} eq {{port}}
access-list {{acl_name}} extended permit udp {{source_network}} {{wildcard}} {{destination_network}} {{wildcard}} eq {{port}}
access-list {{acl_name}} extended permit icmp {{source_network}} {{wildcard}} {{destination_network}} {{wildcard}} {{icmp_type}}
access-list {{acl_name}} extended deny ip any any
!
! IPv6 ACL
ipv6 access-list {{ipv6_acl_name}}
 permit tcp {{source_ipv6}}/{{prefix_length}} {{destination_ipv6}}/{{prefix_length}} eq {{port}}
 permit udp {{source_ipv6}}/{{prefix_length}} {{destination_ipv6}}/{{prefix_length}} eq {{port}}
 deny ipv6 any any
!
! タイムベースACL
time-range {{time_range_name}}
 periodic {{time_period}}
!
access-list {{acl_name}} extended permit tcp {{source_network}} {{wildcard}} {{destination_network}} {{wildcard}} eq {{port}} time-range {{time_range_name}}
```

### NAT設定
```cisco
! Dynamic PAT
object network {{pat_object_name}}
 nat ({{interface_name}}) {{interface_name}}
!
! Static NAT
object network {{static_nat_object_name}}
 host {{real_ip}}
 nat ({{inside_interface}}, {{outside_interface}}) {{mapped_ip}}
!
! Static NAT with Port Translation
object network {{static_pat_object_name}}
 host {{real_ip}}
 nat ({{inside_interface}}, {{outside_interface}}) static {{mapped_ip}} service {{protocol}} {{port}}
!
! Policy NAT
object network {{policy_nat_object_name}}
 nat ({{inside_interface}}, {{outside_interface}}) source static {{real_network}} {{mapped_network}}
!
! Twice NAT
object network {{twice_nat_object_name}}
 nat ({{inside_interface}}, {{outside_interface}}) source static {{real_ip}} {{mapped_ip}} destination static {{real_dest_ip}} {{mapped_dest_ip}}
!
! Identity NAT
object network {{identity_nat_object_name}}
 nat ({{inside_interface}}, {{outside_interface}}) source static {{real_ip}} {{real_ip}}
!
! NAT exemption
nat ({{inside_interface}}, {{outside_interface}}) source {{source_network}} {{destination_network}} no-proxy-arp
```

### セキュリティポリシー設定
```cisco
! セキュリティポリシー
access-list {{acl_name}} extended permit tcp {{source_network}} {{wildcard}} {{destination_network}} {{wildcard}} eq {{port}}
access-list {{acl_name}} extended permit udp {{source_network}} {{wildcard}} {{destination_network}} {{wildcard}} eq {{port}}
access-list {{acl_name}} extended permit icmp {{source_network}} {{wildcard}} {{destination_network}} {{wildcard}} {{icmp_type}}
access-list {{acl_name}} extended deny ip any any
!
! グローバルポリシー
access-group {{acl_name}} in interface {{interface_name}}
!
! サブジェクトポリシー
policy-map type inspect {{policy_map_name}}
 class {{class_map_name}}
  inspect {{inspection_policy}}
!
! サービスポリシー
service-policy {{policy_map_name} interface {{interface_name}}
!
! ゾーンポリシー
zone security {{zone_name}}
 description {{zone_description}}
!
zone-pair security {{zone_pair_name}} source {{source_zone}} destination {{destination_zone}}
 service-policy type inspect {{policy_map_name}}
!
! アクセスリスト適用
access-group {{acl_name}} in interface {{interface_name}}
access-group {{acl_name}} out interface {{interface_name}}
```

### IPS/IDS設定
```cisco
! IPS/IDS設定
ips policy {{ips_policy_name}
 description {{ips_policy_description}}
!
! IPS/IDSアクション
ips action {{ips_action_name}
 alert
!
! IPS/IDSルール
ips rule {{ips_rule_name}
 action {{ips_action_name}}
!
! IPS/IDS適用
ips policy {{ips_policy_name} interface {{interface_name}}
```

### アンチウイルス設定
```cisco
! アンチウイルス設定
av policy {{av_policy_name}
 description {{av_policy_description}}
!
! アンチウイルスアクション
av action {{av_action_name}
 drop
!
! アンチウイルスルール
av rule {{av_rule_name}
 action {{av_action_name}}
!
! アンチウイルス適用
av policy {{av_policy_name} interface {{interface_name}}
```

### Webフィルタリング設定
```cisco
! Webフィルタリング設定
webfilter policy {{webfilter_policy_name}
 description {{webfilter_policy_description}}
!
! Webフィルタリングアクション
webfilter action {{webfilter_action_name}
 block
!
! Webフィルタリングルール
webfilter rule {{webfilter_rule_name}
 action {{webfilter_action_name}}
!
! Webフィルタリング適用
webfilter policy {{webfilter_policy_name} interface {{interface_name}}
```

### アンチスパム設定
```cisco
! アンチスパム設定
spam policy {{spam_policy_name}
 description {{spam_policy_description}}
!
! アンチスパムアクション
spam action {{spam_action_name}
 drop
!
! アンチスパムルール
spam rule {{spam_rule_name}
 action {{spam_action_name}}
!
! アンチスパム適用
spam policy {{spam_policy_name} interface {{interface_name}}
```

### VPN設定
```cisco
! IPsec VPN設定
crypto ipsec transform-set {{transform_set_name}}
 esp-aes 256 esp-sha-hmac
 mode tunnel
!
! IKEv2設定
crypto ikev2 proposal {{ikev2_proposal_name}
 encryption aes 256
 integrity sha384
 group 14
!
crypto ikev2 policy {{ikev2_policy_name}
 proposal {{ikev2_proposal_name}
!
! トンネルインターフェース
interface Tunnel0
 description VPN Tunnel
 ip address {{tunnel_ip}} {{tunnel_mask}}
 tunnel source {{source_interface}}
 tunnel destination {{destination_ip}}
 tunnel mode ipsec ipv4
 tunnel protection ipsec profile {{ipsec_profile_name}}
!
! VPNポリシー
access-list {{vpn_acl_name}} extended permit ip {{source_network}} {{wildcard}} {{destination_network}} {{wildcard}}
!
! VPNグループ
crypto ikev2 keyring {{keyring_name}
 peer {{peer_name}}
 address {{peer_ip}}
 pre-shared-key {{pre_shared_key}
!
! VPNプロファイル
crypto ikev2 profile {{ikev2_profile_name}
 keyring {{keyring_name}
 match identity remote address {{peer_ip}
!
! VPNユーザーグループ
group-policy {{group_policy_name} internal
!
! VPNトンネルグループ
tunnel-group {{tunnel_group_name} type ipsec-l2l
tunnel-group {{tunnel_group_name} ipsec-attributes
 pre-shared-key {{pre_shared_key}
```

### 高可用性設定
```cisco
! 高可用性設定
failover
!
! フェイルオーバーモード
failover mode {{failover_mode}}
!
! フェイルオーバートラック
failover track {{track_object}}
!
! フェイルオーバーインターフェース
failover interface {{failover_interface_name}} {{failover_ip}} {{failover_mask}}
!
! フェイルオーバーリンク
failover link {{failover_link_name}}
!
! フェイルオーバー状態
failover state {{failover_state}}
!
! フェイルオーバータイマー
failover polltime {{polltime}} {{holdtime}}
!
! フェイルオーバーログ
failover logging
!
! フェイルオーバー同期
failover replication {{replication_type}}
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
! トラブルシューティング用設定
! デバッグ設定（運用時はコメントアウト）
debug crypto ipsec
debug crypto ikev2
debug firewall
!
! 保存設定
end
write memory
```

## 変数一覧
| 変数名 | 説明 | 例 |
|--------|------|-----|
| {{hostname}} | ホスト名 | FTD1 |
| {{domain_name}} | ドメイン名 | company.local |
| {{ntp_server}} | NTPサーバー | 192.168.1.1 |
| {{dns_server1}} | DNSサーバー1 | 8.8.8.8 |
| {{dns_server2}} | DNSサーバー2 | 8.8.4.4 |
| {{enable_password}} | 特権EXECパスワード | $1$secret$ |
| {{admin_password}} | 管理者パスワード | $1$admin$ |
| {{monitor_password}} | 監視用パスワード | $1$monitor$ |
| {{ssh_ip}} | SSHアクセスIP | 192.168.1.100 |
| {{ssh_subnet}} | SSHサブネットマスク | 255.255.255.0 |
| {{telnet_ip}} | TelnetアクセスIP | 192.168.1.100 |
| {{telnet_subnet}} | Telnetサブネットマスク | 255.255.255.0 |
| {{interface_name}} | インターフェース名 | GigabitEthernet0/0 |
| {{description}} | インターフェース説明 | Outside Interface |
| {{outside_security_level}} | アウトサイドセキュリティレベル | 0 |
| {{inside_security_level}} | インサイドセキュリティレベル | 100 |
| {{dmz_security_level}} | DMZセキュリティレベル | 50 |
| {{guest_security_level}} | ゲストセキュリティレベル | 10 |
| {{management_security_level}} | 管理セキュリティレベル | 150 |
| {{mpls_security_level}} | MPLSセキュリティレベル | 25 |
| {{outside_ip}} | アウトサイドIP | 203.0.113.1 |
| {{outside_mask}} | アウトサイドサブネットマスク | 255.255.255.0 |
| {{inside_ip}} | インサイドIP | 192.168.1.1 |
| {{inside_mask}} | インサイドサブネットマスク | 255.255.255.0 |
| {{dmz_ip}} | DMZ IP | 10.1.1.1 |
| {{dmz_mask}} | DMZサブネットマスク | 255.255.255.0 |
| {{guest_ip}} | ゲストIP | 192.168.100.1 |
| {{guest_mask}} | ゲストサブネットマスク | 255.255.255.0 |
| {{loopback_ip}} | ループバックIP | 10.1.1.1 |
| {{loopback_mask}} | ループバックサブネットマスク | 255.255.255.255 |
| {{management_ip}} | 管理IP | 192.168.1.100 |
| {{management_mask}} | 管理サブネットマスク | 255.255.255.0 |
| {{channel_ip}} | チャネルIP | 203.0.113.1 |
| {{channel_mask}} | チャネルサブネットマスク | 255.255.255.0 |
| {{object_name}} | オブジェクト名 | SERVER_NETWORK |
| {{network_address}} | ネットワークアドレス | 192.168.1.0 |
| {{subnet_mask}} | サブネットマスク | 255.255.255.0 |
| {{host_object_name}} | ホストオブジェクト名 | WEB_SERVER |
| {{host_ip}} | ホストIP | 192.168.1.10 |
| {{object_group_name}} | オブジェクトグループ名 | INTERNAL_NETWORKS |
| {{service_object_name}} | サービスオブジェクト名 | HTTP_SERVICE |
| {{protocol}} | プロトコル | tcp |
| {{port}} | ポート番号 | 80 |
| {{service_group_name}} | サービスグループ名 | WEB_SERVICES |
| {{service_group_description}} | サービスグループ説明 | Web Services Group |
| {{icmp_group_name}} | ICMPグループ名 | ICMP_ALLOWED |
| {{icmp_group_description}} | ICMPグループ説明 | Allowed ICMP Types |
| {{icmp_type}} | ICMPタイプ | echo-reply |
| {{nat_object_name}} | NATオブジェクト名 | PAT_OBJECT |
| {{nat_type}} | NATタイプ | dynamic |
| {{interface_name}} | インターフェース名 | outside |
| {{mapped_ip}} | マッピングIP | 203.0.113.100 |
| {{acl_object_name}} | ACLオブジェクト名 | ACL_OBJECT |
| {{acl_object_description}} | ACLオブジェクト説明 | ACL Object Description |
| {{acl_name}} | ACL名 | OUTSIDE_IN_ACL |
| {{source_network}} | ソースネットワーク | 192.168.1.0 |
| {{wildcard}} | ワイルドカードマスク | 0.0.0.255 |
| {{destination_network}} | 宛先ネットワーク | 203.0.113.0 |
| {{port}} | ポート番号 | 443 |
| {{ipv6_acl_name}} | IPv6 ACL名 | INSIDE_IN_IPV6_ACL |
| {{source_ipv6}} | ソースIPv6 | 2001:db8::1 |
| {{prefix_length}} | プレフィックス長 | 64 |
| {{destination_ipv6}} | 宛先IPv6 | 2001:db8::2 |
| {{time_range_name}} | タイムレンジ名 | BUSINESS_HOURS |
| {{time_period}} | タイム期間 | weekdays 8:00 to 18:00 |
| {{pat_object_name}} | PATオブジェクト名 | PAT_POOL |
| {{static_nat_object_name}} | 静的NATオブジェクト名 | WEB_SERVER_STATIC |
| {{real_ip}} | 実IP | 192.168.1.10 |
| {{mapped_ip}} | マッピングIP | 203.0.113.10 |
| {{inside_interface}} | インサイドインターフェース | inside |
| {{outside_interface}} | アウトサイドインターフェース | outside |
| {{static_pat_object_name}} | 静的PATオブジェクト名 | WEB_SERVER_PAT |
| {{protocol}} | プロトコル | tcp |
| {{port}} | ポート番号 | 80 |
| {{policy_nat_object_name}} | ポリシNATオブジェクト名 | POLICY_NAT_OBJECT |
| {{real_network}} | 実ネットワーク | 192.168.1.0 |
| {{mapped_network}} | マッピングネットワーク | 203.0.113.0 |
| {{twice_nat_object_name}} | 2回NATオブジェクト名 | TWICE_NAT_OBJECT |
| {{real_ip}} | 実IP | 192.168.1.10 |
| {{mapped_ip}} | マッピングIP | 203.0.113.10 |
| {{real_dest_ip}} | 実宛先IP | 10.1.1.10 |
| {{mapped_dest_ip}} | マッピング宛先IP | 10.2.2.10 |
| {{identity_nat_object_name}} | ID NATオブジェクト名 | ID_NAT_OBJECT |
| {{source_network}} | ソースネットワーク | 192.168.1.0 |
| {{destination_network}} | 宛先ネットワーク | 10.1.1.0 |
| {{zone_name}} | ゾーン名 | INSIDE_ZONE |
| {{zone_description}} | ゾーン説明 | Inside Security Zone |
| {{zone_pair_name}} | ゾーンペア名 | INSIDE_OUTSIDE_PAIR |
| {{source_zone}} | ソースゾーン | inside |
| {{destination_zone}} | 宛先ゾーン | outside |
| {{policy_map_name}} | ポリシーマップ名 | INSPECT_POLICY |
| {{class_map_name}} | クラスマップ名 | TRAFFIC_CLASS |
| {{inspection_policy}} | 検査ポリシー | default-inspection-traffic |
| {{ips_policy_name}} | IPSポリシー名 | IPS_POLICY |
| {{ips_policy_description}} | IPSポリシー説明 | Intrusion Prevention Policy |
| {{ips_action_name}} | IPSアクション名 | IPS_ACTION |
| {{ips_rule_name}} | IPSルール名 | IPS_RULE |
| {{av_policy_name}} | AVポリシー名 | AV_POLICY |
| {{av_policy_description}} | AVポリシー説明 | Antivirus Policy |
| {{av_action_name}} | AVアクション名 | AV_ACTION |
| {{av_rule_name}} | AVルール名 | AV_RULE |
| {{webfilter_policy_name}} | Webフィルタリングポリシー名 | WEBFILTER_POLICY |
| {{webfilter_policy_description}} | Webフィルタリングポリシー説明 | Web Filtering Policy |
| {{webfilter_action_name}} | Webフィルタリングアクション名 | WEBFILTER_ACTION |
| {{webfilter_rule_name}} | Webフィルタリングルール名 | WEBFILTER_RULE |
| {{spam_policy_name}} | スパムポリシー名 | SPAM_POLICY |
| {{spam_policy_description}} | スパムポリシー説明 | Spam Filtering Policy |
| {{spam_action_name}} | スパムアクション名 | SPAM_ACTION |
| {{spam_rule_name}} | スパムルール名 | SPAM_RULE |
| {{transform_set_name}} | 変換セット名 | TRANSFORM_SET |
| {{ikev2_proposal_name}} | IKEv2プロポーザル名 | IKEV2_PROPOSAL |
| {{ikev2_policy_name}} | IKEv2ポリシー名 | IKEV2_POLICY |
| {{tunnel_ip}} | トンネルIP | 10.1.1.1 |
| {{tunnel_mask}} | トンネルサブネットマスク | 255.255.255.0 |
| {{source_interface}} | ソースインターフェース | outside |
| {{destination_ip}} | 宛先IP | 203.0.113.2 |
| {{ipsec_profile_name}} | IPsecプロファイル名 | IPSEC_PROFILE |
| {{vpn_acl_name}} | VPN ACL名 | VPN_ACL |
| {{source_network}} | ソースネットワーク | 192.168.1.0 |
| {{wildcard}} | ワイルドカードマスク | 0.0.0.255 |
| {{destination_network}} | 宛先ネットワーク | 10.1.1.0 |
| {{keyring_name}} | キーリング名 | KEYRING |
| {{peer_name}} | ピア名 | PEER1 |
| {{peer_ip}} | ピアIP | 203.0.113.2 |
| {{pre_shared_key}} | 事前共有キー | sharedkey123 |
| {{ikev2_profile_name}} | IKEv2プロファイル名 | IKEV2_PROFILE |
| {{group_policy_name}} | グルーポリシー名 | GROUP_POLICY |
| {{tunnel_group_name}} | トンネルグループ名 | TUNNEL_GROUP |
| {{failover_mode}} | フェイルオーバーモード | active |
| {{track_object}} | トラッキングオブジェクト | 1 |
| {{failover_interface_name}} | フェイルオーバーインターフェース名 | FAILOVER |
| {{failover_ip}} | フェイルオーバーIP | 192.168.1.200 |
| {{failover_mask}} | フェイルオーバーサブネットマスク | 255.255.255.0 |
| {{failover_link_name}} | フェイルオーバーリンク名 | FAILOVER_LINK |
| {{failover_state}} | フェイルオーバーステート | active |
| {{polltime}} | ポルタイム | 5 |
| {{holdtime}} | ホールドタイム | 15 |
| {{replication_type}} | レプリケーションタイプ | ssl |
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

