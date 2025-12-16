import { AppDataSource } from '../../../data-source';
import { LearningTreeNode } from '../models/learning-tree-node.entity';
import { NotFoundError } from '../../../errors';

export interface UpdateLearningTreeNodeInput {
  name?: string;
  description?: string;
  video_file_name?: string;
}

export class UpdateLearningTreeNodeService {
  async run(uuid: string, input: UpdateLearningTreeNodeInput): Promise<LearningTreeNode> {
    const learningTreeNodeRepository = AppDataSource.getRepository(LearningTreeNode);

    const learningTreeNode = await learningTreeNodeRepository.findOne({
      where: { uuid },
    });

    if (!learningTreeNode) {
      throw new NotFoundError('Learning tree node not found');
    }

    if (input.name !== undefined) {
      learningTreeNode.name = input.name;
    }
    if (input.description !== undefined) {
      learningTreeNode.description = input.description;
    }
    if (input.video_file_name !== undefined) {
      learningTreeNode.video_file_name = input.video_file_name;
    }

    await learningTreeNodeRepository.save(learningTreeNode);

    return learningTreeNode;
  }
}
