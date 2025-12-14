import { AppDataSource } from '../../../data-source';
import { LearningTreeNode } from '../models/learning-tree-node.entity';
import { NotFoundError } from '../../../errors';

export class GetLearningTreeNodeService {
  async run(uuid: string): Promise<LearningTreeNode> {
    const learningTreeNodeRepository = AppDataSource.getRepository(LearningTreeNode);

    const learningTreeNode = await learningTreeNodeRepository.findOne({
      where: { uuid },
    });

    if (!learningTreeNode) {
      throw new NotFoundError('Learning tree node not found');
    }

    return learningTreeNode;
  }
}
