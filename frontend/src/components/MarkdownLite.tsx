import type { ReactNode } from "react";

interface MarkdownLiteProps {
  text: string;
}

export default function MarkdownLite({ text }: MarkdownLiteProps) {
  const lines = text.split("\n");
  const blocks: ReactNode[] = [];
  let listBuffer: string[] = [];

  const flushList = (key: string) => {
    if (listBuffer.length === 0) return;
    blocks.push(
      <ul key={key} className="ml-4 list-disc space-y-1 text-[13px] leading-relaxed text-white/75">
        {listBuffer.map((item, i) => (
          <li key={i}>{item}</li>
        ))}
      </ul>
    );
    listBuffer = [];
  };

  lines.forEach((line, i) => {
    const trimmed = line.trim();
    if (trimmed.startsWith("### ")) {
      flushList(`l-${i}`);
      blocks.push(
        <h3 key={i} className="mt-3 text-[13px] font-semibold text-white/85">
          {trimmed.slice(4)}
        </h3>
      );
    } else if (trimmed.startsWith("## ")) {
      flushList(`l-${i}`);
      blocks.push(
        <h2 key={i} className="mt-4 text-[14.5px] font-semibold text-[#E08A3C]">
          {trimmed.slice(3)}
        </h2>
      );
    } else if (trimmed.startsWith("# ")) {
      flushList(`l-${i}`);
      blocks.push(
        <h1 key={i} className="text-[16px] font-semibold text-white">
          {trimmed.slice(2)}
        </h1>
      );
    } else if (trimmed.startsWith("- ") || trimmed.startsWith("* ")) {
      listBuffer.push(trimmed.slice(2));
    } else if (trimmed === "") {
      flushList(`l-${i}`);
    } else {
      flushList(`l-${i}`);
      blocks.push(
        <p key={i} className="text-[13px] leading-relaxed text-white/75">
          {trimmed}
        </p>
      );
    }
  });
  flushList("l-end");

  return <div className="space-y-1.5">{blocks}</div>;
}
