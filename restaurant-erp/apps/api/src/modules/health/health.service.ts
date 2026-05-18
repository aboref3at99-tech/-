import { APP_VERSION, type HealthResponse } from '@restaurant/shared';

export function getHealth(): HealthResponse {
  return {
    service: 'restaurant-api',
    status: 'ok',
    timestamp: new Date().toISOString(),
    version: APP_VERSION
  };
}
