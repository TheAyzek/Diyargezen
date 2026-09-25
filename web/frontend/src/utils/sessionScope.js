// Storage partitioning is not encryption or a replacement for server authorization.
export function captureSession() {
  const token = localStorage.getItem('token') || '';
  const username = localStorage.getItem('username') || '';
  const generation = localStorage.getItem('sessionGeneration') || '';
  const guest = localStorage.getItem('isGuest') === 'true';
  const authenticated = !!token && token !== 'offline-guest-token' && !!username;
  const owner = authenticated ? `account:${username}` : 'guest';
  return { token, owner, authenticated, key: JSON.stringify([token, username, generation, guest]) };
}

export function isCurrentSession(session) {
  return session.key === captureSession().key;
}

export function assertSession(session) {
  if (!isCurrentSession(session)) throw new Error('Oturum değişti; eski işlem iptal edildi.');
}

export function rotateSession() {
  localStorage.setItem('sessionGeneration', crypto.randomUUID());
}
