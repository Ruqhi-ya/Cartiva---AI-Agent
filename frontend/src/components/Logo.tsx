export function Logo({ size = "md" }: { size?: "sm" | "md" }) {
  const text = size === "sm" ? "text-lg" : "text-xl";
  return (
    <div className="flex items-center gap-2">
      <span className="flex h-8 w-8 items-center justify-center rounded-xl bg-primary text-white font-extrabold">
        C
      </span>
      <span className={`font-extrabold tracking-tight text-ink ${text}`}>
        Cartiva
      </span>
    </div>
  );
}
