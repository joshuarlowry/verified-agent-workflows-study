import { authClient } from "./auth-client.js";
import { APP_NAME } from "../shared/domain.js";
import AuthPanel from "./components/AuthPanel.js";
import Workboard from "./components/Workboard.js";
import type { SessionUser } from "../shared/types.js";

export default function App() {
  // better-auth/react exposes a reactive session store.
  const session = authClient.useSession();

  if (session.isPending) {
    return (
      <main className="app-shell" aria-busy="true">
        <h1>{APP_NAME}</h1>
        <p>Checking your session…</p>
      </main>
    );
  }

  const u = session.data?.user;
  const user: SessionUser | null = u ? { id: u.id, email: u.email, name: u.name } : null;

  return (
    <div className="app-shell">
      <header className="app-header">
        <h1 className="app-title">{APP_NAME}</h1>
        {user ? (
          <div className="header-controls">
            <span className="muted">{user.email}</span>
            <button
              type="button"
              className="btn"
              onClick={() => {
                void authClient.signOut();
              }}
            >
              Sign out
            </button>
          </div>
        ) : null}
      </header>
      {user ? <Workboard /> : <AuthPanel />}
    </div>
  );
}
