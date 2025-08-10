


# Cisco Wireless LAN Controller (WLC) Configuration Template

## デバイスタイプ
- **タイプ**: 無線LANコントローラ
- **OS**: Cisco IOS XE for WLC
- **モデル**: Cisco 3504/5520/8540シリーズ
- **用途**: 無線LANネットワーク管理

## 基本設定
```cisco
! 基本設定
config t
!
! コントローラ名設定
config controller name {{controller_name}}
!
! 管理IP設定
config interface management
 ip address {{mgmt_ip}} {{mgmt_mask}}
 gateway {{gateway_ip}}
!
! ドメイン名設定
config network domain {{domain_name}}
!
! NTP設定
config network ntp
 server {{ntp_server}}
!
! DNS設定
config network dns
 server {{dns_server1}}
 server {{dns_server2}}
!
! 特権EXECモードパスワード
config security password enable {{enable_password}}
!
! VTYコンソール設定
config security console
 timeout {{console_timeout}}
!
! ローカルユーザー設定
config security user admin
 username admin
 password {{admin_password}}
 role network-admin
!
config security user monitor
 username monitor
 password {{monitor_password}}
 role network-operator
!
! SSH設定
config security ssh
 enable
 version 2
!
! Telnet設定（非推奨）
config security telnet
 enable
!
! SNMP設定
config security snmp
 community {{community_string}} ro
 community {{community_string_rw}} rw
 host {{snmp_server}} version 2c {{community_string}}
!
! Syslog設定
config logging
 host {{syslog_server}}
 level {{severity_level}}
!
! RADIUS設定
config security radius
 server {{radius_server}} key {{radius_key}}
!
! TACACS+設定
config security tacacs
 server {{tacacs_server}} key {{tacacs_key}}
```

### ネットワーク設定
```cisco
! インターフェース設定
config interface
!
! 管理インターフェース
interface management
 description {{description}}
 ip address {{mgmt_ip}} {{mgmt_mask}}
 gateway {{gateway_ip}}
!
! ポートチャネル設定
interface port-channel {{channel_id}}
 description {{channel_description}}
!
! 物理インターフェース設定
interface GigabitEthernet {{interface_id}}
 description {{description}}
 no shutdown
!
! サブインターフェース設定
interface GigabitEthernet {{interface_id}}.{{sub_id}}
 encapsulation dot1Q {{vlan_id}}
 ip address {{sub_ip}} {{sub_mask}}
!
! VLAN設定
config vlan
 vlan {{vlan_id}}
 name {{vlan_name}}
!
! DHCPリレー設定
config dhcp relay
 interface {{interface_name}}
 server {{dhcp_server}}
!
! DHCPスコープ設定
config dhcp scope
 name {{scope_name}}
 network {{network_address}} {{subnet_mask}}
 gateway {{gateway_ip}}
 dns {{dns_server}}
 lease {{lease_days}}
!
! 静的ルート設定
config route
 static {{destination_network}} {{subnet_mask}} {{next_hop}}
!
! デフォルトルート設定
config route
 default {{default_gateway}}
```

### 無線ネットワーク設定
```cisco
! 無線ネットワークプロファイル設定
config wlan profile
 name {{wlan_profile_name}}
!
! SSID設定
config wlan ssid
 name {{ssid_name}}
!
! セキュリティプロファイル設定
config wlan security
 profile {{security_profile_name}}
 type {{security_type}}
!
! WPA2-Enterprise設定
config wlan security wpa2-enterprise
 profile {{wpa2_profile_name}}
 authentication {{auth_type}}
 server {{radius_server}}
!
! WPA2-Personal設定
config wlan security wpa2-personal
 profile {{wpa2_personal_profile_name}}
 key {{psk_key}}
!
! 認証プロファイル設定
config wlan authentication
 profile {{auth_profile_name}}
 method {{auth_method}}
!
! QoSプロファイル設定
config wlan qos
 profile {{qos_profile_name}}
!
! ローミングプロファイル設定
config wlan roaming
 profile {{roaming_profile_name}}
!
! グループプロファイル設定
config wlan group
 profile {{group_profile_name}}
!
! WLAN ID設定
config wlan id {{wlan_id}}
 profile {{wlan_profile_name}}
 ssid {{ssid_name}}
 interface {{interface_name}}
!
! WLAN割り当て設定
config wlan assignment
 wlan {{wlan_id}}
 interface {{interface_name}}
 vlan {{vlan_id}}
!
! WLANポリシー設定
config wlan policy
 wlan {{wlan_id}}
 bandwidth {{bandwidth_limit}}
 client-limit {{client_limit}}
!
! WLAN ACL設定
config wlan acl
 wlan {{wlan_id}}
 acl {{acl_name}}
```

