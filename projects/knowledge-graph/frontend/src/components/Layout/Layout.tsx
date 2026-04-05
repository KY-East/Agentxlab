import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { LogOut } from "lucide-react";
import { GoogleLogin } from "@react-oauth/google";
import { useAuth } from "../../contexts/AuthContext";
import { useTranslation } from "react-i18next";
import { useState, useRef, useEffect } from "react";

const NAV_ITEMS = [
  { to: "/", key: "discover" },
  { to: "/canvas", key: "canvas" },
  { to: "/debate", key: "debate" },
  { to: "/forum", key: "community" },
] as const;

export default function Layout() {
  const { user, loading, login, logout } = useAuth();
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setMenuOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  const isZh = i18n.language?.startsWith("zh");
  const toggleLang = () => i18n.changeLanguage(isZh ? "en" : "zh");

  return (
    <div className="h-screen flex flex-col bg-[#0a0a0a] text-neutral-200 overflow-hidden">
      <header className="flex items-center justify-between px-6 py-2.5 border-b-2 border-neutral-800 shrink-0">
        <NavLink
          to="/"
          className="font-mono text-sm font-bold uppercase tracking-[0.2em] text-white hover:text-cyan-400 transition-colors"
        >
          [ {t("common.appName")} ]
        </NavLink>

        <div className="flex items-center gap-6">
          <nav className="flex items-center gap-5">
            {NAV_ITEMS.map(({ to, key }) => (
              <NavLink
                key={to}
                to={to}
                end={to === "/"}
                className={({ isActive }) =>
                  `font-mono text-xs uppercase tracking-wider pb-2 -mb-[13px] transition-colors ${
                    isActive
                      ? "border-b-2 border-cyan-400 text-white"
                      : "text-neutral-500 hover:text-white border-b-2 border-transparent"
                  }`
                }
              >
                {t(`nav.${key}`)}
              </NavLink>
            ))}
          </nav>

          <button
            onClick={toggleLang}
            className="font-mono text-xs text-neutral-500 hover:text-white transition-colors"
          >
            {isZh ? (
              <>
                <span className="text-white">ZH</span>
                <span className="mx-1 text-neutral-700">|</span>
                <span>EN</span>
              </>
            ) : (
              <>
                <span>ZH</span>
                <span className="mx-1 text-neutral-700">|</span>
                <span className="text-white">EN</span>
              </>
            )}
          </button>

          {!loading && (
            <div className="relative" ref={menuRef}>
              {user ? (
                <>
                  <button
                    onClick={() => setMenuOpen((v) => !v)}
                    className="flex items-center gap-2 px-2 py-1 hover:bg-neutral-900 transition-colors"
                  >
                    {user.avatar_url ? (
                      <img
                        src={user.avatar_url}
                        alt=""
                        className="w-6 h-6 rounded-sm"
                      />
                    ) : (
                      <div className="w-6 h-6 rounded-sm bg-neutral-800 flex items-center justify-center text-[10px] font-mono font-bold text-cyan-400">
                        {user.display_name.charAt(0).toUpperCase()}
                      </div>
                    )}
                    <span className="hidden md:inline font-mono text-xs text-neutral-400 max-w-[100px] truncate">
                      {user.display_name}
                    </span>
                  </button>

                  {menuOpen && (
                    <div className="absolute right-0 top-full mt-1 w-48 bg-[#0a0a0a] border-2 border-neutral-800 z-50">
                      <div className="px-3 py-2 border-b border-neutral-800">
                        <p className="font-mono text-[10px] uppercase tracking-wider text-neutral-600">{t("nav.points")}</p>
                        <p className="font-mono text-sm font-bold text-cyan-400">
                          {user.points.toLocaleString(i18n.language === "zh" ? "zh-CN" : "en-US")}
                        </p>
                      </div>
                      <button
                        onClick={() => { navigate("/profile"); setMenuOpen(false); }}
                        className="w-full text-left px-3 py-2 font-mono text-xs text-neutral-400 hover:bg-neutral-900 hover:text-white transition-colors"
                      >
                        {t("nav.profile")}
                      </button>
                      <button
                        onClick={() => { logout(); setMenuOpen(false); }}
                        className="w-full text-left px-3 py-2 font-mono text-xs text-red-500 hover:bg-neutral-900 flex items-center gap-2 transition-colors"
                      >
                        <LogOut size={12} />
                        {t("nav.logout")}
                      </button>
                    </div>
                  )}
                </>
              ) : (
                <GoogleLogin
                  onSuccess={(resp) => {
                    if (resp.credential) login(resp.credential);
                  }}
                  size="small"
                  shape="rectangular"
                  theme="filled_black"
                />
              )}
            </div>
          )}
        </div>
      </header>
      <main className="flex-1 min-h-0 overflow-hidden">
        <Outlet />
      </main>
    </div>
  );
}
