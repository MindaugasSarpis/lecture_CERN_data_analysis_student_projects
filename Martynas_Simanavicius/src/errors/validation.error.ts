import { BaseError } from './base.error';

export class ValidationError extends BaseError {
  statusCode = 400;

  constructor(message: string = 'Validation error') {
    super(message);
  }
}
