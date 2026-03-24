# 项目目录结构说明

本文档用于说明当前项目目录的职责边界，避免前后端代码在后续开发中出现职责混乱、重复堆叠或模块耦合过深的问题。

## 1. 目录设计原则
- 前后端分离，分别维护各自的页面、模块、业务逻辑和基础设施代码。
- 优先按业务模块拆分，再补充共享能力目录。
- 页面层、业务层、数据层和任务层保持职责清晰，不混写。
- 后续开始写代码时，每个函数前都要添加注释，说明函数功能。

## 2. 根目录

### [frontend](/E:/workspace/vibe_coding/baby/babysyc/frontend)
前端项目目录，负责 Web / PWA 页面、组件、交互逻辑和前端类型定义。

### [backend](/E:/workspace/vibe_coding/baby/babysyc/backend)
后端项目目录，负责接口、业务逻辑、数据模型、任务调度和 Agent 服务。

### [PRD.md](/E:/workspace/vibe_coding/baby/babysyc/PRD.md)
完整产品需求文档，描述产品定位、权限、功能、Agent 能力、范围与验收标准。

### [MVP.md](/E:/workspace/vibe_coding/baby/babysyc/MVP.md)
最小可行版本文档，描述当前阶段必须落地的闭环、核心功能和开发优先级。

### [STRUCTURE.md](/E:/workspace/vibe_coding/baby/babysyc/STRUCTURE.md)
项目目录职责说明文档，用于约束目录边界和后续扩展方式。

## 3. 前端目录说明

### [frontend/public](/E:/workspace/vibe_coding/baby/babysyc/frontend/public)
存放静态资源，例如图标、PWA 相关文件、默认图片和不参与构建编译的素材。

### [frontend/src](/E:/workspace/vibe_coding/baby/babysyc/frontend/src)
前端源码根目录。

### [frontend/src/app](/E:/workspace/vibe_coding/baby/babysyc/frontend/src/app)
Next.js App Router 页面入口层，负责页面路由、布局和页面级组织，不承载复杂业务细节。

### [frontend/src/app/home](/E:/workspace/vibe_coding/baby/babysyc/frontend/src/app/home)
首页模块路由目录，后续用于承载宝宝今日卡片、最近照片、本周总结、提醒和记录建议。

### [frontend/src/app/growth](/E:/workspace/vibe_coding/baby/babysyc/frontend/src/app/growth)
成长记录模块路由目录，后续用于录入和查看身高、体重、睡眠、喂养等内容。

### [frontend/src/app/vaccine](/E:/workspace/vibe_coding/baby/babysyc/frontend/src/app/vaccine)
疫苗模块路由目录，后续用于计划查看、已接种记录和提醒管理。

### [frontend/src/app/media](/E:/workspace/vibe_coding/baby/babysyc/frontend/src/app/media)
相册和视频模块路由目录，后续用于时间轴浏览、素材筛选和媒体详情展示。

### [frontend/src/app/agent](/E:/workspace/vibe_coding/baby/babysyc/frontend/src/app/agent)
Agent 页面路由目录，后续用于问答、成长总结和记录引导展示。

### [frontend/src/components](/E:/workspace/vibe_coding/baby/babysyc/frontend/src/components)
前端组件总目录，所有可复用 UI 组件都应放在这里，避免直接写进页面文件。

### [frontend/src/components/shared](/E:/workspace/vibe_coding/baby/babysyc/frontend/src/components/shared)
通用共享组件目录，例如按钮、弹窗、卡片、表单基础组件和通用布局块。

### [frontend/src/components/home](/E:/workspace/vibe_coding/baby/babysyc/frontend/src/components/home)
首页专属组件目录，例如今日卡片、最近照片卡片、本周总结卡片和提醒卡片。

### [frontend/src/components/growth](/E:/workspace/vibe_coding/baby/babysyc/frontend/src/components/growth)
成长记录专属组件目录，例如记录表单、趋势图、记录列表和分析卡片。

### [frontend/src/components/vaccine](/E:/workspace/vibe_coding/baby/babysyc/frontend/src/components/vaccine)
疫苗模块专属组件目录，例如疫苗计划卡片、接种记录列表和提醒组件。

### [frontend/src/components/media](/E:/workspace/vibe_coding/baby/babysyc/frontend/src/components/media)
相册和视频模块专属组件目录，例如媒体网格、时间筛选器、标签编辑器和详情弹层。

### [frontend/src/components/agent](/E:/workspace/vibe_coding/baby/babysyc/frontend/src/components/agent)
Agent 模块专属组件目录，例如问答输入框、总结卡片、建议列表和对话消息块。

