import { BaseError } from './base.error';

export class BadRequestError extends BaseError {
  statusCode = 400;

  constructor(message: string = 'Bad request') {
    super(message);
  }
}
