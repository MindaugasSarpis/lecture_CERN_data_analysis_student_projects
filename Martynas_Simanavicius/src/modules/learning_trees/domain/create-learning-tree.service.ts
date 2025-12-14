import { AppDataSource } from '../../../data-source';
import { LearningTree } from '../models/learning-tree.entity';
import { ValidationError } from '../../../errors';

export interface CreateLearningTreeInput {
  name: string;
  description?: string;
}

export class CreateLearningTreeService {
  async run(input: CreateLearningTreeInput): Promise<LearningTree> {
    const learningTreeRepository = AppDataSource.getRepository(LearningTree);

    // Create new learning tree
    const learningTree = learningTreeRepository.create({
      name: input.name,
      description: input.description || null,
    });

    // Save learning tree to database
    await learningTreeRepository.save(learningTree);

    return learningTree;
  }
}
