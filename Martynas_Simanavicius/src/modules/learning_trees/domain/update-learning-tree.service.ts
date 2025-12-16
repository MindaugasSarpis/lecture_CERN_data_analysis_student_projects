import { AppDataSource } from '../../../data-source';
import { LearningTree } from '../models/learning-tree.entity';
import { NotFoundError } from '../../../errors';

export interface UpdateLearningTreeInput {
  name?: string;
  description?: string;
}

export class UpdateLearningTreeService {
  async run(uuid: string, input: UpdateLearningTreeInput): Promise<LearningTree> {
    const learningTreeRepository = AppDataSource.getRepository(LearningTree);

    const learningTree = await learningTreeRepository.findOne({
      where: { uuid },
    });

    if (!learningTree) {
      throw new NotFoundError('Learning tree not found');
    }

    // Update fields if provided
    if (input.name !== undefined) {
      learningTree.name = input.name;
    }
    if (input.description !== undefined) {
      learningTree.description = input.description;
    }

    // Save updated learning tree
    await learningTreeRepository.save(learningTree);

    return learningTree;
  }
}
