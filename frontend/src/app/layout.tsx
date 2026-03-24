// 渲染应用根布局，并注入全局样式与页面元信息。
import type { Metadata } from "next";
import "./globals.css";
import { Geist } from "next/font/google";
import { cn } from "@/lib/utils";

const geist = Geist({subsets:['latin'],variable:'--font-sans'});

export const metadata: Metadata = {
  title: "Baby Growth Archive",
  description: "Private family baby growth archive app",
};

// 包裹所有页面内容，作为前端应用的根布局入口。
export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN" className={cn("font-sans", geist.variable)}>
      <body>{children}</body>
    </html>
  );
}
