import { rolesLabel, toViewer } from '../../src/entities/viewer'
import { MENU, menuFor } from '../../src/widgets/app-shell'

const labels = (roles: Parameters<typeof menuFor>[0]) => menuFor(roles).map((item) => item.label)

describe('menuFor', () => {
  it("donne au formateur seulement « Mes modules »", () => {
    expect(labels(['trainer'])).toEqual(['Mes modules'])
  })

  it("donne à l'administrateur tout sauf « Mes modules »", () => {
    expect(labels(['it_admin'])).toEqual(MENU.filter((m) => m.key !== 'mes-modules').map((m) => m.label))
  })

  it('donne à la secrétaire les menus de consultation et de saisie, sans comptes ni vue d’ensemble', () => {
    expect(labels(['secretary'])).toEqual([
      'Formations',
      'Demandes de formation',
      'Sessions et calendrier',
      'Participants',
    ])
  })

  it('donne au coordonnateur les comptes et la vue d’ensemble', () => {
    expect(labels(['coordinator'])).toContain('Comptes')
    expect(labels(['coordinator'])).toContain("Vue d'ensemble")
    expect(labels(['coordinator'])).not.toContain('Documents de cours')
  })

  it("fait l'union des menus pour plusieurs rôles, sans doublon et dans l'ordre", () => {
    expect(labels(['trainer', 'direction'])).toEqual([
      'Formations',
      'Mes modules',
      'Demandes de formation',
      'Sessions et calendrier',
      'Participants',
      "Vue d'ensemble",
    ])
  })

  it('ne donne rien sans rôle', () => {
    expect(menuFor([])).toEqual([])
  })
})

describe('rolesLabel et toViewer', () => {
  it('écrit les rôles en français, dans un ordre fixe', () => {
    expect(rolesLabel(['trainer', 'secretary'])).toBe('Secrétaire, Formateur')
    expect(rolesLabel(['it_admin', 'service_head', 'direction', 'coordinator'])).toBe(
      'Coordonnateur, Chef de service du CFDC, Administrateur informatique, Direction du CFDC',
    )
  })

  it('assemble le nom complet et ignore un rôle inconnu', () => {
    expect(toViewer({ badge: 'B07-42', first_name: 'Marie', last_name: 'Joseph', roles: ['trainer', 'pilote'] })).toEqual({
      badge: 'B07-42',
      fullName: 'Marie Joseph',
      roles: ['trainer'],
    })
  })
})
