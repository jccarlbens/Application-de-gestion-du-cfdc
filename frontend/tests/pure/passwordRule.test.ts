import { checkPassword } from '../../src/pages/set-password/model/passwordRule'

describe('checkPassword', () => {
  it('accepte 8 caractères dont un chiffre, confirmés', () => {
    expect(checkPassword('formation2026', 'formation2026')).toBeNull()
  })

  it.each(['court1', 'sanschiffre', ''])('refuse « %s »', (password) => {
    expect(checkPassword(password, password)).toMatch(/au moins 8 caractères/)
  })

  it('refuse une confirmation différente', () => {
    expect(checkPassword('formation2026', 'formation2027')).toBe('Les deux mots de passe ne sont pas identiques.')
  })
})
