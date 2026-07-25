import { register } from '../router.js';
import * as core from '../../core/health.js';

register('status', {
  description: 'Check CDP connection to TradingView',
  handler: () => core.healthCheck(),
});

register('launch', {
  description: 'Launch TradingView with CDP, or reuse if already running on the port',
  options: {
    port: { type: 'string', short: 'p', description: 'CDP port (default TV_CDP_PORT or 9223)' },
    'no-kill': { type: 'boolean', description: 'Do not kill existing instances when starting fresh' },
    'force-restart': { type: 'boolean', description: 'Kill and relaunch even if CDP is already healthy' },
  },
  handler: (opts) => core.launch({
    port: opts.port ? Number(opts.port) : undefined,
    kill_existing: !opts['no-kill'],
    force_restart: !!opts['force-restart'],
  }),
});
