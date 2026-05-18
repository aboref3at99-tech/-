export interface SecurityBaseline {
  jwtAccessTokenMinutes: number;
  jwtRefreshTokenDays: number;
  maxFailedLoginAttempts: number;
  lockoutMinutes: number;
  bcryptSaltRounds: number;
}

export const securityBaseline: SecurityBaseline = {
  jwtAccessTokenMinutes: 15,
  jwtRefreshTokenDays: 30,
  maxFailedLoginAttempts: 5,
  lockoutMinutes: 15,
  bcryptSaltRounds: 12
};

export interface EnvironmentShape {
  NODE_ENV: 'development' | 'test' | 'production';
  API_PORT: number;
}

export function loadEnvironment(input: NodeJS.ProcessEnv): EnvironmentShape {
  const NODE_ENV = (input.NODE_ENV ?? 'development') as EnvironmentShape['NODE_ENV'];
  const API_PORT = Number(input.API_PORT ?? 4000);

  if (!['development', 'test', 'production'].includes(NODE_ENV)) {
    throw new Error('Invalid NODE_ENV value.');
  }

  if (Number.isNaN(API_PORT) || API_PORT < 1) {
    throw new Error('Invalid API_PORT value.');
  }

  return { NODE_ENV, API_PORT };
}
