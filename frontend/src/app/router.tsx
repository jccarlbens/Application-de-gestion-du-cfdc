import { createBrowserRouter } from 'react-router-dom'
import { HomePage } from '../pages/home'
import { SetPasswordPage } from '../pages/set-password'

export const router = createBrowserRouter([
  { path: '/', element: <HomePage /> },
  // Ouverte depuis le lien reçu par email, sans connexion (US-002).
  { path: '/mot-de-passe', element: <SetPasswordPage /> },
])