### AP設定
```cisco
! APプロファイル設定
config ap profile
 name {{ap_profile_name}}
!
! APグループ設定
config ap group
 name {{ap_group_name}}
 profile {{ap_profile_name}}
!
! AP設定
config ap
 name {{ap_name}}
 mac {{ap_mac}}
 group {{ap_group_name}}
!
! APトラッキング設定
config ap tracking
 ap {{ap_name}}
 threshold {{threshold}}
!
! APカバレッジ設定
config ap coverage
 ap {{ap_name}}
 power {{power_level}}
 channel {{channel}}
!
! APチャネル設定
config ap channel
 ap {{ap_name}}
 band {{band}}
 channel {{channel}}
 width {{channel_width}}
!
! AP電力設定
config ap power
 ap {{ap_name}}
 power {{power_level}}
!
! APアップグレード設定
config ap upgrade
 ap {{ap_name}}
 image {{image_name}}
!
! APバックアップ設定
config ap backup
 ap {{ap_name}}
 schedule {{backup_schedule}}
!
! APモニタリング設定
config ap monitoring
 ap {{ap_name}}
 interval {{monitoring_interval}}
 threshold {{monitoring_threshold}}
```

### RF設定
```cisco
! RFプロファイル設定
config rf profile
 name {{rf_profile_name}}
!
! RFグループ設定
config rf group
 name {{rf_group_name}}
 profile {{rf_profile_name}}
!
! RFチャネル設定
config rf channel
 band {{band}}
 channels {{channels}}
!
! RF電力設定
config rf power
 band {{band}}
 power {{power_level}}
!
! RFノイズ設定
config rf noise
 band {{band}}
 threshold {{noise_threshold}}
!
! RF干渉設定
config rf interference
 band {{band}}
 threshold {{interference_threshold}}
!
! RFカバレッジ設定
config rf coverage
 band {{band}}
 threshold {{coverage_threshold}}
!
! RF容量設定
config rf capacity
 band {{band}}
 threshold {{capacity_threshold}}
!
! RFトラッキング設定
config rf tracking
 band {{band}}
 threshold {{tracking_threshold}}
!
! RFオプティマイゼーション設定
config rf optimization
 band {{band}}
 enable
!
! RFローミング設定
config rf roaming
 band {{band}}
 threshold {{roaming_threshold}}
```

### 高可用性設定
```cisco
! 高可用性設定
config high-availability
!
! クラスタ設定
config cluster
 name {{cluster_name}}
!
! クラスタメンバー設定
config cluster member
 ip {{member_ip}}
 priority {{priority}}
!
! クラスタ同期設定
config cluster sync
 interval {{sync_interval}}
!
! クラスタフェイルオーバー設定
config cluster failover
 mode {{failover_mode}}
!
! クラスタロードバランシング設定
config cluster load-balance
 method {{load_balance_method}}
!
! クラスタトラッキング設定
config cluster tracking
 object {{track_object}}
!
! クラスタ状態設定
config cluster status
 mode {{cluster_mode}}
!
! クラスタアップグレード設定
config cluster upgrade
 method {{upgrade_method}}
```

