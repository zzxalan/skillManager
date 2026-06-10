# Smart Project Map

## 项目模型

smart 是电子班牌/空间管理项目体系，采用 `smart-core` 基座 + 多个 `smart-*` 插件 + 终端/应用系统的组织方式。

- `smart-core`：基座系统，负责公共底座能力、插件加载、运行容器和公共服务。
- `smart-*` 插件：围绕具体业务域拆分的插件工程，多数采用 `smart-<domain>-mixed` 命名，通常同时包含后端和前端。
- 终端/应用系统：不作为 smart-core 微前端插件运行，例如 Android 电子班牌终端、微信小程序。

## 命名关系

| 概念 | 示例 | 说明 |
| --- | --- | --- |
| plugin id | `attendance` | 插件运行时短标识，常用于插件注册、路由、菜单或配置。 |
| 中文名 | `考勤` | 面向业务沟通的插件名称。 |
| 英文项目名/仓库目录 | `smart-attendance-mixed` | 工程目录和仓库主名称。 |
| Git 仓库 | `ssh://root@192.168.50.2:3323/Outbook/smart-attendance-mixed.git` | 代码 checkout 来源。 |
| 本地相对路径 | `./smart-attendance-mixed` | 工作区根目录下的期望目录。 |

## 基座

| plugin id | 中文名 | 英文项目名 | Git 仓库 | 相对路径 | 说明 |
| --- | --- | --- | --- | --- | --- |
| `smart` | 基座 | `smart-core-mixed` | `ssh://root@192.168.50.2:3323/Outbook/smart-core-mixed.git` | `./smart-core-mixed` | Smart 系统运行容器，负责加载和运行各功能插件，并提供公共底层服务。 |

## 核心微前端插件

| plugin id | 中文名 | 英文项目名 | Git 仓库 | 相对路径 | 说明 |
| --- | --- | --- | --- | --- | --- |
| `activity` | 活动计划 | `smart-activity-mixed` | `ssh://root@192.168.50.2:3323/Outbook/smart-activity-mixed.git` | `./smart-activity-mixed` | 提供活动计划制定、日程管理、任务分发等功能。 |
| `attendance` | 考勤 | `smart-attendance-mixed` | `ssh://root@192.168.50.2:3323/Outbook/smart-attendance-mixed.git` | `./smart-attendance-mixed` | 提供学校/空间的人员考勤打卡、规则配置及考勤数据统计功能。 |
| `basic` | 基础包 | `smart-basic-mixed` | `ssh://root@192.168.50.2:3323/Outbook/smart-basic-mixed.git` | `./smart-basic-mixed` | 包含系统运行所需的核心基础数据、组织架构、角色权限和通用公共配置。 |
| `classPanel` | 班牌 | `smart-classPanel-mixed` | `ssh://root@192.168.50.2:3323/Outbook/smart-classPanel-mixed.git` | `./smart-classPanel-mixed` | 支持班级电子班牌设备终端管理、界面展示和校园发布。 |
| `course` | 课程 | `smart-course-mixed` | `ssh://root@192.168.50.2:3323/Outbook/smart-course-mixed.git` | `./smart-course-mixed` | 提供排课、排期、课表展示及选课等课程教务管理功能。 |
| `door` | 门禁管理 | `smart-door-mixed` | `ssh://root@192.168.50.2:3323/Outbook/smart-door-mixed.git` | `./smart-door-mixed` | 实现校园或空间门禁控制、通行授权、出入记录等安全管理。 |
| `exam` | 考试插件 | `smart-exam-mixed` | `ssh://root@192.168.50.2:3323/Outbook/smart-exam-mixed.git` | `./smart-exam-mixed` | 支持线上考试、线下排考、成绩导入等考试管理流程。 |
| `face` | 人脸识别 | `smart-face-mixed` | `ssh://root@192.168.50.2:3323/Outbook/smart-face-mixed.git` | `./smart-face-mixed` | 提供人脸特征底库管理、设备对比核验及人脸特征识别功能。 |
| `iot` | 物联设备 | `smart-iot-mixed` | `ssh://root@192.168.50.2:3323/Outbook/smart-iot-mixed.git` | `./smart-iot-mixed` | 提供 IoT 设备接入控制、协议转换和运行状态监测。 |
| `iotDashboard` | 物联大屏 | `smart-iotDashboard-mixed` | `ssh://root@192.168.50.2:3323/Outbook/smart-iotDashboard-mixed.git` | `./smart-iotDashboard-mixed` | 面向大屏展示物联数据大盘，支持可视化拓扑和图表分析。 |
| `notice` | 校园公告 | `smart-notice-mixed` | `ssh://root@192.168.50.2:3323/Outbook/smart-notice-mixed.git` | `./smart-notice-mixed` | 提供校园通知、紧急公告、新闻动态的发布与审核流程。 |
| `pubInfo` | 信发 | `smart-pubInfo-mixed` | `ssh://root@192.168.50.2:3323/Outbook/smart-pubInfo-mixed.git` | `./smart-pubInfo-mixed` | 用于多媒体信息发布系统终端的内容发布、节目制作和排期管理。 |
| `room-change` | 教室调换 | `smart-room-change-mixed` | `ssh://root@192.168.50.2:3323/Outbook/smart-room-change-mixed.git` | `./smart-room-change-mixed` | 提供教室临时占用、调课调室申请与审批流程。 |
| `spider` | 对接插件 | `smart-spider-mixed` | `ssh://root@192.168.50.2:3323/zhangzhixiong/smart-spider-mixed.git` | `./smart-spider-mixed` | 基于基座架构的数据采集对接插件，负责具体数据抓取和格式清洗。 |
| `tools` | 运维工具 | `smart-tools` | `ssh://root@192.168.50.2:3323/Outbook/smart-tools.git` | `./smart-tools` | 提供系统故障排查、脚本执行、健康检查等运维管理工具。 |
| `touch` | 碰一碰 | `smart-touch-mixed` | `ssh://root@192.168.50.2:3323/Outbook/smart-touch-mixed.git` | `./smart-touch-mixed` | 管理 NFC 碰一碰设备、快速关联与交互响应配置。 |
| `triAudit` | 三审三校 | `smart-triAudit-mixed` | `ssh://root@192.168.50.2:3323/Outbook/smart-triAudit-mixed.git` | `./smart-triAudit-mixed` | 实现信息发布及媒体内容发布的多级审核机制，确保内容安全。 |
| `uniTask` | 统一任务 | `smart-uniTask-mixed` | `ssh://root@192.168.50.2:3323/Outbook/smart-uniTask-mixed.git` | `./smart-uniTask-mixed` | 负责系统内分布式定时任务和后台作业的统一调度、执行与监控。 |

