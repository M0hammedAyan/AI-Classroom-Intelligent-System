// Reticle dev-only SDK — self-guards on import.meta.env.DEV, no-op in prod
import { registerCapabilities } from '@reticlehq/react';

if (import.meta.env.DEV) {
  registerCapabilities({
    testids: [
      'login-email',
      'login-password',
      'login-submit',
      'sidebar-nav',
      'attendance-mark',
      'risk-flag-card',
      'student-list',
      'enroll-face',
    ],
    signals: ['auth:login', 'auth:logout', 'attendance:marked', 'risk:recomputed'],
    stores: [],
  });
}
