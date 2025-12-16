import { BaseError } from './base.error';

export class ConflictError extends BaseError {
  statusCode = 409;

  constructor(message: string = 'Resource conflict') {
    super(message);
  }
}
