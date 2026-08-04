import { NavLink } from "react-router-dom";

const navLinkClass = ({ isActive }) =>
  `text-sm font-medium transition-colors ${
    isActive ? "text-purple-600" : "text-gray-500 hover:text-gray-900"
  }`;

function Navbar() {
  return (
    <header className="sticky top-0 z-50 border-b border-gray-200/80 bg-white/80 backdrop-blur-md">
      <nav className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <NavLink to="/" className="flex items-center gap-2 text-xl font-bold text-gray-900">
          <span className="text-2xl">🎵😂</span>
          <span>
            MemeSync <span className="text-purple-600">AI</span>
          </span>
        </NavLink>

        <div className="flex items-center gap-8">
          <NavLink to="/upload" className={navLinkClass}>
            Upload
          </NavLink>
          <NavLink to="/gallery" className={navLinkClass}>
            Gallery
          </NavLink>

          <NavLink
            to="/upload"
            className="rounded-lg bg-gray-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-gray-700"
          >
            Get Started
          </NavLink>
        </div>
      </nav>
    </header>
  );
}

export default Navbar;
