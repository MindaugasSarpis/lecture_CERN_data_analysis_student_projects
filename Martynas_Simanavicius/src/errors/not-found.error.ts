import { BaseError } from './base.error';

export class NotFoundError extends BaseError {
  statusCode = 404;

  constructor(message: string = 'Resource not found') {
    super(message);
  }
}
