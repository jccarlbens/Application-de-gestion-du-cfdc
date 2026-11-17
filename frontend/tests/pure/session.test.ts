import { toMe } from '../../src/pages/home/api/session'

describe('toMe', () => {
  it('assemble le nom complet et garde le numéro de badge', () => {
    expect(toMe({ badge: 'B07-42', first_name: 'Marie', last_name: 'Joseph', roles: ['secretary'] })).toEqual({
      badge: 'B07-42',
      fullName: 'Marie Joseph',
    })
  })
})
