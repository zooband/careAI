/**
 * Simple auth store using localStorage.
 */
const STORAGE_KEY = 'qinban_auth'

export function login(role, user) {
  const data = { role, user, loggedInAt: Date.now() }
  localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
  return data
}

export function logout() {
  localStorage.removeItem(STORAGE_KEY)
}

export function getAuth() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY))
  } catch {
    return null
  }
}

export function isLoggedIn() {
  return getAuth() !== null
}

export function requireAuth(role) {
  const auth = getAuth()
  if (!auth) return false
  if (role && auth.role !== role) return false
  return true
}
