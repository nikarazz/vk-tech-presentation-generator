export function Footer() {
  return (
    <footer className="border-t border-[var(--color-border)] mt-auto">
      <div className="max-w-7xl mx-auto px-6 py-6 text-sm text-[var(--color-text-muted)] flex flex-col md:flex-row items-center justify-between gap-3">
        <div>
          © 2026 · Сделано командой{" "}
          <span className="font-medium text-[var(--color-text)]">
            Understand
          </span>{" "}
          на хакатоне{" "}
          <a
            href="https://i.moscow/hackaton/lct"
            target="_blank"
            rel="noopener noreferrer"
            className="text-[var(--color-vk-primary)] hover:underline"
          >
            ЛЦТ 2026
          </a>
        </div>
        <div className="flex items-center gap-4">
          <a
            href="https://github.com/nikarazz/vk-tech-presentation-generator"
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-[var(--color-vk-primary)] transition-colors"
          >
            GitHub
          </a>
          <a href="#" className="hover:text-[var(--color-vk-primary)] transition-colors">
            Документация
          </a>
          <a href="#" className="hover:text-[var(--color-vk-primary)] transition-colors">
            Архитектура
          </a>
        </div>
      </div>
    </footer>
  );
}
