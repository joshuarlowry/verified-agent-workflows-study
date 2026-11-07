import { useState } from "react";
import { authClient, readAuthErrorMessage } from "../auth-client.js";
import { APP_NAME } from "../../shared/domain.js";

type Mode = "signin" | "signup";

const SEED_ACCOUNT_HINTS = [
  "ada@workboard.test (owner of Apollo Launch)",
  "bruno@workboard.test (member in both workspaces)",
  "cleo@workboard.test (member of Borealis Ops only)",
];

export default function AuthPanel() {
  const [mode, setMode] = useState<Mode>("signin");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      if (mode === "signin") {
        const res = await authClient.signIn.email({ email, password });
        if (res.error) {
          setError(readAuthErrorMessage(res.error, "Sign in failed. Check your email and password."));
        }
      } else {
        const res = await authClient.signUp.email({ email, password, name: name || email });
        if (res.error) {
          setError(readAuthErrorMessage(res.error, "Account creation failed."));
        }
      }
    } catch (err: unknown) {
      setError(readAuthErrorMessage(err, "Something went wrong. Please try again."));
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="panel auth-panel" aria-labelledby="auth-heading">
      <h2 id="auth-heading">
        {mode === "signin" ? `Sign in to ${APP_NAME}` : `Create your ${APP_NAME} account`}
      </h2>
      {error ? (
        <p className="banner banner-error" role="alert">
          {error}
        </p>
      ) : null}
      <form onSubmit={(e) => void handleSubmit(e)} noValidate>
        {mode === "signup" ? (
          <div className="field">
            <label htmlFor="auth-name">Name</label>
            <input
              id="auth-name"
              name="name"
              type="text"
              autoComplete="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>
        ) : null}
        <div className="field">
          <label htmlFor="auth-email">Email</label>
          <input
            id="auth-email"
            name="email"
            type="email"
            autoComplete="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>
        <div className="field">
          <label htmlFor="auth-password">Password</label>
          <input
            id="auth-password"
            name="password"
            type="password"
            autoComplete={mode === "signin" ? "current-password" : "new-password"}
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>
        <button type="submit" className="btn btn-primary" disabled={busy}>
          {busy ? "Working…" : mode === "signin" ? "Sign in" : "Create account"}
        </button>
      </form>
      <p style={{ marginTop: "0.75rem" }}>
        {mode === "signin" ? (
          <button type="button" className="btn" onClick={() => { setMode("signup"); setError(null); }}>
            Need an account? Create one
          </button>
        ) : (
          <button type="button" className="btn" onClick={() => { setMode("signin"); setError(null); }}>
            Already have an account? Sign in
          </button>
        )}
      </p>
      <div className="demo-hint panel" style={{ margin: 0, padding: "0.75rem" }}>
        <p className="muted" style={{ margin: 0 }}>
          Seeded demo accounts (password pattern, e.g. <code>ada-passphrase-01</code>):
        </p>
        <ul>
          {SEED_ACCOUNT_HINTS.map((hint) => (
            <li key={hint} className="muted">
              {hint}
            </li>
          ))}
        </ul>
      </div>
    </main>
  );
}