### [frontend/src/lib](/E:/workspace/vibe_coding/baby/babysyc/frontend/src/lib)
前端工具和基础能力目录，后续用于接口请求封装、格式化方法、权限判断和常量管理。

### [frontend/src/types](/E:/workspace/vibe_coding/baby/babysyc/frontend/src/types)
前端类型定义目录，后续用于定义接口返回类型、业务实体类型和组件入参类型。

### [frontend/src/hooks](/E:/workspace/vibe_coding/baby/babysyc/frontend/src/hooks)
前端自定义 Hook 目录，后续用于抽离状态逻辑、接口调用逻辑和页面交互逻辑。

### [frontend/src/styles](/E:/workspace/vibe_coding/baby/babysyc/frontend/src/styles)
前端样式目录，后续用于全局样式、主题变量和特殊样式文件。

## 4. 后端目录说明

### [backend/app](/E:/workspace/vibe_coding/baby/babysyc/backend/app)
后端应用主目录，所有服务端核心代码都应放在此处。

### [backend/app/api](/E:/workspace/vibe_coding/baby/babysyc/backend/app/api)
接口聚合层目录，后续用于统一注册路由、版本入口和公共 API 配置。

### [backend/app/core](/E:/workspace/vibe_coding/baby/babysyc/backend/app/core)
后端核心基础设施目录，后续用于配置管理、数据库连接、鉴权中间件、日志和通用依赖。

### [backend/app/models](/E:/workspace/vibe_coding/baby/babysyc/backend/app/models)
数据模型目录，后续用于定义数据库 ORM 模型和模型间关系。

### [backend/app/schemas](/E:/workspace/vibe_coding/baby/babysyc/backend/app/schemas)
数据校验模型目录，后续用于定义请求体、响应体和内部数据传输结构。

### [backend/app/services](/E:/workspace/vibe_coding/baby/babysyc/backend/app/services)
通用服务目录，后续用于沉淀跨模块复用的业务服务，例如文件上传、权限判断、消息编排和总结生成。

### [backend/app/tasks](/E:/workspace/vibe_coding/baby/babysyc/backend/app/tasks)
异步任务目录，后续用于提醒调度、媒体处理、周报生成和其他 Celery 任务。

### [backend/app/modules](/E:/workspace/vibe_coding/baby/babysyc/backend/app/modules)
业务模块目录，后端主要按业务域拆分，每个模块后续独立维护路由、服务、模型适配和业务逻辑。

### [backend/app/modules/auth](/E:/workspace/vibe_coding/baby/babysyc/backend/app/modules/auth)
认证与身份模块，后续负责登录、邀请、访问校验和会话管理。

### [backend/app/modules/family](/E:/workspace/vibe_coding/baby/babysyc/backend/app/modules/family)
家庭空间模块，后续负责家庭信息、家庭成员、角色和权限管理。

### [backend/app/modules/baby_profile](/E:/workspace/vibe_coding/baby/babysyc/backend/app/modules/baby_profile)
宝宝档案模块，后续负责宝宝基础资料、当前宝宝上下文和档案维护。

### [backend/app/modules/growth](/E:/workspace/vibe_coding/baby/babysyc/backend/app/modules/growth)
成长记录模块，后续负责体征记录、趋势分析和成长评估相关逻辑。

### [backend/app/modules/vaccine](/E:/workspace/vibe_coding/baby/babysyc/backend/app/modules/vaccine)
疫苗模块，后续负责计划生成、接种记录和提醒时间更新。

### [backend/app/modules/media](/E:/workspace/vibe_coding/baby/babysyc/backend/app/modules/media)
媒体模块，后续负责上传凭证、媒体元数据、标签、时间轴查询和媒体权限控制。

### [backend/app/modules/reminder](/E:/workspace/vibe_coding/baby/babysyc/backend/app/modules/reminder)
提醒模块，后续负责站内提醒、Web Push 订阅和提醒确认逻辑。

### [backend/app/modules/agent](/E:/workspace/vibe_coding/baby/babysyc/backend/app/modules/agent)
Agent 模块，后续负责问答会话、上下文拼装、总结生成、记录引导和风险提示。

### [backend/tests](/E:/workspace/vibe_coding/baby/babysyc/backend/tests)
后端测试目录，后续用于单元测试、接口测试和关键权限测试。

## 5. 后续文件组织约束
- 页面文件只负责页面组装，不直接堆积复杂逻辑。
- 通用业务逻辑优先放在 `services` 或 `lib` 中。
- 组件应尽量按业务模块归档，避免全部堆在 `shared`。
- 后端各模块优先保持独立，跨模块复用能力再抽到 `services`。
- 每个函数前必须添加注释，简要说明函数用途和职责边界。
