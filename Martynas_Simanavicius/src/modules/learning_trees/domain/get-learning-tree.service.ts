import { AppDataSource } from '../../../data-source';
import { LearningTree } from '../models/learning-tree.entity';
import { NotFoundError } from '../../../errors';

export class GetLearningTreeService {
  async run(uuid: string): Promise<LearningTree> {
    const learningTreeRepository = AppDataSource.getRepository(LearningTree);

    const learningTree = await learningTreeRepository.findOne({
      where: { uuid },
    });

    if (!learningTree) {
      throw new NotFoundError('Learning tree not found');
    }

    return learningTree;
  }
}
