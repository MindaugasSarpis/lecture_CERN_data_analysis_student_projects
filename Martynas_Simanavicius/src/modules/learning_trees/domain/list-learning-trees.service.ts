import { AppDataSource } from '../../../data-source';
import { LearningTree } from '../models/learning-tree.entity';

export class ListLearningTreesService {
  async run(): Promise<LearningTree[]> {
    const learningTreeRepository = AppDataSource.getRepository(LearningTree);

    const learningTrees = await learningTreeRepository.find({
      order: { createdAt: 'DESC' },
    });

    return learningTrees;
  }
}
