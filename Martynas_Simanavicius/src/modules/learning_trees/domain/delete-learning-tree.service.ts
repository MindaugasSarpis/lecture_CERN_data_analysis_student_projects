import { AppDataSource } from '../../../data-source';
import { LearningTree } from '../models/learning-tree.entity';
import { NotFoundError } from '../../../errors';

export class DeleteLearningTreeService {
  async run(uuid: string): Promise<void> {
    const learningTreeRepository = AppDataSource.getRepository(LearningTree);

    const learningTree = await learningTreeRepository.findOne({
      where: { uuid },
    });

    if (!learningTree) {
      throw new NotFoundError('Learning tree not found');
    }

    await learningTreeRepository.remove(learningTree);
  }
}
