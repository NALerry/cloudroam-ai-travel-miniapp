package com.twm.twmbe.repository;

import com.twm.twmbe.entity.Comment;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

@Repository
public interface CommentRepository extends JpaRepository<Comment, Long> {

    // 根据帖子ID查找评论，按创建时间倒序
    Page<Comment> findByPostIdOrderByCreatedAtDesc(Long postId, Pageable pageable);

    // 根据帖子ID和父评论ID查找回复
    Page<Comment> findByPostIdAndParentIdOrderByCreatedAtDesc(Long postId, Long parentId, Pageable pageable);

    // 统计帖子的评论数量
    Long countByPostId(Long postId);

    // 更新点赞数
    @Modifying
    @Query("UPDATE Comment c SET c.likeCount = c.likeCount + 1 WHERE c.id = :id")
    void incrementLikeCount(@Param("id") Long id);

    // 减少点赞数
    @Modifying
    @Query("UPDATE Comment c SET c.likeCount = c.likeCount - 1 WHERE c.id = :id AND c.likeCount > 0")
    void decrementLikeCount(@Param("id") Long id);
}