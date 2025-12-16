import { AppDataSource } from '../../../data-source';
import { UserVideo } from '../models/user-video.entity';
import { NotFoundError } from '../../../errors';

export class GetUserVideoService {
  async run(uuid: string): Promise<UserVideo> {
    const userVideoRepository = AppDataSource.getRepository(UserVideo);

    const userVideo = await userVideoRepository.findOne({
      where: { uuid },
    });

    if (!userVideo) {
      throw new NotFoundError('User video not found');
    }

    return userVideo;
  }
}
