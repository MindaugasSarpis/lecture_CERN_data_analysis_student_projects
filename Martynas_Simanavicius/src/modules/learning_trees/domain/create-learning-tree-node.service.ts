import { AppDataSource } from '../../../data-source';
import { LearningTreeNode } from '../models/learning-tree-node.entity';
import { ValidationError } from '../../../errors';

export interface CreateLearningTreeNodeInput {
  name: string;
  description?: string;
  video_file_name?: string;
  learning_tree_id: number;
}

export class CreateLearningTreeNodeService {
  async run(input: CreateLearningTreeNodeInput): Promise<LearningTreeNode> {
    const learningTreeNodeRepository = AppDataSource.getRepository(LearningTreeNode);

    const learningTreeNode = learningTreeNodeRepository.create({
      name: input.name,
      description: input.description || null,
      video_file_name: input.video_file_name || null,
      learning_tree_id: input.learning_tree_id,
    });

    await learningTreeNodeRepository.save(learningTreeNode);

    return learningTreeNode;
  }
}
