
import { useState, useEffect } from 'react';
import { login, loadStoredToken } from '../api/client';

export function useAuth() {
  const [authed, setAuthed] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const t = loadStoredToken();
    if (t) setAuthed(true);
    setLoading(false);
  }, []);

  async function doLogin(u: string, p: string) {
    try {
      setError('');
      await login(u, p);
      setAuthed(true);
    } catch {
      setError('Invalid credentials');
    }
  }

  function doLogout() {
    localStorage.removeItem('rip_token');
    delete (window as any).__token;
    setAuthed(false);
  }

  return { authed, loading, error, doLogin, doLogout };
}
