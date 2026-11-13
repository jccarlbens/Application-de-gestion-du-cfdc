// La règle de NFR.md § Sécurité, vérifiée aussi par le serveur : au moins
// 8 caractères, dont au moins un chiffre. Renvoie le message à afficher, ou null.
export const PASSWORD_RULE = 'Au moins 8 caractères, dont au moins un chiffre.'

export function checkPassword(password: string, confirmation: string): string | null {
  if (password.length < 8 || !/\d/.test(password)) {
    return 'Le mot de passe doit faire au moins 8 caractères, dont au moins un chiffre.'
  }
  if (password !== confirmation) {
    return 'Les deux mots de passe ne sont pas identiques.'
  }
  return null
}
