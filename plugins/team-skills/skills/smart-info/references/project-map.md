# Smart Project Map

## 目录

- [项目模型](#项目模型)
- [插件术语](#插件术语)
- [基座](#基座)
- [核心微前端插件](#核心微前端插件)
- [工具插件](#工具插件)
- [终端与应用系统](#终端与应用系统)
- [快速归属判断](#快速归属判断)
- [维护规则](#维护规则)

## 项目模型

smart 是电子班牌/空间管理项目体系，采用 `smart-core` 基座 + 多个 `smart-*` 插件 + 工具插件 + 终端/应用系统的组织方式。

- `smart-core`：基座系统，负责公共底座能力、插件加载、运行容器和公共服务。
- `smart-*` 插件：围绕具体业务域拆分的插件工程，多数采用 `smart-<domain>-mixed` 命名，通常同时包含后端和前端。
- 工具插件：围绕运维、健康检查、脚本执行等辅助能力组织的插件，例如 `smart-tools`。
- 终端/应用系统：不作为 smart-core 微前端插件运行，例如 Android 电子班牌终端、微信小程序。

## 插件术语

| 术语 | 定义 | 权威来源 | 示例 |
| --- | --- | --- | --- |
| 插件工程名 | 工作区目录和 Git 仓库主名称 | 实际仓库/用户确认清单 | `smart-attendance-mixed` |
| 插件标识 | `frontend/public/config.json` 顶层 `app`，用于机器识别，区分大小写 | 当前 `config.json` | `attendance` |
| 插件正式名称 | `frontend/public/config.json` 顶层 `appName` | 当前 `config.json` | 考勤应用 |
| 插件别名 | 团队或业务交流中的自然语言称呼，只用于识别 | 用户确认/稳定的工作区用法 | 考勤、课堂考勤 |
| Git 仓库 | 代码 checkout 来源 | 实际 Git remote/用户确认清单 | `ssh://root@192.168.50.2:3323/Outbook/smart-attendance-mixed.git` |
| 本地相对路径 | smart 工作区根目录下的期望目录 | 实际工作区/用户确认清单 | `./smart-attendance-mixed` |

用户使用工程名、插件标识、正式名称或已登记别名中的任一称呼时，都应解析到同一个项目。别名不覆盖 `appName`，也不改变 `app`、接口参数、路由、包名或构建产物。

## 基座

| 插件标识 `app` | 正式名称 `appName` | 已登记别名 | 插件工程名 | Git 仓库 | 相对路径 | 说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `core` | 基座 | 宿主、smart-core | `smart-core-mixed` | `ssh://root@192.168.50.2:3323/Outbook/smart-core-mixed.git` | `./smart-core-mixed` | Smart 系统运行容器，负责加载和运行各功能插件，并提供公共底层服务；不按普通业务插件处理。 |

## 核心微前端插件

| 插件标识 `app` | 正式名称 `appName` | 已登记别名 | 插件工程名 | Git 仓库 | 相对路径 | 说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `activity` | 活动计划应用 | 活动、活动计划 | `smart-activity-mixed` | `ssh://root@192.168.50.2:3323/Outbook/smart-activity-mixed.git` | `./smart-activity-mixed` | 提供活动计划制定、日程管理、任务分发等功能。 |
| `attendance` | 考勤应用 | 考勤、课堂考勤 | `smart-attendance-mixed` | `ssh://root@192.168.50.2:3323/Outbook/smart-attendance-mixed.git` | `./smart-attendance-mixed` | 提供人员考勤打卡、规则配置及考勤数据统计功能。 |
| `basic` | 基础应用 | 基础插件、基础包 | `smart-basic-mixed` | `ssh://root@192.168.50.2:3323/Outbook/smart-basic-mixed.git` | `./smart-basic-mixed` | 包含核心基础数据、组织架构、角色权限和通用公共配置。 |
| `book` | 教室预约 | — | `smart-book-mixed` | `ssh://root@192.168.50.2:3323/Outbook/smart-book-mixed.git` | `./smart-book-mixed` | 提供教室资源预约、使用申请、审批与记录管理。 |
| `classPanel` | 班级应用 | 班牌、电子班牌 | `smart-classPanel-mixed` | `ssh://root@192.168.50.2:3323/Outbook/smart-classPanel-mixed.git` | `./smart-classPanel-mixed` | 支持班级电子班牌设备管理、界面展示和校园发布。 |
| `course` | 课表应用 | 课表、课程 | `smart-course-mixed` | `ssh://root@192.168.50.2:3323/Outbook/smart-course-mixed.git` | `./smart-course-mixed` | 提供排课、排期、课表展示及选课等课程教务管理功能。 |
| `course-supervision` | 督导巡课 | — | `smart-course-supervision-mixed` | `ssh://root@192.168.50.2:3323/Outbook/smart-course-supervision-mixed.git` | `./smart-course-supervision-mixed` | 提供巡课任务、课堂督导、巡课记录和统计分析能力。 |
| `deviceControl` | 设备控制 | — | `smart-deviceControl-mixed` | `ssh://root@192.168.50.2:3323/Outbook/smart-deviceControl-mixed.git` | `./smart-deviceControl-mixed` | 基于物联设备能力提供统一设备控制、场景联动和控制入口。 |
| `door` | 门禁管理 | 门禁 | `smart-door-mixed` | `ssh://root@192.168.50.2:3323/Outbook/smart-door-mixed.git` | `./smart-door-mixed` | 实现门禁控制、通行授权、出入记录等安全管理。 |
| `exam` | 考试应用 | 考试、考试插件 | `smart-exam-mixed` | `ssh://root@192.168.50.2:3323/Outbook/smart-exam-mixed.git` | `./smart-exam-mixed` | 支持线上考试、线下排考、成绩导入等考试管理流程。 |
| `face` | 人脸应用 | 人脸、人脸识别 | `smart-face-mixed` | `ssh://root@192.168.50.2:3323/Outbook/smart-face-mixed.git` | `./smart-face-mixed` | 提供人脸特征底库管理、设备对比核验及人脸特征识别功能。 |
| `feedback` | 意见反馈 | 反馈 | `smart-feedback-mixed` | `ssh://root@192.168.50.2:3323/Outbook/smart-feedback-mixed.git` | `./smart-feedback-mixed` | 提供意见、建议和问题反馈相关能力。 |
| `floorBuildingIndex` | 楼栋索引 | — | `smart-floorBuildingIndex-mixed` | `ssh://root@192.168.50.2:3323/Outbook/smart-floorBuildingIndex-mixed.git` | `./smart-floorBuildingIndex-mixed` | 提供楼栋、楼层及空间索引展示和导航能力。 |
| `headcount` | 人头监测 | 点人头插件 | `smart-headcount-mixed` | `ssh://root@192.168.50.2:3323/Outbook/smart-headcount-mixed.git` | `./smart-headcount-mixed` | 提供空间人流、人头识别或人数监测相关管理能力。 |
| `iot` | 物联应用 | 物联、物联设备 | `smart-iot-mixed` | `ssh://root@192.168.50.2:3323/Outbook/smart-iot-mixed.git` | `./smart-iot-mixed` | 提供 IoT 设备接入控制、协议转换和运行状态监测。 |
| `iotDashboard` | 物联大屏 | — | `smart-iotDashboard-mixed` | `ssh://root@192.168.50.2:3323/Outbook/smart-iotDashboard-mixed.git` | `./smart-iotDashboard-mixed` | 面向大屏展示物联数据大盘，支持可视化拓扑和图表分析。 |
| `meeting` | 会议管理 | 会议 | `smart-meeting-mixed` | `ssh://root@192.168.50.2:3323/Outbook/smart-meeting-mixed.git` | `./smart-meeting-mixed` | 提供会议室、会议预约、会议安排与相关记录管理能力。 |
| `notice` | 校园公告 | 公告 | `smart-notice-mixed` | `ssh://root@192.168.50.2:3323/Outbook/smart-notice-mixed.git` | `./smart-notice-mixed` | 提供校园通知、紧急公告、新闻动态的发布与审核流程。 |
| `pubInfo` | 信发应用 | 信发、信息发布 | `smart-pubInfo-mixed` | `ssh://root@192.168.50.2:3323/Outbook/smart-pubInfo-mixed.git` | `./smart-pubInfo-mixed` | 用于多媒体信息发布终端的内容发布、节目制作和排期管理。 |
| `room-change` | 教室调换 | 调课、调室 | `smart-room-change-mixed` | `ssh://root@192.168.50.2:3323/Outbook/smart-room-change-mixed.git` | `./smart-room-change-mixed` | 提供教室临时占用、调课调室申请与审批流程。 |
| `room-introduction` | 教室介绍 | 空间介绍 | `smart-roomIntroduction-mixed` | `ssh://root@192.168.50.2:3323/Outbook/smart-roomIntroduction-mixed.git` | `./smart-roomIntroduction-mixed` | 提供教室基础信息、空间介绍、设施说明和展示入口。 |
| `seatVision` | AI座位识别 | 占座、占座插件 | `smart-seatVision-mixed` | `ssh://root@192.168.50.2:3323/zhangzhixiong/smart-seatVision-mixed.git` | `./smart-seatVision-mixed` | 提供座位状态的 AI 识别和占用判断能力。 |
| 未配置 | 未配置 | 对接插件、采集插件 | `smart-spider-mixed` | `ssh://root@192.168.50.2:3323/Outbook/smart-spider-mixed.git` | `./smart-spider-mixed` | 当前无 `frontend/public/config.json`，不编造 `app` / `appName`；业务上负责第三方数据抓取、清洗和同步。 |
| `study-settings` | 自习设置 | 自习 | `smart-studySettings-mixed` | `ssh://root@192.168.50.2:3323/Outbook/smart-studySettings-mixed.git` | `./smart-studySettings-mixed` | 提供自习空间、时段、规则等配置管理能力。 |
| `touch` | 碰一碰 | NFC碰一碰 | `smart-touch-mixed` | `ssh://root@192.168.50.2:3323/Outbook/smart-touch-mixed.git` | `./smart-touch-mixed` | 管理 NFC 碰一碰设备、快速关联与交互响应配置。 |
| `triAudit` | 三审三校 | 内容审核 | `smart-triAudit-mixed` | `ssh://root@192.168.50.2:3323/Outbook/smart-triAudit-mixed.git` | `./smart-triAudit-mixed` | 实现信息发布及媒体内容发布的多级审核机制。 |
| `uniTask` | 统一任务 | 定时任务、任务调度 | `smart-uniTask-mixed` | `ssh://root@192.168.50.2:3323/Outbook/smart-uniTask-mixed.git` | `./smart-uniTask-mixed` | 负责分布式定时任务和后台作业的统一调度、执行与监控。 |

## 工具插件

`smart-tools` 当前无 `frontend/public/config.json`，因此不将目录名中的 `tools` 当作配置事实。

| 项目名称 | 已登记别名 | 英文项目名 | Git 仓库 | 相对路径 | 说明 |
| --- | --- | --- | --- | --- | --- |
| 运维工具 | 工具插件 | `smart-tools` | `ssh://root@192.168.50.2:3323/Outbook/smart-tools.git` | `./smart-tools` | 提供系统故障排查、脚本执行、健康检查等运维管理工具。 |

## 终端与应用系统

| 项目 ID | 中文名 | 英文项目名 | Git 仓库 | 相对路径 | 说明 |
| --- | --- | --- | --- | --- | --- |
| `-` | 电子班牌 Android 终端 | `ClassScreen` | `ssh://root@192.168.50.2:3323/Outbook/ClassScreen.git` | `./ClassScreen` | 电子班牌端侧 Android App，提供人脸识别、考勤核验、信发内容展示等终端交互与硬件适配。 |
| `-` | 微信小程序 (v4) | `outbook-miniprogram-v4` | `ssh://root@192.168.50.2:3323/Outbook/outbook-miniprogram-v4.git` | `./outbook-miniprogram-v4` | 移动端微信小程序，提供家长端、教师端的移动办公应用入口及校园服务交互。 |

## 快速归属判断

| 用户说法 | 优先查看 |
| --- | --- |
| 基座、宿主、公共服务、插件加载、统一登录、菜单、公共权限 | `smart-core-mixed` |
| 活动、活动计划、日程任务 | `smart-activity-mixed` |
| 考勤、课堂考勤、打卡、考勤规则、考勤统计 | `smart-attendance-mixed` |
| 基础数据、基础包、组织架构、角色权限、公共配置 | `smart-basic-mixed` |
| 教室预约、预约申请、预约审批、预约记录 | `smart-book-mixed` |
| 班牌、电子班牌、班级应用、班级屏、班牌设备 | `smart-classPanel-mixed`；端侧 Android 问题也可能涉及 `ClassScreen` |
| 课程、排课、课表、选课 | `smart-course-mixed` |
| 督导巡课、巡课任务、课堂督导、巡课记录 | `smart-course-supervision-mixed` |
| 设备控制、统一控制、场景联动、控制入口 | `smart-deviceControl-mixed`；具体设备能力也可能涉及 `smart-iot-mixed` |
| 门禁、通行、授权、出入记录 | `smart-door-mixed` |
| 考试、排考、成绩 | `smart-exam-mixed` |
| 人脸、人脸识别、人脸底库、人脸核验 | `smart-face-mixed`；端侧识别问题也可能涉及 `ClassScreen` |
| 意见、建议、问题反馈 | `smart-feedback-mixed` |
| 楼栋、楼层、空间索引、空间导航 | `smart-floorBuildingIndex-mixed` |
| 人头监测、点人头、人流、人数监测、空间人数识别 | `smart-headcount-mixed` |
| 物联、IoT、设备接入、协议、设备状态 | `smart-iot-mixed` |
| 物联大屏、物联可视化、拓扑、图表大屏 | `smart-iotDashboard-mixed` |
| 会议、会议室、会议预约、会议安排 | `smart-meeting-mixed` |
| 公告、通知、新闻、紧急公告 | `smart-notice-mixed` |
| 信发、信息发布、节目、排期、多媒体发布 | `smart-pubInfo-mixed`；内容审核可能涉及 `smart-triAudit-mixed` |
| 调课、调室、教室临时占用 | `smart-room-change-mixed` |
| 教室介绍、空间介绍、设施说明、展示入口 | `smart-roomIntroduction-mixed` |
| AI 座位识别、占座、占座插件、座位状态 | `smart-seatVision-mixed` |
| 对接、采集、抓取、数据清洗 | `smart-spider-mixed` |
| 自习、自习空间、自习时段、自习规则 | `smart-studySettings-mixed` |
| 运维、健康检查、脚本、故障排查 | `smart-tools` |
| 碰一碰、NFC、碰一碰设备 | `smart-touch-mixed` |
| 三审三校、内容审核、多级审核 | `smart-triAudit-mixed` |
| 定时任务、后台作业、调度监控 | `smart-uniTask-mixed` |
| Android 终端、端侧 App、硬件适配 | `ClassScreen` |
| 家长端、教师端、小程序、移动端微信入口 | `outbook-miniprogram-v4` |

## 维护规则

- 新增、删除或重命名项目时，更新本文件对应清单和快速归属判断；只有触发场景发生变化时才同步修改 `SKILL.md` 的 description。
- `app` / `appName` 变更时，直接读取对应插件的 `frontend/public/config.json` 更新本文件；不从 README、包名或目录名反推。
- 别名只更新“已登记别名”和“快速归属判断”；发生冲突时，使用插件标识或工程名消歧。
- 变更仓库 URL 前，优先核对实际 Git remote；变更目录或业务说明时，以实际工作区和用户确认清单为准。
- 工程无 `frontend/public/config.json` 或缺少 `app` / `appName` 时，将两列记为“未配置”，保留工程名、仓库、别名和业务说明。
- 更新后运行 `scripts/check-project-map.py --workspace <smart-工作区>`；发现地图与实际配置冲突时，说明差异并回写本文件。
