import { Link } from "react-router-dom";

function Footer() {
  return (
    <footer className="border-t border-gray-200 bg-gray-50">
      <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 px-6 py-8 sm:flex-row">
        <div className="flex items-center gap-2 text-lg font-bold text-gray-900">
          <span>🎵😂</span>
          <span>
            MemeSync <span className="text-purple-600">AI</span>
          </span>
        </div>

        <nav className="flex gap-6 text-sm text-gray-500">
          <Link to="/" className="hover:text-gray-900">
            Home
          </Link>
          <Link to="/upload" className="hover:text-gray-900">
            Upload
          </Link>
          <Link to="/gallery" className="hover:text-gray-900">
            Gallery
          </Link>
        </nav>

        <p className="text-sm text-gray-400">
          © {new Date().getFullYear()} MemeSync AI. All rights reserved.
        </p>
      </div>
    </footer>
  );
}

export default Footer;
