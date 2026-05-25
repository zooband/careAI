const API_BASE = '/api'

export async function fetchScenarios() {
  const res = await fetch(`${API_BASE}/scenarios`)
  return res.json()
}

export async function reviewContent(text) {
  const res = await fetch(`${API_BASE}/review-content`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text }),
  })
  return res.json()
}

export async function generateVideo({ scenarioId, reminderType, caregiverText }) {
  const res = await fetch(`${API_BASE}/generate-video`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      scenario_id: scenarioId,
      reminder_type: reminderType,
      caregiver_text: caregiverText,
    }),
  })
  return res.json()
}

export async function generateCareReminder({ profileText, prompt }) {
  const res = await fetch(`${API_BASE}/generate-care-reminder`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ profile_text: profileText, prompt }),
  })
  return res.json()
}
