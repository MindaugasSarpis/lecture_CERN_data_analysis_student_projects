import { AppDataSource } from '../../../data-source';
import { UserVideo } from '../models/user-video.entity';
import { NotFoundError } from '../../../errors';

export interface UpdateUserVideoInput {
  video_file_name?: string;
  learning_tree_node_id?: number;
}

export class UpdateUserVideoService {
  async run(uuid: string, input: UpdateUserVideoInput): Promise<UserVideo> {
    const userVideoRepository = AppDataSource.getRepository(UserVideo);

    const userVideo = await userVideoRepository.findOne({
      where: { uuid },
    });

    if (!userVideo) {
      throw new NotFoundError('User video not found');
    }

    if (input.video_file_name !== undefined) {
      userVideo.video_file_name = input.video_file_name;
    }
    if (input.learning_tree_node_id !== undefined) {
      userVideo.learning_tree_node_id = input.learning_tree_node_id;
    }

    await userVideoRepository.save(userVideo);

    return userVideo;
  }
}
