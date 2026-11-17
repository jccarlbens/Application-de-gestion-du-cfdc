import { createBrowserRouter } from 'react-router-dom'
import { HomePage } from '../pages/home'
import { LoginPage } from '../pages/login'
import { SetPasswordPage } from '../pages/set-password'

export const router = createBrowserRouter([
  // Ramène à /connexion si personne n'est connecté (US-004).
  { path: '/', element: <HomePage /> },
  { path: '/connexion', element: <LoginPage /> },
  // Ouverte depuis le lien reçu par email, sans connexion (US-002).
  { path: '/mot-de-passe', element: <SetPasswordPage /> },
])
