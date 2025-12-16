import { AppDataSource } from '../../../data-source';
import { LearningTreeNode } from '../models/learning-tree-node.entity';
import { NotFoundError } from '../../../errors';

export class DeleteLearningTreeNodeService {
  async run(uuid: string): Promise<void> {
    const learningTreeNodeRepository = AppDataSource.getRepository(LearningTreeNode);

    const learningTreeNode = await learningTreeNodeRepository.findOne({
      where: { uuid },
    });

    if (!learningTreeNode) {
      throw new NotFoundError('Learning tree node not found');
    }

    await learningTreeNodeRepository.remove(learningTreeNode);
  }
}
