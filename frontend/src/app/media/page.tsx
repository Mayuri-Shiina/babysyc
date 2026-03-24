import { Card, CardContent } from "@/components/ui/card";

const recentMemories = [
  { id: "media-1", label: "第一次趴趴看", tone: "bg-[#f5dfd2]" },
  { id: "media-2", label: "午后晒太阳", tone: "bg-[#eadcc8]" },
  { id: "media-3", label: "和外婆互动", tone: "bg-[#d8c6bb]" },
];

// 渲染相册页内容，承接首页移出的最近相册回忆区块。
export default function MediaPage() {
  return (
    <main className="min-h-screen bg-[linear-gradient(180deg,#fffaf5_0%,#f4eadf_100%)] px-4 pb-28 pt-6 text-[#5c4436] sm:px-6">
      <div className="mx-auto flex max-w-4xl flex-col gap-5">
        <section className="space-y-2">
          <p className="text-xs font-medium uppercase tracking-[0.28em] text-[#a78672]">Media</p>
          <h1 className="text-3xl font-semibold text-[#5d4638]">相册</h1>
          <p className="text-sm leading-6 text-[#8f7768]">把最近的可爱瞬间和时间轴回忆都放在这里。</p>
        </section>

        <section className="space-y-3">
          <div>
            <h2 className="text-lg font-semibold text-[#5f4738]">最近相册回忆</h2>
            <p className="text-sm text-[#8e7463]">首页不再展开，回忆浏览回到相册页本身。</p>
          </div>
          <div className="grid gap-3 sm:grid-cols-3">
            {recentMemories.map((item) => (
              <Card
                key={item.id}
                className="rounded-[1.75rem] border border-white/45 bg-white/65 shadow-[0_16px_45px_rgba(181,143,116,0.12)] backdrop-blur-xl"
              >
                <CardContent className="space-y-3 px-4 py-4">
                  <div
                    className={`aspect-[4/3] rounded-[1.5rem] ${item.tone} shadow-[inset_0_1px_0_rgba(255,255,255,0.65)]`}
                  />
                  <div className="space-y-1">
                    <p className="text-sm font-medium text-[#61493b]">{item.label}</p>
                    <p className="text-xs text-[#9c7f6d]">今天 14:20 · 相册已更新</p>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>
      </div>
    </main>
  );
}