### 監視設定
```cisco
! 監視設定
config monitoring
!
! AP監視設定
config monitoring ap
 interval {{ap_interval}}
 threshold {{ap_threshold}}
!
! クライアント監視設定
config monitoring client
 interval {{client_interval}}
 threshold {{client_threshold}}
!
! RF監視設定
config monitoring rf
 interval {{rf_interval}}
 threshold {{rf_threshold}}
!
! ネットワーク監視設定
config monitoring network
 interval {{network_interval}}
 threshold {{network_threshold}}
!
! パフォーマンス監視設定
config monitoring performance
 interval {{performance_interval}}
 threshold {{performance_threshold}}
!
! トラップ設定
config monitoring trap
 host {{trap_host}}
 community {{trap_community}}
!
! レポート設定
config monitoring report
 type {{report_type}}
 schedule {{report_schedule}}
!
! アラート設定
config monitoring alert
 rule {{alert_rule}}
 action {{alert_action}}
```

### トラブルシューティング設定
```cisco
! トラブルシューティング設定
config troubleshooting
!
! デバッグ設定
config debug
 category {{debug_category}}
 level {{debug_level}}
!
! ログ設定
config logging
 level {{log_level}}
 size {{log_size}}
!
! キャプチャ設定
config capture
 interface {{capture_interface}}
 filter {{capture_filter}}
!
! トレース設定
config trace
 protocol {{trace_protocol}}
!
! 分析設定
config analysis
 type {{analysis_type}}
 interval {{analysis_interval}}
!
! 診断設定
config diagnostic
 test {{diagnostic_test}}
 schedule {{diagnostic_schedule}}
!
! レポート設定
config report
 type {{report_type}}
 format {{report_format}}
 schedule {{report_schedule}}
```

### その他の設定
```cisco
! その他の設定
config misc
!
! ライセンス設定
config license
 type {{license_type}}
 count {{license_count}}
!
! 設定バックアップ設定
config backup
 schedule {{backup_schedule}}
 location {{backup_location}}
!
! 設定リストア設定
config restore
 source {{restore_source}}
!
! 設定エクスポート設定
config export
 format {{export_format}}
 location {{export_location}}
!
! 設定インポート設定
config import
 format {{import_format}}
 location {{import_location}}
!
! 設定バージョン設定
config version
 max {{max_versions}}
!
! 設定コミット設定
config commit
 auto-save {{auto_save}}
!
! 設定ロールバック設定
config rollback
 version {{rollback_version}}
!
! 設定同期設定
config sync
 peer {{sync_peer}}
!
! 設定バックアップ設定
config backup
 schedule {{backup_schedule}}
 location {{backup_location}}
!
! 設定リストア設定
config restore
 source {{restore_source}}
!
! 設定エクスポート設定
config export
 format {{export_format}}
 location {{export_location}}
!
! 設定インポート設定
config import
 format {{import_format}}
 location {{import_location}}
!
! 設定バージョン設定
config version
 max {{max_versions}}
!
! 設定コミット設定
config commit
 auto-save {{auto_save}}
!
! 設定ロールバック設定
config rollback
 version {{rollback_version}}
!
! 設定同期設定
config sync
 peer {{sync_peer}}
!
! 保存設定
end
save config
```

