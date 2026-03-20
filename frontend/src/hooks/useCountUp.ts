import { useEffect, useRef, useState } from 'react';

/**
 * Animates a number from 0 to target using ease-out cubic.
 * Re-runs whenever target changes.
 */
export function useCountUp(target: number, duration = 1100): number {
  const [value, setValue] = useState(0);
  const raf  = useRef<number>(0);
  const t0   = useRef<number>(0);

  useEffect(() => {
    if (target === 0) { setValue(0); return; }
    t0.current = performance.now();

    function tick(now: number) {
      const p = Math.min((now - t0.current) / duration, 1);
      const eased = 1 - Math.pow(1 - p, 3);          // cubic ease-out
      setValue(Math.round(target * eased));
      if (p < 1) raf.current = requestAnimationFrame(tick);
    }

    raf.current = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf.current);
  }, [target, duration]);

  return value;
}
