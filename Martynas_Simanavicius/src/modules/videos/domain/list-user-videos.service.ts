import { AppDataSource } from '../../../data-source';
import { UserVideo } from '../models/user-video.entity';

export interface ListUserVideosFilters {
  user_id?: number;
  learning_tree_node_id?: number;
}

export class ListUserVideosService {
  async run(filters?: ListUserVideosFilters): Promise<UserVideo[]> {
    const userVideoRepository = AppDataSource.getRepository(UserVideo);

    const where: any = {};
    if (filters?.user_id) {
      where.user_id = filters.user_id;
    }
    if (filters?.learning_tree_node_id) {
      where.learning_tree_node_id = filters.learning_tree_node_id;
    }

    const userVideos = await userVideoRepository.find({
      where,
      order: { createdAt: 'DESC' },
    });

    return userVideos;
  }
}
