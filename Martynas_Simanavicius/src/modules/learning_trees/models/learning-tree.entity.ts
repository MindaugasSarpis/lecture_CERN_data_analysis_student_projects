import { Entity, PrimaryGeneratedColumn, Column, CreateDateColumn, UpdateDateColumn, Generated, Index, OneToMany } from 'typeorm';
import { LearningTreeNode } from './learning-tree-node.entity';

@Entity('learning_trees')
export class LearningTree {
  @PrimaryGeneratedColumn()
  id: number;

  @Column({ type: 'uuid' })
  @Generated('uuid')
  @Index()
  uuid: string;

  @Column({ type: 'varchar', length: 120 })
  name: string;

  @Column({ type: 'text', nullable: true })
  description: string | null;

  @OneToMany(() => LearningTreeNode, (node) => node.learningTree)
  nodes: LearningTreeNode[];

  @CreateDateColumn({ type: 'timestamptz' })
  createdAt: Date;

  @UpdateDateColumn({ type: 'timestamptz' })
  updatedAt: Date;
}
