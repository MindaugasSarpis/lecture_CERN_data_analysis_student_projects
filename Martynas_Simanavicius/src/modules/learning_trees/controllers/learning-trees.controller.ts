import { Request, Response } from 'express';
import { CreateLearningTreeService } from '../domain/create-learning-tree.service';
import { GetLearningTreeService } from '../domain/get-learning-tree.service';
import { ListLearningTreesService } from '../domain/list-learning-trees.service';
import { UpdateLearningTreeService } from '../domain/update-learning-tree.service';
import { DeleteLearningTreeService } from '../domain/delete-learning-tree.service';
import { BaseError, ValidationError } from '../../../errors';

export class LearningTreesController {
  async create(req: Request, res: Response): Promise<void> {
    try {
      const { name, description } = req.body;

      // Validate required fields
      if (!name) {
        throw new ValidationError('Missing required field: name');
      }

      // Create learning tree using the service
      const createLearningTreeService = new CreateLearningTreeService();
      const learningTree = await createLearningTreeService.run({
        name,
        description,
      });

      // Return success response
      res.status(201).json({
        uuid: learningTree.uuid,
        name: learningTree.name,
        description: learningTree.description,
        createdAt: learningTree.createdAt,
        updatedAt: learningTree.updatedAt,
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

      // Get learning tree using the service
      const getLearningTreeService = new GetLearningTreeService();
      const learningTree = await getLearningTreeService.run(uuid);

      // Return success response
      res.status(200).json({
        uuid: learningTree.uuid,
        name: learningTree.name,
        description: learningTree.description,
        createdAt: learningTree.createdAt,
        updatedAt: learningTree.updatedAt,
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
      // List all learning trees using the service
      const listLearningTreesService = new ListLearningTreesService();
      const learningTrees = await listLearningTreesService.run();

      // Return success response
      res.status(200).json(
        learningTrees.map((tree) => ({
          uuid: tree.uuid,
          name: tree.name,
          description: tree.description,
          createdAt: tree.createdAt,
          updatedAt: tree.updatedAt,
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
      const { name, description } = req.body;

      if (!uuid) {
        throw new ValidationError('Missing required parameter: uuid');
      }

      // Update learning tree using the service
      const updateLearningTreeService = new UpdateLearningTreeService();
      const learningTree = await updateLearningTreeService.run(uuid, {
        name,
        description,
      });

      // Return success response
      res.status(200).json({
        uuid: learningTree.uuid,
        name: learningTree.name,
        description: learningTree.description,
        createdAt: learningTree.createdAt,
        updatedAt: learningTree.updatedAt,
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

      // Delete learning tree using the service
      const deleteLearningTreeService = new DeleteLearningTreeService();
      await deleteLearningTreeService.run(uuid);

      // Return success response
      res.status(200).json({
        message: 'Learning tree deleted successfully',
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
