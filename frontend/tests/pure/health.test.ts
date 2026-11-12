import { toHealth } from '../../src/pages/home/api/health'

describe('toHealth', () => {
  it('traduit une base joignable', () => {
    expect(toHealth({ status: 'ok', database: 'reachable' })).toEqual({ isDatabaseReachable: true })
  })

  it('traduit une base injoignable', () => {
    expect(toHealth({ status: 'ok', database: 'unreachable' })).toEqual({ isDatabaseReachable: false })
  })
})
