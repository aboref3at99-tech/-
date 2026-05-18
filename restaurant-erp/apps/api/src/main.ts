import { loadEnvironment, securityBaseline } from '@restaurant/config';
import { getHealth } from './modules/health/health.service.js';

const env = loadEnvironment(process.env);
const health = getHealth();

console.log('API bootstrap complete');
console.log('Environment:', env.NODE_ENV);
console.log('Port:', env.API_PORT);
console.log('Security baseline:', securityBaseline);
console.log('Health snapshot:', health);
