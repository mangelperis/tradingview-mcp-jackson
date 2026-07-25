import { register } from '../router.js';
import * as core from '../../core/watchlist.js';
import * as morning from '../../core/morning.js';

register('watchlist', {
  description: 'Watchlist tools (get, add, sync)',
  subcommands: new Map([
    ['get', {
      description: 'Get watchlist symbols',
      handler: () => core.get(),
    }],
    ['add', {
      description: 'Add a symbol to the watchlist',
      handler: (opts, positionals) => {
        if (!positionals[0]) throw new Error('Symbol required. Usage: tv watchlist add AAPL');
        return core.add({ symbol: positionals[0] });
      },
    }],
    ['sync', {
      description: 'Replace rules.json watchlist from the live TradingView list (refuses empty)',
      options: {
        rules: {
          type: 'string',
          short: 'r',
          description: 'Path to rules.json (default: project rules.json)',
        },
      },
      handler: async ({ rules }) => morning.syncWatchlistToRules({ rules_path: rules }),
    }],
  ]),
});
