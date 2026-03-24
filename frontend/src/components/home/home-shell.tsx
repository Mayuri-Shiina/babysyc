import Link from "next/link";
import {
  Bell,
  Camera,
  ChevronRight,
  Heart,
  MessageCircleMore,
  Ruler,
  Sparkles,
  Stethoscope,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

const pendingReminders = [
  {
    id: "reminder-vaccine",
    title: "百白破第二针将在 2 天后到期",
    detail: "记得提前安排接种时间，完成后可以顺手补一条记录。",
  },
  {
    id: "reminder-growth",
    title: "已经 3 天没有新增成长记录",
    detail: "补一条体重、睡眠或喂养情况，后续趋势会更完整。",
  },
];

const quickActions = [
  {
    id: "quick-growth",
    title: "记体征",
    description: "宝宝最近会独坐了吗？点击记录。",
    href: "/growth",
    icon: Ruler,
  },
  {
    id: "quick-media",
    title: "传照片",
    description: "把今天的可爱瞬间放进成长相册。",
    href: "/media",
    icon: Camera,
  },
  {
    id: "quick-agent",
    title: "问问 Agent",
    description: "看看最近有哪些成长变化值得关注。",
    href: "/agent",
    icon: MessageCircleMore,
  },
];

const recentMedia = [
  { id: "media-1", label: "第一次趴趴看", tone: "bg-[#f5dfd2]" },
  { id: "media-2", label: "午后晒太阳", tone: "bg-[#eadcc8]" },
  { id: "media-3", label: "和外婆互动", tone: "bg-[#d8c6bb]" },
];

const latestGrowthRecords = [
  { id: "growth-1", label: "体重", value: "6.4 kg", note: "比上次增加 0.2 kg" },
  { id: "growth-2", label: "睡眠", value: "13.5 h", note: "夜醒次数减少" },
  { id: "growth-3", label: "喂养", value: "5 次", note: "节奏稳定" },
];

const bottomNavigationItems = [
  { id: "nav-home", label: "首页", href: "/home", active: true },
  { id: "nav-growth", label: "成长", href: "/growth", active: false },
  { id: "nav-media", label: "相册", href: "/media", active: false },
  { id: "nav-agent", label: "Agent", href: "/agent", active: false },
];


// 生成首页 Hero 卡片中的一句话摘要，先使用规则文案承载“正在成长”的情感体验。
function getHeroSummary() {
  return "今天已经是来到这个世界的第 128 天啦，最近开始更爱笑，也更愿意和家人互动。";
}


// 渲染首页顶部栏，优先传达宝宝身份和轻问候语。
function HomeHeader() {
  return (
    <header className="flex items-center justify-between gap-4 rounded-[2rem] border border-white/45 bg-white/55 px-5 py-4 backdrop-blur-xl">
      <div className="space-y-1">
        <p className="text-xs font-medium uppercase tracking-[0.28em] text-[#a78672]">Baby Archive</p>
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-semibold text-[#5d4638]">小糯米</h1>
          <button
            type="button"
            className="rounded-full bg-[#f2e6da] px-3 py-1 text-xs font-medium text-[#8d6f5c]"
          >
            当前宝宝
          </button>
        </div>
        <p className="text-sm text-[#8f7768]">今天也记录一点小成长</p>
      </div>
      <div className="flex h-11 w-11 items-center justify-center rounded-full bg-[#fff7f0] text-[#af8b73] shadow-[0_12px_30px_rgba(189,151,124,0.16)]">
        <Heart className="size-5" />
      </div>
    </header>
  );
}


// 渲染宝宝今日核心卡片，集中回答“目前宝宝多大、状态如何”。
function HeroCard() {
  return (
    <Card className="overflow-hidden rounded-[2rem] border-white/35 bg-white/50 shadow-[0_24px_80px_rgba(161,124,98,0.16)] backdrop-blur-2xl">
      <CardContent className="relative overflow-hidden px-6 py-6 sm:px-7 sm:py-7">
        <div className="absolute inset-x-0 top-0 h-32 bg-[radial-gradient(circle_at_top_left,_rgba(255,255,255,0.8),_rgba(255,255,255,0))]" />
        <div className="grid gap-6 sm:grid-cols-[auto_1fr] sm:items-center">
          <div className="relative flex h-28 w-28 items-center justify-center rounded-[2rem] bg-[linear-gradient(160deg,#fff7f0_0%,#edd8c8_100%)] p-1 shadow-[0_18px_40px_rgba(178,139,110,0.22)]">
            <div className="flex h-full w-full items-center justify-center rounded-[1.65rem] bg-[linear-gradient(180deg,#fff9f4_0%,#f1dfd1_100%)] text-3xl font-semibold text-[#a27f69]">
              糯
            </div>
          </div>
          <div className="space-y-4">
            <div className="flex flex-wrap items-center gap-2 text-sm text-[#9c7b68]">
              <span className="rounded-full bg-[#fff4eb] px-3 py-1 font-medium">第 128 天</span>
              <span className="rounded-full bg-[#f1e2d6] px-3 py-1 font-medium">4 个月 8 天</span>
            </div>
            <div className="space-y-2">
              <h2 className="text-2xl font-semibold tracking-tight text-[#5b4337] sm:text-[2rem]">
                小家伙正在把每一天都长成新的模样。
              </h2>
              <p className="max-w-2xl text-sm leading-7 text-[#81685a] sm:text-base">{getHeroSummary()}</p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}


// 渲染高优先级提醒卡片组，无提醒时由上层控制隐藏。
function PendingRemindersSection() {
  if (pendingReminders.length === 0) {
    return null;
  }

  return (
    <section className="space-y-3">
      <div className="flex items-center gap-2 text-sm font-medium text-[#8f6d5b]">
        <Bell className="size-4" />
        <span>待留意的提醒</span>
      </div>
      <div className="grid gap-3">
        {pendingReminders.map((reminder) => (
          <Card
            key={reminder.id}
            className="rounded-[1.75rem] border border-[#ecd7c7]/70 bg-[linear-gradient(180deg,rgba(255,250,246,0.92)_0%,rgba(249,236,224,0.88)_100%)] shadow-[0_16px_40px_rgba(193,155,125,0.12)] backdrop-blur-xl"
          >
            <CardContent className="flex items-start gap-4 px-5 py-5">
              <div className="mt-1 flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-[#f4dcc8] text-[#a87e65]">
                <Stethoscope className="size-5" />
              </div>
              <div className="space-y-1">
                <h3 className="text-sm font-semibold text-[#674d3f]">{reminder.title}</h3>
                <p className="text-sm leading-6 text-[#896d5c]">{reminder.detail}</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </section>
  );
}


// 渲染今日建议记录与快捷录入区域，降低首页首屏的记录门槛。
function QuickActionsSection() {
  return (
    <section className="space-y-3">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-sm font-medium text-[#7f6352]">今日建议记录</p>
          <p className="text-xs text-[#a08372]">把容易错过的小变化，轻轻记下来。</p>
        </div>
        <Button
          type="button"
          variant="ghost"
          className="rounded-full px-3 text-xs text-[#8e725f] hover:bg-[#f5e7db] hover:text-[#6f5547]"
        >
          更多建议
        </Button>
      </div>
      <div className="grid gap-3 sm:grid-cols-3">
        {quickActions.map((action) => {
          const ActionIcon = action.icon;
          return (
            <Card
              key={action.id}
              className="rounded-[1.75rem] border border-white/45 bg-white/60 shadow-[0_18px_50px_rgba(184,146,119,0.12)] backdrop-blur-xl"
            >
              <CardContent className="flex h-full flex-col gap-4 px-5 py-5">
                <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-[#fff2e8] text-[#ab8268] shadow-[inset_0_1px_0_rgba(255,255,255,0.85)]">
                  <ActionIcon className="size-5" />
                </div>
                <div className="space-y-2">
                  <h3 className="text-base font-semibold text-[#5f4739]">{action.title}</h3>
                  <p className="text-sm leading-6 text-[#8d7362]">{action.description}</p>
                </div>
                <Link
                  href={action.href}
                  className="mt-auto inline-flex h-8 items-center justify-center gap-1.5 rounded-full bg-[#9f785f] px-2.5 text-sm font-medium whitespace-nowrap text-[#fff8f3] shadow-[0_18px_40px_rgba(159,120,95,0.22)] transition-all hover:bg-[#906b54]"
                >
                  立即前往
                  <ChevronRight className="size-4" />
                </Link>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </section>
  );
}


// 渲染本周成长总结卡片，突出 Agent 生成价值和回顾感。
function AgentSummarySection() {
  return (
    <Card className="rounded-[2rem] border-white/45 bg-[linear-gradient(180deg,rgba(255,249,244,0.92)_0%,rgba(247,236,227,0.88)_100%)] shadow-[0_24px_60px_rgba(180,143,116,0.14)] backdrop-blur-xl">
      <CardHeader className="gap-3 px-6 pt-6">
        <div className="flex items-center gap-2 text-sm font-medium text-[#8d6e5d]">
          <Sparkles className="size-4" />
          <span>本周成长总结</span>
        </div>
        <div className="space-y-2">
          <CardTitle className="text-xl text-[#5f4738]">这一周，笑容和互动都悄悄变多了。</CardTitle>
          <CardDescription className="max-w-2xl text-sm leading-7 text-[#876d5d]">
            Agent 观察到，这周宝宝的互动状态更积极，睡眠节奏也更稳定。最近上传的照片和最新体征记录都显示，小家伙正在一点点长成更有回应的小朋友。
          </CardDescription>
        </div>
      </CardHeader>
      <CardContent className="grid gap-3 px-6 pb-6 sm:grid-cols-3">
        <div className="rounded-[1.5rem] bg-white/60 p-4 text-sm leading-6 text-[#7b6254]">
          <p className="font-medium text-[#5d4538]">亮点 1</p>
          <p>开始更频繁地看向熟悉的人，互动反馈更明显。</p>
        </div>
        <div className="rounded-[1.5rem] bg-white/60 p-4 text-sm leading-6 text-[#7b6254]">
          <p className="font-medium text-[#5d4538]">亮点 2</p>
          <p>最近照片记录更丰富，成长回忆有了更连续的片段。</p>
        </div>
        <div className="rounded-[1.5rem] bg-white/60 p-4 text-sm leading-6 text-[#7b6254]">
          <p className="font-medium text-[#5d4538]">建议</p>
          <p>下周可以多补一条睡眠或翻身尝试的记录，方便后续回看。</p>
        </div>
      </CardContent>
    </Card>
  );
}


// 渲染最近相册和视频回忆区域，满足回顾与“看娃”的高频需求。
function RecentMediaSection() {
  return (
    <section className="space-y-4">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h3 className="text-lg font-semibold text-[#5f4738]">最近相册回忆</h3>
          <p className="text-sm text-[#8e7463]">翻看最近留下的可爱瞬间。</p>
        </div>
        <Link
          href="/media"
          className="inline-flex h-8 items-center justify-center rounded-full px-3 text-sm font-medium text-[#8d725f] transition-all hover:bg-[#f5e8dc]"
        >
          查看全部
        </Link>
      </div>
      <div className="grid gap-3 sm:grid-cols-3">
        {recentMedia.map((item) => (
          <Card
            key={item.id}
            className="rounded-[1.75rem] border border-white/45 bg-white/60 shadow-[0_16px_45px_rgba(181,143,116,0.12)] backdrop-blur-xl"
          >
            <CardContent className="space-y-3 px-4 py-4">
              <div className={`aspect-[4/3] rounded-[1.5rem] ${item.tone} shadow-[inset_0_1px_0_rgba(255,255,255,0.65)]`} />
              <div className="space-y-1">
                <p className="text-sm font-medium text-[#61493b]">{item.label}</p>
                <p className="text-xs text-[#9c7f6d]">今天 14:20 · 相册已更新</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </section>
  );
}


// 渲染最新成长体征记录区域，作为进入成长页的自然入口。
function LatestGrowthRecordSection() {
  return (
    <section className="space-y-4">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h3 className="text-lg font-semibold text-[#5f4738]">最新成长记录</h3>
          <p className="text-sm text-[#8d7362]">看看最近一次记录到了哪些变化。</p>
        </div>
        <Link
          href="/growth"
          className="inline-flex h-8 items-center justify-center rounded-full px-3 text-sm font-medium text-[#8d725f] transition-all hover:bg-[#f6e8dc]"
        >
          进入成长页
        </Link>
      </div>
      <div className="grid gap-3 sm:grid-cols-3">
        {latestGrowthRecords.map((record) => (
          <Card
            key={record.id}
            className="rounded-[1.75rem] border border-white/45 bg-white/60 shadow-[0_18px_50px_rgba(183,145,117,0.11)] backdrop-blur-xl"
          >
            <CardContent className="space-y-2 px-5 py-5">
              <p className="text-xs font-medium uppercase tracking-[0.2em] text-[#a18270]">{record.label}</p>
              <p className="text-2xl font-semibold text-[#5f4739]">{record.value}</p>
              <p className="text-sm leading-6 text-[#8c7261]">{record.note}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </section>
  );
}


// 渲染底部固定导航，承载首页、成长、相册和 Agent 的全局切换入口。
function BottomNavigation() {
  return (
    <nav className="fixed inset-x-0 bottom-4 z-20 mx-auto flex w-[min(92vw,30rem)] items-center justify-between rounded-full border border-white/55 bg-white/70 p-2 shadow-[0_28px_60px_rgba(160,121,95,0.18)] backdrop-blur-2xl">
      {bottomNavigationItems.map((item) => (
        <Link
          key={item.id}
          href={item.href}
          className={item.active ? "inline-flex h-8 items-center justify-center rounded-full bg-[#9f785f] px-5 text-sm font-medium whitespace-nowrap text-[#fff8f3] transition-all hover:bg-[#906b54]" : "inline-flex h-8 items-center justify-center rounded-full px-5 text-sm font-medium whitespace-nowrap text-[#8d715e] transition-all hover:bg-[#f6e7db] hover:text-[#6f5547]"}
        >
          {item.label}
        </Link>
      ))}
    </nav>
  );
}


// 渲染首页静态骨架，聚焦“温暖、回忆感和正在成长中的状态”。
export function HomeShell() {
  return (
    <div className="min-h-screen bg-[linear-gradient(180deg,#fffaf5_0%,#f6ece2_45%,#efe0d2_100%)] text-[#5c4436]">
      <div className="pointer-events-none fixed inset-0 bg-[radial-gradient(circle_at_top_left,_rgba(255,255,255,0.75),_rgba(255,255,255,0)_35%),radial-gradient(circle_at_top_right,_rgba(246,225,210,0.45),_rgba(246,225,210,0)_26%),radial-gradient(circle_at_bottom_left,_rgba(234,213,196,0.4),_rgba(234,213,196,0)_24%)]" />
      <main className="relative mx-auto flex w-full max-w-6xl flex-col gap-6 px-4 pb-28 pt-4 sm:px-6 sm:pb-32 sm:pt-6 lg:px-8">
        <HomeHeader />
        <HeroCard />
        <PendingRemindersSection />
        <QuickActionsSection />
        <div className="space-y-6 pt-2">
          <AgentSummarySection />
          <RecentMediaSection />
          <LatestGrowthRecordSection />
        </div>
      </main>
      <BottomNavigation />
    </div>
  );
}
