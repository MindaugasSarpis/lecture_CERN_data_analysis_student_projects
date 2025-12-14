import { Request, Response } from 'express';
import { CreateLearningTreeNodeService } from '../domain/create-learning-tree-node.service';
import { GetLearningTreeNodeService } from '../domain/get-learning-tree-node.service';
import { ListLearningTreeNodesService } from '../domain/list-learning-tree-nodes.service';
import { UpdateLearningTreeNodeService } from '../domain/update-learning-tree-node.service';
import { DeleteLearningTreeNodeService } from '../domain/delete-learning-tree-node.service';
import { BaseError, ValidationError } from '../../../errors';

export class LearningTreeNodesController {
  async create(req: Request, res: Response): Promise<void> {
    try {
      const { name, description, video_file_name, learning_tree_id } = req.body;

      if (!name) {
        throw new ValidationError('Missing required field: name');
      }

      if (!learning_tree_id) {
        throw new ValidationError('Missing required field: learning_tree_id');
      }

      const createLearningTreeNodeService = new CreateLearningTreeNodeService();
      const learningTreeNode = await createLearningTreeNodeService.run({
        name,
        description,
        video_file_name,
        learning_tree_id,
      });

      res.status(201).json({
        uuid: learningTreeNode.uuid,
        name: learningTreeNode.name,
        description: learningTreeNode.description,
        video_file_name: learningTreeNode.video_file_name,
        learning_tree_id: learningTreeNode.learning_tree_id,
        createdAt: learningTreeNode.createdAt,
        updatedAt: learningTreeNode.updatedAt,
      });
    } catch (error) {
      if (error instanceof BaseError) {
        res.status(error.statusCode).json({ error: error.message });
      } else if (error instanceof Error) {
        res.status(500).json({ error: error.message });
      } else {
        res.status(500).json({ error: 'Internal server error' });
      }
    }
  }

  async getOne(req: Request, res: Response): Promise<void> {
    try {
      const { uuid } = req.params;

      if (!uuid) {
        throw new ValidationError('Missing required parameter: uuid');
      }

      const getLearningTreeNodeService = new GetLearningTreeNodeService();
      const learningTreeNode = await getLearningTreeNodeService.run(uuid);

      res.status(200).json({
        uuid: learningTreeNode.uuid,
        name: learningTreeNode.name,
        description: learningTreeNode.description,
        video_file_name: learningTreeNode.video_file_name,
        learning_tree_id: learningTreeNode.learning_tree_id,
        createdAt: learningTreeNode.createdAt,
        updatedAt: learningTreeNode.updatedAt,
      });
    } catch (error) {
      if (error instanceof BaseError) {
        res.status(error.statusCode).json({ error: error.message });
      } else if (error instanceof Error) {
        res.status(500).json({ error: error.message });
      } else {
        res.status(500).json({ error: 'Internal server error' });
      }
    }
  }

  async list(req: Request, res: Response): Promise<void> {
    try {
      const { learning_tree_id } = req.query;

      const filters: any = {};
      if (learning_tree_id) {
        filters.learning_tree_id = parseInt(learning_tree_id as string, 10);
      }

      const listLearningTreeNodesService = new ListLearningTreeNodesService();
      const learningTreeNodes = await listLearningTreeNodesService.run(
        Object.keys(filters).length > 0 ? filters : undefined
      );

      res.status(200).json(
        learningTreeNodes.map((node) => ({
          uuid: node.uuid,
          name: node.name,
          description: node.description,
          video_file_name: node.video_file_name,
          learning_tree_id: node.learning_tree_id,
          createdAt: node.createdAt,
          updatedAt: node.updatedAt,
        }))
      );
    } catch (error) {
      if (error instanceof BaseError) {
        res.status(error.statusCode).json({ error: error.message });
      } else if (error instanceof Error) {
        res.status(500).json({ error: error.message });
      } else {
        res.status(500).json({ error: 'Internal server error' });
      }
    }
  }

  async update(req: Request, res: Response): Promise<void> {
    try {
      const { uuid } = req.params;
      const { name, description, video_file_name } = req.body;

      if (!uuid) {
        throw new ValidationError('Missing required parameter: uuid');
      }

      const updateLearningTreeNodeService = new UpdateLearningTreeNodeService();
      const learningTreeNode = await updateLearningTreeNodeService.run(uuid, {
        name,
        description,
        video_file_name,
      });

      res.status(200).json({
        uuid: learningTreeNode.uuid,
        name: learningTreeNode.name,
        description: learningTreeNode.description,
        video_file_name: learningTreeNode.video_file_name,
        learning_tree_id: learningTreeNode.learning_tree_id,
        createdAt: learningTreeNode.createdAt,
        updatedAt: learningTreeNode.updatedAt,
      });
    } catch (error) {
      if (error instanceof BaseError) {
        res.status(error.statusCode).json({ error: error.message });
      } else if (error instanceof Error) {
        res.status(500).json({ error: error.message });
      } else {
        res.status(500).json({ error: 'Internal server error' });
      }
    }
  }

  async delete(req: Request, res: Response): Promise<void> {
    try {
      const { uuid } = req.params;

      if (!uuid) {
        throw new ValidationError('Missing required parameter: uuid');
      }

      const deleteLearningTreeNodeService = new DeleteLearningTreeNodeService();
      await deleteLearningTreeNodeService.run(uuid);

      res.status(200).json({
        message: 'Learning tree node deleted successfully',
      });
    } catch (error) {
      if (error instanceof BaseError) {
        res.status(error.statusCode).json({ error: error.message });
      } else if (error instanceof Error) {
        res.status(500).json({ error: error.message });
      } else {
        res.status(500).json({ error: 'Internal server error' });
      }
    }
  }
}
