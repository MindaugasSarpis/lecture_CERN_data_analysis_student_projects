import { Request, Response } from 'express';
import { CreateUserService } from '../domain/create-user.service';
import { LoginUserService } from '../domain/login-user.service';
import { BaseError, ValidationError } from '../../../errors';

export class AuthController {
  async register(req: Request, res: Response): Promise<void> {
    try {
      const { email, password, username } = req.body;

      // Validate required fields
      if (!email || !password || !username) {
        throw new ValidationError('Missing required fields: email, password, username');
      }

      // Create user using the interactor
      const createUserService = new CreateUserService();
      const user = await createUserService.run({
        username,
        email,
        password,
      });

      // Return success response (excluding password)
      res.status(201).json({
        uuid: user.uuid,
        email: user.email,
        username: user.username,
        createdAt: user.createdAt,
      });
    } catch (error) {
      if (error instanceof BaseError) {
        res.status(error.statusCode).json({ error: error.message });
      } else if (error instanceof Error) {
        res.status(500).json({ error: error.message });
      } else {
        res.status(500).json({ error: 'Internal server error' });
      }
    }
  }

  async login(req: Request, res: Response): Promise<void> {
    try {
      const { email, password } = req.body;

      // Validate required fields
      if (!email || !password) {
        throw new ValidationError('Missing required fields: email, password');
      }

      // Login user using the interactor
      const loginUserService = new LoginUserService();
      const result = await loginUserService.run({
        email,
        password,
      });

      // Return success response with access token
      res.status(200).json(result);
    } catch (error) {
      if (error instanceof BaseError) {
        res.status(error.statusCode).json({ error: error.message });
      } else if (error instanceof Error) {
        res.status(500).json({ error: error.message });
      } else {
        res.status(500).json({ error: 'Internal server error' });
      }
    }
  }
}
