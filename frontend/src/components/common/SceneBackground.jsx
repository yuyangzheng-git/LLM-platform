// Full-screen impressionist painting from the Roots & Roads site, washed
// with cream (or dusk in dark mode) so text stays readable, plus paper grain.
export function SceneBackground() {
  return (
    <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none" aria-hidden="true">
      <picture>
        <source media="(max-width: 767px)" srcSet="/background-mobile.jpg" />
        <img
          src="/background.jpg"
          alt=""
          className="absolute inset-0 w-full h-full object-cover object-[center_65%] scale-105"
          style={{ filter: 'var(--scene-filter)' }}
          decoding="async"
        />
      </picture>
      <div
        className="absolute inset-0"
        style={{ background: 'linear-gradient(to bottom, var(--scene-wash-top), var(--scene-wash-bottom))' }}
      />
      <div className="paper-texture absolute inset-0" />
    </div>
  )
}

// Thin terracotta → sunshine → river strip along the bottom edge
export function RainbowRoad() {
  return (
    <div
      className="fixed bottom-0 inset-x-0 h-1 bg-rainbow-road opacity-80 pointer-events-none z-30"
      aria-hidden="true"
    />
  )
}
