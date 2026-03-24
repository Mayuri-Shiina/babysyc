import Link from "next/link";
import {
  Baby,
  Check,
  ChevronRight,
  Pill,
  Ruler,
  TrendingUp,
  Weight,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

const babyProfile = {
  name: "小糯米",
  gender: "女宝宝",
  birthDate: "2025年11月16日",
  weekAge: "第 18 周",
  dayAge: "第 128 天",
};

const vitalStats = [
  { id: "weight", label: "体重", value: "6.4", unit: "kg", accent: "bg-[#fff3ec]" },
  { id: "height", label: "身长", value: "63", unit: "cm", accent: "bg-[#f9f1ff]" },
  { id: "head", label: "头围", value: "41", unit: "cm", accent: "bg-[#eef7ff]" },
];

const growthChartWeeks = ["12周", "13周", "14周", "15周", "16周", "17周", "18周"];

const growthChartSeries = [
  {
    id: "weight",
    label: "体重",
    color: "#ea7a56",
    values: [4.9, 5.2, 5.4, 5.7, 5.9, 6.1, 6.4],
    displayValue: "6.4 kg",
    dotClassName: "bg-[#ea7a56]",
  },
  {
    id: "height",
    label: "身长",
    color: "#8f68d8",
    values: [56, 57.4, 58.8, 60.1, 61.2, 62.1, 63],
    displayValue: "63 cm",
    dotClassName: "bg-[#8f68d8]",
  },
  {
    id: "head",
    label: "头围",
    color: "#58a8cf",
    values: [37.5, 38.1, 38.7, 39.3, 39.8, 40.4, 41],
    displayValue: "41 cm",
    dotClassName: "bg-[#58a8cf]",
  },
];

const milestones = [
  { id: "milestone-1", text: "会追视移动物体", done: true },
  { id: "milestone-2", text: "听到声音会转头", done: true },
  { id: "milestone-3", text: "趴卧时能短暂抬头", done: true },
  { id: "milestone-4", text: "开始发出咿呀声（4-5 月）", done: false },
];

const vaccineReminders = [
  { id: "vaccine-1", title: "百白破第二针", status: "2 天后到期", tone: "bg-[#fff4ea]" },
  { id: "vaccine-2", title: "乙肝疫苗第二剂", status: "已完成", tone: "bg-[#f6f2ea]" },
];

const weeklyTrends = [
  { id: "trend-1", label: "体重变化", value: "+0.2 kg", note: "比上次记录更稳一点", accent: "bg-[#fff0e8]" },
  { id: "trend-2", label: "睡眠趋势", value: "13.5 h", note: "夜醒次数有减少", accent: "bg-[#f3efff]" },
  { id: "trend-3", label: "喂养节奏", value: "5 次", note: "节奏稳定，状态平缓", accent: "bg-[#eef7ff]" },
];

const weeklyAdviceBars = [
  {
    id: "advice-feeding",
    icon: "🍼",
    text: "已喂 2 次，建议 8-12 次，还差 6 次",
    tone: "bg-[#fff6eb]",
    color: "text-[#8b674e]",
  },
  {
    id: "advice-sleep",
    icon: "🌙",
    text: "今日睡了 1h30m，建议 14-17 小时",
    tone: "bg-[#f1edff]",
    color: "text-[#5e508f]",
  },
  {
    id: "advice-diaper",
    icon: "🧷",
    text: "换了 2 次尿片，可判断宝宝是否吃够",
    tone: "bg-[#eaf5ff]",
    color: "text-[#4d7592]",
  },
];


// 计算折线图中单个数据点的坐标，使用每条线自己的相对区间做归一化显示。
function buildChartPoints(values: number[]): string {
  const width = 100;
  const height = 100;
  const paddingX = 6;
  const paddingY = 10;
  const minValue = Math.min(...values);
  const maxValue = Math.max(...values);
  const range = Math.max(maxValue - minValue, 1);

  return values
    .map((value, index) => {
      const x = paddingX + (index * (width - paddingX * 2)) / (values.length - 1);
      const normalized = (value - minValue) / range;
      const y = height - paddingY - normalized * (height - paddingY * 2);
      return `${x},${y}`;
    })
    .join(" ");
}


// 渲染成长页顶部宝宝身份卡，突出头像、出生信息和周龄日龄。
function GrowthIdentityHeader() {
  return (
    <Card className="overflow-hidden rounded-[2.2rem] border-white/45 bg-[linear-gradient(180deg,rgba(255,251,247,0.95)_0%,rgba(247,238,229,0.92)_100%)] shadow-[0_24px_70px_rgba(183,145,117,0.12)] backdrop-blur-xl">
      <CardContent className="px-5 py-5 sm:px-6 sm:py-6">
        <div className="flex items-start gap-4">
          <div className="flex h-22 w-22 shrink-0 items-center justify-center rounded-full bg-[linear-gradient(180deg,#ffd8bf_0%,#f4c6ab_100%)] shadow-[0_16px_36px_rgba(194,152,121,0.2)] ring-4 ring-white/80">
            <span className="text-4xl">🌱</span>
          </div>
          <div className="min-w-0 flex-1 space-y-2 pt-1">
            <div className="space-y-1">
              <p className="text-3xl font-semibold tracking-tight text-[#2f241e]">{babyProfile.name}</p>
              <p className="text-base font-medium text-[#8f7564]">
                {babyProfile.gender} · {babyProfile.birthDate}
              </p>
              <p className="text-base font-medium text-[#7c6557]">
                {babyProfile.weekAge} · {babyProfile.dayAge}
              </p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}


// 渲染成长页三项核心指标卡，作为首屏的主要数据入口。
function GrowthVitalStats() {
  return (
    <div className="grid grid-cols-3 gap-3">
      {vitalStats.map((stat) => (
        <Card
          key={stat.id}
          className="rounded-[1.7rem] border-white/45 bg-white/75 shadow-[0_14px_32px_rgba(183,145,117,0.1)] backdrop-blur-xl"
        >
          <CardContent className="px-3 py-4 text-center sm:px-4 sm:py-5">
            <div className={`mx-auto mb-3 flex h-10 w-10 items-center justify-center rounded-2xl ${stat.accent}`}>
              {stat.id === "weight" ? (
                <Weight className="size-4 text-[#df7d5d]" />
              ) : stat.id === "height" ? (
                <Ruler className="size-4 text-[#8f68d8]" />
              ) : (
                <Baby className="size-4 text-[#58a8cf]" />
              )}
            </div>
            <p className="text-[2rem] leading-none font-semibold text-[#2f241e]">{stat.value}</p>
            <p className="mt-1 text-sm font-medium text-[#8d7565]">{stat.unit}</p>
            <p className="mt-2 text-base font-medium text-[#7a6457]">{stat.label}</p>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}


// 渲染成长页二级标签页导航，固定承载生长发育、疫苗提醒和本周趋势。
function GrowthTabsHeader() {
  return (
    <TabsList className="w-full justify-between rounded-full bg-white/75 p-1 shadow-[0_16px_36px_rgba(183,145,117,0.08)]">
      <TabsTrigger
        value="development"
        className="h-12 rounded-full px-5 text-base font-semibold data-active:bg-[#ea7a56] data-active:text-white"
      >
        生长发育
      </TabsTrigger>
      <TabsTrigger
        value="vaccine"
        className="h-12 rounded-full px-5 text-base font-semibold data-active:bg-[#ea7a56] data-active:text-white"
      >
        疫苗提醒
      </TabsTrigger>
      <TabsTrigger
        value="trend"
        className="h-12 rounded-full px-5 text-base font-semibold data-active:bg-[#ea7a56] data-active:text-white"
      >
        本周趋势
      </TabsTrigger>
    </TabsList>
  );
}


// 渲染身高、体重、头围三参数折线趋势图，提供一个更直观的成长变化视图。
function GrowthLineChartPanel() {
  return (
    <Card className="rounded-[2rem] border-white/45 bg-white/85 shadow-[0_20px_54px_rgba(183,145,117,0.1)] backdrop-blur-xl">
      <CardContent className="space-y-5 px-5 py-5 sm:px-6">
        <div className="space-y-1">
          <h2 className="text-2xl font-semibold text-[#2f241e]">成长折线趋势</h2>
          <p className="text-sm leading-6 text-[#9a8274]">把体重、身长、头围放在同一张趋势图里，先看整体变化节奏。</p>
        </div>

        <div className="grid grid-cols-3 gap-3">
          {growthChartSeries.map((series) => (
            <div
              key={series.id}
              className="rounded-[1.4rem] bg-[#fbf6ef] px-4 py-4 shadow-[inset_0_1px_0_rgba(255,255,255,0.8)]"
            >
              <div className="flex items-center gap-2">
                <span className={`h-2.5 w-2.5 rounded-full ${series.dotClassName}`} />
                <p className="text-sm font-medium text-[#8d7565]">{series.label}</p>
              </div>
              <p className="mt-3 text-2xl font-semibold text-[#2f241e]">{series.displayValue}</p>
            </div>
          ))}
        </div>

        <div className="rounded-[1.75rem] bg-[linear-gradient(180deg,#fffdfb_0%,#fbf4ec_100%)] p-4 shadow-[inset_0_1px_0_rgba(255,255,255,0.82)]">
          <svg viewBox="0 0 100 100" className="h-64 w-full">
            <defs>
              <linearGradient id="weight-fill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#ea7a56" stopOpacity="0.16" />
                <stop offset="100%" stopColor="#ea7a56" stopOpacity="0" />
              </linearGradient>
              <linearGradient id="height-fill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#8f68d8" stopOpacity="0.14" />
                <stop offset="100%" stopColor="#8f68d8" stopOpacity="0" />
              </linearGradient>
              <linearGradient id="head-fill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#58a8cf" stopOpacity="0.14" />
                <stop offset="100%" stopColor="#58a8cf" stopOpacity="0" />
              </linearGradient>
            </defs>

            {[18, 36, 54, 72, 90].map((y) => (
              <line
                key={`grid-${y}`}
                x1="6"
                y1={y}
                x2="94"
                y2={y}
                stroke="#efe2d6"
                strokeWidth="0.6"
                strokeDasharray="2 2"
              />
            ))}

            {growthChartSeries.map((series) => {
              const points = buildChartPoints(series.values);
              const lastPoint = points.split(" ").at(-1)?.split(",") ?? ["0", "0"];

              return (
                <g key={series.id}>
                  <polyline
                    fill="none"
                    stroke={series.color}
                    strokeWidth="1.8"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    points={points}
                  />
                  {points.split(" ").map((point) => {
                    const [x, y] = point.split(",");
                    return <circle key={`${series.id}-${point}`} cx={x} cy={y} r="1.6" fill={series.color} />;
                  })}
                  <circle cx={lastPoint[0]} cy={lastPoint[1]} r="2.3" fill={series.color} />
                </g>
              );
            })}

            {growthChartWeeks.map((week, index) => (
              <text
                key={week}
                x={6 + (index * 88) / (growthChartWeeks.length - 1)}
                y="98"
                textAnchor="middle"
                fontSize="3.1"
                fill="#a48977"
              >
                {week}
              </text>
            ))}
          </svg>
        </div>

        <div className="rounded-[1.5rem] bg-[#fbf6ef] px-4 py-4 text-base leading-7 text-[#6f5b4e]">
          最近几周的身高、体重、头围都在稳定上升。当前先用静态高保真趋势图承接，后续接真实数据后直接替换为接口结果。
        </div>
      </CardContent>
    </Card>
  );
}


// 渲染发育里程碑卡，突出当前阶段已完成和待观察的能力点。
function MilestonePanel() {
  return (
    <Card className="rounded-[2rem] border-white/45 bg-white/85 shadow-[0_20px_54px_rgba(183,145,117,0.1)] backdrop-blur-xl">
      <CardContent className="px-5 py-5 sm:px-6">
        <div className="space-y-1">
          <h2 className="text-2xl font-semibold text-[#2f241e]">发育里程碑</h2>
          <p className="text-sm leading-6 text-[#9a8274]">这个阶段常见的发育表现，可以边观察边补记录。</p>
        </div>

        <div className="mt-4 rounded-[1.6rem] bg-[#fffdfb] px-4">
          {milestones.map((item, index) => (
            <div
              key={item.id}
              className={`flex items-center gap-4 py-5 ${index === 0 ? "" : "border-t border-[#f2e7dc]"}`}
            >
              <div
                className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-full ${
                  item.done
                    ? "bg-[#edf8ef] text-[#68ab73]"
                    : "border border-[#eadbce] bg-[#fffaf5] text-[#cfad95]"
                }`}
              >
                {item.done ? <Check className="size-5" /> : <span className="text-lg leading-none">○</span>}
              </div>
              <p className={`text-xl leading-8 ${item.done ? "font-medium text-[#342821]" : "text-[#8d7768]"}`}>
                {item.text}
              </p>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}


// 渲染疫苗提醒卡，作为成长页内部的二级入口和近期摘要。
function VaccineReminderPanel() {
  return (
    <Card className="rounded-[2rem] border-white/45 bg-white/85 shadow-[0_20px_54px_rgba(183,145,117,0.1)] backdrop-blur-xl">
      <CardContent className="space-y-4 px-5 py-5 sm:px-6">
        <div className="flex items-start justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2 text-sm font-medium text-[#8f7564]">
              <Pill className="size-4" />
              <span>疫苗提醒</span>
            </div>
            <h2 className="text-2xl font-semibold text-[#2f241e]">近期疫苗安排</h2>
            <p className="text-sm leading-6 text-[#9a8274]">疫苗作为成长页内部二级入口承接，不进入一级导航。</p>
          </div>
          <Link
            href="/vaccine"
            className="inline-flex h-10 items-center justify-center gap-1 rounded-full bg-[#ea7a56] px-4 text-sm font-semibold text-white transition-all hover:bg-[#d86b48]"
          >
            进入疫苗
            <ChevronRight className="size-4" />
          </Link>
        </div>

        <div className="space-y-3">
          {vaccineReminders.map((item) => (
            <div
              key={item.id}
              className={`flex items-center justify-between gap-3 rounded-[1.5rem] px-4 py-4 ${item.tone}`}
            >
              <span className="text-base font-medium text-[#4f3c31]">{item.title}</span>
              <span className="rounded-full bg-white/80 px-3 py-1 text-sm font-medium text-[#8d7565]">
                {item.status}
              </span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}


// 渲染本周趋势卡，展示体重、睡眠和喂养三个方向的轻量趋势。
function WeeklyTrendPanel() {
  return (
    <div className="space-y-4">
      <Card className="rounded-[2rem] border-white/45 bg-white/85 shadow-[0_20px_54px_rgba(183,145,117,0.1)] backdrop-blur-xl">
        <CardContent className="space-y-4 px-5 py-5 sm:px-6">
          <div className="flex items-center gap-2 text-sm font-medium text-[#8f7564]">
            <TrendingUp className="size-4" />
            <span>本周趋势</span>
          </div>
          <div className="grid grid-cols-3 gap-3">
            {weeklyTrends.map((trend) => (
              <div
                key={trend.id}
                className={`rounded-[1.6rem] px-4 py-4 ${trend.accent} shadow-[inset_0_1px_0_rgba(255,255,255,0.72)]`}
              >
                <p className="text-sm font-medium text-[#8d7565]">{trend.label}</p>
                <p className="mt-3 text-[2rem] leading-none font-semibold text-[#2f241e]">{trend.value}</p>
                <p className="mt-3 text-sm leading-6 text-[#6f5b4e]">{trend.note}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <div className="space-y-2">
        {weeklyAdviceBars.map((item) => (
          <div
            key={item.id}
            className={`flex items-center gap-3 rounded-[1.35rem] px-4 py-4 text-lg font-medium ${item.tone} ${item.color}`}
          >
            <span className="text-2xl leading-none">{item.icon}</span>
            <span>{item.text}</span>
          </div>
        ))}
      </div>
    </div>
  );
}


// 渲染成长页主体，使用确认后的固定二级标签组织主要内容。
export default function GrowthPage() {
  return (
    <main className="min-h-screen bg-[linear-gradient(180deg,#fffaf4_0%,#f7ecdf_42%,#f4e5d5_100%)] px-4 pb-28 pt-6 text-[#3e3027] sm:px-6">
      <div className="mx-auto flex max-w-5xl flex-col gap-5">
        <GrowthIdentityHeader />
        <GrowthVitalStats />

        <Tabs defaultValue="development" className="gap-4">
          <GrowthTabsHeader />

          <TabsContent value="development" className="space-y-4">
            <GrowthLineChartPanel />
            <MilestonePanel />
          </TabsContent>

          <TabsContent value="vaccine" className="space-y-4">
            <VaccineReminderPanel />
          </TabsContent>

          <TabsContent value="trend" className="space-y-4">
            <WeeklyTrendPanel />
          </TabsContent>
        </Tabs>

        <div className="flex justify-center pt-1">
          <Button
            type="button"
            className="h-12 rounded-full bg-[#ea7a56] px-6 text-base font-semibold text-white shadow-[0_18px_40px_rgba(218,122,89,0.24)] hover:bg-[#d86b48]"
          >
            记录新数据
          </Button>
        </div>
      </div>
    </main>
  );
}
