import { ApiError, genericMessage } from '../../src/shared/api'

describe('genericMessage', () => {
  it.each([502, 503, 504])('invite à réessayer pour un %i', (status) => {
    expect(genericMessage(status)).toBe('Le serveur est momentanément indisponible. Réessayez dans une minute.')
  })

  it('donne le statut pour les autres erreurs', () => {
    expect(genericMessage(500)).toBe('La requête a échoué (statut 500).')
  })

  it("garde le message du serveur quand il y en a un", () => {
    expect(new ApiError(502, "L'email n'a pas pu être envoyé.").message).toBe("L'email n'a pas pu être envoyé.")
  })
})
