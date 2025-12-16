import { AppDataSource } from '../../../data-source';
import { User } from '../models/user.entity';
import bcrypt from 'bcryptjs';
import { ConflictError } from '../../../errors';

export interface CreateUserInput {
  username: string;
  email: string;
  password: string;
}

export class CreateUserService {
  async run(input: CreateUserInput): Promise<User> {
    const userRepository = AppDataSource.getRepository(User);

    // Check if user already exists by email or username
    const existingUser = await userRepository.findOne({
      where: [{ email: input.email }, { username: input.username }],
    });

    if (existingUser) {
      throw new ConflictError('User with this email or username already exists');
    }

    // Hash password
    const hashedPassword = await bcrypt.hash(input.password, 10);

    // Create new user
    const user = userRepository.create({
      username: input.username,
      email: input.email,
      password: hashedPassword,
    });

    // Save user to database
    await userRepository.save(user);

    return user;
  }
}
