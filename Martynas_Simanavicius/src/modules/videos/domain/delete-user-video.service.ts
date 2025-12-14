import { AppDataSource } from '../../../data-source';
import { UserVideo } from '../models/user-video.entity';
import { NotFoundError } from '../../../errors';

export class DeleteUserVideoService {
  async run(uuid: string): Promise<void> {
    const userVideoRepository = AppDataSource.getRepository(UserVideo);

    const userVideo = await userVideoRepository.findOne({
      where: { uuid },
    });

    if (!userVideo) {
      throw new NotFoundError('User video not found');
    }

    await userVideoRepository.remove(userVideo);
  }
}
