import { screen } from '@testing-library/react'
import { DocumentsPage } from '../../src/pages/documents'
import { json, me, renderApp } from './renderApp'

function doc(overrides: Record<string, unknown> = {}) {
  return {
    id: 'd-1', module_id: 'm-1', module_title: 'Vitesses', training_id: 't-1', training_title: 'Conduite sur la rampe',
    file_name: 'Cours.pdf', content_type: 'application/pdf', size_bytes: 1024 * 1024,
    uploaded_by_name: 'Ada Admin (Z01-01)', uploaded_at: '2026-11-20T10:00:00Z', replaced_by_id: null, ...overrides,
  }
}

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('DocumentsPage', () => {
  it('regroupe les documents en vigueur par formation et par module', async () => {
    renderApp(<DocumentsPage />, {
      at: '/documents', path: '/documents',
      responses: {
        '/auth/me': () => json(me(['it_admin'])),
        '/documents': () => json([
          doc(),
          doc({ id: 'd-2', file_name: 'Annexe.pptx' }),
          doc({ id: 'd-0', file_name: 'Ancien.pdf', replaced_by_id: 'd-1' }),
          doc({ id: 'd-3', module_id: 'm-9', module_title: 'Protocole', training_id: 't-2', training_title: 'Accueil VIP' }),
        ]),
      },
    })
    expect(await screen.findByRole('link', { name: 'Conduite sur la rampe' })).toHaveAttribute('href', '/formations/t-1')
    expect(screen.getByRole('link', { name: 'Accueil VIP' })).toHaveAttribute('href', '/formations/t-2')
    expect(screen.getByRole('link', { name: 'Annexe.pptx' })).toHaveAttribute('href', '/api/v1/documents/d-2/download')
    expect(screen.queryByText('Ancien.pdf')).not.toBeInTheDocument()
    expect(screen.getByText('1 version remplacée : sur la fiche de chaque formation.')).toBeInTheDocument()
  })

  it("n'est ouverte qu'à l'administrateur", async () => {
    renderApp(<DocumentsPage />, { at: '/documents', path: '/documents', responses: { '/auth/me': () => json(me(['coordinator'])) } })
    expect(await screen.findByText("Vous n'avez pas accès à cette page.")).toBeInTheDocument()
  })
})
