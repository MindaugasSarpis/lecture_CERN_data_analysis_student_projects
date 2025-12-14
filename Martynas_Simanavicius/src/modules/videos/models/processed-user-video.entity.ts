import { Entity, PrimaryGeneratedColumn, Column, CreateDateColumn, UpdateDateColumn, Generated, Index, OneToOne, JoinColumn } from 'typeorm';
import { UserVideo } from './user-video.entity';

@Entity('processed_user_videos')
export class ProcessedUserVideo {
  @PrimaryGeneratedColumn()
  id: number;

  @Column({ type: 'uuid' })
  @Generated('uuid')
  @Index()
  uuid: string;

  @Column({ type: 'integer' })
  @Index()
  user_video_id: number;

  @OneToOne(() => UserVideo, (userVideo) => userVideo.processedVideo)
  @JoinColumn({ name: 'user_video_id' })
  userVideo: UserVideo;

  @Column({ type: 'varchar', length: 255 })
  video_file_name: string;

  @CreateDateColumn({ type: 'timestamptz' })
  createdAt: Date;

  @UpdateDateColumn({ type: 'timestamptz' })
  updatedAt: Date;
}
