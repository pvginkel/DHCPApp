import { API_BASE_URL } from './config'

export function redirectToLogin(): never {
  const redirectUri = encodeURIComponent(window.location.href)
  window.location.href = `${API_BASE_URL}/auth/login?redirect=${redirectUri}`
  // Throw to halt execution after redirect
  throw new Error('Redirecting to login')
}

export async function checkAuth(): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/auth/self`, {
    credentials: 'same-origin',
  })

  if (response.status === 401) {
    redirectToLogin()
  }

  if (!response.ok) {
    throw new Error(`Auth check failed: ${response.status}`)
  }
}
