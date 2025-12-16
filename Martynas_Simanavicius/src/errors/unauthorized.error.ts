import { BaseError } from './base.error';

export class UnauthorizedError extends BaseError {
  statusCode = 401;

  constructor(message: string = 'Unauthorized') {
    super(message);
  }
}