## 终端与应用系统

| 项目 ID | 中文名 | 英文项目名 | Git 仓库 | 相对路径 | 说明 |
| --- | --- | --- | --- | --- | --- |
| `-` | 电子班牌 Android 终端 | `ClassScreen` | `ssh://root@192.168.50.2:3323/Outbook/ClassScreen.git` | `./ClassScreen` | 电子班牌端侧 Android App，提供人脸识别、考勤核验、信发内容展示等终端交互与硬件适配。 |
| `-` | 微信小程序 v4 | `outbook-miniprogram-v4` | `ssh://root@192.168.50.2:3323/Outbook/outbook-miniprogram-v4.git` | `./outbook-miniprogram-v4` | 移动端微信小程序，提供家长端、教师端移动办公入口及校园服务交互。 |

## 快速归属判断

| 用户说法 | 优先查看 |
| --- | --- |
| 基座、宿主、公共服务、插件加载、统一登录、菜单、公共权限 | `smart-core-mixed` |
| 活动、活动计划、日程任务 | `smart-activity-mixed` |
| 考勤、打卡、考勤规则、考勤统计 | `smart-attendance-mixed` |
| 基础数据、组织架构、角色权限、公共配置 | `smart-basic-mixed` |
| 班牌、电子班牌、班级屏、班牌设备 | `smart-classPanel-mixed`；端侧 Android 问题也可能涉及 `ClassScreen` |
| 课程、排课、课表、选课 | `smart-course-mixed` |
| 门禁、通行、授权、出入记录 | `smart-door-mixed` |
| 考试、排考、成绩 | `smart-exam-mixed` |
| 人脸、人脸底库、人脸核验 | `smart-face-mixed`；端侧识别问题也可能涉及 `ClassScreen` |
| 物联、IoT、设备接入、协议、设备状态 | `smart-iot-mixed` |
| 物联大屏、物联可视化、拓扑、图表大屏 | `smart-iotDashboard-mixed` |
| 公告、通知、新闻、紧急公告 | `smart-notice-mixed` |
| 信发、信息发布、节目、排期、多媒体发布 | `smart-pubInfo-mixed`；内容审核可能涉及 `smart-triAudit-mixed` |
| 调课、调室、教室临时占用 | `smart-room-change-mixed` |
| 对接、采集、抓取、数据清洗 | `smart-spider-mixed` |
| 运维、健康检查、脚本、故障排查 | `smart-tools` |
| 碰一碰、NFC、碰一碰设备 | `smart-touch-mixed` |
| 三审三校、内容审核、多级审核 | `smart-triAudit-mixed` |
| 定时任务、后台作业、调度监控 | `smart-uniTask-mixed` |
| Android 终端、端侧 App、硬件适配 | `ClassScreen` |
| 家长端、教师端、小程序、移动端微信入口 | `outbook-miniprogram-v4` |

## 维护规则

- 新增、删除或重命名插件时，同时更新 `SKILL.md` 的触发描述和本文件对应清单。
- 如果只变更仓库 URL、目录名或中文说明，只更新本文件。
- 发现项目地图与实际代码或平台配置不一致时，不要静默修正任务结论；先说明冲突，再按用户确认或最新权威清单更新本文件。