## 変数一覧
| 変数名 | 説明 | 例 |
|--------|------|-----|
| {{controller_name}} | コントローラ名 | WLC-01 |
| {{mgmt_ip}} | 管理IP | 192.168.1.100 |
| {{mgmt_mask}} | 管理サブネットマスク | 255.255.255.0 |
| {{gateway_ip}} | ゲートウェイIP | 192.168.1.1 |
| {{domain_name}} | ドメイン名 | company.local |
| {{ntp_server}} | NTPサーバー | 192.168.1.1 |
| {{dns_server1}} | DNSサーバー1 | 8.8.8.8 |
| {{dns_server2}} | DNSサーバー2 | 8.8.4.4 |
| {{enable_password}} | 特権EXECパスワード | $1$secret$ |
| {{admin_password}} | 管理者パスワード | $1$admin$ |
| {{monitor_password}} | 監視用パスワード | $1$monitor$ |
| {{console_timeout}} | コンソールタイムアウト | 30 |
| {{community_string}} | SNMPコミュニティ文字列 | public_ro |
| {{community_string_rw}} | SNMP RWコミュニティ文字列 | private_rw |
| {{snmp_server}} | SNMPサーバー | 192.168.1.200 |
| {{syslog_server}} | Syslogサーバー | 192.168.1.300 |
| {{severity_level}} | シverityレベル | 6 |
| {{radius_server}} | RADIUSサーバー | 192.168.1.400 |
| {{radius_key}} | RADIUSキー | radiuskey123 |
| {{tacacs_server}} | TACACS+サーバー | 192.168.1.500 |
| {{tacacs_key}} | TACACS+キー | tacacskey123 |
| {{description}} | インターフェース説明 | Management Interface |
| {{channel_id}} | チャネルID | 1 |
| {{channel_description}} | チャネル説明 | Uplink Channel |
| {{interface_id}} | インターフェースID | 1 |
| {{sub_id}} | サブインターフェースID | 100 |
| {{vlan_id}} | VLAN ID | 100 |
| {{sub_ip}} | サブインターフェースIP | 192.168.100.1 |
| {{sub_mask}} | サブインターフェースサブネットマスク | 255.255.255.0 |
| {{vlan_name}} | VLAN名 | Management |
| {{interface_name}} | インターフェース名 | management |
| {{dhcp_server}} | DHCPサーバー | 192.168.1.1 |
| {{scope_name}} | スコープ名 | SCOPE_1 |
| {{network_address}} | ネットワークアドレス | 192.168.1.0 |
| {{subnet_mask}} | サブネットマスク | 255.255.255.0 |
| {{lease_days}} | リース日数 | 7 |
| {{destination_network}} | 宛先ネットワーク | 10.1.1.0 |
| {{next_hop}} | ネクストホップ | 10.1.1.1 |
| {{default_gateway}} | デフォルトゲートウェイ | 192.168.1.1 |
| {{wlan_profile_name}} | WLANプロファイル名 | CORP_WIFI |
| {{ssid_name}} | SSID名 | CompanyWiFi |
| {{security_profile_name}} | セキュリティプロファイル名 | WPA2_SEC |
| {{security_type}} | セキュリティタイプ | wpa2 |
| {{wpa2_profile_name}} | WPA2プロファイル名 | WPA2_ENT |
| {{auth_type}} | 認証タイプ | radius |
| {{wpa2_personal_profile_name}} | WPA2パーソナルプロファイル名 | WPA2_PSK |
| {{psk_key}} | PSKキー | securepassword123 |
| {{auth_profile_name}} | 認証プロファイル名 | RADIUS_AUTH |
| {{auth_method}} | 認証方法 | peap |
| {{qos_profile_name}} | QoSプロファイル名 | QOS_PROFILE |
| {{roaming_profile_name}} | ローミングプロファイル名 | ROAMING_PROFILE |
| {{group_profile_name}} | グループプロファイル名 | GROUP_PROFILE |
| {{wlan_id}} | WLAN ID | 1 |
| {{bandwidth_limit}} | 帯域幅制限 | 10000 |
| {{client_limit}} | クライアント制限 | 50 |
| {{acl_name}} | ACL名 | WLAN_ACL |
| {{ap_profile_name}} | APプロファイル名 | AP_PROFILE |
| {{ap_group_name}} | APグループ名 | AP_GROUP |
| {{ap_name}} | AP名 | AP-01 |
| {{ap_mac}} | AP MACアドレス | 00:1A:2B:3C:4D:5E |
| {{threshold}} | しきい値 | 3 |
| {{power_level}} | 電力レベル | 5 |
| {{channel}} | チャネル | 36 |
| {{channel_width}} | チャネル幅 | 20 |
| {{image_name}} | イメージ名 | 8.5.120.0 |
| {{backup_schedule}} | バックアップスケジュール | 0 2 * * * |
| {{monitoring_interval}} | 監視間隔 | 300 |
| {{rf_profile_name}} | RFプロファイル名 | RF_PROFILE |
| {{rf_group_name}} | RFグループ名 | RF_GROUP |
| {{band}} | バンド | 2.4ghz |
| {{channels}} | チャネル | 1,6,11 |
| {{noise_threshold}} | ノイズしきい値 | -90 |
| {{interference_threshold}} | 干渉しきい値 | -85 |
| {{coverage_threshold}} | カバレッジしきい値 | -85 |
| {{capacity_threshold}} | 容量しきい値 | 50 |
| {{tracking_threshold}} | トラッキングしきい値 | -80 |
| {{cluster_name}} | クラスタ名 | WLC_CLUSTER |
| {{member_ip}} | メンバIP | 192.168.1.101 |
| {{priority}} | 優先度 | 100 |
| {{sync_interval}} | 同期間隔 | 60 |
| {{failover_mode}} | フェイルオーバーモード | sso |
| {{load_balance_method}} | ロードバランシング方法 | round-robin |
| {{track_object}} | トラッキングオブジェクト | 1 |
| {{cluster_mode}} | クラスタモード | high-availability |
| {{upgrade_method}} | アップグレード方法 | rolling |
| {{ap_interval}} | AP監視間隔 | 300 |
| {{ap_threshold}} | AP監視しきい値 | 3 |
| {{client_interval}} | クライアント監視間隔 | 300 |
| {{client_threshold}} | クライアント監視しきい値 | 5 |
| {{rf_interval}} | RF監視間隔 | 300 |
| {{rf_threshold}} | RF監視しきい値 | -85 |
| {{network_interval}} | ネットワーク監視間隔 | 300 |
| {{network_threshold}} | ネットワーク監視しきい値 | 3 |
| {{performance_interval}} | パフォーマンス監視間隔 | 300 |
| {{performance_threshold}} | パフォーマンス監視しきい値 | 80 |
| {{trap_host}} | トラップホスト | 192.168.1.200 |
| {{trap_community}} | トラップコミュニティ | public |
| {{report_type}} | レポートタイプ | summary |
| {{report_schedule}} | レポートスケジュール | 0 6 * * * |
| {{alert_rule}} | アラートルール | ap-down |
| {{alert_action}} | アラートアクション | email |
| {{debug_category}} | デバッグカテゴリ | all |
| {{debug_level}} | デバッグレベル | debug |
| {{log_level}} | ログレベル | info |
| {{log_size}} | ログサイズ | 1048576 |
| {{capture_interface}} | キャプチャインターフェース | any |
| {{capture_filter}} | キャプチャフィルター | tcp port 80 |
| {{trace_protocol}} | トレースプロトコル | all |
| {{analysis_type}} | 分析タイプ | rf |
| {{analysis_interval}} | 分析間隔 | 3600 |
| {{diagnostic_test}} | 診断テスト | all |
| {{diagnostic_schedule}} | 診断スケジュール | 0 3 * * * |
| {{license_type}} | ライセンスタイプ | permanent |
| {{license_count}} | ライセンスク数 | 100 |
| {{backup_schedule}} | バックアップスケジュール | 0 2 * * * |
| {{backup_location}} | バックアップ場所 | tftp://192.168.1.200/ |
| {{restore_source}} | リストアソース | tftp://192.168.1.200/wlc_backup.cfg |
| {{export_format}} | エクスポート形式 | cli |
| {{export_location}} | エクスポート場所 | tftp://192.168.1.200/ |
| {{import_format}} | インポート形式 | cli |
| {{import_location}} | インポート場所 | tftp://192.168.1.200/wlc_config.cfg |
| {{max_versions}} | 最大バージョン数 | 10 |
| {{auto_save}} | オートセーブ | enabled |
| {{rollback_version}} | ロールバックバージョン | 5 |
| {{sync_peer}} | 同期ピア | 192.168.1.101 |


