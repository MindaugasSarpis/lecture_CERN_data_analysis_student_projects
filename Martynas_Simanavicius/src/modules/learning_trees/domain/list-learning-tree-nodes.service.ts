import { AppDataSource } from '../../../data-source';
import { LearningTreeNode } from '../models/learning-tree-node.entity';

export interface ListLearningTreeNodesFilters {
  learning_tree_id?: number;
}

export class ListLearningTreeNodesService {
  async run(filters?: ListLearningTreeNodesFilters): Promise<LearningTreeNode[]> {
    const learningTreeNodeRepository = AppDataSource.getRepository(LearningTreeNode);

    const where: any = {};
    if (filters?.learning_tree_id) {
      where.learning_tree_id = filters.learning_tree_id;
    }

    const learningTreeNodes = await learningTreeNodeRepository.find({
      where,
      order: { createdAt: 'DESC' },
    });

    return learningTreeNodes;
  }
}
