import { createBrowserRouter } from 'react-router-dom'
import { AccountPage } from '../pages/account'
import { NewAccountPage } from '../pages/account-new'
import { AccountsPage } from '../pages/accounts'
import { DocumentsPage } from '../pages/documents'
import { DomainsPage } from '../pages/domains'
import { HomePage } from '../pages/home'
import { LoginPage } from '../pages/login'
import { SectionPage } from '../pages/section'
import { SetPasswordPage } from '../pages/set-password'
import { TrainingPage } from '../pages/training'
import { NewTrainingPage } from '../pages/training-new'
import { TrainingsPage } from '../pages/trainings'
import { MENU } from '../widgets/app-shell'

// Les menus dont l'écran existe déjà ; les autres mènent à « Bientôt disponible ».
const BUILT = new Set(['comptes', 'formations', 'documents'])

export const router = createBrowserRouter([
  // Pages réservées aux personnes connectées : sans session, retour à /connexion.
  { path: '/', element: <HomePage /> },
  { path: '/comptes', element: <AccountsPage /> },
  { path: '/comptes/nouveau', element: <NewAccountPage /> },
  { path: '/comptes/:badge', element: <AccountPage /> },
  { path: '/formations', element: <TrainingsPage /> },
  { path: '/formations/nouvelle', element: <NewTrainingPage /> },
  { path: '/formations/domaines', element: <DomainsPage /> },
  { path: '/formations/:id', element: <TrainingPage /> },
  { path: '/documents', element: <DocumentsPage /> },
  ...MENU.filter((item) => !BUILT.has(item.key)).map((item) => ({
    path: item.path,
    element: <SectionPage menuKey={item.key} />,
  })),
  // Pages ouvertes.
  { path: '/connexion', element: <LoginPage /> },
  { path: '/mot-de-passe', element: <SetPasswordPage /> },
])
