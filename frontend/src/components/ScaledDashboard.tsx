import { useEffect, useRef, useState, type ReactNode } from "react";

const DESIGN_WIDTH = 896;

interface ScaledDashboardProps {
  children: ReactNode;
}

export default function ScaledDashboard({ children }: ScaledDashboardProps) {
  const outerRef = useRef<HTMLDivElement>(null);
  const innerRef = useRef<HTMLDivElement>(null);
  const [scale, setScale] = useState(1);
  const [innerHeight, setInnerHeight] = useState(0);

  useEffect(() => {
    const outer = outerRef.current;
    const inner = innerRef.current;
    if (!outer || !inner) return;

    const update = () => {
      const width = outer.offsetWidth;
      setScale(width / DESIGN_WIDTH);
      setInnerHeight(inner.offsetHeight);
    };

    update();

    const observer = new ResizeObserver(update);
    observer.observe(outer);
    observer.observe(inner);

    return () => observer.disconnect();
  }, []);

  return (
    <div ref={outerRef} style={{ height: innerHeight * scale }}>
      <div
        ref={innerRef}
        style={{
          width: DESIGN_WIDTH,
          transform: `scale(${scale})`,
          transformOrigin: "top left",
        }}
      >
        {children}
      </div>
    </div>
  );
}
