import { createBrowserRouter } from 'react-router-dom'
import { HomePage } from '../pages/home'
import { LoginPage } from '../pages/login'
import { SectionPage } from '../pages/section'
import { SetPasswordPage } from '../pages/set-password'
import { MENU } from '../widgets/app-shell'

export const router = createBrowserRouter([
  // Pages réservées aux personnes connectées : sans session, retour à /connexion.
  { path: '/', element: <HomePage /> },
  // Une page par menu (US-007) ; chacune deviendra un vrai écran.
  ...MENU.map((item) => ({ path: item.path, element: <SectionPage menuKey={item.key} /> })),
  // Pages ouvertes.
  { path: '/connexion', element: <LoginPage /> },
  { path: '/mot-de-passe', element: <SetPasswordPage /> },
])
